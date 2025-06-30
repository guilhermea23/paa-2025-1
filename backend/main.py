from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uuid

app = FastAPI()


class PromptRequest(BaseModel):
    prompt: str


class Filme(BaseModel):
    id: str
    nome: str
    estrelas: int


class RecommendationResponse(BaseModel):
    filmes: List[Filme]


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
