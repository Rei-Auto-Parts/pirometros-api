# Tarefas — Gestão de pirômetros na API (complemento, resumo e leituras sem temperatura)

> Ordem de dependência. `[P]` marca tarefa paralelizável (não toca arquivo de outra `[P]`
> da mesma fase). Teste vem antes da implementação que ele prova.
> Todo caminho é relativo a `pirometros-api/`; comandos só por `make`, no serviço `dev`.

## Fase 1 — Domínio e interfaces

- [x] T001 [P] Criar as constantes (paleta de 12 cores, `NICKNAME_MAX_LENGTH=40`, `NOTE_MAX_LENGTH=500`, padrão `#rrggbb`) em `app/core/domain/constants/pyrometer_constants.py`
- [x] T002 [P] Criar os DTOs `PyrometerProfileDto`, `PyrometerOverviewDto` e `PyrometerSummaryDto` em `app/core/domain/dtos/pyrometer_profile_dto.py`, `app/core/domain/dtos/pyrometer_overview_dto.py` e `app/core/domain/dtos/pyrometer_summary_dto.py`
- [x] T003 [P] Teste unitário de `PyrometerNotFoundError` em `app/tests/unit/core/domain/errors/pyrometer_not_found_error_test.py`
- [x] T004 Implementar `PyrometerNotFoundError` em `app/core/domain/errors/pyrometer_not_found_error.py`
- [x] T005 Teste unitário da cor padrão (mesma cor para o mesmo serial; cores diferentes em colisão; paleta esgotada reaproveita) em `app/tests/unit/core/domain/models/default_color_model_test.py`
- [x] T006 Implementar a cor padrão em `app/core/domain/models/default_color_model.py` (depende de T001)
- [x] T007 Criar as interfaces `app/interfaces/adapters/repositories/i_pyrometer_profile_repository.py`, `app/interfaces/infra/tools/i_clock_tool.py`, `app/interfaces/core/application/i_list_pyrometer_summaries_use_case.py` e `app/interfaces/core/application/i_save_pyrometer_profile_use_case.py` (depende de T002)
- [x] T008 Alterar `app/interfaces/adapters/repositories/i_reading_repository.py` (`find_summaries`, `pyrometer_exists`) e `app/interfaces/core/application/i_list_pyrometers_use_case.py` (retorna `PyrometerOverviewDto`) (depende de T002)

## Fase 2 — Aplicação

- [x] T009 Teste unitário de `ListPyrometersUseCase` (sem complemento → padrões; com complemento; ordenado por serial; cor padrão pela ordem) em `app/tests/unit/core/application/list_pyrometers_use_case_test.py`
- [x] T010 Alterar `ListPyrometersUseCase` em `app/core/application/list_pyrometers_use_case.py` (depende de T006, T007, T008, T009)
- [x] T011 [P] Teste unitário de `ListPyrometerSummariesUseCase` (minutos pelo relógio; nunca negativo; lista vazia) em `app/tests/unit/core/application/list_pyrometer_summaries_use_case_test.py`
- [x] T012 Implementar `ListPyrometerSummariesUseCase` em `app/core/application/list_pyrometer_summaries_use_case.py` (depende de T007, T008, T011)
- [x] T013 [P] Teste unitário de `SavePyrometerProfileUseCase` (grava; vazio vira `None`; serial inexistente levanta erro e não grava) em `app/tests/unit/core/application/save_pyrometer_profile_use_case_test.py`
- [x] T014 Implementar `SavePyrometerProfileUseCase` em `app/core/application/save_pyrometer_profile_use_case.py` (depende de T004, T007, T008, T013)

## Fase 3 — Adapters e infra

