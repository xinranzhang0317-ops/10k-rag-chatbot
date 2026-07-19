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

## Addition to the Gemini quota entries above: embeddings also have a daily cap (Member 2, Jul 17)
**Broke:** Building the search index with Gemini embeddings failed with quota errors after about 180 chunks, and again after about 90 more the next day, even while staying under the documented limit of 100 requests per minute. Waiting between attempts did not help.
**Fixed:** We switched the embedding comparison to a local model, mxbai-embed-large through Ollama, which has no quota.
**Learned:** On top of the per minute limit Member 1 logged above, the free tier also caps embeddings at roughly 200 requests per day. Our corpus produces 906 chunks, so it cannot be embedded for free no matter how the requests are spaced. Enabling billing for roughly one dollar would remove the limit if anyone wants the Gemini embeddings comparison later. Additionally, we froze all runs on a single model, gemini-3.1-flash-lite, so that scores stay comparable. The gemini-flash-latest alias is right for the app but wrong for experiments, because the model behind it can change between runs.

## The local Ollama embedder crashes when given too much at once (Member 2, Jul 17)
**Broke:** Sending all 900 plus chunks to the Ollama embedder in one call dropped the connection with an end of file error partway through.
**Fixed:** We split the work into batches of 100 chunks per call. Member 1 independently settled on batches of 64 in the app. Either size works.
**Learned:** Local embedding models have no quotas, but they do have memory limits. Any large embedding job should be sent in batches.

## A saved index silently ignored our code changes (Member 2, Jul 18)
**Broke:** We added code that cleans the PDF text and labels the financial statement pages, ran the experiment again, and got answers completely identical to the previous run. It looked like our changes did nothing.
**Fixed:** The cause was the cache. The script saves the finished search index to disk and reloads it to save time, and the cache name only reflects the embedding model and chunk settings, not the text processing. So the script kept loading the old index built from the uncleaned text. Deleting the cache folder before rerunning fixed it.
**Learned:** Text cleaning and page labels are baked into the index when it is built. If a change to loading or cleaning code appears to have no effect, delete the cached index before assuming the change failed.

## The 10-K PDFs have browser print headers on every page (Member 2, Jul 18)
**Broke:** The chunks containing the cash flow statements almost never came back from the search, so the questions about cash taxes and capital spending failed in 14 configurations in a row, even with otherwise correct settings.
**Fixed:** Every page of the PDFs carries leftover text from being printed from a web browser, including a timestamp and a sec.gov address. We added a cleaning step that removes those lines before indexing. Immediately afterward, the search returned Amazon's exact capital expenditure and cash tax figures for the first time.
**Learned:** Identical boilerplate on every page makes all chunks look more similar to each other in the index, which drowns out the content that matters. Cleaning the text before indexing improved results more than any setting we tuned.

## Confirmation of the fetch_k bug above, seen from a different angle (Member 2, Jul 18)
**Broke:** In our tuning experiments, three configurations in a row with different retrieval settings returned exactly the same chunks for every question. Changing settings provably did nothing.
**Fixed:** Same root cause and same fix as Member 1's entry above: setting fetch_k to 2000 so the filtered search considers the whole index. On the very next run the search returned Microsoft's tax reconciliation table for the first time in 19 runs, which corrected the Microsoft part of our own team's question. The correct effective tax rate is 17.6 percent from the table, not the rounded 18 percent from the narrative section.
**Learned:** The bug shows up differently depending on where you meet it. In the app the clue was wrong chunk counts. In experiments the clue was identical results across settings that should differ. If tuning a parameter changes nothing at all, the parameter is probably not reaching the search.
