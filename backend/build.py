# build_faiss_index.py
import faiss
import numpy as np

def main(embeddings_path="assets/movie_embeddings_roberta.npy",
         index_path="assets/faiss_index.idx"):
    # 1) load your precomputed embeddings
    embeddings = np.load(embeddings_path).astype("float32")

    # 2) normalize if you want inner-product == cosine
    faiss.normalize_L2(embeddings)

    # 3) build the index
    dim   = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    # 4) write it to disk
    faiss.write_index(index, index_path)
    print(f"✅ Built and saved FAISS index with {index.ntotal} vectors to {index_path}")

if __name__ == "__main__":
    main()
