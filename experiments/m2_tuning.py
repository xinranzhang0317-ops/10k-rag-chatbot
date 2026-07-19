"""
M2 - RAG Tuning Grid Search (Stage 2)  |  Owner: Member 2 (Angela)
Deliverable: results/rag_tuning.md by Jul 18 EOD (numbers handed to Member 1).

USAGE (from the project folder, with `conda activate chatbot` and Ollama running):

    python m2_tuning.py check      # verify PDFs, API key, Ollama - run this first
    python m2_tuning.py run        # Stage A: 9-config grid, saves answers to runs/
    python m2_tuning.py show Q7    # print every config's answer to one question
    python m2_tuning.py summary    # scoreboard (after filling m2_scores.py)
    python m2_tuning.py stageb     # Stage B: Gemini embeddings on the winning config
    python m2_tuning.py export     # write results/rag_tuning.md

Scoring workflow: after `run`, use `show Q1` ... `show Q10` to read answers,
type 0-3 scores into m2_scores.py (auto-created template), then `summary` / `export`.

Note: code reflects the FINAL run-L configuration (cleaning + tagging + fetch_k + pins + rules). 
Earlier runs A–J used progressively fewer of these features (see rag_tuning.md ladder);
re-running the Stage-A grid now would not reproduce the original A results.
"""

import os, sys, json, time, itertools
from pathlib import Path

import re
JUNK_PATTERNS = [
    re.compile(r"\d{4}/\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2}"),   # print timestamps: 2026/4/13 16:18
    re.compile(r"sec\.gov/Archives"),                        # browser URL lines
    re.compile(r"第\s*\d+\s*/\s*\d+\s*⻚"),                  # page-count artifacts
]
def clean_page_text(text):
    lines = text.split("\n")
    kept = [ln for ln in lines if not any(p.search(ln) for p in JUNK_PATTERNS)]
    return "\n".join(kept)

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR    = Path("data")
CACHE_DIR   = Path("faiss_cache")
RUNS_DIR    = Path("runs")
RESULTS_DIR = Path("results")

PDFS = [
    DATA_DIR / "Alphabet_10k_2025.pdf",
    DATA_DIR / "Amazon_10k_2025.pdf",
    DATA_DIR / "Microsoft_10K_2025.pdf",
]

CHUNK_SIZES  = [500, 1000, 1500]
K_VALUES     = [4, 8, 15]
FETCH_K_MULT = 3
LAMBDA_MULT  = 0.7

EMBEDDINGS_STAGE_A = "nomic-embed-text"
LLM_MODEL = "gemini-3.1-flash-lite"
LLM_TEMPERATURE    = 0.0

SECONDS_BETWEEN_LLM_CALLS = 7           
GEMINI_EMBED_BATCH = 90               
GEMINI_EMBED_PAUSE = 65

BEST_CS = 1500
BEST_K  = 15

QUESTIONS = {
  "Q1":  "Among AWS, Google Cloud, and Microsoft's Intelligent Cloud, which segment had the highest operating margin in its most recent fiscal year? Rank all three with percentages.",
  "Q2":  "Using the effective tax rate reconciliation tables in the latest 10-K filings, identify which of Amazon, Alphabet, and Microsoft had the largest difference between the U.S. statutory federal tax rate and its reported effective tax rate. Then identify the single disclosed factor that contributed most to that difference for each company.",
  "Q3":  "What was Amazon's cash, cash equivalents, and restricted cash at the beginning of fiscal 2024?",
  "Q4":  "Compare R&D expense as a percentage of total revenue for Microsoft and Amazon in the most recent fiscal year. Rank them and give each percentage.",
  "Q5":  "Using only the latest 10-K filings, calculate each company's 2025 cash-tax gap, defined as income taxes paid, net of refunds, minus provision for income taxes, for Alphabet, Amazon, and Microsoft. Report each result in USD billions, rank the three companies from highest to lowest, and identify the only company with a positive gap. Use each company's own fiscal year and do not substitute income taxes payable or the effective tax rate.",
  "Q6":  "Based on Amazon's profit growth in recent years, predict Amazon's profit in 2026.",
  "Q7":  "According to Microsoft's FY2025 10-K, what was its FY2024 Productivity and Business Processes segment revenue?",
  "Q8":  "Based only on the latest 10-K filings, identify the largest reportable business segment by revenue for Alphabet, Amazon, and Microsoft. For each company, calculate that segment's revenue as a percentage of the company's consolidated revenue, round the result to one decimal place, and rank the three companies from most to least dependent on their largest segment. Show the fiscal year and revenue figures used in your calculation. Use reportable segments rather than individual products or revenue categories.",
  "Q9":  "Out of Amazon, Microsoft, and Alphabet, which company had the highest profit and revenue for 2024 and 2025? Out of these companies, which company would be the best investment for both institutional and retail investors?",
  "Q10": "Using each company's most recent 10-K, sum the total capital expenditures reported as purchases/additions of property and equipment across Alphabet, Amazon, and Microsoft. State each figure with its correct units, compute capex as a percentage of each company's revenue, and identify which company is investing most aggressively in AI/cloud infrastructure on a relative basis.",
}

