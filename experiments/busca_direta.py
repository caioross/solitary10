"""Busca exaustiva certificada: existe n <= LIMITE, n != 10, com I(n) = 9/5?

Cobre TODOS os inteiros até o limite, sem nenhuma hipótese estrutural.
Serve como verdade-base para validar as restrições da literatura.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.abundancy import ALVO, amigos_no_intervalo  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limite", type=int, default=2_000_000)
    args = parser.parse_args()

    achados = amigos_no_intervalo(ALVO, args.limite)
    extras = [n for n in achados if n != 10]
    print(f"Intervalo varrido: [1, {args.limite}]")
    print(f"n com I(n) = 9/5: {achados}")
    if extras:
        print(f"!!! AMIGO(S) DE 10 ENCONTRADO(S): {extras} — reverifique com fatoração independente antes de comemorar.")
    else:
        print("[VERIFICADO-NUMERICAMENTE] Nenhum amigo de 10 no intervalo.")


if __name__ == "__main__":
    main()
