from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import os

model = SentenceTransformer("all-MiniLM-L6-v2")

def chunk_text(text, chunk_size=1000):
    chunks = []

    for i in range(0, len(text), chunk_size):
        chunk = text[i:i+chunk_size]
        chunks.append(chunk)

    return chunks


from pathlib import Path

def chunk_text(text, chunk_size=500):
    chunks = []

    for i in range(0, len(text), chunk_size):
        chunk = text[i:i+chunk_size]
        chunks.append(chunk)

    return chunks


def load_docs(folder="data"):
    docs = []

    for file in Path(folder).rglob("*"):
        if file.is_file():
            try:
                text = file.read_text(encoding="utf-8")

                chunks = chunk_text(text)

                for chunk in chunks:
                    docs.append({
                        "path": str(file),
                        "content": chunk
                    })

            except Exception as e:
                print(f"Failed to read {file}: {e}")

    return docs

def build_or_load_index(docs):

    if os.path.exists("data/index.pkl"):
        print("Loading saved index...")

        with open("data/index.pkl", "rb") as f:
            return pickle.load(f)

    print("Building embeddings...")

    texts = [doc["content"] for doc in docs]

    embeddings = model.encode(texts)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))

    data = (index, embeddings)

    with open("data/index.pkl", "wb") as f:
        pickle.dump(data, f)

    return data


def retrieve(query, docs, index, k=3):
    query_embedding = model.encode([query])

    distances, indices = index.search(
        np.array(query_embedding),
        k
    )

    results = []

    for i in indices[0]:
        results.append(docs[i])

    return results