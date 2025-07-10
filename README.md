# paa-2025-1

## Passo a passo para configuração do banco de dados na pasta `backend`

Como o arquivo de fonte dos filmes excede os 100MB permitido pelo GitHub, a configuração deve ser feita localmente da seguinte maneira:

1. Baixe o arquivo fonte no formato `.csv` dentro da pasta de trabalho (`backend`)

2. Após isso renomeie o arquivo para __bdPAA.csv__

3. Execute o arquivo  `backend/create_db.py` apenas uma vez para não criar um banco de dados com duplicatas

## Como rodar
```
$ uvicorn main:app --reload
```
