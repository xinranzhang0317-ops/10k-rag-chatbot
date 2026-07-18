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
