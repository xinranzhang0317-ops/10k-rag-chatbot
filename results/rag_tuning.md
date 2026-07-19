# RAG tuning results — Member 2
## Summary: Config.py values to apply (Member 1)
```python
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 150
K_PER_COMPANY = 8

# add to EMBEDDING_OPTIONS:
"Ollama (mxbai-embed-large)": {"provider": "ollama", "model": "mxbai-embed-large"},

# change default:
DEFAULT_EMBEDDING = "Ollama (mxbai-embed-large)"
```
- One-time setup per machine: `ollama pull mxbai-embed-large`
- app.py: raise the k slider's max_value (8 is currently the ceiling)
- Demo build: copy 3 code blocks from experiments/m2_tuning.py into app.py for better performance(the config.py values above alone = 23/30; with these = 30/30):
  1. **clean_page_text** → apply per page in load_and_tag
  2. **STATEMENT_MARKERS** + its if-line → same page loop
  3. **PINNED_PAGES** + statement-slot search → chat handler after the per-company search

## Method
Each experiment tested one retrieval configuration by asking the same 10 evaluation questions (eval_questions.md) and scoring every answer 0–3 against
Member 5's answer key. Maximum score is 30. Eight of the questions mainly test retrieval quality; that sub-score (max 24) is shown in parentheses.

Experiments are labeled A through L in the order they were run. A is the baseline grid (9 combinations of chunk size and k). Each later experiment changed one thing at a time and kept everything that worked. The corpus was the three companies used in the evaluation questions (Alphabet, Amazon, Microsoft). The language model was fixed to gemini-3.1-flash-lite at temperature 0 for every run, so score differences come only from retrieval changes. Full per-question scores are in experiments/m2_scores.py, and the script is experiments/m2_tuning.py.

## Results
| Run | chunk_size | overlap | Retrieval design | Embedding | Score | Notes |
|---|---|---|---|---|---|---|
| — | 2000 | 200 | 3 per company | nomic | not tested | current config.py values |
| A | 500 | 50 | top 4 overall | nomic | 9.5/30 | worst tier; small chunks cut tables apart mid-figure |
| A | 500 | 50 | top 15 overall | nomic | 14/30 | |
| A | 1000 | 100 | top 4 overall | nomic | 8.5/30 | retrieving only 4 chunks often left whole companies out |
| A | 1000 | 100 | top 15 overall | nomic | 18/30 | |
| A | 1500 | 150 | top 15 overall | nomic | 18.5/30 (14/24) | best baseline |
| B | 1500 | 150 | top 15 overall | mxbai-embed-large | 21.5/30 (16/24) | changing only the embedding model gained 3 points |
| C | 1500 | 150 | top 15 overall | mxbai + query expansion | 24/30 (18/24) | financial keywords appended to the search query |
| D | 1500 | 150 | 5 per company | mxbai | 22.5/30 (16.5/24) | separate search per company |
| E | 1500 | 150 | 8 per company | mxbai + expansion | 23.5/30 (17.5/24) | C and D combined |
| F | 1500 | 150 | 8 per company | mxbai + page cleaning | 24/30 (18.5/24) | removed print headers from every PDF page; first run to find Amazon's exact capex and cash-tax figures |
| G–I | 1500 | 150 | 8 per company + statement slots | mxbai | 24.5/30 (19/24) | three runs produced identical results — caused by the fetch_k bug (see challenges.md) |
| J | 1500 | 150 | 8 per company + statement slots | mxbai + fetch_k=2000 | 26.5/30 (20.5/24) | first run to retrieve Microsoft's tax reconciliation table |
| K | 1500 | 150 | J + pinned pages | mxbai + answer rules in prompt | 29/30 (23.5/24) | |
| L | 1500 | 150 | same as K | K + revised tie-checking rule | 30/30 (24/24) | all 10 questions answered fully correctly |

- *"top N overall": one search across all three filings mixed together, keeping the N most similar chunks. This is the starter-code behavior. Its weakness: a comparison question can come back with 15 Amazon chunks and zero Alphabet chunks, and the model then cannot answer for Alphabet.*
- *"N per company": a separate search for each company, N chunks each, so every company always appears in the context.*
- *"statement slots": pages containing the core financial tables (income statement, cash flow statement, tax and segment tables) are labeled during loading, and a second search limited to those labeled pages adds extra chunks per company. Number-heavy tables rarely resemble the question text, so they kept losing the normal search to prose sections.*
- *"pinned pages": a short fixed list of core statement pages per company is always included in the context, with no search involved. This was needed for two Microsoft table pages that lost even the statement-slot search.*

## Recommended config.py values
- CHUNK_SIZE = 1500, CHUNK_OVERLAP = 150 (best of the tested values 500, 1000, 1500; the current 2000 was not part of the tested grid)
- K_PER_COMPANY = 8 (the sidebar slider maximum needs raising)
- Add mxbai-embed-large to EMBEDDING_OPTIONS and make it the default. This was the single largest quality improvement. Requires each member to run `ollama pull mxbai-embed-large` once.
- Keep fetch_k=2000 on every filtered search. app.py already does this; runs G–I independently demonstrated why it is necessary.
- Apply the ingestion steps from experiments/m2_tuning.py: page-header cleaning, statement-page labeling, statement slots, and (for the demo) the pinned page list.

## Findings
1. Ranked by impact: embedding model choice > cleaning the PDF text > the fetch_k fix > per-company retrieval and query expansion > chunk size and k. Within the baseline grid, larger chunks and larger k were always better; 500-character chunks and k=4 were unusable.
2. How closely the question's wording matches the target table's wording predicted success better than any parameter. Q3, whose wording appears verbatim in the table it needs, scored 3/3 in every run including the worst. Q5, Q8, and Q10, whose wording shares little with their target tables, were the last to reach full marks.
3. The 10-K PDFs carry browser print headers (timestamps and URLs) on every page. This identical text on every page made all chunks look more alike to the embedding model and buried the financial tables. Removing it (run F) recovered table chunks that 14 prior configurations had failed to retrieve.
4. Four cases were documented where the model produced a wrong number by doing arithmetic on incomplete context: summing part of a table as if it were the total, deriving a figure not present in the text, and attributing one company's figure to another. These motivated the answer rules added in runs K–L. The rule that resolved tie-reporting: require the model to list every line item with its magnitude before comparing, rather than asking it to "check for ties" in the abstract.
5. Correction to the answer key, confirmed independently by Member 4's prompt test: Microsoft's effective tax rate per its reconciliation table is 17.6% (a 3.4-point difference from the statutory rate), not the rounded 18% stated in the MD&A section.
6. Caveats: each configuration was run once, so differences under about one point should be treated as noise. Runs K and L combine retrieval changes with prompt rules and a page list chosen from failure analysis, so they are an integrated prototype rather than pure retrieval tuning, and the integrated app should be re-tested on the 10 questions before the demo recording.
