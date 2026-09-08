"""
dashboard_insights.py
Week 3 deliverable — AI-Enhanced Analytics Engineer project (MidTenn Lend Map)

Generates natural-language insight summaries from SBA loan KPI snapshots,
intended to be embedded in a Power BI dashboard (e.g. via a text/HTML visual
fed by this script's output).

Usage:
    python dashboard_insights.py

Requires:
    pip install anthropic python-dotenv
    An ANTHROPIC_API_KEY set as an environment variable (or in a local .env file)
"""

import os
import json
from typing import Dict, Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv is optional — script still works if ANTHROPIC_API_KEY is set another way
    pass

from anthropic import Anthropic

client = Anthropic()  # reads ANTHROPIC_API_KEY from environment

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """You are a data analyst writing a short insight summary for a business \
audience who will read it directly on a dashboard. Rules:
- Use ONLY the numbers provided in the KPI snapshot. Never invent, estimate, or extrapolate \
any figure that isn't given to you.
- Write 3 to 5 sentences, plain business language, no jargon, no SQL/technical terms.
- Lead with the most important or surprising change first.
- If a metric shows a notable increase or decrease, name a plausible business implication, \
but clearly frame it as an observation, not a certainty.
- Do not use bullet points. Write flowing prose.
- Do not repeat the raw JSON back to the reader."""

# Two few-shot examples reused from the Week 1 prompt-engineering benchmark,
# since few-shot outperformed zero-shot and CoT there for this kind of
# structured-data-to-summary task.
FEW_SHOT_EXAMPLES = [
    {
        "role": "user",
        "content": json.dumps({
            "period": "2026-06",
            "total_loans": 298,
            "total_amount": 38500000,
            "avg_loan_size": 129194,
            "top_industry": "Retail Trade",
            "mom_change_pct": -3.1
        })
    },
    {
        "role": "assistant",
        "content": (
            "Loan activity cooled slightly in June, with total lending volume down 3.1% "
            "from the prior month. The portfolio remained anchored by 298 loans totaling "
            "$38.5 million, at an average size of about $129,000 per loan. Retail Trade "
            "held its position as the top industry this period. The modest pullback is "
            "worth watching next month to see if it reflects a short-term dip or the start "
            "of a slower lending trend."
        )
    },
]


def generate_insight(kpi_snapshot: Dict[str, Any]) -> str:
    """
    Given a dict of KPI values for a reporting period, return a natural-language
    insight summary suitable for display on a Power BI dashboard.
    """
    messages = FEW_SHOT_EXAMPLES + [
        {"role": "user", "content": json.dumps(kpi_snapshot)}
    ]

    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    return response.content[0].text.strip()


if __name__ == "__main__":
    # Test scenarios covering growth, decline, and an anomaly case
    test_snapshots = [
        {
            "period": "2026-08",
            "total_loans": 342,
            "total_amount": 45200000,
            "avg_loan_size": 132163,
            "top_industry": "Food Services",
            "mom_change_pct": 12.4
        },
        {
            "period": "2026-09",
            "total_loans": 210,
            "total_amount": 51000000,
            "avg_loan_size": 242857,
            "top_industry": "Construction",
            "mom_change_pct": -38.7
        },
        {
            "period": "2026-07",
            "total_loans": 305,
            "total_amount": 39800000,
            "avg_loan_size": 130492,
            "top_industry": "Health Care and Social Assistance",
            "mom_change_pct": 2.3
        },
    ]

    for snapshot in test_snapshots:
        print(f"\n--- Period: {snapshot['period']} ---")
        insight = generate_insight(snapshot)
        print(insight)