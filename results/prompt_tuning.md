# Prompt Engineering A/B Test

## Experimental Controls

- Embedding model: Ollama (nomic-embed-text)
- Language model: Gemini (gemini-flash-latest)
- Chunk size: 2000
- Chunk overlap: 200
- Chunks per company: 3
- Selected companies: Alphabet, Amazon, Microsoft
- Test questions: Q1–Q10 from `eval_questions.md`
- Variable changed: System prompt only

## Scoring Rubric

- 3: Fully correct
- 2: Mostly correct
- 1: Partially correct
- 0: Incorrect or unsupported

Also record citation accuracy, hallucination, and failure type.

---

# Prompt Versions

## Baseline Prompt

```python
PERSONA = """You are a financial analyst assistant that answers questions about \
SEC 10-K annual reports for Alphabet (Google), Amazon, and Microsoft.

Rules you must follow:
1. Answer ONLY from the provided context. The context is excerpts from the \
companies' 10-K filings.
2. Every fact you state must name its source company, e.g. "Amazon reported...".
3. If the context does not contain the answer, say exactly: "I don't have enough \
information in the filings to answer that." Do not guess. Do not use outside \
knowledge about these companies.
4. For comparison questions, address every company the user asked about. If the \
context is missing one of them, say which one is missing rather than comparing \
only the ones you have.
5. Quote exact figures as they appear in the filing, including the units and the \
fiscal year. Never round or estimate a number that isn't in the context.
6. Be concise. Lead with the direct answer, then the supporting detail.
"""

ANSWER_TEMPLATE = """{persona}

Context from the 10-K filings:
---------------------
{context}
---------------------

Question: {question}

Answer:"""
```

## Improved Prompt

```python
PERSONA = """You are a careful financial analyst assistant answering questions \
about SEC 10-K annual reports.

Use only the provided filing context. Do not use outside knowledge or invent \
missing facts.

Rules:
1. Examine all retrieved excerpts before deciding that information is missing.
2. Do not refuse the entire question when part of it can be answered. Provide \
all supported results first, then clearly identify any missing company, figure, \
or disclosure.
3. For cross-company questions, analyze each requested company separately and \
then provide the comparison or ranking.
4. When calculations are requested, show the reported inputs, formula, result, \
units, and fiscal year. Convert millions and billions accurately.
5. Distinguish directly disclosed metrics from proxies or broader categories. \
If two figures are not directly comparable, explain why instead of forcing a \
ranking.
6. Identify ties, ambiguity, and disclosure limitations rather than selecting \
an arbitrary answer.
7. For forecasting or investment questions, first provide any supported \
historical facts. Then explain that a forecast or investment recommendation \
cannot be determined objectively from historical 10-K data alone. Do not simply \
refuse without addressing the factual portion.
8. If the context truly lacks all evidence needed for the question, say: \
"The retrieved filing context does not provide enough information to answer \
this reliably."
9. Every factual statement must identify the source company. Include the fiscal \
year and exact units for financial figures.
10. Be concise but complete. Lead with the direct conclusion, followed by \
evidence, calculations, and limitations.
"""

ANSWER_TEMPLATE = """{persona}

Context from the 10-K filings:
---------------------
{context}
---------------------

Question: {question}

Respond using this structure when applicable:

Direct answer:
[Conclusion or partial conclusion]

Evidence and calculations:
[Company-by-company figures, formulas, and results]

Limitations:
[Missing disclosures, non-comparability, ambiguity, forecasting assumptions, \
or investment-recommendation limitations]

Answer:"""
```

---

# Baseline Prompt Results

## Q1

**Chatbot answer:**

I don't have enough information in the filings to answer that.

**Score:** 0

**Citation/source correct:** No

**Hallucination:** No

**Failure type:** Retrieval

**Notes:** The answer exists in the filings, but the chatbot refused to answer. The retrieved context likely did not include the required segment revenue and operating income figures for all three companies.

