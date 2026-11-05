# Plano de implementação — Gestão de pirômetros na API (complemento, resumo e leituras sem temperatura)

> Descreve **como**. Deriva da spec e da constituição; não introduz requisito novo.

## Decisões técnicas

| Decisão | Escolha | Alternativas descartadas | Por quê |
|---|---|---|---|
| Onde guardar o complemento | Tabela própria no schema `app` (migration `0002`), chave primária = serial do pirômetro | Escrever em `public.receiver_data` (proibido, P1); arquivo/JSON | RF-02, RF-07, RF-08; o schema `app` já é o lugar das tabelas da API |
| Acesso ao banco | SQL explícito via `text()` do SQLAlchemy Core, como o `ReadingRepository` | ORM/modelos declarativos | Mantém o padrão do projeto (KISS) e o `target_metadata` do Alembic continua `None` |
| Gravação | Upsert numa única instrução (`INSERT ... ON CONFLICT (serial) DO UPDATE`) | Ler e depois inserir/atualizar | RF-02: "a primeira cria, as seguintes substituem", sem duplicar e sem corrida |
| Pirômetro existe? | Consulta `EXISTS` em `receiver_data` pelo serial, feita no `ReadingRepository` | Carregar toda a lista e procurar | RF-02: serial inexistente é recusado sem gravar nada |
| Lista de pirômetros | Caso de uso junta `find_pyrometers()` (dados) com os complementos e aplica os padrões | JOIN entre `public.receiver_data` e `app` no SQL | Regra de padrão (apelido vazio, cor padrão, ativo) é regra de negócio: mora em `core`, não no SQL |
| Cor padrão | Paleta fixa de 12 cores em constante de domínio; cor = `paleta[crc32(serial) % 12]`, e, se já usada por um pirômetro anterior (em ordem de serial), avança para a próxima livre | Índice pela posição na lista | RF-04. A posição na lista mudaria as cores quando surge um pirômetro novo; o hash fixa a cor no serial e a sondagem só atua em colisão |
| Validação de apelido, observação e cor | Limites como constantes de domínio (40, 500, `#rrggbb`) e validação nos modelos Pydantic de entrada do controller (erro 422) | Validar também no caso de uso | RF-03. Fronteira do sistema é o controller; o caso de uso recebe dado já válido (KISS) |
| Campo vazio | Apelido/observação vazios ou só espaços viram `NULL`; cor `null` volta à cor padrão | Guardar string vazia | RF-01, RF-02: "sem apelido" tem uma só representação |
| Resumo por pirômetro | Uma consulta `DISTINCT ON (dev_id)` da leitura mais recente **com temperatura**, ordenada por `reg_date DESC, id DESC` | Uma consulta por pirômetro | RF-05, RNF-01; o índice `(dev_id, reg_date)` atende |
| "Agora" do tempo sem leitura | Relógio injetável (`IClockTool`) que devolve o horário local **sem fuso**, calculado com o fuso configurado em `LOCAL_TIMEZONE` (padrão `America/Sao_Paulo`) | `datetime.now()` direto; `now()` do Postgres | O container roda em UTC; o relógio injetável também deixa o teste determinístico. O fuso é aplicado só ao "agora", nunca a `reg_date` (P3) |
| Minutos sem leitura | Inteiro, `floor((agora − measured_at) / 60 s)`, nunca negativo | Segundos; formatação em horas | RF-05 pede minutos; formatar "10 h" é do front |
| Leitura sem temperatura | `reg_temperature IS NOT NULL` entra em `PERIOD_FILTER`, valendo para `find_readings`, `count_readings` e `find_series` | Filtrar depois, na camada de aplicação | RF-06: total e paginação só contam com o filtro no SQL |
| Resumo e pirômetro sem leitura com temperatura | O pirômetro fica **fora** do resumo | Devolver item com campos nulos | RF-05 fala da "leitura mais recente com temperatura"; sem ela não há o que resumir. O front trata ausência como "sem leituras" |
| Rotas | `GET /pyrometers` (estendida), `GET /pyrometers/summary`, `PUT /pyrometers/{pyrometer_id}` | Rota por campo; `POST` | `PUT` substitui o complemento inteiro (RF-02); `summary` é declarada antes da rota com parâmetro |

## Padrões de projeto aplicados

