# CIPRESCHATAPP — RAG avec Ollama + Mistral Nemo

Stack : Flask · React.js · Apache · MySQL · ChromaDB · Ollama (Mistral Nemo 12B)

## Prérequis (Windows — mode dev)

| Outil | Version min. | Lien |
|---|---|---|
| Python | 3.11+ | https://python.org |
| Node.js | 20+ | https://nodejs.org |
| WampServer | 3.3+ | https://www.wampserver.com (inclut Apache 2.4 + MySQL 8) |
| Ollama | dernière | https://ollama.com |

> **WampServer est déjà installé sur la machine de dev** — Apache et MySQL sont fournis par WampServer, pas besoin de les installer séparément.
> Python, Node.js et Ollama doivent être accessibles depuis le PATH (vérifier avec `python --version`, `node --version`, `ollama --version`).

## Installation rapide (mode dev)

Ouvrir **PowerShell en tant qu'Administrateur** :

```powershell
# 1. Entrer dans le projet
cd C:\Users\knyanda\Documents\Projets\CIPRESCHATAPP

# 2. Autoriser l'exécution de scripts (si pas déjà fait)
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

# 3. Lancer le script d'installation
.\scripts\setup_dev.ps1
```

## Lancer en mode dev

**Avant tout :** démarrer WampServer (icône dans la barre des tâches — attendre que le logo passe au vert).

Ouvrir **3 terminaux PowerShell** séparés :

```powershell
# Terminal 1 — Ollama
ollama pull mistral   # première fois uniquement (~7 Go)
ollama serve

# Terminal 2 — Backend Flask
cd backend; .\venv\Scripts\Activate.ps1; flask --app run run --debug

# Terminal 3 — Frontend React
cd frontend; npm run dev
```

> Apache et MySQL sont gérés par WampServer — pas besoin de les démarrer manuellement dans un terminal.

Accès : http://localhost:3000 (direct) ou http://localhost (via Apache/WampServer)

## Configuration Apache (Windows — WampServer)

1. Copier `apache\cipreschatapp-dev.conf` dans le dossier extra d'Apache fourni par WampServer :
   ```
   C:\wamp64\bin\apache\apache2.4.xx\conf\extra\cipreschatapp-dev.conf
   ```
   *(remplacer `apache2.4.xx` par la version installée, ex. `apache2.4.62`)*

2. Ouvrir `C:\wamp64\bin\apache\apache2.4.xx\conf\httpd.conf` et ajouter à la fin :
   ```
   Include conf/extra/cipreschatapp-dev.conf
   ```

