"""Testes do certificador recursivo (core/omega_k.py), Blocos 3 e 4."""
from fractions import Fraction

import pytest
from sympy import isprime, n_order

import core.omega6 as omega6
import core.omega_k as omega_k
from core.cadeias import expoentes_validos_ordens
from core.motor import I_pp, sigma_pp, sup_pp
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
    # (PHASE_1.md, Block 4) tem de mudar junto.
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
    assert ramos == [({5: 2, 11: 2}, {}, {}), ({5: 2}, {11: 4}, {})]
    ramos_cauda = _ramos_expoente(C, {5: 2}, {11: 4})
    assert ramos_cauda == [({5: 2, 7: 2}, {11: 4}, {}), ({5: 2}, {11: 4, 7: 4}, {})]
    # com cota superior a_11 <= 2 (maximos) o ganho do 11 é 1: a ramificação vai
    # para outro primo (o 13), nenhuma cauda toca o 11, e a cota viaja nos filhos
    r11 = _ramos_expoente(C, {5: 2}, {}, {11: 2})
    assert r11 and all(11 not in m and mx == {11: 2} for _, m, mx in r11)
    assert any(f.get(13) == 2 for f, _, _ in r11) and any(m.get(13) == 4 for _, m, _ in r11)
    # com a_13 <= 2 tambem, prod_sup (com I(11^2) e I(13^2) no lugar dos sups) cai
    # abaixo de 9/5: nenhuma cauda mata, e a ramificacao recusa (None) — o indice,
    # agora limitado, e o caminho
    from core.omega_k import _prod_min_sup
    assert _prod_min_sup(C, {5: 2}, {}, {11: 2, 13: 2})[1] < ALVO
    assert _ramos_expoente(C, {5: 2}, {}, {11: 2, 13: 2}) is None
    assert _prod_min_sup(C, {5: 2}, {11: 4, 7: 4})[0] > ALVO       # cauda dupla morta
    # a partição completa do nó só produz esses ramos (a1 = 2 fixo); o filho
    # exato fecha sigma(11^2) = 7·19 no passo 1: com lo = 13 o 19 é pinado; com
    # lo = 89 (19 <= lo) o filho MORRE — pelo invariante o 19 já estaria em C
    st = StatsK()
    casos = [c[:4] for c in omega_k._particao(C, 2, 13, st, {5: 2}, {})]
    assert (((), {5: 2, 11: 2}, {}, {}) in casos) and (((), {5: 2}, {11: 4}, {}) in casos)
    assert [c[:4] for c in omega_k._particao(C, 2, 13, st, {5: 2, 11: 2}, {})] == \
        [((19,), {5: 2, 11: 2}, {}, {})]
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
        exatos = [f for f, m, _ in ramos if m == {}]
        caudas = [m for f, m, _ in ramos if m != {}]
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


# ---------------------------------------------------------------------------
# Bloco 6 — cota finita de expoente (Cor. 6) e níveis de Wieferich (Prop. 9)
# ---------------------------------------------------------------------------

def _w_bruto(r, q):
    """w_r(q) = v_r(q^{ord_r(q)} - 1) por definição (ordem via n_order)."""
    o = int(n_order(q, r))
    x = q**o - 1
    v = 0
    while x % r == 0:
        x //= r
        v += 1
    return v


def test_prop9_nivel_wieferich_contra_forca_bruta():
    # para r pequeno e todo primo q <= L, w_r(q) <= _nivel_wieferich_max(r, L); e a
    # cota e justa em pelo menos um caso (existe q <= L atingindo-a) para algum L
    from sympy import primerange
    from core.omega_k import _min_residuo_teichmuller, _nivel_wieferich_max
    for r in (3, 5, 7, 11, 13, 31):
        for L in (10**3, 10**4, 10**5):
            cota = _nivel_wieferich_max(r, L)
            maximo = max(_w_bruto(r, q) for q in primerange(2, L + 1) if q % r not in (0, 1))
            assert maximo <= cota, (r, L, maximo, cota)
    # a definição de m_a(r): todo q ≢ 1 mod r com w_r(q) >= a satisfaz q >= m_a(r)
    for r in (7, 11, 31):
        for a in (2, 3):
            m = _min_residuo_teichmuller(r, a)
            for q in primerange(2, min(m, 200_000)):
                if q % r in (0, 1):
                    continue
                assert _w_bruto(r, q) < a, (r, a, q)
    # exemplo clássico: 3^10 = 59049 = 11^2·488 + 1, logo w_11(3) = 2 e m_2(11) <= 3
    assert _w_bruto(11, 3) == 2 and _min_residuo_teichmuller(11, 2) <= 3


def test_cota_L_desconhecidos_e_uma_cota():
    # nivel 1: todo q visitado pelo laco do indice e <= L1. Filhos com q <= B_min
    # tem prod_sup >= 9/5 (sem cota de indice): a cota L so vale para q > B_min, e
    # nesses filhos (s = 2) o laco do indice do filho para em q2 <= L.
    from sympy import nextprime
    from core.omega_k import _cota_L_desconhecidos, _prod_min_sup, _sup_prox_excl
    for C, s, fixos in [([5, 7, 11, 13, 31], 2, {5: 2}), ([5, 7, 11, 13, 31, 331], 1, {5: 2}),
                        ([5, 7, 11, 13, 31], 2, {5: 2, 7: 4}), ([5, 7, 11, 13, 31, 97], 3, {5: 2})]:
        L1, B_min, L = _cota_L_desconhecidos(C, s, fixos, {})
        assert (L is None) == (s >= 2)          # s = 2 needs lo >= B_min (given below)
        if s == 2:
            assert _cota_L_desconhecidos(C, s, fixos, {}, None, None, B_min - 1)[2] is None
            L = _cota_L_desconhecidos(C, s, fixos, {}, None, None, B_min)[2]
            assert L is not None
        _, prod_sup = _prod_min_sup(C, fixos, {})
        q = max(C)
        visitados = []
        while True:
            q = int(nextprime(q))
            if prod_sup * sup_pp(q) * _sup_prox_excl(q, s - 1, frozenset(C)) <= Fraction(9, 5):
                break
            visitados.append(q)
        assert all(q <= L1 for q in visitados), (C, s, visitados[-1], L1)
        if C == [5, 7, 11, 13, 31, 331]:
            assert not visitados and L1 < 331     # no morto pelo indice: nenhum U > lo cabe
        if s != 2:
            continue
        for q in visitados:
            ps2 = prod_sup * sup_pp(q)
            if q <= B_min:
                assert ps2 >= Fraction(9, 5), (C, q, B_min)      # filho sem cota
                continue
            assert ps2 < Fraction(9, 5)
            q2 = q
            ultimo = None
            while True:
                q2 = int(nextprime(q2))
                if ps2 * sup_pp(q2) <= Fraction(9, 5):
                    break
                assert q2 <= L, (C, q, q2, L)
                ultimo = q2
            if q == int(nextprime(B_min)) and ultimo is not None:
                # the bound is essentially attained at the first child above B_min
                assert L < 2 * ultimo + 2, (C, q, ultimo, L)


