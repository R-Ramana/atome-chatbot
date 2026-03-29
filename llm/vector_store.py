import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

docs_store = {}

def normalize(v):
    return v / np.linalg.norm(v)

def build_index(docs, namespace="default"):
    global docs_store

    store = []

    for d in docs:
        emb = model.encode(d)
        emb = normalize(emb)
        store.append((d, emb))
    
    docs_store[namespace] = store
    print(f"Indexed {len(docs_store)} chunks for namespace {namespace}")

def cosine_sim(a, b):
    return np.dot(a, b)

def expand_query(q):
    return f"{q}. Explain what this is in detail."

def search(query, namespace="default"):
    if namespace not in docs_store:
        print(f"No namespace found: {namespace}")
        return []

    query_expanded = expand_query(query)

    q_emb = model.encode(query_expanded)
    q_emb = normalize(q_emb)

    results = []

    for d, emb in docs_store[namespace]:
        score = cosine_sim(q_emb, emb)

        if "atome card" in d.lower():
            score += 0.3

        results.append((d, score))

    results.sort(key=lambda x: x[1], reverse=True)

    print("\n=== TOP RESULTS ===")
    for i, (doc, score) in enumerate(results[:3]):
        print(f"\nTOP {i+1} SCORE:", score)
        print(doc[:200])

    return [r[0] for r in results[:5]]