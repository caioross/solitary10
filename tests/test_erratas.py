"""Testes das erratas à literatura (experiments/verifica_erratas.py, results/ERRATA.md).

Cada teste é uma verificação independente e exata (int / Fraction) de um defeito
catalogado. Os testes NÃO dependem de sympy nem de rede: reimplementam o que
precisam ou chamam o script de verificação.
"""
from fractions import Fraction

import pytest

from experiments.verifica_erratas import (
    I,
    X_r,
    conjunto_L,
    e1_lema_particao,
    e2_minimo_L,
    e3_otimo_teorema_110,
    e4_remark_37,
    e5_escopo_teorema_12,
    e6_caso12,
    parte_fixa,
    particoes,
    primo,
)


# ------------------------------------------------------------------ infraestrutura
def test_primo_e_particoes():
    assert [primo(i) for i in range(1, 9)] == [2, 3, 5, 7, 11, 13, 17, 19]
    assert sorted(particoes(4)) == sorted([(4,), (3, 1), (2, 2), (2, 1, 1), (1, 1, 1, 1)])
    assert all(sum(c) == 6 for c in particoes(6))


# -------------------- E1: Lema 2.3 de arXiv:2404.00624 = Lema 23 de arXiv:2409.04451
def test_lema_particao_falso_como_enunciado():
    """`a*n < sum a^{c_i}` falha na partição toda de 1's (vale igualdade)."""
    for a in (3, 5, 7):
        for n in (1, 2, 5):
            c = tuple([1] * n)
            assert a * n == sum(a ** ci for ci in c)  # igualdade, não `<`
            assert not a * n < sum(a ** ci for ci in c)


def test_lema_particao_versao_corrigida():
    """`a*n <= sum a^{c_i}`, com igualdade sse todo c_i = 1 — vale sempre."""
    for a in range(3, 8):
        for n in range(1, 9):
            for c in particoes(n):
                lhs, rhs = a * n, sum(a ** ci for ci in c)
                assert lhs <= rhs
                assert (lhs == rhs) == (set(c) == {1})


def test_e1_exaustivo():
    r = e1_lema_particao(a_max=6, n_max=7, verboso=False)
    assert r["falhas"] > 0 and r["todas_igualdade"] and r["todas_uns"]


# ------------------- E2: Lema 3.6 de arXiv:2404.00624 = Lema 24 de arXiv:2409.04451
@pytest.mark.parametrize("a", [1, 2, 3, 4, 5, 6])
def test_minimo_de_L_e_atingido(a):
    L = conjunto_L(2 * a - 1, 5)
    assert min(L) == 8 * a - 4          # enunciado do lema: correto
    assert (8 * a - 4) in L             # e ATINGIDO -> a prova exibida (estrita) não vale
    e2_minimo_L(a_max=5, verboso=False)


# --------------------------------- E3/E4: Teorema 1.10 e Remark 3.7 de arXiv:2404.00624
def test_teorema_110_e_o_otimo_da_relaxacao():
    """Nenhuma folga: o ótimo da relaxação usada na prova é exatamente 2w+6a-4."""
    assert e3_otimo_teorema_110(a_max=5, w_max=12, verboso=False)["pares"] > 0


def test_remark_37_off_by_one():
    """Da desigualdade exibida segue +2a-2; a eq. (7) do paper afirma +2a-1."""
    for a in range(1, 6):
        for w in range(2, 15):
            om = w + 2 * a - 2
            assert 2 * a + 2 * om >= 2 * w + 6 * a - 4   # satisfaz o exibido
            assert om < w + 2 * a - 1                    # viola a eq. (7)
    assert e4_remark_37(a_max=5, w_max=12, verboso=False)["testemunhas"] > 0


def test_corolario_111_expoente_corrigido():
    """Omega(m) <= K com a eq. (7) corrigida dá w(N) <= K-2a+2 (não K-2a+1)."""
    for a in range(1, 6):
        for K in range(2 * a, 30):
            # maior w(N) compatível com Omega(m) >= w(N)+2a-2 e Omega(m) <= K
            w_max = K - 2 * a + 2
            assert w_max + 2 * a - 2 <= K
            assert (w_max + 1) + 2 * a - 2 > K   # K-2a+3 já é incompatível


# ------------------------------------------ E5: Teorema 1.2 de arXiv:2412.02701
@pytest.mark.parametrize("r", list(range(2, 13)))
def test_identidade_parte_fixa_vezes_Xr(r):
    assert parte_fixa(r) * X_r(r) == Fraction(9, 5)


def test_Xr_maior_que_um_apenas_ate_r5():
    assert all(X_r(r) > 1 for r in range(2, 6))
    assert all(X_r(r) < 1 for r in range(6, 13))
    assert X_r(6) == Fraction(82944, 85085)


def test_nenhum_par_AB_admissivel_para_r_maior_igual_6():
    """Passo final exige 1 + B/A < X_r; com X_r < 1 isso é impossível."""
    for r in range(6, 10):
        x = X_r(r)
        for A in range(1, 60):
            for B in range(1, 60):
                assert not (1 + Fraction(B, A) < x)


def test_parte_fixa_F6_excede_alvo():
    """Em r = 6 a parte fixa sozinha já supera 9/5 — a contradição não fecha."""
    assert parte_fixa(6) == Fraction(17017, 9216)
    assert parte_fixa(6) > Fraction(9, 5)
    assert all(parte_fixa(r) < Fraction(9, 5) for r in range(2, 6))


def test_e5_escopo():
    linhas = e5_escopo_teorema_12(r_max=10, verboso=False)["linhas"]
    assert [v for r, _, v in linhas if r <= 5] == [True] * 4
    assert [v for r, _, v in linhas if r >= 6] == [False] * 5


# ------------------------------------------ E6: Caso-12 do Teorema 1.2 de 2404.00624
def test_caso12_typo_sem_consequencia():
    assert Fraction(381, 361) == I(19, 2)
    assert I(23, 2) == Fraction(553, 529)
    p = I(5, 4) * I(7, 2) * I(11, 2) * I(13, 2) * I(23, 2)
    q = I(5, 2) * I(7, 2) * I(11, 2) * I(13, 2) * I(23, 2) * I(31, 2)
    assert p > Fraction(9, 5) and q > Fraction(9, 5)
    e6_caso12(verboso=False)
