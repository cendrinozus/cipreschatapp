import json
import ollama
from flask import current_app
from app.services.embedder import search_similar
from app.services import external_api

# ── Prompts ────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Tu es un assistant interne d'entreprise. Tu réponds uniquement en français.
Tu utilises les extraits de documents fournis et, si présentes, les données du système de gestion pour répondre aux questions.

Règles :
- Réponds toujours en français, de façon claire et professionnelle.
- Si le contexte contient la réponse, utilise-le et cite la source (nom du fichier) entre crochets, ex: [rapport_2024.pdf].
- Si plusieurs sources confirment l'information, cite-les toutes.
- Si le contexte ne contient pas assez d'informations pour répondre, dis-le clairement sans inventer.
- Ne réponds jamais à des questions hors du périmètre des documents et données de l'entreprise.
"""

_ROUTER_SYSTEM = """Tu es un routeur qui analyse si une question nécessite des données en temps réel du système de gestion de l'entreprise.
Réponds UNIQUEMENT en JSON valide, sans texte supplémentaire.

Si la question mentionne des courriers, budgets, dépenses, factures, fournisseurs, utilisateurs, agents, documents, comptes, balances, ou des termes comme "base de données", "BD", "système", "cherche", "trouve dans" :
{"needs_api": true, "classe": "MODULE.CLASSE", "recherche": "TERME_OU_VIDE"}

Sinon :
{"needs_api": false}

Classes disponibles :
- gec.CourrierArrivee  → courriers arrivée, entrants, reçus
- gec.CourrierDepart   → courriers départ, sortants, envoyés
- gec.LotCourrier      → lots de courriers
- geb.Budget           → budgets
- geb.Depense          → dépenses
- geb.Facture          → factures
- geb.Fournisseur      → fournisseurs, prestataires
- geb.LigneBudgetaire  → lignes budgétaires
- geb.PrevisionBudgetaire → prévisions budgétaires
- geb.VirementBudgetaire  → virements budgétaires
- generic.Utilisateur  → utilisateurs, agents, personnel, employés
- ged.Document         → documents, fichiers GED
- gef.Balance          → balances financières
- gef.Compte           → comptes financiers
- gef.EtatFinancier    → états financiers
"""


# ── Routeur : décide si l'API externe est nécessaire ──────────────────────────

def _route(question: str, model: str) -> dict | None:
    """
    Appel rapide (JSON, temperature=0) pour décider si la question
    nécessite des données de l'API externe.
    Retourne {"classe": ..., "recherche": ...} ou None.
    """
    try:
        client = ollama.Client(host=current_app.config["OLLAMA_URL"])
        resp = client.chat(
            model=model,
            messages=[
                {"role": "system", "content": _ROUTER_SYSTEM},
                {"role": "user",   "content": f"Question : {question}"},
            ],
            format="json",
            options={"temperature": 0},
        )
        msg     = resp.message if hasattr(resp, "message") else resp["message"]
        content = msg.content  if hasattr(msg,  "content") else msg["content"]
        result  = json.loads(content)
        if result.get("needs_api"):
            return result
    except Exception as e:
        print(f"[router] erreur : {e}")
    return None


# ── Helpers RAG ────────────────────────────────────────────────────────────────

def build_context(results: list[dict]) -> tuple[str, list[dict]]:
    if not results:
        return "", []
    context_lines, sources = [], []
    for i, r in enumerate(results):
        src   = r["metadata"].get("source", "inconnu")
        idx   = r["metadata"].get("chunk_index", i)
        score = r.get("score", 0)
        context_lines.append(f"[Extrait {i+1} — {src}, partie {idx}]\n{r['text']}")
        sources.append({"file": src, "chunk_index": idx, "score": score})
    return "\n\n".join(context_lines), sources

def should_cite(results: list[dict], threshold: float = 0.65) -> bool:
    return any(r.get("score", 0) >= threshold for r in results)


# ── Pipeline principal ─────────────────────────────────────────────────────────

def ask(question: str, history: list[dict] | None = None) -> dict:
    """
    Pipeline RAG + routeur API externe.
    Returns: {"answer", "sources", "cited", "api_calls"}
    """
    top_k   = current_app.config["TOP_K_RESULTS"]
    model   = current_app.config["OLLAMA_MODEL"]
    api_calls: list = []

    # 1. Recherche sémantique dans ChromaDB
    results          = search_similar(question, top_k=top_k)
    context, sources = build_context(results)
    cite             = should_cite(results)

    # 2. Routeur : l'API externe est-elle nécessaire ?
    api_context = ""
    if external_api.is_configured():
        routing = _route(question, model)
        if routing:
            classe    = routing.get("classe", "")
            recherche = routing.get("recherche", "")
            data      = (external_api.search(classe, recherche)
                         if recherche else external_api.lister(classe))
            api_context = external_api.format_results(data, classe)
            api_calls.append({
                "classe":    classe,
                "recherche": recherche or None,
                "nb_lignes": len(data),
            })
            print(f"[API externe] {classe} | recherche='{recherche}' | {len(data)} ligne(s)")

    # 3. Construction du message utilisateur
    parts = []
    if context:
        parts.append(
            f"Contexte extrait des documents :\n{'='*60}\n{context}\n{'='*60}"
        )
    if api_context:
        parts.append(
            f"Données en temps réel du système de gestion :\n{'='*60}\n{api_context}\n{'='*60}"
        )
    if not parts:
        parts.append("(Aucune donnée pertinente trouvée — documents ni système de gestion.)")

    parts.append(f"Question : {question}")
    user_message = "\n\n".join(parts)

    # 4. Construction des messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        for h in history[-6:]:
            messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": user_message})

    # 5. Appel LLM principal
    print(f"[rag] Appel Ollama model={model} ({len(messages)} messages)...")
    client   = ollama.Client(host=current_app.config["OLLAMA_URL"])
    response = client.chat(model=model, messages=messages)
    print("[rag] Réponse Ollama reçue.")
    resp_msg = response.message if hasattr(response, "message") else response["message"]
    answer   = resp_msg.content if hasattr(resp_msg, "content") else resp_msg["content"]

    return {
        "answer":    answer,
        "sources":   sources if cite else [],
        "cited":     cite,
        "api_calls": api_calls,
    }
