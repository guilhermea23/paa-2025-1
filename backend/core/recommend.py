from sentence_transformers import SentenceTransformer, CrossEncoder
import faiss
import time
import logging
import numpy as np
import pandas as pd


class RecommendationSystem:
    def __init__(self, index_path: str, data_path: str):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Loading recommendation system…")

        # load models
        self.dense_model = SentenceTransformer(
            "sentence-transformers/all-mpnet-base-v2"
        )
        self.logger.info(f"Loaded dense model.")

        self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-12-v2")
        self.logger.info(f"Loaded cross encoder.")

        # load movie metadata
        self.movies = pd.read_pickle(data_path)

        # load prebuilt FAISS index
        # faiss.omp_set_num_threads(8)
        self.index = faiss.read_index(index_path)
        self.logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors.")

        self.logger.info("Successfully loaded recommendation system.")

    def search_with_multi_signal_reranking(
        self,
        query: str,
        final_k: int = 10,
        candidate_k: int = 50,
        dense_weight: float = 0.3,
        cross_weight: float = 0.5,
        rating_weight: float = 0.2,
        rating_boost: bool = True,
        normalize_scores: bool = True,
    ) -> list[str]:
        self.logger.info(f"🔍 Multi-signal search: '{query}'")

        # --- Stage 1: FAISS ANN retrieval ---
        start = time.time()

        # encode & normalize query
        q_emb = self.dense_model.encode([query], normalize_embeddings=True)
        # FAISS expects float32
        q_emb = q_emb.astype("float32")

        stage1_time = (time.time() - start) * 1000
        self.logger.info(f"  Encoding time: {stage1_time:.1f}ms")

        middle = time.time()

        # retrieve top candidate_k via FAISS inner-product
        distances, indices = self.index.search(q_emb, candidate_k)
        top_indices = indices[0]  # shape: (candidate_k,)
        stage1_time = (time.time() - middle) * 1000
        self.logger.info(
            f"  ✅ FAISS retrieval ({candidate_k} nearest): {stage1_time:.1f}ms"
        )

        # prepare candidate list
        candidates = []
        for idx, dense_score in zip(top_indices, distances[0]):
            movie = self.movies.iloc[idx]
            text = f"{movie['title']} {movie['genres']} {movie['overview']}"
            candidates.append(
                {
                    "idx": idx,
                    "movie": movie,
                    "doc_text": text,
                    "dense_score": float(dense_score),  # faiss returns numpy types
                }
            )

        # --- Stage 2: cross-encoder + rating reranking ---
        self.logger.info("Stage 2: multi-signal reranking…")
        start = time.time()

        # cross-encoder
        pairs = [(query, c["doc_text"]) for c in candidates]
        cross_scores = self.cross_encoder.predict(pairs).tolist()

        # optional rating boost
        rating_scores = (
            [c["movie"]["vote_average"] for c in candidates] if rating_boost else None
        )

        # normalize each score array to [0,1]
        if normalize_scores:
            dense_arr = self._normalize([c["dense_score"] for c in candidates])
            cross_arr = self._normalize(cross_scores)
            if rating_boost:
                rating_arr = self._normalize(rating_scores)
        else:
            dense_arr, cross_arr, rating_arr = (
                [c["dense_score"] for c in candidates],
                cross_scores,
                rating_scores or [],
            )

        # combine
        for i, c in enumerate(candidates):
            score = dense_weight * dense_arr[i] + cross_weight * cross_arr[i]
            if rating_boost:
                score += rating_weight * rating_arr[i]
            c.update(
                {
                    "cross_score": cross_arr[i],
                    "rating_score": rating_arr[i] if rating_boost else 0.0,
                    "combined_score": score,
                }
            )

        # sort & take top final_k
        reranked = sorted(candidates, key=lambda x: x["combined_score"], reverse=True)
        stage2_time = (time.time() - start) * 1000
        self.logger.info(f"  ✅ Reranking: {stage2_time:.1f}ms")
        self.logger.info(f"  ✅ Total: {(stage1_time + stage2_time):.1f}ms")

        return [str(c["idx"]) for c in reranked[:final_k]]

    @staticmethod
    def _normalize(scores: list[float]) -> list[float]:
        arr = np.array(scores, dtype="float32")
        mn, mx = arr.min(), arr.max()
        if mx - mn < 1e-6:
            return [0.5] * len(arr)
        return ((arr - mn) / (mx - mn)).tolist()