| Padrão | Onde | Problema que resolve | Custo aceito |
|---|---|---|---|
| Repository (já usado) | `PyrometerProfileRepository` | Isola o SQL do complemento do caso de uso | um arquivo e uma interface a mais |
| Injeção de dependência / Protocol (já usado) | `IClockTool`, repositórios e casos de uso | Testar com mocks gerados da interface; relógio fixo no BDD | nenhum além das interfaces já previstas |

**Considerados e recusados**

| Padrão | Motivo |
|---|---|
| Strategy para escolher a cor padrão | Há uma única regra de cor; uma função pura resolve (YAGNI) |
| Unit of Work / transação em duas tabelas | O upsert toca uma tabela só, numa instrução |
| CQRS (modelos separados de leitura e escrita) | Escala desproporcional; leitura e escrita são pequenas e vivem em casos de uso separados |
| Decorator/Proxy de cache no resumo | RNF-01 (500 ms com 100.000 leituras) não exige; medir antes de cachear |

## Arquivos a criar ou alterar

Todo caminho sob `app/`. Testes unitários espelham o caminho em `app/tests/unit/` com sufixo `_test.py`.

| Camada | Arquivo | Ação | Teste espelhado |
|---|---|---|---|
| core/domain | `app/core/domain/constants/pyrometer_constants.py` (paleta de 12 cores, `NICKNAME_MAX_LENGTH=40`, `NOTE_MAX_LENGTH=500`, padrão `#rrggbb`) | criar | coberto pelos testes dos arquivos que o usam |
| core/domain | `app/core/domain/dtos/pyrometer_profile_dto.py` (serial, apelido, cor, observação, ativo) | criar | — (dado puro) |
| core/domain | `app/core/domain/dtos/pyrometer_overview_dto.py` (serial, nome do aparelho, apelido, cor efetiva, observação, ativo) | criar | — (dado puro) |
| core/domain | `app/core/domain/dtos/pyrometer_summary_dto.py` (serial, temperatura, medida em, bateria, minutos sem leitura) | criar | — (dado puro) |
| core/domain | `app/core/domain/errors/pyrometer_not_found_error.py` | criar | `app/tests/unit/core/domain/errors/pyrometer_not_found_error_test.py` |
| core/domain | `app/core/domain/models/default_color_model.py` (função pura: cor padrão por serial, com sondagem em colisão) | criar | `app/tests/unit/core/domain/models/default_color_model_test.py` |
| core/application | `app/core/application/list_pyrometers_use_case.py` | alterar (junta dados + complementos, aplica padrões) | `app/tests/unit/core/application/list_pyrometers_use_case_test.py` |
| core/application | `app/core/application/list_pyrometer_summaries_use_case.py` | criar | `app/tests/unit/core/application/list_pyrometer_summaries_use_case_test.py` |
| core/application | `app/core/application/save_pyrometer_profile_use_case.py` | criar | `app/tests/unit/core/application/save_pyrometer_profile_use_case_test.py` |
| interfaces | `app/interfaces/core/application/i_list_pyrometers_use_case.py` | alterar (novo retorno) | — |
| interfaces | `app/interfaces/core/application/i_list_pyrometer_summaries_use_case.py` | criar | — |
| interfaces | `app/interfaces/core/application/i_save_pyrometer_profile_use_case.py` | criar | — |
| interfaces | `app/interfaces/adapters/repositories/i_pyrometer_profile_repository.py` | criar | — |
| interfaces | `app/interfaces/adapters/repositories/i_reading_repository.py` | alterar (`find_summaries`, `pyrometer_exists`) | — |
| interfaces | `app/interfaces/infra/tools/i_clock_tool.py` | criar | — |
| adapters/repositories | `app/adapters/repositories/reading_repository.py` | alterar (filtro de temperatura, `find_summaries`, `pyrometer_exists`) | `app/tests/unit/adapters/repositories/reading_repository_test.py` |
| adapters/repositories | `app/adapters/repositories/pyrometer_profile_repository.py` (`find_all`, `save` com upsert) | criar | `app/tests/unit/adapters/repositories/pyrometer_profile_repository_test.py` |
| adapters/controllers | `app/adapters/controllers/pyrometers_controller.py` (resposta estendida, `GET /pyrometers/summary`, `PUT /pyrometers/{pyrometer_id}`, 404 e 422) | alterar | `app/tests/unit/adapters/controllers/pyrometers_controller_test.py` |
| infra/tools | `app/infra/tools/clock_tool.py` (horário local sem fuso, pelo fuso configurado) | criar | `app/tests/unit/infra/tools/clock_tool_test.py` |
| infra/tools | `app/infra/tools/config_tool.py` (`local_timezone`) | alterar | `app/tests/unit/infra/tools/config_tool_test.py` |
| infra/migrations | `app/infra/migrations/versions/0002_create_pyrometer_profile.py` | criar | `app/tests/it/infra/init/migration_init_test_integration.py` (alterar) |
| infra/init | `app/infra/init/ioc_init.py` | alterar (liga os novos itens) | fora da conta (constituição) |
| tests/support | `app/tests/support/api_client.py` | alterar (liga os novos itens, relógio fixo) | — |
| tests/support | `app/tests/support/receiver_data_fixture.py` | alterar (`insert_reading` aceita temperatura nula; limpeza do complemento) | — |
| tests/it | `app/tests/it/adapters/repositories/pyrometer_profile_repository_test_integration.py` | criar | — |
| tests/it | `app/tests/it/adapters/repositories/reading_repository_test_integration.py` | alterar (sem temperatura, resumo, existência) | — |
| tests/it | `app/tests/it/infra/api/pyrometers_api_test_integration.py` | criar | — |
| tests/it | `app/tests/it/infra/api/readings_api_test_integration.py` | alterar (sem temperatura em lista, total e série) | — |
| tests/bdd | `app/tests/bdd/gestao_de_pirometros.feature` (cenários da spec, `# language: pt`) | criar | — |
| tests/bdd | `app/tests/bdd/steps/gestao_de_pirometros_steps.py` | criar | — |
| tests/bdd | `app/tests/bdd/environment.py` | alterar (limpa complementos entre cenários) | — |
| config | `app/.env.example` | alterar (`LOCAL_TIMEZONE`) | — |

