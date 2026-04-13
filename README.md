# Python Agent Challenge

Solução em Python para o desafio técnico com API, orquestração de fluxo, tool de conhecimento via HTTP, LLM no fluxo principal e resposta rastreável por seção.

## Objetivo

Expor um endpoint `POST /messages` que:

1. recebe a pergunta do usuário;
2. busca contexto na KB oficial via `KB_URL`;
3. seleciona trechos relevantes;
4. chama o LLM com pergunta + contexto;
5. retorna:
   - `answer`
   - `sources` com apenas `section`.

Quando não há contexto suficiente, retorna o fallback obrigatório:

```json
{
  "answer": "Não encontrei informação suficiente na base para responder essa pergunta.",
  "sources": []
}
````
Requisitos
Python 3.12+
Docker Desktop
Docker Compose
Git
Variáveis de ambiente

Crie um arquivo .env na raiz do projeto com base no .env.example.

Exemplo:

OPENAI_API_KEY=sua_chave_aqui
KB_URL=https://url-oficial-do-desafio
MODEL=gpt-4o-mini

A KB_URL deve ser a URL oficial da base do desafio.

Como rodar
Opção 1: com Docker
Clone o repositório:
git clone <url-do-repositorio>
cd python-agent-challenge
Crie o arquivo .env na raiz do projeto.
Abra o Docker Desktop e aguarde iniciar completamente.
Suba a aplicação:
docker compose up -d --build

Ou com Makefile:

make up
Verifique os logs:
docker compose logs -f
Acesse:
API: http://localhost:8000
Docs: http://localhost:8000/docs
Opção 2: localmente com ambiente virtual
Clone o repositório:
git clone <url-do-repositorio>
cd python-agent-challenge
Crie e ative o ambiente virtual.

No Windows PowerShell:

python -m venv .venv
.venv\Scripts\Activate.ps1

No Linux/macOS:

python3 -m venv .venv
source .venv/bin/activate
Instale as dependências:
pip install --upgrade pip
pip install -r requirements.txt
Crie o arquivo .env na raiz do projeto.
Inicie a aplicação:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
Acesse:
API: http://localhost:8000
Docs: http://localhost:8000/docs
Como testar

Exemplo de requisição:

{
  "message": "O que é composição?",
  "session_id": "sessao-123"
}
cURL
curl -X POST "http://localhost:8000/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "O que é composição?",
    "session_id": "sessao-123"
  }'
PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/messages" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{
    "message": "O que é composição?",
    "session_id": "sessao-123"
  }'
Testes

Com pytest:

pytest -v

Ou com Makefile:

make test
Comandos úteis

Subir a aplicação:

make up

Derrubar a aplicação:

make down

Rodar testes:

make test
Estrutura do projeto
.
├── app/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── .env.example
└── README.md
Problema comum com Docker

Se aparecer o erro:

open //./pipe/dockerDesktopLinuxEngine: O sistema não pode encontrar o arquivo especificado

significa que o Docker Desktop não está aberto ou ainda não terminou de iniciar.

Solução:

Abra o Docker Desktop.
Aguarde ele iniciar completamente.
Rode novamente:
docker compose up -d --build

Para verificar se o Docker está ativo:

docker version