def test_cor6_majora_os_expoentes_de_amigos_plantados(monkeypatch):
    # Em qualquer no (C parcial, s desconhecidos, alguns expoentes fixos) a cota
    # A_r tem de ser >= o expoente verdadeiro de r no amigo plantado.
    from core.omega_k import _cota_L_desconhecidos, _cota_expoente_conhecido
    assinaturas = [
        {5: 2, 7: 2, 11: 2, 13: 2, 17: 2, 19: 2, 23: 4},
        {5: 4, 7: 2, 11: 6, 13: 2, 17: 2, 19: 4, 23: 2},
        {5: 2, 7: 8, 11: 2, 13: 4, 17: 2, 19: 2, 23: 2, 29: 2},
    ]
    for assin in assinaturas:
        alvo = _I(assin)
        monkeypatch.setattr(omega6, "ALVO", alvo)
        primos = sorted(assin)
        for n_conhecidos in range(len(primos), 2, -1):
            C = primos[:n_conhecidos]
            s = len(primos) - n_conhecidos
            for fixos in ({}, {5: assin[5]}, {5: assin[5], primos[1]: assin[primos[1]]}):
                cotas = _cota_L_desconhecidos(C, s, fixos, {}, None, None, max(C)) if s else None
                if s and (cotas is None or cotas[2] is None or max(C) < cotas[1]):
                    continue        # sem cota valida para todos os desconhecidos neste no
                L = None if cotas is None else max(cotas[2], max(primos))
                for r in C:
                    if r in fixos:
                        continue
                    A = _cota_expoente_conhecido(r, C, s, fixos, L)
                    if A is None:
                        continue
                    assert A >= assin[r], (assin, C, s, fixos, r, A)


def test_cor6_no_quase_justo_de_k9_da_cotas_finitas():
    # C = {5,7,11,13,31,97}, s = 3, a1 = 2: o indice enumera ~14 000 primos; a cota
    # finita existe para cada conhecido livre e converte a cauda em ramos exatos
    from core.omega_k import _cota_L_desconhecidos, _cota_expoente_conhecido, _ramos_cor6
    C = [5, 7, 11, 13, 31, 97]
    L1, B_min, L = _cota_L_desconhecidos(C, 3, {5: 2}, {})
    assert L1 > 100_000 and L is None            # s = 3: sem cota uniforme
    assert _ramos_cor6(C, 3, 97, {5: 2}, {}) is None
    # no filho com s = 2 e lo acima de B_min todos os desconhecidos tem cota
    C = [5, 7, 11, 13, 31, 97, 52361]
    L1, B_min, L = _cota_L_desconhecidos(C, 2, {5: 2}, {}, None, None, 52361)
    assert 10**8 < B_min < L1 and L is None                  # lo < B_min: no bound on U_2
    assert _ramos_cor6(C, 2, 52361, {5: 2}, {}) is None      # lo < B_min: nao se aplica
    lo = B_min + 1
    L = _cota_L_desconhecidos(C, 2, {5: 2}, {}, None, None, lo)[2]
    assert L1 < L < L1 * L1
    for r in (7, 11, 13, 31, 97, 52361):
        A = _cota_expoente_conhecido(r, C, 2, {5: 2}, L)
        assert A is not None and 2 <= A <= 400, (r, A)
    ramos = _ramos_cor6(C, 2, lo, {5: 2}, {})
    assert ramos and all(m == {} for _, m, _ in ramos)
    r = next(iter(set(ramos[0][0]) - {5}))
    assert sorted(f[r] for f, _, _ in ramos) == list(range(2, max(f[r] for f, _, _ in ramos) + 1, 2))
    # as cotas de todos os livres viajam nos filhos como maximos, e o ramo usa a menor
    mx = ramos[0][2]
    # Block 7: bounds of expensive primes (r > R_CHEAP_PROP9, here 52361) are computed
    # only when no cheap prime can be branched, so only the cheap ones travel as maximos
    assert set(mx) == {7, 11, 13, 31, 97} and all(v >= 2 for v in mx.values())
    assert r in mx
    assert max(f[r] for f, _, _ in ramos) == mx[r] - (mx[r] % 2)


def test_lema_do_fecho_total_mata_no_tudo_fixo_sem_pins(monkeypatch):
    # (1) pins de sigma's fixos: C = {5, 7, 11} com a = 2 fixos, s = 2, lo = 11:
    #     sigma(25) = 31, sigma(49) = 3·19, sigma(121) = 7·19 -> pins (19, 31), sem lema
    st = StatsK()
    casos = omega_k._particao([5, 7, 11], 2, 11, st, {5: 2, 7: 2, 11: 2}, {})
    assert casos and casos[0][0] == (19, 31) and st.fecho_total_mortos == 0
    # (2) com lo = 31 o pin 19 <= lo mata o no (invariante), tambem sem lema
    assert omega_k._particao([5, 7, 11], 2, 31, StatsK(), {5: 2, 7: 2, 11: 2}, {}) == []
    # (3) o lema: todos fixos e NENHUM primo novo em sigma(q^{a_q}) (simulado):
    #     x = (9/5) / (I(25) I(49) I(121)) = 1.135... nao e inteiro -> morto
    monkeypatch.setattr(omega_k, "_novos_de_sigma", lambda *a, **k: ((), 0))
    st = StatsK()
    assert omega_k._particao([5, 7, 11], 2, 11, st, {5: 2, 7: 2, 11: 2}, {}) == []
    assert st.fecho_total_mortos == 1
    x = Fraction(9, 5) / (I_pp(5, 2) * I_pp(7, 2) * I_pp(11, 2))
    assert x.denominator != 1 and 1 < x < Fraction(9, 5)
    # (4) com um expoente livre o lema nao se aplica (o no segue para os orcamentos)
    st = StatsK()
    try:
        omega_k._particao([5, 7, 11], 2, 11, st, {5: 2, 7: 2}, {})
    except NaoCertificavel:
        pass
    assert st.fecho_total_mortos == 0


