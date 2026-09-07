"""
rag_query.py
Week 4 deliverable — AI-Enhanced Analytics Engineer project (MidTenn Lend Map)

Answers natural-language questions about the MidTenn Lend Map project by:
1. Embedding the user's question (Voyage AI)
2. Finding the most similar chunks in knowledge_base.npz (cosine similarity)
3. Passing those chunks + the question to Claude to generate a grounded answer

Usage:
    python rag_query.py "What data sources does this project use?"

Requires:
    Run build_knowledge_base.py first to generate knowledge_base.npz
"""

import sys
import numpy as np

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import voyageai
from anthropic import Anthropic

EMBED_MODEL = "voyage-4"
CLAUDE_MODEL = "claude-sonnet-4-5"
KNOWLEDGE_BASE_FILE = "knowledge_base.npz"
TOP_K = 3  # how many chunks to retrieve per question

voyage_client = voyageai.Client()
claude_client = Anthropic()

SYSTEM_PROMPT = """You answer questions about the MidTenn Lend Map data engineering \
project using ONLY the excerpts provided below. If the excerpts don't contain enough \
information to answer confidently, say so plainly rather than guessing. Keep answers \
concise and specific."""


def load_knowledge_base(path: str):
    data = np.load(path, allow_pickle=True)
    return data["chunks"], data["sources"], data["embeddings"]


def cosine_similarity(query_vec: np.ndarray, doc_vecs: np.ndarray) -> np.ndarray:
    query_norm = query_vec / np.linalg.norm(query_vec)
    doc_norms = doc_vecs / np.linalg.norm(doc_vecs, axis=1, keepdims=True)
    return doc_norms @ query_norm


def retrieve_top_chunks(question: str, chunks, sources, embeddings, top_k: int):
    result = voyage_client.embed(
        [question],
        model=EMBED_MODEL,
        input_type="query",  # different input_type than documents — Voyage optimizes for each
    )
    query_vec = np.array(result.embeddings[0])

    similarities = cosine_similarity(query_vec, embeddings)
    top_indices = np.argsort(similarities)[::-1][:top_k]

    return [(chunks[i], sources[i], similarities[i]) for i in top_indices]


def generate_answer(question: str, retrieved_chunks: list[tuple]) -> str:
    context = "\n\n---\n\n".join(
        f"[Source: {source}]\n{chunk}" for chunk, source, _ in retrieved_chunks
    )

    user_message = f"""Context excerpts:
{context}

Question: {question}"""

    response = claude_client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text.strip()


def ask(question: str, verbose: bool = True) -> str:
    chunks, sources, embeddings = load_knowledge_base(KNOWLEDGE_BASE_FILE)
    retrieved = retrieve_top_chunks(question, chunks, sources, embeddings, TOP_K)

    if verbose:
        print("\nRetrieved chunks:")
        for chunk, source, score in retrieved:
            preview = chunk[:80].replace("\n", " ")
            print(f"  [{score:.3f}] {source}: {preview}...")

    return generate_answer(question, retrieved)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = input("Ask a question about the project: ")

    answer = ask(question)
    print(f"\nAnswer:\n{answer}")