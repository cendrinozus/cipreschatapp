import requests
import urllib3
from flask import current_app

# Certificat SSL auto-signé sur le serveur interne — vérification désactivée
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Colonnes recherchables par classe (utilisées dans listerOr pour un OR multi-champs)
SEARCHABLE_FIELDS: dict[str, list[str]] = {
    "gec.CourrierArrivee":       ["expediteur", "objet", "reference"],
    "gec.CourrierDepart":        ["destinataire", "objet", "reference"],
    "gec.LotCourrier":           ["reference", "objet"],
    "geb.Budget":                ["libelle", "reference"],
    "geb.Depense":               ["libelle", "beneficiaire", "reference"],
    "geb.Facture":               ["reference", "libelle", "fournisseur"],
    "geb.Fournisseur":           ["nom", "raisonSociale", "email"],
    "geb.LigneBudgetaire":       ["libelle"],
    "geb.PrevisionBudgetaire":   ["libelle", "reference"],
    "geb.VirementBudgetaire":    ["libelle", "reference"],
    "geb.Besoin":                ["libelle", "description"],
    "generic.Utilisateur":       ["nom", "prenoms", "login", "email"],
    "generic.Entite":            ["libelle", "sigle"],
    "generic.Fonction":          ["libelle"],
    "ged.Document":              ["titre", "reference", "libelle"],
    "ged.SousTypeDocument":      ["libelle"],
    "ged.Demande":               ["objet", "reference"],
    "gef.Balance":               ["libelle"],
    "gef.Compte":                ["libelle", "numero"],
    "gef.EtatFinancier":         ["libelle", "reference"],
    "gef.Rubrique":              ["libelle"],
}

DEFAULT_FIELDS = ["libelle", "reference"]


def _base_url() -> str:
    return current_app.config.get("EXTERNAL_API_URL", "").rstrip("/")

def _headers() -> dict:
    token = current_app.config.get("EXTERNAL_API_TOKEN", "")
    return {"Authorization": f"Bearer {token}"} if token else {}

def is_configured() -> bool:
    return bool(_base_url())


def lister(classe: str, filters: dict | None = None, limit: int = 30) -> list[dict]:
    """Appelle /generic/lister — retourne les enregistrements d'une table."""
    url = _base_url()
    if not url:
        return []
    params = {"classe": classe, "limit": str(limit), "start": "0", **(filters or {})}
    try:
        r = requests.get(f"{url}/generic/lister", params=params,
                         headers=_headers(), timeout=10, verify=False)
        if r.ok:
            return r.json().get("data", [])
        print(f"[external_api] lister HTTP {r.status_code} pour {classe}")
    except Exception as e:
        print(f"[external_api] lister erreur : {e}")
    return []


def search(classe: str, term: str, limit: int = 20) -> list[dict]:
    """
    Appelle /generic/listerOr avec les colonnes recherchables de la classe.
    Produit : col1 LIKE '%term%' OR col2 LIKE '%term%' OR ...
    """
    url = _base_url()
    if not url:
        return []

    fields = SEARCHABLE_FIELDS.get(classe, DEFAULT_FIELDS)
    # Chaque champ passé en paramètre devient une condition OR dans listerOr
    params = {"classe": classe, "limit": str(limit), "start": "0"}
    for field in fields:
        params[field] = term

    try:
        r = requests.get(f"{url}/generic/listerOr", params=params,
                         headers=_headers(), timeout=10, verify=False)
        print(f"[external_api] URL appelée : {r.url}")
        print(f"[external_api] HTTP {r.status_code} | Content-Type: {r.headers.get('Content-Type','?')}")
        print(f"[external_api] Réponse brute (200 premiers chars) : {r.text[:200]}")
        if r.ok:
            data = r.json()
            print(f"[external_api] total déclaré : {data.get('total', '?')} | data : {len(data.get('data', []))} ligne(s)")
            return data.get("data", [])
        print(f"[external_api] search HTTP {r.status_code} — {classe} / '{term}'")
    except Exception as e:
        print(f"[external_api] search erreur : {e}")
    return []


def format_results(data: list[dict], classe: str) -> str:
    """Formate les résultats de l'API en texte lisible pour le LLM."""
    if not data:
        return f"Aucune donnée trouvée pour '{classe}'."

    lines = [f"[Données système — {classe} : {len(data)} enregistrement(s)]"]
    for i, row in enumerate(data[:25], 1):
        parts = [f"{k}: {v}" for k, v in row.items()
                 if v is not None and str(v).strip() not in ("", "null")]
        lines.append(f"  {i}. " + " | ".join(parts))
    return "\n".join(lines)
