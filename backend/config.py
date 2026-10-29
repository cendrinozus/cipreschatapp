import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = False  # dev : pas d'expiration

    # MySQL
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER', 'chatbot')}:"
        f"{os.getenv('MYSQL_PASSWORD', 'chatbot_pass')}@"
        f"{os.getenv('MYSQL_HOST', 'localhost')}/"
        f"{os.getenv('MYSQL_DB', 'chatbot_db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Ollama
    OLLAMA_URL   = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
    EMBED_MODEL  = os.getenv("EMBED_MODEL", "nomic-embed-text")
    # Options d'inférence : num_ctx doit être identique pour tous les appels,
    # sinon Ollama recharge le modèle à chaque changement de valeur.
    OLLAMA_NUM_CTX     = int(os.getenv("OLLAMA_NUM_CTX", "8192"))
    OLLAMA_NUM_THREAD  = int(os.getenv("OLLAMA_NUM_THREAD", "0"))  # 0 = auto
    OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "1024"))

    # Fichiers
    UPLOAD_FOLDER  = os.getenv("UPLOAD_FOLDER", "uploads")
    CHROMA_PATH    = os.getenv("CHROMA_PATH", "chroma_db")
    MAX_CHUNK_SIZE = 512
    CHUNK_OVERLAP  = 50
    TOP_K_RESULTS  = 5

    ALLOWED_EXTENSIONS = {"pdf", "docx", "xlsx", "txt", "md"}

    # API externe (système de gestion CIPRES)
    EXTERNAL_API_URL   = os.getenv("EXTERNAL_API_URL", "")
    EXTERNAL_API_TOKEN = os.getenv("EXTERNAL_API_TOKEN", "")
