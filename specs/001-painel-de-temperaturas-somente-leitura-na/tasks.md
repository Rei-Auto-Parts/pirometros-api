# Tarefas — Painel de temperaturas (API, somente leitura)

> Ordem de dependência. `[P]` marca tarefa paralelizável (não toca arquivo de outra `[P]`
> da mesma fase). Teste vem antes da implementação que ele prova.
> DTOs, constantes, erros e interfaces não têm comportamento próprio e não levam teste
> unitário (conforme o plano); são exercitados pelos testes dos casos de uso e do repositório.

## Fase 1 — Domínio e interfaces

- [x] T001 [P] Criar constantes de página (padrão 50, máximo 500) e período máximo da série (31 dias) em `app/core/domain/constants/reading_constants.py`
- [x] T002 [P] Criar `PeriodTooLongError` em `app/core/domain/errors/period_too_long_error.py`
- [x] T003 [P] Criar `ReadingDto` (todos os dados da medição, sem `synced_at`) em `app/core/domain/dtos/reading_dto.py`
- [x] T004 [P] Criar `ReadingsPageDto` (`items`, `total`, `page`, `page_size`) em `app/core/domain/dtos/readings_page_dto.py`
- [x] T005 [P] Criar `PyrometerSeriesDto` em `app/core/domain/dtos/pyrometer_series_dto.py`
- [x] T006 [P] Criar `PyrometerDto` (serial e nome) em `app/core/domain/dtos/pyrometer_dto.py`
- [x] T007 [P] Criar `IReadingRepository` em `app/interfaces/adapters/repositories/i_reading_repository.py`
- [x] T008 [P] Criar `IListReadingsUseCase` em `app/interfaces/core/application/i_list_readings_use_case.py`
- [x] T009 [P] Criar `IGetReadingsSeriesUseCase` em `app/interfaces/core/application/i_get_readings_series_use_case.py`
- [x] T010 [P] Criar `IListPyrometersUseCase` em `app/interfaces/core/application/i_list_pyrometers_use_case.py`

## Fase 2 — Aplicação

- [x] T011 [P] Teste unitário de `ListReadingsUseCase` em `app/tests/unit/core/application/list_readings_use_case_test.py`
- [x] T012 [P] Implementar `ListReadingsUseCase` em `app/core/application/list_readings_use_case.py`
- [x] T013 [P] Teste unitário de `GetReadingsSeriesUseCase` (inclui período acima de 31 dias) em `app/tests/unit/core/application/get_readings_series_use_case_test.py`
- [x] T014 [P] Implementar `GetReadingsSeriesUseCase` em `app/core/application/get_readings_series_use_case.py`
- [x] T015 [P] Teste unitário de `ListPyrometersUseCase` em `app/tests/unit/core/application/list_pyrometers_use_case_test.py`
- [x] T016 [P] Implementar `ListPyrometersUseCase` em `app/core/application/list_pyrometers_use_case.py`

## Fase 3 — Adapters e infra

- [x] T017 [P] Teste unitário de `ReadingRepository` em `app/tests/unit/adapters/repositories/reading_repository_test.py`
- [x] T018 [P] Implementar `ReadingRepository` (só `SELECT`, colunas explícitas, `trim` no receptor, ordem por `reg_date` desc e `id` desc) em `app/adapters/repositories/reading_repository.py`
- [x] T019 [P] Teste unitário de `ReadingsController` (422 para período longo, 503 com banco fora, datas sem offset) em `app/tests/unit/adapters/controllers/readings_controller_test.py`
- [x] T020 [P] Implementar `ReadingsController` (`GET /api/readings` e `GET /api/readings/series`) em `app/adapters/controllers/readings_controller.py`
- [x] T021 [P] Teste unitário de `PyrometersController` em `app/tests/unit/adapters/controllers/pyrometers_controller_test.py`
- [x] T022 [P] Implementar `PyrometersController` (`GET /api/pyrometers`) em `app/adapters/controllers/pyrometers_controller.py`
- [x] T023 Teste unitário de `build_api_router` com os controllers novos em `app/tests/unit/infra/api/api_router_test.py`
- [x] T024 Alterar `build_api_router` para receber os dois controllers novos em `app/infra/api/api_router.py`
- [x] T025 Montar repositório, casos de uso e controllers em `app/infra/init/ioc_init.py`
- [x] T026 [P] Documentar os endpoints em `README.md`

## Fase 4 — Integração e BDD

