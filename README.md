# CIPRESCHATAPP — RAG avec Ollama + Mistral

Stack : Flask · React.js · Apache · MySQL · ChromaDB · Ollama (Mistral 7B)

## Prérequis (Windows)

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

## Structure du projet

```
CIPRESCHATAPP\
├── backend\
│   ├── app\
│   │   ├── routes\         # auth.py, chat.py, documents.py, admin.py
│   │   ├── models\         # user.py, session.py, message.py
│   │   ├── services\       # rag.py, embedder.py, llm.py, ingestor.py
│   │   └── utils\          # auth_utils.py, file_utils.py
│   ├── uploads\            # Documents téléversés
│   ├── chroma_db\          # Base vectorielle persistée
│   ├── config.py
│   ├── run.py
│   └── requirements.txt
├── frontend\
│   ├── src\
│   │   ├── components\     # ChatWindow, MessageBubble, UploadPanel...
│   │   ├── pages\          # LoginPage, ChatPage, AdminPage
│   │   ├── hooks\          # useChat, useAuth
│   │   ├── services\       # api.js
│   │   └── context\        # AuthContext.jsx
│   ├── package.json
│   └── vite.config.js
├── apache\
│   └── cipreschatapp-dev.conf   # VirtualHost dev
└── scripts\
    ├── setup_dev.ps1            # Script d'installation Windows
    └── init_db.sql
```

## Variables d'environnement

Copier `backend\.env.example` → `backend\.env` et renseigner :

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

## Créer le premier administrateur

```powershell
# 1. Enregistrer un compte via l'API
Invoke-RestMethod -Method Post -Uri http://localhost:5000/api/auth/register `
  -ContentType "application/json" `
  -Body '{"username":"admin","email":"admin@example.com","password":"motdepasse"}'

# 2. Passer le rôle admin via MySQL
mysql -u root -p -e "UPDATE chatbot_db.users SET role='admin' WHERE email='admin@example.com';"
```
