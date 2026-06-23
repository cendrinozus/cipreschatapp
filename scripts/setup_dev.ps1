# setup_dev.ps1 — Installation complète en mode développement (Windows)
# Exécuter PowerShell en tant qu'Administrateur pour la configuration Apache

$ErrorActionPreference = "Stop"

function Write-Step { param($msg) Write-Host "`n$msg" -ForegroundColor Cyan }
function Write-Ok   { param($msg) Write-Host $msg -ForegroundColor Green }
function Write-Err  { param($msg) Write-Host $msg -ForegroundColor Red; exit 1 }

Write-Host "=== CIPRESCHATAPP - Setup Dev (WampServer) ===" -ForegroundColor Cyan

# ── Détection WampServer ──────────────────────────────────────────────────────
$WAMP_DIR     = "C:\wamp64"
$APACHE_VER   = "apache2.4.65"
$MYSQL_VER    = "mysql8.4.7"
$APACHE_CONF  = "$WAMP_DIR\bin\apache\$APACHE_VER\conf"
$APACHE_EXTRA = "$APACHE_CONF\extra"
$MYSQL_BIN    = "$WAMP_DIR\bin\mysql\$MYSQL_VER\bin"

if (-not (Test-Path $WAMP_DIR)) {
    Write-Err "WampServer introuvable dans $WAMP_DIR. Vérifiez le chemin d'installation."
}

# Ajouter le client mysql au PATH de session si absent
if (-not (Get-Command mysql -ErrorAction SilentlyContinue)) {
    $env:PATH = "$MYSQL_BIN;$env:PATH"
}

# ── Vérifications préalables ──────────────────────────────────────────────────
Write-Step "Vérification des prérequis..."
foreach ($tool in @("python", "node", "mysql", "ollama")) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        Write-Err "$tool est requis mais introuvable dans le PATH."
    }
}
Write-Ok "✓ Tous les prérequis sont présents"

$ROOT_DIR = (Resolve-Path "$PSScriptRoot\..").Path

# ── Backend Python ────────────────────────────────────────────────────────────
Write-Step "[1/5] Installation du backend Flask..."
Set-Location "$ROOT_DIR\backend"
python -m venv venv
& ".\venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }
Write-Ok "✓ Backend prêt"

# ── Base de données ───────────────────────────────────────────────────────────
Write-Step "[2/5] Initialisation MySQL..."
$mysqlPass = Read-Host "Mot de passe root MySQL (Entrée si aucun)"
if ([string]::IsNullOrEmpty($mysqlPass)) {
    Get-Content "$ROOT_DIR\scripts\init_db.sql" | mysql -u root
} else {
    Get-Content "$ROOT_DIR\scripts\init_db.sql" | mysql -u root "-p$mysqlPass"
}
Write-Ok "✓ Base de données créée (chatbot_db)"

# ── Ollama models ─────────────────────────────────────────────────────────────
Write-Step "[3/5] Téléchargement des modèles Ollama..."
ollama pull mistral
ollama pull nomic-embed-text
Write-Ok "✓ Modèles téléchargés"

# ── Frontend React ────────────────────────────────────────────────────────────
Write-Step "[4/5] Installation du frontend React..."
Set-Location "$ROOT_DIR\frontend"
npm install --silent
Write-Ok "✓ Frontend prêt"

# ── Apache (WampServer) ───────────────────────────────────────────────────────
Write-Step "[5/5] Configuration Apache (WampServer)..."

# Copie du VirtualHost
$destConf = "$APACHE_EXTRA\cipreschatapp-dev.conf"
Copy-Item "$ROOT_DIR\apache\cipreschatbot-dev.conf" $destConf -Force
Write-Ok "  ✓ VirtualHost copie dans $destConf"

# Ajout de l'Include dans httpd.conf si absent
$httpdConf   = "$APACHE_CONF\httpd.conf"
$includeLine = "Include conf/extra/cipreschatapp-dev.conf"
if (-not (Select-String -Path $httpdConf -Pattern "cipreschatapp-dev" -Quiet)) {
    Add-Content -Path $httpdConf -Value "`n$includeLine"
    Write-Ok "  ✓ Include ajoute dans httpd.conf"
} else {
    Write-Ok "  ✓ Include deja present dans httpd.conf"
}

# Activation des modules proxy (decommentage dans httpd.conf)
$proxyModules = @("proxy_module", "proxy_http_module", "proxy_wstunnel_module")
$httpdContent = Get-Content $httpdConf -Raw
$changed = $false
foreach ($mod in $proxyModules) {
    $commented = "#LoadModule $mod"
    if ($httpdContent -match [regex]::Escape($commented)) {
        $httpdContent = $httpdContent -replace [regex]::Escape($commented), "LoadModule $mod"
        $changed = $true
        Write-Ok "  ✓ Module active : $mod"
    }
}
if ($changed) { Set-Content -Path $httpdConf -Value $httpdContent -NoNewline }

# Entrée hosts pour cipreschatapp.local
$hostsFile  = "C:\Windows\System32\drivers\etc\hosts"
$isAdmin    = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
$hostExists = Select-String -Path $hostsFile -Pattern "cipreschatapp.local" -Quiet

if ($hostExists) {
    Write-Ok "  ✓ cipreschatapp.local deja present dans le fichier hosts"
} elseif ($isAdmin) {
    Add-Content -Path $hostsFile -Value "127.0.0.1   cipreschatapp.local"
    Write-Ok "  ✓ cipreschatapp.local ajoute dans le fichier hosts"
} else {
    Write-Host @"

  [ACTION MANUELLE REQUISE] Droits administrateur necessaires pour modifier le fichier hosts.
  Ajoutez la ligne suivante dans C:\Windows\System32\drivers\etc\hosts
  (ouvrez Notepad en tant qu'Administrateur) :

      127.0.0.1   cipreschatapp.local

  Ou relancez ce script en Administrateur pour qu'il le fasse automatiquement.
"@ -ForegroundColor Yellow
}

Write-Host "`n  Redemarrez Apache depuis l'icone WampServer dans la barre des taches." -ForegroundColor Yellow

# ── Dossiers de travail ───────────────────────────────────────────────────────
New-Item -ItemType Directory -Force "$ROOT_DIR\backend\uploads"   | Out-Null
New-Item -ItemType Directory -Force "$ROOT_DIR\backend\chroma_db" | Out-Null

Write-Host "`n=== Installation terminee ! ===" -ForegroundColor Green
Write-Host @"

Pour demarrer l'application, ouvrez 3 terminaux PowerShell :

  Terminal 1 (Ollama) :
    ollama serve

  Terminal 2 (Backend Flask) :
    cd backend; .\venv\Scripts\Activate.ps1; flask --app run run --debug

  Terminal 3 (Frontend React) :
    cd frontend; npm run dev

  Acces : http://cipreschatapp.local (via Apache/WampServer) ou http://localhost:3000 (direct)

  Creer le premier admin :
    POST http://localhost:5000/api/auth/register
    { "username": "admin", "email": "admin@lacipres.org", "password": "1234" }
    Puis modifier le role via MySQL :
    UPDATE chatbot_db.users SET role='admin' WHERE email='admin@lacipres.org';
"@
