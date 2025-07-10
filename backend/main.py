from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from datetime import datetime

import sqlite3
import uuid
import json

app = FastAPI()

class PromptRequest(BaseModel):
    prompt: str


class Filme(BaseModel):
    id: str
    nome: str
    sinopse: str
    estrelas: float
    generos: list[str]
    data_lancamento: datetime


class RecommendationResponse(BaseModel):
    filmes: List[Filme]


def get_filmes_by_ids(db_path: str, ids: List[str]) -> List[Filme]:
    """
    Busca filmes no banco SQLite pelo campo 'id' e retorna uma lista de objetos Filme.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

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
            data_lancamento=data_lancamento
        )
        filmes.append(filme)

    conn.close()
    return filmes


@app.post("/recommendations", response_model=RecommendationResponse)
def get_recommendations(request: PromptRequest):
    prompt = request.prompt.strip()

    exemplos = {
        "ação": [
            {"nome": "Mad Max: Estrada da Fúria", "estrelas": 5},
            {"nome": "John Wick", "estrelas": 4},
            {"nome": "Velocidade Máxima", "estrelas": 3},
        ],
        "romance": [
            {"nome": "Orgulho e Preconceito", "estrelas": 5},
            {"nome": "La La Land", "estrelas": 4},
            {"nome": "Como Eu Era Antes de Você", "estrelas": 4},
        ],
    }

    if "ação" in prompt.lower():
        categoria = "ação"
    else:
        categoria = "romance"
    filmes_recomendados = exemplos.get(categoria, [])

    resposta = RecommendationResponse(
        filmes=[
            Filme(id=str(uuid.uuid4()), nome=filme["nome"], estrelas=filme["estrelas"])
            for filme in filmes_recomendados
        ]
    )

    return resposta
