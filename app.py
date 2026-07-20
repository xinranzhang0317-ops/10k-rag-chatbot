"""
10-K Terminal — RAG chatbot comparing SEC 10-K filings.
JHU-CDHAI Chatbot-AIEB final project.
Run:  streamlit run app.py
Architecture: every chunk is tagged with its source company, and retrieval runs
once PER COMPANY instead of once globally (see balanced_retrieval).

M2 additions (Angela) — every change is marked with an "# M2:" comment:
  1. clean_page_text: strips browser print headers from every PDF page
  2. STATEMENT_MARKERS tagging: labels financial-statement chunks
  3. Statement slots + PINNED_PAGES in the chat handler: guarantees the core
     financial tables reach the LLM
Tested locally with config values CHUNK_SIZE=1500 / CHUNK_OVERLAP=150 /
K_PER_COMPANY=8 / mxbai-embed-large. NOTE: after merging, delete any existing
faiss_index* cache folders once — cleaning and tagging bake in at index build.
"""
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
import config
import prompts
import re  # M2: needed for page cleaning

# M2: block 1 — page-header cleaning. The source PDFs carry browser print
# headers (timestamps, sec.gov URLs, page counters) on every page. Identical
# boilerplate on every page drags all chunk embeddings toward each other and
# buries the financial tables in retrieval.
JUNK_PATTERNS = [
    re.compile(r"\d{4}/\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2}"),
    re.compile(r"sec\.gov/Archives"),
    re.compile(r"第\s*\d+\s*/\s*\d+\s*⻚"),
]
def clean_page_text(text):
    lines = text.split("\n")
    return "\n".join(ln for ln in lines if not any(p.search(ln) for p in JUNK_PATTERNS))

# M2: block 2 — pages containing these headings hold the core financial
# tables; chunks from them get doc_type="statement" so retrieval can reserve
# slots for them (number-heavy tables rarely resemble question wording, so
# they lose plain similarity search to prose).
STATEMENT_MARKERS = [
    "STATEMENTS OF CASH FLOWS", "STATEMENTS OF OPERATIONS",
    "STATEMENTS OF INCOME", "INCOME STATEMENTS",
    "REPORTABLE SEGMENTS", "SEGMENT RESULTS",
    "SEGMENT REVENUE, COST OF REVENUE", "INFORMATION ABOUT SEGMENTS",
    "SUPPLEMENTAL CASH FLOW", "CASH PAID FOR INCOME TAXES",
    "ADDITIONS TO PROPERTY AND EQUIPMENT",
    "EFFECTIVE TAX RATE", "STATUTORY RATE",
    "COMPONENTS OF THE PROVISION FOR INCOME TAXES",
]

# M2: block 3 (data) — core statement pages per eval company, ALWAYS included
# in context (no search). Fix for two Microsoft table pages that lost every
# similarity contest. Companies not listed (Apple, Tesla) are unaffected.
PINNED_PAGES = {
    "Alphabet":  {49, 52, 86, 87},
    "Amazon":    {59, 60, 102, 103, 108},
    "Microsoft": {67, 86, 89, 90, 124, 125, 126, 142},
}

load_dotenv()
st.set_page_config(page_title="10-K Terminal", page_icon="📊", layout="wide")
# ---------------------------------------------------------------------------
# Model builders
# ---------------------------------------------------------------------------
def build_embeddings(choice: str):
    spec = config.EMBEDDING_OPTIONS[choice]
    if spec["provider"] == "ollama":
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(model=spec["model"])
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        st.error("GOOGLE_API_KEY not found. Add it to your .env file.")
        st.stop()
    return GoogleGenerativeAIEmbeddings(model=spec["model"], google_api_key=key)
def build_llm(choice: str):
    spec = config.LLM_OPTIONS[choice]
    if spec["provider"] == "ollama":
        from langchain_ollama import OllamaLLM
        return OllamaLLM(model=spec["model"], temperature=config.TEMPERATURE)
    from langchain_google_genai import ChatGoogleGenerativeAI
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        st.error("GOOGLE_API_KEY not found. Add it to your .env file.")
        st.stop()
    return ChatGoogleGenerativeAI(
        model=spec["model"], google_api_key=key, temperature=config.TEMPERATURE
    )
# ---------------------------------------------------------------------------
# Index building
# ---------------------------------------------------------------------------
def load_and_tag(company: str, path: str):
    """Load one company's 10-K and stamp every chunk with its company name."""
    loader = PyPDFLoader(path)
    pages = loader.load()
    for pg in pages:  # M2: clean every page BEFORE splitting/embedding
        pg.page_content = clean_page_text(pg.page_content)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(pages)
    for c in chunks:
        c.metadata["company"] = company
        c.metadata["source_file"] = os.path.basename(path)
        # M2: tag chunks containing core financial-statement content
        if any(m in c.page_content.upper() for m in STATEMENT_MARKERS):
            c.metadata["doc_type"] = "statement"
    return chunks