## Mapa requisito → arquivos

| Requisito | Arquivos |
|---|---|
| RF-01 | `list_pyrometers_use_case.py`, `pyrometer_profile_repository.py` (`find_all`), `pyrometers_controller.py`, `default_color_model.py` |
| RF-02 | `save_pyrometer_profile_use_case.py`, `pyrometer_profile_repository.py` (`save`), `reading_repository.py` (`pyrometer_exists`), `pyrometers_controller.py`, migration `0002`, `pyrometer_not_found_error.py` |
| RF-03 | `pyrometer_constants.py`, `pyrometers_controller.py` (modelo de entrada) |
| RF-04 | `default_color_model.py`, `pyrometer_constants.py` |
| RF-05 | `list_pyrometer_summaries_use_case.py`, `reading_repository.py` (`find_summaries`), `clock_tool.py`, `pyrometers_controller.py` |
| RF-06 | `reading_repository.py` (`PERIOD_FILTER`) |
| RF-07 | `pyrometer_profile_repository.py` só escreve em `app`; teste BDD "dado gravado não é alterado" |
| RF-08 | migration `0002` + teste IT que regrava e relê pela API recriada |
| RNF-01/02 | `reading_repository.py` (`DISTINCT ON`, índice existente); IT mede com 100.000 leituras e 10 pirômetros |
| RNF-03 | `clock_tool.py` e `pyrometers_controller.py` devolvem datas sem offset |
| RNF-05 | repositório de complemento sem SQL sobre `public.receiver_data`; BDD compara a tabela antes e depois |

## Contrato entre camadas