# ---------------------------------------------------------------------------
# Block 7 - the B_min split of a near-tight node (state field `hi`)
# ---------------------------------------------------------------------------

NEAR_TIGHT = [5, 7, 11, 13, 31, 97, 52361]      # a1 = 2: prod_sup = 9/5 - 1.76e-8


def test_block7_index_facts():
    # For an integer U >= 2: prod_sup*sup(U) >= 9/5 iff U <= B; v(B-1) > sup(B);
    # prod_sup*v(h) < 9/5 for every h > B. Checked exactly on several nodes.
    from core.omega_k import _prod_min_sup, _virtual
    ALVO = Fraction(9, 5)
    nodes = [(NEAR_TIGHT, {5: 2}), ([5, 7, 11, 13, 31, 97], {5: 2}), ([5, 7, 11, 13, 31], {5: 2}),
             ([5, 7, 11, 13, 31, 331], {5: 2}), ([5, 7, 11, 13, 31], {5: 2, 7: 4})]
    for C, fixos in nodes:
        _, prod_sup = _prod_min_sup(C, fixos, {})
        assert prod_sup < ALVO
        R = ALVO / prod_sup
        B = int(1 + 1 / (R - 1))
        assert B >= 3
        assert prod_sup * Fraction(B, B - 1) >= ALVO > prod_sup * Fraction(B + 1, B)
        assert _virtual(B - 1) == Fraction(B, B - 1) + Fraction(1, (B - 1) ** 2)
        assert prod_sup * _virtual(B - 1) > ALVO
        for h in (B + 1, B + 2, 2 * B, 10 * B + 7):
            assert prod_sup * _virtual(h) < ALVO, (C, h)
    assert _virtual(7) == I_pp(7, 2) and _virtual(52361) == I_pp(52361, 2)


def test_block7_virtual_factor_is_a_lower_bound():
    # I(N) >= prod_min * v(hi) for every configuration with smallest unknown <= hi:
    # exhaustive over small known sets, exponents, and unknown primes.
    from sympy import primerange
    from core.omega_k import _prod_min_sup, _virtual
    for C, fixos, minimos in [([5, 7, 11], {5: 2}, {}), ([5, 7, 13], {5: 4}, {7: 4}),
                              ([5, 11, 31], {5: 2, 31: 2}, {})]:
        prod_min, _ = _prod_min_sup(C, fixos, minimos)
        for hi in (17, 23, 40, 101):
            v = _virtual(hi)
            for U1 in primerange(max(C) + 1, hi + 1):
                for a1 in (2, 4, 6):
                    for others in ((), (U1 + 100 - (U1 + 100) % 2 + 3,)):   # any second factor > 1
                        for exps in ([2, 2, 2], [2, 4, 2], [6, 2, 4]):
                            total = Fraction(1)
                            ok_cfg = True
                            for q, e in zip(C, exps):
                                e = fixos.get(q, max(e, minimos.get(q, 2)))
                                total *= I_pp(q, e)
                            total *= I_pp(U1, a1)
                            for o in others:
                                total *= Fraction(o * o + o + 1, o * o)
                            assert ok_cfg and total >= prod_min * v, (C, hi, U1, a1)
                            if others:
                                assert total > prod_min * v


def test_block7_split_cases_on_the_near_tight_node():
    from core.omega_k import _INHERIT, _prod_min_sup, _split_cases
    C, fixos = NEAR_TIGHT, {5: 2}
    _, prod_sup = _prod_min_sup(C, fixos, {})
    R = Fraction(9, 5) / prod_sup
    B = int(1 + 1 / (R - 1))
    assert 10**8 < B < 2 * 10**8
    cases = _split_cases(C, 2, 52361, fixos, {}, {}, None)
    assert cases[0] == ((), None, B - 1)                    # (a): hi := B - 1
    assert cases[-1] == ((), B, _INHERIT)                   # (b): lo := B
    if isprime(B):
        assert cases[1] == ((B,), B, None)                  # (a2): pin B, lo := B, hi dropped
    assert len(cases) == (3 if isprime(B) else 2)
    # not applicable: s = 1, lo already >= B - 1, no progress on an existing hi,
    # no index bound, short interval
    assert _split_cases(C, 1, 52361, fixos, {}, {}, None) is None
    assert _split_cases(C, 2, B - 1, fixos, {}, {}, None) is None
    assert _split_cases(C, 2, 52361, fixos, {}, {}, B - 1) is None
    assert _split_cases([5, 7, 11, 13, 31, 89], 2, 89, fixos, {}, {}, None) is None   # prod_sup > 9/5
    assert _split_cases([5, 7, 11, 13, 31, 331], 2, 331, fixos, {}, {}, None) is None  # short
    # with a larger hi already set, case (a) tightens it and (b) keeps it
    cases = _split_cases(C, 2, 52361, fixos, {}, {}, 3 * B)
    assert cases[0] == ((), None, B - 1) and cases[-1] == ((), B, _INHERIT)
    # with hi = B, case (b) (U_1 > B) is empty and is omitted
    cases = _split_cases(C, 2, 52361, fixos, {}, {}, B)
    assert cases[0] == ((), None, B - 1) and all(c[1] != B or c[0] for c in cases)


