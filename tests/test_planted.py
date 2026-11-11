"""Planted friends driven through the whole recursive certifier (Phase 1, Block 8).

A planted friend is an N0 that satisfies the structural hypotheses of the certifier (an odd
square, 5 its least prime, 3 not dividing it). Its target is t = I(N0); with
core.omega6.ALVO = t, certifica_omega(omega(N0)) must find N0. Since Block 8 the budget
partition is generic in the target, so these runs exercise the real machine (closures,
budgets, last-unknown solver, tails, finite exponent bound, split, index), not a
stand-in. A step that fires somewhere in the tree of a run need not act on the path of
its friend: test_planted_runs_exercise_every_step_of_the_partition checks along the path
the three cases of the split, a tail, the finite exponent bound and the last-unknown
solver. See results/PHASE_1.md, Block 8.

The certifier is a cover, not a disjoint split: a friend may be reached along several
paths, so the tests compare sets of distinct signatures, never counts. For the same
reason "found" alone cannot see a node that drops the friend while another path still
reaches it; the end-to-end runs therefore also check every node that contains the friend
(_run_checked): it must have a child that contains the friend, or report it.
"""
import os
from fractions import Fraction
from itertools import combinations

import pytest
from sympy import factorint, nextprime

import core.omega6 as omega6
import core.omega_k as omega_k
from core.cadeias import ordens_impares, v_p
from core.motor import I_pp, sigma_pp
from core.omega_k import NaoCertificavel, StatsK, certifica_omega

