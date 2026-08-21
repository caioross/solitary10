"""Cadeias de divisibilidade para amigos de 10 (Fase 1, Bloco 2).

Base matemática (rotulada):
  [PROVADO, Fase 0]  N = prod p_i^{a_i}, 5 = p_1 < ... < p_k, primos >= 5, a_i pares >= 2.
  Equação-mestra: prod_i sigma(p_i^{a_i}) = sigma(N) = 9N/5 = 9 * 5^{a_1-1} * prod_{i>=2} p_i^{a_i}.
    => todo fator primo de cada sigma(p_i^{a_i}) está em S ∪ {3};
    => orçamentos exatos de valuação: para todo primo q,
       soma_i v_q(sigma(p_i^{a_i})) = v_q(9N/5).
  [Lema 2.1 de arXiv:2404.00624 = Nielsen/Voight; re-derivado via LTE e testado aqui]
    Para q primo ímpar, q != p, o = ord_q(p):
      v_q(sigma(p^a)) = v_q(a+1)                    se o == 1
                      = v_q(p^o - 1) + v_q(a+1)     se o > 1 e o | a+1
                      = 0                           caso contrário.
    Com a par, a+1 ímpar: só ordens ímpares contribuem.
  [Zsygmondy, clássico] p >= 5, d ímpar >= 3: Phi_d(p) tem primo primitivo q com
    ord_q(p) = d (sem exceções nesse regime); q ≡ 1 (mod d); q = 3 impossível.
    => todo divisor d > 1 de a+1 é ordem ord_q(p) de algum q em S \\ {p}.

Consequências implementadas:
  - v_q_sigma: a fórmula acima, exata, sem fatorar nada.
  - sigma_fecha_em: teste EXATO de "todos os fatores primos de sigma(p^a) estão em
    S ∪ {3}" por reconstrução: sigma(p^a) == prod_{q em S∪{3}} q^{v_q_sigma(q,p,a)}.
    (Sem fatoração: as valuações vêm da fórmula; a igualdade fecha a conta.)
  - ordens_impares: D(p, S) = {ord_q(p) : q em S \\ {p}, ordem ímpar > 1} — candidatos
    a divisores de a+1.
  - expoentes_validos_ordens: expoentes válidos de p num conjunto COMPLETO S
    (equivalente ao FECHO ciclotômico do Bloco 1, mas por ordens + reconstrução:
    escala para max(S) grande).
  - f_menor_ordem_impar: o f_p^q de arXiv:2404.00624 (Teorema 1.3): menor ímpar > 1
    com q^f ≡ 1 (mod p^k), p^{k-1} || q-1. Usado em testes contra a Tabela 4.

Tudo em aritmética inteira exata.
"""
from __future__ import annotations

from functools import lru_cache

from sympy import n_order

# ---------------------------------------------------------------------------
# valuações e ordens
# ---------------------------------------------------------------------------


def v_p(q: int, n: int) -> int:
    """v_q(n) para n >= 1."""
    v = 0
    while n % q == 0:
        n //= q
        v += 1
    return v


@lru_cache(maxsize=None)
def ordem_mod(p: int, q: int) -> int:
    """ord_q(p): ordem multiplicativa de p módulo o primo q (exige q ∤ p)."""
    return int(n_order(p, q))


@lru_cache(maxsize=None)
def _v_q_de_p_ordem_menos_1(q: int, p: int) -> int:
    """v_q(p^{ord_q(p)} - 1), computado por divisões exatas (número pequeno)."""
    return v_p(q, p ** ordem_mod(p, q) - 1)


def v_q_sigma(q: int, p: int, a: int) -> int:
    """v_q(sigma(p^a)) pela fórmula de Nielsen/Voight (q primo ímpar, q != p).

    Justificativa (LTE): sigma(p^a) = (p^{a+1}-1)/(p-1). Se o = ord_q(p) não divide
    a+1, então q ∤ p^{a+1}-1 e q ∤ p-1 dividem juntos... (caso o=1: q | p-1 e
    v_q(p^{a+1}-1) = v_q(p-1) + v_q(a+1), subtraindo v_q(p-1) sobra v_q(a+1);
    caso o>1, o | a+1: q ∤ p-1, v_q(p^{a+1}-1) = v_q(p^o - 1) + v_q((a+1)/o * o /o)
    = v_q(p^o-1) + v_q(a+1) por LTE aplicado a (p^o)^{(a+1)/o} - 1.)
    Testada exaustivamente contra a valuação direta em test_cadeias.py.
    """
    if q == 2:
        # a fórmula (LTE) vale só para q ímpar; para a par sigma(p^a) é ímpar e 0
        # seria correto, mas para a ímpar daria resposta errada — recusar é honesto.
        raise ValueError("v_q_sigma exige q primo ímpar (q = 2 não é suportado)")
    if q == p:
        return 0  # sigma(p^a) ≡ 1 (mod p)
    o = ordem_mod(p, q)
    if o == 1:
        return v_p(q, a + 1)
    if (a + 1) % o == 0:
        return _v_q_de_p_ordem_menos_1(q, p) + v_p(q, a + 1)
    return 0