- [x] T015 [P] Teste unitário do filtro de temperatura, de `find_summaries` e de `pyrometer_exists` em `app/tests/unit/adapters/repositories/reading_repository_test.py`
- [x] T016 Alterar `ReadingRepository` em `app/adapters/repositories/reading_repository.py` (`reg_temperature IS NOT NULL` em `PERIOD_FILTER`, `find_summaries`, `pyrometer_exists`) (depende de T008, T015)
- [x] T017 [P] Teste unitário de `PyrometerProfileRepository` (`find_all`, upsert) em `app/tests/unit/adapters/repositories/pyrometer_profile_repository_test.py`
- [x] T018 Implementar `PyrometerProfileRepository` em `app/adapters/repositories/pyrometer_profile_repository.py` (depende de T002, T007, T017)
- [x] T019 [P] Teste unitário de `ClockTool` (horário local sem fuso pelo fuso configurado) em `app/tests/unit/infra/tools/clock_tool_test.py`
- [x] T020 Implementar `ClockTool` em `app/infra/tools/clock_tool.py` (depende de T007, T019)
- [x] T021 [P] Teste unitário de `Settings.local_timezone` (padrão e sobrescrita) em `app/tests/unit/infra/tools/config_tool_test.py`
- [x] T022 Alterar `Settings` em `app/infra/tools/config_tool.py` e acrescentar `LOCAL_TIMEZONE` em `app/.env.example` (depende de T021)
- [x] T023 Criar a migration `app/infra/migrations/versions/0002_create_pyrometer_profile.py` (tabela `app.pyrometer_profile`: serial chave primária, apelido, cor, observação, ativo, atualizado em) — sem teste unitário (`infra/migrations/` fora da cobertura); provada em T029
- [x] T024 Teste unitário de `PyrometersController` (resposta estendida; `GET /pyrometers/summary`; `PUT` ok, 404 serial inexistente, 422 cor/apelido/observação inválidos) em `app/tests/unit/adapters/controllers/pyrometers_controller_test.py` (depende de T007, T008)
- [x] T025 Alterar `PyrometersController` em `app/adapters/controllers/pyrometers_controller.py` e a assinatura em `app/infra/api/api_router.py` se necessário (depende de T001, T004, T024)
- [x] T026 Ligar os novos itens (repositório de complemento, relógio, casos de uso, controller) em `app/infra/init/ioc_init.py` (depende de T010, T012, T014, T016, T018, T020, T022, T025)

## Fase 4 — Integração e BDD

- [x] T027 Alterar `app/tests/support/receiver_data_fixture.py` (`insert_reading` aceita temperatura nula; função que limpa `app.pyrometer_profile`) e `app/tests/support/api_client.py` (liga os novos itens com relógio fixo) (depende de T026)
- [x] T028 [P] Teste de integração do repositório de complemento (upsert não duplica; sobrevive a nova conexão) em `app/tests/it/adapters/repositories/pyrometer_profile_repository_test_integration.py`
- [x] T029 [P] Alterar o teste de integração das migrations para exigir a tabela `app.pyrometer_profile` em `app/tests/it/infra/init/migration_init_test_integration.py`
- [x] T030 [P] Alterar o teste de integração do `ReadingRepository` (sem temperatura em lista, total e série; resumo da leitura mais recente com temperatura; existência) em `app/tests/it/adapters/repositories/reading_repository_test_integration.py`
- [x] T031 [P] Criar o teste de integração de `/pyrometers`, `/pyrometers/summary` e `PUT /pyrometers/{id}` (inclui desempenho ≤ 500 ms com 100.000 leituras e 10 pirômetros, RNF-01/02) em `app/tests/it/infra/api/pyrometers_api_test_integration.py`
- [x] T032 [P] Alterar o teste de integração de `/readings` e `/readings/series` (sem temperatura) em `app/tests/it/infra/api/readings_api_test_integration.py`
- [x] T033 Alterar `app/tests/bdd/environment.py` para limpar o complemento a cada cenário
- [x] T034 Criar `app/tests/bdd/gestao_de_pirometros.feature` (`# language: pt`) e `app/tests/bdd/steps/gestao_de_pirometros_steps.py`, com um cenário por critério de aceite da spec, nas tarefas T035 a T048 (mesmos arquivos: não paralelizar)
- [x] T035 Cenário `Pirômetro sem complemento` em `app/tests/bdd/gestao_de_pirometros.feature`
- [x] T036 Cenário `Gravar complemento` em `app/tests/bdd/gestao_de_pirometros.feature`
- [x] T037 Cenário `Regravar substitui` em `app/tests/bdd/gestao_de_pirometros.feature`
- [x] T038 Cenário `Inativar pirômetro` em `app/tests/bdd/gestao_de_pirometros.feature`
- [x] T039 Cenário `Serial inexistente` em `app/tests/bdd/gestao_de_pirometros.feature`
- [x] T040 Cenário `Cor inválida` em `app/tests/bdd/gestao_de_pirometros.feature`
- [x] T041 Cenário `Apelido acima do máximo` em `app/tests/bdd/gestao_de_pirometros.feature`
- [x] T042 Cenário `Cor padrão estável` em `app/tests/bdd/gestao_de_pirometros.feature`
- [x] T043 Cenário `Resumo por pirômetro` em `app/tests/bdd/gestao_de_pirometros.feature`
- [x] T044 Cenário `Resumo ignora leitura sem temperatura` em `app/tests/bdd/gestao_de_pirometros.feature`
- [x] T045 Cenário `Leituras sem temperatura fora da lista` em `app/tests/bdd/gestao_de_pirometros.feature`
- [x] T046 Cenário `Leituras sem temperatura fora da série` em `app/tests/bdd/gestao_de_pirometros.feature`
- [x] T047 Cenário `Complemento sobrevive a novas leituras` em `app/tests/bdd/gestao_de_pirometros.feature`
- [x] T048 Cenário `Dado gravado não é alterado` em `app/tests/bdd/gestao_de_pirometros.feature`
- [x] T049 `make validate` verde (fmt → lint → test → cover ≥ 90% → it → bdd)