---

## Q2

**Chatbot answer:**

I don't have enough information in the filings to answer that. The provided context is missing the full effective tax rate reconciliation table and the explicit U.S. statutory federal tax rate for Microsoft.

However, the details for the other two companies are as follows:

Alphabet reported a "US federal statutory rate" of "21.0 %" and a "Total" effective tax rate of "16.8 %" for the fiscal year "2025" (a difference of 4.2%). The single factor contributing most to this difference was the "Foreign-derived intangible income deduction" at "(2.5) %".

Amazon reported "Income taxes computed at the federal statutory rate" of "21.0 %" and a "Total" effective tax rate of "19.6 %" for the fiscal year "2025" (a difference of 1.4%). The factors contributing most to this difference were "Research and development tax credits" at "(2.5) %" and "State and local income taxes, net of federal effect" at "2.5 %".

**Score:** 1

**Citation/source correct:** No

**Hallucination:** No

**Failure type:** Retrieval

**Notes:** Correctly retrieved Alphabet and Amazon figures and recognized Amazon's tie, but failed to retrieve Microsoft and therefore did not fully answer the three-company comparison or explicitly conclude that Alphabet had the largest gap.

---

## Q3

**Chatbot answer:**

Amazon reported $73,890 million in cash, cash equivalents, and restricted cash at the beginning of fiscal 2024.

This is listed under the "CASH, CASH EQUIV ALENTS, AND RESTRICTED CASH, BEGINNING OF PERIOD" line item for the year ended December 31, 2024, in Amazon's Consolidated Statements of Cash Flows.

**Score:** 3

**Citation/source correct:** Yes

**Hallucination:** No

**Failure type:** None

**Notes:** Correct value, company, fiscal period, and units. Minor formatting issue: "EQUIVALENTS" was split as "EQUIV ALENTS."

---

## Q4

**Chatbot answer:**

I don't have enough information in the filings to answer that.

The provided context is missing research and development (R&D) expense details for Amazon. For Microsoft, the filings report that research and development expenses were 12% of revenue in fiscal year 2025.

**Score:** 2

**Citation/source correct:** No

**Hallucination:** No

**Failure type:** Interpretation / Retrieval

**Notes:** Correctly recognized that Amazon does not provide a directly comparable standalone R&D figure. Microsoft’s result is approximately correct, but the answer should report 11.53%, explicitly explain the non-comparability, and state that a strict ranking cannot be made.

---

## Q5

**Chatbot answer:**

I don't have enough information in the filings to answer that.

The provided context is missing the cash paid for income taxes, net of refunds, for Microsoft's fiscal year 2025, which prevents calculating its cash-tax gap, ranking all three companies, and identifying the only company with a positive gap.

The available data and calculations for the other two companies are:

Alphabet (for the fiscal year ended December 31, 2025):

- Cash paid for income taxes, net of refunds: $21,526 million (or $21.526 billion)
- Provision for income taxes: $26,656 million (or $26.656 billion)
- Cash-tax gap calculation: $21.526 billion − $26.656 billion = −$5.130 billion

Amazon (for the fiscal year ended December 31, 2025):

- Cash paid for income taxes, net of refunds: $8.3 billion
- Provision for income taxes: $19.1 billion
- Cash-tax gap calculation: $8.3 billion − $19.1 billion = −$10.8 billion

**Score:** 1

**Citation/source correct:** No

**Hallucination:** No

**Failure type:** Retrieval

**Notes:** Correctly calculated the Alphabet and Amazon cash-tax gaps, but the retrieved context omitted Microsoft’s cash taxes paid. Therefore, the chatbot could not complete the three-company ranking or identify Microsoft as the only company with a positive gap. The original chatbot output also contained broken mathematical formatting when copied from Streamlit.

---

## Q6

**Chatbot answer:**

I don't have enough information in the filings to answer that.

**Score:** 2

**Citation/source correct:** No

**Hallucination:** No

