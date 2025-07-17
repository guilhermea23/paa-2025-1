import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
from core.recommend import RecommendationSystem

def debug_gladiator_vs_django():
    """Debug why Django Unchained ranks higher than Gladiator"""
    
    print("=== DEBUGGING GLADIATOR vs DJANGO RANKING ===\n")
    
    # Load system
    rec_system = RecommendationSystem(
        index_path="assets/faiss_index.idx",
        data_path="assets/movie_data.pkl"
    )
    
    query = "A movie about a roman soldier who becomes a slave and has to fight to the top in order to defeat the evil son of Marcus Aurelius"
    
    test_results = rec_system.search(
        query=query,
        final_k=5,
        candidate_k=50,
        dense_weight=0.1,
        cross_weight=0.5,
        rating_weight=0.4
    )
    for i, movie_id in enumerate(test_results):
        # Find movie by ID
        movie_row = rec_system.movies[rec_system.movies['id'] == int(movie_id)]
        if len(movie_row) > 0:
            movie = movie_row.iloc[0]
            print(f"  {i+1}. {movie['title']}")
        else:
            print(f"  {i+1}. Movie ID {movie_id} not found!")

if __name__ == "__main__":
    debug_gladiator_vs_django()