## Rastreabilidade

| Requisito | Tarefas |
|---|---|
| RF-01 | T002, T008, T009, T010, T018, T024, T025, T031, T035 |
| RF-02 | T004, T013, T014, T016, T018, T023, T024, T025, T028, T031, T036, T037, T038, T039 |
| RF-03 | T001, T024, T025, T040, T041 |
| RF-04 | T001, T005, T006, T009, T010, T042 |
| RF-05 | T002, T011, T012, T016, T019, T020, T024, T025, T030, T043, T044 |
| RF-06 | T015, T016, T030, T032, T045, T046 |
| RF-07 | T018, T031, T048 |
| RF-08 | T023, T028, T029, T047 |
| RNF-01 | T016, T031 |
| RNF-02 | T010, T018, T031 |
| RNF-03 | T019, T020, T024, T025 |
| RNF-04 | T049 |
| RNF-05 | T018, T048 |

## Emenda 2026-11-05 — cor única entre pirômetros (RF-09)

- [x] T050 Teste unitário de `ColorInUseError` em `app/tests/unit/core/domain/errors/color_in_use_error_test.py` e implementação em `app/core/domain/errors/color_in_use_error.py`
- [x] T051 Teste unitário e implementação do modelo compartilhado `build_overviews` (cor padrão nunca repete cor escolhida) em `app/tests/unit/core/domain/models/pyrometer_overview_model_test.py` e `app/core/domain/models/pyrometer_overview_model.py`; `default_color_model.py` aceita cores reservadas
- [x] T052 Alterar `ListPyrometersUseCase` e `SavePyrometerProfileUseCase` (recusa cor de outro pirômetro, comparação sem diferenciar maiúsculas) com testes em `app/tests/unit/core/application/`
- [x] T053 Controller responde 409 (`app/adapters/controllers/pyrometers_controller.py`) com teste unitário e IT em `app/tests/it/infra/api/pyrometers_api_test_integration.py`
- [x] T054 Cenários BDD "Cor já em uso por outro pirômetro", "Cor padrão de outro pirômetro também conta como em uso" e "Regravar a própria cor" em `app/tests/bdd/gestao_de_pirometros.feature`
- [x] T055 `make validate` verde

## Convergence

> Seção **append-only**, escrita por `/bu:converge`. Cada rodada acrescenta um bloco;
> nada é reescrito.

### Rodada 1 — 2026-11-05