**Failure type:** Forecasting / Unsupported inference

**Notes:** Correctly refused to invent a 2026 profit figure, but did not explain that the 10-K contains historical results only and that any forecast would require assumptions or a forecasting method.

---

## Q7

**Chatbot answer:**

Microsoft reported that its Productivity and Business Processes segment revenue for fiscal year 2024 was $106,820 million.

**Score:** 3

**Citation/source correct:** Yes

**Hallucination:** No

**Failure type:** None

**Notes:** Correct company, fiscal year, segment, and revenue figure.

---

## Q8

**Chatbot answer:**

I don't have enough information in the filings to answer that. The provided context is missing the reportable segment revenue figures for Microsoft.

For the other companies:

Alphabet reported Google Services as its largest reportable segment for the fiscal year ended December 31, 2025. Its revenue was $342,721 million out of $402,836 million in total revenues, which is 85.1% of consolidated revenue.

Amazon reported North America as its largest reportable segment for the fiscal year ended December 31, 2025. Its net sales were $426,305 million out of $716,924 million in consolidated net sales, which is 59.5% of consolidated revenue.

**Score:** 1

**Citation/source correct:** No

**Hallucination:** No

**Failure type:** Retrieval

**Notes:** Correctly identified and calculated Alphabet and Amazon, but failed to retrieve Microsoft’s segment figures, so it could not complete the three-company ranking. The missing Microsoft answer should have been Productivity and Business Processes at 42.9% of consolidated revenue.

---

## Q9

**Chatbot answer:**

I don't have enough information in the filings to answer that.

**Score:** 0

**Citation/source correct:** No

**Hallucination:** No

**Failure type:** Retrieval

**Notes:** The chatbot appropriately avoided making an unsupported investment recommendation, but it also failed to retrieve the available historical figures. It should have identified Amazon as the revenue leader and Alphabet as the net-income leader in both 2024 and 2025, then explained that there is no single objectively best investment based only on the 10-K filings.

---

## Q10

**Chatbot answer:**

I don't have enough information in the filings to answer that.

**Score:** 0

**Citation/source correct:** No

**Hallucination:** No

**Failure type:** Retrieval

**Notes:** The required capex and revenue figures are available in the filings, but the chatbot failed to retrieve them. It should have calculated Microsoft at 22.9%, Alphabet at 22.7%, and Amazon at 18.4%, while clarifying that these are company-wide capex ratios rather than precise AI/cloud-only spending measures.

---

# Improved Prompt Results

## Q1

**Chatbot answer:**

Direct answer: The retrieved filing context does not provide enough information to answer this reliably. Key financial figures required to calculate the operating margins for AWS, Google Cloud, and Microsoft's Intelligent Cloud in their most recent fiscal years are missing from the provided text. Consequently, a ranking of the three segments cannot be determined.

Evidence and calculations:

Amazon (AWS Segment, FY2025 ended December 31, 2025):
- Reported Net Sales: $128,725 million.
- Reported Operating Income: Not disclosed in the provided context.
- Operating Margin cannot be calculated.

Alphabet (Google Cloud Segment, FY2025 ended December 31, 2025):
- Reported Operating Income: $13,910 million.
- Total revenue was not retrieved.
- Operating Margin cannot be calculated.

Microsoft (Intelligent Cloud Segment, FY2025 ended June 30, 2025):
- Segment revenue and operating income were not retrieved.
- Operating Margin cannot be calculated.

Limitations: The ranking cannot be performed because the required figures were not all present in the retrieved excerpts.

**Score:** 1

**Citation/source correct:** Yes

**Hallucination:** No

**Failure type:** Retrieval

**Notes:** The improved prompt produced a clearer company-by-company partial answer and explicitly identified the missing inputs. However, it still could not calculate or rank the three operating margins because the required chunks were not retrieved. This shows that prompt engineering improved response behavior but could not overcome retrieval limitations.

---

## Q2

