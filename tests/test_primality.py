"""Exact primality verification (core/primality.py) and the ledger of primality claims of
the recursive certifier (Phase 1, Block 8)."""
import random
from pathlib import Path

import pytest
from sympy import isprime, nextprime

import core.omega_k as omega_k
from core import primality as pr

STORE = Path(__file__).resolve().parents[1] / "data" / "primality_certificates.json.gz"


@pytest.fixture(scope="module")
def store():
    return pr.load_store(STORE)


def test_small_proved_prime_is_exact_below_10_5():
    for n in range(-5, 100_000):
        assert pr.small_proved_prime(n) == (n >= 2 and isprime(n)), n


@pytest.mark.parametrize("n", [
    2047,                              # strong pseudoprime to base 2
    1373653,                           # bases 2, 3
    3215031751,                        # bases 2, 3, 5, 7
    2152302898747,                     # bases 2..11
    3474749660383,                     # bases 2..13
    341550071728321,                   # bases 2..17
    3825123056546413051,               # bases 2..23
    318665857834031151167461,          # bases 2..37 (psi_12)
    561, 41041, 825265,                # Carmichael numbers
])
def test_strong_pseudoprimes_below_the_limit_are_rejected(n):
    assert n < pr.MR_LIMIT and not isprime(n) and not pr.small_proved_prime(n)


def test_the_limit_itself_and_beyond_are_not_claimed():
    # psi_13 = MR_LIMIT is a strong pseudoprime to the 13 bases: it must be outside the range
    assert not isprime(pr.MR_LIMIT)
    assert all(not pr.mr_witness(pr.MR_LIMIT, a) for a in pr.MR_BASES)
    assert not pr.small_proved_prime(pr.MR_LIMIT)
    p = int(nextprime(pr.MR_LIMIT))
    assert not pr.small_proved_prime(p) and not pr.proved_prime(p, {})


