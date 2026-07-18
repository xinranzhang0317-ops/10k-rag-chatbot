"""Verify balanced retrieval actually isolates companies via metadata filter."""
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import FakeEmbeddings

# Deliberately lopsided: Amazon has lots of cloud-revenue text, Alphabet barely
# any. Under plain top-k this is exactly the case that starves Alphabet.
docs = []
for i in range(10):
    docs.append(Document(page_content=f"Amazon AWS cloud revenue segment {i}",
                         metadata={"company": "Amazon", "page": i}))
for i in range(2):
    docs.append(Document(page_content=f"Alphabet Google Cloud revenue {i}",
                         metadata={"company": "Alphabet", "page": i}))
for i in range(3):
    docs.append(Document(page_content=f"Microsoft Azure intelligent cloud {i}",
                         metadata={"company": "Microsoft", "page": i}))

store = FAISS.from_documents(docs, FakeEmbeddings(size=64))

query = "cloud revenue"
companies = ["Alphabet", "Amazon", "Microsoft"]
K = 3

# --- plain top-k (the starter-code behaviour) ---
plain = store.similarity_search(query, k=K * len(companies))
from collections import Counter
plain_dist = Counter(d.metadata["company"] for d in plain)

# --- balanced retrieval (ours) ---
balanced = []
for c in companies:
    balanced.extend(store.similarity_search(query, k=K, filter={"company": c}))
bal_dist = Counter(d.metadata["company"] for d in balanced)

print("plain top-k distribution :", dict(plain_dist))
print("balanced distribution    :", dict(bal_dist))

assert set(bal_dist) == set(companies), f"missing companies: {set(companies) - set(bal_dist)}"
# k is a ceiling: a company with fewer than k chunks returns all it has.
expected = {"Alphabet": 2, "Amazon": 3, "Microsoft": 3}
assert dict(bal_dist) == expected, f"got {dict(bal_dist)}, expected {expected}"
print("\nPASS: every company represented; plain top-k starved Alphabet, balanced did not")
