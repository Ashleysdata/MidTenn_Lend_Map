import duckdb
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment
con = duckdb.connect('db/midtenn.duckdb')

SCHEMA_CONTEXT = """
You can query the following DuckDB tables (gold schema):

gold.risk_signals(county, product, total_complaints, timely_responses, disputed_complaints, dispute_rate_pct, timely_response_rate_pct)

gold.loan_health(county, naics_description, loan_status, total_loans, total_amount, pct_of_county_loans)
-- loan_status values: 'PIF' (paid in full), 'NOT FUNDED', 'COMMIT' (committed), 'CANCLD' (cancelled), 'CHGOFF' (charged off / defaulted), 'EXEMPT'

gold.county_demographics(county, year, total_population, median_household_income, poverty_rate_pct, unemployment_rate_pct, prev_year_population, population_growth_pct)
"""

def question_to_sql(question: str) -> str:
    prompt = f"""{SCHEMA_CONTEXT}

Translate the following natural language question into a single DuckDB SQL query. Return only the SQL — no explanation, no markdown code fences.

Question: {question}
SQL:"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    sql = response.content[0].text.strip()
    # strip any leftover markdown fences
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql

def run_question(question: str):
    print(f"\nQuestion: {question}")
    sql = question_to_sql(question)
    print(f"Generated SQL:\n{sql}")
    try:
        result = con.execute(sql).fetchdf()
        print(f"\nResult:\n{result}")
    except Exception as e:
        print(f"Execution error: {e}")

if __name__ == "__main__":
    test_questions = [
        "Which county has the most loans with a delinquent or charged-off status?",
        "Which county has the highest unemployment rate?",
        "Which county has the highest complaint dispute rate?",
    ]
    for q in test_questions:
        run_question(q)