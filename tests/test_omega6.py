"""Testes do certificador omega = 6 (core/omega6.py)."""
from fractions import Fraction

import pytest

import core.omega6 as omega6
from core.motor import I_pp
from core.omega6 import (
    NaoCertificavel,
    Stats6,
    _parte_impar_divisores,
    _prefixos_c5,
    _ramo_ii_pinagem,
    certifica_omega6,
)


def _I(assinatura: dict[int, int]) -> Fraction:
    x = Fraction(1)
    for p, a in assinatura.items():
        x *= I_pp(p, a)
    return x


def test_parte_impar_divisores():
    assert _parte_impar_divisores(22) == {11}
    assert _parte_impar_divisores(10) == {5}
    assert _parte_impar_divisores(12) == {3}
    assert _parte_impar_divisores(45) == {3, 5, 9, 15, 45}
    assert _parte_impar_divisores(8) == set()
    assert _parte_impar_divisores(2) == set()


def test_prefixos_c5_contem_os_criticos():
    prefixos = [tuple(c) for c, _, _ in _prefixos_c5()]
    assert (5, 7, 11, 13, 23) in prefixos          # o RamoNaoLimitado do Bloco 1
    assert (5, 7, 11, 13, 29) in prefixos          # a cadeia longa da literatura
    assert all(c[0] == 5 and list(c) == sorted(c) for c in prefixos)
    assert len(prefixos) < 500


def test_ramo_ii_so_para_o_alvo_real(monkeypatch):
    monkeypatch.setattr(omega6, "ALVO", Fraction(2))
    with pytest.raises(NaoCertificavel):
        _ramo_ii_pinagem([5, 7, 11, 13, 23], Stats6())


def test_pinagem_no_prefixo_critico():
    # derivação mecânica esperada para {5,7,11,13,23} (conferida à mão em
    # results/FASE_1.md, Bloco 2):
    #  CASO A (11 alimenta o 5): ord_P(11) = 5 => P | Phi_5(11) = 5·3221 => P = 3221
    #  CASO B (só P alimenta): v5cap = 1 => a1 = 2 => sigma(25) = 31 => P = 31
    # ambos os conjuntos completos morrem no fecho, e quem os mata é o primo 7
    # (verificado em test_quem_mata_os_conjuntos_do_ramo_ii)
    stats = Stats6()
    _ramo_ii_pinagem([5, 7, 11, 13, 23], stats)
    assert sorted(stats.pins_testados) == [31, 3221]
    assert stats.conjuntos_completos == 2
    assert stats.amigos == []


def test_planted_ramo_i_todos_prefixos(monkeypatch):
    # alvo plantado com I(N0) > max prod_sup(C5) = I-sup de {5,7,11,13,17}:
    # TODOS os prefixos caem no ramo (i) e a assinatura tem de ser encontrada
    alvo_assin = {5: 2, 7: 2, 11: 2, 13: 2, 17: 2, 19: 2}
    monkeypatch.setattr(omega6, "ALVO", _I(alvo_assin))
    stats = certifica_omega6()
    assert alvo_assin in stats.amigos
    assert stats.prefixos_ramo_ii == 0
    for amigo in stats.amigos:
        assert _I(amigo) == _I(alvo_assin)


def test_planted_ramo_i_com_expoente_alto(monkeypatch):
    # expoente 4 no sexto primo: o fecho de ordens tem de encontrá-lo
    alvo_assin = {5: 2, 7: 2, 11: 2, 13: 2, 17: 2, 19: 4}
    monkeypatch.setattr(omega6, "ALVO", _I(alvo_assin))
    stats = certifica_omega6()
    assert alvo_assin in stats.amigos


def test_planted_ramo_i_com_expoente_alto_no_primeiro(monkeypatch):
    # expoente 4 no 5: exercita a1 != 2 e o orçamento v5 generalizado
    alvo_assin = {5: 4, 7: 2, 11: 2, 13: 2, 17: 2, 19: 2}
    monkeypatch.setattr(omega6, "ALVO", _I(alvo_assin))
    stats = certifica_omega6()
    assert alvo_assin in stats.amigos


def test_guarda_caso_a_pin_indisponivel():
    # honestidade do CASO A: se 5 JÁ é ordem conhecida da base q ≡ 1 (mod 5),
    # o pin não existe e nada pode ser certificado. Alcançável: em
    # C5 = [5,7,11,13,31], ord_11(31) = 5, logo 5 ∈ D_31.
    with pytest.raises(NaoCertificavel, match="ordem conhecida"):
        _ramo_ii_pinagem([5, 7, 11, 13, 31], Stats6())


def test_guarda_caso_b_sem_pin():
    # honestidade do CASO B: se sigma(5^{a1}) fecha inteiramente em C5 ∪ {3},
    # não sobra fator para pinar P. Alcançável em C5 = [5,7,13,17,31]
    # (a1 = 2 e sigma(25) = 31 ∈ C5).
    with pytest.raises(NaoCertificavel, match="sem pin"):
        _ramo_ii_pinagem([5, 7, 13, 17, 31], Stats6())


def test_prefixos_c5_recusa_em_vez_de_travar(monkeypatch):
    # o laço de candidatos só termina se prod_sup < ALVO ESTRITAMENTE; para um
    # alvo dentro da janela (prod_min, prod_sup] do nó [5,7,11,13] o método TEM de
    # levantar NaoCertificavel (falha honesta) em vez de rodar para sempre.
    # Sem o raise, esta chamada não retornaria nunca.
    alvo = _I({5: 2, 7: 2, 11: 2, 13: 2, 10007: 2, 10009: 2})
    assert I_pp(5, 2) * I_pp(7, 2) * I_pp(11, 2) * I_pp(13, 2) < alvo
    monkeypatch.setattr(omega6, "ALVO", alvo)
    with pytest.raises(NaoCertificavel, match="nao limita o proximo primo"):
        _prefixos_c5()


def test_quem_mata_os_conjuntos_do_ramo_ii():
    # correção de uma afirmação errada da primeira redação: NÃO é o 13 que fica
    # sem expoente nos dois conjuntos do ramo (ii) — o 13 tem ordem ímpar
    # (ord_23(13) = 11) e m = 11 é candidato legítimo, morto só na reconstrução.
    # Quem mata os dois conjuntos é o primo 7.
    from core.cadeias import expoentes_validos_ordens, ordens_impares

    for P in (31, 3221):
        S = frozenset({5, 7, 11, 13, 23, P})
        assert expoentes_validos_ordens(7, S) == [], P          # o matador
        assert 11 in ordens_impares(13, S)                      # 13 TEM ordem ímpar
        assert expoentes_validos_ordens(13, S) == [], P         # mas não fecha
    # e o 5 ainda tem expoente válido em {5,7,11,13,23,31}: a cadeia só fecha no 7
    assert expoentes_validos_ordens(5, frozenset({5, 7, 11, 13, 23, 31})) == [2]