| Requisito | Estado | Evidência |
|---|---|---|
| RF-01 | realizado | `app/core/application/list_pyrometers_use_case.py:24` junta dados + complementos; `app/adapters/controllers/pyrometers_controller.py` `GET /pyrometers`; BDD "Pirômetro sem complemento" |
| RF-02 | realizado | `save_pyrometer_profile_use_case.py:31` (404 sem gravar); upsert em `pyrometer_profile_repository.py:14`; BDD "Gravar", "Regravar", "Inativar", "Serial inexistente" |
| RF-03 | realizado | `pyrometers_controller.py:35-37` (40, `#rrggbb`, 500); BDD "Cor inválida", "Apelido acima do máximo" |
| RF-04 | realizado | `app/core/domain/models/default_color_model.py:9` (hash + sondagem); `default_color_model_test.py`; BDD "Cor padrão estável" |
| RF-05 | realizado | `reading_repository.py:72` `find_summaries`; `list_pyrometer_summaries_use_case.py`; `clock_tool.py:13`; BDD "Resumo por pirômetro", "Resumo ignora leitura sem temperatura" |
| RF-06 | realizado | `reading_repository.py:17` `PERIOD_FILTER` com `reg_temperature IS NOT NULL`; IT e BDD "Leituras sem temperatura fora da lista/série"; no banco de dev o total caiu de 34.560 para 33.491 |
| RF-07 | realizado | repositório de complemento sem SQL sobre `receiver_data` (teste unitário confere); BDD "Dado gravado não é alterado" |
| RF-08 | realizado | migration `0002_create_pyrometer_profile.py:19`; IT "keep the profile when the app is recreated" e BDD "Complemento sobrevive a novas leituras" |
| RNF-01 / RNF-02 | realizado | `pyrometers_api_test_integration.py:139` mede ≤ 0,5 s com 100.000 leituras e 10 pirômetros |
| RNF-03 | realizado | `measured_at` sem offset nos testes do controller e do IT do resumo |
| RNF-04 | realizado | cobertura total 100% (mínimo 90%) |
| RNF-05 | realizado | IT e BDD comparam `receiver_data` antes e depois |

**`make validate` (saída real):** `fmt` e `lint` verdes (ruff e mypy sem erros); 111 testes unitários passaram; cobertura "aprovada: 100.00% (mínimo 90.00%)"; 41 testes de integração passaram; BDD: 3 features, 26 cenários e 96 passos passaram, 0 falhas.

**Cenários BDD:** 14 de 14 critérios da spec têm cenário em `app/tests/bdd/gestao_de_pirometros.feature`; todos passam.

**Excesso de escopo:** nenhum. Coluna `updated_at` na tabela está no plano. Dois ajustes em testes antigos (passo BDD "recebo os dois, cada um com serial e nome" e o IT de `/pyrometers`) passaram a conferir serial e nome em vez do JSON exato, porque a resposta ganhou campos (RF-01).

**Desvios registrados:**
1. Spec: os cenários "Cor inválida" e "Resumo ignora leitura sem temperatura" ganharam um `Dado` para ficarem executáveis (a spec já foi ajustada).
2. A cor padrão pode mudar para um pirômetro que colida com um novo de serial menor (risco já registrado no plano; só afeta quem não escolheu cor).
3. Pirômetro sem nenhuma leitura com temperatura não aparece no resumo (decisão do plano).

Veredito: convergido
Tarefas acrescentadas: nenhuma

### Rodada 2 — 2026-11-05 (emenda: cor única, RF-09)

| Requisito | Estado | Evidência |
|---|---|---|
| RF-09 | realizado | `save_pyrometer_profile_use_case.py` `_ensure_color_is_free`; `ColorInUseError` → 409 em `pyrometers_controller.py`; BDD: 3 cenários novos; IT `...already_has_the_color` |
| RF-04 (estendido) | realizado | `pyrometer_overview_model.py`: cor padrão só para quem não escolheu, sem repetir cor escolhida; `pyrometer_overview_model_test.py` |

**`make validate` (saída real):** ruff e mypy sem erros; 123 testes unitários passaram; cobertura "aprovada: 100.00% (mínimo 90.00%)"; 42 de integração passaram; BDD: 3 features, 29 cenários e 106 passos passaram.

**Desvio/risco:** quando alguém escolhe cor, deixa de consumir vaga de cor padrão; num caso raro de colisão de hash, a cor padrão de outro pirômetro pode mudar. Dois salvamentos simultâneos da mesma cor por pessoas diferentes não são serializados (sem login e sem histórico, fora de escopo).

Veredito: convergido
Tarefas acrescentadas: T050 a T055 (emenda)