# id: (signature, what it exercises)
PLANTED = {
    "P01": ({5: 2, 7: 2, 11: 2, 19: 2, 31: 4}, "budgets as for 9/5 (T5 = a1 - 1, T3 = 2); an order witnessed only by an extra"),
    "P02": ({5: 2, 7: 2, 11: 2, 31: 4, 67: 2}, "budgets as for 9/5"),
    "P03": ({5: 2, 7: 2, 11: 2, 19: 2, 31: 4, 127: 4}, "budgets as for 9/5, k = 6"),
    "P04": ({5: 2, 31: 2, 421: 2, 59221: 4}, "budgets as for 9/5, a 62-bit extra"),
    "P05": ({5: 2, 7: 2, 11: 2, 19: 2, 31: 4, 37: 2, 67: 2}, "close to 9/5, k = 7"),
    "P06": ({5: 2, 7: 2, 11: 2, 19: 2, 31: 4, 37: 2, 67: 2, 439: 2}, "close to 9/5, k = 8 (slow); splits and Cor. 6 in the tree, not on the friend's path"),
    "P07": ({5: 2, 7: 2, 11: 2, 19: 2, 31: 4, 67: 2, 17351: 4}, "k = 7, two feeders of 5, 5 not in den"),
    "P08": ({5: 2, 7: 2, 11: 2, 19: 2, 31: 2, 37: 2, 67: 2, 439: 2}, "k = 8 (slow); splits and Cor. 6 in the tree, not on the friend's path"),
    "P09": ({5: 2, 7: 2, 11: 2, 19: 2, 31: 2, 67: 2}, "k = 6, T5 = 0"),
    "P10": ({5: 2, 7: 2, 19: 2, 31: 2, 37: 2, 67: 2, 163: 2}, "k = 7; splits and Cor. 6 in the tree, not on the friend's path"),
    "P11": ({5: 4, 11: 4, 71: 2}, "a1 = 4, sigma(5^4) = 11 * 71, 3 not in num"),
    "P12": ({5: 4, 11: 4, 71: 2, 5113: 2}, "a1 = 4, T3 = 1"),
    "P13": ({5: 4, 11: 4, 71: 2, 3221: 4, 5113: 2}, "a1 = 4, two feeders of 5"),
    "P14": ({5: 4, 11: 4, 3221: 4}, "a1 = 4, three extras"),
    "P15": ({5: 4, 11: 4, 71: 4, 3221: 4}, "a1 = 4, three feeders of 5"),
    "P16": ({5: 6, 11: 4, 19531: 2}, "sigma(5^6) = 19531 prime"),
    "P17": ({5: 6, 7: 2, 11: 2, 19: 2, 19531: 2}, "sigma(5^6) = 19531 prime, T5 = 0"),
    "P18": ({5: 6, 421: 2, 19531: 2, 59221: 4}, "sigma(5^6) prime, a 62-bit extra"),
    "P19": ({5: 10, 11: 4, 3221: 4}, "sigma(5^10) prime and not in N0, a1_min = 8"),
    "P20": ({5: 12, 421: 2, 59221: 4}, "sigma(5^12) prime and not in N0, a1_min = 12"),
    "P21": ({5: 2, 11: 4, 31: 4, 17351: 4}, "5 divides num"),
    "P22": ({5: 2, 11: 4, 31: 4, 3221: 4}, "5 divides num"),
    "P23": ({5: 2, 11: 4, 31: 4, 3221: 4, 17351: 4}, "5^2 divides num, four feeders of 5"),
    "P24": ({5: 2, 11: 4, 31: 4}, "3 does not divide num"),
    "P25": ({5: 2, 31: 2, 67: 2}, "a small extra (7)"),
    "P26": ({5: 2, 7: 2, 31: 2, 67: 2}, "a small extra (19)"),
    "P27": ({5: 2, 31: 2, 331: 2}, "smoke test"),
    "P28": ({5: 2, 19: 2, 127: 2}, "31 = sigma(5^2) in num, not in N0"),
    "X01": ({5: 2, 11: 4}, "a1 bound needs e5"),
    "X02": ({5: 2, 19: 6}, "L over C and extras"),
    "X03": ({5: 2, 23: 4}, "L over C and extras"),
    "X04": ({5: 2, 11: 2, 13: 2, 17: 2, 19: 2, 29: 6}, "eps = 1 for an extra ell (7 | num, 29 = 1 mod 7)"),
    "X05": ({5: 2, 11: 2, 17: 2, 23: 2, 29: 2, 41: 2}, "k = 6; splits and Cor. 6 in the tree, not on the friend's path"),
    "X06": ({5: 2, 7: 2, 13: 2, 17: 2, 19: 2, 41: 4}, "a1 bound needs e5"),
    "X07": ({5: 4, 7: 2, 11: 2, 13: 2, 17: 2, 19: 2}, "a1 = 4 in the index regime"),
    "X08": ({5: 2, 7: 4}, "L over C and extras"),
    "X09": ({5: 2, 7: 2}, "injective feasibility over C and extras"),
    "X10": ({5: 2, 11: 2, 6779: 4}, "total-closure lemma with unknowns in num"),
    "X11": ({5: 2, 7: 2, 11: 2, 13: 2, 17: 2, 22751: 4}, "solver cap a_q + v_q(num): 11^3 divides Phi_5(22751)"),
    "X12": ({5: 2, 7: 2, 11: 2}, "small, many extras"),
    "X13": ({5: 10, 7: 2}, "a1 = 10 = v5(den): the lower bound of the range of a1 is tight"),
    "X14": ({5: 2, 11: 24, 13: 2, 17: 2, 19: 2, 23: 2}, "k_max cap uses the same witness pool"),
    "X15": ({5: 2, 11: 2, 13: 2, 17: 2, 19: 2, 281: 4}, "k = 6, many solver calls"),
    "X16": ({5: 2, 31: 2, 67: 2, 149: 2}, "total-closure lemma with an unknown prime of num in den(x)"),
    "X17": ({5: 2, 67: 2, 71: 2}, "total-closure lemma"),
    "X18": ({5: 2, 11: 4, 31: 4, 41: 4}, "5 divides num"),
    "X19": ({5: 2, 11: 24, 31: 4}, "5 divides num, v5(a + 1) = 2"),
    "X20": ({5: 2, 11: 4, 31: 4, 61: 4}, "5 divides num"),
    "X21": ({5: 2, 11: 4, 41: 4, 61: 4}, "5 divides num"),
    # constructed for the regions that small primes never reach (Block 8 adversarial round)
    "R01": ({5: 2, 7: 4, 2003: 2, 2027: 2}, "split case (b), U_1 > B, then Cor. 6 at s = 2"),
    "R02": ({5: 2, 7: 4, 3001: 2, 30011: 2}, "split (a), tail on 7 (second exact value), split (b) with hi kept"),
    "R03": ({5: 2, 7: 6, 1511: 4, 1531: 2}, "split offering (a), (a2) and (b); the friend is in (b)"),
    "R04": ({5: 2, 7: 4, 11: 4, 1511: 2, 1523: 2}, "split (b), nested Cor. 6 on 11 and 7"),
    "R05": ({5: 2, 701: 2, 344472103: 2}, "split case (a2): U_1 = B"),
    "R06": ({5: 2, 31: 4, 5351: 2, 153216258673: 2}, "case (a2) and a tight virtual factor"),
    "R07": ({5: 2, 31: 4, 7577: 2, 57418519: 2}, "tight virtual factor, tail on 31"),
    "R08": ({5: 2, 7: 6, 1103: 2, 500001272101: 2}, "virtual factor within 1/hi^3"),
    "R09": ({5: 2, 7: 2, 17: 4, 347: 2}, "tail: the friend at the start of the tail"),
    "R10": ({5: 4, 29: 4, 31: 8, 20524187: 2}, "tail; per-feeder cap with extras as witnesses"),
    "R11": ({5: 2, 7: 8, 6353: 2, 121964100157: 2}, "split (b), tail and virtual factor"),
    "R12": ({5: 2, 29: 2, 37: 2, 59: 10, 67: 2}, "last unknown: caps of extras, an extra may be U"),
    "R13": ({5: 2, 7: 2, 11: 2, 23: 2, 67: 2}, "index loop must not skip the primes of num"),
    "R14": ({5: 2, 11: 4, 3257: 2}, "range of a1 at C = {5, 3257} needs e5"),
    "R15": ({5: 2, 19: 2, 1873: 2, 2819: 2}, "split (b) with Cor. 6"),
    "R16": ({5: 2, 61: 2, 677: 2, 459013: 2}, "tight virtual factor"),
    "R17": ({5: 2, 13: 2, 761: 2, 2203: 2}, "split case (a2)"),
    "R18": ({5: 2, 11: 6, 9391: 2, 22250243: 2, 31: 2}, "split case (a2), k = 5"),
    "R19": ({5: 2, 29: 2, 1459: 2, 24953: 2, 41: 4}, "tail; split (a) bound B - 1"),
    # added after the whole-code pass of Block 8
    "R20": ({5: 2, 7: 2, 29: 6}, "last unknown, mode (0, 0): eps = 1 for ell = 7 in C"),
    "R21": ({5: 2, 7: 2, 11: 2, 29: 6}, "last unknown, mode (0, 0): eps = 1 for ell = 7 in C"),
    "R22": ({5: 16, 7: 2, 461: 4}, "last unknown with every cap attained: R_max includes ell^eps"),
    "R23": ({5: 16, 7: 2, 521: 4}, "last unknown with every cap attained: R_max includes ell^eps"),
    "R24": ({5: 2, 1333167020982637261167217: 2}, "a large prime (r - 1 above 80 bits) in a complete set"),
    "R25": ({5: 2, 1481: 2, 3248367653: 2}, "index fallback at s = 1: the span guard uses B_min, not L1 "
                                             "(the L1 guard refused it)"),
    "R26": ({5: 2, 1213: 2, 1784770613: 2}, "index fallback at s = 1: the span guard uses B_min"),
    "R27": ({5: 2, 37: 2, 67: 4}, "the v3 budget cuts a signature inside the complete-set test "
                                  "(5^2 37^2 67^2 carries v3 = 2 > v3(num) = 1)"),
}
SLOW = {"P06", "P08"}          # the two most expensive runs; run with SOLITARY_SLOW=1
FAST = sorted(set(PLANTED) - SLOW)


def _I(sig: dict[int, int]) -> Fraction:
    x = Fraction(1)
    for p, a in sig.items():
        x *= I_pp(p, a)
    return x


def _sigma(sig: dict[int, int]) -> int:
    s = 1
    for p, a in sig.items():
        s *= sigma_pp(p, a)
    return s


def _found(st: StatsK) -> set[tuple]:
    return {tuple(sorted(a.items())) for a in st.amigos}


@pytest.fixture
def alvo(monkeypatch):
    def set_target(t: Fraction) -> Fraction:
        monkeypatch.setattr(omega6, "ALVO", t)
        return t
    return set_target


def _nodes(sig: dict[int, int]):
    """Every consistent node of N0: 5 in C, C a subset of S, s = |S minus C| unknowns."""
    S = sorted(sig)
    rest = S[1:]
    for r in range(len(rest) + 1):
        for extra in combinations(rest, r):
            C = [5] + list(extra)
            yield C, len(S) - len(C)


