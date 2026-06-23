#!/bin/bash
# setup_dev.sh — Installation complète en mode développement

set -e
CYAN='\033[0;36m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'

echo -e "${CYAN}=== CIPRESCHATAPP — Setup Dev ===${NC}\n"

# ── Vérifications préalables ──────────────────────────────────────────────────
command -v python3  >/dev/null || { echo -e "${RED}Python3 requis${NC}"; exit 1; }
command -v node     >/dev/null || { echo -e "${RED}Node.js requis${NC}"; exit 1; }
command -v mysql    >/dev/null || { echo -e "${RED}MySQL requis${NC}"; exit 1; }
command -v ollama   >/dev/null || { echo -e "${RED}Ollama requis (https://ollama.com)${NC}"; exit 1; }

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ── Backend Python ────────────────────────────────────────────────────────────
echo -e "${CYAN}[1/5] Installation du backend Flask...${NC}"
cd "$ROOT_DIR/backend"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
cp -n .env.example .env 2>/dev/null || true
echo -e "${GREEN}✓ Backend prêt${NC}\n"

# ── Base de données ───────────────────────────────────────────────────────────
echo -e "${CYAN}[2/5] Initialisation MySQL...${NC}"
echo "Entrez le mot de passe root MySQL (laisser vide si aucun) :"
read -s MYSQL_ROOT_PASS
if [ -z "$MYSQL_ROOT_PASS" ]; then
  mysql -u root < "$ROOT_DIR/scripts/init_db.sql"
else
  mysql -u root -p"$MYSQL_ROOT_PASS" < "$ROOT_DIR/scripts/init_db.sql"
fi
echo -e "${GREEN}✓ Base de données créée (chatbot_db)${NC}\n"

# ── Ollama models ─────────────────────────────────────────────────────────────
echo -e "${CYAN}[3/5] Téléchargement des modèles Ollama...${NC}"
ollama pull mistral
ollama pull nomic-embed-text
echo -e "${GREEN}✓ Modèles téléchargés${NC}\n"

# ── Frontend React ────────────────────────────────────────────────────────────
echo -e "${CYAN}[4/5] Installation du frontend React...${NC}"
cd "$ROOT_DIR/frontend"
npm install --silent
echo -e "${GREEN}✓ Frontend prêt${NC}\n"

# ── Apache ────────────────────────────────────────────────────────────────────
echo -e "${CYAN}[5/5] Configuration Apache...${NC}"
if command -v apache2 >/dev/null; then
  sudo a2enmod proxy proxy_http proxy_wstunnel headers rewrite 2>/dev/null || true
  sudo cp "$ROOT_DIR/apache/cipreschatapp-dev.conf" /etc/apache2/sites-available/
  sudo a2ensite cipreschatapp-dev 2>/dev/null || true
  sudo systemctl reload apache2
  echo -e "${GREEN}✓ Apache configuré${NC}\n"
else
  echo -e "${RED}Apache non trouvé — configurez manuellement apache/cipreschatapp-dev.conf${NC}\n"
fi

# ── Dossiers de travail ───────────────────────────────────────────────────────
mkdir -p "$ROOT_DIR/backend/uploads"
mkdir -p "$ROOT_DIR/backend/chroma_db"

echo -e "${GREEN}=== Installation terminée ! ===${NC}\n"
echo "Pour démarrer l'application :"
echo ""
echo "  Terminal 1 (Ollama) :"
echo "    ollama serve"
echo ""
echo "  Terminal 2 (Backend Flask) :"
echo "    cd backend && source venv/bin/activate && flask --app run run --debug"
echo ""
echo "  Terminal 3 (Frontend React) :"
echo "    cd frontend && npm run dev"
echo ""
echo "  Accès : http://localhost (via Apache) ou http://localhost:3000 (direct)"
echo ""
echo "  Créer le premier admin :"
echo "    POST http://localhost:5000/api/auth/register"
echo "    { \"username\": \"admin\", \"email\": \"admin@...\", \"password\": \"...\" }"
echo "    Puis modifier le rôle via MySQL :"
echo "    UPDATE chatbot_db.users SET role='admin' WHERE email='admin@...';"
