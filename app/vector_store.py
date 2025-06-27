"""
Vector store wrapper.
• Uses Chroma (local) with an OpenAI embedding function.
• Persists the collection to ./embeddings so we embed only once.
"""

from pathlib import Path
from typing import List
from chromadb import Client
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from app.document_loader import load_all

# ---------- CONFIG ----------
PERSIST_DIR = Path(__file__).resolve().parent.parent / "embeddings"
COLLECTION_NAME = "finrag"
EMBED_MODEL = "text-embedding-ada-002"     # swap for OpenAI v3 as needed
# -----------------------------

# Initialise Chroma client with persistence
client = Client(
    Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=str(PERSIST_DIR)
    )
)

# Create or load collection
if COLLECTION_NAME in [c.name for c in client.list_collections()]:
    collection = client.get_collection(COLLECTION_NAME)
else:
    collection = client.create_collection(COLLECTION_NAME)

# Embedding function (lazy-init OpenAI)
openai_embed = embedding_functions.OpenAIEmbeddingFunction(
    model_name=EMBED_MODEL,
    api_key=None   # reads OPENAI_API_KEY from env
)

def _bootstrap_index():
    """Embed docs only if the collection is empty."""
    if collection.count() > 0:
        return

    docs = load_all()                       # [(chunk, meta), …]
    texts, metadatas = zip(*docs)

    collection.add(
        documents=list(texts),
        metadatas=list(metadatas),
        ids=[f"c_{i}" for i in range(len(texts))],
        embedding_function=openai_embed,
    )

    client.persist()
    print(f"Indexed {len(texts)} chunks.")

_bootstrap_index()      # run at import time


# ---------- Public helper ----------

def similarity_search(query: str,
                      allowed_depts: List[str],
                      k: int = 4):
    """
    Return top-k chunks whose metadata.department is in allowed_depts.
    Each result is a dict: {"content": str, "metadata": dict}
    """
    results = collection.query(
        query_texts=[query],
        n_results=k,
        where={"department": {"$in": allowed_depts}},
        include=["documents", "metadatas"],
        embedding_function=openai_embed
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    return [{"content": d, "metadata": m} for d, m in zip(docs, metas)]