def test_block7_tails_apply_under_hi_and_the_chain_dies():
    # In case (a) the tails are applicable although prod_sup < 9/5, they partition the
    # exponent of the branched prime, and following only tail children ends in a node
    # killed by the virtual factor.
    from core.omega_k import _prod_min_sup, _ramos_expoente, _virtual
    ALVO = Fraction(9, 5)
    C, fixos = NEAR_TIGHT, {5: 2}
    _, prod_sup = _prod_min_sup(C, fixos, {})
    B = int(1 + 1 / (ALVO / prod_sup - 1))
    hi = B - 1
    assert _ramos_expoente(C, fixos, {}, {}) is None                 # no hi: index regime
    assert _ramos_expoente(C, fixos, {}, {}, B + 1) is None          # hi > B: still no tails
    minimos: dict[int, int] = {}
    steps = 0
    while True:
        prod_min, _ = _prod_min_sup(C, fixos, minimos)
        if prod_min * _virtual(hi) > ALVO:
            break                                                    # dead by the virtual factor
        ramos = _ramos_expoente(C, fixos, minimos, {}, hi)
        assert ramos, "tails must apply while the node is alive"
        caudas = [m for f, m, _ in ramos if f == fixos]
        exatos = [f for f, m, _ in ramos if f != fixos]
        assert len(caudas) == 1
        (q, A), = [(q, a) for q, a in caudas[0].items() if minimos.get(q) != a]
        amin = minimos.get(q, 2)
        assert A > amin and sorted(f[q] for f in exatos) == list(range(amin, A, 2))
        minimos = caudas[0]
        steps += 1
        assert steps <= len(C)
    assert steps == len(C) - 1          # every free prime had to be pushed (margin ~ 1/hi^2)


def test_block7_hi_inheritance_and_kills(monkeypatch):
    from core.omega_k import Case, _INHERIT, _prod_min_sup, _virtual
    calls = []
    real = omega_k._certifica

    def spy(C, s, lo, stats, fixos=None, minimos=None, maximos=None, hi=None):
        calls.append((tuple(C), s, lo, hi))
        if len(calls) == 1:
            return real(C, s, lo, stats, fixos, minimos, maximos, hi)
        return None                                   # do not descend below the children

    def run(cases, C, s, lo, hi):
        calls.clear()
        monkeypatch.setattr(omega_k, "_particao", lambda *a, **k: cases)
        monkeypatch.setattr(omega_k, "_certifica", spy)
        omega_k._certifica(C, s, lo, StatsK(), {5: 2}, {}, {}, hi)
        return calls[1:]

    C = [5, 7, 11, 13, 31]
    f = {5: 2}
    # children without pins inherit hi; pins all > hi keep it; a pin <= hi drops it
    kids = run([Case((), f, {}, {}), Case((1009,), f, {}, {}), Case((61,), f, {}, {}),
                Case((61, 1009), f, {}, {})], C, 3, 31, 100)
    assert kids == [((5, 7, 11, 13, 31), 3, 31, 100), ((5, 7, 11, 13, 31, 1009), 2, 31, 100),
                    ((5, 7, 11, 13, 31, 61), 2, 31, None), ((5, 7, 11, 13, 31, 61, 1009), 1, 31, None)]
    # explicit overrides of the split: (a) sets hi, (a2) pins with lo and drops hi, (b) raises lo
    kids = run([Case((), f, {}, {}, None, 70), Case((71,), f, {}, {}, 71, None),
                Case((), f, {}, {}, 71, _INHERIT)], C, 3, 31, 100)
    assert kids == [((5, 7, 11, 13, 31), 3, 31, 70), ((5, 7, 11, 13, 31, 71), 2, 71, None),
                    ((5, 7, 11, 13, 31), 3, 71, 100)]
    # kills: s = 0 with hi set; hi <= lo; virtual factor above the target
    for C_, s_, lo_, hi_ in [(C, 0, 31, 100), (C, 2, 100, 100), (C, 2, 31, 37)]:
        st = StatsK()
        calls.clear()
        monkeypatch.setattr(omega_k, "_particao", lambda *a, **k: pytest.fail("must die before"))
        monkeypatch.setattr(omega_k, "_certifica", real)
        prod_min, _ = _prod_min_sup(C_, f, {})
        if (C_, s_, lo_, hi_) == (C, 2, 31, 37):
            assert prod_min < Fraction(9, 5) < prod_min * _virtual(37)
        omega_k._certifica(C_, s_, lo_, st, f, {}, {}, hi_)
        assert st.dead_hi == 1 and st.amigos == []


def test_block7_index_fallback_stops_at_hi(monkeypatch):
    # when the partition declines, the enumeration of the smallest unknown runs over
    # primes in (lo, hi] only and the children drop hi
    seen = []
    real = omega_k._certifica

    def spy(C, s, lo, stats, fixos=None, minimos=None, maximos=None, hi=None):
        if len(seen) == 0:
            seen.append("root")
            return real(C, s, lo, stats, fixos, minimos, maximos, hi)
        seen.append((C[-1] if C[-1] > 31 else max(C), s, lo, hi))
        return None

    def decline(*a, **k):
        raise NaoCertificavel("declined")

    monkeypatch.setattr(omega_k, "_particao", decline)
    monkeypatch.setattr(omega_k, "_certifica", spy)
    # children with q <= 67 are skipped by the usual prod_min kill (I(q^2) too large);
    # without hi the loop runs up to the index break (q = 191), with hi = 100 up to 97
    omega_k._certifica([5, 7, 11, 13, 31], 2, 31, StatsK(), {5: 2}, {}, {}, 100)
    kids = seen[1:]
    assert [k[2] for k in kids] == [71, 73, 79, 83, 89, 97]
    assert all(k[1] == 1 and k[3] is None for k in kids)
    seen.clear()
    omega_k._certifica([5, 7, 11, 13, 31], 2, 31, StatsK(), {5: 2}, {}, {}, None)
    assert [k[2] for k in seen[1:]][:6] == [71, 73, 79, 83, 89, 97] and seen[-1][2] == 191
    # hi = 60: the node dies by the virtual factor before any enumeration
    seen.clear()
    st = StatsK()
    omega_k._certifica([5, 7, 11, 13, 31], 2, 31, st, {5: 2}, {}, {}, 60)
    assert seen == ["root"] and st.dead_hi == 1


