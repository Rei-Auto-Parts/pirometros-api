# pirometros-api

> Identidade e princípios **deste** projeto. Este arquivo **é versionado** — é o que o time
> compartilha. Os princípios da organização ficam em `.specify/memory/constitution.md`, que o
> `/bu:constitution` gera a cada clone e o `.gitignore` mantém fora do git.

## Identidade

- **Projeto**: pirometros-api
- **Tipo**: api
- **Stack**: Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2 (pydantic-settings), psycopg 3, PostgreSQL
- **Domínio**: API interna da fundição que lê as leituras dos pirômetros de imersão e as transforma em informação e histórico para os gestores (não é tempo real para a produção).
- **Cobertura mínima acordada**: 90%

## Contexto

- O software do fabricante grava as leituras num SQL Server local. Um **sincronizador** (outro repositório, em produção) as copia a cada 5 minutos para o Postgres, banco `pirometros`, tabela `public.receiver_data`.
- Deploy: VPS Linux interna com Easypanel; o app é construído a partir do `Dockerfile` de `app/`. Postgres no Easypanel, host interno `banco_dados_postgres`, porta `5432`.
- Todas as rotas ficam sob `/api`; a documentação OpenAPI fica em `/api/docs`.

## Princípios específicos deste projeto

> Cada princípio declara o que **proíbe**.

### Princípio 1 — `public.receiver_data` é somente leitura

A tabela `public.receiver_data` é escrita **exclusivamente** pelo sincronizador. A API só a **lê**.
**Proíbe**: criar, alterar, apagar, migrar ou escrever nessa tabela, por código, migration ou
script. O Alembic versiona apenas o schema `app` e ignora explicitamente qualquer objeto fora dele
(`include_object` em `infra/migrations/env.py`). As tabelas próprias da API moram no schema `app`
do banco `pirometros`.

### Princípio 2 — Só o banco `pirometros`

O Postgres de produção hospeda **outros bancos em produção**. **Proíbe**: conectar, consultar ou
alterar qualquer banco que não seja `pirometros`. Desenvolvimento e testes usam um Postgres
descartável do compose, nunca o de produção.

### Princípio 3 — Horário local, sem conversão de fuso

`reg_date` é `timestamp` **sem fuso**, em horário local (America/Sao_Paulo). **Proíbe**: converter
fuso (`AT TIME ZONE`, `astimezone`, `pytz`, `zoneinfo` aplicado a `reg_date`) ou serializar
`reg_date` com offset. O valor segue como veio do banco.

### Princípio 4 — Sem autenticação por enquanto

A VPS é interna e só a rede da empresa acessa. **Proíbe**: implementar login, usuários, perfis,
tokens ou qualquer controle de acesso na API até que uma spec o peça.

### Princípio 5 — Sem segredos versionados

Configuração por variáveis de ambiente (pydantic-settings). **Proíbe**: commitar `.env`, senha,
DSN com credencial ou qualquer segredo; o `.env.example` traz apenas placeholders.

### Princípio 6 — Integração contra Postgres real

A constituição da organização pede integração contra dependências simuladas (WireMock). Esta API
não tem dependência HTTP externa: sua única dependência é o Postgres, que o WireMock não simula.
Os testes `it` e `bdd` rodam contra um **Postgres descartável** no compose (schema `app` e
migrations de verdade). **Proíbe**: mockar a conexão com o banco nos testes `it` e `bdd`.

## Emendas

| Versão | Data | O que mudou |
|---|---|---|
| 1.0.0 | 2026-10-30 | ratificação inicial |
