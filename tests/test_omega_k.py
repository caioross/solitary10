"""Testes do certificador recursivo (core/omega_k.py), Blocos 3 e 4."""
from fractions import Fraction

import pytest
from sympy import isprime, n_order

import core.omega6 as omega6
import core.omega_k as omega_k
from core.cadeias import expoentes_validos_ordens
from core.motor import I_pp, sigma_pp
from core.omega_k import NaoCertificavel, StatsK, _pinagem, certifica_omega


def _I(assinatura: dict[int, int]) -> Fraction:
    x = Fraction(1)
    for p, a in assinatura.items():
        x *= I_pp(p, a)
    return x


# ---------------------------------------------------------------------------
# Certificados k <= 7
# ---------------------------------------------------------------------------

def test_k_ate_5_eliminados():
    for k in range(1, 6):
        st = certifica_omega(k)
        assert st.amigos == [], k
        assert st.assinaturas_testadas == 0, k


def test_k6_particao_primeiro_reduz_a_arvore_e_mantem_o_veredito():
    st = certifica_omega(6)
    s6 = omega6.certifica_omega6()
    assert st.amigos == [] and s6.amigos == []
    # o Bloco 2 (índice primeiro) testou 2745 conjuntos; com a PARTIÇÃO POR
    # ORÇAMENTOS em todo nó, o a1 comprometido entrando EXATO nas cotas de índice
    # e na cota universal (Bloco 4) e o último desconhecido por equação
    # ciclotômica (Bloco 5), todos os 26 conjuntos completos de k = 6 morrem já
    # pela poda barata de índice (prod_min > 9/5 ou prod_sup <= 9/5), em 55 nós.
    assert s6.conjuntos_completos == 2745
    assert st.nos == 55
    assert st.conjuntos_completos == 0
    assert st.completos_mortos_indice == 26
    assert st.assinaturas_testadas == 0
    # o primeiro pin é o a1 = 2 forçando 31 na raiz
    assert st.pins[0] == ((5,), "a1=2", (31,))
    assert ((5,), "a1=4", (11, 71)) in st.pins


def test_k7_certificado_pelo_recursivo():
    # Bloco 4: a parede do Bloco 3 ({5,7,11,13,31,331}+P, a1 = 2) cai com o a1
    # exato nas cotas de índice; o resto da árvore fecha com as valuações diretas
    # (sem materializar sigma(p^a) para a ~ 10^11) e a cota universal aplicada
    # também ao a1 comprometido. Contagens congeladas: se mudarem, o relatório
    # (FASE_1.md, Bloco 4) tem de mudar junto.
    st = certifica_omega(7)
    assert st.amigos == []
    assert st.assinaturas_testadas == 0
    assert st.nos == 459
    assert st.conjuntos_completos == 40
    assert st.completos_mortos_indice == 247
    assert st.ultimos_resolvidos >= 1              # Bloco 5: s = 1 sem enumerar primos
    assert st.conjuntos_com_primo_grande == 0      # maior primo em C tem 60 bits
    assert st.ramos_expoente == 0                  # caudas só entram em k = 8


def test_residual_do_bloco_3_morre_pelo_a1_exato():
    # {5,7,11,13,31,331}+P com a1 = 2: prod_sup com I(25) exato = 1,7868 < 9/5,
    # logo o índice limita P (fallback) e o nó fecha sem NaoCertificavel.
    C = [5, 7, 11, 13, 31, 331]
    prod_min, prod_sup = omega_k._prod_min_sup(C, {5: 2}, {})
    assert prod_sup < Fraction(9, 5) < omega_k._prod_min_sup(C, {}, {})[1]
    st = StatsK(k=7)
    omega_k._certifica(C, 1, 331, st, {5: 2}, {})
    assert st.amigos == []
    # Bloco 5: o caso aberto (k5 = 1, k3 = 1) é resolvido por Phi_5(P) = 5·11^a·31^b·331^c
    # (candidatos finitos), não pelo índice
    assert st.ultimos_resolvidos >= 1 and st.ramo_i == 0


