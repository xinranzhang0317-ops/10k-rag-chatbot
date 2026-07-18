# 10-K Comparison Chatbot

RAG chatbot comparing Alphabet, Amazon, and Microsoft 10-K filings.
JHU-CDHAI Chatbot-AIEB final project.

## Setup

```bash
conda activate chatbot
python -m pip install -r requirements.txt

cp .env.example .env        # then paste your Gemini key into .env
```

Put the three 10-K PDFs in `data/`, named exactly:

```
data/alphabet_10k.pdf
data/amazon_10k.pdf
data/microsoft_10k.pdf
```

Run:

```bash
streamlit run app.py
```

First run embeds all three filings and takes a few minutes. The index is cached
to disk after that, so restarts are instant. Changing the embedding model or
chunk size rebuilds it; changing the LLM does not.

## What's different from the starter code

The starter code retrieves the global top-k chunks across all filings. Ask
"which company has the highest cloud revenue?" and you can get 5 chunks from
Amazon and none from Alphabet, purely because Amazon's phrasing sat closer to
the question in vector space. The model then can't answer — so it guesses.

We tag every chunk with its source company and retrieve **k chunks per company**,
guaranteeing every selected company reaches the prompt. Run `python
test_retrieval.py` to see the difference in distribution.

## Who edits what

Merge conflicts are the enemy on a 3-day timeline. Stay in your lane:

| File | Owner |
|---|---|
| `app.py`, `config.py`, `README.md` | Member 1 (Andrea) |
| `prompts.py` | Member 4 — nobody else |
| `experiments/`, `results/rag_tuning.md` | Member 2 |
| `experiments/`, `results/llm_comparison.md` | Member 3 |
| `eval_questions.md`, `results/scores.md` | Member 5 |
| `TECH_NOTE.md`, `.gitignore` | Member 6 |

**Members 2 and 3: do not edit `app.py`.** Run your experiments in a notebook,
report the winning numbers, and Member 1 applies them to `config.py`.

## Setup gotchas (read before you burn an afternoon)

These all cost us real time already:

- **Use `python -m pip`, not `pip`.** Plain `pip` can install into a different
  Python than the one running the app, so the package installs "successfully"
  and the import still fails.
- **Activate the env first.** `zsh: command not found: streamlit` almost always
  means you're in `(base)`, not `(chatbot)`.
- **Don't unpin langchain.** langchain 1.x removed `RetrievalQA` from
  `langchain.chains` and moved things in `langchain_core.messages`. Symptoms:
  `No module named 'langchain.chains'`, or `cannot import name 'content' from
  'langchain_core.messages'`. The pins in `requirements.txt` exist for this.
- **Gemini's `embedding-001` is retired.** Use `models/gemini-embedding-001`.
- **Gemini free tier caps embedding at 100 requests/minute.** A full 10-K blows
  past it. That's why we default to local Ollama embeddings. Each retry burns
  more quota, so waiting a full minute between attempts matters.
- **`limit: 0` from Gemini is not a rate limit.** It means that model has no
  free-tier allowance on your project at all — waiting won't help. Try
  `gemini-2.5-flash`, or switch the LLM to Ollama in the sidebar.
- **Ollama must be running** or you get `connection refused` on port 11434.
  Open the Ollama app, or run `ollama serve`. Check with `ollama list`.
- **Pull the models once:** `ollama pull mistral` and
  `ollama pull nomic-embed-text`.
- **Embedding crashed mid-run?** `connection reset by peer` on the tokenize port
  usually means the embedder ran out of memory. Run `ollama stop mistral` to
  free ~4.4GB first.

## Never commit your API key

`.env` is gitignored. Check before every push. If a key does land in the repo
history, revoke it at https://aistudio.google.com/apikey immediately — deleting
the file is not enough, it stays in git history.
