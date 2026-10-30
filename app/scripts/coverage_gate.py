#!/usr/bin/env python3
"""Portao de cobertura: falha quando o percentual medido fica abaixo do minimo.

Uso:
    coverage_gate.py --value 87.4 --min 90
    <comando que imprime o percentual> | coverage_gate.py --min 90

Aceita "87.4", "87.4%" ou "total: (statements) 87.4%".
"""

from __future__ import annotations

import argparse
import re
import sys

WITH_SIGN = re.compile(r"(\d+(?:[.,]\d+)?)\s*%")
BARE_NUMBER = re.compile(r"(\d+(?:[.,]\d+)?)")


def parse_percentage(raw: str) -> float:
    """Extrai o percentual da ultima linha da saida da ferramenta de cobertura.

    O numero com `%` tem prioridade: a linha TOTAL do coverage.py comeca com a
    contagem de statements, e ler o primeiro numero daria 534 em vez de 96%.
    """
    line = raw.strip().splitlines()[-1] if raw.strip() else ""
    matches = WITH_SIGN.findall(line) or BARE_NUMBER.findall(line)
    if not matches:
        raise ValueError(
            f"cobertura invalida: recebido {raw.strip()[:60]!r}, "
            "esperado um numero como '87.4' ou '87.4%'"
        )
    return float(matches[-1].replace(",", "."))


def main() -> int:
    parser = argparse.ArgumentParser(description="Portao de cobertura de testes unitarios.")
    parser.add_argument("--value", help="percentual medido; se ausente, le do stdin")
    parser.add_argument("--min", type=float, default=90.0, help="percentual minimo exigido")
    args = parser.parse_args()

    raw = args.value if args.value is not None else sys.stdin.read()
    measured = parse_percentage(raw)

    if measured + 1e-9 < args.min:
        print(f"COBERTURA REPROVADA: {measured:.2f}% medido, minimo {args.min:.2f}%.")
        print("Escreva o teste que falta. Nao baixe o limite nem exclua arquivo da medicao.")
        return 1
    print(f"Cobertura aprovada: {measured:.2f}% (minimo {args.min:.2f}%).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValueError as error:
        print(str(error), file=sys.stderr)
        sys.exit(2)
