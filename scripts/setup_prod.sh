#!/usr/bin/env bash
# setup_prod.sh — Installation production CIPRESCHATAPP (Docker)
# Exécuter depuis la racine du projet : bash scripts/setup_prod.sh

set -e

CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

step() { echo -e "\n${CYAN}$1${NC}"; }
ok()   { echo -e "${GREEN}$1${NC}"; }
warn() { echo -e "${YELLOW}$1${NC}"; }
err()  { echo -e "${RED}$1${NC}"; exit 1; }

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo -e "${CYAN}=== CIPRESCHATAPP - Setup Production ===${NC}"

# ── Vérifications préalables ──────────────────────────────────────────────────
step "Vérification des prérequis..."
command -v docker  >/dev/null 2>&1 || err "docker est requis mais introuvable. Installez Docker Engine."
command -v sed     >/dev/null 2>&1 || err "sed est requis mais introuvable."
ok "✓ Docker disponible"

# ── Choix du modèle LLM ───────────────────────────────────────────────────────
step "Choix du modèle Ollama..."
echo ""
echo "  [1] mistral       — 7B  | ~5 Go RAM  | Recommandé (16 Go RAM ou moins)"
echo "  [2] mistral-nemo  — 12B | ~8 Go RAM  | Meilleure qualité (32 Go RAM recommandé)"
echo ""

while true; do
    read -rp "Votre choix (1 ou 2) : " choice
    case "$choice" in
        1) OLLAMA_MODEL="mistral";      break ;;
        2) OLLAMA_MODEL="mistral-nemo"; break ;;
        *) echo "Entrez 1 ou 2." ;;
    esac
done

ok "  Modèle sélectionné : $OLLAMA_MODEL"

# ── Fichier .env ──────────────────────────────────────────────────────────────
step "Configuration du fichier .env..."
ENV_FILE="$ROOT_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
    cp "$ROOT_DIR/.env.example" "$ENV_FILE"
    ok "  .env créé depuis .env.example"
fi

# Injection du modèle choisi (crée la ligne si absente, la remplace sinon)
if grep -q "^OLLAMA_MODEL=" "$ENV_FILE"; then
    sed -i "s|^OLLAMA_MODEL=.*|OLLAMA_MODEL=$OLLAMA_MODEL|" "$ENV_FILE"
else
    echo "OLLAMA_MODEL=$OLLAMA_MODEL" >> "$ENV_FILE"
fi
ok "  OLLAMA_MODEL=$OLLAMA_MODEL écrit dans .env"

# Rappel des secrets à changer
warn "
  [IMPORTANT] Avant de continuer, éditez .env et remplacez :
    SECRET_KEY          → clé aléatoire forte
    JWT_SECRET_KEY      → clé aléatoire forte
    MYSQL_ROOT_PASSWORD → mot de passe root MySQL
    MYSQL_PASSWORD      → mot de passe utilisateur chatbot
"

read -rp "Les secrets sont-ils configurés ? (o/N) : " confirm
case "$confirm" in
    o|O|oui|Oui) ;;
    *) warn "Installation annulée. Éditez .env puis relancez le script."; exit 0 ;;
esac

# ── Build et démarrage Docker ─────────────────────────────────────────────────
step "Build et démarrage des conteneurs..."
cd "$ROOT_DIR"
docker compose up -d --build

echo -e "\n${GREEN}=== Déploiement lancé ! ===${NC}"
echo "
  Modèle : $OLLAMA_MODEL (téléchargement automatique au premier démarrage)

  Suivre les logs :
    docker compose logs -f backend

  Services :
    Frontend  : https://chatbot.lacipres.org
    Backend   : https://chatbot.lacipres.org/api
    phpMyAdmin: http://<hote>:8282

  Compte admin par défaut : admin@lacipres.org / 1234  <-- CHANGER !
"