# ---------------------------------------------------------------------------
# The planted targets are what they claim
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("pid", sorted(PLANTED))
def test_planted_friend_satisfies_the_hypotheses(pid, alvo):
    sig, _ = PLANTED[pid]
    assert min(sig) == 5 and 3 not in sig and all(a % 2 == 0 and a >= 2 for a in sig.values())
    t = alvo(_I(sig))
    N0 = 1
    for p, a in sig.items():
        N0 *= p ** a
    assert N0 % t.denominator == 0                         # den | N0
    extras, fnum, fden = omega_k._alvo()                   # admissible: no refusal
    assert set(fnum) == set(factorint(t.numerator)) == extras
    # every prime of sigma(N0) lies in S or in primes(num)
    assert set(factorint(_sigma(sig))) <= set(sig) | extras


# ---------------------------------------------------------------------------
# Statement level: the generic budgets, the range of a1, the total-closure lemma
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("pid", sorted(PLANTED))
def test_generic_budgets_are_the_valuations_of_sigma(pid, alvo):
    sig, _ = PLANTED[pid]
    alvo(_I(sig))
    s = _sigma(sig)
    assert omega_k._orcamento5(sig[5]) == v_p(5, s)
    assert omega_k._orcamento3() == v_p(3, s)
    # and the feeders carry them (Fact 2, even exponents)
    assert v_p(5, s) == sum(v_p(5, a + 1) for q, a in sig.items() if q % 5 == 1)
    assert v_p(3, s) == sum(v_p(3, a + 1) for q, a in sig.items() if q % 3 == 1)


@pytest.mark.parametrize("pid", sorted(PLANTED))
def test_range_of_a1_contains_the_planted_exponent_at_every_node(pid, alvo):
    sig, _ = PLANTED[pid]
    alvo(_I(sig))
    for C, s in _nodes(sig):
        a1_min, a1_max = omega_k._faixa_a1(C, s)
        assert a1_min <= sig[5] <= a1_max, (C, s, a1_min, a1_max)


def test_range_of_a1_has_a_lower_bound_when_5_divides_den_more_than_once(alvo):
    for pid, low in (("P19", 8), ("P20", 12), ("X13", 10)):     # v5(den) = 8, 11, 10
        sig, _ = PLANTED[pid]
        alvo(_I(sig))
        assert omega_k._faixa_a1([5], len(sig) - 1)[0] == low


@pytest.mark.parametrize("pid", sorted(PLANTED))
def test_total_closure_lemma_never_kills_a_planted_friend(pid, alvo):
    # At every node whose precondition holds (all of C fixed at the exponents of N0, and
    # every sigma(q^a), q in C, supported on C and the extras), the lemma must not fire.
    sig, _ = PLANTED[pid]
    t = alvo(_I(sig))
    extras = omega_k._alvo()[0]
    S = sorted(sig)
    checked = 0
    for C, s in _nodes(sig):
        if s == 0:
            continue
        if not all(set(factorint(sigma_pp(q, sig[q]))) <= set(C) | extras for q in C):
            continue
        U1 = min(set(S) - set(C))
        lo = max(p for p in C if p < U1)            # every prime of S <= lo is in C
        x = t / _I({q: sig[q] for q in C})
        assert not omega_k._fecho_total_mata(x, C, s, lo), (C, s, lo, x)
        checked += 1
    if not checked:
        # e.g. the primes of sigma(5^a1) close only over all of S: nothing to check
        pytest.skip("no node of this friend satisfies the precondition of the lemma")


# ---------------------------------------------------------------------------
# End to end
# ---------------------------------------------------------------------------

def _run(sig: dict[int, int]) -> StatsK:
    return certifica_omega(len(sig), light=True)


def _contains(sig, C, s, lo, fixos, minimos, maximos, hi) -> bool:
    """Does the node (C, s, lo, fixos, minimos, maximos, hi) contain N0 = sig? C is a
    subset of its primes with s unknowns left, the fixed exponents and the bounds agree
    with N0, every unknown is > lo and, if hi is set, the smallest unknown is <= hi."""
    S = set(sig)
    unk = S - set(C)
    return (set(C) <= S and s == len(unk)
            and all(sig.get(p) == a for p, a in fixos.items())
            and all(sig.get(p, a) >= a for p, a in minimos.items())
            and all(sig.get(p, a) <= a for p, a in maximos.items())
            and all(u > lo for u in unk)
            and (hi is None or (len(unk) > 0 and min(unk) <= hi)))


def _run_checked(sig: dict[int, int]) -> tuple[StatsK, list, set[str]]:
    """certifica_omega(omega(N0)) with every node watched. Returns (stats, kills, steps).
    kills: the nodes that contain N0 but have no child that contains it (s >= 1) or do
    not report it (s = 0), i.e. a false kill, even when another path still finds N0.
    steps: what acted on N0 along its path: "tail" (a lower bound from a tail), "cor6"
    (an upper bound from the finite exponent bound), the case of a split that holds N0
    ("split (a)", "split (a2)", "split (b)"), and "solver" (the last-unknown solver
    returned the last unknown of N0)."""
    real, real_split, real_solver = (omega_k._certifica, omega_k._split_cases,
                                     omega_k._ultimo_desconhecido)
    key, S = tuple(sorted(sig.items())), set(sig)
    stack, kills, steps = [], [], set()

    def certifica(C, s, lo, stats, fixos=None, minimos=None, maximos=None, hi=None):
        node = (list(C), s, lo, dict(fixos or {}), dict(minimos or {}), dict(maximos or {}), hi)
        inside = _contains(sig, *node)
        if inside:
            steps.update(name for name, bound in (("tail", node[4]), ("cor6", node[5])) if bound)
            if stack:
                stack[-1][1] = True             # the parent has a child that contains N0
        stack.append([inside, False])
        before = len(stats.amigos)
        try:
            real(C, s, lo, stats, fixos, minimos, maximos, hi)
        finally:
            had_child = stack.pop()[1]
        if inside and (not had_child if s >= 1 else
                       key not in {tuple(sorted(a.items())) for a in stats.amigos[before:]}):
            kills.append(node)

    def split_cases(C, s, lo, fixos, minimos, maximos, hi):
        cases = real_split(C, s, lo, fixos, minimos, maximos, hi)
        if cases is not None and _contains(sig, C, s, lo, fixos, minimos, maximos, hi):
            U1, B = min(S - set(C)), cases[0][2] + 1         # case (a) is ((), None, B - 1)
            steps.add("split (a)" if U1 < B else "split (a2)" if U1 == B else "split (b)")
        return cases

    def solver(C, lo, fixos, k5, k3, prod_sup, hi=None):
        cands = real_solver(C, lo, fixos, k5, k3, prod_sup, hi)
        if (cands and stack and stack[-1][0] and all(sig.get(p) == a for p, a in fixos.items())
                and S - set(C) <= set(cands)):
            steps.add("solver")
        return cands

    omega_k._certifica, omega_k._split_cases, omega_k._ultimo_desconhecido = (
        certifica, split_cases, solver)
    try:
        st = certifica_omega(len(sig), light=True)
    finally:
        omega_k._certifica, omega_k._split_cases, omega_k._ultimo_desconhecido = (
            real, real_split, real_solver)
    return st, kills, steps