RETRIEVAL_QS = ["Q1","Q2","Q3","Q4","Q5","Q7","Q8","Q10"]   # primary metric, max 24
PROMPT_QS    = ["Q6","Q9"]                                   # prompt-behavior, tracked separately
BASE_PROMPT = """You are a careful financial analyst answering questions from SEC 10-K excerpts.
Question: {q}
Rules:
1. Use ONLY the provided context. Never use outside knowledge.
2. Use stated totals only. NEVER compute a total by summing table components, and NEVER derive a figure that is not printed in the context (not from growth rates, effective tax rates, or subtraction).
3. Every context block is tagged [Company p.X]. Before using any number, verify it came from the company you are discussing. Never attribute one company's figure to another company.
4. When identifying the "largest" factor: FIRST list every reconciliation line item with its magnitude. THEN compare absolute values. If the two largest absolute values are EQUAL (e.g. 2.5 and -2.5, or 1.5 and -1.5), you MUST state "this is a tie between X and Y" — choosing only one is an error.
5. Show inputs, formula, result, units, and fiscal year for every calculation.
6. If a required figure is absent from the context, say so for that item, but still fully answer every part that is supported. Cite specific figures and fiscal years. For trend or forecast questions, always include the relevant multi-year historical figures from the context before stating the limitation.
"""

# ── Lazy imports (so `check` can give friendly errors) ────────────────────────
def _imports():
    global PyPDFLoader, RecursiveCharacterTextSplitter, FAISS
    global OllamaEmbeddings, GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI, ResourceExhausted
    from dotenv import load_dotenv
    load_dotenv()
    from langchain_community.document_loaders import PyPDFLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import FAISS
    from langchain_ollama import OllamaEmbeddings
    from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
    from google.api_core.exceptions import ResourceExhausted

def check():
    _imports()
    ok = True
    for p in PDFS:
        if p.exists():
            print(f"  [ok] {p}")
        else:
            print(f"  [MISSING] {p}")
            ok = False
    if os.environ.get("GOOGLE_API_KEY"):
        print("  [ok] GOOGLE_API_KEY found (.env)")
    else:
        print("  [MISSING] GOOGLE_API_KEY - create a .env file with GOOGLE_API_KEY=...")
        ok = False
    try:
        OllamaEmbeddings(model=EMBEDDINGS_STAGE_A).embed_query("ping")
        print("  [ok] Ollama + nomic-embed-text responding")
    except Exception as e:
        print(f"  [FAIL] Ollama check: {e}\n         -> is Ollama running? did you `ollama pull nomic-embed-text`?")
        ok = False
    print("\nAll checks passed - run: python m2_tuning.py run" if ok
          else "\nFix the items above, then re-run: python m2_tuning.py check")

