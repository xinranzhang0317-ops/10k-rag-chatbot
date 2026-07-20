# Tech Note — 10-K Comparison Chatbot

JHU-CDHAI Chatbot-AIEB Final Project

## Team

| Member | Role |
|---|---|
| Andrea Zhang (1) | UI/UX + Multi-Doc Architecture (Lead Engineer) |
| Angela Kim (2) | RAG Tuning |
| Xier Shen (3) | LLM Comparison |
| Aster (Wanqian) Xiong (4) | Prompt / Persona Engineering |
| Yiyun Wu (5) | Evaluation + Boundary Testing |
| Larisa Thai (6) | Tech Note + Presentation + Repo Hygiene |

## Approach

A Streamlit chatbot answering questions across Alphabet, Amazon, and
Microsoft's 10-K filings, built on top of the starter
`chat_with_pdf_gemini_with_history.py` script and extended for multi-document
comparison.

The single architectural problem the starter code doesn't solve: when you ask
a comparison question across three filings, a global top-k similarity search
can return 15 chunks from one company and zero from another, purely because
that company's phrasing happens to sit closer to the question in vector
space. The model then can't answer for the missing company, so it guesses.
The fix was to tag every chunk with its source company at ingestion time and
retrieve **k chunks per company** instead of top-k globally, guaranteeing
every selected company reaches the prompt.

## RAG Configuration

Final values, from Member 2's tuning experiments:

```python
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 150
K_PER_COMPANY = 8
DEFAULT_EMBEDDING = "Ollama (mxbai-embed-large)"
DEFAULT_LLM = "Gemini (gemini-flash-latest)"
```

Fourteen labeled experiments (A through L) moved the evaluation score from an
18.5/30 baseline to 30/30. Ranked by impact:

1. **Embedding model choice** — switching from `nomic-embed-text` to
   `mxbai-embed-large` gained 3 points on its own, more than any chunk-size
   change.
2. **Cleaning the PDF text** — every page of the source PDFs carried leftover
   browser-print boilerplate (timestamps, a sec.gov URL). This identical text
   on every page made all chunks look more similar to the embedder and buried
   the financial tables. Removing it recovered table chunks that 14 prior
   configurations had failed to retrieve.
3. **The `fetch_k` bug** — LangChain's FAISS similarity search with a
   metadata filter only searches the top `fetch_k` candidates globally
   (default 20) before filtering by company. If a company's chunks weren't in
   that global top-20, the per-company filter had nothing to return, so
   "balanced retrieval" was silently unbalanced. Setting `fetch_k=2000` fixed
   it. This is the strongest boundary/challenges story in the project — see
   below.
4. **Per-company retrieval and query expansion** — smaller individual gains,
   but necessary to reach full marks.
5. **Chunk size and k** — mattered least of the five levers tested, though
   500-character chunks and k=4 were unusable (too small to keep tables
   intact, too few chunks to guarantee coverage).

A secondary finding worth flagging in the presentation: how closely a
question's wording matched its target table's wording predicted success
better than any tuning parameter did. Questions with near-verbatim overlap
scored well even under the worst configuration; questions with little lexical
overlap were the last to reach full marks regardless of tuning.

## Model Choice

Four models were compared on the same 10-question evaluation set:
Gemini Flash (`gemini-flash-latest`), Mistral, Llama 3.1, and DeepSeek-R1.

| Model | Accuracy | Hallucination rate |
|---|---|---|
| Gemini Flash | 70% | 1/10 |
| Llama 3.1 | 66.7% | 3/10 |
| DeepSeek-R1 | 60% | 2/10 |
| Mistral | 50% | 5/10 |

**Recommended and default: Gemini Flash.** Full detail and the "why models
differ" analysis is in `results/llm_comparison.md` — briefly, the more
useful axis than raw accuracy is what a model does when evidence is
incomplete. Gemini Flash and DeepSeek-R1 were more likely to say the retrieved
evidence was insufficient; Mistral was the opposite, hallucinating on half
the question set, often by mixing fiscal years or inventing reconciling
figures. For a finance-facing tool, that failure mode matters as much as
accuracy does.

