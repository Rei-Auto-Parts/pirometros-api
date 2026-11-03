# pirometros-api

API interna da fundição que lê as leituras dos pirômetros de imersão e as transforma em
informação e histórico para os gestores. Stack: Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic,
Pydantic v2 e psycopg 3. Segue o padrão de desenvolvimento da Byte Union.

## Contexto

O software do fabricante grava as leituras num SQL Server local. Um sincronizador (outro
repositório) as copia a cada 5 minutos para o Postgres, banco `pirometros`, tabela
`public.receiver_data`. Esta API **só lê** essa tabela: nunca a cria, altera, apaga ou migra.
As tabelas da própria API ficam no schema `app` do mesmo banco.

Restrições (detalhes em `.specify/project.md`):

- só o banco `pirometros` pode ser tocado (o Postgres tem outros bancos em produção);
- `reg_date` é `timestamp` sem fuso, em horário local (America/Sao_Paulo): nunca converter fuso;
- sem autenticação por enquanto (a VPS é interna).

## Desenvolvimento

Tudo roda em Docker, pelo `Makefile` em `app/`. Pré-requisitos: Docker com Compose e `make`.

```bash
cd app
make infra      # builda a imagem e sobe o serviço dev e um Postgres descartável
make install    # instala as dependências dentro do serviço dev
make init       # espera o Postgres e aplica as migrations do schema app
make run        # sobe a API em http://localhost:8000
make validate   # fmt, lint, test, cover (mínimo 90%), it e bdd
make down       # derruba os containers
```

- Saúde: `GET http://localhost:8000/api/health`
- Documentação OpenAPI: `http://localhost:8000/api/docs`
- Outros alvos: `make help`. Os testes `it` e `bdd` usam o Postgres do compose, que não tem
  `public.receiver_data`: a fixture de `app/tests/support/` cria uma tabela igual só nesse banco
  descartável.

## Endpoints

Tudo é leitura de `public.receiver_data`. As datas são horário local, sem fuso (`2026-10-29T11:00:30`).
`start` e `end` são obrigatórios, inclusivos e não aceitam fuso.

| Rota | O que devolve |
|---|---|
| `GET /api/readings?start=&end=&dev_id=&page=&page_size=` | leituras do período, da mais recente para a mais antiga pela data da medição; `dev_id` (serial) é repetível; página padrão 50, máximo 500 |
| `GET /api/readings/series?start=&end=&dev_id=` | pontos de temperatura agrupados por pirômetro, em ordem de data; período máximo de 31 dias |
| `GET /api/pyrometers` | pirômetros existentes, com serial e nome atual |

Erros: `422` para parâmetro inválido ou período da série acima de 31 dias; `503` se o banco estiver fora.

## Variáveis de ambiente

Veja `app/.env.example`. Nada de segredo vai para o git.

| Variável | Obrigatória | Padrão | Descrição |
|---|---|---|---|
| `DATABASE_URL` | sim | — | DSN do banco `pirometros`, no formato `postgresql+psycopg://usuario:senha@host:5432/pirometros` |
| `PORT` | não | `8000` | porta HTTP |
| `LOG_LEVEL` | não | `INFO` | `DEBUG`, `INFO`, `WARNING` ou `ERROR` |
| `RUN_MIGRATIONS_ON_START` | não | `true` | aplica as migrations do schema `app` ao subir (idempotente) |

### Usuário do banco (recomendado)

Crie um papel dedicado, que só leia `receiver_data` e só escreva no schema `app`:

```sql
CREATE ROLE pirometros_api LOGIN PASSWORD '<senha>';
GRANT CONNECT, CREATE ON DATABASE pirometros TO pirometros_api;  -- CREATE: criar o schema app
GRANT USAGE ON SCHEMA public TO pirometros_api;
GRANT SELECT ON public.receiver_data TO pirometros_api;
```

## Deploy no Easypanel

O código, o `Dockerfile` e o compose ficam dentro de `app/`. Crie um **App** no Easypanel:

1. **Fonte**: GitHub, repositório `Rei-Auto-Parts/pirometros-api`, branch `main`.
2. **Build**: tipo *Dockerfile*, **caminho de build** `/app` (a pasta `app/` do repositório) e
   arquivo `Dockerfile`. O Dockerfile tem duas stages: `dev` (só desenvolvimento) e `prod`, a
   última, que o Easypanel constrói por padrão e que não leva ferramentas de teste.
3. **Ambiente**: defina `DATABASE_URL` apontando para `banco_dados_postgres:5432/pirometros`.
4. **Rede**: porta do app `8000`. Não é preciso expor domínio público: o front acessa a API
   pela rede interna, via proxy do nginx em `/api`.

Ao subir, a API aplica as migrations do schema `app`.
