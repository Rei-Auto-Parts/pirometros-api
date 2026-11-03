# Especificação — Painel de temperaturas (API, somente leitura)

> Descreve **o quê** e **por quê**. Não descreve como implementar: sem nome de biblioteca,
> sem esquema de banco, sem assinatura de função.

## Problema

Os pirômetros de imersão da fundição enviam cada medição para um banco, mas ninguém consegue
consultá-las de forma útil: só existe a tabela bruta. Gestores e a Qualidade não veem o que foi
medido, por qual pirômetro e quando.

## Objetivo

A API expõe, só para leitura, exatamente o que está gravado no banco: as leituras dos pirômetros
ordenadas pela data da medição, a série de temperaturas por pirômetro num período e a lista de
pirômetros. O front monta o painel em cima disso.

## Fora de escopo

- Qualquer tratamento, estimativa ou correção de datas ou de valores: mostra-se o que está gravado.
- Saúde dos pirômetros (bateria baixa, sem leitura recente) e indicadores de atraso de entrega.
- Números do turno (medições oficiais, % dentro da faixa, abaixo, acima, sem código).
- Mapa de códigos de local, pontos de medição, equipamentos, setores, etapas.
- Faixas de temperatura, avaliação de faixa e classificação.
- Correção manual de leituras.
- Autenticação, usuários e perfis.
- Escrita de qualquer tipo na tabela de leituras.

## Personas e cenários de uso

- **Gestor da fundição**: consulta o que cada pirômetro mediu num dia ou período e a evolução
  da temperatura.
- **Laboratório da Qualidade**: acompanha, numa TV, as últimas medições e a evolução por pirômetro.

## Requisitos funcionais

| ID | Requisito | Prioridade |
|---|---|---|
| RF-01 | O sistema deve listar as leituras de um período informado (início e fim), da mais recente para a mais antiga pela data da medição, com paginação (padrão 50, máximo 500), filtráveis por pirômetro. | obrigatório |
| RF-02 | Cada leitura listada deve trazer todos os dados da medição gravados: identificador, pirômetro (serial e nome), receptor, data da medição, temperatura, unidade, termopar, junta fria, tempo de leitura, tempo de detecção, bateria e código de local. | obrigatório |
| RF-03 | O sistema deve devolver a série de temperaturas de um ou mais pirômetros num período informado, agrupada por pirômetro e ordenada pela data da medição, com todos os pontos. Período acima de 31 dias é recusado com erro claro. | obrigatório |
| RF-04 | O sistema deve listar os pirômetros existentes (serial e nome atual). | obrigatório |
| RF-05 | O sistema nunca deve criar, alterar ou apagar leituras, nem converter fuso das datas. | obrigatório |

## Requisitos não funcionais

| ID | Requisito | Critério mensurável |
|---|---|---|
| RNF-01 | Desempenho da listagem e da série | p95 ≤ 500 ms para um período de até 7 dias com até 10.000 leituras |
| RNF-02 | Datas sem conversão de fuso | 100% das datas devolvidas sem offset, iguais às gravadas |
| RNF-03 | Somente leitura | 0 comandos de escrita executados sobre a tabela de leituras |
| RNF-04 | Cobertura de testes | ≥ 90% |

## Critérios de aceite

```gherkin
# language: pt
Funcionalidade: Painel de temperaturas (API, somente leitura)

  Contexto:
    Dado que toda consulta de leituras ou de série informa um período, com início e fim

  Cenário: Listar leituras da mais recente para a mais antiga
    Dado que existem leituras dos pirômetros "PI-12" e "PI-14" no dia 29/10/2026
    Quando eu consulto as leituras desse dia
    Então recebo as leituras da mais recente para a mais antiga pela data da medição
    E cada leitura traz todos os dados da medição gravados

  Cenário: Leitura que chegou atrasada fica na ordem da data
    Dado que o "PI-14" mediu às 09:00 e essa leitura foi gravada depois de uma das 14:02
    Quando eu consulto as leituras desse dia
    Então a leitura das 09:00 vem depois da leitura das 14:02

  Cenário: Filtrar leituras por pirômetro
    Dado que existem leituras de "PI-12" e "PI-14" no mesmo período
    Quando eu consulto as leituras do "PI-12" nesse período
    Então recebo somente leituras do "PI-12"

  Cenário: Período limita as leituras
    Dado que existem leituras em 28/10/2026 e em 29/10/2026
    Quando eu consulto as leituras de 29/10/2026
    Então recebo somente leituras de 29/10/2026

  Cenário: Paginação respeita o limite
    Dado que existem mais de 500 leituras no período
    Quando eu consulto as leituras sem informar o tamanho da página
    Então recebo 50 leituras
    Mas se eu pedir mais de 500 por página, recebo um erro de validação

  Cenário: Datas sem fuso
    Dado uma leitura gravada em 2026-10-29 11:00:30
    Quando eu consulto as leituras
    Então a data devolvida é "2026-10-29T11:00:30" sem offset de fuso

  Cenário: Série por pirômetro
    Dado leituras de "PI-12" e "PI-14" no dia 29/10/2026
    Quando eu consulto a série desse dia
    Então recebo uma série para cada pirômetro, ordenada pela data da medição

  Cenário: Período da série acima do máximo
    Quando eu consulto a série de um período de 40 dias
    Então recebo um erro de validação informando o máximo de 31 dias

  Cenário: Listar pirômetros
    Dado que existem leituras de "PI-12" e "PI-14"
    Quando eu consulto os pirômetros
    Então recebo os dois, cada um com serial e nome

  Cenário: Dado gravado não é alterado
    Dado que existem leituras de "PI-12" e "PI-14"
    Quando eu consulto as leituras, a série e os pirômetros
    Então a tabela de leituras permanece idêntica
```

## Ambiguidades

Nenhuma em aberto.

## Esclarecimentos

| Pergunta | Resposta | Data |
|---|---|---|
| Escopo da primeira spec | Painel simples que mostra exatamente o que está gravado; sem tratamento de datas, sem saúde de pirômetro | 2026-11-03 |
| Ordenação | Sempre pela data da medição, nunca pelo identificador | 2026-11-03 |
| Consulta sem período | Não existe: leituras e série sempre pedem início e fim | 2026-11-03 |
| Série: todos os pontos ou agregar | Todos os pontos, com período máximo de 31 dias | 2026-11-03 |
| Tamanho de página | 50 padrão, 500 máximo | 2026-11-03 |
| Tabela nos testes de integração | Fixture cria a tabela só no Postgres descartável do compose | 2026-11-03 |

## Métricas de sucesso

- O painel mostra a leitura mais recente de cada pirômetro com atraso ≤ 6 minutos em relação ao SQL Server (5 min do sincronizador + margem).
- Nenhuma escrita na tabela de leituras é registrada em produção.
