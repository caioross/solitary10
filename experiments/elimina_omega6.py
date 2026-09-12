"""Certificação: nenhum amigo de 10 tem omega(N) = 6  =>  omega(N) >= 7.

Reproduz mecanicamente o Teorema 1.2 de arXiv:2404.00624 (Chatterjee-Mandal-Mandal)
usando o certificador core/omega6.py (cadeias de divisibilidade: fecho por ordens,
orçamentos v3/v5 da equação-mestra, e extração exata do sexto primo pelo índice).
Ver a moldura matemática em results/PHASE_1.md (Bloco 2) e core/omega6.py.

Se alguma escada não fechar (NaoCertificavel), NADA é certificado.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.omega6 import NaoCertificavel, certifica_omega6  # noqa: E402


def main() -> None:
    t0 = time.perf_counter()
    try:
        stats = certifica_omega6()
    except NaoCertificavel as exc:
        print(f"NAO CERTIFICADO: {exc}")
        sys.exit(2)
    dt = time.perf_counter() - t0

    print(f"prefixos C5: {stats.prefixos} (ramo i: {stats.prefixos_ramo_i}, "
          f"ramo ii: {stats.prefixos_ramo_ii}, "
          f"mortos por poda-min: {stats.prefixos_mortos_min})")
    print(f"conjuntos completos: {stats.conjuntos_completos}; "
          f"folhas alcancadas na fase de expoentes: {stats.assinaturas_testadas}")
    print(f"pins de P testados no ramo ii: {stats.pins_testados}")
    print(f"tempo: {dt:.1f}s")

    if stats.amigos:
        print(f"!!! AMIGO(S) DE 10 ENCONTRADO(S): {stats.amigos}")
        print("    Reverifique com fatoração independente antes de qualquer alarde.")
        sys.exit(1)

    print()
    print("CERTIFICADO: nenhum amigo de 10 tem omega(N) = 6; com omega >= 6 "
          "(Resultado F), todo amigo de 10 tem omega(N) >= 7.")
    print("Rótulo: [PROVADO-CONDICIONAL: Teoremas A-D e Lemas/Fato 0 da Fase 0 + "
          "Zsygmondy e formula de valuacao de Nielsen/Voight (classicos; formula "
          "re-testada exaustivamente em tests/test_cadeias.py) + correção de "
          "core/omega6.py e core/cadeias.py (passada adversarial em "
          "results/PHASE_1.md §2.5) + correção de sympy.n_order/factorint/nextprime "
          "nas chamadas consumidas (todas re-verificadas por implementações "
          "próprias na passada adversarial)]")
    print("Reproduz o Teorema 1.2 de arXiv:2404.00624 por via independente.")


if __name__ == "__main__":
    main()