@pytest.mark.parametrize("pid", FAST)
def test_planted_friend_is_found_end_to_end(pid, alvo):
    sig, _ = PLANTED[pid]
    t = alvo(_I(sig))
    st, kills, _ = _run_checked(sig)
    assert tuple(sorted(sig.items())) in _found(st)
    assert all(_I(a) == t for a in st.amigos)
    assert st.particoes > 0                     # the budget partition was really used
    assert kills == [], kills[:3]               # no node that contains N0 dropped it


@pytest.mark.skipif(not os.environ.get("SOLITARY_SLOW"), reason="slow: set SOLITARY_SLOW=1")
@pytest.mark.parametrize("pid", sorted(SLOW))
def test_planted_friend_is_found_end_to_end_slow(pid, alvo):
    sig, _ = PLANTED[pid]
    t = alvo(_I(sig))
    st, kills, _ = _run_checked(sig)
    assert tuple(sorted(sig.items())) in _found(st)
    assert all(_I(a) == t for a in st.amigos)
    assert kills == [], kills[:3]


def test_planted_runs_exercise_every_step_of_the_partition(alvo):
    # Each step must act on the friend along its own path, not merely fire somewhere in
    # the tree: R02 a split in case (a), R03 a split in case (b) and the finite exponent
    # bound, R05 case (a2) of a split, R09 a tail, X16 the last-unknown solver.
    want = {"R02": {"split (a)"}, "R03": {"split (b)", "cor6"}, "R05": {"split (a2)"},
            "R09": {"tail"}, "X16": {"solver"}}
    n_pins = dead_hi = 0
    for pid, steps_wanted in want.items():
        sig, _ = PLANTED[pid]
        alvo(_I(sig))
        st, kills, steps = _run_checked(sig)
        assert tuple(sorted(sig.items())) in _found(st) and kills == [], pid
        assert steps_wanted <= steps, (pid, steps)
        n_pins += st.n_pins
        dead_hi += st.dead_hi
    # tree counters (anywhere in these trees): pins, and nodes killed because no unknown
    # can be <= hi (such a kill is never on the path of a friend)
    assert n_pins > 0 and dead_hi > 0


def test_a_large_prime_goes_through_the_large_prime_lemma(monkeypatch, alvo):
    # R24 = 5^2 r^2 with r - 1 above ORDEM_BITS (never factored) and r = 1 (mod 3), so that
    # T3 = 1 and the solver finds r through the budget of 3 (the two primes r = 2 (mod 3)
    # built the same way during the review were refused, not found). Finding the friend
    # proves that the list of 5 was composed by the lemma; conjuntos_com_primo_grande alone
    # would not (it is counted before the return on an empty list of r, which is how all
    # 201 large-prime sets of k = 9 die).
    sig, _ = PLANTED["R24"]
    r = max(sig)
    assert (r - 1).bit_length() > omega_k.ORDEM_BITS and r % 3 == 1
    assert omega_k._pr.small_proved_prime(r)
    alvo(_I(sig))
    chamadas = []
    lema = omega_k._expoentes_com_primo_grande
    monkeypatch.setattr(omega_k, "_expoentes_com_primo_grande",
                        lambda *a: chamadas.append(a[0]) or lema(*a))
    st = _run(sig)
    assert tuple(sorted(sig.items())) in _found(st) and st.conjuntos_com_primo_grande >= 1
    assert 5 in chamadas


@pytest.mark.parametrize("a1", [14, 32, 44])
def test_planted_friends_at_composite_orders(a1, alvo):
    # a1 + 1 = 15, 33, 45: sigma(5^a1) has cyclotomic pieces Phi_d(5) with d divisible by
    # two distinct primes, the only values core.omega_k._phi_valor takes from
    # sympy.cyclotomic_poly (the k <= 8 runs of 9/5 use d = 15, 21, 33, 35, 39 only; from
    # k = 9 the range of a1 reaches 45, 51, 55, 57). A wrong value there loses the friend;
    # no friend of PLANTED has such an order.
    sig = {5: a1, 7: 2}
    t = alvo(_I(sig))
    st = _run(sig)
    assert tuple(sorted(sig.items())) in _found(st)
    assert all(_I(a) == t for a in st.amigos)


# ---------------------------------------------------------------------------
# Node level
# ---------------------------------------------------------------------------

def _from_node(C, s, lo, fixos) -> StatsK:
    st = StatsK(k=len(C) + s)
    omega_k._certifica(C, s, lo, st, dict(fixos), {}, {}, None)
    return st


def test_node_with_an_unknown_prime_of_num_in_den_x_reaches_the_friend(alvo):
    # X16 = 5^2 31^2 67^2 149^2: at C = {5, 67, 149}, all fixed, x = 993/961 and the
    # unknown 31, a prime of num (an extra), divides den(x) = 31^2; the 9/5 form of the
    # total-closure lemma (den(x) != 1) would kill this node.
    sig, _ = PLANTED["X16"]
    t = alvo(_I(sig))
    C = [5, 67, 149]
    x = t / _I({q: sig[q] for q in C})
    assert x.denominator != 1 and not omega_k._fecho_total_mata(x, C, 1, 5)
    st = _from_node(C, 1, 5, {q: sig[q] for q in C})
    assert tuple(sorted(sig.items())) in _found(st)