# ---------------------------------------------------------------------------
# Partição por orçamentos (Bloco 3)
# ---------------------------------------------------------------------------

def test_pinagem_e_particao_completa_em_qualquer_no():
    # solidez da estratégia "partição primeiro": a lista de pins da raiz enumera
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


def test_viabilidade_injetiva_mata_o_residual_do_181():
    # antes do emparelhamento injetivo, {5,7,11,13,31,181}+P ficava aberto com
    # 45 | a_P+1 "viável" porque 181 ≡ 1 (mod 45); mas 9 e 45 exigem testemunhas
    # DISTINTAS e só o 181 serve — 45 não é viável.
    from core.omega_k import _expoentes_viaveis_unico, _viavel_m0
    assert 45 not in _expoentes_viaveis_unico((5, 7, 11, 13, 31, 181))
    assert 15 in _expoentes_viaveis_unico((5, 7, 11, 13, 31, 181))
    assert _expoentes_viaveis_unico((5, 7, 11, 13, 31, 331)) == (3, 5, 11, 15)
    # o teste direto sobre m0 = 5^k5·3^k3 (usado pela partição) é equivalente:
    # existe múltiplo viável de m0 sse m0 é viável
    for C in [(5, 7, 11, 13, 31, 181), (5, 7, 11, 13, 31, 331), (5, 7, 11, 13, 23)]:
        viaveis = _expoentes_viaveis_unico(C)
        for k5 in range(0, 3):
            for k3 in range(0, 3):
                if (k5, k3) == (0, 0):
                    continue
                m0 = 5**k5 * 3**k3
                assert _viavel_m0(k5, k3, list(C)) == any(m % m0 == 0 for m in viaveis), (C, m0)


# ---------------------------------------------------------------------------
# Bloco 4 — testemunhas sem fatorar r - 1, fecho por peças, caudas
# ---------------------------------------------------------------------------

def test_testes_de_ordem_por_exponenciacao_modular_batem_com_n_order():
    from core.omega_k import _e_ordem, _ordem_e_potencia
    primos = [7, 11, 13, 19, 31, 61, 71, 181, 331, 3221, 19531, 305175781]
    for q in [5, 7, 11, 13, 31]:
        for r in primos:
            if r == q:
                continue
            o = int(n_order(q, r))
            assert _e_ordem(q, r, o)
            for m in (3, 5, 9, 15, 25):
                assert _e_ordem(q, r, m) == (o == m), (q, r, m)
            for ell in (3, 5):
                for j in (1, 2, 3):
                    assert _ordem_e_potencia(q, r, ell, j) == (o == ell**j), (q, r, ell, j)


def test_fecho_de_sigma_por_pecas_ciclotomicas_equivale_ao_fecho_direto():
    from core.omega_k import _novos_de, _novos_de_sigma
    permitidos = {3, 5, 7, 11, 13, 31}
    for p in (5, 7, 11, 13):
        for a in range(2, 26, 2):
            for s in (1, 2, 3, 6):
                direto = _novos_de(sigma_pp(p, a), permitidos, s)
                pecas = _novos_de_sigma(p, a, permitidos, s)
                if direto is None:
                    assert pecas is None, (p, a, s)
                else:
                    assert pecas == (direto, 0), (p, a, s)


