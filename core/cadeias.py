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
    => todo divisor d > 1 de a+1 é ordem ord_q(p) de algum q em S \\ {p}
       (target 9/5; for a generic target num/den the witness q is a prime of sigma(N),
       so it lies in (S ∪ extras) \\ {p}, extras = primes of num: see ordens_impares).

Consequências implementadas:
  - v_q_sigma: the formula above, exact. It needs ord_q(p), hence the factorization of
    q - 1 (fatoracao_q_menos_1), but never a factorization of sigma(p^a). Used by the
    tests only; the certifier uses v_q_sigma_direto.
  - sigma_fecha_em: teste EXATO de "todos os fatores primos de sigma(p^a) estão em
    S ∪ extras" (extras = primes of the numerator of the target; {3} for 9/5) por
    reconstrução: sigma(p^a) == prod_{q em S ∪ extras} q^{v_q_sigma_direto(q,p,a)}.
    (No factorization and no orders: each valuation is v_q(p^{a+1} - 1) - v_q(p - 1),
    by modular exponentiation; the equality closes the account.)
  - ordens_impares: D(p, S) = {ord_q(p) : q em (S ∪ extras) \\ {p}, ordem ímpar > 1} —
    candidatos a divisores de a+1.
  - expoentes_validos_ordens: expoentes válidos de p num conjunto COMPLETO S
    (equivalente ao FECHO ciclotômico do Bloco 1, mas por ordens + reconstrução:
    escala para max(S) grande).
  - f_menor_ordem_impar: o f_p^q de arXiv:2404.00624 (Teorema 1.3): menor ímpar > 1
    com q^f ≡ 1 (mod p^k), p^{k-1} || q-1. Usado em testes contra a Tabela 4.

