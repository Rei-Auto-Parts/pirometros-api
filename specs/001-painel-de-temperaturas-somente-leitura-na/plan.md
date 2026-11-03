# Plano de implementação — Painel de temperaturas (API, somente leitura)

> Descreve **como**. Deriva da spec e da constituição; não introduz requisito novo.

## Decisões técnicas

| Decisão | Escolha | Alternativas descartadas | Por quê |
|---|---|---|---|
| Como ler | `SELECT` com colunas explícitas em `public.receiver_data`, filtrado por `reg_date` no período e por `dev_id`, ordenado por `reg_date` desc (desempate `id` desc), com `LIMIT/OFFSET` | Ler tudo e filtrar em memória | A consulta é sempre por período e usa o índice de data |
| Série | Mesma consulta, sem paginação, ordenada por `reg_date` asc, agrupada por pirômetro no caso de uso | Agregar por intervalo | Spec pede todos os pontos |
| Lista de pirômetros | Um por `dev_id`, com o nome da leitura de maior `reg_date` | Tabela própria no schema `app` | Nada novo no banco; o índice `(dev_id, reg_date)` cobre |
| Paginação | `page` (≥ 1) e `page_size` (1 a 500, padrão 50); resposta com `items`, `total`, `page`, `page_size` | Cursor | Volume pequeno; KISS |
| Filtro por pirômetro | `dev_id` (serial), repetível | `dev_name` | O briefing manda usar o serial |
| Período da série | Máximo de 31 dias; excedido lança `PeriodTooLongError`, o controller responde 422 | Validar só no controller | É regra de negócio; o controller só traduz |
| Datas | `datetime` sem fuso de ponta a ponta; JSON sem offset | — | P3 |
| Nome do receptor | `gtw_name` devolvido com `trim` | Devolver com o espaço | O briefing manda aplicar trim |
| Tabela nos testes `it`/`bdd` | Fixture em `app/tests/support/` cria `public.receiver_data` só no Postgres descartável do compose | Mockar o banco (P6 proíbe); migration (P1 proíbe) | Confirmado pelo usuário |

## Padrões de projeto aplicados

| Padrão | Onde | Problema que resolve | Custo aceito |
|---|---|---|---|
| Repository | `ReadingRepository` | Isolar o acesso à tabela atrás de uma interface | Uma interface a mais |
| Injeção de dependência (construtor) | casos de uso e controllers | Mockar tudo nos unit | Montagem em `ioc_init` |
| **Recusado**: cache ou Decorator no repositório | `ReadingRepository` | Sem medição que prove necessidade | — |

## Arquivos a criar ou alterar

Todos sob `app/`. Teste espelhado em `app/tests/unit/<mesmo caminho>_test.py`.

| Camada | Arquivo | Ação | Teste espelhado |
|---|---|---|---|
| core/domain | `core/domain/constants/reading_constants.py` (página 50/500, período máx. 31 dias) | criar | — |
| core/domain | `core/domain/errors/period_too_long_error.py` | criar | — |
| core/domain | `core/domain/dtos/reading_dto.py` | criar | — |
| core/domain | `core/domain/dtos/readings_page_dto.py` | criar | — |
| core/domain | `core/domain/dtos/pyrometer_series_dto.py` | criar | — |
| core/domain | `core/domain/dtos/pyrometer_dto.py` | criar | — |
| core/application | `core/application/list_readings_use_case.py` | criar | `tests/unit/core/application/list_readings_use_case_test.py` |
| core/application | `core/application/get_readings_series_use_case.py` | criar | `tests/unit/core/application/get_readings_series_use_case_test.py` |
| core/application | `core/application/list_pyrometers_use_case.py` | criar | `tests/unit/core/application/list_pyrometers_use_case_test.py` |
| interfaces | `interfaces/core/application/i_list_readings_use_case.py` | criar | — |
| interfaces | `interfaces/core/application/i_get_readings_series_use_case.py` | criar | — |
| interfaces | `interfaces/core/application/i_list_pyrometers_use_case.py` | criar | — |
| interfaces | `interfaces/adapters/repositories/i_reading_repository.py` | criar | — |
| adapters | `adapters/repositories/reading_repository.py` | criar | `tests/unit/adapters/repositories/reading_repository_test.py` |
| adapters | `adapters/controllers/readings_controller.py` (`GET /api/readings`, `GET /api/readings/series`) | criar | `tests/unit/adapters/controllers/readings_controller_test.py` |
| adapters | `adapters/controllers/pyrometers_controller.py` (`GET /api/pyrometers`) | criar | `tests/unit/adapters/controllers/pyrometers_controller_test.py` |
| infra | `infra/api/api_router.py` (recebe os 2 controllers novos) | alterar | `tests/unit/infra/api/api_router_test.py` |
| infra | `infra/init/ioc_init.py` (monta repositório, casos de uso, controllers) | alterar | — (fora da cobertura) |
| tests (apoio) | `tests/support/receiver_data_fixture.py` | criar | — |
| tests it | `tests/it/adapters/repositories/reading_repository_test_integration.py` | criar | — |
| tests it | `tests/it/infra/api/readings_api_test_integration.py` | criar | — |
| tests bdd | `tests/bdd/painel_de_temperaturas.feature` (os 10 cenários da spec) | criar | — |
| tests bdd | `tests/bdd/steps/painel_de_temperaturas_steps.py` | criar | — |
| docs | `README.md` (endpoints) | alterar | — |
| infra | `infra/api/api_server.py` (handler que traduz erro do banco em 503, em um só lugar) | alterar | `tests/unit/infra/api/api_server_test.py` |
| tests (apoio) | `tests/support/api_client.py`, `tests/it/conftest.py`, `tests/bdd/environment.py` | criar | — |