def test_node_where_the_last_unknown_needs_the_cap_of_num(alvo):
    # X11 = 5^2 7^2 11^2 13^2 17^2 22751^4: 11^3 exactly divides Phi_5(22751) while a_11 = 2;
    # the cap e_11 <= a_11 + v11(num) - v11(den) = 3 is what lets the solver see it.
    sig, _ = PLANTED["X11"]
    t = alvo(_I(sig))
    C = [5, 7, 11, 13, 17]
    fixos = {q: sig[q] for q in C}
    assert v_p(11, (22751**5 - 1) // 22750) == 3 and v_p(11, t.numerator) == 1
    prod_sup = omega_k._prod_min_sup(C, fixos, {}, {})[1]
    assert omega_k._cota_indice_U(prod_sup) == 22751
    assert omega_k._ultimo_desconhecido(C, 17, fixos, 1, 0, prod_sup) == [22751]
    st = _from_node(C, 1, 17, fixos)
    assert tuple(sorted(sig.items())) in _found(st)


def test_node_where_a_level_is_witnessed_only_by_an_extra(alvo):
    # X14 = 5^2 11^24 13^2 17^2 19^2 23^2: v5(25) = 2 levels for the feeder 11, witnessed
    # only by primes of num that are not primes of N0. At the node C = {5, 11, 13, 17, 19},
    # s = 1 (the unknown 23 does not feed 5), the budget case list must keep 11 with k = 2:
    # with witnesses searched in C only, the two levels would need two distinct unknowns,
    # more than s = 1. (The run from the root is test_planted_friend_is_found_end_to_end.)
    sig, _ = PLANTED["X14"]
    alvo(_I(sig))
    extras = omega_k._alvo()[0]
    ws = [r for r in sorted(set(sig) | extras) if r != 11
          and omega_k._ordem_e_potencia(11, r, 5, 2)]
    assert ws and all(r not in sig for r in ws)      # level 2 is witnessed by extras only
    C, fixos = [5, 11, 13, 17, 19], {5: sig[5]}
    T5 = omega_k._orcamento5(sig[5])
    assert T5 == 2 and [q for q in C if q % 5 == 1] == [11]
    # 11 is the only known feeder of 5, so the open case with nothing left for the
    # unknown is exactly the assignment k_11 = 2
    assert ("aberto", 0) in omega_k._casos_ell(C, 1, 19, 5, T5, fixos)
    st = _from_node(C, 1, 19, fixos)
    assert tuple(sorted(sig.items())) in _found(st)
    # The node C = {5, 11}, s = 4, with 11 fixed at 24: v5(25) = 2 forces k_11 = 2; with
    # witnesses among the primes of N only, the case would be a pin of witnesses that
    # are not primes of N0
    fixos = {5: sig[5], 11: sig[11]}
    assert omega_k._casos_ell([5, 11], len(sig) - 2, 11, 5,
                              omega_k._orcamento5(sig[5]), fixos) == [("aberto", 0)]
    st = _from_node([5, 11], len(sig) - 2, 11, fixos)
    assert tuple(sorted(sig.items())) in _found(st)


@pytest.mark.parametrize("sig,r", [({5: 2, 7: 2, 29: 6}, 7), ({5: 2, 11: 2, 23: 10}, 11),
                                   ({5: 2, 7: 2, 43: 6}, 7), ({5: 2, 13: 2, 53: 12}, 13)])
def test_exponent_bound_counts_the_primes_of_num_as_witnesses(sig, r, alvo):
    # The finite exponent bound in the form that is true for every target (the count of
    # Corollary 6 of arXiv:2310.15900 with the primes of num as witnesses, results/ERRATA.md
    # E6): the level r | a_q + 1 of the feeder q = 1 (mod r) is witnessed by a prime of num
    # that is not a prime of N0. The bound is attained, A_r = a_r = 2; with witnesses taken
    # among the primes of N only (the step of the printed proof) it would be 1 < a_r, which
    # is how mutant cor6_pool_C of experiments/planted_mutations.py is killed. This is a
    # check of the formula, evaluated here with every prime of N0 known (s = 0): on the
    # path of a friend the certifier evaluates the bound only at nodes with two unknowns.
    # End to end N0 is still found with that restriction (the bound never fires on these
    # runs), and N0 is not an instance of the printed corollary (v_q(I(N0)) != 0 for its
    # largest q).
    alvo(_I(sig))
    q = max(sig)
    assert q % r == 1 and (sig[q] + 1) % r == 0
    extras = omega_k._alvo()[0]
    assert any(e % r == 1 and e not in sig for e in extras)
    C = sorted(sig)
    assert omega_k._cota_expoente_conhecido(r, C, 0, {5: sig[5]}, None) == sig[r] == 2
    st = certifica_omega(len(sig), light=True)
    assert tuple(sorted(sig.items())) in _found(st)


def test_node_where_the_virtual_factor_meets_the_target_exactly(alvo):
    # prod_min * v(hi) = t with s = 1: the friend lives exactly at equality (U_1 = hi)
    sig = {5: 2, 31: 2, 67: 2}
    t = alvo(_I(sig))
    assert omega_k._prod_min_sup([5, 31], {}, {}, {})[0] * omega_k._virtual(67) == t
    st = StatsK(k=3)
    omega_k._certifica([5, 31], 1, 31, st, {}, {}, {}, 67)
    assert tuple(sorted(sig.items())) in _found(st)


def test_nodes_with_upper_bounds_attained(alvo):
    # maximos equal to the true exponents: the exponent lists and the s = 0 test must
    # keep the friend (an upper bound is attainable, unlike p/(p-1))
    sig = {5: 2, 31: 2, 67: 2}
    alvo(_I(sig))
    for fixos in ({}, {5: 2}):
        st = StatsK(k=3)
        omega_k._certifica([5, 31, 67], 0, 67, st, dict(fixos), {}, {31: 2, 67: 2}, None)
        assert tuple(sorted(sig.items())) in _found(st), fixos


def test_node_with_a_lower_bound_attained(alvo):
    # minimos equal to the true exponent (a tail a_q >= A whose friend has a_q = A): the
    # exponent list of q in the complete set must keep A; here prod_min equals the target
    sig = {5: 2, 11: 24, 13: 2, 17: 2, 19: 2, 23: 2}
    t = alvo(_I(sig))
    C = sorted(sig)
    assert omega_k._prod_min_sup(C, {5: 2}, {11: 24}, {})[0] == t
    st = StatsK(k=len(sig))
    omega_k._certifica(C, 0, 23, st, {5: 2}, {11: 24}, {}, None)
    assert tuple(sorted(sig.items())) in _found(st)


def test_exponent_bound_respects_attained_upper_bounds(alvo):
    # 29 = 1 (mod 7) with a_29 + 1 = 7: the level cap from maximos[29] = 6 is one level,
    # and with it the bound on a_7 is attained (= 2)
    alvo(_I({5: 2, 7: 2, 29: 6}))
    assert omega_k._cota_expoente_conhecido(7, [5, 7, 29], 0, {5: 2}, None, {29: 6}) == 2
    # and for every fast planted friend: all known, every other exponent bounded above by
    # its true value (attained), the bound on each a_r stays >= the true a_r
    for pid in FAST:
        sig, _ = PLANTED[pid]
        if len(sig) > 6 or max(sig) > 10**6:
            continue
        alvo(_I(sig))
        C = sorted(sig)
        for r in C[1:]:
            maximos = {q: sig[q] for q in C if q not in (5, r)}
            A = omega_k._cota_expoente_conhecido(r, C, 0, {5: sig[5]}, None, maximos)
            assert A is None or A >= sig[r], (pid, r, A)


def test_level_cap_from_maximos_is_exact():
    # _cap_nivel(r, M) must be the largest v_r(a + 1) over the even exponents 2 <= a <= M:
    # a smaller cap can kill a friend with a_q = r^j - 1 <= M (mutant cap_nivel_off), a
    # larger one only weakens the bound. The test above pins one value (r = 7, M = 6);
    # this one pins the table for r = 5, 7, 11, 13, 29, 31 and M < 3000.
    assert omega_k._cap_nivel(7, None) is None
    for r in (5, 7, 11, 13, 29, 31):
        best = 0
        for M in range(3000):
            if M >= 2 and M % 2 == 0:
                best = max(best, v_p(r, M + 1))
            assert omega_k._cap_nivel(r, M) == best, (r, M)


@pytest.mark.parametrize("sig,C,s,lo,fixos,path", [
    ({5: 2, 5003: 2, 5009: 2, 5011: 2}, [5, 5003], 2, 5003, {}, "expensive"),
    ({5: 2, 7: 8, 1733: 2, 5003: 2, 5009: 2}, [5, 7, 1733], 2, 1733, {5: 2}, "wieferich"),
    ({5: 2, 7: 4, 29: 2, 1009: 2, 2003: 2, 2027: 2}, [5, 7, 29, 1009], 2, 1009, {5: 2}, "cap"),
])
def test_nodes_where_the_finite_exponent_bound_branches_on_the_friend(sig, C, s, lo, fixos, path,
                                                                       monkeypatch, alvo):
    # From each start node, at nodes consistent with the friend (C inside S, s = |S| - |C|,
    # fixed exponents those of N0, upper bounds at or above them), the certifier takes a
    # piece of the bound that the other planted friends never take; a spy on
    # _cota_expoente_conhecido, restricted to those nodes, checks it:
    #   expensive: a bound for a free prime above R_CHEAP_PROP9 (coverage ahead of k = 10:
    #              the k = 9 run never evaluates that group);
    #   wieferich: w_7(1733) = 3, the second iteration of the Wieferich loop (used at k = 9);
    #   cap:       the free feeder 29 = 1 (mod 7) with an upper bound, min(niv, cap) < niv
    #              (used at k = 9).
    # None of them is sharp (the unknowns' term carries slack): they show that these pieces
    # keep the friend, not that their constants are exact. The level cap is pinned by
    # test_level_cap_from_maximos_is_exact, the feeder levels by the attained bounds
    # above.
    alvo(_I(sig))
    cota = omega_k._cota_expoente_conhecido
    chamadas = []

    def spy(r, C_, s_, fixos_, L, maximos=None):
        chamadas.append((r, list(C_), s_, dict(fixos_), L, dict(maximos or {})))
        return cota(r, C_, s_, fixos_, L, maximos)

    monkeypatch.setattr(omega_k, "_cota_expoente_conhecido", spy)
    st = StatsK(k=len(sig))
    omega_k._certifica(C, s, lo, st, dict(fixos), {}, {}, None)
    assert tuple(sorted(sig.items())) in _found(st)
    assert st.cor6_ramos > 0
    chamadas = [(r, C_, s_, f, L, mx) for r, C_, s_, f, L, mx in chamadas
                if set(C_) <= set(sig) and s_ == len(sig) - len(C_)
                and all(sig[p] == a for p, a in f.items())
                and all(sig[p] <= M for p, M in mx.items())]
    if path == "expensive":
        assert any(r > omega_k.R_CHEAP_PROP9 for r, *_ in chamadas)
    elif path == "wieferich":
        assert pow(1733, 3, 7) == 1 and 1733 % 7 != 1               # odd order 3 modulo 7
        assert pow(1733, 6, 7**3) == 1 and pow(1733, 6, 7**4) != 1  # w_7(1733) = 3
        assert any(r == 7 and 1733 in C_ and 1733 not in f for r, C_, _, f, _, _ in chamadas)
    else:
        def capped(r, C_, s_, f, L, mx):
            A = cota(r, C_, s_, f, L, mx)
            return A is not None and A < cota(r, C_, s_, f, L, {q: M for q, M in mx.items()
                                                                 if q != 29})
        assert any(r == 7 and 29 not in f and 29 in mx and capped(r, C_, s_, f, L, mx)
                   for r, C_, s_, f, L, mx in chamadas)


def test_finite_exponent_bound_kills_exactly_below_the_bound(alvo):
    # The kill A_r < min_r of the finite exponent bound (no friend lies on it): target
    # I(5^2 5003^2 5009^2 5011^2) at C = {5, 5003}, s = 2. The bound on a_5003 is A = 10;
    # a minimum A leaves the single branch a = A, a minimum A + 2 kills the case.
    # (A == 10 is a pinned value, like the frozen counts: a sharper but still valid bound
    # also fails here. The branch checks below are statements about the bound.)
    sig = {5: 2, 5003: 2, 5009: 2, 5011: 2}
    alvo(_I(sig))
    C = [5, 5003]
    ramos = omega_k._ramos_cor6(C, 2, 5003, {5: 2}, {}, {}, None)
    A = max(f[5003] for f, _, _ in ramos)
    assert A == 10 and sorted(f[5003] for f, _, _ in ramos) == list(range(2, A + 1, 2))
    assert [f for f, _, _ in omega_k._ramos_cor6(C, 2, 5003, {5: 2}, {5003: A}, {}, None)] == \
        [{5: 2, 5003: A}]
    assert omega_k._ramos_cor6(C, 2, 5003, {5: 2}, {5003: A + 2}, {}, None) == []
    st = StatsK(k=4)
    omega_k._certifica(C, 2, 5003, st, {5: 2}, {5003: A + 2}, {}, None)
    assert st.cor6_mortos == 1 and st.amigos == []


def test_signature_test_of_a_complete_set_applies_the_v3_budget(alvo):
    # target I(5^2 7^2 13^2): V3 = v3(num) = 2, carried by 7^2 and 13^2 (v3(3) = 1 each).
    # 13^8 overshoots (1 + 2 > 2: cut inside the recursion), 13^4 undershoots (1 + 0 != 2:
    # rejected at the leaf), 13^2 is the friend; an empty list returns at once.
    sig = {5: 2, 7: 2, 13: 2}
    alvo(_I(sig))
    assert omega6._parametros_do_alvo()[1] == 2
    st = StatsK()
    omega6._conjunto_completo([5, 7, 13], st, listas=[[2], [2], [2, 4, 8]])
    assert st.amigos == [sig] and st.assinaturas_testadas == 2
    st = StatsK()
    omega6._conjunto_completo([5, 7, 13], st, listas=[[2], [2], [4, 8]])
    assert st.amigos == [] and st.assinaturas_testadas == 1
    st = StatsK()
    omega6._conjunto_completo([5, 7, 13], st, listas=[[2], [], [2]])
    assert st.amigos == [] and st.assinaturas_testadas == 0


def test_total_closure_lemma_is_not_applied_with_an_unfactored_residue(monkeypatch, alvo):
    # Phi_3(180676527253) contains 100003^2 * 17205109; with FATORA_BITS = 20 that part
    # stays an unfactored residue (two unknown primes, no pin). The lemma's precondition
    # (no residue) must stop it from firing: here den(x) contains 100003^2.
    sig = {5: 2, 100003: 2, 17205109: 2, 180676527253: 2}
    alvo(_I(sig))
    monkeypatch.setattr(omega_k, "FATORA_BITS", 20)
    for f in (omega_k._phi_valor, omega_k._classifica_cofator, omega_k._fatora,
              omega_k._divisao_pequena):
        f.cache_clear()
    try:
        st = StatsK(k=4)
        omega_k._certifica([5, 180676527253], 2, 5, st, {5: 2, 180676527253: 2}, {}, {}, None)
        assert tuple(sorted(sig.items())) in _found(st)
        assert st.fecho_total_mortos == 0
    finally:
        for f in (omega_k._phi_valor, omega_k._classifica_cofator, omega_k._fatora,
                  omega_k._divisao_pequena):
            f.cache_clear()


F3A = {5: 2, 100003: 2, 180676527253: 2}
F2A = {5: 2, 100003: 2, 131617: 2, 1530721: 2, 1792933: 2, 3307219: 2}


@pytest.mark.parametrize("sig,C,gates", [
    # Phi_3(180676527253) = 3 * 63241 * 17205109 * 100003^2 with 63241 and 17205109 primes of
    # num: the cofactor 100003^2 is a prime power, ONE unknown (the pin 100003)
    (F3A, [5, 180676527253], {}),
    # the same piece skipped by the degree gate, then by the size gate: no pin, and the
    # total-closure lemma must not fire (a piece was not examined; den(x) = 100003^2)
    (F3A, [5, 180676527253], {"GRAU_PHI_MAX": 1}),
    (F3A, [5, 180676527253], {"PIN_BITS": 30}),
    # Phi_3(1792933) = 3 * 7 * 100003 * 1530721 and Phi_3(3307219) = 3 * 277 * 100003 * 131617:
    # with FATORA_BITS = 20 both cofactors stay unfactored residues sharing the unknown
    # 100003; the coprime-base refinement reveals the pins 100003, 131617 and 1530721
    (F2A, [5, 1792933, 3307219], {"FATORA_BITS": 20}),
])
def test_closure_branches_that_no_real_run_reaches_keep_the_friend(
        sig, C, gates, monkeypatch, alvo):
    # branches that no 9/5 run decides by: a prime-power cofactor and a common factor of two
    # residues (none at k <= 9, results/PHASE_1.md 7.6), and the guard of the total-closure
    # lemma on skipped pieces (removing it changes no count of the k = 8 tree)
    assert 180676527253**2 + 180676527253 + 1 == 3 * 63241 * 17205109 * 100003**2
    assert 1792933**2 + 1792933 + 1 == 3 * 7 * 100003 * 1530721
    assert 3307219**2 + 3307219 + 1 == 3 * 277 * 100003 * 131617
    alvo(_I(sig))
    omega_k._alvo()  # the target is factored with the default gates
    caches = (omega_k._phi_valor, omega_k._classifica_cofator, omega_k._fatora,
              omega_k._divisao_pequena)
    for name, value in gates.items():
        monkeypatch.setattr(omega_k, name, value)
    for f in caches:
        f.cache_clear()
    try:
        st = _from_node(C, len(sig) - len(C), 5, {q: sig[q] for q in C})
        assert tuple(sorted(sig.items())) in _found(st)
        assert st.fecho_total_mortos == 0
    finally:
        for f in caches:
            f.cache_clear()


def test_node_of_the_large_prime_lemma_case_b1(alvo):
    # N0 = 5^2 q^4 r^2 with r = Phi_5(q) = sigma(q^4) a prime of 81 bits (r - 1 is not
    # factored): the exponent list of q comes from case (B1, prime) of the lemma
    q = 1058147
    r = (q**5 - 1) // (q - 1)
    assert (r - 1).bit_length() > omega_k.ORDEM_BITS and omega_k._pr.small_proved_prime(r)
    sig = {5: 2, q: 4, r: 2}
    alvo(_I(sig))
    # 5 is no odd order of q modulo 5 or the primes of num: a_q + 1 = 5 = ord_r(q) can only
    # come from the loop (B1, prime), bounded through A_r = 2 + v_r(num) - v_r(den) = 1
    assert 5 not in ordens_impares(q, frozenset({5, q}), omega_k._alvo()[0])
    for fixos in ({5: 2}, {}, {5: 2, q: 4}):
        st = StatsK(k=3)
        omega_k._certifica([5, q], 1, q, st, dict(fixos), {}, {}, None)
        assert tuple(sorted(sig.items())) in _found(st) and st.conjuntos_com_primo_grande >= 1


def test_known_refusal_one_unknown_with_both_budgets_zero(alvo):
    # A known refusal (results/FAILURES.md, Block 8): N0 = 5^2 q^4 r^2 with q = 1050367
    # = 1 (mod 3) and r = Phi_5(q) (81 bits, r = 2 mod 3). At C = {5, q}, s = 1 both budgets
    # are 0; the last-unknown solver needs L(C), and the prime 175061 of q - 1 has the free
    # q on its right-hand side, beyond the size gate, so the whole solver declines; the
    # finite exponent bound is not offered at s = 1, and the index interval of r is about
    # 10^24 wide. The node must be REFUSED, never lose the friend; with a_q fixed the
    # closure pins r and the friend is found.
    q = 1050367
    r = (q**5 - 1) // (q - 1)
    sig = {5: 2, q: 4, r: 2}
    alvo(_I(sig))
    with pytest.raises(NaoCertificavel, match="MAX_INDEX_SPAN"):
        omega_k._certifica([5, q], 1, q, StatsK(k=3), {5: 2}, {}, {}, None)
    st = StatsK(k=3)
    omega_k._certifica([5, q], 1, q, st, {5: 2, q: 4}, {}, {}, None)
    assert tuple(sorted(sig.items())) in _found(st)


def test_injective_feasibility_against_brute_force():
    from itertools import permutations
    from random import Random

    def brute(divs, pool):
        return any(all((p - 1) % d == 0 for d, p in zip(divs, perm))
                   for perm in permutations(pool, len(divs)))

    # three cases that need backtracking (the last two are real calls of the 9/5 trees)
    for divs, pool in (([3, 9], [5, 19, 31]), ([3, 5, 15], [3, 5, 7, 13, 19, 31, 30941]),
                       ([3, 5, 9, 15, 45], [3, 5, 7, 11, 13, 31, 181, 199])):
        assert omega_k._tem_atribuicao_injetiva(divs, pool) and brute(divs, pool)
    rng = Random(8)
    primes = [7, 11, 13, 19, 31, 37, 41, 61, 71, 73, 101, 109, 127, 151, 181, 191, 199, 211,
              241, 271, 331, 421, 541, 631, 661, 991, 1801, 2251]
    for _ in range(800):
        pool = rng.sample(primes, rng.randint(1, 6))
        divs = sorted(set(rng.choice([3, 5, 9, 15, 25, 45, 75]) for _ in range(rng.randint(1, 4))))
        assert omega_k._tem_atribuicao_injetiva(divs, pool) == brute(divs, pool), (divs, pool)


def test_cyclotomic_solver_respects_the_caps():
    # For Phi_ell(U0) = ell^eps * prod q^e_q, the solver must return U0 when every cap is at
    # least e_q, and must not when one cap is below its e_q.
    from sympy import factorint, primerange
    checked = 0
    for ell in (3, 5):
        for U0 in primerange(11, 400):
            R = omega_k._phi_primo(ell, U0)
            eps = 1 if U0 % ell == 1 else 0
            fac = {int(q): int(e) for q, e in factorint(R // ell**eps).items()}
            if ell in fac or any((q - 1) % ell for q in fac):
                continue
            C_ell = sorted(fac)
            C_set = set(C_ell) | {5}
            exact = dict(fac)
            assert U0 in omega_k._solucoes_phi(ell, eps, C_ell, R, exact, U0 - 1, C_set)
            above = {q: e + 1 for q, e in fac.items()}
            assert U0 in omega_k._solucoes_phi(ell, eps, C_ell, R, above, U0 - 1, C_set)
            for q in C_ell:
                below = {**exact, q: exact[q] - 1}
                assert U0 not in omega_k._solucoes_phi(ell, eps, C_ell, R, below, U0 - 1, C_set)
            checked += 1
    assert checked > 50


# ---------------------------------------------------------------------------
# Refusals and the 9/5 regression
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("t", [Fraction(2), Fraction(3, 2), Fraction(10, 3), Fraction(7, 9),
                               Fraction(1), Fraction(5, 7),
                               Fraction(5, 3)])     # refused only by 3 | den
def test_inadmissible_targets_are_refused_at_the_root(t, alvo):
    alvo(t)
    with pytest.raises(NaoCertificavel):
        certifica_omega(3)


def test_target_with_a_large_prime_in_num_is_refused(alvo):
    big = int(nextprime(2**90))
    alvo(Fraction(big, 5))
    with pytest.raises(NaoCertificavel):
        certifica_omega(3)


def test_negative_budget_gives_no_case():
    assert omega_k._casos_ell([5, 11, 31], 1, 31, 5, -1, {5: 2}) == []


def test_generic_code_reproduces_the_9_5_tree_at_k_8():
    assert omega6.ALVO == Fraction(9, 5)
    st = certifica_omega(8, light=True)
    got = {f: getattr(st, f) for f in (
        "nos", "mortos_min", "ramo_i", "particoes", "ramos_expoente", "caudas",
        "conjuntos_completos", "completos_mortos_indice", "conjuntos_com_primo_grande",
        "casos_sem_fecho", "ultimos_resolvidos", "candidatos_ultimo", "cor6_ramos",
        "cor6_mortos", "fecho_total_mortos", "splits", "dead_hi", "assinaturas_testadas",
        "n_pins")}
    assert got == {"nos": 18390, "mortos_min": 243, "ramo_i": 357, "particoes": 5970,
                   "ramos_expoente": 311, "caudas": 311, "conjuntos_completos": 3642,
                   "completos_mortos_indice": 8327, "conjuntos_com_primo_grande": 0,
                   "casos_sem_fecho": 338, "ultimos_resolvidos": 487, "candidatos_ultimo": 37,
                   "cor6_ramos": 17, "cor6_mortos": 0, "fecho_total_mortos": 0, "splits": 20,
                   "dead_hi": 208, "assinaturas_testadas": 0, "n_pins": 14348}
    assert st.amigos == []


def test_9_5_parameters_are_those_of_the_earlier_blocks():
    assert omega6.ALVO == Fraction(9, 5)
    extras, fnum, fden = omega_k._alvo()
    assert extras == {3} and dict(fnum) == {3: 2} and dict(fden) == {5: 1}
    assert omega_k._orcamento5(10) == 9 and omega_k._orcamento3() == 2
    for c5 in range(4):
        for s in range(1, 6):
            C = [5] + [11, 31, 41][:c5]
            a1_max = 1 + (c5 + s) * (c5 + s - 1)
            assert omega_k._faixa_a1(C, s) == (2, a1_max - a1_max % 2)