def test_block7_last_unknown_solver_uses_hi():
    # s = 1 with hi: U <= hi bounds the right-hand side even when prod_sup >= 9/5
    from core.omega_k import _ultimo_desconhecido
    C = [5, 7, 11, 13, 31, 89]                    # prod_sup(a1 = 2) > 9/5: no index bound
    assert _ultimo_desconhecido(C, 89, {5: 2}, 1, 0, Fraction(9, 5)) is None
    for k5, k3, ell in [(1, 0, 5), (0, 1, 3)]:
        got = _ultimo_desconhecido(C, 89, {5: 2}, k5, k3, Fraction(9, 5), 20000)
        assert got == _bruto_ultimo(C, 89, ell, 1, 20000)
    # and with an index bound the smaller of the two is used
    C2 = [5, 7, 11, 13, 31]
    from core.omega_k import _cota_indice_U, _prod_min_sup
    ps = _prod_min_sup(C2, {5: 2}, {})[1]
    assert _cota_indice_U(ps) == 96
    assert _ultimo_desconhecido(C2, 31, {5: 2}, 0, 1, ps) == [67]
    assert _ultimo_desconhecido(C2, 31, {5: 2}, 0, 1, ps, 66) == []
    assert _ultimo_desconhecido(C2, 31, {5: 2}, 0, 1, ps, 67) == [67]


def test_block7_near_tight_k9_node_closes_without_enumeration():
    # Before Block 7 this node enumerated ~11 million primes for its smallest unknown
    # (U_1 < 2.05e8). With the split it closes in a few dozen nodes.
    import time
    st = StatsK(k=9)
    t = time.perf_counter()
    omega_k._certifica(NEAR_TIGHT, 2, 52361, st, {5: 2}, {}, {}, None)
    assert st.amigos == []
    assert st.splits >= 1 and st.dead_hi >= 1 and st.cor6_ramos >= 1
    assert st.ramo_i == 0                         # the index enumeration was never needed
    assert st.nos < 500
    assert time.perf_counter() - t < 60


def test_block7_coprime_base_properties():
    # pairwise coprime, all > 1, same prime support as the product of the inputs
    from math import gcd
    from sympy import factorint
    from core.omega_k import _coprime_base
    casos = [[12, 18, 35], [2 * 3 * 5, 3 * 5 * 7, 5 * 7 * 11], [49, 7, 343], [101 * 103, 103 * 107, 109],
             [1, 97, 97], [2**10, 6**5, 15**3, 77], []]
    for nums in casos:
        base = _coprime_base(nums)
        assert all(b > 1 for b in base)
        for i in range(len(base)):
            for j in range(i + 1, len(base)):
                assert gcd(base[i], base[j]) == 1, (nums, base)
        suporte = set()
        for n in nums:
            if n > 1:
                suporte |= set(factorint(n))
        suporte_base = set()
        for b in base:
            suporte_base |= set(factorint(b))
        assert suporte_base == suporte, (nums, base)


def test_block7_residue_unknowns_counts_and_reveals():
    from core.omega_k import _residue_unknowns
    p1, p2, p3, p4 = 1000003, 1000033, 1000037, 1000039
    # coprime residues add up: 2 + 2 further unknown primes, nothing identified
    assert _residue_unknowns([p1 * p2, p3 * p4], set()) == (set(), 4)
    # a shared prime is revealed by the gcd, and so are the cofactors
    assert _residue_unknowns([p1 * p2, p2 * p3], set()) == ({p1, p2, p3}, 0)
    # the same residue twice still means only two unknown primes
    assert _residue_unknowns([p1 * p2, p1 * p2], set()) == (set(), 2)
    # a pin found elsewhere may divide a residue
    assert _residue_unknowns([p1 * p2], {p1}) == ({p1, p2}, 0)
    assert _residue_unknowns([p1 * p2 * p3], {p1}) == ({p1}, 2)
    assert _residue_unknowns([p1**2 * p2], {p1}) == ({p1, p2}, 0)
    assert _residue_unknowns([], {p1}) == ({p1}, 0)


def test_block7_coprime_residues_of_two_fixed_primes_kill_with_two_slots(monkeypatch):
    # sigma(7^42) = Phi_43(7) and sigma(11^42) = Phi_43(11) left unfactored (factoring
    # budget forced to 0): each residue hides >= 2 unknown primes; they are coprime,
    # so >= 4 unknown primes are needed. Dead with s <= 3, alive with s = 4.
    from math import gcd
    from core.omega_k import _divisao_pequena, _phi_valor
    monkeypatch.setattr(omega_k, "FATORA_BITS", 0)
    r7 = _divisao_pequena(_phi_valor(43, 7))[1]
    r11 = _divisao_pequena(_phi_valor(43, 11))[1]
    assert r7 > 1 and r11 > 1 and gcd(r7, r11) == 1
    assert not isprime(r7) and not isprime(r11)
    C = [5, 7, 11, 13, 31]
    fixos = {5: 2, 7: 42, 11: 42}
    for s_, vivo in [(2, False), (3, False), (4, True)]:
        st = StatsK()
        try:
            casos = omega_k._particao(C, s_, 31, st, fixos, {})
        except NaoCertificavel:
            casos = "open"
        assert (casos != []) == vivo, (s_, casos)
    # one fixed prime alone only guarantees two unknown primes
    st = StatsK()
    try:
        casos = omega_k._particao(C, 2, 31, st, {5: 2, 7: 42}, {})
    except NaoCertificavel:
        casos = "open"
    assert casos != []


