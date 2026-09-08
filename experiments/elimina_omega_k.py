"""Certificacao recursiva: nenhum amigo de 10 tem omega(N) = k (Fase 1, Bloco 3).

Usa core/omega_k.py (certificador recursivo: enumeracao pelo indice quando o
prefixo permite, PINAGEM pela alimentacao do 5 com a cota universal
a1 <= 1 + (c5 + s)(c5 + s - 1) quando nao permite). Ver results/FASE_1.md, Bloco 3.

Se alguma cobertura nao fechar (NaoCertificavel), NADA e certificado para esse k.

Uso:  python experiments/elimina_omega_k.py --k 7
      python experiments/elimina_omega_k.py --k-max 7     (varre k = 1..7)
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.omega_k import NaoCertificavel, certifica_omega  # noqa: E402


def roda(k: int) -> bool:
    t0 = time.perf_counter()
    try:
        st = certifica_omega(k)
    except NaoCertificavel as exc:
        print(f"omega = {k}: NAO CERTIFICADO apos {time.perf_counter() - t0:.1f}s")
        print(f"   estado residual: {exc}")
        return False
    dt = time.perf_counter() - t0
    print(f"omega = {k}: nos={st.nos} mortos_min={st.mortos_min} ramo_i={st.ramo_i} "
          f"particoes={st.particoes} conjuntos_completos={st.conjuntos_completos} "
          f"folhas={st.assinaturas_testadas} amigos={len(st.amigos)} tempo={dt:.1f}s")
    if st.pins:
        print("   pins (prefixo, caso, primos pinados):")
        for c, caso, p in st.pins:
            print(f"     {list(c)} {caso} -> {list(p)}")
    if st.amigos:
        print(f"!!! omega = {k}: AMIGO(S) DE 10 ENCONTRADO(S): {st.amigos}")
        print("    Reverifique com fatoracao independente antes de qualquer alarde.")
        sys.exit(1)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k", type=int, default=None, help="certifica so este omega")
    parser.add_argument("--k-max", type=int, default=None, help="varre omega = 1..k-max")
    args = parser.parse_args()
    if args.k is None and args.k_max is None:
        parser.error("informe --k ou --k-max")

    ks = [args.k] if args.k is not None else list(range(1, args.k_max + 1))
    certificados = []
    for k in ks:
        if roda(k):
            certificados.append(k)
        else:
            break

    if certificados and certificados == list(range(1, max(certificados) + 1)):
        w = max(certificados) + 1
        print()
        print(f"CERTIFICADO: todo amigo de 10 tem omega(N) >= {w}.")
    elif certificados:
        print()
        print(f"CERTIFICADO (parcial): nenhum amigo de 10 tem omega(N) em {certificados}.")
    if certificados:
        print("Rotulo: [PROVADO-CONDICIONAL: Teoremas A-D e Lemas/Fato 0 da Fase 0 + "
              "Zsygmondy e formula de valuacao de Nielsen/Voight (classicos) + correcao "
              "de core/omega_k.py (certificador recursivo AINDA SEM passada adversarial "
              "propria - nao e load-bearing), core/omega6.py e core/cadeias.py (passada "
              "adversarial em results/FASE_1.md §2.5) + correcao de "
              "sympy.n_order/factorint/nextprime/cyclotomic_poly nas chamadas consumidas]")
        print("Nota: para omega >= 7 o certificado load-bearing e o do Bloco 2 "
              "(experiments/elimina_omega6.py); este recursivo e corroboracao independente.")


if __name__ == "__main__":
    main()
