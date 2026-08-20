"""Cota inferior CERTIFICADA para o menor amigo de 10, condicional a omega(N) >= 10.

Lógica (tudo exato):
  1. [PROVADO, Fase 0] Um amigo N tem todos os primos >= 5 (com 5 | N) e todos os
     expoentes pares >= 2; logo N >= (produto dos seus primos)².
  2. [literatura] omega(N) >= 10 (arXiv:2310.15900).
  3. Se (produto dos k menores primos >= 5)² > B, nenhum amigo N <= B tem omega = k
     (nem maior). Logo basta varrer omega = 10, 11, ..., k_max-1 com a busca limitada
     exaustiva do motor (core/motor.busca_limitada), que sempre termina (teto de
     produto) e testa a igualdade 5·sigma(N) = 9·N em toda assinatura sobrevivente.
  4. Varredura vazia => NENHUM amigo de 10 com N <= B. Rótulo:
     [PROVADO-CONDICIONAL: Teoremas A-D + omega >= 10 + correção do motor].

Comparação-alvo: a alegação NÃO certificada "menor amigo > 10^30" (OEIS A074902).
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sympy import nextprime  # noqa: E402

from core.motor import busca_limitada  # noqa: E402


def k_maximo(bound: int) -> int:
    """Menor k tal que (produto dos k menores primos >= 5)² > bound.
    Nenhum amigo <= bound pode ter omega >= esse k."""
    prod, k, p = 1, 0, 3
    while prod * prod <= bound:
        p = int(nextprime(p))
        prod *= p
        k += 1
    return k


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log10-bound", type=int, default=30,
                        help="B = 10**este_valor (padrão 30)")
    parser.add_argument("--somente-k", type=int, default=None,
                        help="varre apenas este omega (para paralelizar)")
    parser.add_argument("--p2-intervalo", type=str, default=None,
                        help="shard: restringe o 2º primo a 'lo:hi' (hi pode ser inf). "
                             "A união dos shards deve cobrir [7, inf) — a montagem do "
                             "certificado completo é responsabilidade de quem fragmenta.")
    parser.add_argument("--prefixo-intervalos", type=str, default=None,
                        help="shard multinível: intervalos 'lo:hi' separados por vírgula "
                             "para o 2º, 3º, ... primos (ex.: '7:7,11:13').")
    args = parser.parse_args()
    bound = 10 ** args.log10_bound

    def _parse_int(spec: str) -> tuple[int, int | None]:
        lo_s, hi_s = spec.split(":")
        return (int(lo_s), None if hi_s in ("inf", "") else int(hi_s))

    prefixo_intervalos = None
    if args.prefixo_intervalos:
        prefixo_intervalos = [_parse_int(s) for s in args.prefixo_intervalos.split(",")]
    elif args.p2_intervalo:
        prefixo_intervalos = [_parse_int(args.p2_intervalo)]
    p2_intervalo = prefixo_intervalos  # nome legado usado nos prints abaixo

    k_teto = k_maximo(bound)  # omega >= k_teto impossível para N <= bound
    print(f"B = 10^{args.log10_bound}; omega possível para N <= B: 10 .. {k_teto - 1}")
    if k_teto <= 10:
        print("B está abaixo do limite de assinatura (Teorema E da Fase 0); nada a varrer.")
        return

    ks = [args.somente_k] if args.somente_k is not None else list(range(10, k_teto))
    total_amigos = []
    for k in ks:
        t0 = time.perf_counter()
        stats = busca_limitada(k, bound, prefixo_intervalos=prefixo_intervalos)
        dt = time.perf_counter() - t0
        print(
            f"omega = {k}: varrido em {dt:.2f}s — nós={stats.nos_visitados}, "
            f"podas(min/max/produto)={stats.podas_min}/{stats.podas_max}/"
            f"{stats.podas_produto}, conjuntos_completos={stats.conjuntos_completos}, "
            f"assinaturas_testadas={stats.assinaturas_testadas}, "
            f"amigos={len(stats.amigos_encontrados)}"
        )
        total_amigos.extend(stats.amigos_encontrados)

    if total_amigos:
        print(f"!!! AMIGO(S) ENCONTRADO(S): {total_amigos} — reverifique com fatoração "
              "independente antes de qualquer alarde.")
        sys.exit(1)

    print()
    if args.somente_k is not None or p2_intervalo is not None:
        print(f"SHARD LIMPO: k={ks}, p2_intervalo={p2_intervalo}, B=10^{args.log10_bound}, "
              "0 amigos. O certificado completo exige a união dos shards cobrindo "
              "todos os omega em [10, k_teto) e todo o intervalo [7, inf) de p2.")
    else:
        print(f"CERTIFICADO (condicional a omega(N) >= 10): nenhum amigo de 10 com "
              f"N <= 10^{args.log10_bound}.")
        print("Rótulo: [PROVADO-CONDICIONAL: Teoremas A-D e Lemas/Fato 0 da Fase 0 + "
              "omega(N) >= 10 (arXiv:2310.15900) + correção do motor core/motor.py "
              "(passada adversarial em results/FASE_1.md §1.5) + correção de "
              "sympy.nextprime/primerange (cruzada com crivo próprio em "
              "tests/test_motor_crosscheck.py; o fecho ciclotômico NÃO é usado aqui)]")


if __name__ == "__main__":
    main()