def test_block7_index_loop_skips_exactly_the_dead_prefix(monkeypatch):
    # _first_live_q is the least q with prod_min·v(q) <= 9/5 (exact), and starting the
    # index loop there visits exactly the children visited without the skip.
    from core.omega_k import _first_live_q, _prod_min_sup, _virtual
    ALVO = Fraction(9, 5)
    for C, fixos, minimos in [([5, 7, 11, 13, 31], {5: 2}, {}), ([5, 7, 11, 13, 31, 97], {5: 2}, {}),
                              ([5, 7, 11, 13, 31, 97, 52361], {5: 2}, {7: 6, 11: 4}),
                              ([5, 7, 11], {5: 2}, {}), ([5, 7, 11, 13, 31], {5: 2, 7: 2, 11: 2}, {})]:
        prod_min, _ = _prod_min_sup(C, fixos, minimos)
        q0 = _first_live_q(prod_min)
        assert prod_min * _virtual(q0) <= ALVO
        assert q0 == 2 or prod_min * _virtual(q0 - 1) > ALVO

    def children(C, s, lo, fixos, hi, skip):
        seen = []
        real = omega_k._certifica

        def spy(C_, s_, lo_, stats, f=None, m=None, mx=None, hi_=None):
            if not seen:
                seen.append("root")
                return real(C_, s_, lo_, stats, f, m, mx, hi_)
            seen.append((tuple(C_), s_, lo_, hi_))
            return None

        def decline(*a, **k):
            raise NaoCertificavel("declined")

        monkeypatch.setattr(omega_k, "_particao", decline)
        monkeypatch.setattr(omega_k, "_certifica", spy)
        if not skip:
            monkeypatch.setattr(omega_k, "_first_live_q", lambda pm: 2)
        omega_k._certifica(C, s, lo, StatsK(), fixos, {}, {}, hi)
        monkeypatch.undo()
        return seen[1:]

    for C, s, lo, fixos, hi in [([5, 7, 11, 13, 31], 2, 31, {5: 2}, None), ([5, 7, 11, 13, 31], 1, 31, {5: 2}, None),
                                ([5, 7, 11, 13, 31], 2, 31, {5: 2}, 150), ([5, 7, 11, 13, 31, 331], 1, 331, {5: 2}, None),
                                ([5, 7, 11, 13, 31, 97], 2, 97, {5: 2}, 60000)]:
        com = children(C, s, lo, fixos, hi, True)
        sem = children(C, s, lo, fixos, hi, False)
        assert com == sem, (C, s, hi)


@pytest.mark.parametrize("cfg", [
    {},                                   # default strategy
    {"LIMIAR_INDICE": 10**12},            # never split, never use the finite exponent bound
    {"LIMIAR_INDICE": 0},                 # split / bound wherever applicable
    {"R_CHEAP_PROP9": 0},                 # no "cheap primes first" preference
    {"FATORA_BITS": 40},                  # tiny factoring budget: more unfactored residues
])
def test_block7_verdict_does_not_depend_on_the_strategy(monkeypatch, cfg):
    # the strategy thresholds only choose between sound alternatives: every variant
    # must certify k = 6 and k = 7 (no friend, no NaoCertificavel); trees may differ
    for name, value in cfg.items():
        monkeypatch.setattr(omega_k, name, value)
    for f in (omega_k._divisao_pequena, omega_k._classifica_cofator, omega_k._fatora, omega_k._phi_valor):
        f.cache_clear()
    for k in (6, 7):
        st = certifica_omega(k, light=True)
        assert st.amigos == [] and st.assinaturas_testadas == 0
        assert st.pins == [] and st.conjuntos == [] and st.n_pins > 0     # light mode: counters only
    if cfg == {"LIMIAR_INDICE": 0}:
        assert st.splits > 0 and st.dead_hi > 0 and st.cor6_ramos > 0     # the new paths really ran
    for f in (omega_k._divisao_pequena, omega_k._classifica_cofator, omega_k._fatora, omega_k._phi_valor):
        f.cache_clear()


def test_total_closure_lemma_needs_every_piece_examined(monkeypatch):
    # Found by the adversarial panel of Block 7: sigma(5^210) = Phi_211(5) has degree
    # 210 > GRAU_PHI_MAX, so the piece is skipped; with every known exponent fixed the
    # total-closure lemma used to kill the node although "no new prime" was never
    # verified. The lemma must not fire when a piece was skipped.
    st = StatsK()
    try:
        casos = omega_k._particao([5], 15, 5, st, {5: 210}, {}, {})
    except NaoCertificavel:
        casos = "open"
    assert st.fecho_total_mortos == 0
    assert casos != []
    # same node shape with every piece examined: the lemma still fires
    monkeypatch.setattr(omega_k, "_novos_de_sigma", lambda *a, **k: ((), 0))
    st = StatsK()
    assert omega_k._particao([5, 7, 11], 2, 11, st, {5: 2, 7: 2, 11: 2}, {}) == []
    assert st.fecho_total_mortos == 1


def test_block7_ramos_expoente_dead_when_prod_min_exceeds_target():
    # P0 > 9/5: the case is dead ([]), not a tail that leaves the node unchanged
    from core.omega_k import _prod_min_sup, _ramos_expoente
    C = [5, 7, 11, 13, 17]
    assert _prod_min_sup(C, {5: 2}, {})[0] > Fraction(9, 5)
    assert _ramos_expoente(C, {5: 2}, {}, {}) == []
    assert _ramos_expoente(C, {5: 2, 7: 2, 11: 2, 13: 2, 17: 2}, {}, {}) == []     # no free prime
    # with hi: the virtual factor alone can push a live node over the target
    C = [5, 7, 11, 13, 31]
    assert _prod_min_sup(C, {5: 2}, {})[0] < Fraction(9, 5)
    assert _ramos_expoente(C, {5: 2}, {}, {}, 37) == []


def test_block7_vacuous_hi_interval_is_dead():
    # (19, 20] holds no prime: the smallest unknown cannot exist (reviewer's example)
    st = StatsK()
    omega_k._certifica([5, 7, 11, 19, 71], 2, 19, st, {5: 4}, {}, {}, 20)
    assert st.dead_hi == 1 and st.nos == 1
    # (19, 23] holds 23, but 23 in C leaves nothing either
    st = StatsK()
    omega_k._certifica([5, 7, 11, 19, 23], 2, 19, st, {5: 4}, {}, {}, 23)
    assert st.dead_hi == 1 and st.nos == 1


def test_block7_solver_declines_beyond_the_size_gate(monkeypatch):
    # large ell: Phi_ell(U_max) would have (ell-1)·bits(U_max) bits; the solver must
    # decline as a whole (None), never skip the single ell
    from core.omega_k import _ultimo_desconhecido
    C = [5, 7, 11, 13, 31]
    ps = omega_k._prod_min_sup(C, {5: 2}, {})[1]
    assert _ultimo_desconhecido(C, 31, {5: 2}, 0, 0, ps) is not None
    monkeypatch.setattr(omega_k, "SOLVER_BITS", 10)
    assert _ultimo_desconhecido(C, 31, {5: 2}, 0, 0, ps) is None
    assert _ultimo_desconhecido(C, 31, {5: 2}, 0, 1, ps) is None


