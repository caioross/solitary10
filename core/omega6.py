"""Certificador: nenhum amigo de 10 com omega(N) = 6 (Fase 1, Bloco 2).

Arquitetura (justificativas completas em results/FASE_1.md, Bloco 2):

ESTÁGIO A — enumeração de prefixos C5 = {5 < p2 < p3 < p4 < p5} por DFS com as podas
de índice do Bloco 1 (terminação garantida: nos níveis 1..4 o limite do laço é
prod p/(p-1) de <= 4 primos <= 1001/576 < 9/5).

ESTÁGIO B — para cada prefixo vivo (prod_min < 9/5), dois ramos:

  (i) prod_sup(C5) < 9/5: o sexto primo p6 é limitado pelo índice
      (necessário sup(p6) > (9/5)/prod_sup, que falha para p6 grande — o laço
      encerra por monotonia). Cada conjunto completo S vai para a fase de
      expoentes: FECHO por ordens (core/cadeias.py) + orçamentos v3/v5 da
      equação-mestra + teste de igualdade exato 5·sigma(N) = 9·N.

  (ii) prod_sup(C5) >= 9/5: p6 (=: P) não é limitado por índice. Usa-se PINAGEM
      pela alimentação do 5 (específica do alvo 9/5; ver _ramo_ii_pinagem):
      a1 = v5(N) >= 2 dá v5(sigma(N)) = a1 - 1 >= 1, e pelo Fato 2 (fórmula de
      valuação) só bases q ≡ 1 (mod 5) alimentam o 5, com v5(sigma(q^a)) =
      v5(a+1). Logo:
        CASO q ∈ C5, q ≡ 1 (mod 5), com 5 | a_q + 1: o divisor 5 de a_q+1 é uma
          ordem ord_r(q) com r em S \\ {q} (Zsygmondy); se 5 não é ordem de q
          módulo nenhum primo CONHECIDO (5 ∉ D_q), então ord_P(q) = 5, i.e.
          P | Phi_5(q) — P fica PINADO nos fatores novos de Phi_5(q) (finitos).
          (Se 5 ∈ D_q o pin não existe e o método declara NaoCertificavel.)
        CASO só P alimenta o 5: P ≡ 1 (mod 10) e 5 | a_P + 1. Todo divisor
          d > 1 de a_P + 1 é uma ordem ord_r(P) de um primo r do conjunto
          (Zsygmondy); r != 3 e r != P (pois r ≡ 1 mod d com d ímpar >= 3, e P
          não divide Phi_d(P)), logo r ∈ C5 e d | r - 1 — o conjunto E desses m
          é finito e dá v5(a_P+1) <= v5cap; então
          a1 = 1 + v5(a_P+1) percorre um conjunto finito, e sigma(5^{a1}) tem de
          fatorar em C5 ∪ {3} ∪ {P}: o resto do strip por C5 ∪ {3} pina P
          (resto = P^v), mata o caso (>= 2 primos novos) ou, se resto = 1,
          o método declara NaoCertificavel (sem pin — nunca ocorre no alvo real).
      Cada P pinado > p5 vira o conjunto completo C5 ∪ {P}, tratado pela MESMA
      fase exaustiva do ramo (i). Pins <= p5 são descartados com solidez: um
      amigo com esse conjunto tem OUTRO prefixo-de-5-menores, coberto pela
      enumeração do Estágio A.

Honestidade estrutural: toda lacuna de cobertura detectável levanta
NaoCertificavel e NENHUM certificado é emitido.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction

from sympy import factorint, nextprime

from core.cadeias import expoentes_validos_ordens, ordens_impares, v_p
from core.motor import ALVO, I_pp, sigma_pp, sup_pp


class NaoCertificavel(Exception):
    """Cobertura não fechada mecanicamente: NADA é certificado."""


@dataclass
class Stats6:
    prefixos: int = 0
    prefixos_ramo_i: int = 0
    prefixos_ramo_ii: int = 0
    prefixos_mortos_min: int = 0
    conjuntos_completos: int = 0
    assinaturas_testadas: int = 0
    pins_testados: list[int] = field(default_factory=list)
    amigos: list[dict[int, int]] = field(default_factory=list)


def _parametros_do_alvo() -> tuple[frozenset[int], int, int, int]:
    """(extras, V3, v5_num, v5_den) lidos do ALVO corrente (módulo-global, para
    permitir testes com alvo plantado): sigma(N) = num·N/den com den | N, logo
    - fatores primos de sigma(N) ⊆ S ∪ primes(num)  (extras = primes(num));
    - para ℓ = 3 (3 ∤ N): soma_i v3(sigma(p_i^{a_i})) = v3(num) = V3;
    - v5(sigma(N)) = v5(num) + a1 - v5(den)  (v5(N) = a1).
    Para o alvo real 9/5: extras = {3}, V3 = 2, orçamento v5 = a1 - 1."""
    num = ALVO.numerator
    den = ALVO.denominator
    return (frozenset(factorint(num)), v_p(3, num), v_p(5, num), v_p(5, den))


# ---------------------------------------------------------------------------
# Estágio A — prefixos C5
# ---------------------------------------------------------------------------

def _sup_prox(depois_de: int, slots: int) -> Fraction:
    prod = Fraction(1)
    q = depois_de
    for _ in range(slots):
        q = int(nextprime(q))
        prod *= sup_pp(q)
    return prod


def _prefixos_c5() -> list[tuple[list[int], Fraction, Fraction]]:
    """Todos os C5 = [5, p2..p5] que sobrevivem às podas de índice do espaço k=6.
    Retorna (prefixo, prod_sup, prod_min)."""
    out: list[tuple[list[int], Fraction, Fraction]] = []

    def dfs(escolhidos: list[int], prod_sup: Fraction, prod_min: Fraction) -> None:
        if len(escolhidos) == 5:
            out.append((list(escolhidos), prod_sup, prod_min))
            return
        restantes = 6 - len(escolhidos)
        if prod_min >= ALVO:          # fatores restantes > 1: I > alvo sempre
            return
        if prod_sup * _sup_prox(escolhidos[-1], restantes) <= ALVO:
            return
        # Terminação do laço de candidatos: o limite de
        # filho_sup * _sup_prox(q, restantes-1) quando q -> infinito é exatamente
        # prod_sup. Se prod_sup >= ALVO nenhum candidato fecha o laço, que rodaria
        # para sempre. Para o alvo 9/5 e k = 6 isso NUNCA ocorre (o máximo de
        # prod_sup em qualquer nó de nível <= 4 é 1001/576 < 9/5), mas o raise é
        # obrigatório: sem ele o método falha por travamento silencioso em vez de
        # recusar-se a certificar — e no nível 5 o máximo já é 17017/9216 >= 9/5,
        # ou seja, reaproveitar este DFS para omega = 7 travaria no alvo REAL.
        if prod_sup >= ALVO:
            raise NaoCertificavel(
                f"prefixo parcial {escolhidos}: prod p/(p-1) = {prod_sup} >= {ALVO}; "
                "a poda de indice nao limita o proximo primo"
            )
        q = escolhidos[-1]
        while True:
            q = int(nextprime(q))
            filho_sup = prod_sup * sup_pp(q)
            # majoração do filho não-crescente em q => break é definitivo
            if filho_sup * _sup_prox(q, restantes - 1) <= ALVO:
                return
            dfs(escolhidos + [q], filho_sup, prod_min * I_pp(q, 2))

    dfs([5], sup_pp(5), I_pp(5, 2))
    return out


# ---------------------------------------------------------------------------
# Conjuntos completos (usado pelos dois ramos)
# ---------------------------------------------------------------------------

def _v3_parcial(p: int, m: int) -> int:
    """Contribuição de p^{m-1} ao orçamento v3 (= v3(m) se p ≡ 1 mod 3, senão 0;
    Fato 2 com expoente par)."""
    return v_p(3, m) if p % 3 == 1 else 0


def _conjunto_completo(S: list[int], stats: Stats6) -> None:
    """Conjunto de 6 primos fechado: FECHO de ordens + orçamentos + igualdade."""
    stats.conjuntos_completos += 1
    extras, V3, v5_num, v5_den = _parametros_do_alvo()
    fs = frozenset(S)
    listas = []
    for p in S:
        exps = expoentes_validos_ordens(p, fs, extras)
        if not exps:
            return
        listas.append(exps)

    sup_suf = [Fraction(1)] * (len(S) + 1)
    min_suf = [Fraction(1)] * (len(S) + 1)
    for i in range(len(S) - 1, -1, -1):
        sup_suf[i] = sup_suf[i + 1] * sup_pp(S[i])
        min_suf[i] = min_suf[i + 1] * I_pp(S[i], 2)

    exps_atuais: list[int] = []

    def rec(i: int, prod_I: Fraction, soma_v3: int) -> None:
        if soma_v3 > V3:
            return
        if i == len(S):
            # folha ANTES das podas de índice: com zero fatores restantes elas
            # degeneram em comparações com o próprio I(N) e a de sup mataria a
            # igualdade exata (bug pego pelos testes de alvo plantado)
            stats.assinaturas_testadas += 1
            if soma_v3 != V3:
                return
            # orçamento v5: v5(sigma(N)) = v5_num + a1 - v5_den = soma dos feeders
            a1 = exps_atuais[0]
            v5 = sum(v_p(5, exps_atuais[j] + 1)
                     for j in range(1, len(S)) if S[j] % 5 == 1)
            if v5_num + a1 - v5_den != v5:
                return
            n = 1
            s = 1
            for p, a in zip(S, exps_atuais):
                n *= p**a
                s *= sigma_pp(p, a)
            if ALVO.denominator * s == ALVO.numerator * n:
                stats.amigos.append(dict(zip(S, exps_atuais)))
            return
        # podas de índice (apenas com fatores restantes; justificativas exatas:
        # I >= prod*mins com > matando e igualdade viva; I < prod*sups estrito)
        if prod_I * min_suf[i] > ALVO:
            return
        if prod_I * sup_suf[i] <= ALVO:
            return
        for a in listas[i]:
            exps_atuais.append(a)
            rec(i + 1, prod_I * I_pp(S[i], a), soma_v3 + _v3_parcial(S[i], a + 1))
            exps_atuais.pop()

    rec(0, Fraction(1), 0)


# ---------------------------------------------------------------------------
# Ramo (ii) — pinagem de P pela alimentação do 5 (específica do alvo 9/5)
# ---------------------------------------------------------------------------

def _parte_impar_divisores(n: int) -> set[int]:
    """Divisores ímpares > 1 de n (= divisores > 1 da parte ímpar de n)."""
    while n % 2 == 0:
        n //= 2
    out = set()
    d = 3
    while d * d <= n:
        if n % d == 0:
            out.add(d)
            out.add(n // d)
        d += 2
    if n > 1:
        out.add(n)
    return out


def _strip(n: int, permitidos: set[int]) -> int:
    for q in permitidos:
        while n % q == 0:
            n //= q
    return n


def _ramo_ii_pinagem(C5: list[int], stats: Stats6) -> None:
    """Fecha o ramo (ii) pinando o sexto primo P. SÓ vale para o alvo 9/5
    (usa v5(sigma(N)) = a1 - 1 >= 1 e a estrutura 5·sigma = 9·N)."""
    if ALVO != Fraction(9, 5):
        raise NaoCertificavel(
            "ramo (ii) usa pinagem específica do alvo 9/5; alvo atual difere"
        )
    fs = frozenset(C5)
    p5 = C5[-1]
    pins: set[int] = set()

    # a1 >= 2 => v5(sigma(N)) = a1 - 1 >= 1 => o 5 TEM alimentador, e (Fato 2)
    # alimentadores são bases ≡ 1 (mod 5) — em C5 ou o próprio P.

    # CASO A: algum q ∈ C5, q ≡ 1 (mod 5), alimenta (5 | a_q + 1).
    for q in C5[1:]:
        if q % 5 != 1:
            continue
        D_q = ordens_impares(q, fs)
        if 5 in D_q:
            raise NaoCertificavel(
                f"pin indisponível: 5 já é ordem conhecida para a base {q} em {C5}"
            )
        # 5 é divisor de a_q+1 => 5 = ord_r(q) para algum r em S\{q} (Zsygmondy);
        # como 5 ∉ D_q, r = P: ord_P(q) = 5 => P | Phi_5(q) = sigma(q^4).
        candidatos = [r for r in factorint(sigma_pp(q, 4))
                      if r not in fs and r != 3]
        pins.update(candidatos)  # vazio => caso morto (nenhum P possível)

    # CASO B: só P alimenta o 5: P ≡ 1 (mod 10), 5 | a_P + 1 e
    # a1 - 1 = v5(a_P + 1). Todo divisor > 1 de a_P+1 tem primo primitivo
    # (≡ 1 mod d) em C5 ∪ {3}, logo d | q - 1 para algum q ∈ C5 ∪ {3}:
    permitidos_d = set()
    for q in set(C5) | {3}:
        permitidos_d |= _parte_impar_divisores(q - 1)
    E = [m for m in sorted(permitidos_d)
         if all((m % d != 0) or (d in permitidos_d) for d in range(3, m, 2))]
    v5cap = max((v_p(5, m) for m in E if m % 5 == 0), default=0)
    for v in range(1, v5cap + 1):
        a1 = 1 + v
        if a1 % 2 == 1:
            continue  # a1 é par [PROVADO, Teorema B]
        resto = _strip(sigma_pp(5, a1), set(C5) | {3})
        if resto.bit_length() > 256:
            # fatorar poderia rodar indefinidamente: travamento não é falha honesta
            raise NaoCertificavel(
                f"caso só-P com a1={a1}: resto do strip tem {resto.bit_length()} bits; "
                "fatoração fora do orçamento — nada é certificado"
            )
        if resto == 1:
            raise NaoCertificavel(
                f"caso só-P com a1={a1}: sigma(5^{a1}) fecha em C5∪{{3}}, sem pin"
            )
        fat = factorint(resto)
        if len(fat) >= 2:
            continue  # >= 2 primos fora de C5∪{3}: precisaria de 2 slots — morto
        pins.update(fat)

    # cada P pinado > p5 fecha um conjunto completo; P <= p5 é impossível PARA
    # ESTE prefixo (o conjunto teria outros 5 menores primos e é coberto pelo
    # prefixo correspondente na enumeração do Estágio A)
    for P in sorted(pins):
        if P > p5:
            stats.pins_testados.append(P)
            _conjunto_completo(C5 + [P], stats)


# ---------------------------------------------------------------------------
# Certificado
# ---------------------------------------------------------------------------

def certifica_omega6(stats: Stats6 | None = None) -> Stats6:
    """Varre exaustivamente o espaço omega(N) = 6. Se retornar com stats.amigos
    vazio, NENHUM amigo de 10 tem 6 fatores primos distintos. Levanta
    NaoCertificavel se alguma cobertura não fechar (sem certificado)."""
    stats = stats or Stats6()
    for C5, prod_sup, prod_min in _prefixos_c5():
        stats.prefixos += 1
        if prod_min >= ALVO:   # I(N) > prod_min >= alvo para qualquer p6/expoentes
            stats.prefixos_mortos_min += 1
            continue
        if ALVO > prod_sup:   # empate manda para o ramo (ii), que não usa índice
            stats.prefixos_ramo_i += 1
            p6 = C5[-1]
            while True:
                p6 = int(nextprime(p6))
                if prod_sup * sup_pp(p6) <= ALVO:   # monotone em p6 => definitivo
                    break
                # admite p6 quando prod_min*I(p6²) <= ALVO: a IGUALDADE é um
                # candidato vivo (assinatura toda-mínima com I == alvo); só
                # > ALVO é provadamente morto (bug pego por teste plantado)
                if prod_min * I_pp(p6, 2) <= ALVO:
                    _conjunto_completo(C5 + [p6], stats)
        else:
            stats.prefixos_ramo_ii += 1
            _ramo_ii_pinagem(C5, stats)
    return stats


__all__ = ["Stats6", "NaoCertificavel", "certifica_omega6"]