def test_resto_sem_fatorar_conserva_os_pins_e_conta_dois_desconhecidos(monkeypatch):
    # sigma(5^8) = 31·19·829 (Phi_3(5) = 31, Phi_9(5) = 15751 = 19·829): a divisão
    # por tentativa até 10^5 acha os dois primos mesmo com o orçamento de
    # fatoração forçado a 0 bits — o 31 (permitido) não conta como novo
    from core.omega_k import _novos_de_sigma, _novos_e_resto
    monkeypatch.setattr(omega_k, "FATORA_BITS", 0)
    assert _novos_de_sigma(5, 8, {3, 5, 31}, 1) is None
    assert _novos_de_sigma(5, 8, {3, 5, 31}, 2) == ((19, 829), 0)
    # 3·19·829·1000003·1000033: 19 e 829 são pins conhecidos, o resto composto
    # (> 10^5, > 0 bits) garante mais 2: precisa de 4 slots
    valor = 3 * 19 * 829 * 1000003 * 1000033
    assert _novos_e_resto(valor, {3}, 3) is None
    assert _novos_e_resto(valor, {3}, 4) == ((19, 829), 1000003 * 1000033)
    assert _novos_e_resto(valor, {3, 19}, 3) == ((829,), 1000003 * 1000033)
    monkeypatch.setattr(omega_k, "FATORA_BITS", 90)
    assert _novos_e_resto(valor, {3}, 4) == ((19, 829, 1000003, 1000033), 1)


def test_conjunto_com_primo_grande_da_as_mesmas_listas_que_o_fecho_direto(monkeypatch):
    # Os casos (A)/(B2)/(B1) do cabeçalho são uma segunda derivação, sem ord_r(p),
    # das listas de expoentes. Forçando "grande" = r - 1 com mais de 20 bits, os
    # conjuntos completos reais de k = 7 exercitam a via nova, que tem de dar
    # EXATAMENTE as listas da via direta (ambas exatas e completas).
    from core.omega_k import _listas_expoentes
    monkeypatch.setattr(omega_k, "ORDEM_BITS", 12)
    conjuntos = certifica_omega(7).conjuntos
    extras = omega6._parametros_do_alvo()[0]
    exercitados = 0
    for C in conjuntos:
        C = list(C)
        grandes = omega_k._grandes(C)
        if len(grandes) != 1:
            continue
        exercitados += 1
        fs = frozenset(C)
        direto = [expoentes_validos_ordens(p, fs, extras) for p in C]
        st = StatsK()
        via_nova = _listas_expoentes(C, extras, st, {}, {})
        assert st.conjuntos_com_primo_grande == 1
        if any(not lista for lista in direto):
            assert via_nova is None, C
        else:
            assert via_nova == direto, C
    assert exercitados >= 10


def test_caso_b1_primo_e_encontrado_sem_fatorar_r_menos_1(monkeypatch):
    # S = {5, 7, 11, 13, 19, 31} com r = 19 "grande": ord_19(7) = 3 (7^3 = 343 =
    # 18·19 + 1), e 3 não é ordem de 7 módulo nenhum outro primo de S; logo o
    # candidato a_7 + 1 = 3 só existe pelo caso (B1) primo — que tem de achá-lo
    # com a cota p^{ell-1} < ell·r^{A_r}. E sigma(7^2) = 57 = 3·19 fecha.
    from core.omega_k import _expoentes_com_primo_grande
    S_peq = frozenset({5, 7, 11, 13, 31})
    assert all(int(n_order(7, q)) != 3 for q in S_peq if q != 7)
    exps = _expoentes_com_primo_grande(7, S_peq, 19, frozenset({3}), A_r=2)
    assert 2 in exps


