# setup_prod.ps1 — Installation production CIPRESCHATAPP (Docker)
# Exécuter depuis la racine du projet

$ErrorActionPreference = "Stop"

function Write-Step { param($msg) Write-Host "`n$msg" -ForegroundColor Cyan }
function Write-Ok   { param($msg) Write-Host $msg -ForegroundColor Green }
function Write-Err  { param($msg) Write-Host $msg -ForegroundColor Red; exit 1 }

Write-Host "=== CIPRESCHATAPP - Setup Production ===" -ForegroundColor Cyan

$ROOT_DIR = (Resolve-Path "$PSScriptRoot\..").Path

# ── Vérifications préalables ──────────────────────────────────────────────────
Write-Step "Vérification des prérequis..."
foreach ($tool in @("docker")) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        Write-Err "$tool est requis mais introuvable. Installez Docker Desktop."
    }
}
Write-Ok "✓ Docker disponible"

# ── Choix du modèle LLM ───────────────────────────────────────────────────────
Write-Step "Choix du modèle Ollama..."
Write-Host ""
Write-Host "  [1] mistral       — 7B  | ~5 Go RAM  | Recommandé (16 Go RAM ou moins)"
Write-Host "  [2] mistral-nemo  — 12B | ~8 Go RAM  | Meilleure qualité (32 Go RAM recommandé)"
Write-Host ""

do {
    $choice = Read-Host "Votre choix (1 ou 2)"
} while ($choice -notin @("1", "2"))

$OLLAMA_MODEL = if ($choice -eq "1") { "mistral" } else { "mistral-nemo" }
Write-Ok "  Modèle sélectionné : $OLLAMA_MODEL"

# ── Fichier .env ──────────────────────────────────────────────────────────────
Write-Step "Configuration du fichier .env..."
$envFile = "$ROOT_DIR\.env"

if (-not (Test-Path $envFile)) {
    Copy-Item "$ROOT_DIR\.env.example" $envFile
    Write-Ok "  .env créé depuis .env.example"
}

# Injection du modèle choisi
$envContent = Get-Content $envFile -Raw
$envContent = $envContent -replace "OLLAMA_MODEL=.*", "OLLAMA_MODEL=$OLLAMA_MODEL"
Set-Content -Path $envFile -Value $envContent.TrimEnd()
Write-Ok "  OLLAMA_MODEL=$OLLAMA_MODEL écrit dans .env"

# Rappel des secrets à changer
Write-Host @"

  [IMPORTANT] Avant de continuer, editez .env et remplacez :
    SECRET_KEY          → clé aléatoire forte
    JWT_SECRET_KEY      → clé aléatoire forte
    MYSQL_ROOT_PASSWORD → mot de passe root MySQL
    MYSQL_PASSWORD      → mot de passe utilisateur chatbot

"@ -ForegroundColor Yellow

$confirm = Read-Host "Les secrets sont-ils configurés ? (o/N)"
if ($confirm -notin @("o", "O", "oui", "Oui")) {
    Write-Host "Installation annulée. Editez .env puis relancez le script." -ForegroundColor Yellow
    exit 0
}

# ── Build et démarrage Docker ─────────────────────────────────────────────────
Write-Step "Build et démarrage des conteneurs..."
Set-Location $ROOT_DIR
docker compose up -d --build

Write-Host "`n=== Déploiement lancé ! ===" -ForegroundColor Green
Write-Host @"

  Modèle : $OLLAMA_MODEL (téléchargement automatique au premier démarrage)

  Suivre les logs :
    docker compose logs -f backend

  Services :
    Frontend  : https://chatbot.lacipres.org
    Backend   : https://chatbot.lacipres.org/api
    phpMyAdmin: http://<hote>:8181

  Compte admin par défaut : admin@lacipres.org / 1234  <-- CHANGER !
"@
