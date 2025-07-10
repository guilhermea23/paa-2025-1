# MovieAI Projeto PAA 2025

# Back-End

# Configuração de ambiente
É recomendado criar um ambiente virtual antes de instalar os pacotes necessários para a execução desse projeto. Dessa forma, tendo o python e pip instalados, execute o seguinte comando:

```
$ python3 -m venv .venv
```

Dessa forma você criou uma pasta .venv que simboliza o seu ambiente virtual, separado do resto do seu dispositivo e evitando quaisquer conflitos com outros projetos. Logo em seguida é necessário ativar esse ambiente.

No linux ou mac:
```
$ source .venv/bin/activate
```

## Configuração da DB

Segue um passo a passo para configuração do banco de dados na pasta `backend`. Para evitar problemas de arquivos muito grandes, decidimos não incluir o banco de dados sqlite no repositório. Dessa forma ele deve ser carregado a partir do arquivo `movies.csv`. Para isso, dentro do diretório `backend` execute o seguinte comando:

```
$ python3 create_db.py
```

## Como rodar
```
$ uvicorn main:app --reload
```

# Front-End

## Passo a passo para executar o front-end do projeto

### Pré-requisitos

Antes de começar, garanta que você tenha as seguintes ferramentas instaladas na sua máquina:

- [Node.js](https://nodejs.org/) (versão 18.x ou superior)
- [pnpm](https://pnpm.io/installation) (gerenciador de pacotes)

```bash
npm install -g pnpm
```

1. Navegue para a pasta `frontend`

2. Instale as dependências

```bash
pnpm install
```

3. Configurar as variáveis de ambiente  

```bash
cp .env.example .env.local
```

4. Sincronizar o Banco de Dados

Este projeto usa o Prisma para gerenciar o banco de dados. Após configurar a DATABASE_URL no passo anterior, rode o seguinte comando para sincronizar o schema do Prisma com o seu banco de dados:
Bash

```bash
pnpm db:push
```

5. Rodar o Projeto

Com tudo configurado, inicie o servidor de desenvolvimento:
Bash

```bash
pnpm dev
```
ou
```bash
npm run dev
```

Follow our deployment guides for [Vercel](https://create.t3.gg/en/deployment/vercel), [Netlify](https://create.t3.gg/en/deployment/netlify) and [Docker](https://create.t3.gg/en/deployment/docker) for more information.
