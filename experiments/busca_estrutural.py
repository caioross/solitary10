"""Busca estrutural: por Ward (2008), um amigo de 10 é um quadrado ímpar com 25 | N.

Logo N = m^2 com m ímpar e 5 | m. Varrer m até LIMITE_M cobre N até LIMITE_M^2
dentro do espaço estrutural — muito além do alcance da busca direta.

ATENÇÃO: a exaustividade aqui é CONDICIONAL às restrições de Ward, que devem ser
re-derivadas e provadas na Fase 0 antes de este resultado ser citado.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.abundancy import sigma_do_quadrado  # noqa: E402


def busca(limite_m: int) -> list[int]:
    achados = []
    for m in range(5, limite_m + 1, 10):  # m ímpar, múltiplo de 5
        n = m * m
        if 5 * sigma_do_quadrado(m) == 9 * n:
            achados.append(n)
    return achados


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limite-m", type=int, default=1_000_000)
    args = parser.parse_args()

    achados = busca(args.limite_m)
    print(f"Espaço varrido: N = m^2, m ímpar múltiplo de 5, m <= {args.limite_m}")
    print(f"(cobre candidatos estruturais até N = {args.limite_m ** 2:.2e})")
    if achados:
        print(f"!!! CANDIDATO(S): {achados} — reverifique com fatoração independente.")
    else:
        print("[VERIFICADO-NUMERICAMENTE | condicional a Ward] Nenhum amigo no espaço varrido.")


if __name__ == "__main__":
    main()
