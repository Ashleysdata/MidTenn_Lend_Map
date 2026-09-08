"""
build_knowledge_base.py
Week 4 deliverable — AI-Enhanced Analytics Engineer project (MidTenn Lend Map)

One-time (or "re-run when docs change") script that:
1. Reads project documentation files
2. Splits them into smaller chunks
3. Generates an embedding vector for each chunk using Voyage AI
4. Saves everything to a local file (knowledge_base.npz) for fast retrieval later

Usage:
    python build_knowledge_base.py

Requires:
    pip install voyageai python-dotenv numpy
    A VOYAGE_API_KEY set as an environment variable (or in a local .env file)
"""

import os
import glob
import numpy as np

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import voyageai

# ---- Configuration ----

# Which files to pull into the knowledge base. Add more paths/patterns as
# the project grows (e.g. docs/*.md).
DOC_PATHS = [
    "README.md",
]

CHUNK_SIZE = 800       # characters per chunk (rough, not token-exact)
CHUNK_OVERLAP = 100    # overlap between consecutive chunks so context isn't cut mid-thought

EMBED_MODEL = "voyage-4"
OUTPUT_FILE = "knowledge_base.npz"

voyage_client = voyageai.Client()  # reads VOYAGE_API_KEY from environment


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into overlapping chunks of roughly chunk_size characters."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return [c.strip() for c in chunks if c.strip()]


def load_documents(paths: list[str]) -> list[dict]:
    """Read each doc file and return a list of {source, text} dicts."""
    docs = []
    for path in paths:
        for filepath in glob.glob(path):
            with open(filepath, "r", encoding="utf-8") as f:
                docs.append({"source": filepath, "text": f.read()})
    return docs


def build_knowledge_base():
    documents = load_documents(DOC_PATHS)
    if not documents:
        raise FileNotFoundError(
            f"No documents found for patterns: {DOC_PATHS}. "
            "Run this script from the MidTenn_Lend_Map project root."
        )

    all_chunks = []
    chunk_sources = []

    for doc in documents:
        chunks = chunk_text(doc["text"], CHUNK_SIZE, CHUNK_OVERLAP)
        all_chunks.extend(chunks)
        chunk_sources.extend([doc["source"]] * len(chunks))

    print(f"Loaded {len(documents)} document(s), split into {len(all_chunks)} chunks.")

    # Voyage recommends passing input_type="document" when embedding content
    # that will be searched against later (as opposed to the search query itself).
    result = voyage_client.embed(
        all_chunks,
        model=EMBED_MODEL,
        input_type="document",
    )
    embeddings = np.array(result.embeddings)

    np.savez(
        OUTPUT_FILE,
        chunks=np.array(all_chunks, dtype=object),
        sources=np.array(chunk_sources, dtype=object),
        embeddings=embeddings,
    )

    print(f"Saved knowledge base to {OUTPUT_FILE} ({embeddings.shape[0]} vectors, "
          f"{embeddings.shape[1]} dimensions each).")


if __name__ == "__main__":
    build_knowledge_base()
    