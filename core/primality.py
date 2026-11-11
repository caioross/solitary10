"""Exact verification of primality claims (Phase 1, Block 8).

The recursive certifier asserts that certain integers are prime (cofactors of cyclotomic
values, factors returned by sympy.factorint, candidates of the last-unknown solver). For
n < 2^64 sympy.isprime is a proof (it is documented as deterministic there: sympy 1.14
without gmpy2 uses fixed Miller-Rabin bases proved sufficient below 2^64, and BPSW, used
otherwise, has no counterexample below 2^64). Above 2^64 this module gives the proof:

  * n < MR_LIMIT = 3 317 044 064 679 887 385 961 981 (about 3.3·10^24): trial division
    by the primes below 2^17, then the strong probable-prime test to the 13 bases
    2, 3, ..., 41. Below MR_LIMIT a composite fails one of these 13 tests (Sorenson and
    Webster, Math. Comp. 86 (2017), the value psi_13), so passing them is a proof.
  * n >= MR_LIMIT: an elliptic-curve certificate (Goldwasser-Kilian / Atkin-Morain), a
    chain of steps (N, a, b, m, q, x, y) with N_1 = n, N_{i+1} = q_i, whose last q is
    proved by the previous item. Step theorem: let gcd(N, 6) = 1, gcd(4a^3 + 27b^2, N) = 1,
    P = (x, y) on E: y^2 = x^3 + ax + b mod N, q | m, q >= (floor(N^(1/4)) + 2)^2
    (> (N^(1/4) + 1)^2). If Q = [m/q]P is computed by the affine formulas with every
    denominator invertible mod N (so Q is an affine point modulo every prime p | N), and
    [q]Q = O, and q is prime, then N is prime: otherwise some prime p | N has
    p <= sqrt(N), Q mod p has order exactly q in E(F_p), and
    q <= #E(F_p) <= (sqrt(p) + 1)^2 <= (N^(1/4) + 1)^2 < q.

Everything here is exact integer arithmetic; nothing calls sympy. How the certificates are
found does not matter (experiments/ecpp_generator.py uses floating point to compute class
polynomials): only verify_chain decides.
"""
from __future__ import annotations

import gzip
import json
from math import gcd, isqrt
from pathlib import Path

MR_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)
MR_LIMIT = 3317044064679887385961981          # psi_13 (Sorenson-Webster)

_SIEVE_N = 1 << 17
_sieve = bytearray([1]) * (_SIEVE_N + 1)
_sieve[0] = _sieve[1] = 0
for _i in range(2, isqrt(_SIEVE_N) + 1):
    if _sieve[_i]:
        _sieve[_i * _i::_i] = bytearray(len(_sieve[_i * _i::_i]))
SMALL_PRIMES = tuple(i for i in range(_SIEVE_N + 1) if _sieve[i])
del _sieve, _i


def mr_witness(n: int, a: int) -> bool:
    """True iff a is a witness to the compositeness of the odd n > 2 (strong test)."""
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    x = pow(a, d, n)
    if x == 1 or x == n - 1:
        return False
    for _ in range(r - 1):
        x = x * x % n
        if x == n - 1:
            return False
    return True


def small_proved_prime(n: int) -> bool:
    """Exact primality of n < MR_LIMIT (False for n >= MR_LIMIT: no claim)."""
    if type(n) is not int or n < 2 or n >= MR_LIMIT:
        return False
    for p in SMALL_PRIMES:
        if p * p > n:
            return True
        if n % p == 0:
            return n == p
    return not any(mr_witness(n, a) for a in MR_BASES)


# ---------------------------------------------------------------------------
# Ledger of primality claims. The certifier modules call record_claim(n) for every
# integer they rely on being prime on the word of sympy (isprime answers True, prime
# factors returned by factorint). While LEDGER is a set, every claim n >= 2^64 is kept, so
# that experiments/certify_primes.py can prove each one with the functions below. Below
# 2^64 sympy.isprime is itself a proof (see the module docstring). An answer False is not
# recorded: core.omega_k proves it by a Miller-Rabin witness where a cofactor is declared
# composite, and lists the places where a False answer is taken from sympy (the comment
# before _SMALL_PRIME_SET).
# Recording changes no decision.
# ---------------------------------------------------------------------------
LEDGER: set[int] | None = None
LEDGER_FROM = 1 << 64


def record_claim(n: int) -> None:
    if LEDGER is not None and n >= LEDGER_FROM:
        LEDGER.add(int(n))


