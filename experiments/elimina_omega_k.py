"""Certificacao recursiva: nenhum amigo de 10 tem omega(N) = k (Fase 1, Blocos 3-8).

Usa core/omega_k.py (certificador recursivo: particao por orcamentos v5/v3 com a
cota universal a1 <= 1 + (c5 + s)(c5 + s - 1), fecho dos expoentes comprometidos,
ramificacao por expoente com cauda, conjuntos completos com um primo grande sem
fatorar r - 1, indice como fallback). Ver results/PHASE_1.md, Blocos 3 e 4.
Since Block 8 the budgets and the range of a1 are generic in the target; the forms above
are their 9/5 case, the only target this script runs.

Se alguma cobertura nao fechar (NaoCertificavel), NADA e certificado para esse k.
Exit status: 0 iff every requested k was certified; 1 if a friend was found; 2 if the
run stopped at a k that could not be certified (NaoCertificavel), as in
experiments/elimina_omega6.py.

Uso:  python experiments/elimina_omega_k.py --k 7
      python experiments/elimina_omega_k.py --k-max 7     (varre k = 1..7)
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.omega_k import NaoCertificavel, certifica_omega  # noqa: E402


def roda(k: int, args_pins: bool = False) -> bool:
    t0 = time.perf_counter()
    try:
        st = certifica_omega(k, light=not args_pins)
    except NaoCertificavel as exc:
        print(f"omega = {k}: NAO CERTIFICADO apos {time.perf_counter() - t0:.1f}s")
        print(f"   estado residual: {exc}")
        return False
    dt = time.perf_counter() - t0
    print(f"omega = {k}: nos={st.nos} mortos_min={st.mortos_min} ramo_i={st.ramo_i} "
          f"particoes={st.particoes} ramos_expoente={st.ramos_expoente} caudas={st.caudas} "
          f"conjuntos_completos={st.conjuntos_completos} "
          f"completos_mortos_indice={st.completos_mortos_indice} "
          f"com_primo_grande={st.conjuntos_com_primo_grande} "
          f"casos_sem_fecho={st.casos_sem_fecho} ultimos_resolvidos={st.ultimos_resolvidos} candidatos_ultimo={st.candidatos_ultimo} cor6_ramos={st.cor6_ramos} cor6_mortos={st.cor6_mortos} fecho_total_mortos={st.fecho_total_mortos} "
          f"splits={st.splits} dead_hi={st.dead_hi} "
          f"folhas={st.assinaturas_testadas} amigos={len(st.amigos)} tempo={dt:.1f}s")
    if st.pins and args_pins:
        print("   pins (prefixo, caso, primos pinados):")
        for c, caso, p in st.pins:
            print(f"     {list(c)} {caso} -> {list(p)}")
    elif st.n_pins:
        print(f"   pins registrados: {st.n_pins} (use --pins para listar)")
    if st.amigos:
        print(f"!!! omega = {k}: AMIGO(S) DE 10 ENCONTRADO(S): {st.amigos}")
        print("    Reverifique com fatoracao independente antes de qualquer alarde.")
        sys.exit(1)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k", type=int, default=None, help="certifica so este omega")
    parser.add_argument("--k-max", type=int, default=None, help="varre omega = 1..k-max")
    parser.add_argument("--pins", action="store_true", help="lista todos os pins (verboso)")
    args = parser.parse_args()
    if args.k is None and args.k_max is None:
        parser.error("informe --k ou --k-max")

    ks = [args.k] if args.k is not None else list(range(1, args.k_max + 1))
    certificados = []
    for k in ks:
        if roda(k, args.pins):
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
        print("Label: [PROVED-CONDITIONAL: Theorems A-D and Lemmas/Fact 0 of Phase 0 + "
              "Zsygmondy, LTE and the Nielsen/Voight valuation formula (classical) + "
              "correctness of core/omega_k.py, core/cadeias.py, core/omega6.py, "
              "core/primality.py and of the primitives ALVO, I_pp, sigma_pp and sup_pp of "
              "core/motor.py (adversarial passes: results/PHASE_1.md sections 1.5, 2.5, "
              "7.4, 8.4 and 8.9; replay audit 7.6 with its open items closed in 8.6 "
              "except a run on other hardware; "
              "planted friends driven end to end, 8.2, with the limit stated in 8.3: the "
              "finite exponent bound is tested statement by statement, not end to end) "
              "+ the primality claims of the run above 2^64, proved when "
              "experiments/certify_primes.py --k-max K exits 0 for the same K (this "
              "script does not check them; without that run they rest on sympy's BPSW), "
              "and sympy.isprime below 2^64 and its answers 'composite' above 2^64 at "
              "the sites listed in 8.5 + correctness "
              "of sympy.factorint/nextprime/primerange/integer_nthroot/cyclotomic_poly/"
              "divisors/totient in the calls consumed]")
        print("Note: not load-bearing. For omega >= 7 the load-bearing certificate is "
              "the one of Block 2 (experiments/elimina_omega6.py); omega(N) >= 10 is "
              "the theorem of Thackeray (arXiv:2310.15900), which a full run up to "
              "k = 9 reproduces by a different method.")
    if len(certificados) < len(ks):
        print()
        print(f"NAO CERTIFICADO: requested k = {ks[0]}..{ks[-1]}; the run stopped at "
              f"k = {ks[len(certificados)]} (NaoCertificavel); certified: "
              f"{certificados or 'none'}.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