# ── Corpus / index ────────────────────────────────────────────────────────────
_RAW = None
def load_corpus():
    global _RAW
    if _RAW is None:
        STATEMENT_MARKERS = [
            "STATEMENTS OF CASH FLOWS", "STATEMENTS OF OPERATIONS",
            "STATEMENTS OF INCOME", "INCOME STATEMENTS",
            "REPORTABLE SEGMENTS", "SEGMENT RESULTS",
            "SEGMENT REVENUE, COST OF REVENUE",
            "INFORMATION ABOUT SEGMENTS",
            "SUPPLEMENTAL CASH FLOW", "CASH PAID FOR INCOME TAXES",
            "ADDITIONS TO PROPERTY AND EQUIPMENT",
            "EFFECTIVE TAX RATE", "STATUTORY RATE",
            "COMPONENTS OF THE PROVISION FOR INCOME TAXES",
        ]
        docs = []
        for pdf in PDFS:
            company = pdf.stem.split("_")[0]
            pages = PyPDFLoader(str(pdf)).load()
            for pg in pages:
                pg.page_content = clean_page_text(pg.page_content)
                pg.metadata["company"] = company
                if any(m in pg.page_content.upper() for m in STATEMENT_MARKERS):
                    pg.metadata["doc_type"] = "statement"
            docs.extend(pages)
            print(f"  loaded {company}: {len(pages)} pages")
        _RAW = docs
    return _RAW

def embedder_for(name):
    if name == "nomic-embed-text":
        return OllamaEmbeddings(model="nomic-embed-text")
    if name == "mxbai-embed-large":
        return OllamaEmbeddings(model="mxbai-embed-large")
    if name == "gemini":
        return GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    raise ValueError(name)

def build_or_load_index(chunk_size, embeddings_name):
    overlap = int(chunk_size * 0.10)
    tag = f"{embeddings_name}_cs{chunk_size}_ov{overlap}"
    cache = CACHE_DIR / tag
    emb = embedder_for(embeddings_name)
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    chunks = splitter.split_documents(load_corpus())

    if cache.exists():
        vs = FAISS.load_local(str(cache), emb, allow_dangerous_deserialization=True)
        print(f"  [cache hit] {tag} ({len(chunks)} chunks)")
        return vs, len(chunks), 0.0

    print(f"  building index {tag}: {len(chunks)} chunks...")
    t0 = time.time()
    if embeddings_name == "gemini":
        vs = None
        for i in range(0, len(chunks), GEMINI_EMBED_BATCH):
            batch = chunks[i:i + GEMINI_EMBED_BATCH]
            for attempt in range(6):
                try:
                    if vs is None:
                        vs = FAISS.from_documents(batch, emb)
                    else:
                        vs.add_documents(batch)
                    break
                except Exception as e:
                    if "429" not in str(e):
                        raise
                    print(f"    embed 429, attempt {attempt+1}/6, sleeping 75s")
                    time.sleep(75)
            else:
                raise RuntimeError("Embed quota exhausted after 6 retries - likely a DAILY cap. See notes.")
            done = min(i + GEMINI_EMBED_BATCH, len(chunks))
            print(f"    embedded {done}/{len(chunks)}")
            if done < len(chunks):
                time.sleep(GEMINI_EMBED_PAUSE)
    else:
        OLLAMA_BATCH = 100
        vs = None
        for i in range(0, len(chunks), OLLAMA_BATCH):
            batch = chunks[i:i + OLLAMA_BATCH]
            if vs is None:
                vs = FAISS.from_documents(batch, emb)
            else:
                vs.add_documents(batch)
            done = min(i + OLLAMA_BATCH, len(chunks))
            if done % 500 < OLLAMA_BATCH or done == len(chunks):
                print(f"    embedded {done}/{len(chunks)}")
    secs = time.time() - t0
    vs.save_local(str(cache))
    print(f"  [built] {tag} in {secs:.0f}s")
    return vs, len(chunks), secs

