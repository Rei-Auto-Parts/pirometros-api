# language: pt
Funcionalidade: Saude da API

  Cenario: API e banco de dados no ar
    Dado que o banco de dados esta acessivel
    Quando eu consulto a saude da API
    Entao a API responde com status 200
    E a resposta informa api "up" e banco "up"

  Cenario: Banco de dados fora do ar
    Dado que o banco de dados esta inacessivel
    Quando eu consulto a saude da API
    Entao a API responde com status 200
    E a resposta informa api "up" e banco "down"
