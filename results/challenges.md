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

## (add yours below)