*Note on naming: the task list originally specified `gemini-2.5-flash`.
That model (and `2.5-flash-lite`) began returning 404s on fresh API keys
during testing, so the team standardized on the `gemini-flash-latest` alias
instead — see the Challenges section.*

## Prompt Engineering

Member 4 (Aster) ran a controlled A/B test: same retrieval settings, same
model (Gemini Flash), same 10 questions — the only variable changed was the
system prompt.

| Metric | Baseline prompt | Improved prompt |
|---|---:|---:|
| Total score | 13/30 | 21/30 |
| Average score | 1.3/3 | 2.1/3 |
| Correct citation/source | 2/10 | 7/10 |
| Hallucinations | 0 | 0 |

**The core change:** the baseline prompt issued a blanket refusal — *"I don't
have enough information in the filings to answer that"* — whenever any part
of a multi-company question was missing, even if two of the three companies'
data was fully available. The improved prompt instead requires the model to
answer every supported part first, then explicitly name what's missing,
rather than refusing the whole question. It also adds a required structure
(direct answer → evidence and calculations → limitations) and explicit rules
for handling proxies, ties, and forecasting/investment questions without
either fabricating a number or refusing outright.

**What this fixed, concretely:** on Q9 (revenue/profit leaders + investment
recommendation), the baseline scored 0 — it refused the entire question
rather than reporting the historical figures it had. The improved prompt
scored 3 — it reported Amazon as revenue leader and Alphabet as net-income
leader for both years, then correctly explained why "best investment" can't
be answered from 10-K data alone rather than either inventing an answer or
refusing everything.

**What it didn't fix:** Q1, Q5, and Q10 stayed low under both prompts (score
1, 1, 0) because the required figures simply weren't retrieved — the prompt
can only act on evidence it's given. This is the clean, useful distinction
for the presentation: **prompt engineering improves what the model does with
retrieved evidence; it cannot recover evidence that retrieval never surfaced.**
That's what Member 2's retrieval tuning is for, and it's why the two
workstreams are complementary rather than substitutes.

## Evaluation

A full verified ground-truth answer key for all 10 questions now exists in
`eval_questions.md`, with sourced figures, calculations, and common failure
modes documented per question. Worth highlighting in the presentation: two
of the ten questions (Q2 and Q5) have a **tie** in their correct answer —
e.g. Q2 asks for "the single disclosed factor" behind Amazon's and
Microsoft's tax-rate gap, but both companies disclose two reconciliation
items of equal magnitude. The answer key treats correctly identifying that
ambiguity as part of a full-credit answer, not a chatbot failure — a good
detail for the boundary-testing story, since it shows the evaluation itself
accounts for genuinely ambiguous questions rather than penalizing the bot
for not inventing false precision.

**Final result:** after merging Member 2's retrieval fixes into `app.py` (see
Boundary Testing below) and rebuilding the index, the full 10-question set was
rerun end-to-end and scored **30/30** — every question that had previously
lost points (the tax-rate figure in Q2, the false refusal on Q4, the missing
forecast caveat on Q6, and the unsupported inference on Q10) was resolved by
the same three retrieval changes. `results/scores.md` has the per-question
breakdown from Member 5.

## Boundary Testing / Hallucination Case

**Case: unsupported inference on AI/cloud capex (Q10) — found, then fixed**

Question: sum capital expenditures across Alphabet, Amazon, and Microsoft,
compute capex as a percentage of revenue, and identify which company is
investing most aggressively in AI/cloud infrastructure on a relative basis.

**Original behavior (pre-fix):** the chatbot's arithmetic was correct —
Microsoft ~22.9% of revenue, Alphabet ~22.7%, Amazon ~18.4% — but it then
concluded Microsoft was "investing most aggressively in AI/cloud
infrastructure." The 10-Ks only disclose **company-wide** capex; they don't
break out AI/cloud-specific spending. The model presented an inference as if
it were a fact directly stated in the filings.

