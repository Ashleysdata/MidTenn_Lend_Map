"""
rag_query.py
Week 4 deliverable — AI-Enhanced Analytics Engineer project (MidTenn Lend Map)
Answers natural-language questions about the MidTenn Lend Map project by:
1. Embedding the user's question (Voyage AI)
2. Finding the most similar chunks via pgvector similarity search (Postgres)
3. Passing those chunks + the question to Claude to generate a grounded answer
Usage:
    python rag_query.py "What data sources does this project use?"
Requires:
    knowledge_chunks table populated in pgvector (see migrate_to_pgvector.py)
"""
import sys
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
import voyageai
import psycopg2
from anthropic import Anthropic

EMBED_MODEL = "voyage-4"
CLAUDE_MODEL = "claude-sonnet-4-5"
TOP_K = 3  # how many chunks to retrieve per question

DB_CONFIG = dict(
    host="localhost",
    port=5435,
    dbname="postgres",
    user="postgres",
    password="yourpassword",
)

voyage_client = voyageai.Client()
claude_client = Anthropic()

SYSTEM_PROMPT = """You answer questions about the MidTenn Lend Map data engineering \
project using ONLY the excerpts provided below. If the excerpts don't contain enough \
information to answer confidently, say so plainly rather than guessing. Keep answers \
concise and specific."""


def retrieve_top_chunks(question: str, top_k: int):
    result = voyage_client.embed(
        [question],
        model=EMBED_MODEL,
        input_type="query",  # different input_type than documents — Voyage optimizes for each
    )
    query_vec = result.embeddings[0]  # list of 1024 floats

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    # <=> is pgvector's cosine distance operator: smaller = more similar
    cur.execute(
        """
        SELECT chunk_text, source, 1 - (embedding <=> %s::vector) AS similarity
        FROM knowledge_chunks
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
        """,
        (query_vec, query_vec, top_k),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows  # list of (chunk_text, source, similarity)


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
    retrieved = retrieve_top_chunks(question, TOP_K)
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