Cobertura dos requisitos: RF-01/02 `list_readings`; RF-03 `get_readings_series`; RF-04
`list_pyrometers`; RF-05 repositório só com `SELECT` (o teste `it` confere que a tabela fica
idêntica); RNF-02 serialização sem offset nos controllers.

## Contrato entre camadas

```
HTTP -> Controller (valida parâmetros, traduz erro de domínio em 422, serializa)
     -> UseCase (orquestra) -> IReadingRepository (SELECT)
```

- O repositório devolve DTOs com os valores como estão gravados (só `gtw_name` com `trim`).
- `core` não importa `adapters` nem `infra`: depende só de `interfaces`.
- Erro: `PeriodTooLongError` sobe do caso de uso da série e vira 422; parâmetro inválido
  (`page_size` > 500) é 422 do framework; banco fora do ar vira 503 genérico, sem expor DSN.
- Datas saem no JSON sem offset (`2026-10-29T11:00:30`).

## Dependências externas

| Dependência | Versão | Justificativa | Simulada nos testes por |
|---|---|---|---|
| PostgreSQL | 16 (compose) | única dependência | Postgres descartável do compose (P6), com a fixture da tabela |

Nenhuma biblioteca nova.

## Impacto no contrato de operação

Nenhum alvo novo no `Makefile`, nenhum serviço novo no compose, nenhuma variável de ambiente nova.

## Riscos

| Risco | Probabilidade | Mitigação |
|---|---|---|
| Fixture cria a tabela no banco de teste e parece violar P1 | baixa | Fica só em `tests/support` e aborta se `DATABASE_URL` não apontar para o `postgres` do compose; nenhuma migration nem script de produção a cria. Aceito pelo usuário |
| Desempenho com o crescimento da tabela | baixa | Consulta sempre por período usa o índice de `reg_date` |

## Conformidade com a constituição

| Princípio | Como este plano o respeita |
|---|---|
| Contrato de operação | Tudo roda por `make`; sem alvo, serviço ou variável novos |
| Arquitetura limpa | Controllers e repositório em `adapters`, regra em `core`, abstrações em `interfaces`; `core` só depende de `interfaces` |
| Testes provam a entrega | Todo arquivo de produção tem unit espelhado; `it` e `bdd` contra Postgres real; os 10 cenários da spec viram BDD; cobertura ≥ 90% |
| Simplicidade defensável | Só `SELECT`, sem regra de tratamento, sem cache |
| P1 `receiver_data` somente leitura | Só `SELECT` com colunas explícitas; Alembic continua versionando só `app` |
| P2 Só o banco `pirometros` | Reaproveita o engine existente |
| P3 Sem conversão de fuso | `reg_date` trafega como veio, sem fuso e sem relógio local |
| P4 Sem autenticação | Nenhuma rota protegida |
| P5 Sem segredos versionados | Nenhuma variável nova |
| P6 Integração contra Postgres real | `it` e `bdd` usam o Postgres do compose, sem mock de conexão |
