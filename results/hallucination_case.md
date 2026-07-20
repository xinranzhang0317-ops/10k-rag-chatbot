# Hallucination Case Study

## Case Overview

**Question:**  
Using each company’s most recent 10-K, sum capital expenditures across Alphabet, Amazon, and Microsoft, compute capital expenditures as a percentage of revenue, and identify which company is investing most aggressively in AI and cloud infrastructure.

## Earlier-Run Response

In an earlier evaluation run, the chatbot correctly calculated the company-wide capital-expenditure ratios:

- Microsoft: approximately **22.9%**
- Alphabet: approximately **22.7%**
- Amazon: approximately **18.4%**

It then concluded that Microsoft was investing most aggressively in AI and cloud infrastructure.

## Why This Was a Hallucination

The calculations were correct, but the conclusion was not directly supported by the filings.

The 10-K filings disclose total company-wide capital expenditures. They do not separately disclose how much of those expenditures was specifically allocated to AI or cloud infrastructure.

Therefore, the chatbot treated a broad company-wide metric as if it were a direct measure of AI- and cloud-specific investment.

- **Failure type:** Unsupported inference
- **Hallucination:** Yes
- **Earlier-run score for Q10:** 2/3

## What the Chatbot Should Have Said

A better answer would be:

> Microsoft had the highest company-wide capital expenditures as a percentage of revenue among the three companies. However, the filings do not separately disclose AI- or cloud-specific capital expenditures, so the available evidence is not sufficient to determine which company invested most aggressively specifically in AI and cloud infrastructure.

## Why This Case Matters

This case shows that correct retrieval and correct arithmetic do not automatically guarantee a reliable conclusion.

A RAG chatbot can retrieve the right numbers, calculate them correctly, and still overreach when interpreting what those numbers prove.

## Resolution

To reduce this type of failure, the prompt was revised to require the chatbot to:

1. Distinguish directly reported facts from calculated values and inferred conclusions.
2. Add a caveat when the requested metric is not separately disclosed.
3. State whether a conclusion is directly supported by the filing.
4. Avoid treating a broad company-wide metric as a precise proxy without qualification.

After these changes, the final tuned configuration handled the boundary correctly and received full credit on the final evaluation.

## Screenshot

![Q10 hallucination case](img/q10_hallucination.png)
