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


# ---------------------------------------------------------------------------
# Bloco 4 — valuações diretas (sem ordens), gate de tamanho, divisores
# ---------------------------------------------------------------------------

def test_v_q_sigma_direto_contra_valuacao_direta_exaustiva_inclusive_q_2():
    from core.cadeias import v_q_sigma_direto
    for p in PRIMOS:
        for q in [2] + PRIMOS:
            if q == p:
                continue
            for a in range(0, 21):
                assert v_q_sigma_direto(q, p, a) == v_p(q, sigma_pp(p, a)), (q, p, a)


def test_v_q_de_p_ordem_menos_1_modular_bate_com_a_potencia_inteira():
    from core.cadeias import _v_q_de_p_ordem_menos_1, ordem_mod
    for p in PRIMOS:
        for q in PRIMOS + [3221, 19531]:
            if q == p:
                continue
            assert _v_q_de_p_ordem_menos_1(q, p) == v_p(q, p ** ordem_mod(p, q) - 1), (q, p)


def test_sigma_fecha_em_nao_materializa_expoentes_enormes():
    # conjunto real de k = 7 (Bloco 4): 167140584971 - 1 = 2·5·16714058497 com o
    # cofator primo, logo ord_r(p) ~ 10^10 e a+1 = ord_r(p) é candidato legítimo
    # do fecho; a reconstrução tem de responder False pelo gate de tamanho sem
    # calcular p^{a+1} (que teria 10^10·log2(p) bits). Tempo < 1 s.
    import time
    S = frozenset({5, 11, 31, 71, 181, 1741, 167140584971})
    t = time.perf_counter()
    assert not sigma_fecha_em(5, 16714058497 - 1, S)
    assert not sigma_fecha_em(11, 83570292485 - 1, S)
    assert expoentes_validos_ordens(5, S) == [2, 4, 14]
    assert expoentes_validos_ordens(11, S) == []
    assert time.perf_counter() - t < 5


def test_gate_de_tamanho_e_so_atalho():
    # onde a potência é calculável, a resposta com e sem o gate é a mesma
    from core.cadeias import v_q_sigma_direto
    casos = [(5, frozenset({5, 7, 11, 13, 31})), (7, frozenset({5, 7, 19})),
             (13, frozenset({5, 7, 13, 61})), (5, frozenset({5, 11, 71}))]
    for p, S in casos:
        for a in range(2, 60, 2):
            prod = 1
            for q in sorted(S | {3}):
                if q != p:
                    prod *= q ** v_q_sigma_direto(q, p, a)
            assert sigma_fecha_em(p, a, S) == (prod == sigma_pp(p, a)), (p, a)


def test_divisores_impares_por_fatoracao_batem_com_divisao_por_tentativa():
    from core.cadeias import _divisores_impares_maiores_que_1

    def bruto(m):
        return {d for d in range(3, m + 1, 2) if m % d == 0}

    for m in list(range(1, 400, 2)) + [3455, 10365, 76293945, 3**5 * 5**3]:
        assert set(_divisores_impares_maiores_que_1(m)) == bruto(m), m
