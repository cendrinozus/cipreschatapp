#!/bin/sh
set -e

echo "Waiting for MySQL..."
until python -c "
import pymysql, os, sys
try:
    pymysql.connect(
        host=os.getenv('MYSQL_HOST', 'mysql'),
        user=os.getenv('MYSQL_USER', 'chatbot'),
        password=os.getenv('MYSQL_PASSWORD', 'chatbot_pass'),
        database=os.getenv('MYSQL_DB', 'chatbot_db')
    ).close()
except Exception:
    sys.exit(1)
" 2>/dev/null; do
    printf "."
    sleep 3
done
echo " MySQL ready."

echo "Waiting for Ollama..."
until python -c "
import urllib.request, os, sys
try:
    urllib.request.urlopen(os.getenv('OLLAMA_URL', 'http://ollama:11434') + '/api/version', timeout=3)
except Exception:
    sys.exit(1)
" 2>/dev/null; do
    printf "."
    sleep 5
done
echo " Ollama ready."

echo "Ensuring Ollama models are available (first run may take several minutes)..."
python -c "
import ollama, os
client = ollama.Client(host=os.getenv('OLLAMA_URL', 'http://ollama:11434'))
for model in [os.getenv('OLLAMA_MODEL', 'mistral-nemo'), os.getenv('EMBED_MODEL', 'nomic-embed-text')]:
    print(f'  Pulling {model}...')
    client.pull(model)
    print(f'  {model} ready.')
"

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 600 --keep-alive 5 run:app
