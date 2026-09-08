# MidTenn Lend Map

A data engineering capstone project that transforms public financial and demographic data into actionable small business lending intelligence for Middle Tennessee community banks.

## What is This Project?

Middle Tennessee has emerged as one of the fastest-growing economic regions in the U.S. Nashville consistently ranks among the top cities for startups, and the broader region has seen significant growth over the past 5 years, with major companies like Oracle, Amazon, and AllianceBernstein relocating here.

Yet local banks still rely heavily on relationships and intuition to find small business loan customers. **MidTenn Lend Map** changes that — by integrating five public data sources into a unified analytics platform, it helps community banks like Wilson Bank and Trust identify where lending demand is growing, which markets are underserved, and where the best opportunities are across Middle Tennessee counties.

Data sources include:

- **FRED (Federal Reserve)** — Interest rates and macroeconomic indicators
- **SBA (Small Business Administration)** — Small business loan approvals by region and industry
- **CFPB** — Consumer financial complaints across Middle Tennessee
- **FDIC** — Bank distribution, market share, and financial health
- **U.S. Census Bureau** — Income, poverty rate, and business demographics by county

The result: a continuously updated platform that turns open government data into a competitive intelligence tool for lending teams.

## System Architecture

| Technology | Purpose/Role |
|------------|--------------|
| **Python** | Main programming language |
| **Prefect** | Workflow orchestration and scheduling |
| **MinIO** | Object storage (S3-compatible) for raw data lake |
| **DuckDB** | High-performance analytical query engine |
| **SQLMesh** | ELT transformations across Bronze / Silver / Gold layers |
| **Metabase** | BI dashboards and interactive visualizations |
| **Docker** | Containerization and local environment |
| **pytest** | Unit testing framework |

## Medallion Architecture

```
Raw APIs → MinIO (raw lake) → DuckDB + SQLMesh (Bronze → Silver → Gold) → PostgreSQL → Metabase
```

- **Bronze Layer**: Raw data ingested from APIs, stored as-is in DuckDB
- **Silver Layer**: Cleaned, standardized, and deduplicated data
- **Gold Layer**: Business-ready aggregations (loan volume by county, approval rates by industry, etc.)

## Key Insights Delivered

- 📍 **Opportunity Heat Map** — Which Middle Tennessee counties have the highest unmet small business lending demand
- 🏭 **Target Industry Segments** — Which industries have the highest approval rates and growth trajectories
- 🏦 **Competitive White Space** — Where rivals are underrepresented, revealing first-mover opportunities
- ⚠️ **Risk Intelligence** — High-complaint areas and macro risk signals overlaid with opportunity data
- 📈 **Growth Trend Forecasting** — Forward-looking analysis based on population, income, and economic activity

## Installation & Local Development

1. **Clone the repository**:
```bash
git clone https://github.com/YOUR_USERNAME/MidTenn-Lend-Map.git
cd MidTenn-Lend-Map
```

2. **Install dependencies with uv**:
```bash
pip install uv        # one-time: install uv itself
uv sync               # creates .venv and installs all dependencies
```

4. **Set up environment variables**:
```bash
cp .env.example .env
# Fill in your API keys in .env
```

5. **Start services with Docker Compose**:
```bash
docker compose up -d
```

6. **Run unit tests**:
```bash
uv run pytest
```

7. **Run the Prefect pipeline locally**:
```bash
export PREFECT_API_URL="http://localhost:4200/api"
uv run python src/pipeline/main_flow.py
```

8. **Access dashboards**:
- Prefect UI: http://localhost:4200
- MinIO Console: http://localhost:9001
- Metabase: http://localhost:3001

9. **Stop services**:
```bash
docker compose down
```

## Project Structure

```
MidTenn-Lend-Map/
├── .env.example          # Environment variable template
├── .gitignore
├── docker-compose.yml
├── pyproject.toml
├── README.md
├── src/
│   ├── ingestion/        # API ingestion scripts (FRED, SBA, CFPB, FDIC, Census)
│   ├── models/           # SQLMesh Bronze / Silver / Gold models
│   └── pipeline/         # Prefect flow definitions
└── tests/                # pytest unit tests
```

## AI-Enhanced Analytics Layer 🚧

Building three AI capability layers on top of the existing gold-layer data:

### Week 1: Prompt Engineering Foundations 
See companion project: [prompt-comparison-benchmark](https://github.com/Ashleysdata/prompt-comparison-benchmark)

### Week 2: Text-to-SQL Layer 
Added `text_to_sql.py` — translates natural language questions into DuckDB SQL 
queries against the gold-layer tables (loan_health, risk_signals, county_demographics), 
executes them, and returns results.

**Example:**
- Q: "Which county has the most loans with a delinquent or charged-off status?"
- Generated SQL: `SELECT county FROM gold.loan_health WHERE loan_status = 'CHGOFF' GROUP BY county ORDER BY SUM(total_loans) DESC LIMIT 1`
- A: Rutherford County

### Week 3: AI Dashboard Insights 
Added `dashboard_insights.py` — generates natural-language insight summaries 
from SBA loan KPI snapshots (loan volume, average loan size, top industry, 
month-over-month change), intended for embedding in a Power BI dashboard visual.

**Example:**
- Input: `{"period": "2026-09", "total_loans": 210, "total_amount": 51000000, 
  "avg_loan_size": 242857, "top_industry": "Construction", "mom_change_pct": -38.7}`
- Output: "September saw a dramatic 38.7% decline in loan volume from August, 
  dropping to just 210 loans, though the story is more nuanced than it first 
  appears. Despite fewer transactions, total lending actually increased to 
  $51 million because average loan size nearly doubled to roughly $243,000..."


### Week 4: RAG Knowledge Base 
Added `build_knowledge_base.py` and `rag_query.py` — chunks project documentation, 
generates embeddings via Voyage AI, and retrieves relevant context to answer 
natural-language questions about the project using Claude.

**Example:**
- Q: "What data sources does this project use?"
- A: Correctly identified all five data sources (FRED, SBA, CFPB, FDIC, Census) 
  with their specific roles, grounded entirely in the README content.

## Data Coverage

**Geographic Focus**: Middle Tennessee
- Davidson County (Nashville)
- Williamson County (Franklin, Brentwood)
- Rutherford County (Murfreesboro)
- Montgomery County (Clarksville)

**Time Range**: 2019 – Present (5-year window capturing post-COVID growth surge)

RAG retrieval now uses PostgreSQL + pgvector for similarity search (previously local numpy cosine similarity over a saved .npz file), moving the knowledge base from a local file to a queryable vector database.