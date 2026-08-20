"""Eliminação certificada de omega(N) = k para um amigo N de 10 (motor da Fase 1).

Reproduz computacionalmente, de forma independente e exata, o teorema de Ward (2008):
omega(N) >= 6. O motor (core/motor.py) usa somente restrições [PROVADO] da Fase 0
(Teoremas A-D) e podas por racionais exatos; ramos que a poda de índice não fecha
levantam RamoNaoLimitado e NADA é certificado para aquele k (sem certificação falsa).

Esperado (verificado em tests/test_motor.py e tests/test_motor_crosscheck.py):
  k = 1     eliminado pelo FECHO no conjunto completo {5};
  k = 2..4  eliminados na raiz (PODA-MAX: prod p/(p-1) dos menores primos <= 9/5);
  k = 5     três conjuntos completos ({5,7,11,13,17}, {..19}, {..23}), todos mortos
            pelo FECHO em p = 5 (sigma(5^a) exigiria primos fora do conjunto — a
            automação do "truque do 31" de Ward; nos dois primeiros, a poda-min
            de folha também bastaria — o fecho é o único indispensável no {..23});
  k = 6     RamoNaoLimitado (fronteira do método; exige propagação de divisibilidade,
            próximo bloco da Fase 1).
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.motor import RamoNaoLimitado, elimina_omega_k  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k-max", type=int, default=5)
    args = parser.parse_args()

    certificados = []
    for k in range(1, args.k_max + 1):
        t0 = time.perf_counter()
        try:
            stats = elimina_omega_k(k)
        except RamoNaoLimitado as exc:
            print(f"omega = {k}: NÃO CERTIFICADO — {exc}")
            break
        dt = time.perf_counter() - t0
        if stats.amigos_encontrados:
            print(f"!!! omega = {k}: AMIGO(S) ENCONTRADO(S): {stats.amigos_encontrados}")
            print("    Reverifique com fatoração independente antes de qualquer alarde.")
            sys.exit(1)
        certificados.append(k)
        print(
            f"omega = {k}: ELIMINADO em {dt:.2f}s — nós={stats.nos_visitados}, "
            f"podas_min={stats.podas_min}, podas_max={stats.podas_max}, "
            f"conjuntos_completos={stats.conjuntos_completos}, "
            f"mortos_por_fecho={stats.conjuntos_mortos_por_fecho}, "
            f"assinaturas_testadas={stats.assinaturas_testadas}"
        )

    if certificados == list(range(1, max(certificados, default=0) + 1)) and certificados:
        w = max(certificados) + 1
        print()
        print(f"CERTIFICADO: todo amigo de 10 tem omega(N) >= {w}.")
        print("Rótulo: [PROVADO-CONDICIONAL: Teoremas A-D e Lemas/Fato 0 da Fase 0 + "
              "teorema de Zsygmondy e identidade ciclotômica (clássicos, não "
              "re-derivados aqui) + correção do motor core/motor.py (passada "
              "adversarial em results/FASE_1.md §1.5) + correção de "
              "sympy.factorint/cyclotomic_poly/nextprime (superfície do certificado "
              "re-verificada sem sympy em tests/test_motor_crosscheck.py)]")


if __name__ == "__main__":
    main()
