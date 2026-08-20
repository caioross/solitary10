"""Limite inferior exato para um amigo N de 10, a partir das restrições da Fase 0.

Restrições usadas (com seus rótulos — ver results/FASE_0.md):
  [PROVADO]             N é ímpar, quadrado perfeito, 25 | N, menor primo divisor = 5.
                        (Teoremas A-D da Fase 0; logo todo primo de N é >= 5 e todo
                        expoente é par >= 2.)
  [CONDICIONAL-1]       omega(N) >= 10 (arXiv:2310.15900, Thackeray; verificado por
                        leitura, NÃO re-derivado neste projeto).
  [CONDICIONAL-2]       em N = 5^{2a}·m^2 com gcd(m, 5) = 1, m não é livre de
                        quadrados, i.e. existe primo p != 5 com p^4 | N
                        (arXiv:2404.00624, Teorema 1.9; verificado por leitura).

LIMITE BASE (usa [PROVADO] + [CONDICIONAL-1]):
    Se q_1 < ... < q_k são os primos de N (k >= 10, todos >= 5) com expoentes e_j:
      N = prod q_j^{e_j}  >=  prod_{j<=10} q_j^{e_j}   (fatores extras > 1)
                          >=  prod_{j<=10} q_j^2        (e_j par >= 2)
                          >=  prod_{j<=10} s_j^2        (q_j >= s_j, o j-ésimo menor
                                                          primo >= 5, pois os q_j são
                                                          primos distintos >= 5)
    => N >= (5·7·11·13·17·19·23·29·31·37)^2.
    Este limite NÃO depende de nenhuma congruência: congruências só poderiam FORÇAR
    primos/expoentes maiores e, portanto, só elevariam o limite.

LIMITE AFIADO (acrescenta [CONDICIONAL-2]):
    A configuração mínima do limite base tem todos os expoentes = 2, i.e.
    m = 7·11·...·37 livre de quadrados — proibida pelo Teorema 1.9 de 2404.00624.
    Logo algum primo p != 5 tem expoente >= 4; o custo mínimo é p = 7 (fator 7^2 = 49):
    => N >= 49 · (5·7·...·37)^2.
    (A mesma configuração com expoente 4 no 7 já satisfaz as demais restrições
    conhecidas — witnesses verificados abaixo — então nenhuma outra restrição da
    tabela eleva o limite de graça além disso.)

Aritmética 100% inteira; floats aparecem apenas em exibição aproximada, nunca em
comparação ou passo que sustente a afirmação.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

PRIMOS_MIN = [5, 7, 11, 13, 17, 19, 23, 29, 31, 37]  # 10 menores primos >= 5


def eh_primo(n: int) -> bool:
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True


def main() -> None:
    assert all(eh_primo(p) for p in PRIMOS_MIN)
    assert len(PRIMOS_MIN) == 10 and PRIMOS_MIN == sorted(PRIMOS_MIN)
    # não há primo >= 5 fora da lista que seja menor que max(PRIMOS_MIN)
    assert [p for p in range(5, 38) if eh_primo(p)] == PRIMOS_MIN

    # witnesses das congruências conhecidas dentro da configuração mínima
    # (mostram que as congruências NÃO forçam primos fora do conjunto mínimo;
    #  o limite base vale independentemente delas):
    w_mod10 = [p for p in PRIMOS_MIN if p % 10 == 1]   # arXiv:2404.00624
    w_mod6 = [p for p in PRIMOS_MIN if p % 6 == 1]     # arXiv:2404.00624
    w_mod3 = [p for p in PRIMOS_MIN if p % 3 == 1]     # Ward: expoente 2 ≡ 2 (mod 6) ok
    # Corolário 1.5 de 2404.00624 com a = 1: 2a+1 = 3 => precisa p | N com ordem
    # ímpar de 5 mod p igual a 3, i.e. p | sigma(5^2) = 31 => p = 31, que está no
    # conjunto mínimo:
    assert 31 in PRIMOS_MIN and (5**3 - 1) // 4 == 31

    prod = 1
    for p in PRIMOS_MIN:
        prod *= p
    limite_base = prod * prod          # todo expoente par >= 2 => N >= (prod s_j)^2
    limite_afiado = 49 * limite_base   # + Teorema 1.9 de 2404.00624 (fator minimo 7^2)

    # comparações (todas exatas):
    bound_2504 = 625 * 9 ** (10 - 3)  # N > 625·9^(omega-3), omega = 10 (arXiv:2504.08295)
    varredura_estrutural = 10**12      # seção 2 da Fase 0

    print("Conjunto mínimo de primos:", PRIMOS_MIN)
    print(f"  witnesses ≡ 1 (mod 10): {w_mod10}; ≡ 1 (mod 6): {w_mod6}; ≡ 1 (mod 3): {w_mod3}")
    print(f"Produto dos 10 primos: {prod}")
    print(f"LIMITE BASE:   N >= {limite_base}")
    print(f"  ({len(str(limite_base))} dígitos; aproximadamente {limite_base:.4e})")
    print("  Rótulo: [PROVADO-CONDICIONAL: Teoremas A-D da Fase 0 (provados) + "
          "omega(N) >= 10 (arXiv:2310.15900)]")
    print(f"LIMITE AFIADO: N >= {limite_afiado}")
    print(f"  ({len(str(limite_afiado))} dígitos; aproximadamente {limite_afiado:.4e})")
    print("  Rótulo: [PROVADO-CONDICIONAL: idem + Teorema 1.9 de arXiv:2404.00624 "
          "(m não é livre de quadrados)]")
    print("Comparações:")
    print(f"  bound de arXiv:2504.08295 (omega=10): N > {bound_2504}  ({bound_2504:.2e}) — mais fraco")
    print(f"  varredura estrutural da Fase 0:       N > {varredura_estrutural}  — mais fraco")
    print("  alegação NÃO certificada da literatura (OEIS A074902, citada na conclusão")
    print("  de arXiv:2404.00624): menor amigo > 10^30 — mais forte, porém sem")
    print("  certificação publicada; NÃO usar como hipótese.")
    assert limite_afiado > limite_base > varredura_estrutural > bound_2504


if __name__ == "__main__":
    main()
