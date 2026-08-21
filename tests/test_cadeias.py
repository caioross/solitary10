"""Testes de core/cadeias.py — fórmula de valuação, f_p^q, fecho por ordens."""
from sympy import primerange

from core.cadeias import (
    _candidatos_m,
    expoentes_validos_ordens,
    f_menor_ordem_impar,
    ordens_impares,
    sigma_fecha_em,
    v_p,
    v_q_sigma,
)
from core.motor import expoentes_validos, sigma_pp

PRIMOS = list(primerange(3, 40))


def test_v_q_sigma_contra_valuacao_direta_exaustiva():
    for p in PRIMOS:
        for q in PRIMOS:
            if q == p:
                continue
            for a in range(1, 21):
                assert v_q_sigma(q, p, a) == v_p(q, sigma_pp(p, a)), (q, p, a)


def test_v3_so_contribui_para_base_1_mod_3_com_expoente_par():
    # mecanismo do orçamento v3 = 2: com a par, v_3(sigma(p^a)) = v_3(a+1) se
    # p ≡ 1 (mod 3), e 0 se p ≡ 2 (mod 3)
    for p in (5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43):
        for a in range(2, 30, 2):
            esperado = v_p(3, a + 1) if p % 3 == 1 else 0
            assert v_q_sigma(3, p, a) == esperado


def test_v5_so_contribui_para_base_1_mod_5_com_expoente_par():
    for p in (7, 11, 13, 17, 19, 23, 29, 31, 37, 41):
        for a in range(2, 30, 2):
            esperado = v_p(5, a + 1) if p % 5 == 1 else 0
            assert v_q_sigma(5, p, a) == esperado


def test_f_contra_tabela4_de_2404_00624():
    # amostras verificadas na nota de leitura (f_p^q: p | sigma(q^{2a}) sse f | 2a+1)
    tabela = {
        (31, 5): 3, (11, 5): 5, (71, 5): 5, (19, 5): 9, (829, 5): 9,
        (59, 5): 29, (35671, 5): 29, (3221, 11): 5, (61, 13): 3,
        (127, 19): 3, (67, 29): 3, (37, 7): 9,
    }
    for (p, q), f in tabela.items():
        assert f_menor_ordem_impar(p, q) == f, (p, q)


def test_f_equivale_a_v_q_sigma():
    for q in (5, 7, 11, 13):
        for p in (3, 7, 11, 13, 19, 31, 37, 61, 71):
            if p == q:
                continue
            f = f_menor_ordem_impar(p, q)
            for a in range(2, 40, 2):
                divide = v_q_sigma(p, q, a) > 0
                if f is None:
                    assert not divide, (p, q, a)
                else:
                    assert divide == ((a + 1) % f == 0), (p, q, a, f)


def _strip(n: int, permitidos: set[int]) -> int:
    for q in permitidos:
        while n % q == 0:
            n //= q
    return n


def test_sigma_fecha_em_contra_strip_bruto():
    casos = [
        (5, frozenset({5, 7, 11, 13, 31})),
        (5, frozenset({5, 7, 11, 13, 23})),
        (5, frozenset({5, 11, 71})),
        (7, frozenset({5, 7, 19})),
        (13, frozenset({5, 7, 13, 61})),
    ]
    for p, S in casos:
        permitidos = set(S) | {3}
        for a in range(2, 30, 2):
            assert sigma_fecha_em(p, a, S) == (_strip(sigma_pp(p, a), permitidos) == 1)


def test_expoentes_validos_ordens_equivale_ao_fecho_ciclotomico():
    # duas implementações independentes (ciclotômicos+factorint vs ordens+reconstrução)
    casos = [
        (5, frozenset({5, 7, 11, 13, 31})),
        (5, frozenset({5, 7, 11, 13, 23})),
        (5, frozenset({5, 11, 71})),
        (7, frozenset({5, 7, 19})),
        (7, frozenset({5, 7, 11, 13, 17})),
        (13, frozenset({5, 7, 13, 61})),
        (5, frozenset({5, 7, 11, 13, 17})),
        (5, frozenset({5, 7, 11, 13, 19})),
    ]
    for p, S in casos:
        assert expoentes_validos_ordens(p, S) == expoentes_validos(p, S), (p, S)


def test_candidatos_m_filtra_divisores():
    assert _candidatos_m({3, 5, 9, 15}) == [3, 5, 9, 15]
    assert _candidatos_m({9, 15}) == []          # 3 | 9 e 3 | 15, mas 3 fora de D
    assert _candidatos_m({3, 9, 27}) == [3, 9, 27]
    assert _candidatos_m({5, 25}) == [5, 25]
    assert _candidatos_m({15}) == []             # 3 e 5 fora de D
    assert _candidatos_m(set()) == []


def test_ordens_grandes_nao_podem_ser_truncadas():
    # TERCEIRA CEGUEIRA pega pela revisão: truncar ordens_impares (ex.: o < 100)
    # ou a lista de expoentes por tamanho produz FALSOS KILLS em massa sem que
    # nenhum teste reclame. A execução real usa candidatos m de até ~10^4:
    # ancorar ordens grandes concretas do conjunto extremo do ramo (i).
    S = frozenset({5, 7, 11, 13, 29, 20731})
    assert 3455 in ordens_impares(5, S)
    assert 2073 in ordens_impares(11, S)
    assert 10365 in ordens_impares(13, S)
    # e o filtro de divisores tem de aceitar m grande com todos os divisores em D
    assert _candidatos_m({3, 5, 15, 691, 2073, 3455, 10365}) == [3, 5, 15, 691, 2073, 3455, 10365]


def test_v_q_sigma_recusa_q_par():
    import pytest
    with pytest.raises(ValueError, match="ímpar"):
        v_q_sigma(2, 5, 3)
