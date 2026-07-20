# Final Chatbot Evaluation Scores

## Test Information

- **Chatbot version:** `app2.py`
- **Test date:** July 19, 2026
- **Evaluation set:** 10 official questions
- **Scoring scale:** 0–3 points per question
- **Maximum score:** 30 points

## Score Table

| Question | Score | Citation Correct? | Hallucination? | Failure Type | Notes |
|---|---:|---|---|---|---|
| Q1 | 3/3 | Yes | No | None | Correct ranking, operating-margin calculations, percentages, and fiscal-year figures. |
| Q2 | 2/3 | Partially | Yes | Factual / interpretation error | Correctly identified Alphabet as having the largest difference, but Microsoft’s effective tax rate was incorrectly reported as 19.0% instead of 17.6%. |
| Q3 | 3/3 | Yes | No | None | Correctly reported Amazon’s beginning-of-FY2024 cash, cash equivalents, and restricted cash as $73.890B. |
| Q4 | 0/3 | No | No | Retrieval failure / false refusal | The chatbot said there was insufficient information, although Microsoft’s ratio could be calculated and Amazon’s Technology and Infrastructure expense could be used only as a clearly labeled proxy. |
| Q5 | 3/3 | Yes | No | None | Correct cash-tax gap calculations, signs, ranking, and identification of Microsoft as the only company with a positive gap. |
| Q6 | 2/3 | Yes | No | Incomplete boundary explanation | Correctly refused to provide a verified 2026 profit forecast, but did not explain that any estimate would require assumptions or a forecasting method. |
| Q7 | 3/3 | Yes | No | None | Correctly reported FY2024 Productivity and Business Processes revenue as $106.820B. |
| Q8 | 3/3 | Yes | No | None | Correct reportable segments, revenue figures, percentages, and ranking. |
| Q9 | 3/3 | Yes | No | Boundary handling | Correctly identified Amazon as the revenue leader and Alphabet as the profit leader, and appropriately declined to make a definitive investment recommendation. |
| Q10 | 2/3 | Partially | Yes | Unsupported inference | The calculations were correct, but the chatbot treated company-wide capex intensity as a direct measure of AI/cloud infrastructure investment without a caveat. |

## Final Result

- **Total score: 24/30**
- **Overall score: 80.0%**
- **Fully correct questions:** Q1, Q3, Q5, Q7, Q8, and Q9
- **Main issues:** one factual error, one false refusal, one incomplete boundary explanation, and one unsupported inference

## Overall Assessment

The chatbot performed well on numerical retrieval, calculations, and multi-company ranking. Its main weakness was distinguishing between directly disclosed metrics and conclusions that require assumptions or caveats.
