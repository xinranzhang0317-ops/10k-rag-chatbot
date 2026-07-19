# Challenges log

Everyone: append problems + fixes AS THEY HAPPEN. Member 6 mines this for the
challenges slide. Don't try to reconstruct it from memory on the 19th.

Format: what broke → what fixed it → what we learned.

---

## Environment: langchain version hell (Member 1, Jul 16)
**Broke:** `No module named 'langchain.chains'` even though langchain was
installed. Then `cannot import name 'content' from 'langchain_core.messages'`.
**Fixed:** langchain 1.3 removed `RetrievalQA` from `langchain.chains`. Pinned
the whole stack to 0.3.x in requirements.txt.
**Learned:** the starter code targets langchain 0.x. Mixing a 1.x sub-package
with a 0.x core breaks at import time. Pin everything together or nothing.

## Gemini embedding quota (Member 1, Jul 16)
**Broke:** `429 ... limit: 100, model: gemini-embedding-1.0` partway through
embedding a single 10-K.
**Fixed:** switched embeddings to local Ollama nomic-embed-text.
**Learned:** free-tier embed cap is 100 req/min. A 10-K makes far more chunks
than that. Raising chunk_size reduces requests but a full filing still risks it.
Local embeddings have no quota — slower, but they finish.

## Gemini generation quota returns limit: 0 (Member 1, Jul 16)
**Broke:** `429 ... limit: 0, model: gemini-2.0-flash` on every request.
**Fixed:** TBD — trying gemini-2.5-flash / falling back to local mistral.
**Learned:** `limit: 0` means no free-tier allowance for that model on this
project, not "you used it up." Waiting does nothing.

## ## Balanced retrieval silently wasn't balanced (Member 1, Jul 18)
**Broke:** Same comparison question returned different answers across runs —
12-13 chunks retrieved instead of the expected 30. Amazon's numbers randomly
missing despite existing in the index.
**Fixed:** LangChain's FAISS similarity_search with a filter fetches only the
top fetch_k candidates GLOBALLY (default 20), then filters by company. If a
company's chunks aren't in that global top-20, it gets starved. Set
fetch_k=2000 so each company's search sees the whole index.
**Learned:** metadata filtering in FAISS is post-hoc, not true partitioned
search. Verify chunk counts match expectations — the UI showing "6 × 5 = 30
chunks" while retrieving 12 was the tell.

## Three Gemini models died on us in one project (Member 1, Jul 16-18)
**Broke:** gemini-2.0-flash → quota limit: 0 (no free tier on our project).
embedding-001 → retired. gemini-2.5-flash and 2.5-flash-lite → "no longer
available to new users" (404) on a fresh API key.
**Fixed:** default to the gemini-flash-latest alias (hot-swaps to current
model), keep local Ollama one dropdown away as fallback.
**Learned:** never pin Gemini model names in a project with a deadline; free
tier availability differs by key age and project.

## Free tier = 20 requests/day per model (Member 1, Jul 18)
**Broke:** hit the daily cap mid-testing (GenerateRequestsPerDayPerModel = 20).
**Fixed:** test on local mistral, reserve Gemini quota for demo screenshots.
Each member makes their own free key (6 × 20/day). Fresh unspent key on
presentation day.
**Learned:** quota is a demo-day risk; rehearse the Ollama fallback switch.

## Gemini model roulette blocked the experiment harness (Member 2, Jul 17-18)
**Broke:** gemini-2.5-flash returned 404 "no longer available to new users" on a
fresh key — even though ListModels still listed it. gemini-3.5-flash worked,
then died at 20 requests/DAY (two tuning runs = 20 calls).
**Fixed:** froze all experiments on gemini-3.1-flash-lite (usable daily quota,
same model for every run so scores are comparable).
**Learned:** ListModels shows retired models — availability differs by key age.
For experiments, freeze one model that fits the quota math; the flash-latest
alias Andrea uses is right for the app, wrong for controlled comparisons.

## Gemini embeddings have a DAILY cap, not just per-minute (Member 2, Jul 17)
**Broke:** Stage B with Gemini embeddings 429'd at ~180 chunks, then again at
~90 more the next attempt, despite batching 90/min under the documented
100/min limit. Waiting a minute did nothing.
**Fixed:** substituted local mxbai-embed-large for the embedding comparison.
(Turned out to be the single biggest quality lever anyway.)
**Learned:** the free tier also caps embeddings around ~200/day. A 906-chunk
corpus can't be embedded free even with perfect rate limiting. ~$1 of billing
would unlock it — worth it if anyone wants the Gemini-embeddings datapoint.

## Ollama embedder dies on large payloads (Member 2, Jul 17)
**Broke:** `EOF` / connection reset on the tokenize port when embedding all
900+ chunks in one FAISS.from_documents call.
**Fixed:** batch 100 chunks per add_documents call. (Andrea independently
landed on batch 64 in app.py — either works.)
**Learned:** local embedders have memory limits instead of quotas. Batch
everything.

## Stale FAISS cache silently ignored ingestion changes (Member 2, Jul 18)
**Broke:** added page-text cleaning and statement tagging, re-ran, got
byte-identical answers — the changes appeared to do nothing.
**Fixed:** the cache key only encodes embeddings+chunk_size+overlap, so the
loader served the OLD index built from dirty, untagged text. `rm -rf` the
cache folder before any run after changing load/clean/tag logic.
**Learned:** metadata and cleaning bake in at index build time. If an
ingestion change "did nothing," suspect the cache before the change.

## The 10-K PDFs carry browser print headers in every page (Member 2, Jul 18)
**Broke:** cash-flow-statement chunks never ranked in retrieval; Q5/Q10
failed in 14 straight configs even with correct settings.
**Fixed:** regex-stripped the `2026/4/13 16:18` timestamps, sec.gov/Archives
URLs, and page-count artifacts stamped on every page (906 chunks vs 929
dirty). Amazon's exact capex ($131,819M) and cash-tax figures retrieved for
the first time immediately after.
**Learned:** identical boilerplate on every page drags all chunk embeddings
toward each other and drowns the signal. Clean before you embed — it beat
every parameter change we tried.

## fetch_k starvation hit the tuning harness too (Member 2, Jul 18)
**Broke:** three successive configs (statement tagging, broader markers,
doubled quota) returned chunk-for-chunk identical retrievals — parameter
changes provably did nothing.
**Fixed:** same root cause Andrea logged above: filtered similarity_search
only filters the global top-20 unless fetch_k is raised. Added fetch_k=2000;
the very next run retrieved Microsoft's tax reconciliation table for the
first time in 19 runs and fixed our own team question's Microsoft answer
(17.6%, not the 18% MD&A rounding).
**Learned:** independent replication of the fetch_k bug from a second
codebase — and the tell is different: not just wrong chunk counts, but
identical retrievals across configs that should differ. If tuning a
parameter changes nothing, the parameter isn't reaching the search.
