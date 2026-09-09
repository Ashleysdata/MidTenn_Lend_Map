# RAG Eval Report — MidTenn Lend Map Knowledge Base

Questions evaluated: 10/10

## Aggregate Scores (1-5 scale)

- Average relevance: 5.00
- Average accuracy: 5.00
- Average groundedness: 4.40
- Answers flagged as hallucinated: 3/10

## By Difficulty

- **easy** (n=2): relevance=5.00, accuracy=5.00, groundedness=4.00
- **hard** (n=3): relevance=5.00, accuracy=5.00, groundedness=4.33
- **medium** (n=4): relevance=5.00, accuracy=5.00, groundedness=4.50
- **trap** (n=1): relevance=5.00, accuracy=5.00, groundedness=5.00

## Per-Question Results

| ID | Difficulty | Category | Rel | Acc | Ground | Hallucinated | Notes |
|---|---|---|---|---|---|---|---|
| q1 | easy | data_sources | 5 | 5 | 3 | True | Answer is relevant and accurate but includes specific details about what each source provides that aren't visible in the retrieved context chunks. |
| q2 | easy | architecture | 5 | 5 | 5 | False | Perfect answer with correct tool name and well-grounded supporting details from context. |
| q3 | medium | architecture | 5 | 5 | 5 | False | Perfectly addresses the question with accurate layer distinctions fully supported by context. |
| q4 | medium | installation | 5 | 5 | 3 | True | Answer is correct (port 3001) but the supporting quote doesn't appear complete in the provided context chunks. |
| q5 | medium | ai_layer | 5 | 5 | 5 | False | Perfect match with reference answer, all details supported by context including example query. |
| q6 | medium | structure | 5 | 5 | 5 | False | Answer correctly identifies src/models/ location matching the reference answer, fully supported by the retrieved context. |
| q7 | hard | data_coverage | 5 | 5 | 3 | True | Answer is relevant and accurate but includes specific city names and county details not present in the provided context chunks. |
| q8 | hard | example | 5 | 5 | 5 | False | Answer correctly identifies Rutherford County and accurately explains all SQL operations from the context. |
| q9 | hard | companion_project | 5 | 5 | 5 | False | Answer correctly identifies Week 1 as Prompt Engineering Foundations and references the companion project under Ashleysdata on GitHub. |
| q10 | trap | out_of_scope | 5 | 5 | 5 | False | Correctly identifies the information is not in the context and declines to fabricate an answer. |

## Flagged Answers (relevance/accuracy/groundedness <= 3, or hallucinated)

### q1: What data sources does this project use?
- Reference: FRED (interest rates and macroeconomic indicators), SBA (small business loan approvals by region/industry), CFPB (consumer financial complaints), FDIC (bank distribution, market share, financial health), and U.S. Census Bureau (income, poverty rate, business demographics by county).
- RAG answer: According to the excerpts, **MidTenn Lend Map** integrates five public data sources:

1. **FRED (Federal Reserve)** — Interest rates and macroeconomic indicators
2. **SBA (Small Business Administration)** — Small business loan approvals by region and industry
3. **CFPB (Consumer Financial Protection Bureau)** — Consumer financial complaints across Middle Tennessee
4. **FDIC (Federal Deposit Insurance Corporation)** — Bank distribution, market share, and financial health
5. **U.S. Census Bureau** — Income, poverty rate, and business demographics by county

These sources are ingested into the system and transformed through a medallion architecture (Bronze → Silver → Gold layers) to create actionable lending intelligence.
- Grade: {'relevance': 5, 'accuracy': 5, 'groundedness': 3, 'hallucinated': True, 'notes': "Answer is relevant and accurate but includes specific details about what each source provides that aren't visible in the retrieved context chunks."}

### q4: What port does Metabase run on locally?
- Reference: http://localhost:3001
- RAG answer: According to the README.md, Metabase runs on **port 3001** locally.

The documentation states: "Metabase: http://localhost:3001"
- Grade: {'relevance': 5, 'accuracy': 5, 'groundedness': 3, 'hallucinated': True, 'notes': "Answer is correct (port 3001) but the supporting quote doesn't appear complete in the provided context chunks."}

### q7: Which counties are covered geographically, and what time range does the data span?
- Reference: Geographic focus: Davidson County (Nashville), Williamson County (Franklin, Brentwood), Rutherford County (Murfreesboro), and Montgomery County (Clarksville). Time range: 2019-Present, a 5-year window capturing the post-COVID growth surge.
- RAG answer: Based on the provided excerpts, the **MidTenn Lend Map** project covers:

## Geographic Coverage (Middle Tennessee)
- **Davidson County** (Nashville)
- **Williamson County** (Franklin, Brentwood)
- **Rutherford County** (Murfreesboro)
- **Montgomery County** (Clarksville)

## Time Range
**2019 – Present** (described as a "5-year window capturing post-COVID growth surge")
- Grade: {'relevance': 5, 'accuracy': 5, 'groundedness': 3, 'hallucinated': True, 'notes': 'Answer is relevant and accurate but includes specific city names and county details not present in the provided context chunks.'}