def f_menor_ordem_impar(p: int, q: int) -> int | None:
    """f_p^q de arXiv:2404.00624 (Teo. 1.3): menor ímpar f > 1 com q^f ≡ 1 (mod p^k),
    onde p^{k-1} || q - 1. None se não existe (então p nunca divide sigma(q^{2a})).

    Equivalente operacional (consistente com v_q_sigma): p | sigma(q^{2a}) sse
    f existe e f | 2a+1.
    """
    o = ordem_mod(q, p)  # ordem de q mod p
    if o == 1:
        return p  # q ≡ 1 (mod p): ordem de q mod p^k é exatamente p (LTE)
    if o % 2 == 1:
        return o
    return None


# ---------------------------------------------------------------------------
# fecho por ordens (substitui o fecho ciclotômico para conjuntos grandes)
# ---------------------------------------------------------------------------


def ordens_impares(p: int, conjunto: frozenset[int],
                   extras: frozenset[int] = frozenset({3})) -> set[int]:
    """D(p, S) = {ord_q(p) : q em (S ∪ extras)\\{p}} restrito a ordens ímpares > 1.

    Pelo argumento de Zsygmondy do cabeçalho, todo divisor > 1 de a+1 (a par)
    pertence a D quando os fatores primos de sigma(N) estão em S ∪ extras.
    Para o problema real (alvo 9/5), extras = {3} e ord_3 nunca é ímpar > 1,
    então incluir extras não muda nada; a generalização existe para os testes
    de completude com alvo plantado (sigma(N) = num·N/den).
    """
    out = set()
    for q in set(conjunto) | set(extras):
        if q != p:
            o = ordem_mod(p, q)
            if o > 1 and o % 2 == 1:
                out.add(o)
    return out


def sigma_fecha_em(p: int, a: int, conjunto: frozenset[int],
                   extras: frozenset[int] = frozenset({3})) -> bool:
    """True sse TODOS os fatores primos de sigma(p^a) estão em conjunto ∪ extras.

    Teste exato por reconstrução: sigma(p^a) == prod q^{v_q_sigma(q, p, a)}.
    (>= sempre vale termo a termo; igualdade sse não sobra fator fora do conjunto.)
    """
    alvo = (p ** (a + 1) - 1) // (p - 1)
    prod = 1
    for q in sorted(set(conjunto) | set(extras)):
        if q != p:
            v = v_q_sigma(q, p, a)
            if v:
                prod *= q**v
    return prod == alvo


def _divisores_impares_maiores_que_1(m: int) -> set[int]:
    """Divisores ímpares > 1 de m ímpar, por divisão por tentativa até sqrt(m)."""
    out = set()
    d = 3
    while d * d <= m:
        if m % d == 0:
            out.add(d)
            out.add(m // d)
        d += 2
    if m > 1:
        out.add(m)
    return out


def _candidatos_m(D: set[int]) -> list[int]:
    """m ímpares > 1 cujos divisores > 1 estão todos em D (implica m em D).

    Enumera os DIVISORES de m (custo O(sqrt m)) em vez de varrer todos os ímpares
    < m (custo O(m)): mesma semântica, e evita a parede de desempenho quando os
    conjuntos têm primos grandes (relevante para omega >= 7).
    """
    return [m for m in sorted(D)
            if _divisores_impares_maiores_que_1(m) <= D]


def expoentes_validos_ordens(p: int, conjunto: frozenset[int],
                             extras: frozenset[int] = frozenset({3})) -> list[int]:
    """Expoentes a (pares >= 2) possíveis para p^a || N com conjunto de primos
    EXATAMENTE `conjunto` (fatores de sigma(N) confinados a conjunto ∪ extras).
    Equivalente a core.motor.expoentes_validos para extras={3}, mas por ordens +
    reconstrução (sem fatorar ciclotômicos): escala para max(S) grande."""
    if p not in conjunto:
        raise ValueError("p deve pertencer ao conjunto")
    D = ordens_impares(p, conjunto, extras)
    S = frozenset(conjunto)
    return [m - 1 for m in _candidatos_m(D) if sigma_fecha_em(p, m - 1, S, extras)]


__all__ = [
    "v_p",
    "ordem_mod",
    "v_q_sigma",
    "f_menor_ordem_impar",
    "ordens_impares",
    "sigma_fecha_em",
    "_candidatos_m",
    "expoentes_validos_ordens",
]
