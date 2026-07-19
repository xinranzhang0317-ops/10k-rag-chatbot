# RAG Chatbot Evaluation Questions and Verified Answer Key

**Project:** AI Essentials for Business Final RAG Chatbot  
**Prepared for:** Model evaluation, RAG tuning, prompt testing, and boundary analysis  
**Source documents:** Alphabet, Amazon, and Microsoft FY2025 Form 10-K filings  
**Important:** All dollar figures are in **USD billions** unless otherwise stated.

---

## Scoring Rubric

Use the same rubric for every model/configuration:

- **3points for Fully correct:** Correct conclusion, figures, fiscal years, units, calculations, and source interpretation.
- **2points for Mostly correct:** Correct main conclusion, but one minor omission or rounding/citation issue.
- **1points for Partially correct:** Retrieves relevant information but makes a material calculation, interpretation, or ranking error.
- **0points for Incorrect / unsupported:** Wrong answer, irrelevant answer, refusal despite available evidence, or fabricated information.

Also record:

- **Citation/source correct?** Yes / No
- **Correct company and fiscal year?** Yes / No
- **Hallucination?** Yes / No
- **Failure type:** Retrieval / Calculation / Interpretation / Unsupported inference / Forecasting


## Recommended Results-Logging Template

Use this table when testing each model or RAG configuration:

| Question | Model / Configuration | Chatbot Answer | Score (0–3) | Citation Correct? | Hallucination? | Failure Type | Notes |
|---|---|---|---:|---|---|---|---|
| Q1 |  |  |  |  |  |  |  |
| Q2 |  |  |  |  |  |  |  |
| Q3 |  |  |  |  |  |  |  |
| Q4 |  |  |  |  |  |  |  |
| Q5 |  |  |  |  |  |  |  |
| Q6 |  |  |  |  |  |  |  |
| Q7 |  |  |  |  |  |  |  |
| Q8 |  |  |  |  |  |  |  |
| Q9 |  |  |  |  |  |  |  |
| Q10 |  |  |  |  |  |  |  |

---

# Questions Only

## Q1.Among AWS, Google Cloud, and Microsoft's Intelligent Cloud, which segment had the highest operating margin in its most recent fiscal year? Rank all three with percentages.

## Q2. Using the effective tax rate reconciliation tables in the latest 10-K filings, identify which of Amazon, Alphabet, and Microsoft had the largest difference between the U.S. statutory federal tax rate and its reported effective tax rate. Then identify the single disclosed factor that contributed most to that difference for each company.

## Q3. What was Amazon's cash, cash equivalents, and restricted cash at the beginning of fiscal 2024?

## Q4. Compare R&D expense as a percentage of total revenue for Microsoft and Amazon in the most recent fiscal year. Rank them and give each percentage.

## Q5. Using only the latest 10-K filings, calculate each company’s 2025 “cash-tax gap,” defined as income taxes paid, net of refunds, minus provision for income taxes, for Alphabet, Amazon, and Microsoft. Report each result in USD billions, rank the three companies from highest to lowest, and identify the only company with a positive gap. Use each company’s own fiscal year and do not substitute income taxes payable or the effective tax rate.

## Q6. Based on Amazon's profit growth in recent years, predict Amazon's profit in 2026.

## Q7. According to Microsoft’s FY2025 10-K, what was its FY2024 Productivity and Business Processes segment revenue?

## Q8. Based only on the latest 10-K filings, identify the largest reportable business segment by revenue for Alphabet, Amazon, and Microsoft. For each company, calculate that segment’s revenue as a percentage of the company’s consolidated revenue, round the result to one decimal place, and rank the three companies from most to least dependent on their largest segment. Show the fiscal year and revenue figures used in your calculation. Use reportable segments rather than individual products or revenue categories.

## Q9. Out of Amazon, Microsoft, and Alphabet, which company had the highest profit and revenue for 2024 and 2025? Out of these companies, which company would be the best investment for both institutional and retail investors?

## Q10. Using each company's most recent 10-K, sum the total capital expenditures reported as purchases/additions of property and equipment across Alphabet, Amazon, and Microsoft. State each figure with its correct units, compute capex as a percentage of each company's revenue, and identify which company is investing most aggressively in AI/cloud infrastructure on a relative basis.

---

# Verified Ground-Truth Answer Key

## Q1. Among AWS, Google Cloud, and Microsoft's Intelligent Cloud, which segment had the highest operating margin in its most recent fiscal year? Rank all three with percentages.

### Answer

