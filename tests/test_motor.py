"""Testes do motor de busca da Fase 1 (core/motor.py). Aritmética exata em tudo."""
from fractions import Fraction

import pytest
from sympy import divisor_sigma, factorint

import core.motor as motor
from core.motor import (
    ALVO,
    RamoNaoLimitado,
    busca_limitada,
    elimina_omega_k,
    expoentes_validos,
    I_pp,
    sigma_pp,
    sup_pp,
)


def test_sigma_pp_e_I_pp_contra_sympy():
    for p in (5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        for a in range(1, 11):
            assert sigma_pp(p, a) == divisor_sigma(p**a)
            assert I_pp(p, a) == Fraction(int(divisor_sigma(p**a)), p**a)
            assert I_pp(p, a) < sup_pp(p)


def _expoentes_brutos(p: int, S: frozenset[int], a_max: int) -> list[int]:
    """Referência independente do FECHO: a par com fatores de sigma(p^a) em S∪{3}."""
    permitidos = set(S) | {3}
    out = []
    for a in range(2, a_max + 1, 2):
        if all(q in permitidos for q in factorint(sigma_pp(p, a))):
            out.append(a)
    return out


def test_expoentes_validos_contra_forca_bruta():
    casos = [
        (5, frozenset({5, 7, 11, 13, 31})),      # sigma(5^2)=31: a=2 deve entrar
        (5, frozenset({5, 7, 11, 13, 23})),      # truque do 31: NENHUM a válido
        (5, frozenset({5, 11, 71})),             # sigma(5^4)=781=11*71: a=4 entra
        (7, frozenset({5, 7, 19})),              # sigma(7^2)=57=3*19: a=2 entra
        (7, frozenset({5, 7, 11, 13, 17})),      # 19 fora: a=2 não entra
        (13, frozenset({5, 7, 13, 61})),         # sigma(13^2)=183=3*61: a=2 entra
    ]
    for p, S in casos:
        validos = expoentes_validos(p, S)
        brutos = _expoentes_brutos(p, S, a_max=40)
        # igualdade na faixa testada: nem falta (completude) nem sobra (solidez)
        assert [a for a in validos if a <= 40] == brutos, (p, S, validos, brutos)
    # casos pontuais de valor:
    assert expoentes_validos(5, frozenset({5, 7, 11, 13, 31})) == [2]
    assert expoentes_validos(5, frozenset({5, 7, 11, 13, 23})) == []
    assert 4 in expoentes_validos(5, frozenset({5, 11, 71}))


def test_e_amigo_reconhece_o_proprio_10_e_rejeita_quadrados():
    assert motor._e_amigo({2: 1, 5: 1})          # sanidade da igualdade: N = 10
    assert not motor._e_amigo({5: 2, 7: 2})
    assert not motor._e_amigo({3: 2, 5: 2})      # o quase-amigo 225


def test_elimina_omega_1_a_5_reproduz_ward():
    for k in range(1, 5):
        stats = elimina_omega_k(k)
        assert stats.amigos_encontrados == []
    stats5 = elimina_omega_k(5)
    assert stats5.amigos_encontrados == []
    # estrutura da prova de Ward reproduzida: exatamente os três conjuntos
    # {5,7,11,13,17}, {5,7,11,13,19}, {5,7,11,13,23} chegam à fase de expoentes,
    # e todos morrem pelo FECHO em p = 5 (nenhum a válido: o "truque do 31")
    assert stats5.conjuntos_completos == 3
    assert stats5.conjuntos_mortos_por_fecho == 3
    assert stats5.assinaturas_testadas == 0


def test_omega_6_levanta_ramo_nao_limitado():
    # fronteira honesta do método: em {5,7,11,13,23} o produto p/(p-1) excede 9/5
    # e a poda de índice não limita o sexto primo — o motor NÃO certifica.
    with pytest.raises(RamoNaoLimitado):
        elimina_omega_k(6)


def test_busca_limitada_no_espaco_minimo():
    prod10 = 5 * 7 * 11 * 13 * 17 * 19 * 23 * 29 * 31 * 37
    # abaixo do quadrado do produto mínimo: nenhum conjunto cabe
    stats = busca_limitada(10, prod10 * prod10 - 1)
    assert stats.conjuntos_completos == 0
    assert stats.amigos_encontrados == []
    # exatamente o quadrado do produto mínimo: o conjunto mínimo cabe pelo teto de
    # produto, mas é morto pela PODA-MIN (I com expoentes mínimos já excede 9/5)
    stats2 = busca_limitada(10, prod10 * prod10)
    assert stats2.conjuntos_completos == 0
    assert stats2.amigos_encontrados == []
    assert stats2.podas_min >= 1


def test_busca_limitada_completude_com_alvo_plantado(monkeypatch):
    # completude do motor: com alvo I(N0) para N0 = (5*7*11)^2, a busca DEVE achar
    # exatamente a assinatura de N0 (testa DFS + enumeração de expoentes + igualdade)
    n0 = (5 * 7 * 11) ** 2
    alvo = Fraction(sigma_pp(5, 2) * sigma_pp(7, 2) * sigma_pp(11, 2), n0)
    monkeypatch.setattr(motor, "ALVO", alvo)
    stats = busca_limitada(3, n0)
    assert {5: 2, 7: 2, 11: 2} in stats.amigos_encontrados
    assert len(stats.amigos_encontrados) == 1


def test_shards_por_p2_cobrem_exatamente_a_varredura_inteira():
    # a união dos shards {p2 <= 11}, {13 <= p2 <= 29}, {p2 >= 31} deve testar
    # exatamente as mesmas assinaturas que a varredura íntegra (nem falta nem sobra)
    prod10 = 5 * 7 * 11 * 13 * 17 * 19 * 23 * 29 * 31 * 37
    bound = prod10 * prod10 * 10**4  # pequeno o suficiente para ser rápido
    inteira = busca_limitada(10, bound)
    shards = [
        busca_limitada(10, bound, p2_intervalo=(7, 11)),
        busca_limitada(10, bound, p2_intervalo=(13, 29)),
        busca_limitada(10, bound, p2_intervalo=(31, None)),
    ]
    assert sum(s.assinaturas_testadas for s in shards) == inteira.assinaturas_testadas
    assert sum(s.conjuntos_completos for s in shards) == inteira.conjuntos_completos
    assert all(s.amigos_encontrados == [] for s in shards)
    assert inteira.amigos_encontrados == []
    # partição em DOIS níveis (p2 e p3) também deve cobrir exatamente o total
    shards2 = [
        busca_limitada(10, bound, prefixo_intervalos=[(7, 7), (11, 11)]),
        busca_limitada(10, bound, prefixo_intervalos=[(7, 7), (13, None)]),
        busca_limitada(10, bound, prefixo_intervalos=[(11, None)]),
    ]
    assert sum(s.assinaturas_testadas for s in shards2) == inteira.assinaturas_testadas
    assert sum(s.conjuntos_completos for s in shards2) == inteira.conjuntos_completos
    assert all(s.amigos_encontrados == [] for s in shards2)


def test_enumeracao_de_expoentes_contra_forca_bruta():
    # contagem exaustiva independente das assinaturas 5^a * 7^b <= bound (a,b pares >=2)
    bound = 10**7
    esperado = 0
    a = 2
    while 5**a * 49 <= bound:
        b = 2
        while 5**a * 7**b <= bound:
            esperado += 1
            b += 2
        a += 2
    stats = motor.EstatisticasCota()
    motor._enumera_expoentes_cota([5, 7], bound, stats)
    assert stats.assinaturas_testadas == esperado > 0
    assert stats.amigos_encontrados == []
