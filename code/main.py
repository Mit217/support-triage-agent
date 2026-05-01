from retriever import load_docs, build_or_load_index, retrieve

docs = load_docs()

print(f"Loaded {len(docs)} docs")

index, embeddings = build_or_load_index(docs)

query = "I was charged twice"

results = retrieve(query, docs, index)

for r in results:
    print("\n---")
    print(r["path"])
    print(r["content"][:300])