1. Microsoft Intelligent Cloud: **41.96%**
2. AWS: **35.43%**
3. Google Cloud: **23.69%**

### Calculations

- Operating income/revenue
- Microsoft Intelligent Cloud: $44.589B / $106.265B = **41.96%**  

- AWS: $45.606B / $128.725B = **35.43%** 

- Google Cloud: $13.910B / $58.705B = **23.69%**

### Sources

- Alphabet FY2025 Form 10-K: Google Cloud revenue table and segment profitability table, MD&A.
- Amazon FY2025 Form 10-K: Note 10, Segment Information.
- Microsoft FY2025 Form 10-K: Segment Results of Operations / Note 18.

### Common Failure Modes

- Using company-wide operating margin instead of segment operating margin.
- Confusing **Microsoft Cloud gross margin (69%)** with **Intelligent Cloud operating margin**.
- Using Azure alone even though Azure revenue is not separately disclosed.
- Mixing 2024 and 2025 figures.

---

## Q2. Using the effective tax rate reconciliation tables in the latest 10-K filings, identify which of Amazon, Alphabet, and Microsoft had the largest difference between the U.S. statutory federal tax rate and its reported effective tax rate. Then identify the single disclosed factor that contributed most to that difference for each company.

### Answer

**Alphabet had the largest statutory-to-effective tax-rate difference.**

| Company | U.S. statutory rate | Effective rate | Absolute difference |
| Alphabet | 21.0% | 16.8% | **4.2 percentage points** |
| Microsoft | 21.0% | 17.6% | **3.4 percentage points** |
| Amazon | 21.0% | 19.6% | **1.4 percentage points** |

### Largest Disclosed Reconciliation Factor

- **Alphabet:** Foreign-derived intangible income deduction, **−2.5 percentage points**.
- **Amazon:** There is a **tie** in absolute size:
  - Research and development tax credits, **−2.5 percentage points**
  - State and local income taxes, net of federal effect, **+2.5 percentage points**
- **Microsoft:** There is also a **tie** in absolute size:
  - Foreign earnings taxed at lower rates, **−1.5 percentage points**
  - State income taxes, net of federal benefit, **+1.5 percentage points**

### Evaluation Note

The question asks for a **single** largest factor for each company, but Amazon and Microsoft each disclose a tie. A reliable chatbot should identify this ambiguity instead of arbitrarily selecting one factor.

### Sources

- Alphabet FY2025 Form 10-K: Note 14, Income Taxes, effective-rate reconciliation.
- Amazon FY2025 Form 10-K: Note 9, Income Taxes, effective-rate reconciliation.
- Microsoft FY2025 Form 10-K: Note 11, Income Taxes, effective-rate reconciliation.

### Common Failure Modes

- Subtracting in the wrong direction.
- Treating the largest negative item as automatically the largest absolute item.
- Ignoring the ties for Amazon and Microsoft.
- Reporting dollar amounts instead of percentage-point effects.

---

## Q3. What was Amazon's cash, cash equivalents, and restricted cash at the beginning of fiscal 2024?

### Answer

Amazon’s cash, cash equivalents, and restricted cash at the beginning of fiscal 2024 was: **$73.890 billion**

### Source

Amazon FY2025 Form 10-K, Consolidated Statements of Cash Flows:

- Beginning of period:
  - FY2023: $54.253B
  - **FY2024: $73.890B**
  - FY2025: $82.312B

### Common Failure Modes

- Returning the end-of-2024 figure of $82.312B.
- Returning only “cash and cash equivalents” from the balance sheet.
- Using the beginning-of-2025 figure.

---

## Q4. Compare R&D expense as % of total revenue for Microsoft, and Amazon (most recent FY). Rank + give each %.

### Strict Answer

- **Microsoft:**  
   $32.488B / $281.724B = **11.53%** (R&D expense/revenue)

- **Amazon:**  
  Amazon does **not separately disclose a pure “research and development” expense line**. It reports **Technology and Infrastructure**, which includes R&D-related payroll and expenses but also infrastructure, depreciation, AWS operations, and other technology costs.

Therefore, a strict apples-to-apples R&D comparison **cannot be made from the 10-K disclosures alone**.

### Possible Proxy, If Explicitly Allowed

Using Amazon’s Technology and Infrastructure expense as a proxy:

(R&D expense/revenue)
- Microsoft
  $32.488B / $281.724B = **11.53%**
- Amazon Technology and Infrastructure:  
  $108.521B / $716.924B = **15.14%**