# ── Answer runner ─────────────────────────────────────────────────────────────
def answer_all(vector_store, k):
    llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": k * FETCH_K_MULT, "lambda_mult": LAMBDA_MULT},
    )
    QUERY_EXPANSION = (" segment information net sales revenue operating income"
                       " fiscal year segment results")
    out = {}
    for qid, qtext in QUESTIONS.items():
        expanded = qtext + QUERY_EXPANSION
        chunks = []
        for company in ["Alphabet", "Amazon", "Microsoft"]:
            chunks += vector_store.similarity_search(
                expanded, k=8, filter={"company": company}, fetch_k=2000)
        for company in ["Alphabet", "Amazon", "Microsoft"]:
            stmt = vector_store.similarity_search(
                expanded, k=10,
                filter={"company": company, "doc_type": "statement"}, fetch_k=2000)
            seen = {c.page_content[:100] for c in chunks}
            chunks += [c for c in stmt if c.page_content[:100] not in seen]
        PINNED_PAGES = {
            "Alphabet":  {49, 52, 86, 87},
            "Amazon":    {59, 60, 102, 103, 108},
            "Microsoft": {67, 86, 89, 90, 124, 125, 126, 142},
        }
        seen = {c.page_content[:100] for c in chunks}
        for doc in vector_store.docstore._dict.values():
            comp = doc.metadata.get("company")
            if comp in PINNED_PAGES and doc.metadata.get("page") in PINNED_PAGES[comp]:
                if doc.page_content[:100] not in seen:
                    chunks.append(doc)
                    seen.add(doc.page_content[:100])
        context = "\n\n---\n\n".join(
            f"[{c.metadata.get('company','?')} p.{c.metadata.get('page','?')}] {c.page_content}"
            for c in chunks
        )
        prompt = f"Context:\n{context}\n\n{BASE_PROMPT.format(q=qtext)}"
        resp = None
        for attempt in range(4):
            try:
                resp = llm.invoke(prompt)
                break
            except ResourceExhausted:
                wait = 20 * (attempt + 1)
                print(f"    429 on {qid}, sleeping {wait}s")
                time.sleep(wait)
        out[qid] = {
            "answer": resp.content if resp else "<LLM failed after retries>",
            "companies_retrieved": sorted({c.metadata.get("company","?") for c in chunks}),
            "pages": [c.metadata.get("page") for c in chunks],
        }
        print(f"    {qid} done (companies in context: {out[qid]['companies_retrieved']})")
        time.sleep(SECONDS_BETWEEN_LLM_CALLS)
    return out

def _save_run(run_id, meta, answers):
    (RUNS_DIR / f"{run_id}.json").write_text(json.dumps({"meta": meta, "answers": answers}, indent=2))

# ── Commands ──────────────────────────────────────────────────────────────────
def run_stage_a():
    _imports()
    for d in (CACHE_DIR, RUNS_DIR, RESULTS_DIR):
        d.mkdir(exist_ok=True)
    for cs, k in itertools.product(CHUNK_SIZES, K_VALUES):
        run_id = f"A_{EMBEDDINGS_STAGE_A}_cs{cs}_k{k}"
        if (RUNS_DIR / f"{run_id}.json").exists():
            print(f"[skip] {run_id} already on disk")
            continue
        print(f"\n=== {run_id} ===")
        vs, n_chunks, idx_secs = build_or_load_index(cs, EMBEDDINGS_STAGE_A)
        answers = answer_all(vs, k)
        _save_run(run_id, {"stage":"A","embeddings":EMBEDDINGS_STAGE_A,"chunk_size":cs,
                           "overlap":int(cs*0.10),"k":k,"n_chunks":n_chunks,
                           "indexing_seconds":round(idx_secs,1),"llm":LLM_MODEL}, answers)
    print("\nStage A complete. Next: python m2_tuning.py show Q1  (then fill m2_scores.py)")
    _ensure_scores_template()

def run_stage_b():
    _imports()
    for d in (CACHE_DIR, RUNS_DIR, RESULTS_DIR):
        d.mkdir(exist_ok=True)
    run_id = f"L_mxbai_stmts_cs{BEST_CS}_k8x3"
    run_file = RUNS_DIR / f"{run_id}.json"
    if run_file.exists():
        print(f"{run_id} already on disk")
        return
    print(f"=== {run_id} === (local embeddings - no quota, a few minutes to index)")
    vs, n_chunks, idx_secs = build_or_load_index(BEST_CS, "mxbai-embed-large")
    answers = answer_all(vs, BEST_K)
    _save_run(run_id, {"stage": "B", "embeddings": "mxbai-embed-large", "chunk_size": BEST_CS,
                       "overlap": int(BEST_CS*0.10), "k": BEST_K, "n_chunks": n_chunks,
                       "indexing_seconds": round(idx_secs, 1), "llm": LLM_MODEL},
              answers)
    print("Stage B saved - score it in m2_scores.py like the others.")
    