def test_block7_index_loop_refuses_huge_spans(monkeypatch):
    def decline(*a, **k):
        raise NaoCertificavel("declined")

    monkeypatch.setattr(omega_k, "_particao", decline)
    monkeypatch.setattr(omega_k, "MAX_INDEX_SPAN", 50)
    with pytest.raises(NaoCertificavel, match="MAX_INDEX_SPAN"):
        omega_k._certifica([5, 7, 11, 13, 31], 2, 31, StatsK(), {5: 2}, {}, {}, None)


# ---------------------------------------------------------------------------
# Block 7, follow-up of the adversarial panel
# ---------------------------------------------------------------------------

_TREE_COUNTERS = ["nos", "mortos_min", "ramo_i", "particoes", "ramos_expoente", "caudas",
                  "ultimos_resolvidos", "candidatos_ultimo", "cor6_ramos", "cor6_mortos",
                  "fecho_total_mortos", "splits", "dead_hi", "conjuntos_completos",
                  "completos_mortos_indice", "conjuntos_com_primo_grande",
                  "assinaturas_testadas", "n_pins"]


def test_casos_ell_feeder_cap_gives_the_same_case_list(monkeypatch):
    # The per-feeder cap k_max[q] only skips assignments that _fecha kills at its
    # first test. Every distinct real call of the k <= 7 trees whose UNPRUNED
    # enumeration is affordable must return the same list, in the same order.
    from math import comb
    orig = omega_k._casos_ell
    calls = []

    def spy(C, s, lo, ell, T, fixos, sem_fecho=None):
        calls.append((list(C), s, lo, ell, T, dict(fixos)))
        return orig(C, s, lo, ell, T, fixos, sem_fecho)

    monkeypatch.setattr(omega_k, "_casos_ell", spy)
    for k in (5, 6, 7):
        certifica_omega(k, light=True)
    monkeypatch.setattr(omega_k, "_casos_ell", orig)
    seen, compared, capped = set(), 0, 0
    for C, s, lo, ell, T, fixos in calls:
        key = (tuple(C), s, lo, ell, T, tuple(sorted(fixos.items())))
        livres = sum(1 for q in C if q % ell == 1 and q not in fixos)
        if key in seen or comb(T + livres, livres) > 3000:
            continue
        seen.add(key)
        pruned = orig(C, s, lo, ell, T, fixos)
        monkeypatch.setattr(omega_k, "_PRUNE_FEEDERS", False)
        full = orig(C, s, lo, ell, T, fixos)
        monkeypatch.setattr(omega_k, "_PRUNE_FEEDERS", True)
        assert pruned == full, (C, s, lo, ell, T, fixos)
        compared += 1
        capped += livres >= 1 and T > s + 1
    assert compared >= 300 and capped >= 30, (compared, capped)


def test_feeder_cap_does_not_change_the_tree(monkeypatch):
    # same tree with and without the cap (only the counter of skipped closures, which
    # used to be incremented inside doomed assignments, may differ)
    base = certifica_omega(7, light=True)
    monkeypatch.setattr(omega_k, "_PRUNE_FEEDERS", False)
    full = certifica_omega(7, light=True)
    for f in _TREE_COUNTERS:
        assert getattr(base, f) == getattr(full, f), f
    assert base.amigos == full.amigos == []


def test_casos_ell_large_budget_node_is_instant():
    # Found by the adversarial panel (and by the k = 9 run stalling): the child a1 = 54
    # of the k = 9 root has T = 53 and 7 free feeders, i.e. C(60, 7) = 386 206 920
    # unpruned assignments (hours). With the per-feeder cap it is immediate.
    C = [5, 11, 71, 103511, 511831, 12207031, 65628751, 190295821]
    n = (5**55 - 1) // 4                     # sigma(5^54): exactly the primes of C \ {5}
    for q in C[1:]:
        assert n % q == 0
        while n % q == 0:
            n //= q
    assert n == 1
    assert set(omega_k._casos_ell(C, 1, 5, 5, 53, {5: 54})) == {("pin", (3221,)), ("aberto", 53)}
    st = StatsK()
    omega_k._certifica(C, 1, 5, st, {5: 54}, {}, {})
    assert st.amigos == [] and st.nos <= 4
    # the a1 = 34 child (18 643 560 unpruned assignments, 581 s before the cap)
    C = [5, 11, 71, 211, 631, 4201, 19531, 85280581]
    st = StatsK()
    omega_k._certifica(C, 1, 5, st, {5: 34}, {}, {})
    assert st.amigos == [] and st.nos <= 10


def test_casos_ell_refuses_too_many_assignments(monkeypatch):
    # no silent stall: beyond MAX_ASSIGNMENTS the node is refused, never enumerated
    args = ([5, 11, 31, 41, 61], 3, 61, 5, 9, {5: 10})
    assert omega_k._casos_ell(*args) is not None
    monkeypatch.setattr(omega_k, "MAX_ASSIGNMENTS", 3)
    with pytest.raises(NaoCertificavel, match="MAX_ASSIGNMENTS"):
        omega_k._casos_ell(*args)


def test_iroot_is_the_exact_floor_root():
    import random
    from core.omega_k import _iroot
    for e in range(1, 8):
        for n in range(0, 3000):
            r = _iroot(n, e)
            assert r**e <= n < (r + 1) ** e, (n, e)
    rng = random.Random(7)
    for _ in range(400):
        e = rng.randint(2, 40)
        r = rng.getrandbits(rng.randint(2, 300)) + 2
        for n in (r**e - 1, r**e, r**e + 1):
            x = _iroot(n, e)
            assert x**e <= n < (x + 1) ** e, (n, e)


def test_prime_power_cofactors_are_classified_exactly():
    # Panel finding: sympy.perfect_power decides odd exponents with a float filter for
    # bases below 2^40; a false negative would turn a prime power r^e into "composite"
    # (>= 2 unknown primes) and could kill a node falsely. The test is now exact.
    from sympy import nextprime, prevprime
    from core.omega_k import _classifica_cofator, _novos_e_resto, _phi_valor, _prime_power_base
    assert _prime_power_base(3**5) == 3 and _prime_power_base(2**10) == 2
    assert _prime_power_base(36) is None and _prime_power_base(7) is None
    bases = [100003, int(prevprime(2**20)), int(nextprime(2**33)), int(prevprime(2**40)),
             int(nextprime(2**40)), int(prevprime(2**61))]
    for p in bases:
        for e in (2, 3, 5, 7, 11, 13, 16):
            assert _classifica_cofator(p**e) == ("potencia", p), (p, e)
            assert _classifica_cofator(p**e + 2 * p)[0] != "potencia"
        q = int(nextprime(p))
        assert _classifica_cofator(p * q) == ("composto", 0)
        assert _classifica_cofator(p**2 * q) == ("composto", 0)
        assert _classifica_cofator(p**3 * q**3) == ("composto", 0)
        assert _classifica_cofator(p) == ("primo", p)
    # a genuine prime-square cofactor: Phi_3(2288805793) = 3 · 1321442641^2 is ONE new
    # prime, alive with a single slot
    val = _phi_valor(3, 2288805793)
    assert val == 3 * 1321442641**2 and isprime(1321442641)
    assert _novos_e_resto(val, {3, 5, 2288805793}, 1) == ((1321442641,), 1)


