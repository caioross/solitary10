"""Verificação numérica independente das provas da Fase 0 (results/FASE_0.md).

Independência: usa uma segunda implementação de sigma por divisão por tentativa,
sem sympy, e cruza com core.abundancy.sigma. Toda comparação é por inteiros ou
fractions.Fraction — nenhum float.
"""
from fractions import Fraction
from math import isqrt

from core.abundancy import sigma


def _sigma_trial(n: int) -> int:
    """sigma(n) por enumeração direta de divisores até sqrt(n). Sem fatoração."""
    total = 0
    d = 1
    while d * d <= n:
        if n % d == 0:
            total += d
            if d != n // d:
                total += n // d
        d += 1
    return total


def _divisores(n: int) -> list[int]:
    ds = []
    d = 1
    while d * d <= n:
        if n % d == 0:
            ds.append(d)
            if d != n // d:
                ds.append(n // d)
        d += 1
    return ds


def test_cross_check_sigma_trial_vs_sympy():
    for n in range(1, 20_001):
        assert _sigma_trial(n) == sigma(n)


def test_lema1_I_igual_soma_dos_inversos_dos_divisores():
    for n in range(1, 2_001):
        soma = sum(Fraction(1, d) for d in _divisores(n))
        assert soma == Fraction(_sigma_trial(n), n)


def test_lema2_monotonia_estrita_em_divisores_proprios():
    for n in range(2, 3_001):
        i_n = Fraction(_sigma_trial(n), n)
        for d in _divisores(n):
            if d < n:
                assert Fraction(_sigma_trial(d), d) < i_n


def test_lema3_crescimento_em_e_e_cota():
    for p in (3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        cota = Fraction(p, p - 1)
        anterior = Fraction(1)
        for e in range(1, 13):
            atual = Fraction(_sigma_trial(p**e), p**e)
            assert anterior < atual < cota
            anterior = atual


def test_paridade_de_sigma_para_impares():
    # mecanismo do Teorema B: n ímpar => (sigma(n) ímpar <=> n é quadrado)
    for n in range(1, 60_001, 2):
        eh_quadrado = isqrt(n) ** 2 == n
        assert (_sigma_trial(n) % 2 == 1) == eh_quadrado


def test_desigualdades_exatas_do_teorema_D():
    # I(3^4)*I(5^2) > 9/5  <=>  121*31*5 > 81*25*9
    assert Fraction(121, 81) * Fraction(31, 25) > Fraction(9, 5)
    assert 121 * 31 * 5 > 81 * 25 * 9
    # I(3^2)*I(5^4) > 9/5  <=>  13*781*5 > 9*625*9
    assert Fraction(13, 9) * Fraction(781, 625) > Fraction(9, 5)
    assert 13 * 781 * 5 > 9 * 625 * 9
    # I(3^2)*I(5^2)*I(13^2) > 9/5  <=>  13*31*183*5 > 9*25*169*9
    assert Fraction(13, 9) * Fraction(31, 25) * Fraction(183, 169) > Fraction(9, 5)
    assert 13 * 31 * 183 * 5 > 9 * 25 * 169 * 9
    # valores de sigma usados nos casos: sigma(9)=13, sigma(25)=31, sigma(81)=121,
    # sigma(625)=781, sigma(169)=183
    assert _sigma_trial(9) == 13
    assert _sigma_trial(25) == 31
    assert _sigma_trial(81) == 121
    assert _sigma_trial(625) == 781
    assert _sigma_trial(169) == 183


def test_mecanismo_teorema_A_multiplos_de_10_excedem():
    # todo múltiplo próprio de 10 tem I(n) > 9/5 (Lema 2); logo 5*sigma(n) > 9n
    for n in range(20, 300_001, 10):
        assert 5 * _sigma_trial(n) > 9 * n


def test_mecanismo_teorema_A_nenhum_par_satisfaz():
    # cobre os DOIS ramos da prova do Teorema A: pares múltiplos de 10 (I > 9/5)
    # e pares não múltiplos de 5 (5 ∤ N contradiz o Lema 4) — nenhum par resolve
    for n in range(2, 200_001, 2):
        if n != 10:
            assert 5 * _sigma_trial(n) != 9 * n


def test_mecanismo_teorema_D_quadrados_multiplos_de_15():
    # nenhum N = m^2 com 15 | m satisfaz a equação do amigo
    for m in range(15, 4_001, 15):
        n = m * m
        assert 5 * _sigma_trial(n) != 9 * n


def test_quase_amigo_225():
    assert _sigma_trial(225) == 403
    assert 5 * 403 == 2015 != 2025 == 9 * 225
