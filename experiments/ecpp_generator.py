"""UNTRUSTED generator of elliptic-curve primality certificates (Atkin-Morain ECPP).

Used by experiments/certify_primes.py. Nothing here is part of any proof: its only
output is a chain of steps that core.primality.verify_chain accepts or rejects in exact
integer arithmetic. The class polynomials are computed by floating-point q-series
(mpmath), which is why this file lives outside core/.

Method: for a probable prime N, find a fundamental discriminant D < 0 with a solution of
x^2 + |D| y^2 = 4N (Cornacchia); the curves with complex multiplication by D have
N + 1 +- x points (more twists for D = -3, -4). If one of those orders m has a probable
prime cofactor q above (N^(1/4) + 2)^2 after removing small primes, build such a curve
from a root of the Hilbert class polynomial H_D mod N, find a point P with [m]P = O and
[m/q]P != O, and recurse on q. Depth-first with backtracking.
"""
from __future__ import annotations

import random
from math import gcd, isqrt

from core.primality import (MR_BASES, MR_LIMIT, SMALL_PRIMES, _Composite, _ec_mul,
                            mr_witness, small_proved_prime, verify_step)


def is_prp(n: int) -> bool:
    if n < 2:
        return False
    for p in SMALL_PRIMES[:200]:
        if n % p == 0:
            return n == p
    return not any(mr_witness(n, a) for a in MR_BASES)


def jacobi(a: int, n: int) -> int:
    a %= n
    t = 1
    while a:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5):
                t = -t
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            t = -t
        a %= n
    return t if n == 1 else 0