def test_ramificacao_por_expoente_com_cauda_no_residual_de_k8():
    # C = {5,7,11,13,31,89}, a1 = 2, s = 2: nó SOLTO (prod_sup = 1,80166 > 9/5 e
    # nenhum primo tem janela finita sozinho). Ganhos: g7 = 1,00292 > g11 =
    # 1,00075 > g13 > g31 > g89; prod_min·g7 = 1,79942 <= 9/5 < prod_min·g7·g11
    # => ramifica o 11: a11 = 2 exato (sigma(121) = 7·19 pina o 19) e cauda
    # a11 >= 4. Na cauda, m cai para 1: ramifica o 7 com a7 = 2 exato (57 = 3·19)
    # e cauda a7 >= 4, que MORRE (prod_min = 1,8005 > 9/5).
    from core.omega_k import _prod_min_sup, _ramos_expoente
    C = [5, 7, 11, 13, 31, 89]
    ALVO = Fraction(9, 5)
    assert _prod_min_sup(C, {5: 2}, {})[1] > ALVO
    ramos = _ramos_expoente(C, {5: 2}, {})
    assert ramos == [({5: 2, 11: 2}, {}), ({5: 2}, {11: 4})]
    ramos_cauda = _ramos_expoente(C, {5: 2}, {11: 4})
    assert ramos_cauda == [({5: 2, 7: 2}, {11: 4}), ({5: 2}, {11: 4, 7: 4})]
    assert _prod_min_sup(C, {5: 2}, {11: 4, 7: 4})[0] > ALVO       # cauda dupla morta
    # a partição completa do nó só produz esses ramos (a1 = 2 fixo); o filho
    # exato fecha sigma(11^2) = 7·19 no passo 1: com lo = 13 o 19 é pinado; com
    # lo = 89 (19 <= lo) o filho MORRE — pelo invariante o 19 já estaria em C
    st = StatsK()
    casos = omega_k._particao(C, 2, 13, st, {5: 2}, {})
    assert (((), {5: 2, 11: 2}, {}) in casos) and (((), {5: 2}, {11: 4}) in casos)
    assert omega_k._particao(C, 2, 13, st, {5: 2, 11: 2}, {}) == [((19,), {5: 2, 11: 2}, {})]
    assert omega_k._particao(C, 2, 89, st, {5: 2, 11: 2}, {}) == []


def test_ramificacao_particiona_todos_os_expoentes_e_progride():
    # propriedades estruturais da cauda em nós soltos de k = 8 e k = 9
    from core.omega_k import _prod_min_sup, _ramos_expoente
    ALVO = Fraction(9, 5)
    for C, fixos in [([5, 7, 11, 13, 31, 89], {5: 2}), ([5, 7, 11, 13, 31, 71, 97], {5: 2}),
                     ([5, 7, 11, 13, 17, 31, 61], {5: 2}), ([5, 7, 11, 13, 19, 31], {5: 2})]:
        prod_min, prod_sup = _prod_min_sup(C, fixos, {})
        if prod_sup <= ALVO or prod_min >= ALVO:
            continue
        ramos = _ramos_expoente(C, fixos, {})
        assert ramos is not None
        exatos = [f for f, m in ramos if m == {}]
        caudas = [m for f, m in ramos if m != {}]
        assert len(caudas) == 1
        (q, A), = caudas[0].items()
        assert A % 2 == 0 and A >= 4
        assert sorted(f[q] for f in exatos) == list(range(2, A, 2))   # partição de a_q


def test_fixos_forcam_contribuicao_nos_orcamentos():
    # 11 ≡ 1 (mod 5) com a11 = 4 fixo: v5(a11+1) = 1 forçado => o orçamento
    # v5 = a1 - 1 = 1 (a1 = 2) é inteiramente do 11 e Phi_5(11) = 5·3221 pina
    # 3221 (com 71 e 3221 fora de C); com a11 = 2 fixo, v5(3) = 0 e o 11 não
    # alimenta — o caso "só desconhecidos alimentam" fica aberto (s = 2).
    st = StatsK()
    casos = omega_k._casos_ell([5, 7, 11, 13, 23], 2, 23, 5, 1, {5: 2, 11: 4})
    assert casos == [("pin", (3221,))]
    casos = omega_k._casos_ell([5, 7, 11, 13, 23], 2, 23, 5, 1, {5: 2, 11: 2})
    assert casos == [("aberto", None)]
    casos = omega_k._casos_ell([5, 7, 11, 13, 23], 2, 23, 5, 1, {5: 2, 11: 24})   # v5(25) = 2 > 1
    assert casos == []


