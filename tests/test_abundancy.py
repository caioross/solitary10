from fractions import Fraction

from core.abundancy import (
    ALVO,
    abundancia,
    amigos_no_intervalo,
    e_amigo_de_10,
    sigma,
    sigma_do_quadrado,
    solitario_por_gcd,
)


def test_sigma_valores_classicos():
    assert sigma(1) == 1
    assert sigma(10) == 18
    assert sigma(25) == 31
    assert sigma(28) == 56  # número perfeito


def test_sigma_do_quadrado_coerente_com_sigma():
    for m in range(1, 500):
        assert sigma_do_quadrado(m) == sigma(m * m)


def test_abundancia_de_10():
    assert abundancia(10) == Fraction(9, 5) == ALVO


def test_pares_amigos_conhecidos():
    assert abundancia(6) == abundancia(28) == Fraction(2)        # perfeitos
    assert abundancia(30) == abundancia(140) == Fraction(12, 5)  # par amigo clássico


def test_criterio_gcd():
    for n in (2, 3, 4, 5, 7, 8, 9, 16, 21):
        assert solitario_por_gcd(n)
    assert not solitario_por_gcd(10)  # o critério não decide o 10


def test_e_amigo_de_10_exclui_o_proprio_10():
    assert not e_amigo_de_10(10)


def test_nenhum_amigo_de_10_ate_1e5():
    assert amigos_no_intervalo(ALVO, 100_000) == [10]