Proxy ranking:
1. Amazon Technology and Infrastructure proxy: **15.14%**
2. Microsoft R&D: **11.53%**

### Evaluation Note

A strong chatbot should disclose that Amazon’s figure is **not directly comparable** to Microsoft’s R&D expense. Award full credit only if it states this limitation.

### Sources

- Microsoft FY2025 Form 10-K: Operating Expenses — Research and Development.
- Amazon FY2025 Form 10-K: Operating Expenses — Technology and Infrastructure.

### Common Failure Modes

- Calling Amazon’s Technology and Infrastructure line “R&D” without qualification.
- Comparing different years.
- Using total operating expenses instead of the relevant expense line.

---

## Q5 Using only the latest 10-K filings, calculate each company’s 2025 “cash-tax gap,” defined as income taxes paid, net of refunds, minus provision for income taxes, for Alphabet, Amazon, and Microsoft. Report each result in USD billions, rank the three companies from highest to lowest, and identify the only company with a positive gap. Use each company’s own fiscal year and do not substitute income taxes payable or the effective tax rate.



### Answer and Ranking

Cash-tax gap = income taxes paid, net of refunds − provision for income taxes

| Rank | Company | Cash taxes paid | Tax provision | Cash-tax gap |
| 1 | Microsoft | $28.700B | $21.795B | **+$6.905B** |
| 2 | Alphabet | $21.526B | $26.656B | **−$5.130B** |
| 3 | Amazon | $8.295B | $19.087B | **−$10.792B** |

- Microsoft is the only company with a positive cash-tax gap.

### Calculations

- Microsoft: $28.700B − $21.795B = **+$6.905B**
- Alphabet: $21.526B − $26.656B = **−$5.130B**
- Amazon: $8.295B − $19.087B = **−$10.792B**

### Sources

- Alphabet FY2025 Form 10-K: Note 14, Income Taxes.
- Amazon FY2025 Form 10-K: Note 9, Income Taxes.
- Microsoft FY2025 Form 10-K: Note 11, Income Taxes.

### Common Failure Modes

- Reversing the subtraction.
- Using income taxes payable rather than cash taxes paid.
- Using the effective tax rate.
- Dropping the negative signs.
- Mixing millions and billions.

---

## Q6. Based on Amazon's profit growth in recent years, please predict Amazon's profit in 2026.	

### Ground-Truth Evaluation

There is **no objectively verifiable answer in the 10-K**. Amazon’s FY2025 10-K contains historical financial results and forward-looking risk disclosures, but it does not provide a definitive FY2026 net-income forecast.

A reliable RAG chatbot should say that:

1. The filing does not provide enough information for a factual 2026 profit figure.
2. Any prediction would require external assumptions or a forecasting model.
3. If it chooses to estimate, it must clearly label the result as an estimate and state its method and assumptions.

### Historical Context

Amazon net income:

- 2023: $30.425B
- 2024: $59.248B
- 2025: $77.670B

These figures do not establish a uniquely correct 2026 forecast.

### Scoring Guidance

- **3 points:** Explicitly says no verified answer exists and explains why.
- **2 points:** Provides a clearly labeled estimate with transparent assumptions and a strong disclaimer.
- **0–1 points:** Presents a fabricated or overly confident “correct” 2026 profit figure.

### Failure Type

**Boundary / forecasting / unsupported inference**

---

## Q7. According to Microsoft’s FY2025 10-K, what was its FY2024 Productivity and Business Processes segment revenue?


### Answer

Microsoft FY2024 Productivity and Business Processes segment revenue was:

**$106.820 billion**

### Source

Microsoft FY2025 Form 10-K, Segment Results of Operations / Note 18:

- FY2025: $120.810B
- **FY2024: $106.820B**
- FY2023: $94.151B

### Common Failure Modes

- Returning FY2025 revenue.
- Returning operating income instead of revenue.
- Using Microsoft’s total company revenue.

---

## Q8. Based only on the latest 10-K filings, identify the largest reportable business segment by revenue for Alphabet, Amazon, and Microsoft. For each company, calculate that segment’s revenue as a percentage of the company’s consolidated revenue, round the result to one decimal place, and rank the three companies from most to least dependent on their largest segment. Show the fiscal year and revenue figures used in your calculation. Use reportable segments rather than individual products or revenue categories.


### Answer

| Rank | Company | Fiscal year | Largest reportable segment | Segment revenue | Consolidated revenue | Share |
| 1 | Alphabet | FY2025 | Google Services | $342.721B | $402.836B | **85.08%** |
| 2 | Amazon | FY2025 | North America | $426.305B | $716.924B | **59.46%** |
| 3 | Microsoft | FY2025 | Productivity and Business Processes | $120.810B | $281.724B | **42.88%** |