def test_small_proved_prime_agrees_with_sympy_on_random_large_inputs():
    rng = random.Random(20261110)
    for _ in range(3000):
        n = rng.randrange(2**40, pr.MR_LIMIT)
        assert pr.small_proved_prime(n) == isprime(n)
    for _ in range(300):
        p = int(nextprime(rng.randrange(2**64, pr.MR_LIMIT // 2)))
        assert pr.small_proved_prime(p)
        assert not pr.small_proved_prime(p * 3) and not pr.small_proved_prime(p + 1)


def test_store_round_trip(tmp_path, store):
    some = dict(list(sorted(store.items()))[:5])
    path = tmp_path / "certs.json.gz"
    pr.save_store(path, some, {"test": True})
    assert pr.load_store(path) == some


def test_certificates_of_the_store_verify(store):
    assert len(store) >= 2600
    # a sample (experiments/certify_primes.py verifies all of them; the largest, up to
    # 1 797 bits, take about a minute each and are left to it)
    rng = random.Random(7)
    sample = rng.sample(sorted(n for n in store if n.bit_length() <= 600), 60)
    for n in sample:
        assert n >= pr.MR_LIMIT and pr.verify_chain(n, store[n]) and pr.proved_prime(n, store)


def test_every_corruption_of_a_certificate_is_rejected(store):
    n = min((m for m in store if 120 <= m.bit_length() <= 200), key=int.bit_length)
    chain = store[n]
    assert pr.verify_chain(n, chain)
    for i, step in enumerate(chain):
        for key in pr.STEP_KEYS:
            for delta in (1, -1, 2):
                bad = [dict(s) for s in chain]
                bad[i][key] = step[key] + delta
                assert not pr.verify_chain(n, bad), (i, key, delta)
    assert not pr.verify_chain(n, chain[:-1])                # truncated: last q too large
    assert not pr.verify_chain(n + 2, chain)                 # the chain is for n only
    assert not pr.verify_chain(n, [])                        # n >= MR_LIMIT needs a step
    assert not pr.verify_chain(n, chain + chain[-1:])        # wrong N in the extra step


def test_a_chain_for_one_prime_proves_nothing_about_a_composite(store):
    ns = sorted(store, key=int.bit_length)[:3]
    p, q = ns[0], ns[1]
    composite = p * q
    for chain in (store[p], store[q]):
        assert not pr.verify_chain(composite, chain)
    # a step with N replaced by the composite is refused (the curve check fails first, and
    # q is also far below the size bound); the checks that only a forged step reaches are
    # tested below
    forged = [dict(store[p][0], N=composite)]
    assert not pr.verify_step(forged[0]) and not pr.verify_chain(composite, forged)


def test_ledger_records_the_claims_of_the_certifier_and_the_store_proves_them(store):
    led = omega_k.enable_prime_ledger()
    try:
        for k in range(1, 9):
            omega_k.certifica_omega(k, light=True)
        claims = sorted(led)
    finally:
        omega_k.disable_prime_ledger()
    assert claims and all(n >= 2**64 for n in claims)
    assert all(pr.proved_prime(n, store) for n in claims)
    assert any(n >= pr.MR_LIMIT for n in claims)              # some need a certificate


def test_orders_are_computed_from_a_recorded_factorization():
    # core.cadeias.ordem_mod no longer calls sympy.n_order: the order comes from the
    # factorization of q - 1, whose primes are recorded as primality claims.
    from sympy import n_order, primerange
    from core import cadeias
    rng = random.Random(5)
    qs = list(primerange(3, 300)) + [int(nextprime(rng.randrange(10**6, 10**17))) for _ in range(150)]
    for q in qs:
        for p in [5, 7, 11, 13, 31, 97, 19531] + [rng.randrange(2, q) for _ in range(3)]:
            if p % q:
                assert cadeias.ordem_mod(p, q) == n_order(p, q), (p, q)
    with pytest.raises(ArithmeticError):
        cadeias.ordem_mod(10, 5)                              # q | p
    with pytest.raises(ArithmeticError):
        cadeias.ordem_mod(2, 341 * 3)                         # not a prime modulus

    # a prime q with a prime factor of q - 1 above 2^64: the factor reaches the ledger
    ell = int(nextprime(2**64))
    k = 2
    while not isprime(k * ell + 1):
        k += 2
    q = k * ell + 1
    led = omega_k.enable_prime_ledger()
    try:
        assert cadeias.ordem_mod(3, q) == n_order(3, q)
        assert ell in led
        assert omega_k._e_ordem(3, q, cadeias.ordem_mod(3, q))
    finally:
        omega_k.disable_prime_ledger()
    assert pr.small_proved_prime(ell)


def test_small_division_checks_the_factors_against_our_own_sieve(monkeypatch):
    omega_k._divisao_pequena.cache_clear()
    assert omega_k._divisao_pequena(2 * 3 * 3 * 99991 * 1000003) == ((2, 3, 99991), 1000003)
    # a factorisation that does not consist of primes below 10^5 is refused, not trusted
    monkeypatch.setattr(omega_k, "factorint", lambda g: {15: 1, 7: 1} if g == 105 else {g: 1})
    omega_k._divisao_pequena.cache_clear()
    with pytest.raises(ArithmeticError):
        omega_k._divisao_pequena(105 * 1000003)
    omega_k._divisao_pequena.cache_clear()


def test_a_composite_verdict_without_a_witness_is_refused_not_trusted(monkeypatch):
    # A cofactor declared composite counts as >= 2 unknown primes and can kill a node, so
    # _classifica_cofator proves the verdict by a Miller-Rabin witness (_composto_provado)
    # and refuses (NaoCertificavel) when none is found. Here sympy is made to call the
    # prime 2^89 - 1 composite: taken on trust, that answer would kill the case (None).
    P = 2**89 - 1
    assert omega_k._composto_provado(pr.MR_LIMIT)      # psi_13: its witness is 43, the 14th base
    assert not omega_k._composto_provado(P)            # a prime has no witness
    omega_k._classifica_cofator.cache_clear()
    assert omega_k._novos_e_resto(7 * 11 * P, {7, 11}, 1) == ((P,), 1)
    real = omega_k.isprime
    monkeypatch.setattr(omega_k, "isprime", lambda n: False if n == P else real(n))
    omega_k._classifica_cofator.cache_clear()
    try:
        with pytest.raises(omega_k.NaoCertificavel):
            omega_k._novos_e_resto(7 * 11 * P, {7, 11}, 1)
    finally:
        omega_k._classifica_cofator.cache_clear()


def test_verify_chain_accepts_only_plain_dicts_of_plain_ints(store):
    n = min((m for m in store if 120 <= m.bit_length() <= 200), key=int.bit_length)
    chain = store[n]

    class Two(dict):                       # shows one N to .get and another to [...]
        def get(self, key, default=None):
            return n * 3 if key == "N" else super().get(key, default)

    assert not pr.verify_chain(n * 3, [Two(chain[0])] + chain[1:])
    assert not pr.verify_chain(n, [Two(chain[0])] + chain[1:])
    assert not pr.verify_step(Two(chain[0]))
    assert not pr.verify_chain(n, tuple(chain))                # the chain must be a list
    assert not pr.verify_chain(n, [dict(chain[0], N=float(n))] + chain[1:])
    assert not pr.verify_chain(n, [dict(chain[0], q=True)] + chain[1:])
    assert pr.verify_chain(n, chain)


def test_each_check_of_the_step_theorem_is_needed():
    # Forged steps for composite N, each failing exactly ONE check of verify_step; removing
    # that check would certify a composite (experiments/planted_mutations.py, ver_*).
    from math import gcd, isqrt
    # (1) every check passes except the lower bound on q: N = 95477 = 307 * 311
    st = {"N": 95477, "a": 24261, "b": 71568, "m": 337, "q": 337, "x": 71531, "y": 94617}
    N, a, b, x, y, q = st["N"], st["a"], st["b"], st["x"], st["y"], st["q"]
    assert N == 307 * 311 and (y * y - x**3 - a * x - b) % N == 0
    assert gcd(4 * a**3 + 27 * b * b, N) == 1 and pr.small_proved_prime(q)
    assert pr._ec_mul(q, (x, y), a, N) is None                 # [q]P = O, P != O
    r = isqrt(isqrt(N))
    assert (r + 1) ** 2 <= q < (r + 2) ** 2                    # only the bound fails
    assert not pr.verify_step(st) and not pr.verify_chain(N, [st])
    # (2) [m/q]P = O: N = 91 = 7 * 13, P = (1, 0) of order 2, m = 2q
    st = {"N": 91, "a": 2, "b": 88, "m": 58, "q": 29, "x": 1, "y": 0}
    assert (0 - 1 - 2 - 88) % 91 == 0 and pr._ec_mul(2, (1, 0), 2, 91) is None
    assert 29 >= (isqrt(isqrt(91)) + 2) ** 2
    assert not pr.verify_step(st) and not pr.verify_chain(91, [st])
    # (3) every check passes except [q]Q = O: N = (2^61 - 1)(2^89 - 1), P = (2, 3)
    N = (2**61 - 1) * (2**89 - 1)
    q = 37778931863553024000019
    st = {"N": N, "a": 1, "b": N - 1, "m": q, "q": q, "x": 2, "y": 3}
    assert (9 - 8 - 2 + 1) % N == 0 and gcd(4 + 27, N) == 1
    assert pr.small_proved_prime(q) and q >= (isqrt(isqrt(N)) + 2) ** 2
    assert pr._ec_mul(q, (2, 3), 1, N) is not None
    assert not pr.verify_step(st) and not pr.verify_chain(N, [st])


def test_inconsistent_points_are_a_proof_of_compositeness():
    # x1 = x2 and y1 != +-y2 (mod N) cannot happen modulo a prime (y^2 = c has at most two
    # roots), so _ec_add must raise instead of treating the sum as a doubling. The proof of
    # the step theorem uses this check (every operation is then valid modulo every prime of
    # N); no forged step is known that needs it (experiments/planted_mutations.py,
    # ver_inconsistent). N = 91: y1 = y2 mod 7 but y1 = -y2 mod 13, both points on
    # y^2 = x^3 + 58. Plain assert, so that a mutant is killed by an AssertionError.
    assert (1 - 5**3 - 58) % 91 == 0 and (64 * 64 - 5**3 - 58) % 91 == 0
    assert (64 - 1) % 7 == 0 and (64 + 1) % 13 == 0
    try:
        out = pr._ec_add((5, 1), (5, 64), 0, 91)
    except pr._Composite:
        out = "composite"
    assert out == "composite", out


def test_a_denominator_that_is_not_invertible_shows_a_composite():
    # (4) every other check of the step passes, but computing [q]P meets a denominator
    # that is 0 modulo 10007 and not modulo the other prime: N = 10007 * 1000000000039,
    # P of order 10131 modulo 10007, q = 2 (mod 10131). Taking that denominator for O
    # would certify N (experiments/planted_mutations.py, ver_den_gcd).
    from math import gcd, isqrt
    st = {"N": 10007000000390273, "a": 9422129944899486, "b": 2354719932618283,
          "m": 100063889, "q": 100063889, "x": 1470835351590253, "y": 3320517326754412}
    N, a, b, q, x, y = st["N"], st["a"], st["b"], st["q"], st["x"], st["y"]
    assert N == 10007 * 1000000000039 and gcd(N, 6) == 1
    assert gcd(4 * a**3 + 27 * b * b, N) == 1 and (y * y - x**3 - a * x - b) % N == 0
    assert pr.small_proved_prime(q) and q >= (isqrt(isqrt(N)) + 2) ** 2
    with pytest.raises(pr._Composite):
        pr._ec_mul(q, (x, y), a, N)
    assert not pr.verify_step(st) and not pr.verify_chain(N, [st])
    # (5) one addition: a nonzero denominator that is not invertible, and two points with
    # the same x that are neither equal nor opposite (ver_inconsistent), show a composite
    with pytest.raises(pr._Composite):
        pr._ec_add((1, 1), (6, 2), 0, 35)
    with pytest.raises(pr._Composite):
        pr._ec_add((1, 1), (1, 2), 0, 35)
    assert pr._ec_add((1, 1), (1, 34), 0, 35) is None


def test_composite_moduli_and_malformed_steps_are_rejected(tmp_path):
    # The rejections that no certificate of the store reaches.
    from math import gcd, isqrt
    # (1) a singular curve (4a^3 + 27b^2 = 0 mod N) is rejected. The step would fail
    #     [q]Q = O as well (on the cusp y^2 = x^3 modulo the prime 10007 every affine point
    #     other than the cusp (0, 0) has order 10007, not 1009), so this assertion does not
    #     see the discriminant check; the step theorem does not need it (ver_disc is an
    #     expected survivor of experiments/planted_mutations.py)
    assert (1 - 1 - 0 - 0) % 10007 == 0 and 1009 >= (isqrt(isqrt(10007)) + 2) ** 2
    assert pr._ec_mul(1009, pr._ec_mul(2, (1, 1), 0, 10007), 0, 10007) is not None
    assert not pr._verify_values(10007, 0, 0, 2018, 1009, 1, 1)
    # (2) the chord-tangent formulas expose a composite N = 1009 * 1013: equal x with
    #     y1 = y2 mod 1009 and y1 = -y2 mod 1013, or a denominator divisible by 1009
    N = 1009 * 1013
    y2 = 5 + 1009 * ((-10 * pow(1009, -1, 1013)) % 1013)
    assert y2 % 1009 == 5 and (5 + y2) % 1013 == 0 and (5 + y2) % N != 0
    with pytest.raises(pr._Composite):
        pr._ec_add((7, 5), (7, y2), 1, N)
    with pytest.raises(pr._Composite):
        pr._ec_add((7, 5), (7 + 1009, 9), 1, N)
    # (3) a forged step on that N that passes the curve, discriminant and size checks: its
    #     scalar multiplication meets a non-invertible denominator, and the step is rejected
    st = {"N": N, "a": 921402, "b": 932887, "m": 3291, "q": 1097, "x": 891841, "y": 39758}
    a, b, x, y, q = st["a"], st["b"], st["x"], st["y"], st["q"]
    assert (y * y - x**3 - a * x - b) % N == 0 and gcd(4 * a**3 + 27 * b * b, N) == 1
    assert pr.small_proved_prime(q) and q >= (isqrt(isqrt(N)) + 2) ** 2 and st["m"] % q == 0
    with pytest.raises(pr._Composite):
        pr._ec_mul(q, pr._ec_mul(st["m"] // q, (x, y), a, N), a, N)
    assert not pr.verify_step(st) and not pr.verify_chain(N, [st])
    # (4) a step with a missing key, and a store file that does not exist
    bad = {k: v for k, v in st.items() if k != "y"}
    assert not pr.verify_step(bad) and not pr.verify_chain(N, [bad])
    assert pr.load_store(tmp_path / "missing.json.gz") == {}


def test_every_recording_site_records_a_claim_above_2_64():
    from sympy import nextprime as np_
    from core import cadeias
    big = int(np_(2**64))
    led = omega_k.enable_prime_ledger()
    try:
        assert omega_k._primo(big) and big in led
        led.clear()
        assert big in omega_k._fatores_primos(big * 3) and big in led
        led.clear()
        assert omega_k._proximo_primo(2**64) == big and big in led
        led.clear()
        k = 2
        while not isprime(k * big + 1):
            k += 2
        assert (big, 1) in cadeias.fatoracao_q_menos_1(k * big + 1) and big in led
    finally:
        omega_k.disable_prime_ledger()


def test_enabling_the_ledger_clears_the_caches():
    # a factorization cached while no ledger was enabled must be computed again, and its
    # primes recorded, once the ledger is enabled (memo caches of core.omega_k and
    # core.cadeias)
    from core import cadeias
    big = int(nextprime(2**64))
    k = 2
    while not isprime(k * big + 1):
        k += 2
    omega_k.disable_prime_ledger()
    omega_k._fatora(big * 7)
    cadeias.fatoracao_q_menos_1(k * big + 1)
    led = omega_k.enable_prime_ledger()
    try:
        assert omega_k._fatora(big * 7) == (7, big) and big in led
        led.clear()
        assert (big, 1) in cadeias.fatoracao_q_menos_1(k * big + 1) and big in led
    finally:
        omega_k.disable_prime_ledger()


def test_the_ledger_of_k_up_to_8_has_the_expected_size(store):
    led = omega_k.enable_prime_ledger()
    try:
        for k in range(1, 9):
            omega_k.certifica_omega(k, light=True)
        claims = sorted(led)
    finally:
        omega_k.disable_prime_ledger()
    # 10 claims >= 2^64 for k <= 8: 2 below psi_13 and 8 with a certificate
    assert len(claims) == 10
    assert sum(n < pr.MR_LIMIT for n in claims) == 2
    assert all(pr.proved_prime(n, store) for n in claims)

