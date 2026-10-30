#!/usr/bin/env python3
"""Inicializa a infraestrutura local do projeto, por dentro do servico `dev`.

Uso:
    init_infra.py

Espera os servicos de apoio declarados em `INIT_WAIT_FOR` responderem, e sai. O formato e
`host:porta`, separados por virgula — por exemplo `wiremock:8080, banco:5432`. Sem a
variavel, nao ha o que inicializar e o alvo conclui com sucesso.

Roda **dentro** do container `dev` (`docker compose exec`), onde nao existe CLI do docker:
por isso a prontidao e medida por conexao TCP, e nao por `docker compose ps`.

Ajuste por ambiente: `INIT_WAIT_TIMEOUT` (padrao 60 s) e `INIT_WAIT_INTERVAL` (padrao 1 s).

Ponto de extensao do projeto: `provision()`. Buckets, seeds e migracoes entram la.
"""

from __future__ import annotations

import os
import socket
import sys
import time
from collections.abc import Callable

DEFAULT_TIMEOUT = 60.0
DEFAULT_INTERVAL = 1.0

Target = tuple[str, int]


def parse_targets(raw: str) -> list[Target]:
    """Converte "wiremock:8080, banco:5432" na lista de alvos a esperar."""
    alvos: list[Target] = []
    for pedaco in raw.split(","):
        texto = pedaco.strip()
        if not texto:
            continue
        host, _, porta = texto.partition(":")
        if not host or not porta.strip().isdigit():
            raise ValueError(
                f"alvo invalido em INIT_WAIT_FOR: recebido {texto!r}, esperado 'host:porta'"
            )
        alvos.append((host.strip(), int(porta)))
    return alvos


def responds(host: str, port: int, timeout: float = 1.0) -> bool:
    """True quando o servico aceita conexao no endereco informado."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def wait_for(
    alvos: list[Target],
    limite: float,
    intervalo: float,
    sonda: Callable[[str, int], bool] = responds,
    agora: Callable[[], float] = time.monotonic,
    dormir: Callable[[float], None] = time.sleep,
) -> list[Target]:
    """Espera os alvos responderem e devolve os que nao responderam dentro do limite.

    Sonda ao menos uma vez, mesmo com limite zero: o alvo pode ja estar de pe, e nesse caso
    nao ha razao para cobrar tempo de espera de quem nao precisou esperar.
    """
    fim = agora() + limite
    pendentes = list(alvos)
    while True:
        pendentes = [alvo for alvo in pendentes if not sonda(*alvo)]
        if not pendentes or agora() >= fim:
            return pendentes
        dormir(intervalo)


def float_env(nome: str, padrao: float) -> float:
    """Le um ajuste numerico do ambiente, caindo no padrao quando o valor nao e numero."""
    try:
        return float(os.environ.get(nome, "").strip())
    except ValueError:
        return padrao


def provision() -> None:
    """Ponto de extensao do projeto: buckets, seeds, migracoes.

    O esqueleto nao adivinha o que o seu projeto precisa. Acrescente aqui, e mantenha
    headless: sem prompt, sem credencial fora do repositorio, sem passo manual.

    Exemplo de uso:
        criar_bucket("relatorios")
        aplicar_migracoes()
    """
    from infra.init.migration_init import run_migrations

    run_migrations(os.environ["DATABASE_URL"])
    print("migrations do schema `app` aplicadas.")


def _describe(alvos: list[Target]) -> str:
    return ", ".join(f"{host}:{porta}" for host, porta in alvos)


def main() -> int:
    try:
        alvos = parse_targets(os.environ.get("INIT_WAIT_FOR", ""))
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2
    if not alvos:
        print("sem infraestrutura a inicializar: INIT_WAIT_FOR nao declara servico de apoio")
        return 0

    limite = float_env("INIT_WAIT_TIMEOUT", DEFAULT_TIMEOUT)
    intervalo = float_env("INIT_WAIT_INTERVAL", DEFAULT_INTERVAL)
    print(f"esperando {len(alvos)} servico(s) de apoio: {_describe(alvos)}")

    pendentes = wait_for(alvos, limite, intervalo)
    if pendentes:
        print(
            f"INFRAESTRUTURA INDISPONIVEL: {_describe(pendentes)} nao respondeu em "
            f"{limite:.0f}s. Confira `make ps` e `make logs`.",
            file=sys.stderr,
        )
        return 1

    print("infraestrutura pronta.")
    provision()
    return 0


if __name__ == "__main__":
    sys.exit(main())
