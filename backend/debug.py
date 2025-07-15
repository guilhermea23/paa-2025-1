import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer, CrossEncoder
import logging

def debug_action_christmas():
    """Debug the specific 'action christmas' query step by step"""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    print("=== DEBUGGING 'action christmas' QUERY ===\n")
    
    # Load components
    movies = pd.read_pickle("assets/movie_data.pkl")
    index = faiss.read_index("assets/faiss_index.idx")
    dense_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-12-v2")
    
    query = "action christmas"
    candidate_k = 50
    final_k = 7
    
    print(f"Query: '{query}'")
    print(f"Looking for {candidate_k} candidates, returning {final_k} final results\n")
    
    # === STAGE 1: FAISS SEARCH ===
    print("=== STAGE 1: FAISS SEARCH ===")
    
    query_embedding = dense_model.encode([query], normalize_embeddings=True).astype("float32")
    distances, indices = index.search(query_embedding, candidate_k)
    top_indices = indices[0]
    
    print(f"Top 10 FAISS results:")
    for i in range(min(10, len(top_indices))):
        idx = top_indices[i]
        score = distances[0][i]
        if idx < len(movies):
            movie = movies.iloc[idx]
            print(f"  {i+1:2d}. Score: {score:.3f} | {movie['title']} | {movie['genres']}")
        else:
            print(f"  {i+1:2d}. INVALID INDEX: {idx}")
    
    # Look for actual Christmas movies in the dataset
    print(f"\n=== CHECKING FOR CHRISTMAS MOVIES IN DATASET ===")
    christmas_keywords = ['christmas', 'holiday', 'santa', 'xmas']
    christmas_movies = []
    
    for idx, movie in movies.iterrows():
        title_lower = str(movie['title']).lower()
        overview_lower = str(movie.get('overview', '')).lower()
        genres_lower = str(movie.get('genres', '')).lower()
        
        if any(keyword in title_lower or keyword in overview_lower or keyword in genres_lower 
               for keyword in christmas_keywords):
            christmas_movies.append((idx, movie))
    
    print(f"Found {len(christmas_movies)} potential Christmas movies in dataset:")
    for i, (idx, movie) in enumerate(christmas_movies[:10]):  # Show first 10
        print(f"  {movie['title']} (idx: {idx})")
    
    # Check if any Christmas movies appeared in FAISS results
    christmas_indices = {idx for idx, _ in christmas_movies}
    faiss_christmas = [idx for idx in top_indices if idx in christmas_indices]
    print(f"\nChristmas movies in FAISS top {candidate_k}: {faiss_christmas}")
    
    # === STAGE 2: CROSS-ENCODER RERANKING ===
    print(f"\n=== STAGE 2: CROSS-ENCODER RERANKING ===")
    
    # Prepare candidates
    candidates = []
    for idx, dense_score in zip(top_indices, distances[0]):
        if idx < len(movies):
            movie = movies.iloc[idx]
            genres = movie['genres'] if pd.notna(movie['genres']) else ''
            overview = movie['overview'] if pd.notna(movie['overview']) else ''
            text = f"{genres} {overview}".strip()
            
            candidates.append({
                "idx": idx,
                "title": movie['title'],
                "doc_text": text,
                "vote_average": movie["vote_average"],
                "dense_score": float(dense_score),
                "genres": movie['genres']
            })
    
    # Cross-encoder scoring
    pairs = [(query, c["doc_text"]) for c in candidates]
    cross_scores_raw = cross_encoder.predict(pairs).tolist()
    
    # Normalize scores
    def normalize(scores):
        arr = np.array(scores, dtype="float32")
        mn, mx = arr.min(), arr.max()
        if mx - mn < 1e-6:
            return [0.5] * len(arr)
        return ((arr - mn) / (mx - mn)).tolist()
    
    dense_scores = normalize([c["dense_score"] for c in candidates])
    cross_scores = normalize(cross_scores_raw)
    rating_scores = normalize([c["vote_average"] for c in candidates])
    
    # Combine scores
    dense_weight, cross_weight, rating_weight = 0.4, 0.4, 0.2
    
    for i, candidate in enumerate(candidates):
        candidate["cross_score_raw"] = cross_scores_raw[i]
        candidate["cross_score_norm"] = cross_scores[i] 
        candidate["dense_score_norm"] = dense_scores[i]
        candidate["rating_score_norm"] = rating_scores[i]
        candidate["final_score"] = (
            dense_weight * dense_scores[i] +
            cross_weight * cross_scores[i] +
            rating_weight * rating_scores[i]
        )
    
    # Sort and show results
    reranked = sorted(candidates, key=lambda x: x["final_score"], reverse=True)
    
    print(f"Top 10 after reranking:")
    print(f"{'Rank':<4} {'Final':<5} {'Dense':<5} {'Cross':<5} {'Rating':<6} {'Title':<30} {'Genres'}")
    print("-" * 80)
    
    for i, c in enumerate(reranked[:10]):
        print(f"{i+1:<4} {c['final_score']:.3f} {c['dense_score_norm']:.3f} "
              f"{c['cross_score_norm']:.3f} {c['rating_score_norm']:.3f} "
              f"{c['title'][:30]:<30} {str(c['genres'])[:20]}")
    
    # === ANALYSIS ===
    print(f"\n=== ANALYSIS ===")
    
    # Check if cross-encoder is helping or hurting
    print("Cross-encoder raw scores for top 5 FAISS results:")
    for i in range(min(5, len(candidates))):
        c = candidates[i]  # These are in FAISS order
        print(f"  {c['title'][:40]:<40} | Cross-encoder: {c['cross_score_raw']:.3f}")
    
    # Check final ranking
    final_results = reranked[:final_k]
    christmas_in_final = [c for c in final_results if c['idx'] in christmas_indices]
    
    print(f"\nFinal {final_k} results contain {len(christmas_in_final)} Christmas movies")
    
    if len(christmas_in_final) == 0:
        print("❌ PROBLEM: No Christmas movies in final results!")
        print("\nPossible issues:")
        print("1. FAISS not finding Christmas movies (check embeddings)")
        print("2. Cross-encoder demoting Christmas movies") 
        print("3. Query format mismatch")
        print("4. Not enough Christmas movies in dataset")
    else:
        print("✅ Found some Christmas movies in results")
    
    return reranked[:final_k]

if __name__ == "__main__":
    results = debug_action_christmas()