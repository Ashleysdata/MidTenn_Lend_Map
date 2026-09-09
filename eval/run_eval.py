"""
run_eval.py
Eval harness for the RAG project (rag_query.py).

For each labeled question in eval_questions.json:
  1. Run the real RAG pipeline (retrieve_top_chunks + generate_answer)
  2. Ask Claude to grade the RAG answer against a human-written reference answer on:
     - relevance (did it address the question, using the retrieved context?)
     - accuracy (does it match the reference answer / not contradict it?)
     - groundedness (is everything in the answer supported by the retrieved chunks,
       i.e. no fabricated/hallucinated content?)
  3. Save per-question results + an aggregate report.

Usage:
    python eval/run_eval.py
Requires:
    Same env as rag_query.py (ANTHROPIC_API_KEY, VOYAGE_API_KEY, Postgres/pgvector running)
"""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from anthropic import Anthropic
import rag_query

JUDGE_MODEL = "claude-sonnet-4-5"
QUESTIONS_FILE = Path(__file__).parent / "eval_questions.json"
RESULTS_FILE = Path(__file__).parent / "eval_results.json"
REPORT_FILE = Path(__file__).parent / "eval_report.md"

judge_client = Anthropic()

JUDGE_SYSTEM_PROMPT = """You are grading a RAG (retrieval-augmented generation) system's answer \
against a human-written reference answer for a project Q&A knowledge base.

Score the RAG answer on three dimensions, each 1-5 (5 = best):
- relevance: does the answer actually address what was asked?
- accuracy: does the answer's factual content match the reference answer (no wrong facts)?
- groundedness: is everything stated in the answer plausibly supported by the retrieved \
context chunks, i.e. no invented/hallucinated details not present in the context or reference?

For "trap" questions where the reference answer says the information isn't covered, a good \
RAG answer should say it doesn't know / isn't in the context. Score such an answer highly on \
groundedness and accuracy if it correctly declines to answer, and low if it fabricates an answer.

Respond ONLY with strict JSON, no markdown fences, in this exact shape:
{"relevance": <1-5>, "accuracy": <1-5>, "groundedness": <1-5>, "hallucinated": <true|false>, "notes": "<one short sentence>"}
"""


def judge_answer(question: str, reference_answer: str, rag_answer: str, retrieved_chunks: list) -> dict:
    context = "\n\n---\n\n".join(f"[{source}] {chunk[:300]}" for chunk, source, _ in retrieved_chunks)
    user_message = f"""Question: {question}

Reference (human-written) answer:
{reference_answer}

Retrieved context chunks given to the RAG system:
{context}

RAG system's actual answer:
{rag_answer}

Grade the RAG answer as instructed."""
    response = judge_client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=300,
        system=JUDGE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"relevance": None, "accuracy": None, "groundedness": None,
                 "hallucinated": None, "notes": f"JUDGE_PARSE_ERROR: {text[:200]}"}