def sqrt_mod(a: int, p: int) -> int | None:
    """A square root of a mod p (p an odd probable prime), or None (Tonelli-Shanks)."""
    a %= p
    if a == 0:
        return 0
    if pow(a, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(a, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
        if z > 2000:
            return None
    c = pow(z, q, p)
    r = pow(a, (q + 1) // 2, p)
    t = pow(a, q, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1:
            t2 = t2 * t2 % p
            i += 1
            if i == s:
                return None
        bb = pow(c, 1 << (s - i - 1), p)
        r = r * bb % p
        c = bb * bb % p
        t = t * c % p
        s = i
    return r


def cornacchia4(D: int, p: int) -> tuple[int, int] | None:
    """(x, y) with x^2 + |D| y^2 = 4p, or None (D < 0, D = 0 or 1 mod 4)."""
    if jacobi(D, p) != 1:
        return None
    x0 = sqrt_mod(D, p)
    if x0 is None:
        return None
    if (x0 - D) % 2:
        x0 = p - x0
    a, b = 2 * p, x0
    lim = isqrt(4 * p)
    while b > lim:
        a, b = b, a % b
    rest = 4 * p - b * b
    if rest % (-D):
        return None
    c = rest // (-D)
    y = isqrt(c)
    if y * y != c:
        return None
    return b, y


def reduced_forms(D: int) -> list[tuple[int, int, int]]:
    forms = []
    a = 1
    while 3 * a * a <= -D:
        for b in range(-a + 1, a + 1):
            if (b * b - D) % (4 * a):
                continue
            c = (b * b - D) // (4 * a)
            if c < a or (b < 0 and a == c) or gcd(gcd(a, b), c) != 1:
                continue
            forms.append((a, b, c))
        a += 1
    return forms


def is_fundamental(D: int) -> bool:
    if D % 4 == 1:
        n = -D
    elif D % 4 == 0:
        n = -D // 4
        if n % 4 not in (1, 2):
            return False
    else:
        return False
    for p in SMALL_PRIMES:
        if p * p > n:
            break
        if n % (p * p) == 0:
            return False
    return True


_HILBERT: dict[int, list[int] | None] = {}


def hilbert(D: int) -> list[int] | None:
    """Integer coefficients (low to high) of the Hilbert class polynomial H_D, by a
    floating-point q-series; None if the rounding is not clean."""
    if D in _HILBERT:
        return _HILBERT[D]
    import mpmath as mp
    forms = reduced_forms(D)
    prec = int(sum(3.1416 * (-D) ** 0.5 / a for a, _, _ in forms) / 0.6931) + 80 + 16 * len(forms)
    mp.mp.prec = prec
    poly = [mp.mpc(1)]
    sq = mp.sqrt(mp.mpf(-D))
    for a, b, _c in forms:
        tau = mp.mpc(-b, sq) / (2 * a)
        qq = mp.exp(2j * mp.pi * tau)
        e4 = mp.mpc(1)
        e6 = mp.mpc(1)
        qn = qq
        n = 1
        tol = mp.mpf(2) ** (-prec - 8)
        while abs(qn) > tol:
            t = qn / (1 - qn)
            e4 += 240 * n ** 3 * t
            e6 -= 504 * n ** 5 * t
            qn *= qq
            n += 1
        j = 1728 * e4 ** 3 / (e4 ** 3 - e6 ** 2)
        new = [mp.mpc(0)] * (len(poly) + 1)
        for i, co in enumerate(poly):
            new[i + 1] += co
            new[i] -= co * j
        poly = new
    out = []
    for co in poly:
        r = mp.nint(co.real)
        if abs(co.real - r) > mp.mpf(2) ** (-20) or abs(co.imag) > mp.mpf(2) ** (-20):
            _HILBERT[D] = None
            return None
        out.append(int(r))
    _HILBERT[D] = out
    return out


def _pmod(a, m, N):
    a = a[:]
    dm = len(m) - 1
    inv = pow(m[-1], -1, N)
    while len(a) - 1 >= dm:
        c = a[-1] * inv % N
        if c:
            off = len(a) - 1 - dm
            for i in range(dm + 1):
                a[off + i] = (a[off + i] - c * m[i]) % N
        a.pop()
    while a and a[-1] == 0:
        a.pop()
    return a


def _pmul(a, b, m, N):
    if not a or not b:
        return []
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                r[i + j] = (r[i + j] + x * y) % N
    return _pmod(r, m, N)


def _pgcd(a, b, N):
    while b:
        a, b = b, _pmod(a, b, N)
    if a:
        inv = pow(a[-1], -1, N)
        a = [c * inv % N for c in a]
    return a


def _pdiv(a, b, N):
    a = a[:]
    q = [0] * (len(a) - len(b) + 1)
    inv = pow(b[-1], -1, N)
    for k in range(len(q) - 1, -1, -1):
        c = a[k + len(b) - 1] * inv % N
        q[k] = c
        for i in range(len(b)):
            a[k + i] = (a[k + i] - c * b[i]) % N
    return q


def root_mod(poly, N, rng):
    """One root mod N of a polynomial that splits into distinct linear factors."""
    f = [c % N for c in poly]
    inv = pow(f[-1], -1, N)
    f = [c * inv % N for c in f]
    tries = 0
    while len(f) > 2:
        tries += 1
        if tries > 60:
            return None
        r = rng.randrange(N)
        base = _pmod([r, 1], f, N)
        w = [1]
        for bit in bin((N - 1) // 2)[2:]:
            w = _pmul(w, w, f, N)
            if bit == "1":
                w = _pmul(w, base, f, N)
        w = w[:] if w else [0]
        w[0] = (w[0] - 1) % N
        while w and w[-1] == 0:
            w.pop()
        g = _pgcd(f, w, N) if w else f
        if 1 < len(g) < len(f):
            h = _pdiv(f, g, N)
            f = g if len(g) <= len(h) else h
    return (-f[0]) % N


def discriminants(limit: int = 4000, hmax: int = 12) -> list[int]:
    out = []
    for D in range(-3, -limit, -1):
        if D % 4 in (0, 1) and is_fundamental(D):
            h = len(reduced_forms(D))
            if h <= hmax:
                out.append((h, -D, D))
    out.sort()
    return [D for _, _, D in out]


def _orders(D, N, x, y):
    if D == -4:
        return [N + 1 + x, N + 1 - x, N + 1 + 2 * y, N + 1 - 2 * y]
    if D == -3:
        u, v = (x + 3 * y) // 2, (x - 3 * y) // 2
        return [N + 1 + x, N + 1 - x, N + 1 + u, N + 1 - u, N + 1 + v, N + 1 - v]
    return [N + 1 + x, N + 1 - x]


def _strip(m):
    for p in SMALL_PRIMES:
        while m % p == 0:
            m //= p
        if p * p > m:
            break
    return m


def _find_point(N, D, m, q, rng):
    """A step with a point of the required kind on a curve with CM by D, or None."""
    if D not in (-3, -4):
        H = hilbert(D)
        if H is None:
            return None
        try:
            j = root_mod(H, N, rng)
        except ValueError:
            return None
        if j is None or j in (0, 1728 % N):
            return None
        c = j * pow(j - 1728, -1, N) % N
        a0, b0 = (-3 * c) % N, (2 * c) % N
    for _ in range(80):
        x0 = rng.randrange(1, N)
        if D == -3:
            y0 = rng.randrange(1, N)
            a, b, P = 0, (y0 * y0 - x0 ** 3) % N, (x0, y0)
        elif D == -4:
            y0 = rng.randrange(1, N)
            a, b, P = (y0 * y0 - x0 ** 3) * pow(x0, -1, N) % N, 0, (x0, y0)
        else:
            d = (x0 ** 3 + a0 * x0 + b0) % N
            if d == 0:
                continue
            a, b, P = a0 * d * d % N, b0 * d ** 3 % N, (x0 * d % N, d * d % N)
        if gcd(4 * a ** 3 + 27 * b * b, N) != 1:
            continue
        try:
            if _ec_mul(m, P, a, N) is not None:
                continue
            if _ec_mul(m // q, P, a, N) is None:
                continue
        except _Composite:
            return None
        step = {"N": N, "a": a, "b": b, "m": m, "q": q, "x": P[0], "y": P[1]}
        if verify_step(step):
            return step
    return None


_DISCS: dict[tuple[int, int], list[int]] = {}


def ecpp(N, rng, max_cands=4, budget=None, discs=(4000, 12)):
    """A chain for the probable prime N, or None."""
    if discs not in _DISCS:
        _DISCS[discs] = discriminants(*discs)
    budget = budget if budget is not None else [400]
    if N < MR_LIMIT:
        return [] if small_proved_prime(N) else None
    if not is_prp(N) or gcd(N, 6) != 1:
        return None
    r = isqrt(isqrt(N))
    bound = (r + 2) ** 2
    cands = []
    seen = set()
    for D in _DISCS[discs]:
        sol = cornacchia4(D, N)
        if sol is None:
            continue
        for m in _orders(D, N, *sol):
            q = _strip(m)
            if q in seen or q < bound or q * 2 > m or not is_prp(q):
                continue
            seen.add(q)
            cands.append((q, m, D))
        if len(cands) >= max_cands:
            break
    cands.sort()
    for q, m, D in cands:
        if budget[0] <= 0:
            return None
        budget[0] -= 1
        step = _find_point(N, D, m, q, rng)
        if step is None:
            continue
        rest = ecpp(q, rng, max_cands, budget, discs)
        if rest is not None:
            return [step] + rest
    return None


SCHEDULE = ((4, (4000, 12)), (8, (4000, 12)), (16, (12000, 20)), (40, (30000, 32)))


def certify(n: int) -> list[dict] | None:
    """A chain for n under a fixed, deterministic schedule of widening searches (the
    random generator is seeded from n), or None. Untrusted: verify with verify_chain."""
    for attempt, (max_cands, discs) in enumerate(SCHEDULE):
        try:
            chain = ecpp(n, random.Random(n % 1000003 + attempt), max_cands, [4000], discs)
        except Exception:                      # a generator failure is not a verdict
            chain = None
        if chain is not None:
            return chain
    return None
