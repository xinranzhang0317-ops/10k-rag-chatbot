# Final Chatbot Evaluation Scores

## Test Information

- **Chatbot version:** `app.py` (post-merge — page cleaning, statement-slot search, pinned pages)
- **Test date:** July 20, 2026
- **Evaluation set:** 10 official questions
- **Scoring scale:** 0–3 points per question
- **Maximum score:** 30 points

## Score Table

| Question | Score | Citation Correct? | Hallucination? | Failure Type | Notes |
|---|---:|---|---|---|---|
| Q1 | 3/3 | Yes | No | None | Correct ranking, operating-margin calculations, percentages, and fiscal-year figures for all three segments. |
| Q2 | 3/3 | Yes | No | None | Now correctly reports Microsoft's effective tax rate as 17.6% (3.4pp gap), fixed from the earlier 19.0% error. Correctly disclosed genuine ties in Microsoft's and Amazon's largest reconciling factors rather than forcing a single answer. |
| Q3 | 3/3 | Yes | No | None | Correctly reported Amazon's beginning-of-FY2024 cash, cash equivalents, and restricted cash as $73.890B. |
| Q4 | 3/3 | Yes | No | None | Fixed from the earlier false refusal. Now calculates both Microsoft's R&D (11.53%) and Amazon's Technology & Infrastructure proxy (15.14%), with a clear limitation noting Amazon doesn't disclose standalone R&D. |
| Q5 | 3/3 | Yes | No | None | Correct cash-tax gap calculations, signs, ranking, and identification of Microsoft as the only company with a positive gap. |
| Q6 | 3/3 | Yes | No | None | Fixed from the earlier incomplete refusal. Now correctly declines a definitive forecast, explains why, and provides two clearly-labeled hypothetical growth scenarios plus real Q1 2026 guidance instead of stopping short. |
| Q7 | 3/3 | Yes | No | None | Correctly reported FY2024 Productivity and Business Processes revenue as $106.820B, with the segment-recast limitation noted. |
| Q8 | 3/3 | Yes | No | None | Correct reportable segments, revenue figures, percentages, and ranking. |
| Q9 | 3/3 | Yes | No | None | Correctly identified Amazon as revenue leader and Alphabet as profit leader for both years, and appropriately declined to make a definitive investment recommendation. |
| Q10 | 3/3 | Yes | No | None (previously: unsupported inference) | Fixed. The chatbot now explicitly states that no company discloses AI/cloud-specific capex and presents total capex as a proxy rather than treating the ranking as a directly disclosed fact. |

## Final Result

- **Total score: 30/30**
- **Overall score: 100%**
- **Fully correct questions:** all 10
- **Main issues:** none remaining — all four issues found in the prior evaluation pass (Q2's tax-rate figure, Q4's false refusal, Q6's incomplete boundary explanation, Q10's unsupported inference) were resolved by merging Member 2's retrieval fixes (PDF page cleaning, statement-slot search, pinned pages) into `app.py`.

## Overall Assessment

The chatbot performs well across numerical retrieval, multi-step calculations, and multi-company ranking, and now consistently distinguishes directly disclosed figures from calculated proxies and inferred conclusions, adding explicit caveats where the filings don't support a stronger claim. The earlier evaluation pass (24/30) on this same integrated app surfaced exactly the retrieval gaps that Member 2's tuning experiments had already identified but which hadn't yet been merged; closing that gap accounts for the full improvement.