def test_unknown_count_does_not_depend_on_the_order_of_the_fixed_primes():
    # False kill latent since Block 4 (found on the Block 6 code): a pin identified from a
    # LATER fixed prime that divides the unfactored residue of an EARLIER one was counted
    # twice (1 pin + 2 for the residue > s = 2). sigma(20849069^4) = 262321 · Q (98 bits,
    # beyond the factoring budget) and sigma(97^4) = 11 · 31 · 262321:
    # the closure needs exactly the two new primes {262321, Q}. Both insertion orders
    # must give that pin (the coprime-base refinement strips the pin from the residue).
    Q = 720300353869246791671341
    assert isprime(Q) and sigma_pp(97, 4) == 11 * 31 * 262321
    assert sigma_pp(20849069, 4) % (262321 * Q) == 0
    C = [5, 7, 11, 13, 31, 97, 60013, 20849069]
    for fixos in ({5: 2, 20849069: 4, 97: 4}, {5: 2, 97: 4, 20849069: 4}):
        casos = omega_k._particao(C, 2, 60013, StatsK(), fixos, {})
        assert [c.pins for c in casos] == [(262321, Q)], fixos


def test_big_prime_lemma_composite_case_against_brute_force():
    # Case (B1) with ord_r(p) = m composite and m not an order modulo any small prime
    # of S: m is found from the divisors of e (m = ell·e) without factoring ell·e.
    # Truth by brute force: sigma(p^a) supported on S + {3}.
    from core.omega_k import _expoentes_com_primo_grande
    casos = [(11, 9, 1772893, [5, 7, 11, 19]), (13, 9, 1609669, [5, 13, 61]),
             (11, 15, 195019441, [5, 7, 11, 19, 3221]), (17, 15, 6566760001, [5, 17, 307, 88741])]
    for p, m, r, S_peq in casos:
        assert int(n_order(p, r)) == m
        assert all(int(n_order(p, q)) != m for q in S_peq if q != p)
        S = set(S_peq) | {r, 3}
        validos = []
        for a in range(2, 61, 2):
            n = sigma_pp(p, a)
            for q in S:
                while n % q == 0:
                    n //= q
            if n == 1:
                validos.append(a)
        assert m - 1 in validos
        exps = _expoentes_com_primo_grande(p, frozenset(S_peq), r, frozenset({3}), 1)
        assert [a for a in exps if a <= 60] == validos, (p, m)


def test_casos_ell_guard_counts_the_assignments_exactly(monkeypatch):
    # The guard must not refuse because of the crude product of (k_max + 1): with a
    # small budget T the vectors with sum <= T are few. ell = 3, T = 2, six feeders:
    # the product is up to 3^6 = 729, the enumeration at most C(8, 2) = 28 vectors.
    from itertools import product
    C = [5, 7, 13, 19, 31, 37, 43]
    args = (C, 1, 43, 3, 2, {5: 2})
    feeders = [q for q in C if q % 3 == 1]
    assert len(feeders) == 6

    def cap(q):      # the per-feeder cap, recomputed from its definition (s = 1, T = 2)
        k, missing = 0, 0
        while k < 2:
            if not any(omega_k._ordem_e_potencia(q, r, 3, k + 1) for r in C if r != q):
                if missing == 1:
                    break
                missing += 1
            k += 1
        return k

    caps = [cap(q) for q in feeders]
    exact = sum(1 for v in product(*[range(c + 1) for c in caps]) if sum(v) <= 2)
    crude = 1
    for c in caps:
        crude *= c + 1
    assert exact < crude
    reference = omega_k._casos_ell(*args)
    monkeypatch.setattr(omega_k, "MAX_ASSIGNMENTS", exact)          # crude > limit, exact fits
    assert omega_k._casos_ell(*args) == reference
    monkeypatch.setattr(omega_k, "MAX_ASSIGNMENTS", exact - 1)
    with pytest.raises(NaoCertificavel, match=f"{exact} budget assignments"):
        omega_k._casos_ell(*args)


def test_teichmuller_minima_match_the_direct_definition():
    # m_a(r) = min_{y = 2..r-1} (y^(r^(a-1)) mod r^a). The certifier computes these
    # minima incrementally (one exponentiation by r per residue and level) and extends
    # a cached list in place; compare with the definition, in several call orders.
    from sympy import primerange

    def direct(r, a):
        return min(pow(y, r ** (a - 1), r ** a) for y in range(2, r))

    for order in ((2, 3, 4, 5), (5, 2, 4, 3), (4, 5, 3, 2)):
        omega_k._TEICH_MIN.clear()
        for r in primerange(5, 60):
            for a in order:
                assert omega_k._min_residuo_teichmuller(r, a) == direct(r, a), (r, a, order)
    omega_k._TEICH_MIN.clear()
    for r in (331, 1009):
        for a in (3, 2):
            assert omega_k._min_residuo_teichmuller(r, a) == direct(r, a), (r, a)
    # the extension driven by a bound L (the one the certifier uses) gives the same list
    omega_k._TEICH_MIN.clear()
    for r in (7, 11, 31, 97):
        mins = list(omega_k._teich_minima(r, L=10**6))
        assert mins[-1] > 10**6 and all(m <= 10**6 for m in mins[:-1])
        assert mins == [direct(r, a) for a in range(2, len(mins) + 2)]
        assert omega_k._nivel_wieferich_max(r, 10**6) == len(mins)
    omega_k._TEICH_MIN.clear()
