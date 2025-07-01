import csv
import sqlite3

with open("backend/bdPAA.csv", "r", encoding="utf-8") as csvfile:
    leitor_csv = csv.reader(csvfile)
    cabecalho = next(leitor_csv)  # Lê a primeira linha (nomes das colunas)

    # Construir instrução SQL com os campos como TEXT
    colunas_sql = ", ".join([f"{col} TEXT NOT NULL" for col in cabecalho])

    # Conexão com o banco de dados
    connection = sqlite3.connect("backend/bdPAA.db")
    cursor = connection.cursor()

    # Criar tabela
    cursor.execute(f"CREATE TABLE IF NOT EXISTS filmes ({colunas_sql})")

    # Inserir dados linha por linha
    for linha in leitor_csv:
        if len(linha) != len(cabecalho):
            continue  # Pula linhas com número incorreto de colunas

        row = dict(zip(cabecalho, linha))  # Cria dicionário {coluna: valor}

        cursor.execute(
            f"INSERT OR IGNORE INTO filmes ({', '.join(cabecalho)}) VALUES ({', '.join(['?'] * len(cabecalho))})",
            [row[col] for col in cabecalho],
        )

    # Finaliza
    connection.commit()
    connection.close()
    print("Banco de dados criado e dados inseridos com sucesso.")