### Calculations

- Alphabet: $342.721B / $402.836B = **85.08%**
- Amazon: $426.305B / $716.924B = **59.46%**
- Microsoft: $120.810B / $281.724B = **42.88%**

### Ranking

**Alphabet → Amazon → Microsoft**

Alphabet is the most dependent on its largest reportable segment.

### Sources

- Alphabet FY2025 Form 10-K: Google Services, Google Cloud, Other Bets revenue table.
- Amazon FY2025 Form 10-K: Note 10, Segment Information.
- Microsoft FY2025 Form 10-K: Note 18, Segment Information.

### Common Failure Modes

- Using an individual product category such as Google Search or AWS instead of the largest reportable segment.
- Treating Azure as a reportable segment.
- Using operating income instead of revenue.
- Forgetting to round to one decimal place.

---

## Q9. Out of Amazon, Microsoft, Alphabet, which company had the highest profit and revenue for 2024 and 2025. Out of these companies, which companies would be the best investment for both institutional and retail investor?


### Historical Revenue and Net Income

| Company | 2024 revenue | 2025 revenue | 2024 net income | 2025 net income |
| Amazon | **$637.959B** | **$716.924B** | $59.248B | $77.670B |
| Alphabet | $350.018B | $402.836B | **$100.118B** | **$132.170B** |
| Microsoft | $245.122B | $281.724B | $88.136B | $101.832B |

### Answer

- Highest revenue in both 2024 and 2025: Amazon
- Highest net income (“profit”) in both 2024 and 2025: Alphabet

### Investment Recommendation Limitation

The question’s “best investment” portion has **no single objective ground-truth answer** based only on the 10-Ks. A responsible answer should explain that an investment recommendation also requires:

- Current valuation and stock price
- Expected future growth
- Risk tolerance
- Investment horizon
- Portfolio diversification
- Cash-flow needs
- Institutional mandates versus retail-investor circumstances

A chatbot may discuss trade-offs, but it should not state that one company is definitively best for both institutional and retail investors without assumptions.

### Scoring Guidance

Full credit requires:

1. Correct revenue and net-income leaders.
2. Clear recognition that “best investment” is subjective and cannot be determined solely from historical 10-K figures.
3. No personalized financial recommendation presented as certainty.

Possible Failure Type: Mixed factual retrieval + unsupported financial recommendation

---

## Q10. Using each company's most recent 10-K, sum the total capital expenditures (reported as 'purchases of property and equipment') across Alphabet, Amazon, and Microsoft. State each figure with its correct units, compute capex as a percentage of each company's revenue, and identify which company is investing most aggressively in AI/cloud infrastructure on a relative basis.

### Answer

| Company | FY2025 purchases/additions of property and equipment | FY2025 revenue | Capex / revenue |
| Microsoft | $64.551B | $281.724B | **22.9%** |
| Alphabet | $91.447B | $402.836B | **22.7%** |
| Amazon | $131.819B | $716.924B | **18.4%** |

### Total

$64.551B + $91.447B + $131.819B = **$287.817 billion**

### Relative Ranking

1. **Microsoft: 22.9%**
2. **Alphabet: 22.7%**
3. **Amazon: 18.4%**

Microsoft has the highest property-and-equipment spending relative to revenue, narrowly ahead of Alphabet.

### Important Interpretation Caveat

The cash-flow statement figures include property and equipment used for purposes beyond AI/cloud infrastructure. The filings discuss substantial AI/cloud and datacenter investment, but the ratios should be described as **company-wide capex intensity**, not a precise measure of AI/cloud-only spending.

### Sources

- Alphabet FY2025 Form 10-K, Consolidated Statements of Cash Flows: purchases of property and equipment, $91.447B.
- Amazon FY2025 Form 10-K, Consolidated Statements of Cash Flows: purchases of property and equipment, $131.819B.
- Microsoft FY2025 Form 10-K, Consolidated Statements of Cash Flows: additions to property and equipment, $64.551B.

### Common Failure Modes

- Using Amazon’s non-cash “total net additions” instead of cash purchases of property and equipment.
- Using Microsoft’s accounts-payable commitments rather than additions to property and equipment.
- Adding figures expressed in different units.
- Claiming that all capex was spent exclusively on AI/cloud.
- Ranking by absolute dollars rather than capex as a percentage of revenue.

---