- [x] T027 Criar a fixture que cria `public.receiver_data` só no Postgres do compose, abortando se o host não for o `postgres` do compose, em `app/tests/support/receiver_data_fixture.py`
- [x] T028 [P] Teste de integração de `ReadingRepository` (filtros, ordem, paginação, tabela intacta) em `app/tests/it/adapters/repositories/reading_repository_test_integration.py`
- [x] T029 [P] Teste de integração das rotas em `app/tests/it/infra/api/readings_api_test_integration.py`
- [x] T030 Cenário `Listar leituras da mais recente para a mais antiga` em `app/tests/bdd/painel_de_temperaturas.feature` (DADO/QUANDO/ENTÃO)
- [x] T031 Cenário `Leitura que chegou atrasada fica na ordem da data` em `app/tests/bdd/painel_de_temperaturas.feature`
- [x] T032 Cenário `Filtrar leituras por pirômetro` em `app/tests/bdd/painel_de_temperaturas.feature`
- [x] T033 Cenário `Período limita as leituras` em `app/tests/bdd/painel_de_temperaturas.feature`
- [x] T034 Cenário `Paginação respeita o limite` em `app/tests/bdd/painel_de_temperaturas.feature`
- [x] T035 Cenário `Datas sem fuso` em `app/tests/bdd/painel_de_temperaturas.feature`
- [x] T036 Cenário `Série por pirômetro` em `app/tests/bdd/painel_de_temperaturas.feature`
- [x] T037 Cenário `Período da série acima do máximo` em `app/tests/bdd/painel_de_temperaturas.feature`
- [x] T038 Cenário `Listar pirômetros` em `app/tests/bdd/painel_de_temperaturas.feature`
- [x] T039 Cenário `Dado gravado não é alterado` em `app/tests/bdd/painel_de_temperaturas.feature`
- [x] T040 Implementar os passos de todos os cenários em `app/tests/bdd/steps/painel_de_temperaturas_steps.py`
- [x] T041 `make validate` verde

## Rastreabilidade

| Requisito | Tarefas |
|---|---|
| RF-01 | T001, T003, T004, T007, T008, T011, T012, T017, T018, T019, T020, T028, T029, T030, T031, T032, T033, T034 |
| RF-02 | T003, T017, T018, T028, T030 |
| RF-03 | T001, T002, T005, T009, T013, T014, T019, T020, T029, T036, T037 |
| RF-04 | T006, T010, T015, T016, T021, T022, T029, T038 |
| RF-05 | T018, T028, T039 |
| RNF-01 | T018, T028 (consulta por período com índice de data; p95 conferido em T028 com 10.000 leituras) |
| RNF-02 | T019, T029, T035 |
| RNF-03 | T018, T028, T039 |
| RNF-04 | T041 (`make cover` dentro do `make validate`, mínimo 90%) |

## Convergence

> Seção **append-only**, escrita por `/bu:converge`. Cada rodada acrescenta um bloco;
> nada é reescrito.

### Rodada 1 — 2026-11-03
| Requisito | Estado | Evidência |
|---|---|---|
| RF-01 | realizado | `adapters/repositories/reading_repository.py` (`ORDER BY reg_date DESC, id DESC`, `LIMIT/OFFSET`, filtro `dev_id`); `core/application/list_readings_use_case.py`; `GET /api/readings`; BDD "Listar leituras…", "Leitura que chegou atrasada…", "Filtrar…", "Período limita…", "Paginação…" |
| RF-02 | realizado | `ReadingDto` com os 14 campos gravados (sem `synced_at`); BDD "cada leitura traz todos os dados" |
| RF-03 | realizado | `get_readings_series_use_case.py` (agrupa por pirômetro, `PeriodTooLongError` > 31 dias → 422); BDD "Série por pirômetro" e "Período da série acima do máximo" |
| RF-04 | realizado | `list_pyrometers_use_case.py`, `GET /api/pyrometers`; BDD "Listar pirômetros" |
| RF-05 | realizado | Busca por `INSERT/UPDATE/DELETE/ALTER/DROP/TRUNCATE` em `adapters/`, `core/`, `infra/` sem ocorrência; datas `NaiveDatetime`, offset rejeitado com 422; BDD "Datas sem fuso" e "Dado gravado não é alterado" |
| RNF-01 | realizado | teste it com 10.000 leituras < 0,5 s (execução única, não p95) |
| RNF-02 | realizado | testes unit/it e cenário "Datas sem fuso" |
| RNF-03 | realizado | repositório só com `SELECT`; teste it compara a tabela antes e depois |
| RNF-04 | realizado | cobertura 100% (mínimo 90%) |

`make validate`: fmt/lint/mypy limpos (58 arquivos); 64 unit passed; cobertura TOTAL 100%; 22 it passed; BDD 2 features, 12 cenários, 49 passos passed, 0 failed.
Cenários BDD: os 10 critérios de aceite têm cenário e todos passam.
Excesso de escopo: nenhum funcional. Itens fora do plano original, já registrados nele: handler 503 em `infra/api/api_server.py`, `tests/support/api_client.py`, `tests/it/conftest.py`, `tests/bdd/environment.py`. Nada de turno, saúde, correção de data, autenticação ou escrita.
Desvio de processo registrado: teste do repositório escrito junto com a implementação (sem red-first); Fase 1 sem subagentes.
Veredito: convergido
Tarefas acrescentadas: nenhuma