- **Controller → caso de uso**: o controller valida a entrada (Pydantic) e entrega valores simples. `PUT` devolve o pirômetro já com os padrões aplicados, no mesmo formato de um item de `GET /pyrometers`.
- **`ListPyrometersUseCase`**: lê `IReadingRepository.find_pyrometers()` e `IPyrometerProfileRepository.find_all()`, monta `PyrometerOverviewDto` aplicando: sem complemento → apelido e observação `None`, ativo `True`, cor pela função `default_color_model`. A lista é ordenada por serial; a cor padrão usa essa mesma ordem.
- **`SavePyrometerProfileUseCase`**: pergunta `IReadingRepository.pyrometer_exists(serial)`; se não existe, levanta `PyrometerNotFoundError` sem gravar; se existe, normaliza campos vazios para `None` e chama `IPyrometerProfileRepository.save`.
- **`ListPyrometerSummariesUseCase`**: lê `IReadingRepository.find_summaries()` e calcula os minutos com `IClockTool.now()`.
- **Erros**: `PyrometerNotFoundError` → 404 no controller; entrada inválida → 422 (Pydantic); falha de banco segue o handler existente (503).
- **Escrita**: somente `PyrometerProfileRepository`, somente no schema `app`. `ReadingRepository` continua só com `SELECT`.

## Dependências externas

| Dependência | Versão | Justificativa | Simulada nos testes por |
|---|---|---|---|
| `zoneinfo` (biblioteca padrão) | Python 3.12 | Fuso só do "agora" no `clock_tool` | testes unitários usam relógio mockado; BDD usa relógio fixo |
| Nenhuma biblioteca nova | — | O resto usa o que o projeto já tem | — |

## Impacto no contrato de operação

- Nenhum alvo novo no `Makefile`, nenhum serviço novo no compose.
- Variável de ambiente nova: `LOCAL_TIMEZONE` (padrão `America/Sao_Paulo`), acrescentada ao `.env.example`.
- `make init`/subida da API aplicam a migration `0002` pelo caminho que já existe (`run_migrations_on_start`).

## Riscos

| Risco | Probabilidade | Mitigação |
|---|---|---|
| A cor padrão de um pirômetro muda quando surge um novo que colide com ela (a sondagem desloca o de serial maior) | baixa | A sondagem só atua em colisão e segue a ordem de serial; quem quiser cor fixa grava a cor. Documentado; o RF-04 vale "sempre que a paleta permitir" |
| O container roda em UTC e o "agora" sai 3 h errado | média | `LOCAL_TIMEZONE` + `IClockTool`; teste do relógio com fuso explícito |
| `DISTINCT ON` lento com muitas leituras | baixa | Índice `(dev_id, reg_date)` já existe; IT mede 500 ms com 100.000 leituras; só então avaliar outra estratégia |
| Dois gestores editam o mesmo pirômetro ao mesmo tempo | média | Vale a última gravação (sem login, sem histórico: fora de escopo na spec); registrado |
| O filtro de temperatura muda total/paginação do front já implantado | baixa | É o comportamento exigido (RF-14 do front); o front não faz suposição contrária |
| Serial com `.`/caracteres especiais na rota `PUT /pyrometers/{id}` | baixa | Teste de controller e IT com serial real (`C24C.F90D.0000`) |

## Conformidade com a constituição

| Princípio | Como este plano o respeita |
|---|---|
| Contrato de operação | Tudo roda por `make` no serviço `dev`; nenhum alvo novo é necessário. Migration pelo caminho existente |
| Arquitetura limpa | `core` não importa `adapters`/`infra`: o relógio e os repositórios entram por `interfaces/`. Regra de cor padrão e de campos vazios fica em `core`. SQL só em `adapters/repositories` |
| Testes provam a entrega | Todo arquivo de produção com lógica tem teste espelhado; `it` contra o Postgres descartável real e `bdd` a partir dos critérios da spec; cobertura ≥ 90% por arquivo modificado |
| Simplicidade defensável | SQL explícito como o resto do projeto, sem ORM; padrões considerados e recusados listados |
| Autoria | Nenhum artefato credita ferramenta de IA |
| Idioma | Specs, plano e mensagens em português; identificadores em inglês |
| P1 — `receiver_data` somente leitura | Escrita só em `app.pyrometer_profile`; teste compara `receiver_data` antes e depois |
| P2 — só o banco `pirometros` | Nenhuma conexão nova |
| P3 — sem conversão de fuso | O fuso entra só no "agora" do relógio; `reg_date` nunca é convertido |
| P4 — sem autenticação | Nenhum login; qualquer cliente da rede edita (registrado na spec e nos riscos) |
| P5 — sem segredos | `LOCAL_TIMEZONE` não é segredo; `.env.example` com placeholder |
| P6 — Postgres real nos `it`/`bdd` | Os testes novos de integração usam o Postgres do compose, sem mockar a conexão |