def show(qid):
    qid = qid.upper()
    if qid not in QUESTIONS:
        print(f"Unknown question id {qid}; use Q1..Q10"); return
    print("="*100); print(f"{qid}: {QUESTIONS[qid]}"); print("="*100)
    for f in sorted(RUNS_DIR.glob("*.json")):
        data = json.loads(f.read_text())
        a = data["answers"].get(qid, {})
        print(f"\n--- {f.stem}  (companies retrieved: {a.get('companies_retrieved')}) ---")
        print(a.get("answer", "<missing>")[:1500])

def _ensure_scores_template():
    p = Path("m2_tuning_scores.py")
    if p.exists():
        return
    runs = sorted(f.stem for f in RUNS_DIR.glob("*.json"))
    lines = ["# Fill 0-3 per question (Member 5's rubric in eval_questions.md).",
             "# Q4 note: 'not strictly comparable' WITH the limitation stated = 3, not 0.",
             "SCORES = {"]
    for r in runs:
        qs = ",".join(f'"{q}":0' for q in QUESTIONS)
        lines.append(f'    "{r}": {{{qs}}},')
    lines.append("}")
    p.write_text("\n".join(lines))
    print(f"Created {p} - type your scores there.")

def _summary_rows():
    _ensure_scores_template()
    from m2_tuning_scores import SCORES
    rows = []
    for run_id, qs in SCORES.items():
        f = RUNS_DIR / f"{run_id}.json"
        if not f.exists():
            continue
        meta = json.loads(f.read_text())["meta"]
        ret = sum(qs.get(q, 0) for q in RETRIEVAL_QS)
        prm = sum(qs.get(q, 0) for q in PROMPT_QS)
        rows.append({**meta, "run_id": run_id, "ret": ret, "prm": prm, "tot": ret + prm})
    rows.sort(key=lambda r: r["ret"], reverse=True)
    return rows

def summary():
    rows = _summary_rows()
    if not rows:
        print("No scores yet - run the grid, then fill m2_scores.py"); return
    for r in rows:
        print(f"{r['run_id']:38s} retrieval {r['ret']:>2}/24  prompt {r['prm']}/6  "
              f"chunks {r['n_chunks']:>5}  index {r['indexing_seconds']}s")

def export():
    rows = _summary_rows()
    RESULTS_DIR.mkdir(exist_ok=True)
    lines = [
        "# M2 RAG Tuning Results (Stage 2)", "",
        f"Corpus: Alphabet / Amazon / Microsoft FY2025 10-Ks. LLM frozen to {LLM_MODEL} "
        f"(temp {LLM_TEMPERATURE}). Overlap = 10% of chunk_size. Scores 0-3 per question vs "
        "Member 5's verified key (eval_questions.md). Primary metric = retrieval-sensitive score "
        "(Q1-Q5, Q7, Q8, Q10; max 24); Q6/Q9 tracked separately as prompt-behavior questions.", "",
        "| run | embeddings | chunk_size | overlap | k | chunks | index (s) | retrieval /24 | prompt /6 | total /30 |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r['run_id']} | {r['embeddings']} | {r['chunk_size']} | {r['overlap']} | {r['k']} "
                     f"| {r['n_chunks']} | {r['indexing_seconds']} | {r['ret']} | {r['prm']} | {r['tot']} |")
    if rows:
        b = rows[0]
        lines += ["", "## Recommendation to Member 1 (config.py values)", "",
                  f"- chunk_size = {b['chunk_size']}",
                  f"- chunk_overlap = {b['overlap']}",
                  f"- k = {b['k']} (global; if balanced per-company retrieval is live, "
                  f"use k_per_company = {max(1, round(b['k']/3))})",
                  f"- embeddings = {b['embeddings']}", "",
                  "## Notes / observed failure modes", "",
                  "- (fill in: which questions flipped between configs and why)"]
    out = RESULTS_DIR / "rag_tuning.md"
    out.write_text("\n".join(lines))
    print(f"Wrote {out}")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "check":      check()
    elif cmd == "run":      run_stage_a()
    elif cmd == "show":     show(sys.argv[2] if len(sys.argv) > 2 else "Q1")
    elif cmd == "summary":  summary()
    elif cmd == "stageb":   run_stage_b()
    elif cmd == "export":   export()
    else:                   print(__doc__)
