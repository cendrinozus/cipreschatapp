# CIPRESCHATAPP — RAG avec Ollama + Mistral Nemo

Stack : Flask · React.js · Apache · MySQL · ChromaDB · Ollama (Mistral Nemo 12B)

## Prérequis (Windows — mode dev)

| Outil | Version min. | Lien |
|---|---|---|
| Python | 3.11+ | https://python.org |
| Node.js | 20+ | https://nodejs.org |
| MySQL | 8+ | https://dev.mysql.com/downloads/installer/ |
| Apache | 2.4+ | https://www.apachelounge.com/download/ ou XAMPP |
| Ollama | dernière | https://ollama.com |

> Tous ces outils doivent être accessibles depuis le PATH (vérifier avec `python --version`, `node --version`, etc.).

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

Ouvrir **3 terminaux PowerShell** séparés :

```powershell
# Terminal 1 — Ollama
ollama pull mistral-nemo   # première fois uniquement (~7 Go)
ollama serve

# Terminal 2 — Backend Flask
cd backend; .\venv\Scripts\Activate.ps1; flask --app run run --debug

# Terminal 3 — Frontend React
cd frontend; npm run dev
```

Accès : http://localhost:3000 (direct) ou http://localhost (via Apache)

## Configuration Apache (Windows)

1. Copier `apache\cipreschatapp-dev.conf` dans votre dossier Apache :
   - Apache Lounge : `C:\Apache24\conf\extra\`
   - XAMPP : `C:\xampp\apache\conf\extra\`

2. Ajouter à la fin de `httpd.conf` :
   ```
   Include conf/extra/cipreschatapp-dev.conf
   ```

3. Décommenter dans `httpd.conf` :
   ```
   LoadModule proxy_module modules/mod_proxy.so
   LoadModule proxy_http_module modules/mod_proxy_http.so
   LoadModule proxy_wstunnel_module modules/mod_proxy_wstunnel.so
   LoadModule headers_module modules/mod_headers.so
   LoadModule rewrite_module modules/mod_rewrite.so
   ```

4. Redémarrer Apache (via `services.msc` ou le panneau XAMPP).

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

```bash
# 1. Copier et adapter les variables d'environnement
cp .env.example .env        # Linux / macOS
copy .env.example .env      # Windows (cmd / PowerShell)
# Éditer .env : changer SECRET_KEY, JWT_SECRET_KEY et les mots de passe MySQL

# 2. Construire et démarrer tous les services
docker compose up -d --build
```

Le backend attend automatiquement que MySQL et Ollama soient prêts, puis télécharge `mistral-nemo` et `nomic-embed-text` au premier démarrage (**opération longue ~7 Go**).

### Services exposés

| Service | URL | Description |
|---|---|---|
| Frontend | https://chatbot.lacipres.org | Interface React (HTTPS) |
| Backend API | https://chatbot.lacipres.org/api | Flask via proxy Apache |
| phpMyAdmin | http://\<hôte\>:8181 | Administration MySQL |
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
│   └── cipreschatapp-dev.conf   # VirtualHost dev (WampServer / XAMPP)
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
OLLAMA_MODEL=mistral-nemo
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

## Créer le premier administrateur

```powershell
# 1. Enregistrer un compte via l'API
Invoke-RestMethod -Method Post -Uri http://localhost:5000/api/auth/register `
  -ContentType "application/json" `
  -Body '{"username":"admin","email":"admin@example.com","password":"motdepasse"}'

# 2. Passer le rôle admin via MySQL
mysql -u root -p -e "UPDATE chatbot_db.users SET role='admin' WHERE email='admin@example.com';"
```
