from sentence_transformers import SentenceTransformer, CrossEncoder

import time
import logging
import numpy as np
import pandas as pd


class RecommendationSystem:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.logger.info("Loading recommendation system...")
        self.dense_model = SentenceTransformer(
            "sentence-transformers/all-mpnet-base-v2"
        )
        self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-12-v2")

        self.embeddings = np.load("assets/movie_embeddings_mpnet.npy")
        self.movies = pd.read_pickle("assets/movie_data.pkl")
        self.logger.info("Successfully loaded recommendation system.")

    def search_with_multi_signal_reranking(
        self,
        query,
        final_k=10,
        candidate_k=50,
        dense_weight=0.3,
        cross_weight=0.5,
        rating_weight=0.2,
        rating_boost=True,
        normalize_scores=True,
    ):
        self.logger.info(f"Multi-signal search: '{query}'")
        self.logger.info(
            f"Weights - Dense: {dense_weight:.1f}, Cross: {cross_weight:.1f}, Rating: {rating_weight:.1f}"
        )
        self.logger.info(f"Stage 1: Getting top {candidate_k} candidates...")

        # Stage 1: Dense retrieval (unchanged)
        start_time = time.time()
        query_embedding = self.dense_model.encode([query], normalize_embeddings=True)
        similarities = np.dot(self.embeddings, query_embedding.T).flatten()
        top_indices = np.argsort(similarities)[-candidate_k:][::-1]
        stage1_time = time.time() - start_time

        self.logger.info(f"Dense retrieval: {stage1_time*1000:.1f}ms")

        # Prepare candidates for reranking
        candidates = []
        for idx in top_indices:
            movie = self.movies.iloc[idx]
            doc_text = f"{movie['title']} {movie['genres']} {movie['overview']}"
            candidates.append(
                {
                    "idx": idx,
                    "movie": movie,
                    "doc_text": doc_text,
                    "dense_score": similarities[idx],
                }
            )

        # Stage 2: Multi-signal reranking
        self.logger.info("Stage 2: Multi-signal reranking...")
        start_time = time.time()

        # Get cross-encoder scores
        query_doc_pairs = [(query, candidate["doc_text"]) for candidate in candidates]
        cross_scores = self.cross_encoder.predict(query_doc_pairs)

        # Collect all scores
        dense_scores = [c["dense_score"] for c in candidates]
        rating_scores = (
            [c["movie"]["vote_average"] for c in candidates] if rating_boost else None
        )

        # Normalize scores to [0,1] range if requested
        if normalize_scores:
            dense_scores = self.normalize_score_array(dense_scores)
            cross_scores = self.normalize_score_array(cross_scores)
            if rating_boost and rating_scores is not None:
                rating_scores = self.normalize_score_array(rating_scores)

        # Calculate combined scores
        for i, candidate in enumerate(candidates):
            combined_score = (
                dense_weight * dense_scores[i] + cross_weight * cross_scores[i]
            )

            if rating_boost and rating_scores is not None:
                combined_score += rating_weight * rating_scores[i]

            candidate.update(
                {
                    "cross_score": cross_scores[i],
                    "rating_score": (
                        rating_scores[i] if rating_scores is not None else 0
                    ),
                    "combined_score": combined_score,
                }
            )

        # Sort by combined scores
        reranked_candidates = sorted(
            candidates, key=lambda x: x["combined_score"], reverse=True
        )

        stage2_time = time.time() - start_time
        self.logger.info(f"Multi-signal reranking: {stage2_time*1000:.1f}ms")
        self.logger.info(f"Total time: {(stage1_time + stage2_time)*1000:.1f}ms")

        results: list[str] = []
        for i, candidate in enumerate(reranked_candidates[:final_k], 1):
            results.append(str(candidate["idx"]))

        return results

    def normalize_score_array(self, scores):
        """Normalize array of scores to [0,1] range"""
        scores = np.array(scores)
        min_score, max_score = scores.min(), scores.max()
        if max_score - min_score == 0:
            return np.ones_like(scores) * 0.5  # All scores are same
        return (scores - min_score) / (max_score - min_score)