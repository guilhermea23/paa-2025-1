import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss

# Load your data
emb = np.load("assets/movie_embeddings_mpnet.npy")
movies = pd.read_pickle("assets/movie_data.pkl")

print("Número de embeddings:", emb.shape[0])
print("Número de filmes   :", len(movies))

# Verify alignment
assert emb.shape[0] == len(movies), "Mismatch entre embeddings e filmes!"

model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Test with the SAME format used during embedding generation
test_idx = 123
row = movies.iloc[test_idx]

# Recreate the exact same text format used for embeddings
genres = row['genres'] if pd.notna(row['genres']) else ''
overview = row['overview'] if pd.notna(row['overview']) else ''
query = f"{genres} {overview}".strip()

print(f"\nTesting movie at index {test_idx}:")
print(f"Title: {row['title']}")
print(f"Query text: {query[:100]}...")  # First 100 chars

# Encode the query
q_emb = model.encode([query], normalize_embeddings=True)

# Search
idx = faiss.read_index("assets/faiss_index.idx")
D, I = idx.search(q_emb, 5)

print(f"\nResults:")
print(f"Should include {test_idx}: {I[0]}")
print(f"Scores (should be ~1.0): {D[0]}")

# Check if our target index is in the results
if test_idx in I[0]:
    position = np.where(I[0] == test_idx)[0][0]
    score = D[0][position]
    print(f"✅ Found index {test_idx} at position {position} with score {score:.6f}")
else:
    print(f"❌ Index {test_idx} not found in top 5 results")

# Additional verification: compare embeddings directly
print(f"\nDirect embedding comparison:")
stored_emb = emb[test_idx:test_idx+1]  # Get embedding for our test movie
direct_similarity = np.dot(q_emb, stored_emb.T)[0][0]
print(f"Direct cosine similarity: {direct_similarity:.6f}")