- **Failure type:** unsupported inference (not a factual/arithmetic error)
- **Hallucination:** yes — scored 2/3 in initial evaluation

**Why this case mattered:** it showed that correct retrieval and correct
math don't guarantee a reliable conclusion — a model can still overreach in
how it interprets numbers it retrieved accurately. This is a subtler and
more instructive failure than the fabricated-numbers hallucinations logged
elsewhere (see Model Choice section above).

**Fix and outcome:** three pieces of Member 2's retrieval work — PDF header
cleaning, statement-page tagging with a targeted second search, and a
pinned-page fallback for tables that lose even that search — had been
validated in her tuning experiments but not yet merged into `app.py`. Once
merged and the index rebuilt, the same question was rerun: the chatbot now
explicitly states that no company discloses AI/cloud-specific capex and
flags total capex as a proxy rather than presenting the ranking as a direct
fact. Full evaluation rerun after the fix scored **30/30**, up from 24/30 on
the same integrated app before the merge — every question that had lost
points (Q2's tax rate, Q4's false refusal, Q6's incomplete forecast caveat,
Q10's unsupported inference) was resolved by the same three changes.

**How this was reduced:**
1. Cleaning PDF text so financial tables aren't buried in vector-similarity
   noise from repeated print headers
2. A second, targeted search over pages tagged as core financial statements,
   since number-heavy tables often don't lexically resemble the question
3. A small pinned-page fallback for tables that still lose both searches
4. The underlying principle that generalizes beyond this fix: require the
   model to distinguish directly-reported facts from calculated values from
   inferred conclusions, and add an explicit caveat whenever a requested
   metric isn't separately disclosed

## Challenges

Full log in `results/challenges.md`. Highlights:

- **langchain version mismatch** — the starter code targets langchain 0.x;
  1.x removed `RetrievalQA` from `langchain.chains`. Pinned the full stack to
  0.3.x in `requirements.txt`.
- **Gemini quota confusion** — embedding requests capped at 100/minute
  (and ~200/day) with a full 10-K producing 906 chunks, guaranteeing a wall
  no matter how requests are spaced. Switched to local Ollama embeddings,
  which have no quota but do have memory limits (large batches crash the
  embedder — fixed by batching in groups of 64–100).
- **`limit: 0` from Gemini isn't a rate limit** — it means the project has no
  free-tier allowance for that model at all. Multiple Gemini models (2.0-flash,
  2.5-flash, 2.5-flash-lite) became unavailable mid-project for this reason,
  which is why the app defaults to the `gemini-flash-latest` alias instead of
  a pinned model name.
- **The `fetch_k` bug** (see RAG Configuration above) — the single most
  instructive failure of the project: balanced retrieval looked correct in
  the code but was silently starving companies out of context due to FAISS's
  post-hoc metadata filtering. Caught independently by two team members from
  two different angles (inconsistent chunk counts in the app; identical
  results across supposedly-different tuning runs in experiments).
- **Stale index cache** — code changes to text cleaning had no visible effect
  because the cached FAISS index only keys off embedding model and chunk
  settings, not text-processing changes. Any change to loading/cleaning logic
  requires deleting the cache to take effect.

## Known Limitations

- **The pinned statement pages are tuned to these exact three PDFs.** Runs
  K–L in the RAG tuning experiments added a fixed list of core financial
  statement pages per company, chosen by hand after failure analysis on
  this specific corpus. That list would need to be rebuilt for any other
  set of 10-Ks — it is not a general retrieval improvement, it's a
  targeted fix for two Microsoft table pages that lost even the
  statement-slot search on this dataset. We're disclosing this directly
  because it's a more honest read on the result than letting a 30/30 score
  imply the tuning generalizes.
- Latency was not captured in the LLM comparison and is a documented gap
  rather than an estimated figure.
- Runs K–L combine retrieval changes with prompt rules and the pinned-page
  list above, so they represent an integrated prototype rather than
  isolated retrieval tuning — the integrated app should be spot-checked
  against the 10 questions once more before the final recording.
- Each tuning configuration was run once; score differences under roughly
  one point should be treated as noise rather than a real effect.
