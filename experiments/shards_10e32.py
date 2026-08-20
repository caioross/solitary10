"""Reprodução integral do certificado B = 10^32 por união de shards (Fase 1, Bloco 1).

Executa SEQUENCIALMENTE a mesma partição usada nas execuções paralelas registradas em
results/FASE_1.md §1.4, e monta o certificado ao final. Antes de rodar, VERIFICA
programaticamente que a partição cobre o espaço:
  - omega em {10, 11, 12} cobre tudo (k_maximo(10^32) = 13);
  - os intervalos de p2 particionam [7, inf) sem buraco nem sobreposição;
  - dentro de p2 = 7, os intervalos de p3 particionam [11, inf).

Tempo total esperado: ~15-20 min em CPU única. Toda aritmética exata.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sympy import nextprime  # noqa: E402

from core.motor import busca_limitada  # noqa: E402
from experiments.cota_certificada import k_maximo  # noqa: E402

BOUND = 10**32

# partição usada no Bloco 1 (idêntica às execuções registradas em FASE_1.md §1.4)
SHARDS_K10 = [
    [(7, 7), (11, 11)],
    [(7, 7), (13, 13)],
    [(7, 7), (17, 17)],
    [(7, 7), (19, 23)],
    [(7, 7), (29, None)],
    [(11, 13)],
    [(17, 31)],
    [(37, None)],
]


def _verifica_particao(intervalos: list[tuple[int, int | None]], inicio: int) -> None:
    """Intervalos ordenados particionam [inicio, inf) sobre PRIMOS: o primeiro começa
    em `inicio`, cada um termina exatamente onde o próximo começa (sem primo entre
    hi e lo seguinte), e o último é aberto."""
    assert intervalos[0][0] == inicio
    for (lo, hi), (lo2, _) in zip(intervalos, intervalos[1:]):
        assert hi is not None and int(nextprime(hi)) == lo2, (hi, lo2)
    assert intervalos[-1][1] is None


def main() -> None:
    assert k_maximo(BOUND) == 13  # omega >= 13 impossível para N <= 10^32

    # cobertura da partição de p2 (nível 1) e de p3 dentro de p2 = 7 (nível 2)
    nivel1 = [s[0] for s in SHARDS_K10 if len(s) == 1] + [(7, 7)]
    nivel1.sort()
    _verifica_particao(nivel1, 7)
    nivel2 = sorted(s[1] for s in SHARDS_K10 if len(s) == 2)
    _verifica_particao(nivel2, 11)

    total_assinaturas = 0
    amigos = []
    for prefixo in SHARDS_K10:
        t0 = time.perf_counter()
        stats = busca_limitada(10, BOUND, prefixo_intervalos=prefixo)
        print(f"omega=10 shard {prefixo}: {time.perf_counter()-t0:.1f}s, "
              f"assinaturas={stats.assinaturas_testadas}, amigos={len(stats.amigos_encontrados)}",
              flush=True)
        total_assinaturas += stats.assinaturas_testadas
        amigos += stats.amigos_encontrados
    for k in (11, 12):
        stats = busca_limitada(k, BOUND)
        print(f"omega={k} íntegro: assinaturas={stats.assinaturas_testadas}, "
              f"amigos={len(stats.amigos_encontrados)}", flush=True)
        total_assinaturas += stats.assinaturas_testadas
        amigos += stats.amigos_encontrados

    print(f"\nTotal de assinaturas testadas: {total_assinaturas}")
    if amigos:
        print(f"!!! AMIGO(S): {amigos} — reverifique com fatoração independente.")
        sys.exit(1)
    print("CERTIFICADO (condicional a omega(N) >= 10): nenhum amigo de 10 com N <= 10^32.")
    print("Rótulo: como em cota_certificada.py (ver results/FASE_1.md §1.4).")


if __name__ == "__main__":
    main()