class _Composite(Exception):
    pass


def _ec_add(P, Q, a: int, N: int):
    """Affine addition on y^2 = x^3 + ax + b mod N (None = O). Raises _Composite as soon
    as a denominator is neither 0 nor invertible mod N, or the points are inconsistent."""
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % N == 0:
            return None
        if y1 != y2:
            raise _Composite
        num = (3 * x1 * x1 + a) % N
        den = (2 * y1) % N
    else:
        num = (y2 - y1) % N
        den = (x2 - x1) % N
    if gcd(den, N) != 1:
        raise _Composite
    lam = num * pow(den, -1, N) % N
    x3 = (lam * lam - x1 - x2) % N
    y3 = (lam * (x1 - x3) - y1) % N
    return (x3, y3)


def _ec_mul(k: int, P, a: int, N: int):
    R = None
    for bit in bin(k)[2:]:
        R = _ec_add(R, R, a, N)
        if bit == "1":
            R = _ec_add(R, P, a, N)
    return R


STEP_KEYS = ("N", "a", "b", "m", "q", "x", "y")


def verify_step(step: dict) -> bool:
    """True iff the step proves: q prime => N prime (see the module docstring). Only a
    plain dict of plain ints is accepted (no subclass can show different values to
    different readers)."""
    if type(step) is not dict:
        return False
    try:
        N, a, b, m, q, x, y = (step[k] for k in STEP_KEYS)
    except (KeyError, TypeError):
        return False
    return _verify_values(N, a, b, m, q, x, y)


def _verify_values(N, a, b, m, q, x, y) -> bool:
    if not all(type(v) is int for v in (N, a, b, m, q, x, y)):
        return False
    if N <= 1 or gcd(N, 6) != 1 or q <= 1 or m <= 0 or m % q != 0:
        return False
    a, b, x, y = a % N, b % N, x % N, y % N
    if gcd(4 * a * a * a + 27 * b * b, N) != 1:
        return False
    if (y * y - x * x * x - a * x - b) % N != 0:
        return False
    r = isqrt(isqrt(N))                        # floor(N^(1/4))
    if q < (r + 2) ** 2:
        return False
    try:
        Q = _ec_mul(m // q, (x, y), a, N)
        if Q is None:
            return False
        return _ec_mul(q, Q, a, N) is None
    except _Composite:
        return False


def verify_chain(n: int, chain: list[dict]) -> bool:
    """True only if `chain` proves that n is prime (n >= MR_LIMIT needs at least one step)."""
    if type(n) is not int or type(chain) is not list:
        return False
    cur = n
    for step in chain:
        if type(step) is not dict:
            return False
        try:
            vals = tuple(step[k] for k in STEP_KEYS)        # each value is read once
        except (KeyError, TypeError):
            return False
        if vals[0] != cur or not _verify_values(*vals):
            return False
        cur = vals[4]
    return small_proved_prime(cur)


def proved_prime(n: int, store: dict[int, list[dict]] | None = None) -> bool:
    """Exact: n < MR_LIMIT by small_proved_prime, n >= MR_LIMIT by a chain of `store`."""
    if n < MR_LIMIT:
        return small_proved_prime(n)
    chain = (store or {}).get(n)
    return chain is not None and len(chain) > 0 and verify_chain(n, chain)


# ---------------------------------------------------------------------------
# Certificate store: gzip-compressed JSON {"certificates": {"<n>": [step, ...]}} with the
# integers written as decimal strings (exact; CPython converts decimal strings of up to
# 4300 digits by default, and the largest certificate in the store has 541).
# ---------------------------------------------------------------------------

def load_store(path: str | Path) -> dict[int, list[dict]]:
    path = Path(path)
    if not path.exists():
        return {}
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        raw = json.load(fh)
    return {int(n): [{k: int(st[k]) for k in STEP_KEYS} for st in chain]
            for n, chain in raw["certificates"].items()}


def save_store(path: str | Path, store: dict[int, list[dict]], meta: dict | None = None) -> None:
    raw = {"format": "ECPP chains (N, a, b, m, q, x, y), see core/primality.py",
           "meta": meta or {},
           "certificates": {str(n): [{k: str(st[k]) for k in STEP_KEYS} for st in store[n]]
                            for n in sorted(store)}}
    with gzip.open(Path(path), "wt", encoding="utf-8", compresslevel=9) as fh:
        json.dump(raw, fh, separators=(",", ":"))