def test_cota_universal_vale_tambem_para_a1_comprometido():
    # a1 = 40 é admissível na raiz (s = 7: a1 <= 43) mas, fixado, morre assim que
    # C ganha um primo que não alimenta o 5: em {5, 7} com s = 6, a1 <= 31 < 40.
    # Sem esta poda o ramo a1 = 40 de k = 8 (sigma(5^40) = Phi_41(5) sem fator
    # < 10^5, resto de 95 bits) era explorado pelo índice: > 3·10^6 nós.
    st = StatsK()
    assert omega_k._particao([5, 7], 6, 7, st, {5: 40}, {}) == []
    with pytest.raises(NaoCertificavel):        # 11 alimenta: a1 <= 43, nó vivo (aberto)
        omega_k._particao([5, 11], 6, 11, st, {5: 40}, {})
    assert omega_k._particao([5, 11, 13], 5, 13, st, {5: 40}, {}) == []  # c5 = 1, s = 5: a1 <= 31


def test_conjunto_completo_respeita_fixos_e_minimos():
    # S = {5,7,11,13,17,19,23} (regime do índice) com alvo plantado I(N0):
    # a assinatura N0 = 5^2 7^2 11^2 13^2 17^2 19^2 23^4 só sobrevive se os
    # compromissos forem compatíveis com ela.
    assin = {5: 2, 7: 2, 11: 2, 13: 2, 17: 2, 19: 2, 23: 4}
    alvo = _I(assin)
    S = sorted(assin)

    def roda(fixos, minimos):
        st = StatsK()
        extras = omega6._parametros_do_alvo()[0]
        listas = omega_k._listas_expoentes(S, extras, st, fixos, minimos)
        if listas is None:
            return []
        omega6._conjunto_completo(S, st, listas=listas, fixos=fixos)
        return st.amigos

    import core.omega6 as o6
    old = o6.ALVO
    o6.ALVO = alvo
    try:
        assert assin in roda({}, {})
        assert assin in roda({23: 4}, {})
        assert assin in roda({}, {23: 4})
        assert roda({23: 2}, {}) == []
        assert roda({}, {23: 6}) == []
        assert roda({}, {7: 4}) == []
    finally:
        o6.ALVO = old


# ---------------------------------------------------------------------------
# Alvos plantados (completude no regime do índice)
# ---------------------------------------------------------------------------

def test_planted_k7_ramo_i(monkeypatch):
    # alvo plantado com I(N0) acima de qualquer prod_sup de 6 primos (máximo
    # {5,7,11,13,17,19} = 1.949): todos os nós caem no ramo (i) e a assinatura
    # de 7 primos tem de ser encontrada (a partição nunca é acionada).
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


# ---------------------------------------------------------------------------
# Bloco 5 — último desconhecido por equações ciclotômicas
# ---------------------------------------------------------------------------

def _bruto_ultimo(C, lo, ell, eps, U_max):
    """Força bruta independente: primos U em (lo, U_max] fora de C tais que
    Phi_ell(U) = ell^eps · (produto de primos de C_ell)."""
    from sympy import primerange
    C_ell = [q for q in C if (q - 1) % ell == 0]
    out = []
    for U in primerange(lo + 1, U_max + 1):
        if U in C:
            continue
        R = (U**ell - 1) // (U - 1)
        v = 0
        while R % ell == 0:
            R //= ell
            v += 1
        if v != eps:
            continue
        for q in C_ell:
            while R % q == 0:
                R //= q
        if R == 1:
            out.append(U)
    return out


