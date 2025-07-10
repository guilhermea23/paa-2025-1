from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from datetime import datetime
from typing import List

import logging
import torch
import sqlite3
import json

from core.recommend import RecommendationSystem

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading recommendation system...")

    # --- startup code ---
    app.state.recommender = RecommendationSystem(
        index_path="assets/faiss_index.idx",
        data_path="assets/movie_data.pkl",
    )

    logger.info("Load completed successfully.")
    yield

    # --- shutdown code ---
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        torch.mps.empty_cache()


app = FastAPI(lifespan=lifespan)


def get_db():
    conn = sqlite3.connect("movies.db")
    try:
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        conn.close()


class PromptRequest(BaseModel):
    prompt: str


class Filme(BaseModel):
    id: str
    nome: str
    sinopse: str
    estrelas: float
    generos: List[str]
    data_lancamento: datetime


class RecommendationResponse(BaseModel):
    filmes: List[Filme]


def get_filmes_by_ids(db: sqlite3.Connection, ids: List[str]) -> List[Filme]:
    """
    Busca filmes no banco SQLite pelo campo 'id' e retorna uma lista de objetos Filme.
    """
    # db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # Construindo a cláusula IN dinamicamente
    placeholders = ",".join("?" for _ in ids)
    query = f"""
        SELECT id, title, overview, vote_average, genres, release_date
        FROM filmes
        WHERE id IN ({placeholders})
    """
    cursor.execute(query, ids)
    rows = cursor.fetchall()

    filmes: List[Filme] = []
    for row in rows:
        # Parse genres: assume JSON array string ou string separada por vírgulas
        raw_genres: str = row["genres"]
        try:
            generos_list = json.loads(raw_genres)
            if not isinstance(generos_list, list):
                generos_list = [str(generos_list)]
            generos_list = [str(g) for g in generos_list]
        except (json.JSONDecodeError, TypeError):
            generos_list = [g.strip() for g in raw_genres.split(",") if g.strip()]

        # Converter vote_average para inteiro (estrelas)
        estrelas = round(float(row["vote_average"]))

        # Converter data para datetime
        data_lancamento = datetime.fromisoformat(row["release_date"])

        filme = Filme(
            id=str(row["id"]),
            nome=row["title"],
            sinopse=row["overview"],
            estrelas=estrelas,
            generos=generos_list,
            data_lancamento=data_lancamento,
        )
        filmes.append(filme)

    db.close()
    return filmes


@app.post("/recommendations", response_model=RecommendationResponse)
def get_recommendations(
    request: PromptRequest, db: sqlite3.Connection = Depends(get_db)
):
    system: RecommendationSystem = app.state.recommender
    prompt = request.prompt.strip()

    movie_ids = system.search(
        prompt,
        final_k=10,
        candidate_k=50,
        dense_weight=0.1,
        cross_weight=0.5,
        rating_weight=0.4,
    )
    movies = get_filmes_by_ids(db, movie_ids)

    return RecommendationResponse(filmes=movies)