3. Décommenter dans `httpd.conf` (si ce n'est pas déjà fait par WampServer) :
   ```
   LoadModule proxy_module modules/mod_proxy.so
   LoadModule proxy_http_module modules/mod_proxy_http.so
   LoadModule proxy_wstunnel_module modules/mod_proxy_wstunnel.so
   LoadModule headers_module modules/mod_headers.so
   LoadModule rewrite_module modules/mod_rewrite.so
   ```

4. Redémarrer Apache via l'icône WampServer dans la barre des tâches : **clic gauche → Apache → Restart Service**.

> Astuce : WampServer permet aussi d'activer les modules directement via le menu **Apache → Apache modules** sans éditer `httpd.conf` manuellement.

---

## Déploiement production (Docker)

### Prérequis

| Outil | Version min. | Notes |
|---|---|---|
| Docker Engine | 24+ | Linux ou Docker Desktop Windows (backend WSL2) |
| Docker Compose | v2+ | Inclus dans Docker Desktop |

> **RAM recommandée :** 16 Go minimum (Mistral Nemo 12B en CPU-only) · 8 Go VRAM si GPU NVIDIA.

### Compatibilité Windows

Le déploiement fonctionne sur **Docker Desktop Windows** (backend WSL2) sans modification.

Points de vigilance spécifiques Windows :
- Utiliser **PowerShell** ou le terminal intégré de Docker Desktop (pas cmd.exe)
- Le dossier `ssl\` (certificats) est un chemin relatif au projet — fonctionne tel quel
- Pour le GPU Ollama sous Windows, installer [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) et activer le support GPU dans Docker Desktop > Settings > Resources > GPU

### Démarrage

Utiliser le script d'installation interactif (choix du modèle LLM inclus) :

```powershell
# Windows (PowerShell)
.\scripts\setup_prod.ps1
```

```bash
# Linux / macOS
bash scripts/setup_prod.sh
```

Ou manuellement :

```bash
# 1. Copier et adapter les variables d'environnement
cp .env.example .env        # Linux / macOS
copy .env.example .env      # Windows (cmd / PowerShell)
# Éditer .env : changer SECRET_KEY, JWT_SECRET_KEY, mots de passe MySQL
# et OLLAMA_MODEL (mistral ou mistral-nemo)

# 2. Construire et démarrer tous les services
docker compose up -d --build
```

Le backend attend automatiquement que MySQL et Ollama soient prêts, puis télécharge le modèle choisi et `nomic-embed-text` au premier démarrage.

| Modèle | Taille | RAM recommandée |
|---|---|---|
| `mistral` | 7B | 16 Go |
| `mistral-nemo` | 12B | 32 Go |

### Services exposés

| Service | URL | Description |
|---|---|---|
| Frontend | https://chatbot.lacipres.org | Interface React (HTTPS) |
| Backend API | https://chatbot.lacipres.org/api | Flask via proxy Apache |
| phpMyAdmin | http://\<hôte\>:8282 | Administration MySQL |
| Ollama | http://\<hôte\>:11434 | API LLM (interne) |

### SSL en production

Le frontend génère un certificat auto-signé au build — utilisable immédiatement (le navigateur affichera un avertissement à accepter).

Pour remplacer par un vrai certificat (Let's Encrypt ou autre), ajouter dans `docker-compose.yml` sous le service `frontend` :

```yaml
    volumes:
      - ./ssl:/etc/ssl/cipreschatapp:ro
```

Puis créer le dossier `ssl\` à la racine et y placer vos fichiers **avant** de relancer :

```
ssl\
├── cipreschatapp.crt
└── cipreschatapp.key
```

> Ne pas monter ce volume avec un dossier vide — cela écrase les certificats générés au build et empêche Apache de démarrer.

### Commandes utiles

```bash
# Voir les logs en temps réel
docker compose logs -f backend

# Arrêter sans supprimer les volumes
docker compose down

# Supprimer également les données (MySQL, ChromaDB, uploads, modèles Ollama)
docker compose down -v
```

---

## Structure du projet

```
CIPRESCHATAPP\
├── docker-compose.yml           # Orchestration production (5 services)
├── .env.example                 # Variables Docker à copier en .env
├── mysql\
│   └── init.sql                 # Initialisation charset MySQL
├── backend\
│   ├── app\
│   │   ├── routes\              # auth.py, chat.py, documents.py, admin.py
│   │   ├── models\              # user.py, session.py, message.py
│   │   ├── services\            # rag.py, embedder.py, llm.py, ingestor.py
│   │   └── utils\               # auth_utils.py, file_utils.py
│   ├── uploads\                 # Documents téléversés
│   ├── chroma_db\               # Base vectorielle persistée
│   ├── Dockerfile
│   ├── entrypoint.sh            # Attente MySQL/Ollama, pull modèles, Gunicorn
│   ├── config.py
│   ├── run.py
│   └── requirements.txt
├── frontend\
│   ├── src\
│   │   ├── components\          # ChatWindow, MessageBubble, UploadPanel...
│   │   ├── pages\               # LoginPage, ChatPage, AdminPage
│   │   ├── hooks\               # useChat, useAuth
│   │   ├── services\            # api.js
│   │   └── context\             # AuthContext.jsx
│   ├── Dockerfile
│   ├── cipreschatapp.conf       # VirtualHost Apache production (HTTPS + SPA)
│   ├── package.json
│   └── vite.config.js
├── apache\
│   └── cipreschatapp-dev.conf   # VirtualHost dev (WampServer)
└── scripts\
    ├── setup_dev.ps1            # Script d'installation Windows
    └── init_db.sql              # Init base de données (dev)
```

## Variables d'environnement

### Dev — `backend\.env`

```
SECRET_KEY=changeme
JWT_SECRET_KEY=changeme
MYSQL_HOST=localhost
MYSQL_USER=chatbot
MYSQL_PASSWORD=chatbot_pass
MYSQL_DB=chatbot_db
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=mistral
EMBED_MODEL=nomic-embed-text
UPLOAD_FOLDER=uploads
CHROMA_PATH=chroma_db
```

### Production — `.env` (racine, pour Docker Compose)

Copier `.env.example` → `.env` et renseigner au minimum :

```
SECRET_KEY=<clé aléatoire forte>
JWT_SECRET_KEY=<clé aléatoire forte>
MYSQL_ROOT_PASSWORD=<mot de passe root>
MYSQL_PASSWORD=<mot de passe chatbot>
```

## Compte administrateur par défaut

Le script `setup_dev.ps1` crée automatiquement un compte admin au premier lancement :

| Champ | Valeur |
|---|---|
| Email | `admin@lacipres.org` |
| Mot de passe | `1234` |

> Changer ce mot de passe dès la première connexion. En production, modifier `_seed_admin()` dans [backend/app/__init__.py](backend/app/__init__.py) avant le déploiement.

La commande peut aussi être relancée manuellement si nécessaire :

```powershell
cd backend
.\venv\Scripts\Activate.ps1
flask --app run seed
```
