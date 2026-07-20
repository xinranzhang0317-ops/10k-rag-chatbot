# LLM comparison — Member 3

Run the professor's question list across each model. Do not edit app.py.

**Note on model naming:** the task list originally called for `gemini-2.5-flash`.
During testing, `gemini-2.5-flash` and `gemini-2.5-flash-lite` began returning
404s ("no longer available to new users") on fresh API keys — see
`results/challenges.md`. The team standardized on the `gemini-flash-latest`
alias for this reason, which is also what `config.py` actually ships as
`DEFAULT_LLM`. The comparison below uses that model, labeled "Gemini Flash"
rather than "Gemini 2.5 Flash," so it reflects the model the app actually runs.

| Model | Accuracy (score/30) | Correct | Partial | Hallucination | Failure |
|---|---|---|---|---|---|
| Gemini Flash (gemini-flash-latest) | 21/30 (70%) | 4/10 | 4/10 | 1/10 | 1/10 |
| Llama 3.1 | 20/30 (66.7%) | 5/10 | 2/10 | 3/10 | 0/10 |
| DeepSeek-R1 | 18/30 (60%) | 1/10 | 6/10 | 2/10 | 1/10 |
| Mistral | 15/30 (50%) | 0/10 | 5/10 | 5/10 | 0/10 |

*Latency was not captured in this pass — flagging as a known gap rather than
guessing at numbers.*

**Recommended model:** Gemini Flash (gemini-flash-latest). Highest accuracy
and the lowest hallucination rate of the four, and it's already the app's
default in `config.py`.

## Why they differ

The clearest split isn't accuracy, it's **what a model does when the evidence
is incomplete.** Gemini Flash and DeepSeek-R1 were the two models most likely
to say "the retrieved evidence doesn't fully support this" instead of
guessing — DeepSeek in particular scored heavily in the "partial/retrieval
limitation" band (6/10) rather than inventing numbers. Mistral did the
opposite: it hallucinated on half the question set (5/10), frequently
mixing fiscal years or fabricating reconciling tax factors that weren't in
the retrieved chunks at all.

Llama 3.1 sits in between but skews toward overconfidence rather than
caution — it produced the highest hallucination count of the non-Mistral
models (3/10), including one case where it applied company-wide financial
figures to a segment-level calculation instead of flagging that segment data
was missing.

The practical takeaway for a finance-facing chatbot: **accuracy alone
understates the risk difference between these models.** Mistral's raw
accuracy (50%) undersells how often it's confidently wrong versus admitting
uncertainty. A model that says "I don't have enough evidence" and stops is
safer in this domain than one that fills the gap with a plausible-sounding
number, even if their overall scores look similar.

## Cross-reference

Member 2's RAG tuning experiments (`results/rag_tuning.md`) independently
confirm the retrieval quality itself, separate from which LLM is doing the
generation — several of the hallucinations logged here trace back to
incomplete context reaching the model in the first place (see the `fetch_k`
bug in `results/challenges.md`), not the model inventing things from nothing.