def run_eval():
    questions = json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))
    results = []

    for i, q in enumerate(questions, 1):
        print(f"[{i}/{len(questions)}] {q['id']}: {q['question']}")
        retrieved = None
        for attempt in range(4):
            try:
                retrieved = rag_query.retrieve_top_chunks(q["question"], rag_query.TOP_K)
                break
            except Exception as e:
                if "rate limit" in str(e).lower() or "RPM" in str(e):
                    wait = 30 * (attempt + 1)
                    print(f"  rate limited, waiting {wait}s (attempt {attempt + 1}/4)...")
                    time.sleep(wait)
                    continue
                print(f"  RAG pipeline error: {e}")
                results.append({**q, "rag_answer": None, "retrieved_sources": [],
                                 "grade": {"relevance": None, "accuracy": None, "groundedness": None,
                                           "hallucinated": None, "notes": f"RAG_ERROR: {e}"}})
                break
        if retrieved is None:
            if not results or results[-1]["id"] != q["id"]:
                results.append({**q, "rag_answer": None, "retrieved_sources": [],
                                 "grade": {"relevance": None, "accuracy": None, "groundedness": None,
                                           "hallucinated": None, "notes": "RAG_ERROR: rate limited after retries"}})
            continue
        rag_answer = rag_query.generate_answer(q["question"], retrieved)

        grade = judge_answer(q["question"], q["reference_answer"], rag_answer, retrieved)
        results.append({
            **q,
            "rag_answer": rag_answer,
            "retrieved_sources": [f"{s} ({score:.3f})" for _, s, score in retrieved],
            "grade": grade,
        })
        print(f"  -> relevance={grade.get('relevance')} accuracy={grade.get('accuracy')} "
              f"groundedness={grade.get('groundedness')} hallucinated={grade.get('hallucinated')}")
        # Voyage AI free tier is capped at 3 requests/minute; pace embedding calls accordingly.
        time.sleep(25)

    RESULTS_FILE.write_text(json.dumps(results, indent=2), encoding="utf-8")
    write_report(results)
    print(f"\nSaved results to {RESULTS_FILE}")
    print(f"Saved report to {REPORT_FILE}")


def write_report(results: list):
    scored = [r for r in results if r["grade"].get("relevance") is not None]
    n = len(scored)

    def avg(key):
        vals = [r["grade"][key] for r in scored if r["grade"].get(key) is not None]
        return sum(vals) / len(vals) if vals else float("nan")

    hallucinated_count = sum(1 for r in scored if r["grade"].get("hallucinated") is True)

    lines = []
    lines.append("# RAG Eval Report — MidTenn Lend Map Knowledge Base\n")
    lines.append(f"Questions evaluated: {n}/{len(results)}\n")
    lines.append("## Aggregate Scores (1-5 scale)\n")
    lines.append(f"- Average relevance: {avg('relevance'):.2f}")
    lines.append(f"- Average accuracy: {avg('accuracy'):.2f}")
    lines.append(f"- Average groundedness: {avg('groundedness'):.2f}")
    lines.append(f"- Answers flagged as hallucinated: {hallucinated_count}/{n}\n")

    lines.append("## By Difficulty\n")
    difficulties = sorted(set(r["difficulty"] for r in results))
    for d in difficulties:
        subset = [r for r in scored if r["difficulty"] == d]
        if not subset:
            continue
        rel = sum(r["grade"]["relevance"] for r in subset) / len(subset)
        acc = sum(r["grade"]["accuracy"] for r in subset) / len(subset)
        gro = sum(r["grade"]["groundedness"] for r in subset) / len(subset)
        lines.append(f"- **{d}** (n={len(subset)}): relevance={rel:.2f}, accuracy={acc:.2f}, groundedness={gro:.2f}")

    lines.append("\n## Per-Question Results\n")
    lines.append("| ID | Difficulty | Category | Rel | Acc | Ground | Hallucinated | Notes |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for r in results:
        g = r["grade"]
        lines.append(
            f"| {r['id']} | {r['difficulty']} | {r['category']} | {g.get('relevance')} | "
            f"{g.get('accuracy')} | {g.get('groundedness')} | {g.get('hallucinated')} | {g.get('notes', '')} |"
        )

    lines.append("\n## Flagged Answers (relevance/accuracy/groundedness <= 3, or hallucinated)\n")
    flagged = [r for r in scored if r["grade"].get("hallucinated") or
               min(r["grade"]["relevance"], r["grade"]["accuracy"], r["grade"]["groundedness"]) <= 3]
    if not flagged:
        lines.append("None — all answers scored 4+ on every dimension.\n")
    else:
        for r in flagged:
            lines.append(f"### {r['id']}: {r['question']}")
            lines.append(f"- Reference: {r['reference_answer']}")
            lines.append(f"- RAG answer: {r['rag_answer']}")
            lines.append(f"- Grade: {r['grade']}\n")

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    run_eval()