Tudo em aritmética inteira exata.
"""
from __future__ import annotations

from functools import lru_cache

from sympy import divisors, factorint

from core.primality import record_claim

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


@lru_cache(maxsize=1 << 16)
def fatoracao_q_menos_1(q: int) -> tuple[tuple[int, int], ...]:
    """Prime factorization of q - 1 as ((ell, e), ...), from sympy.factorint, with one
    check of our own (Block 8), that the product is q - 1 exactly; every prime factor is
    also passed to core.primality.record_claim, which keeps it only while the ledger is
    enabled and only if it is >= 2^64 (for experiments/certify_primes.py; below 2^64
    sympy.isprime is a proof)."""
    fat = sorted((int(ell), int(e)) for ell, e in factorint(q - 1).items())
    prod = 1
    for ell, e in fat:
        prod *= ell ** e
        record_claim(ell)
    if prod != q - 1:
        raise ArithmeticError(f"factorint({q} - 1) does not multiply back")
    return tuple(fat)


@lru_cache(maxsize=1 << 16)
def ordem_mod(p: int, q: int) -> int:
    """ord_q(p): ordem multiplicativa de p módulo o primo q (exige q ∤ p).
    Block 8: computed here from the factorization of q - 1 instead of sympy.n_order, so
    that the only primality claims involved are the recorded factors of q - 1. Start from
    o = q - 1 (p^(q-1) ≡ 1 mod q, checked) and remove each prime ell of q - 1 while
    p^(o/ell) ≡ 1 (mod q): the result is the order, since it divides q - 1, p^o ≡ 1, and
    p^(o/ell) ≢ 1 for every prime ell of o."""
    o = q - 1
    if pow(p, o, q) != 1:
        raise ArithmeticError(f"p^(q-1) != 1 (mod q): q = {q} is not a prime, or q | p = {p}")
    for ell, e in fatoracao_q_menos_1(q):
        for _ in range(e):
            if pow(p, o // ell, q) != 1:
                break
            o //= ell
    return o


@lru_cache(maxsize=1 << 16)
def _v_q_de_p_ordem_menos_1(q: int, p: int) -> int:
    """v_q(p^{ord_q(p)} - 1) por exponenciação modular: q^v | p^o - 1 sse
    p^o ≡ 1 (mod q^v). (A potência inteira p^o teria o·log2(p) bits — proibitivo
    quando q é um primo grande e o = ord_q(p) ~ q.)"""
    o = ordem_mod(p, q)
    v = 1  # q | p^o - 1 por definição de ordem
    while pow(p, o, q ** (v + 1)) == 1:
        v += 1
    return v


def v_q_potencia_menos_1(q: int, p: int, n: int) -> int:
    """v_q(p^n - 1) para q primo, q ∤ p, n >= 1 — por exponenciação modular, sem
    ordens nem fatorações: q^v | p^n - 1 sse p^n ≡ 1 (mod q^v). Termina porque
    p^n - 1 é finito."""
    v = 0
    while pow(p, n, q ** (v + 1)) == 1:
        v += 1
    return v


def v_q_sigma_direto(q: int, p: int, a: int) -> int:
    """v_q(sigma(p^a)) = v_q(p^{a+1} - 1) - v_q(p - 1), direto da identidade
    sigma(p^a) = (p^{a+1} - 1)/(p - 1). Vale para TODO primo q != p (inclusive
    q = 2) e não precisa de ord_q(p) — logo não precisa fatorar q - 1, o que
    permite conjuntos com primos grandes. Equivale a v_q_sigma onde ambas valem."""
    if q == p:
        return 0
    return v_q_potencia_menos_1(q, p, a + 1) - v_p(q, p - 1)


def v_q_sigma(q: int, p: int, a: int) -> int:
    """v_q(sigma(p^a)) pela fórmula de Nielsen/Voight (q primo ímpar, q != p).

    Justification (LTE), with o = ord_q(p) and sigma(p^a) = (p^{a+1} - 1)/(p - 1):
      - o ∤ a+1: then o != 1, q ∤ p - 1 and q ∤ p^{a+1} - 1, so the valuation is 0;
      - o = 1: q | p - 1 and v_q(p^{a+1} - 1) = v_q(p - 1) + v_q(a+1); subtracting
        v_q(p - 1) leaves v_q(a+1);
      - o > 1, o | a+1: q ∤ p - 1, and LTE applied to (p^o)^{(a+1)/o} - 1 gives
        v_q(p^{a+1} - 1) = v_q(p^o - 1) + v_q((a+1)/o) = v_q(p^o - 1) + v_q(a+1),
        because o | q - 1 and hence q ∤ o.
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

    Teste exato por reconstrução: sigma(p^a) == prod q^{v_q(sigma(p^a))}, com as
    valuações por exponenciação modular (v_q_sigma_direto: sem ordens, sem
    fatorar q - 1). O produto sempre DIVIDE sigma(p^a); a igualdade falha sse sobra
    fator fora do conjunto.

    Gate de tamanho (exato, só inteiros): prod < 2^{bl(prod)} e p^a >= 2^{a·(bl(p)-1)}
    (bl = bit_length). Se bl(prod) <= a·(bl(p)-1) então prod < p^a < sigma(p^a) e a
    resposta é False SEM materializar p^{a+1} — essencial quando a+1 é uma ordem
    módulo um primo grande (a ~ 10^11 e além).
    """
    prod = 1
    for q in sorted(set(conjunto) | set(extras)):
        if q != p:
            v = v_q_sigma_direto(q, p, a)
            if v:
                prod *= q**v
    if prod.bit_length() <= a * (p.bit_length() - 1):
        return False
    alvo = (p ** (a + 1) - 1) // (p - 1)
    return prod == alvo


@lru_cache(maxsize=1 << 16)
def _divisores_impares_maiores_que_1(m: int) -> frozenset[int]:
    """Divisores ímpares > 1 de m, pela fatoração (sympy.divisors). A divisão por
    tentativa até sqrt(m) não escala: m pode ser uma ordem módulo um primo de
    dezenas de bits. (Block 8: sympy.divisors factors m again, without recording its
    primality claims. Harmless: every element returned is a product of the factors that
    sympy.factorint finds for m, hence a true divisor of m, so a wrong primality answer can
    only make the list INCOMPLETE. The callers reached by the certifier test "every
    listed divisor is in D" (_candidatos_m, used by expoentes_validos_ordens and as case
    (A) of omega_k._expoentes_com_primo_grande; case (B1) composite of that lemma, through
    the divisors of e), where a missing divisor can only ADD candidates, or "exactly one
    listed divisor is outside D" (case (B2)), where a missing divisor can only make m a
    candidate or leave no listed divisor outside D, and then m is already a candidate of
    (A), which reads the same list. Every candidate is then decided exactly by
    sigma_fecha_em.
    omega_k._expoentes_viaveis_unico uses it as a generator of candidates: tests only.)"""
    if m <= 1:
        return frozenset()
    return frozenset(d for d in divisors(m) if d > 1 and d % 2 == 1)


def _candidatos_m(D: set[int]) -> list[int]:
    """m ímpares > 1 cujos divisores > 1 estão todos em D (implica m em D).

    Enumerates the DIVISORS of m, by factoring m (_divisores_impares_maiores_que_1),
    instead of scanning every odd number < m (cost O(m)): same semantics, and no
    performance wall when the sets have large primes (relevant for omega >= 7).
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
    "fatoracao_q_menos_1",
    "v_q_sigma",
    "v_q_sigma_direto",
    "v_q_potencia_menos_1",
    "f_menor_ordem_impar",
    "ordens_impares",
    "sigma_fecha_em",
    "_candidatos_m",
    "expoentes_validos_ordens",
]
