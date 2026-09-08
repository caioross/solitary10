"""Testes do certificador recursivo (core/omega_k.py)."""
from fractions import Fraction

import pytest

import core.omega6 as omega6
import core.omega_k as omega_k
from core.motor import I_pp
from core.omega_k import NaoCertificavel, StatsK, _pinagem, certifica_omega


def _I(assinatura: dict[int, int]) -> Fraction:
    x = Fraction(1)
    for p, a in assinatura.items():
        x *= I_pp(p, a)
    return x


def test_k_ate_5_eliminados():
    for k in range(1, 6):
        st = certifica_omega(k)
        assert st.amigos == [], k
        assert st.assinaturas_testadas == 0, k


def test_k6_pinagem_primeiro_reduz_a_arvore_e_mantem_o_veredito():
    st = certifica_omega(6)
    s6 = omega6.certifica_omega6()
    assert st.amigos == [] and s6.amigos == []
    # o Bloco 2 (índice primeiro) testou 2745 conjuntos; com a PARTIÇÃO POR
    # ORÇAMENTOS em todo nó (a1 <= 1 + 5·4 = 21 na raiz força 31, {11,71}, 19531, ...
    # para dentro de C cedo; v3 = 2 e o índice matam o resto): 27 conjuntos, 57 nós.
    assert s6.conjuntos_completos == 2745
    assert st.conjuntos_completos == 27
    assert st.nos == 57
    assert st.assinaturas_testadas == 0
    # o primeiro pin é o a1 = 2 forçando 31 na raiz
    assert st.pins[0] == ((5,), "a1=2", (31,))
    assert ((5,), "a1=4", (11, 71)) in st.pins


def test_pinagem_e_particao_completa_em_qualquer_no():
    # solidez da estratégia "pinagem primeiro": a lista de pins da raiz enumera
    # TODO a1 par de 2 a 1 + (c5+s)(c5+s-1) = 21 (s = 5, c5 = 0) — nenhum a1 é
    # pulado (os ausentes só podem ser casos mortos: > s primos novos)
    st = StatsK()
    pins = _pinagem([5], 5, 5, st)
    a1s = sorted(int(caso[3:]) for _, caso, _ in st.pins)
    assert a1s == [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
    assert all(1 <= len(p) <= 5 and min(p) > 5 for p in pins)


def test_cota_universal_de_a1_no_prefixo_critico_com_dois_slots():
    # C = {5,7,11,13,23}, s = 2: c5 = 1 (só o 11), kcap = 2, a1_max = 1 + 3·2 = 7
    # => a1 em {2, 4, 6} => sigma(25) = 31, sigma(5^4) = 11·71 (11 já em C),
    # sigma(5^6) = 19531 (primo): três pins unitários, todos > 23.
    st = StatsK()
    pins = _pinagem([5, 7, 11, 13, 23], 2, 23, st)
    assert pins == [(31,), (71,), (19531,)]


def test_pinagem_so_para_o_alvo_real(monkeypatch):
    monkeypatch.setattr(omega6, "ALVO", Fraction(2))
    with pytest.raises(NaoCertificavel):
        _pinagem([5, 7, 11, 13, 23], 1, 23, StatsK())


def test_planted_k7_ramo_i(monkeypatch):
    # alvo plantado com I(N0) acima de qualquer prod_sup de 6 primos (máximo
    # {5,7,11,13,17,19} = 1.949): todos os nós caem no ramo (i) e a assinatura
    # de 7 primos tem de ser encontrada (a pinagem nunca é acionada).
    assin = {5: 2, 7: 2, 11: 2, 13: 2, 17: 2, 19: 2, 23: 2}
    alvo = _I(assin)
    assert alvo > Fraction(5, 4) * Fraction(7, 6) * Fraction(11, 10) * Fraction(13, 12) \
        * Fraction(17, 16) * Fraction(19, 18)
    monkeypatch.setattr(omega6, "ALVO", alvo)   # fonte única: omega_k lê omega6.ALVO
    st = certifica_omega(7)
    assert assin in st.amigos
    assert st.particoes == 0
    for amigo in st.amigos:
        assert _I(amigo) == alvo


def test_planted_k7_com_expoente_4_no_ultimo(monkeypatch):
    assin = {5: 2, 7: 2, 11: 2, 13: 2, 17: 2, 19: 2, 23: 4}
    alvo = _I(assin)
    monkeypatch.setattr(omega6, "ALVO", alvo)
    st = certifica_omega(7)
    assert assin in st.amigos


def test_k7_fronteira_honesta_e_caracterizada():
    # Bloco 3 NÃO certifica omega = 7: a partição por orçamentos (5 e 3) deixa aberto
    # exatamente o estado abaixo, e o índice não limita P (prod_sup = 1.8012 >= 9/5).
    # O teste congela a fronteira: se um dia passar a certificar, é notícia; se o
    # residual mudar, o relatório (FASE_1.md §3.4) tem de mudar junto.
    from core.omega_k import _expoentes_viaveis_unico
    with pytest.raises(NaoCertificavel, match=r"C=\[5, 7, 11, 13, 31, 331\], s=1"):
        certifica_omega(7)
    # no residual, P carrega os dois orçamentos e a_P + 1 = 15 é forçado
    assert _expoentes_viaveis_unico((5, 7, 11, 13, 31, 331)) == (3, 5, 11, 15)


def test_viabilidade_injetiva_mata_o_residual_do_181():
    # antes do emparelhamento injetivo, {5,7,11,13,31,181}+P ficava aberto com
    # 45 | a_P+1 "viável" porque 181 ≡ 1 (mod 45); mas 9 e 45 exigem testemunhas
    # DISTINTAS e só o 181 serve — 45 não é viável.
    from core.omega_k import _expoentes_viaveis_unico
    assert 45 not in _expoentes_viaveis_unico((5, 7, 11, 13, 31, 181))
    assert 15 in _expoentes_viaveis_unico((5, 7, 11, 13, 31, 181))