def test_solucoes_phi_batem_com_forca_bruta():
    from core.omega_k import _cota_indice_U, _phi_primo, _prod_min_sup, _solucoes_phi
    casos = [([5, 7, 11, 13, 23], {5: 2}), ([5, 7, 11, 13, 31], {5: 2}),
             ([5, 7, 13, 19, 31], {5: 2, 7: 2}), ([5, 11, 31, 71], {5: 4})]
    encontrados = set()
    for C, fixos in casos:
        prod_sup = _prod_min_sup(C, fixos, {})[1]
        cota = _cota_indice_U(prod_sup)          # None em {5,7,11,13,23} (sem cota)
        U_max = 200_000 if cota is None else min(cota, 200_000)
        lo = max(C)
        for ell in (3, 5, 7, 11):
            C_ell = [q for q in C if (q - 1) % ell == 0]
            for eps in (0, 1):
                esperado = _bruto_ultimo(C, lo, ell, eps, U_max)
                obtido = sorted(_solucoes_phi(ell, eps, C_ell, _phi_primo(ell, U_max), fixos, lo, set(C)))
                assert obtido == esperado, (C, ell, eps, obtido, esperado)
                encontrados.update(esperado)
    assert 67 in encontrados       # não-vacuidade: 67^2 + 67 + 1 = 3·7^2·31 em {5,7,11,13,31}


def test_ultimo_desconhecido_resolve_o_no_quase_justo_de_k9():
    # C = {5,7,11,13,31,97,52361}, a1 = 2: prod_sup = 9/5 - 1,8e-8 e o índice só
    # limita U por U < 1,03e8 (5,9 milhões de primos). O solver enumera vetores de
    # expoentes e extrai raízes inteiras — em bem menos de um segundo.
    import time
    from core.omega_k import _cota_indice_U, _prod_min_sup, _ultimo_desconhecido
    C = [5, 7, 11, 13, 31, 97, 52361]
    prod_sup = _prod_min_sup(C, {5: 2}, {})[1]
    assert _cota_indice_U(prod_sup) > 10**8
    t = time.perf_counter()
    for k5, k3 in [(1, 0), (0, 1), (0, 0), (1, 2)]:
        cands = _ultimo_desconhecido(C, 52361, {5: 2}, k5, k3, prod_sup)
        assert cands is not None
        assert all(isprime(U) and U > 52361 for U in cands)
    assert time.perf_counter() - t < 5
    # sem cota (prod_sup >= 9/5, expoentes livres) o solver recusa, honestamente
    assert _ultimo_desconhecido([5, 7, 11, 13, 31, 89], 89, {5: 2}, 1, 0, Fraction(9, 5)) is None
    # ... salvo se todos os q em C_ell têm expoente fixo (lado direito finito)
    assert _ultimo_desconhecido([5, 7, 11, 13, 31, 89], 89, {5: 2, 11: 2, 31: 2}, 1, 0,
                                Fraction(9, 5)) is not None


def test_ultimo_desconhecido_e_completo_contra_forca_bruta():
    # Completude: em C = {5, 7, 11, 13, 31} com a1 = 2 (cota do índice U < 97),
    # o caso (k5, k3) = (0, 1) exige Phi_3(U) = 3·(produto de {7, 13, 31}) e a
    # força bruta acha exatamente U = 67; o caso (0, 0) é a união sobre
    # L(C) = {3, 5} com eps = 0 (U não alimenta 3 nem 5).
    from core.omega_k import _cota_indice_U, _prod_min_sup, _ultimo_desconhecido
    C = [5, 7, 11, 13, 31]
    prod_sup = _prod_min_sup(C, {5: 2}, {})[1]
    U_max = _cota_indice_U(prod_sup)
    assert U_max == 96
    assert _ultimo_desconhecido(C, 31, {5: 2}, 0, 1, prod_sup) == _bruto_ultimo(C, 31, 3, 1, U_max) == [67]
    assert _ultimo_desconhecido(C, 31, {5: 2}, 1, 0, prod_sup) == _bruto_ultimo(C, 31, 5, 1, U_max)
    esperado = sorted(set(_bruto_ultimo(C, 31, 3, 0, U_max)) | set(_bruto_ultimo(C, 31, 5, 0, U_max)))
    assert _ultimo_desconhecido(C, 31, {5: 2}, 0, 0, prod_sup) == esperado
