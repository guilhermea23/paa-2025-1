from sentence_transformers import SentenceTransformer, CrossEncoder

import numpy as np
import pandas as pd
import logging
import faiss
import time


class RecommendationSystem:
    def __init__(self, index_path: str, data_path: str):
        self.logger = logging.getLogger(__name__)

        # load models
        self.dense_model = SentenceTransformer(
            "sentence-transformers/all-mpnet-base-v2"
        )
        self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-12-v2")

        self.movies = pd.read_pickle(data_path)
        self.index = faiss.read_index(index_path)

        self._warmup()

    def search(
        self,
        query: str,
        final_k: int,
        candidate_k: int,
        dense_weight: float,
        cross_weight: float,
        rating_weight: float,
    ) -> list[str]:
        self.logger.debug(f"Starting search: '{query}'")

        # --- Stage 1: FAISS ANN retrieval ---
        encoding_start = time.time()

        # encode & normalize query (FAISS expects float32)
        query_embedding = self.dense_model.encode(
            [query], normalize_embeddings=True
        ).astype("float32")

        encoding_time = (time.time() - encoding_start) * 1000
        self.logger.info(f"Encoding time: {encoding_time:.1f}ms")

        faiss_start = time.time()

        # retrieve top candidate_k via FAISS inner-product
        distances, indices = self.index.search(query_embedding, candidate_k)
        top_indices = indices[0]  # shape: (candidate_k,)
        faiss_time = (time.time() - faiss_start) * 1000
        self.logger.info(f"FAISS time: {faiss_time:.1f}ms")

        self.logger.info(f"FAISS: ")

        # --- Stage 2: cross-encoder + rating reranking ---

        # prepare candidate list
        candidates: list[dict] = []
        for idx, dense_score in zip(top_indices, distances[0]):
            movie = self.movies.iloc[idx]
            text = f"{movie['title']} {movie['genres']} {movie['overview']}"

            candidates.append(
                {
                    "idx": idx,
                    "doc_text": text,
                    "vote_average": movie["vote_average"],
                    "dense_score": float(dense_score),
                }
            )

        # --- Stage 2: cross-encoder + rating reranking ---
        self.logger.info("Stage 2: multi-signal reranking…")
        reranking_start = time.time()

        # cross-encoder
        pairs = [(query, c["doc_text"]) for c in candidates]

        dense_scores = self._normalize([c["dense_score"] for c in candidates])
        cross_scores = self._normalize(self.cross_encoder.predict(pairs).tolist())
        rating_scores = self._normalize([c["vote_average"] for c in candidates])

        # combine
        for i, candidate in enumerate(candidates):
            candidate["score"] = (
                dense_weight * dense_scores[i]
                + cross_weight * cross_scores[i]
                + rating_weight * rating_scores[i]
            )

        # sort & take top final_k
        reranked = sorted(candidates, key=lambda x: x["score"], reverse=True)

        reranking_time = (time.time() - reranking_start) * 1000
        total_time = time.time() * 1000 - encoding_time

        self.logger.info(f"Reranking: {reranking_time:.1f}ms")
        self.logger.info(f"Total: {total_time:.1f}ms")

        result_ids = []
        for c in reranked[:final_k]:
            idx = c["idx"]
            movie = self.movies.iloc[idx]
            
            # Use the actual movie ID from your DataFrame
            result_ids.append(str(movie['id']))
        
        return result_ids

    def _warmup(self):
        self.dense_model.encode("warmup")
        self.cross_encoder.predict([("warmup", "warm")])

    @staticmethod
    def _normalize(scores: list[float]) -> list[float]:
        arr = np.array(scores, dtype="float32")
        mn, mx = arr.min(), arr.max()
        if mx - mn < 1e-6:
            return [0.5] * len(arr)
        return ((arr - mn) / (mx - mn)).tolist()
