# Especificação — Gestão de pirômetros na API (complemento, resumo e leituras sem temperatura)

> Descreve **o quê** e **por quê**. Não descreve como implementar: sem nome de biblioteca,
> sem esquema de banco, sem assinatura de função.

## Problema

Os pirômetros só existem como aparecem nos dados do sincronizador: um serial e um nome de poucos
caracteres vindo do aparelho (ex.: "PI-12"). Os gestores não conseguem dar um nome que faça
sentido na fábrica, distinguir cada aparelho por cor nem registrar uma observação sobre ele. O
painel também não sabe dizer, num relance, qual a última temperatura de cada aparelho e há quanto
tempo ele não envia leitura. Além disso, a API devolve leituras sem temperatura, que o painel
nunca deve mostrar (RF-14 do front, spec 001) e que quebram total e paginação se filtradas só no
cliente.

## Objetivo

1. Cada pirômetro **existente** pode receber um complemento (apelido, cor, observação, ativo),
   guardado pela própria API, sem tocar nos dados do sincronizador.
2. A API entrega um **resumo por pirômetro** com a última leitura, a bateria e o tempo sem leitura.
3. Leituras sem temperatura **nunca** saem da API (lista, total e série).

## Fora de escopo

- Criar, renomear o serial ou apagar um pirômetro: a lista vem sempre dos dados gravados.
- Alterar o nome que vem do aparelho: o complemento convive com ele.
- Faixa de temperatura mín/máx, alertas, e-mail e qualquer notificação.
- Exportação (CSV ou outra).
- Histórico de alterações do complemento e registro de quem alterou.
- Autenticação, login, perfis (constituição P4): qualquer um que acesse a API pode editar.
- Corrigir, estimar ou apagar leituras; qualquer escrita em `public.receiver_data` (constituição P1).
- Conversão de fuso nas datas (constituição P3).

## Personas e cenários de uso

- **Gestor**: dá a cada pirômetro um apelido e uma cor, anota uma observação ("termopar trocado
  em 03/11") e marca como inativo um aparelho aposentado.
- **Painel (front)**: consulta os pirômetros com seus complementos e o resumo de cada um para
  montar os cards e o gráfico.

## Requisitos funcionais

| ID | Requisito | Prioridade |
|---|---|---|
| RF-01 | A lista de pirômetros existentes deve trazer, além do serial e do nome do aparelho, o apelido, a cor, a observação e se está ativo. Pirômetro sem complemento aparece com apelido e observação vazios, ativo, e com a cor padrão (RF-04). | obrigatório |
| RF-02 | O sistema deve permitir gravar o complemento de um pirômetro existente, identificado pelo serial: apelido, cor, observação e ativo. A primeira gravação cria o complemento; as seguintes o substituem. Serial que não existe nos dados é recusado com erro de "não encontrado", sem gravar nada. | obrigatório |
| RF-03 | Apelido, cor e observação inválidos devem ser recusados com erro de validação claro: apelido acima de 40 caracteres, observação acima de 500 caracteres, cor que não seja hexadecimal `#rrggbb`. Apelido e observação podem ficar vazios. | obrigatório |
| RF-04 | Pirômetro sem cor escolhida deve receber uma cor padrão, sempre a mesma para o mesmo serial, e diferente das demais cores (padrão ou escolhidas) sempre que a paleta permitir. | obrigatório |
| RF-05 | O sistema deve devolver um resumo por pirômetro existente: temperatura e data da leitura mais recente com temperatura, bateria dessa leitura e o tempo, em minutos, desde essa leitura até agora. | obrigatório |
| RF-06 | `GET /readings` (itens e total) e `GET /readings/series` devem excluir leituras sem temperatura, de modo que total e paginação contem só leituras com temperatura. | obrigatório |
| RF-07 | O complemento nunca altera, cria ou apaga leituras; os dados de `public.receiver_data` permanecem idênticos após qualquer operação. | obrigatório |
| RF-09 | Dois pirômetros nunca podem ficar com a mesma cor: gravar uma cor igual à que outro pirômetro usa (escolhida ou padrão) é recusado com erro de conflito, sem gravar nada. Regravar a própria cor é permitido. | obrigatório |
| RF-08 | O complemento gravado deve sobreviver à reinicialização da API e a novas leituras do sincronizador. | obrigatório |

## Requisitos não funcionais

| ID | Requisito | Critério mensurável |
|---|---|---|
| RNF-01 | Desempenho do resumo | resposta em ≤ 500 ms com 100.000 leituras e 10 pirômetros |
| RNF-02 | Desempenho da lista de pirômetros | resposta em ≤ 500 ms com 100.000 leituras e 10 pirômetros |
| RNF-03 | Datas sem fuso | 100% das datas devolvidas sem offset, iguais às gravadas |
| RNF-04 | Cobertura de testes | ≥ 90% por arquivo modificado |
| RNF-05 | Escrita nos dados do sincronizador | 0 escritas em `public.receiver_data` |

## Critérios de aceite

```gherkin
# language: pt
Funcionalidade: Gestão de pirômetros na API

  Cenário: Pirômetro sem complemento
    Dado que existem leituras do pirômetro "PI-12" e nenhum complemento gravado
    Quando eu consulto os pirômetros
    Então "PI-12" vem ativo, sem apelido, sem observação e com uma cor padrão

  Cenário: Gravar complemento
    Dado que existem leituras do pirômetro "PI-12"
    Quando eu gravo o apelido "Forno 2", a cor "#e11d48" e a observação "termopar trocado" para ele
    Então a lista de pirômetros traz "PI-12" com esse apelido, essa cor e essa observação

  Cenário: Regravar substitui
    Dado que "PI-12" tem o apelido "Forno 2"
    Quando eu gravo o apelido "Forno 3" para ele
    Então a lista traz o apelido "Forno 3"
    Mas não existe um segundo complemento para "PI-12"

  Cenário: Inativar pirômetro
    Dado que existem leituras do pirômetro "PI-12"
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
```

## Ambiguidades

Nenhuma em aberto.

## Esclarecimentos

| Pergunta | Resposta | Data |
|---|---|---|
| Pode criar pirômetro novo? | Não: o complemento é só sobre pirômetros que já existem nos dados, chave = serial | 2026-11-05 |
| Notificação por e-mail | Fora de escopo | 2026-11-05 |
| Tamanhos máximos | Apelido 40 caracteres, observação 500 | 2026-11-05 |
| Cor | A API aceita hexadecimal `#rrggbb`; o front oferece paleta fixa de 12 cores | 2026-11-05 |
| Observação | Texto livre único por pirômetro, sem histórico | 2026-11-05 |
| Cor repetida entre pirômetros | Proibida: a API recusa com conflito (decisão do usuário em 2026-11-05) | 2026-11-05 |
| Pirômetro inativo | A API sempre lista todos, com a marca de ativo; quem esconde é o front | 2026-11-05 |
| "Agora" do tempo sem leitura | Horário local do servidor, sem conversão de fuso | 2026-11-05 |
| Alerta por tempo sem leitura | Não existe: o tempo sem leitura é só informação | 2026-11-05 |
| Exportação CSV | Fora de escopo por enquanto | 2026-11-05 |
| Leitura sem temperatura | Excluída da API (pendência da spec 001 do front, RF-14) | 2026-11-04 |

## Métricas de sucesso

- Todo pirômetro em uso aparece no painel com apelido e cor próprios em até 1 semana de uso.
- Nenhuma escrita na tabela de leituras registrada em produção.
- `total` de `/readings` igual à contagem de leituras com temperatura do período.