**Chatbot answer:**

Direct answer:

Alphabet had the largest difference between the U.S. statutory federal tax rate and its reported effective tax rate in FY2025, with a difference of 4.2 percentage points.

The largest disclosed factors were:

- Alphabet: Foreign-derived intangible income deduction, −2.5 percentage points.
- Amazon: A tie between state and local income taxes, net of federal effect, +2.5 percentage points, and research and development tax credits, −2.5 percentage points.
- Microsoft: Earnings taxed at lower rates in foreign jurisdictions.

Evidence and calculations:

- Alphabet: 21.0% − 16.8% = 4.2 percentage points.
- Amazon: 21.0% − 19.6% = 1.4 percentage points.
- Microsoft: The answer identified possible effective rates of 17.6% or 19.0% because it considered the retrieved table headers ambiguous.

Limitations:

The answer stated that the Microsoft table columns were not clearly labeled in the retrieved excerpt. It also noted the tie between Amazon’s two largest reconciliation factors.

**Score:** 2

**Citation/source correct:** No

**Hallucination:** No

**Failure type:** Interpretation

**Notes:** Correctly identified Alphabet as having the largest gap and correctly recognized Amazon’s tie. However, it incorrectly treated Microsoft’s FY2025 effective rate as ambiguous and failed to identify Microsoft’s tie between foreign earnings taxed at lower rates (−1.5 percentage points) and state income taxes (+1.5 percentage points).

---

## Q3

**Chatbot answer:**

Direct answer: Amazon's cash, cash equivalents, and restricted cash at the beginning of fiscal 2024 was $73,890 million (or approximately $73.89 billion).

Evidence and calculations: According to Amazon’s Consolidated Statements of Cash Flows (page 59 of the Amazon 10-K), the cash, cash equivalents, and restricted cash at the beginning of the period for the fiscal year ended December 31, 2024, is reported as:

- Company: Amazon.com, Inc.
- Fiscal Year: 2024
- Line Item: Cash, cash equivalents, and restricted cash, beginning of period
- Value: $73,890 million

Limitations: There are no significant limitations, ambiguities, or missing disclosures. The figure is directly disclosed in the Consolidated Statements of Cash Flows.

**Score:** 3

**Citation/source correct:** Yes

**Hallucination:** No

**Failure type:** None

**Notes:** Fully correct value, company, fiscal year, units, and source.

---

## Q4

**Chatbot answer:**

Direct answer: Using Amazon's "Technology and infrastructure" expense as a proxy for R&D, Amazon ranks higher than Microsoft for FY2025:

- Amazon proxy: 15.14% of total net sales
- Microsoft: 12% of total revenue

However, Amazon does not report a distinct R&D expense line, so the figures are not directly comparable.

Evidence and calculations:

- Microsoft R&D expense: $32,488 million; reported as approximately 12% of revenue.
- Amazon Technology and Infrastructure expense: $108,521 million.
- Amazon total net sales: $716,924 million.
- Proxy calculation: $108,521 million ÷ $716,924 million × 100 = 15.14%.

Limitations: Amazon’s Technology and Infrastructure expense is broader than Microsoft’s R&D expense, so a strict apples-to-apples ranking cannot be made.

**Score:** 2

**Citation/source correct:** Yes

**Hallucination:** No

**Failure type:** Interpretation / Rounding

**Notes:** Correctly identified the disclosure limitation and clearly labeled Amazon’s figure as a proxy. However, Microsoft’s exact calculated percentage is 11.53%, not simply 12%, and the proxy ranking should not be treated as a strict comparison.

---

## Q5

**Chatbot answer:**

Direct answer:

- Alphabet (FY2025): −$5.130 billion
- Amazon (FY2025): −$10.8 billion
- Microsoft (FY2025): Could not be calculated from the retrieved context

Because Microsoft’s figures were not retrieved, the answer could not provide the complete ranking or identify the only company with a positive gap.