@st.cache_resource(show_spinner=False)
def build_index(embedding_choice: str, chunk_size: int, chunk_overlap: int):
    """Build (or load) the FAISS index over all available 10-Ks.
    Cached on the settings that affect it, so flipping the LLM in the sidebar
    does NOT trigger a re-embed. Changing embeddings or chunking does.
    """
    embeddings = build_embeddings(embedding_choice)
    cache_dir = f"{config.INDEX_DIR}_{embedding_choice.split()[0]}_{chunk_size}_{chunk_overlap}"
    if os.path.isdir(cache_dir):
        return FAISS.load_local(cache_dir, embeddings, allow_dangerous_deserialization=True)
    all_chunks = []
    missing = []
    for company, meta in config.COMPANIES.items():
        path = os.path.join("data", meta["file"])
        if not os.path.exists(path):
            missing.append(f"{company} → data/{meta['file']}")
            continue
        all_chunks.extend(load_and_tag(company, path))
    if missing:
        st.error("Missing PDFs:\n\n" + "\n".join(f"- {m}" for m in missing))
        st.stop()
    # Embed in small batches rather than one giant call. A full 10-K produces
    # thousands of chunks; sending them all at once makes the Ollama embedder
    # drop the connection (EOF / connection reset on the tokenize port).
    BATCH = 64
    progress = st.progress(0.0, text="Embedding filings…")
    store = None
    for start in range(0, len(all_chunks), BATCH):
        batch = all_chunks[start:start + BATCH]
        if store is None:
            store = FAISS.from_documents(batch, embeddings)
        else:
            store.add_documents(batch)
        progress.progress(
            min((start + BATCH) / len(all_chunks), 1.0),
            text=f"Embedding filings… {min(start + BATCH, len(all_chunks))}/{len(all_chunks)} chunks",
        )
    progress.empty()
    store.save_local(cache_dir)
    return store
# ---------------------------------------------------------------------------
# THE IMPORTANT BIT
# ---------------------------------------------------------------------------
def balanced_retrieval(store, query: str, companies: list, k_each: int):
    """Retrieve k chunks from EACH company, instead of the global top-k.
    Plain top-k ranks every chunk from every filing together. On comparison
    questions that starves whichever company's wording sits farther from the
    query in vector space — the LLM never sees its numbers, so it refuses or
    invents them. Per-company filtering guarantees representation.
    """
    docs = []
    for company in companies:
        hits = store.similarity_search(query, k=k_each, filter={"company": company}, fetch_k=2000)
        docs.extend(hits)
    return docs
def company_badge(company: str) -> str:
    """Small colored badge using the company's brand color."""
    color = config.COMPANIES.get(company, {}).get("color", "#888888")
    return (
        f'<span style="background:{color}22;border:1px solid {color};'
        f'color:{color};padding:1px 8px;border-radius:10px;'
        f'font-size:0.75rem;font-weight:700">{company}</span>'
    )
def format_context(docs) -> str:
    """Group retrieved chunks by company so the LLM sees clean boundaries."""
    by_company = {}
    for d in docs:
        by_company.setdefault(d.metadata.get("company", "Unknown"), []).append(d)
    blocks = []
    for company, items in by_company.items():
        body = "\n\n".join(
            f"[page {d.metadata.get('page', '?')}] {d.page_content}" for d in items
        )
        blocks.append(f"### {company} 10-K\n{body}")
    return "\n\n".join(blocks)
def render_sources(sources):
    with st.expander(f"Sources ({len(sources)} chunks)"):
        for s in sources:
            st.markdown(
                f"{company_badge(s['company'])} &nbsp;"
                f"<span style='opacity:0.7;font-size:0.8rem'>page {s['page']}</span>",
                unsafe_allow_html=True,
            )
            st.caption(s["preview"])
# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Settings")
    embedding_choice = st.selectbox(
        "Embedding model",
        list(config.EMBEDDING_OPTIONS.keys()),
        index=list(config.EMBEDDING_OPTIONS).index(config.DEFAULT_EMBEDDING),
        help="Ollama runs locally with no rate limit. Gemini is faster but the "
             "free tier caps embedding at 100 requests/minute.",
    )
    llm_choice = st.selectbox(
        "Language model",
        list(config.LLM_OPTIONS.keys()),
        index=list(config.LLM_OPTIONS).index(config.DEFAULT_LLM),
        help="Switch to an Ollama model if Gemini returns a quota error.",
    )
    st.divider()
    st.subheader("Companies")
    selected = []
    for c, meta in config.COMPANIES.items():
        col_dot, col_box = st.columns([1, 9])
        with col_dot:
            st.markdown(
                f"<div style='margin-top:0.45rem;width:10px;height:10px;"
                f"border-radius:50%;background:{meta['color']}'></div>",
                unsafe_allow_html=True,
            )
        with col_box:
            if st.checkbox(f"{c}  ·  {meta['ticker']}", value=True, key=f"chk_{c}"):
                selected.append(c)
    st.divider()
    k_each = st.slider(
        "Chunks retrieved per company",
        min_value=1, max_value=12, value=config.K_PER_COMPANY,  # M2: max raised 8 -> 12
        help="Retrieval is balanced: this many chunks come from EACH selected "
             "company, so comparison questions always see every company.",
    )
    st.caption(
        f"Context size: {k_each} × {len(selected)} = **{k_each * len(selected)} chunks**"
        if selected else "Select at least one company."
    )
    st.divider()
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()
# ---------------------------------------------------------------------------
# Header + tabs
# ---------------------------------------------------------------------------
_ticker_html = " &nbsp;·&nbsp; ".join(
    f'<span style="color:{m["color"]};font-weight:700">{m["ticker"]}</span>'
    for m in config.COMPANIES.values()
)
st.markdown(
    f"""
    <div style="padding:0.2rem 0 0.6rem 0">
      <span style="font-size:2rem;font-weight:800;letter-spacing:1px">10-K TERMINAL</span>
      <span style="color:#FFB000;font-size:2rem;font-weight:800"> ▮</span><br>
      <span style="font-size:0.85rem;opacity:0.9">{_ticker_html}</span>
      <span style="font-size:0.8rem;opacity:0.6"> — grounded in the latest 10-K filings</span>
    </div>
    """,
    unsafe_allow_html=True,
)
tab_chat, tab_about = st.tabs(["💬 Chat", "🔍 How it works"])
with tab_about:
    st.markdown(
        """
### Balanced retrieval, not global top-k
Most RAG bots run **one** similarity search across all documents and take the
top-k chunks overall. On multi-company questions that starves whichever
company's wording sits farther from the query in vector space — the model never
sees its numbers, so it either refuses or invents them.
This app tags every chunk with its source company and searches **each company
separately**, guaranteeing every selected filing is represented in the context:
```
question ──► search Alphabet chunks  ──┐
        ───► search Amazon chunks    ──┼──► grouped context ──► LLM ──► cited answer
        ───► search Microsoft chunks ──┘        (k per company)
```
**Stack** · Streamlit · LangChain · FAISS · Ollama embeddings · Gemini / local
Ollama LLMs (switchable) · anti-hallucination system prompt (refuses rather
than guesses, cites company + page).
        """
    )
with tab_chat:
    if not selected:
        st.warning("Select at least one company in the sidebar.")
        st.stop()
    with st.spinner("Building index (first run embeds the filings — this takes a few minutes)…"):
        store = build_index(embedding_choice, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                render_sources(msg["sources"])
    if question := st.chat_input("e.g. Which company earns the most from cloud services?"):
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            # Narrated thinking panel: shows the balanced retrieval live,
            # then stays as a collapsible audit trail on the answer.
            with st.status("Analyzing filings…", expanded=True) as status:
                docs = []
                for company in selected:
                    st.write(f"⌕ Searching {company} 10-K…")
                    hits = store.similarity_search(question, k=k_each, filter={"company": company}, fetch_k=2000)
                    st.write(f"→ {len(hits)} relevant sections")
                    docs.extend(hits)
                # M2: block 3 (retrieval add-ons)
                # (a) statement slots — second search per company restricted to
                #     statement-tagged chunks, so core tables always compete.
                seen = {d.page_content[:100] for d in docs}
                for company in selected:
                    stmt = store.similarity_search(
                        question, k=10,
                        filter={"company": company, "doc_type": "statement"}, fetch_k=2000)
                    for d in stmt:
                        if d.page_content[:100] not in seen:
                            docs.append(d); seen.add(d.page_content[:100])
                # (b) pinned pages — always in context, no search involved.
                for doc in store.docstore._dict.values():
                    comp = doc.metadata.get("company")
                    if comp in selected and comp in PINNED_PAGES and doc.metadata.get("page") in PINNED_PAGES[comp]:
                        if doc.page_content[:100] not in seen:
                            docs.append(doc); seen.add(doc.page_content[:100])
                context = format_context(docs)
                status.update(
                    label=f"Retrieved {len(docs)} sections — generating answer…",
                    state="running",
                )
                llm = build_llm(llm_choice)
                prompt = prompts.ANSWER_TEMPLATE.format(
                    persona=prompts.PERSONA,
                    context=context,
                    question=question,
                )
                try:
                    response = llm.invoke(prompt)
                    answer = response.content if hasattr(response, "content") else str(response)
                    status.update(
                        label="✓ Answer grounded in the retrieved filings",
                        state="complete",
                        expanded=False,
                    )
                except Exception as e:
                    answer = (
                        f"**Model error.** {type(e).__name__}\n\n"
                        f"```\n{e}\n```\n\n"
                        "If this is a Gemini quota or model error, switch the "
                        "language model to an Ollama option in the sidebar."
                    )
                    status.update(label="✗ Model error", state="error", expanded=False)
            st.markdown(answer)
            sources = [
                {
                    "company": d.metadata.get("company", "?"),
                    "page": d.metadata.get("page", "?"),
                    "preview": d.page_content[:200].replace("\n", " ") + "…",
                }
                for d in docs
            ]
            render_sources(sources)
        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "sources": sources}
        )
