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


def test_pinning_refuses_an_inadmissible_target(monkeypatch):
    # Block 8: the partition is generic; 2 is refused because no odd square N with
    # 3 ∤ N has an even numerator in I(N) (core.omega_k._alvo_de).
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


def test_phi_valor_de_ordem_composta_contra_o_produto_de_moebius():
    # Phi_d(q) for an order d with two or more distinct primes is the only value _phi_valor
    # takes from sympy (cyclotomic_poly with an integer in place of the generator).
    # Independent reference in integers: Phi_d(q) = prod_{e | d} (q^e - 1)^mu(d/e). Every
    # odd d (the exponents of N are even, so d | a + 1 is odd) with phi(d) <= GRAU_PHI_MAX,
    # and both gates: None exactly when phi(d) > GRAU_PHI_MAX or the value has more than
    # PIN_BITS bits.
    from math import isqrt
    from core.omega_k import GRAU_PHI_MAX, PIN_BITS, _phi_valor
    N = GRAU_PHI_MAX**2  # phi(d) >= sqrt(d) for d > 6: nothing above
    menor = list(range(N + 1))  # least prime factor, by our own sieve
    for p in range(2, isqrt(N) + 1):
        if menor[p] == p:
            for m in range(p * p, N + 1, p):
                if menor[m] == m:
                    menor[m] = p

    def fatores(n):
        f = {}
        while n > 1:
            p = menor[n]
            f[p] = f.get(p, 0) + 1
            n //= p
        return f

    def totiente(n):
        for p in fatores(n):
            n = n // p * (p - 1)
        return n

    def mu(n):
        f = fatores(n)
        return 0 if any(e > 1 for e in f.values()) else (-1) ** len(f)

    def referencia(d, q):
        num = den = 1
        for e in range(1, d + 1):
            if d % e == 0 and mu(d // e) == 1:
                num *= q**e - 1
            elif d % e == 0 and mu(d // e) == -1:
                den *= q**e - 1
        assert num % den == 0
        return num // den

    for m in (15, 45, 105):  # the reference itself: prod_{d | m} = q^m - 1
        prod = 1
        for d in range(1, m + 1):
            if m % d == 0:
                prod *= referencia(d, 7)
        assert prod == 7**m - 1
    compostas = [d for d in range(3, N + 1, 2)
                 if len(fatores(d)) >= 2 and totiente(d) <= GRAU_PHI_MAX]
    assert compostas[:6] == [15, 21, 33, 35, 39, 45] and len(compostas) == 76
    nulos = 0
    for q in (5, 11, 100003, 2**61 - 1, 10**40 + 121):
        for d in compostas:
            ref = referencia(d, q)
            val = _phi_valor(d, q)
            if ref.bit_length() > PIN_BITS:
                assert val is None, (d, q)
                nulos += 1
            else:
                assert type(val) is int and val == ref, (d, q)
    assert nulos > 0  # the size gate was exercised
    assert all(_phi_valor(d, 5) is None for d in range(3, 2000, 2) if totiente(d) > GRAU_PHI_MAX)


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
    # The cases (A)/(B2)/(B1) of the header are a second derivation of the exponent
    # lists, without ord_r(p). With "large" forced to r - 1 above 12 bits, the real
    # complete sets of k = 7 enter the large-prime branch. In general its lists are a
    # SUBSET of the direct ones (it also uses v_r(sigma(N)) <= A_r for the large prime r);
    # every exponent the subset drops must need r^v with v > A_r. On the 13 sets of k = 7
    # the large prime itself has no admissible exponent (as on the 201 large-prime sets of
    # k = 9), so _listas_expoentes returns None before any other list is composed: the
    # first loop checks only the counter and the early return. The second loop compares
    # the lemma itself with the direct closure, for every prime r of each set whose own
    # list is non-empty (the lemma never factors r - 1, so it holds for any prime r of
    # the set). The planted sets after it are the ones where _listas_expoentes composes
    # the lists.
    from core.cadeias import v_p, v_q_sigma_direto
    from core.omega_k import _expoentes_com_primo_grande, _listas_expoentes
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
        # the large prime has no admissible exponent: the set dies before any other list
        # is composed (a data check on these sets, not a lemma)
        assert direto[C.index(grandes[0])] == [] and via_nova is None, C
    assert exercitados == 13
    num, den = omega6.ALVO.numerator, omega6.ALVO.denominator
    comparados = exigidos = via_r = 0
    for C in conjuntos:
        fs = frozenset(C)
        direto = {p: expoentes_validos_ordens(p, fs, extras) for p in C}
        for r in C:
            if not direto[r]:
                continue
            A_r = max(direto[r]) + v_p(r, num) - v_p(r, den)
            for p in C:
                if p == r:
                    continue
                nova = _expoentes_com_primo_grande(p, fs - {r}, r, extras, A_r)
                devidos = {a for a in direto[p] if v_q_sigma_direto(r, p, a) <= A_r}
                assert devidos <= set(nova) <= set(direto[p]), (C, p, r, A_r)
                comparados += 1
                exigidos += len(devidos)
                via_r += sum(1 for a in devidos if v_q_sigma_direto(r, p, a) > 0)
    # 498 comparisons, 99 required exponents, 44 of them with r | sigma(p^a) (the lemma
    # must find those without ord_r(p) from r - 1)
    assert comparados >= 450 and exigidos >= 90 and via_r >= 40
    # Planted complete sets (target t = I(N0); extras taken at the default ORDEM_BITS) whose
    # designated large prime HAS an admissible exponent: every other list is composed by
    # the lemma, with A_r = max(list of r) + v_r(num) - v_r(den), and must equal the
    # direct one and keep the planted exponent.
    chamadas = []
    lema = omega_k._expoentes_com_primo_grande
    monkeypatch.setattr(omega_k, "_expoentes_com_primo_grande",
                        lambda *a: chamadas.append(a[0]) or lema(*a))
    for sig, bits in (({5: 2, 7: 2, 67: 4}, 6), ({5: 2, 37: 2, 67: 4}, 6),
                      ({5: 2, 7: 2, 13: 4, 47: 2}, 5)):
        monkeypatch.setattr(omega6, "ALVO", _I(sig))
        monkeypatch.setattr(omega_k, "ORDEM_BITS", 80)
        extras = omega_k._alvo()[0]
        monkeypatch.setattr(omega_k, "ORDEM_BITS", bits)
        C = sorted(sig)
        assert omega_k._grandes(C) == [max(C)]
        fs = frozenset(C)
        direto = [expoentes_validos_ordens(p, fs, extras) for p in C]
        del chamadas[:]
        via_nova = _listas_expoentes(C, extras, StatsK(), {}, {})
        assert via_nova == direto and sorted(chamadas) == C[:-1], sig
        assert all(sig[p] in lista for p, lista in zip(C, via_nova)), sig
        # an empty list for a prime other than r kills the set (5 is fixed outside its list)
        assert _listas_expoentes(C, extras, StatsK(), {5: 4}, {}) is None


def test_conjunto_com_primo_grande_pode_ser_mais_estrito_que_o_fecho_direto(monkeypatch):
    # N0 = 5^6 31^4 with 31 forced to be the large prime: t = I(N0) has 31^4 in den, so
    # v_31(sigma(N)) = a_31 - 4 and A_r = 4 - 4 = 0 on the complete set {5, 31}. The direct
    # closure keeps a_5 = 2 (sigma(25) = 31 lies in S); the large-prime route drops it, since
    # it needs 31 | sigma(N). Its lists are a strict subset, and N0 is still found.
    from core.cadeias import v_q_sigma_direto
    from core.omega_k import _listas_expoentes
    monkeypatch.setattr(omega6, "ALVO", I_pp(5, 6) * I_pp(31, 4))
    monkeypatch.setattr(omega_k, "_grandes", lambda C: [31] if 31 in C else [])
    extras = omega_k._alvo()[0]
    assert expoentes_validos_ordens(5, frozenset({5, 31}), extras) == [2, 6]
    assert expoentes_validos_ordens(31, frozenset({5, 31}), extras) == [4]
    st = StatsK()
    assert _listas_expoentes([5, 31], extras, st, {}, {}) == [[6], [4]]
    assert st.conjuntos_com_primo_grande == 1 and v_q_sigma_direto(31, 5, 2) == 1
    st = StatsK(k=2)
    omega_k._certifica([5, 31], 0, 31, st, {}, {}, {}, None)
    assert {5: 6, 31: 4} in st.amigos


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


def test_light_is_kept_when_a_stats_object_is_passed():
    # certifica_omega(k, stats=..., light=True) keeps counters only, as without stats
    st = certifica_omega(5, stats=StatsK(), light=True)
    assert st.light and st.pins == [] and st.conjuntos == [] and st.n_pins > 0


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
    # Structural properties of the tail branching on LIVE nodes (prod_min < 9/5 < prod_sup,
    # both times v(hi) when hi is set), a1 = 2 fixed: one prime q is branched, its exact
    # exponents are min_q, min_q + 2, ..., A - 2 and the tail is a_q >= A with A > min_q
    # (A <= M_q under an upper bound). The tail can be missing only under an odd upper
    # bound M_q (Cor. 6 stores its raw bound), and then the exact exponents run up to
    # M_q - 1. maximos travel unchanged. Every case must run: until Block 8 this test
    # listed four nodes, three of them dead (prod_min >= 9/5), and skipped them in silence.
    from core.omega_k import _prod_min_sup, _ramos_expoente, _virtual
    ALVO = Fraction(9, 5)
    casos = [  # (C, minimos, maximos, hi)
        ([5, 7, 11, 13, 31, 89], {}, {}, None),
        ([5, 7, 11, 13, 31, 71], {}, {}, None),
        ([5, 7, 11, 13, 37, 61], {}, {}, None),
        ([5, 7, 11, 13, 41, 89, 97], {}, {}, None),
        ([5, 7, 11, 19, 29, 37, 131], {}, {}, None),    # two exact values, a7 = 2, 4
        ([5, 7, 11, 19, 31, 37, 101], {}, {}, None),    # two exact values, a7 = 2, 4
        ([5, 7, 11, 13, 31, 89], {}, {11: 4}, None),
        ([5, 7, 11, 13, 31, 89], {}, {11: 2}, None),    # the cap moves the branching to 13
        ([5, 7, 11, 13, 31, 89], {}, {13: 6}, None),
        ([5, 7, 11, 19, 29, 37, 131], {}, {7: 4}, None),  # the cap moves the branching to 11
        ([5, 7, 11, 19, 29, 37, 131], {}, {7: 8}, None),  # even cap: the tail is kept
        ([5, 7, 11, 19, 29, 37, 131], {}, {7: 5}, None),  # odd cap: no tail
        ([5, 7, 11, 13, 31, 89], {11: 4}, {}, None),    # a tail state
        ([5, 7, 11, 13, 31, 89], {}, {}, 10**6),        # under hi
    ]
    fixos = {5: 2}
    sem_cauda = varios = 0
    for C, minimos, maximos, hi in casos:
        prod_min, prod_sup = _prod_min_sup(C, fixos, minimos, maximos)
        if hi is not None:
            prod_min, prod_sup = prod_min * _virtual(hi), prod_sup * _virtual(hi)
        assert prod_min < ALVO < prod_sup, (C, minimos, maximos, hi)   # live: never skipped
        ramos = _ramos_expoente(C, fixos, minimos, maximos, hi)
        assert ramos and all(mx == maximos for _, _, mx in ramos)
        exatos = [f for f, m, _ in ramos if m == minimos]
        caudas = [(f, m) for f, m, _ in ramos if m != minimos]
        assert len(caudas) <= 1
        (q,) = {p for f in exatos for p in f if p not in fixos} | \
               {p for _, m in caudas for p in m if m.get(p) != minimos.get(p)}
        assert all(f == {**fixos, q: f[q]} for f in exatos)
        amin, M = minimos.get(q, 2), maximos.get(q)
        if caudas:
            f, m = caudas[0]
            A = m[q]
            assert f == fixos and m == {**minimos, q: A}
            assert A % 2 == 0 and A > amin and (M is None or A <= M)
            assert sorted(f[q] for f in exatos) == list(range(amin, A, 2))   # partition of a_q
        else:
            assert M is not None and M % 2 == 1
            assert sorted(f[q] for f in exatos) == list(range(amin, M + 1, 2))
            sem_cauda += 1
        varios += len(exatos) >= 2
    assert sem_cauda >= 1 and varios >= 3


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

def test_planted_k7_above_every_prod_sup_of_6_primes(monkeypatch):
    # alvo plantado com I(N0) acima de qualquer prod_sup de 6 primos (máximo
    # {5,7,11,13,17,19} = 1.949) e a assinatura de 7 primos tem de ser encontrada.
    # Until Block 7 the partition refused any target other than 9/5 and every node fell
    # into branch (i); since Block 8 it is generic (see tests/test_planted.py): here it
    # runs at 26 of the 30 nodes, and branch (i) is still taken at 18.
    assin = {5: 2, 7: 2, 11: 2, 13: 2, 17: 2, 19: 2, 23: 2}
    alvo = _I(assin)
    assert alvo > Fraction(5, 4) * Fraction(7, 6) * Fraction(11, 10) * Fraction(13, 12) \
        * Fraction(17, 16) * Fraction(19, 18)
    monkeypatch.setattr(omega6, "ALVO", alvo)   # fonte única: omega_k lê omega6.ALVO
    st = certifica_omega(7)
    assert assin in st.amigos
    assert st.particoes > 0     # Block 8: the partition is generic and now runs here too
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

def _bruto_ultimo(C, lo, ell, eps, U_max, caps=None):
    """Força bruta independente: primos U em (lo, U_max] fora de C tais que
    Phi_ell(U) = ell^eps · (produto de primos de C_ell), with e_q <= caps[q] for every q
    of C_ell that has a cap (the same specification as the exp_max of _solucoes_phi)."""
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
        acima = False
        for q in C_ell:
            e = 0
            while R % q == 0:
                R //= q
                e += 1
            acima = acima or (caps is not None and q in caps and e > caps[q])
        if R == 1 and not acima:
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
                esperado = _bruto_ultimo(C, lo, ell, eps, U_max, fixos)
                obtido = sorted(_solucoes_phi(ell, eps, C_ell, _phi_primo(ell, U_max), fixos, lo, set(C)))
                assert obtido == esperado, (C, ell, eps, obtido, esperado)
                encontrados.update(esperado)
    assert 67 in encontrados       # não-vacuidade: 67^2 + 67 + 1 = 3·7^2·31 em {5,7,11,13,31}
    # The capped case above, {5, 7, 13, 19, 31} with a_7 = 2, is empty (U_max = 18 < 37), so
    # no cap is reached there. A cap that binds: Phi_3(67) = 3·7^2·31 with U_max = 96.
    C, lo, U_max = [5, 7, 11, 13, 31], 31, 96
    for caps, want in (({7: 2}, [67]), ({7: 3}, [67]), ({7: 1}, []), ({31: 1}, [67]),
                       ({31: 0}, [])):
        obtido = sorted(_solucoes_phi(3, 1, [7, 13, 31], _phi_primo(3, U_max), caps, lo, set(C)))
        assert obtido == _bruto_ultimo(C, lo, 3, 1, U_max, caps) == want, caps


def test_ultimo_desconhecido_resolve_o_no_quase_justo_de_k9(monkeypatch):
    # C = {5,7,11,13,31,97,52361}, a1 = 2: prod_sup = 9/5 - 1,8e-8 e o índice só
    # limita U por U < 1,03e8 (5,9 milhões de primos). O solver enumera vetores de
    # expoentes e extrai raízes inteiras, without enumerating the interval (a deterministic
    # guard instead of a wall-clock limit: no primerange, a handful of nextprime calls).
    from core.omega_k import _cota_indice_U, _prod_min_sup, _ultimo_desconhecido
    C = [5, 7, 11, 13, 31, 97, 52361]
    prod_sup = _prod_min_sup(C, {5: 2}, {})[1]
    assert _cota_indice_U(prod_sup) > 10**8
    calls, real_next = [], omega_k._proximo_primo

    def counted_next(n):
        calls.append(n)
        return real_next(n)

    def no_enumeration(*args):
        raise AssertionError(f"primerange{args} called by the solver")

    monkeypatch.setattr(omega_k, "_proximo_primo", counted_next)
    monkeypatch.setattr(omega_k, "primerange", no_enumeration)
    for k5, k3 in [(1, 0), (0, 1), (0, 0), (1, 2)]:
        cands = _ultimo_desconhecido(C, 52361, {5: 2}, k5, k3, prod_sup)
        assert cands is not None
        assert all(isprime(U) and U > 52361 for U in cands)
    assert len(calls) < 1000                      # the interval holds 5.9 million primes
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
    # para r pequeno e todo primo q <= L, w_r(q) <= _nivel_wieferich_max(r, L)
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
    # Coverage: prefix nodes (C = the smallest primes of the friend, lo = max(C)) of three
    # planted friends, s in {0, 1, 2}, a1 and p_2 fixed or free, no maximos. L is the bound
    # the certifier computes (L1 for s = 1, the B_min form for s = 2 with lo >= B_min),
    # asserted to bound the planted unknowns, and A_r must be >= the true exponent of r.
    # s >= 3 (and s = 2 with lo < B_min) has no uniform L and is skipped. The bound with
    # attained upper bounds (maximos) is tested in tests/test_planted.py.
    from core.omega_k import _cota_L_desconhecidos, _cota_expoente_conhecido
    assinaturas = [
        {5: 2, 7: 2, 11: 2, 13: 2, 17: 2, 19: 2, 23: 4},
        {5: 4, 7: 2, 11: 6, 13: 2, 17: 2, 19: 4, 23: 2},
        {5: 2, 7: 8, 11: 2, 13: 4, 17: 2, 19: 2, 23: 2, 29: 2},
    ]
    feitos = {0: 0, 1: 0, 2: 0}
    for assin in assinaturas:
        alvo = _I(assin)
        monkeypatch.setattr(omega6, "ALVO", alvo)
        primos = sorted(assin)
        for n_conhecidos in range(len(primos), 2, -1):
            C = primos[:n_conhecidos]
            s = len(primos) - n_conhecidos
            for fixos in ({}, {5: assin[5]}, {5: assin[5], primos[1]: assin[primos[1]]}):
                cotas = _cota_L_desconhecidos(C, s, fixos, {}, None, None, max(C)) if s else None
                if s and (cotas is None or cotas[2] is None):
                    continue        # no uniform L for the unknowns at this node
                L = None if cotas is None else cotas[2]
                assert L is None or L >= max(primos), (assin, C, s, fixos, cotas)
                for r in C:
                    if r in fixos:
                        continue
                    A = _cota_expoente_conhecido(r, C, s, fixos, L)
                    if A is None:
                        continue
                    assert A >= assin[r], (assin, C, s, fixos, r, A)
                    feitos[s] += 1
    assert all(feitos.values()), feitos


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
    # the bounds of the free primes of the group examined travel in the children as
    # maximos, and the branch uses the one with fewest branches
    mx = ramos[0][2]
    # Block 7: bounds of expensive primes (r > R_CHEAP_PROP9, here 52361) are computed
    # only when no cheap prime can be branched, so only the cheap ones travel as maximos
    assert set(mx) == {7, 11, 13, 31, 97} and all(v >= 2 for v in mx.values())
    assert r in mx
    assert max(f[r] for f, _, _ in ramos) == mx[r] - (mx[r] % 2)


def test_cor6_kill_at_a_state_of_the_k9_tree():
    # A state on which the k = 9 run kills by the finite exponent bound (cor6_mortos = 4 at
    # k = 9): a_17 >= 12 was committed by a tail, and the bound gives A_17 = 8 < 12.
    C = [5, 7, 11, 17, 19, 2213, 19531]
    fixos = {5: 6, 11: 2}
    minimos = {19531: 4, 2213: 4, 19: 12, 17: 12}
    L1, B_min, L = omega_k._cota_L_desconhecidos(C, 2, fixos, minimos, {}, None, 2213)
    assert 2213 >= B_min and L is not None
    assert omega_k._cota_expoente_conhecido(17, C, 2, fixos, L, {}) == 8 < minimos[17]
    assert omega_k._ramos_cor6(C, 2, 2213, fixos, minimos, {}) == []
    st = StatsK(k=9)
    omega_k._certifica(C, 2, 2213, st, dict(fixos), dict(minimos), {}, None)
    assert st.cor6_mortos >= 1 and st.amigos == []


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
    st = StatsK(k=9)
    omega_k._certifica(NEAR_TIGHT, 2, 52361, st, {5: 2}, {}, {}, None)
    assert st.amigos == []
    assert st.splits >= 1 and st.dead_hi >= 1 and st.cor6_ramos >= 1
    assert st.ramo_i == 0                         # the index enumeration was never needed
    assert st.nos < 500                           # (a node count, not a wall-clock limit)


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


_STRATEGY_CACHES = ("_divisao_pequena", "_classifica_cofator", "_fatora", "_phi_valor")


@pytest.fixture(scope="module")
def strategy_trees_k7():
    """The k = 7 trees of the default strategy and of LIMIAR_INDICE = 0."""
    trees = {}
    for cfg in ({}, {"LIMIAR_INDICE": 0}):
        with pytest.MonkeyPatch.context() as mp:
            for name, value in cfg.items():
                mp.setattr(omega_k, name, value)
            for f in _STRATEGY_CACHES:
                getattr(omega_k, f).cache_clear()
            st = certifica_omega(7, light=True)
        trees[tuple(cfg)] = {f: getattr(st, f) for f in _TREE_COUNTERS}
    for f in _STRATEGY_CACHES:
        getattr(omega_k, f).cache_clear()
    return trees


# At k <= 7 the default never meets a long index interval, so LIMIAR_INDICE = 10**12 and
# R_CHEAP_PROP9 = 0 alone (read only after a long interval) would run the default tree.
@pytest.mark.parametrize("cfg", [
    {},                                   # default strategy
    {"LIMIAR_INDICE": 0},                 # split / bound wherever applicable
    {"LIMIAR_INDICE": 0, "R_CHEAP_PROP9": 0},   # and no "cheap primes first" preference
    {"FATORA_BITS": 40},                  # tiny factoring budget: more unfactored residues
])
def test_block7_verdict_does_not_depend_on_the_strategy(monkeypatch, cfg, strategy_trees_k7):
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
    if cfg:      # a variant must change the k = 7 tree of the strategy it extends, or it tests nothing
        base = ("LIMIAR_INDICE",) if "R_CHEAP_PROP9" in cfg else ()
        assert {f: getattr(st, f) for f in _TREE_COUNTERS} != strategy_trees_k7[base], cfg
    if cfg.get("LIMIAR_INDICE") == 0:
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


def test_solver_root_agrees_with_the_exact_floor_root():
    # The last-unknown solver inverts Phi_ell by u = floor(R^(1/(ell - 1))) with
    # sympy.integer_nthroot, whose fallback without gmpy2 starts from a float and corrects
    # it with integer loops. A root off by one would drop the only U of a right-hand side
    # R, so it is pinned here against the exact _iroot on values shaped like the solver's,
    # up to the size gate SOLVER_BITS (u^(ell-1) < Phi_ell(u) < (u+1)^(ell-1), ell >= 3).
    import random
    from sympy import integer_nthroot
    from core.omega_k import SOLVER_BITS, _iroot, _phi_primo
    rng = random.Random(11)
    for ell in (3, 5, 7, 11, 13, 31, 101, 199):
        gate = SOLVER_BITS // (ell - 1)
        for bits in (rng.randint(2, 64), rng.randint(65, gate), gate):
            u = rng.getrandbits(bits) | 2
            P = _phi_primo(ell, u)
            assert _iroot(P, ell - 1) == u
            for R in (P - 1, P, P + 1, u ** (ell - 1) - 1, u ** (ell - 1), (u + 1) ** (ell - 1) - 1):
                assert int(integer_nthroot(R, ell - 1)[0]) == _iroot(R, ell - 1), (ell, bits)


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


def test_primos_permitidos_acima_de_10_5_saem_do_cofator():
    # _divisao_pequena removes every prime below 10^5 and none above: a permitted prime
    # above 10^5 (a large prime of C, an extra, a pin of an earlier piece) is removed by the
    # loop over `permitidos` in _novos_e_resto; counted as new it would kill falsely
    from sympy import nextprime
    from core.omega_k import _divisao_pequena, _novos_e_resto
    P, r = int(nextprime(10**12)), int(nextprime(10**15))
    assert _divisao_pequena(9 * P**2 * r) == ((3,), P**2 * r)
    assert _novos_e_resto(9 * P**2 * r, {3, P}, 1) == ((r,), 1)
    assert _novos_e_resto(7 * 100003, {7, 100003}, 0) == ((), 1)


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


def test_big_prime_lemma_with_generic_extras_against_the_exact_closure():
    # Block 8: the lemma takes extras = primes(num). Cases built from closures sigma(p^a):
    # r is one of its primes (the lemma never factors r - 1), the others are split at random
    # between S' and the extras. The lemma must return every exponent of the exact closure
    # of S' + {r} (expoentes_validos_ordens, which does factor r - 1) with
    # v_r(sigma(p^a)) <= A_r, and nothing outside that closure.
    import random
    from sympy import factorint, primerange
    from core.cadeias import v_q_sigma_direto
    from core.omega_k import _expoentes_com_primo_grande

    def strip(n, permitidos):
        for q in permitidos:
            while n % q == 0:
                n //= q
        return n

    rng = random.Random(77)
    small = [int(q) for q in primerange(5, 400)]
    compared = required = needs_extra = needs_r = 0
    for p in (5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 61, 71):
        for a in range(2, 20, 2):
            s = sigma_pp(p, a)
            if s.bit_length() > 64:
                continue
            fac = sorted(int(q) for q in factorint(s))
            big = [f for f in fac if f > p]
            if not big:
                continue
            for trial in range(4):
                r = max(big) if trial < 2 else rng.choice(big)
                rest = [f for f in fac if f != r]
                ex = frozenset(f for f in rest if rng.random() < 0.5)
                if rng.random() < 0.7:
                    ex |= {3}
                S_peq = (frozenset(rest) - ex - {3}) | {p}
                S_peq |= frozenset(q for q in rng.sample(small, rng.randrange(0, 4)) if q != r)
                fs = S_peq | {r}
                full = expoentes_validos_ordens(p, fs, ex)
                vr = {x: v_q_sigma_direto(r, p, x) for x in full}
                for A_r in sorted({max(vr.values(), default=0), 2, 40}):
                    got = _expoentes_com_primo_grande(p, S_peq, r, ex, A_r)
                    must = [x for x in full if vr[x] <= A_r]
                    assert set(must) <= set(got) <= set(full), (p, sorted(S_peq), r, sorted(ex), A_r)
                    compared += 1
                    required += len(must)
                    needs_r += sum(1 for x in must if vr[x] > 0)
                    needs_extra += sum(1 for x in must
                                       if strip(sigma_pp(p, x), (set(fs) | {3}) - {p}) != 1)
    assert compared >= 500 and needs_r >= 500 and needs_extra >= 200


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


# ---------------------------------------------------------------------------
# Block 8, whole-code pass: paths that no real run with k <= 9 executes
# ---------------------------------------------------------------------------

def test_casos_ell_kills_a_fixed_feeder_beyond_its_cap(monkeypatch):
    # 11 = 1 (mod 5) fixed at a_11 = 24 carries v5(25) = 2 levels of the budget of 5, and no
    # r in C ∪ {3} other than 11 witnesses one (ord_3(11) = 2, ord_5(11) = 1): two
    # witness-less levels need two distinct unknowns, s = 1. With the per-feeder cap
    # the assignment dies at k_fixo > k_max[q]; without it, in _fecha (len(faltam) > s).
    for T in (2, 3, 5):
        assert omega_k._casos_ell([5, 11], 1, 11, 5, T, {5: 2, 11: 24}) == [], T
        monkeypatch.setattr(omega_k, "_PRUNE_FEEDERS", False)
        assert omega_k._casos_ell([5, 11], 1, 11, 5, T, {5: 2, 11: 24}) == [], T
        monkeypatch.setattr(omega_k, "_PRUNE_FEEDERS", True)
    # one witness-less level fits one slot: a_11 = 4, Phi_5(11) = 5 · 3221 pins 3221
    assert omega_k._casos_ell([5, 11], 1, 11, 5, 1, {5: 2, 11: 4}) == [("pin", (3221,))]


def test_open_case_is_refused_when_the_index_gives_no_bound(monkeypatch):
    # target I(5^2 7^4), node C = {5, 7}, s = 1, a_5 = 2, a_7 <= 4: the pair (0, 0) stays
    # open and prod_sup = I(5^2) I(7^4) equals the target, so the index does not bound the
    # unknown: the node must be refused (no silent gap), never enumerated or dropped.
    t = I_pp(5, 2) * I_pp(7, 4)
    monkeypatch.setattr(omega6, "ALVO", t)
    assert omega_k._prod_min_sup([5, 7], {5: 2}, {}, {7: 4})[1] == t
    with pytest.raises(NaoCertificavel, match="casos abertos"):
        omega_k._certifica([5, 7], 1, 7, StatsK(k=3), {5: 2}, {}, {7: 4}, None)


def test_two_large_primes_in_a_complete_set_are_refused():
    from sympy import nextprime
    r1 = int(nextprime(2**81))
    r2 = int(nextprime(r1))
    with pytest.raises(NaoCertificavel, match="2 primos com r-1 acima"):
        omega_k._listas_expoentes([5, r1, r2], omega_k._alvo()[0], StatsK(), {}, {})


def test_target_with_an_unsplit_composite_part_is_refused(monkeypatch):
    # _fatores_do_alvo: a composite part of num or den above FATORA_BITS that Pollard rho
    # does not split is refused (never factored for hours); k < 1 is an error
    from sympy import nextprime
    p, q = int(nextprime(2**30)), int(nextprime(2**62))
    assert (p * q).bit_length() > omega_k.FATORA_BITS
    assert omega_k._fatores_do_alvo(7 * p * q) == {7: 1, p: 1, q: 1}
    monkeypatch.setattr(omega_k, "pollard_rho", lambda *a, **k: None)
    with pytest.raises(NaoCertificavel, match="was not split"):
        omega_k._fatores_do_alvo(7 * p * q)
    with pytest.raises(ValueError):
        certifica_omega(0)


def test_last_unknown_solver_declines_with_a_large_prime_in_the_pool():
    # L(C) needs the odd primes of r - 1 for every r in C ∪ extras; with r - 1 not factored
    # the set would be incomplete, so _L_de gives None and the whole solver declines
    from sympy import nextprime
    r1 = int(nextprime(2**81))
    C = [5, 7, r1]
    assert omega_k._L_de(C) is None and omega_k._L_de([5, 7]) == {3}
    ps = omega_k._prod_min_sup(C, {5: 2}, {}, {})[1]
    assert ps < Fraction(9, 5)
    assert omega_k._ultimo_desconhecido(C, r1, {5: 2}, 0, 0, ps) is None


def test_big_prime_lemma_case_b2_against_the_direct_list():
    # Case (B2): S = {5, 11, 31, 71, 181, 1741} with r = 31 designated large. The odd orders
    # of 5 modulo the other primes are D = {5, 15}; m = 15 has exactly one divisor outside
    # D, 3 = ord_31(5), so a_5 = 14 comes from (B2) alone ((A) needs every divisor in D).
    # With A_r = 1 (sigma(5^2) = 31 needs v_31 = 1) the lemma gives the direct list.
    from core.cadeias import _candidatos_m, ordens_impares
    from core.omega_k import _e_ordem, _expoentes_com_primo_grande
    S = frozenset({5, 11, 31, 71, 181, 1741})
    S_peq = S - {31}
    D = ordens_impares(5, S_peq, frozenset({3}))
    assert set(D) == {5, 15} and 15 not in _candidatos_m(D)
    assert int(n_order(5, 31)) == 3 and _e_ordem(5, 31, 3)
    direto = expoentes_validos_ordens(5, S, frozenset({3}))
    assert direto == [2, 4, 14]
    assert _expoentes_com_primo_grande(5, S_peq, 31, frozenset({3}), 1) == direto
    # without the factor 31^1 (A_r = 0) only the exponent 2 (sigma(5^2) = 31) is dropped
    assert _expoentes_com_primo_grande(5, S_peq, 31, frozenset({3}), 0) == [4, 14]


def test_new_prime_of_sigma_5_a1_at_most_lo_kills_the_case():
    # C = {5, 37}, s = 2: the range of a1 is {2} and sigma(5^2) = 31 is a new prime. With
    # lo = 5 it is a pin; with lo = 37 every prime of S up to 37 is already in C
    # (invariant of lo), so the case dies.
    assert omega_k._faixa_a1([5, 37], 2) == (2, 2)
    casos = omega_k._particao([5, 37], 2, 5, StatsK(), {}, {})
    assert [(c.pins, c.fixos) for c in casos] == [((31,), {5: 2})]
    assert omega_k._particao([5, 37], 2, 37, StatsK(), {}, {}) == []


def test_pieces_beyond_pin_bits_are_skipped_not_killed(monkeypatch):
    # The exact size gate of _phi_valor: a piece with more than PIN_BITS bits is not
    # factored; the closure loses that information (counted in sem_fecho), never kills.
    pin_bits = omega_k.PIN_BITS
    omega_k._phi_valor.cache_clear()
    monkeypatch.setattr(omega_k, "PIN_BITS", 6)
    try:
        assert omega_k._phi_valor(3, 5) == 31               # 5 bits
        assert omega_k._phi_valor(3, 11) is None             # 133 = 7 · 19: 8 bits
        sem = [0]
        assert omega_k._novos_de_sigma(11, 2, {3, 5, 11}, 1, sem) == ((), 0) and sem == [1]
        assert omega_k._novos_de_sigma(5, 2, {3, 5}, 1, sem) == ((31,), 0) and sem == [1]
    finally:
        monkeypatch.setattr(omega_k, "PIN_BITS", pin_bits)
        omega_k._phi_valor.cache_clear()
    assert omega_k._novos_de_sigma(11, 2, {3, 5, 11}, 2, [0]) == ((7, 19), 0)


def test_prop9_bound_declines_above_r_max(monkeypatch):
    # Prop. 9 costs O(r) per level: above R_MAX_PROP9 the Wieferich level of the unknowns
    # is not computed and the finite exponent bound declines (None) whenever s >= 1
    C = [5, 7, 11, 13, 31, 97, 52361]
    L = 10**6
    assert omega_k._nivel_wieferich_max(31, L) is not None
    assert omega_k._cota_expoente_conhecido(31, C, 2, {5: 2}, L) is not None
    monkeypatch.setattr(omega_k, "R_MAX_PROP9", 30)
    assert omega_k._nivel_wieferich_max(31, L) is None
    assert omega_k._cota_expoente_conhecido(31, C, 2, {5: 2}, L) is None
    assert omega_k._cota_expoente_conhecido(31, C, 0, {5: 2}, None) is not None   # no unknown