Evidence and calculations:

- Alphabet: $21.526 billion cash taxes paid − $26.656 billion tax provision = −$5.130 billion.
- Amazon: $8.3 billion cash taxes paid − $19.1 billion tax provision = −$10.8 billion.
- Microsoft: Required cash-tax figures were missing from the retrieved excerpts.

**Score:** 1

**Citation/source correct:** No

**Hallucination:** No

**Failure type:** Retrieval / Unsupported inference

**Notes:** Alphabet and Amazon were calculated correctly, but Microsoft was missing. The correct Microsoft result is +$6.905 billion, making the complete ranking Microsoft, Alphabet, then Amazon, and Microsoft the only company with a positive gap. The answer also unnecessarily estimated Microsoft’s tax provision using a rounded effective tax rate, even though the question specifically required the reported provision.

---

## Q6

**Chatbot answer:**

Direct answer: An objective forecast of Amazon's FY2026 net income cannot be determined from historical 10-K data alone. Amazon reported net income of:

- FY2023: $30.425 billion
- FY2024: $59.248 billion
- FY2025: $77.670 billion

Amazon provided Q1 2026 operating-income guidance, but it did not provide a full-year FY2026 net-income forecast.

Evidence and calculations:

- FY2023 to FY2024 net-income growth: 94.73%
- FY2024 to FY2025 net-income growth: 31.10%

The sharply different historical growth rates do not establish a reliable growth assumption for FY2026.

Limitations:

A full-year net-income forecast would require additional assumptions about operating margins, non-operating income, taxes, economic conditions, investment spending, and other unpredictable factors. Therefore, the historical filings do not support a uniquely correct FY2026 profit figure.

**Score:** 3

**Citation/source correct:** Yes

**Hallucination:** No

**Failure type:** None — forecasting boundary handled correctly

**Notes:** Correctly explained that no objectively verifiable FY2026 forecast exists, provided accurate historical context, and avoided presenting an unsupported estimate as fact.

---

## Q7

**Chatbot answer:**

Direct answer: Microsoft’s Productivity and Business Processes segment revenue in fiscal year 2024 was $106,820 million, or approximately $106.82 billion.

Evidence and calculations:

According to Microsoft’s Segment Results of Operations table:

- FY2024 revenue: $106,820 million
- FY2025 revenue: $120,810 million
- Reported increase: 13%

Limitations:

Microsoft revised the presentation of prior-year segment figures to reflect changes in segment composition, so the FY2024 amount is presented on the revised comparable basis.

**Score:** 3

**Citation/source correct:** Yes

**Hallucination:** No

**Failure type:** None

**Notes:** Fully correct company, segment, fiscal year, value, and units. The additional segment-reclassification caveat is accurate and relevant.

---

## Q8

**Chatbot answer:**

Direct answer:

- Alphabet: Google Services — 85.08% of total revenue
- Amazon: North America — 59.46% of total revenue
- Microsoft: Productivity and Business Processes — 42.88% of total revenue

Ranking: Alphabet > Amazon > Microsoft.

Evidence and calculations:

- Alphabet: $342,721 million ÷ $402,836 million × 100 = 85.08%.
- Amazon: $426,305 million ÷ $716,924 million × 100 = 59.46%.
- Microsoft: $120,810 million ÷ $281,724 million × 100 = 42.88%.

Limitations:

Microsoft’s fiscal year ended June 30, whereas Alphabet’s and Amazon’s ended December 31. The companies also define their reportable segments differently.

**Score:** 3

**Citation/source correct:** Yes

**Hallucination:** No

**Failure type:** None

**Notes:** Fully correct segment identification, reported figures, percentage calculations, and ranking. The additional fiscal-year and segment-comparability caveats are relevant.

---

## Q9

**Chatbot answer:**

Direct answer:

- Highest total revenue: Amazon in both FY2024 and FY2025.
- Highest net income: Alphabet in both FY2024 and FY2025.
- Best investment: Cannot be determined objectively from these historical results alone.

