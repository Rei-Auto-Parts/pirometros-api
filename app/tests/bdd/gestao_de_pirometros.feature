# language: pt
Funcionalidade: Gestão de pirômetros na API

  Cenário: Pirômetro sem complemento
    Dado que existem leituras do pirômetro "PI-12" e nenhum complemento gravado
    Quando eu consulto os pirômetros
    Então "PI-12" vem ativo, sem apelido, sem observação e com uma cor padrão

  Cenário: Gravar complemento
    Dado que existem leituras do pirômetro "PI-12" e nenhum complemento gravado
    Quando eu gravo o apelido "Forno 2", a cor "#e11d48" e a observação "termopar trocado" para ele
    Então a lista de pirômetros traz "PI-12" com esse apelido, essa cor e essa observação

  Cenário: Regravar substitui
    Dado que "PI-12" tem o apelido "Forno 2"
    Quando eu gravo o apelido "Forno 3" para ele
    Então a lista traz o apelido "Forno 3"
    Mas não existe um segundo complemento para "PI-12"

  Cenário: Inativar pirômetro
    Dado que existem leituras do pirômetro "PI-12" e nenhum complemento gravado
    Quando eu o marco como inativo
    Então a lista traz "PI-12" como inativo
    Mas as leituras dele continuam consultáveis

  Cenário: Serial inexistente
    Dado que não existem leituras do serial "ZZZZ.0000.0000"
    Quando eu tento gravar um complemento para ele
    Então recebo um erro de "não encontrado"
    Mas nada é gravado

  Cenário: Cor inválida
    Dado que "PI-12" tem o apelido "Forno 2"
    Quando eu gravo para "PI-12" a cor "vermelhão"
    Então recebo um erro de validação informando o formato de cor aceito
    Mas o complemento anterior permanece

  Cenário: Apelido acima do máximo
    Quando eu gravo para "PI-12" um apelido com 41 caracteres
    Então recebo um erro de validação informando o máximo de 40 caracteres

  Cenário: Cor já em uso por outro pirômetro
    Dado que "PI-12" tem a cor "#e11d48" e que "PI-14" existe
    Quando eu gravo para "PI-14" a cor "#e11d48"
    Então recebo um erro de conflito informando que a cor já está em uso
    Mas nada muda para "PI-14"

  Cenário: Cor padrão de outro pirômetro também conta como em uso
    Dado que "PI-12" e "PI-14" não têm cor escolhida
    Quando eu gravo para "PI-14" a cor que "PI-12" mostra
    Então recebo um erro de conflito informando que a cor já está em uso

  Cenário: Regravar a própria cor
    Dado que "PI-12" tem a cor "#e11d48"
    Quando eu gravo para "PI-12" o apelido "Forno 2" e a cor "#e11d48"
    Então a lista traz "PI-12" com a cor "#e11d48" e o apelido "Forno 2"

  Cenário: Cor padrão estável
    Dado que "PI-12" e "PI-14" não têm cor escolhida
    Quando eu consulto os pirômetros duas vezes
    Então a cor de cada um é a mesma nas duas consultas
    Mas "PI-12" e "PI-14" têm cores diferentes

  Cenário: Resumo por pirômetro
    Dado que "PI-12" tem leituras às 10:00:00 (1500 graus, bateria 63) e às 10:05:00 (1510 graus, bateria 62)
    E que agora são 10:08:00
    Quando eu consulto o resumo
    Então "PI-12" traz 1510 graus, bateria 62, a data 10:05:00 e 3 minutos sem leitura

  Cenário: Resumo ignora leitura sem temperatura
    Dado que "PI-12" tem uma leitura às 10:00:00 com 1400 graus e a mais recente, às 10:05:00, sem temperatura
    Quando eu consulto o resumo
    Então "PI-12" traz 1400 graus e a data 10:00:00

  Cenário: Leituras sem temperatura fora da lista
    Dado que existem 3 leituras no período, uma delas sem temperatura
    Quando eu consulto as leituras do período
    Então recebo 2 itens e o total é 2

  Cenário: Leituras sem temperatura fora da série
    Dado que existem leituras de "PI-12" no período, uma sem temperatura
    Quando eu consulto a série do período
    Então a série de "PI-12" não traz o ponto sem temperatura

  Cenário: Complemento sobrevive a novas leituras
    Dado que "PI-12" tem o apelido "Forno 2"
    Quando chegam novas leituras de "PI-12"
    Então a lista continua trazendo o apelido "Forno 2"

  Cenário: Dado gravado não é alterado
    Dado que existem leituras de "PI-12" e "PI-14"
    Quando eu gravo um complemento e consulto leituras, série, resumo e pirômetros
    Então a tabela de leituras permanece idêntica
