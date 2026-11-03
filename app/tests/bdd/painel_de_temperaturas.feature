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
