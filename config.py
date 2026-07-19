"""
Central configuration.

Members 2 and 3: this is the ONLY file you need me to change based on your
findings. Send me the numbers, I'll apply them here. Do not edit app.py.
"""

# ---------------------------------------------------------------------------
# Companies. The `key` is what gets stamped onto every chunk's metadata and is
# what balanced retrieval filters on. `file` is the PDF in data/.
# ---------------------------------------------------------------------------
COMPANIES = {
    "Alphabet": {"file": "Alphabet_10k_2025.pdf", "ticker": "GOOGL", "color": "#4285F4"},
    "Amazon":   {"file": "Amazon_10k_2025.pdf",   "ticker": "AMZN",  "color": "#FF9900"},
    "Microsoft": {"file": "Microsoft_10K_2025.pdf", "ticker": "MSFT", "color": "#00A4EF"},
    "Apple":    {"file": "Apple_10k_2025.pdf",    "ticker": "AAPL",  "color": "#B8B8BD"},
    "Tesla":    {"file": "Tesla_10k_2025.pdf",    "ticker": "TSLA",  "color": "#E82127"},
}

# ---------------------------------------------------------------------------
# RAG parameters  <-- MEMBER 2 OWNS THESE NUMBERS
# ---------------------------------------------------------------------------
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 150
K_PER_COMPANY = 8

# Chunks retrieved PER COMPANY (not globally). With 3 companies selected and
# K_PER_COMPANY=3, the LLM sees 9 chunks: 3 from each. This is what stops the
# model from answering a comparison question using only Amazon's filing.
# K_PER_COMPANY = 3

# ---------------------------------------------------------------------------
# Models  <-- MEMBER 3 OWNS THIS RECOMMENDATION
# ---------------------------------------------------------------------------

# Default: local embeddings (no API quota) + Gemini for generation (fast, good
# synthesis). Both switchable in the sidebar.
# DEFAULT_EMBEDDING = "Ollama (nomic-embed-text)"
DEFAULT_EMBEDDING = "Ollama (mxbai-embed-large)" # member 2's  recommendation
DEFAULT_LLM = "Gemini (gemini-flash-latest)"

EMBEDDING_OPTIONS = {
    "Ollama (nomic-embed-text)": {"provider": "ollama", "model": "nomic-embed-text"},
    "Gemini (gemini-embedding-001)": {"provider": "gemini", "model": "models/gemini-embedding-001"},
    "Ollama (mxbai-embed-large)": {"provider": "ollama", "model": "mxbai-embed-large"}
}

LLM_OPTIONS = {
    # Alias that always points at Google's current flash model. Pinned names
    # (gemini-2.0-flash, gemini-2.5-flash) kept getting retired mid-project,
    # so the alias is the safe default.
    "Gemini (gemini-flash-latest)": {"provider": "gemini", "model": "gemini-flash-latest"},
    "Gemini (gemini-3-flash)": {"provider": "gemini", "model": "gemini-3-flash"},
    "Gemini (gemini-2.5-flash-lite)": {"provider": "gemini", "model": "gemini-2.5-flash-lite"},
    "Ollama (mistral)": {"provider": "ollama", "model": "mistral"},
    "Ollama (llama3.1)": {"provider": "ollama", "model": "llama3.1"},
    "Ollama (deepseek-r1:14b)": {"provider": "ollama", "model": "deepseek-r1:14b"},
}

# Lower = less creative = fewer invented numbers. Relevant for a finance bot.
TEMPERATURE = 0.1

# Where the built FAISS index gets cached so we don't re-embed on every restart.
INDEX_DIR = "faiss_index"
