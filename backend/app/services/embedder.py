import chromadb
from chromadb.config import Settings
import ollama
from flask import current_app

_chroma_client = None
_collection    = None

def get_collection():
    global _chroma_client, _collection
    if _collection is None:
        path = current_app.config["CHROMA_PATH"]
        _chroma_client = chromadb.PersistentClient(path=path,
            settings=Settings(anonymized_telemetry=False))
        _collection = _chroma_client.get_or_create_collection(
            name="entreprise_docs",
            metadata={"hnsw:space": "cosine"})
    return _collection

def embed_text(text: str) -> list[float]:
    model  = current_app.config["EMBED_MODEL"]
    client = ollama.Client(host=current_app.config["OLLAMA_URL"])
    resp   = client.embeddings(model=model, prompt=text)
    return resp["embedding"]

def add_chunks(chunks: list[dict]):
    """chunks = [{"id": str, "text": str, "metadata": dict}]"""
    col = get_collection()
    col.add(
        ids        = [c["id"]       for c in chunks],
        embeddings = [embed_text(c["text"]) for c in chunks],
        documents  = [c["text"]     for c in chunks],
        metadatas  = [c["metadata"] for c in chunks],
    )

def search_similar(query: str, top_k: int = 5) -> list[dict]:
    col        = get_collection()
    query_emb  = embed_text(query)
    results    = col.query(query_embeddings=[query_emb], n_results=top_k,
                           include=["documents", "metadatas", "distances"])
    output = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        output.append({"text": doc, "metadata": meta, "score": round(1 - dist, 4)})
    return output

def delete_file_chunks(filename: str):
    col = get_collection()
    col.delete(where={"source": filename})