Evidence and calculations:

FY2024 total revenue:

- Amazon: $637.959 billion
- Alphabet: $350.018 billion
- Microsoft: $245.122 billion

FY2025 total revenue:

- Amazon: $716.924 billion
- Alphabet: $402.836 billion
- Microsoft: $281.724 billion

FY2024 net income:

- Alphabet: $100.118 billion
- Microsoft: $88.136 billion
- Amazon: $59.248 billion

FY2025 net income:

- Alphabet: $132.170 billion
- Microsoft: $101.832 billion
- Amazon: $77.670 billion

Limitations:

Microsoft’s fiscal year ends June 30, while Alphabet’s and Amazon’s end December 31. Revenue and net income alone are also insufficient for an investment recommendation because valuation, cash flow, risk, growth expectations, and other factors must be considered.

**Score:** 3

**Citation/source correct:** Yes

**Hallucination:** No

**Failure type:** None

**Notes:** Correctly identified Amazon as the revenue leader and Alphabet as the net-income leader in both years. It also appropriately explained why these results alone cannot determine the best investment.

---

## Q10

**Chatbot answer:**

Direct answer:

The retrieved filing context did not provide enough quantitative information to calculate the requested results.

Evidence and calculations:

- Alphabet: Exact capital expenditures and total revenue were not retrieved.
- Amazon: Total revenue of $716,924 million was retrieved, but capital expenditures were missing.
- Microsoft: Exact capital expenditures and total revenue were not retrieved.

Limitations:

The answer could not calculate the combined capital expenditures, capex-to-revenue ratios, or relative ranking because the required cash-flow statement figures were absent from the retrieved excerpts.

**Score:** 0

**Citation/source correct:** No

**Hallucination:** No

**Failure type:** Retrieval

**Notes:** The response appropriately avoided fabrication and explained the missing evidence, but it did not answer any required quantitative part. The verified results are Microsoft $64.551B / $281.724B = 22.9%, Alphabet $91.447B / $402.836B = 22.7%, and Amazon $131.819B / $716.924B = 18.4%. Total capex is $287.817B. Microsoft ranks highest by company-wide capex intensity, although this is not an AI/cloud-only measure.

---

# A/B Test Summary

| Metric | Baseline Prompt | Improved Prompt |
|---|---:|---:|
| Total score | 13/30 | 21/30 |
| Average score | 1.3/3 | 2.1/3 |
| Correct citation/source | 2/10 | 7/10 |
| Hallucinations | 0 | 0 |

## Main Findings

The improved prompt increased the total evaluation score from 13/30 to 21/30, an improvement of 8 points. The average score increased from 1.3 to 2.1 out of 3.

The main improvement was response behavior. The baseline prompt frequently refused an entire question when one company or figure was missing. The improved prompt instead:

- answered all supported portions of the question;
- analyzed companies separately;
- showed formulas, inputs, units, and fiscal years;
- distinguished direct disclosures from broader proxies;
- identified ties and comparability limitations;
- handled forecasting and investment questions without making unsupported claims.

The largest improvements occurred on questions involving partial evidence, calculations, comparisons, forecasting, and subjective investment conclusions. For example, the improved prompt produced complete answers for the segment-revenue comparison and the historical revenue/net-income comparison, while the baseline prompt either omitted Microsoft or refused the question.

However, prompt engineering could not fully resolve retrieval failures. Questions 1, 5, and 10 still lacked necessary excerpts from one or more filings, even though the correct information existed in the original PDFs. This demonstrates that the prompt can improve how the model uses retrieved context, but it cannot recover financial figures that were not included in that context.

Overall, the improved prompt should be used in the final application. Its strongest benefits are reduced blanket refusals, clearer calculations, better handling of partial evidence, and more transparent limitations. Final performance may improve further when it is combined with Member 2’s optimized retrieval settings and Member 3’s recommended language model.