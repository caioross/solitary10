"""Mutation check of the planted-friend tests (Phase 1, Block 8).

Each mutant is a small deliberate defect in core/omega_k.py (or, for the verifier of
primality certificates, in core/primality.py): a 9/5-only form left in the generic
partition, an off-by-one in a budget or a bound, a witness searched in the wrong pool, a
dropped case, a missing check. For each mutant the script copies the repository code to a
temporary directory, applies the mutation there (the repository is never modified), runs
the corresponding test file against the mutated copy (tests/test_planted.py, or
tests/test_primality.py for the verifier), and reports whether a test failed on an
assertion or on an expected exception that was not raised ("killed"), or none did
("SURVIVED"). A run that times out, fails without a failed test (an import error, a
crash), fails with another exception in a test, or fails on an AssertionError raised
outside tests/ (an internal check of core/ tripped by the mutant) proves nothing: it is
reported as INCONCLUSIVE and makes the exit status 1. A control run without mutation
must pass.

A mutant that survives is either a defect the tests cannot see (listed in KNOWN_BLIND with
the reason, and reported as such) or not a soundness defect at all (EXPECTED_SURVIVORS; an
exact-value test may still kill such a mutant, and the entry then records why that kill
is not a soundness defect).
One test, test_generic_code_reproduces_the_9_5_tree_at_k_8, compares frozen node counts:
it detects any change of the 9/5 tree, harmful or not. --no-frozen deselects it. The
remaining tests still include exact-value checks (the lower end of the range of a1, the
9/5 parameters, the finite exponent bound evaluated with every prime known and at one
node with two unknowns), refusal tests and the path checks of the end-to-end runs, so a
kill under --no-frozen is not by itself a lost planted friend: a1min_2, which only
loosens a bound, is killed by the exact lower end of the range of a1, cor6_pool_C and
cor6_wild_known by the value of the bound at s = 0, and cor6_wild_unknown and
cor6_drop_top (EXPECTED_SURVIVORS) by its value A = 10 at s = 2 in
tests/test_planted.py::test_finite_exponent_bound_kills_exactly_below_the_bound.

Usage:
  python experiments/planted_mutations.py              # all mutants, 6 in parallel
  python experiments/planted_mutations.py --jobs 1 --only T5_old,witfecha
  python experiments/planted_mutations.py --list
  python experiments/planted_mutations.py --no-frozen --slow   # without the frozen 9/5 counts
  python experiments/planted_mutations.py --sweep default      # judge by planted_sweep.py
With --sweep a mutant is killed only by what planted_sweep.py reports (a planted friend
LOST end to end, a BADFRIEND, or a friend MASKED: dropped by a node on its own path while
another path still finds it): one that only a statement-level test of
tests/test_planted.py detects (cor6_pool_C, for one, loses no planted friend) survives
there, and the exit status is then 1.
Exit status 0 iff the controls pass, every mutant matches the code exactly once, no run
is inconclusive, and every mutant outside EXPECTED_SURVIVORS and KNOWN_BLIND is killed.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = "core/omega_k.py"

# (name, what it breaks, old text, new text); `old` must occur exactly once in TARGET
MUTANTS: list[tuple[str, str, str, str]] = [
    # --- the 9/5-only forms that Block 8 replaced ------------------------------------
    ("extras_3", "extras = {3} everywhere, whatever the target",
     "    return frozenset(fnum), MappingProxyType(fnum), MappingProxyType(fden)",
     "    return frozenset({3}), MappingProxyType(fnum), MappingProxyType(fden)"),
    ("perm_particao", "closures of the partition modulo C + {3}",
     "    stats.particoes += 1\n    permitidos = set(C) | extras",
     "    stats.particoes += 1\n    permitidos = set(C) | {3}"),
    ("perm_casos", "feeder closures modulo C + {3}",
     "    permitidos = set(C) | extras\n    pool = sorted(permitidos)",
     "    permitidos = set(C) | {3}\n    pool = sorted(set(C) | extras)"),
    ("wit", "witnesses of budget levels searched in C only (cap and closure)",
     "    pool = sorted(permitidos)\n",
     "    pool = sorted(set(C))\n"),
    ("witcap", "per-feeder cap with witnesses in C only",
     "            if not testemunha(q, k + 1):",
     "            if not any(_ordem_e_potencia(q, r, ell, k + 1) for r in C if r != q):"),
    ("witfecha", "closure of a budget assignment with witnesses in C only",
     "            faltam = [j for j in range(1, k + 1) if not testemunha(q, j)]",
     "            faltam = [j for j in range(1, k + 1)\n"
     "                      if not any(_ordem_e_potencia(q, r, ell, j) for r in C if r != q)]"),
    ("kmax1", "one witness-less level fewer allowed per feeder",
     "                if faltando == s:",
     "                if faltando == s - 1:"),
    ("T5_old", "5-budget a1 - 1 (the 9/5 value)",
     "    return a1 + fnum.get(5, 0) - fden.get(5, 0)",
     "    return a1 - 1"),
    ("T5_plus1", "5-budget off by one",
     "    return a1 + fnum.get(5, 0) - fden.get(5, 0)",
     "    return a1 + fnum.get(5, 0) - fden.get(5, 0) + 1"),
    ("T5_no_v5num", "5-budget forgets v5(num)",
     "    return a1 + fnum.get(5, 0) - fden.get(5, 0)",
     "    return a1 - fden.get(5, 0)"),
    ("T3_old", "3-budget 2 (the 9/5 value)",
     "    return _alvo()[1].get(3, 0)",
     "    return 2"),
    ("T3_plus1", "3-budget off by one",
     "    return _alvo()[1].get(3, 0)",
     "    return _alvo()[1].get(3, 0) + 1"),
    ("a1max_old", "range of a1: the 9/5 bound 1 + (c5 + s)(c5 + s - 1)",
     "    a1_max = (c5 + s) * (c5 + s - 1 + e5) + shift",
     "    a1_max = 1 + (c5 + s) * (c5 + s - 1)"),
    ("a1max_no_e5", "range of a1 without the extras = 1 mod 5",
     "    a1_max = (c5 + s) * (c5 + s - 1 + e5) + shift",
     "    a1_max = (c5 + s) * (c5 + s - 1) + shift"),
    ("a1max_shift1", "range of a1 with the 9/5 shift 1",
     "    a1_max = (c5 + s) * (c5 + s - 1 + e5) + shift",
     "    a1_max = (c5 + s) * (c5 + s - 1 + e5) + 1"),
    ("a1max_minus2", "range of a1 two below the bound",
     "    a1_max = (c5 + s) * (c5 + s - 1 + e5) + shift",
     "    a1_max = (c5 + s) * (c5 + s - 1 + e5) + shift - 2"),
    ("a1min_2", "range of a1 starts at 2 (not a soundness defect)",
     "    a1_min = max(2, shift)",
     "    a1_min = 2"),
    ("closure_old", "total-closure lemma in its 9/5 form, den(x) != 1",
     "    for p in sorted((extras | set(fden)) - set(C)):",
     "    for p in []:"),
    ("closure_s", "total-closure lemma allows s - 1 primes only",
     "    return d != 1 or usados > s",
     "    return d != 1 or usados >= s"),
    ("closure_den", "total-closure lemma strips the primes of den only",
     "    for p in sorted((extras | set(fden)) - set(C)):",
     "    for p in sorted(set(fden) - set(C)):"),
    ("m0_pool", "injective feasibility into C only",
     "    return _tem_atribuicao_injetiva(divs, sorted(set(C) | _alvo()[0]))",
     "    return _tem_atribuicao_injetiva(divs, C)"),
    ("Cell", "last unknown: right-hand side over C only",
     "        C_ell = [q for q in pool if (q - 1) % ell == 0]",
     "        C_ell = [q for q in C if (q - 1) % ell == 0]"),
    ("caps_old", "last unknown: e_q <= a_q (the 9/5 cap)",
     "    caps = {q: fixos[q] + fnum.get(q, 0) - fden.get(q, 0) for q in C if q in fixos}",
     "    caps = {q: fixos[q] for q in C if q in fixos}"),
    ("caps_minus1", "last unknown: cap one below",
     "    caps = {q: fixos[q] + fnum.get(q, 0) - fden.get(q, 0) for q in C if q in fixos}",
     "    caps = {q: fixos[q] + fnum.get(q, 0) - fden.get(q, 0) - 1 for q in C if q in fixos}"),
    ("extcap_minus1", "last unknown: cap of an extra one below",
     "    caps.update({e: fnum[e] for e in extras if e not in C_set})",
     "    caps.update({e: fnum[e] - 1 for e in extras if e not in C_set})"),
    ("L_pool", "last unknown: L over C only",
     "    pool = sorted(set(C) | _alvo()[0])\n    if _grandes(pool):",
     "    pool = sorted(set(C))\n    if _grandes(pool):"),
    ("eps_pool", "last unknown: eps = 1 only for ell in C",
     "            epss = [0, 1] if (ell in C_set or ell in extras) else [0]",
     "            epss = [0, 1] if ell in C_set else [0]"),
    ("eps_forced0", "last unknown: eps = 0 for the ell forced by the budgets",
     "        r = resolve(5, [1])",
     "        r = resolve(5, [0])"),
    ("root_degree", "last unknown: root of degree ell instead of ell - 1",
     "            u = int(integer_nthroot(R, ell - 1)[0])",
     "            u = int(integer_nthroot(R, ell)[0])"),
    ("umax_minus1", "last unknown: index bound one below",
     "    U_max = _cota_indice_U(prod_sup)\n    if hi is not None:\n        U_max = hi if U_max",
     "    U_max = _cota_indice_U(prod_sup)\n    U_max = None if U_max is None else U_max - 1\n"
     "    if hi is not None:\n        U_max = hi if U_max"),
    # --- earlier blocks, now reachable by planted friends -----------------------------
    ("tail_gap", "tails: exact branches and tail skip every other exponent",
     "            exatos.append(a)                         # termina: fator·I(q^a) -> acc > ALVO\n"
     "            a += 2",
     "            exatos.append(a)                         # termina: fator·I(q^a) -> acc > ALVO\n"
     "            a += 4"),
    ("cor6_wild_unknown", "Cor. 6: one wildcard fewer for the unknowns",
     "        total += s * (om + _nivel_max(W, s - 1))",
     "        total += s * (om + _nivel_max(W, s - 2))"),
    ("cor6_wild_known", "Cor. 6: one wildcard fewer for a known feeder",
     "            niv = _nivel_max(Wq, s)",
     "            niv = _nivel_max(Wq, s - 1)"),
    ("virtual_big", "virtual factor slightly too large",
     "    return Fraction(hi * hi + hi + 1, hi * hi)",
     "    return Fraction(hi * hi + hi + 2, hi * hi)"),
    ("split_drop_a2", "split without the case U_1 = B",
     "        cases.append(((B,), B, None))",
     "        pass"),
    ("split_drop_b", "split without the case U_1 > B",
     "        cases.append(((), B, _INHERIT))",
     "        pass"),
    ("index_child_min", "index loop kills a child slightly too early",
     "        if s - 1 >= 1 and filho_min >= _o6.ALVO:",
     "        if s - 1 >= 1 and filho_min * Fraction(1001, 1000) >= _o6.ALVO:"),
    # --- proposed by the adversarial round of Block 8 ----------------------------------
    ("index_skip_extras", "index loop skips the primes of num (an extra may be a prime of N)",
     "        if q in fs:\n            continue\n        filho_sup = prod_sup * sup_pp(q)",
     "        if q in fs or q in _alvo()[0]:\n            continue\n"
     "        filho_sup = prod_sup * sup_pp(q)"),
    ("solver_excl_extras", "last unknown: an extra is never a candidate for U",
     "    C_set = set(C)\n    pool = sorted(C_set | extras)",
     "    C_set = set(C) | extras\n    pool = sorted(C_set)"),
    ("extcap_lo", "last unknown: cap 0 for the extras <= lo",
     "    caps.update({e: fnum[e] for e in extras if e not in C_set})",
     "    caps.update({e: (fnum[e] if e > lo else 0) for e in extras if e not in C_set})"),
    ("e5_lo", "range of a1: e5 counts only the extras above max(C)",
     "    e5 = sum(1 for e in extras if e not in C and e % 5 == 1)\n    a1_min = max(2, shift)",
     "    e5 = sum(1 for e in extras if e not in C and e % 5 == 1 and e > max(C))\n"
     "    a1_min = max(2, shift)"),
    ("split_hi_Bm2", "split: case (a) with hi = B - 2",
     "    cases: list[tuple[tuple[int, ...], int | None, object]] = [((), None, B - 1)]",
     "    cases: list[tuple[tuple[int, ...], int | None, object]] = [((), None, B - 2)]"),
    ("split_b_lo_B1", "split: case (b) with lo = B + 1",
     "        cases.append(((), B, _INHERIT))",
     "        cases.append(((), B + 1, _INHERIT))"),
    ("virtual_cube", "virtual factor v(hi) + 1/hi^3",
     "    return Fraction(hi * hi + hi + 1, hi * hi)",
     "    return Fraction(hi**3 + hi**2 + hi + 1, hi**3)"),
    ("cor6_pool_C", "Cor. 6: level witnesses in C only (the step of the printed proof)",
     "    pool = sorted(set(C) | set(extras))",
     "    pool = sorted(set(C))"),
    # --- proposed by the whole-code pass of Block 8 --------------------------------------
    ("hi_eq_kill", "virtual factor: kill also at equality with s = 1",
     "        if pv > _o6.ALVO or (s >= 2 and pv == _o6.ALVO):",
     "        if pv >= _o6.ALVO:"),
    ("max_strict_lists", "complete sets: an exponent equal to its upper bound is dropped",
     "(p not in maximos or a <= maximos[p])]",
     "(p not in maximos or a < maximos[p])]"),
    ("cor6_drop_top", "Cor. 6 branching: the exponent A_r itself is not branched",
     "    return [({**fixos, r: a}, minimos, novos_max) for a in range(amin, A + 1, 2)]",
     "    return [({**fixos, r: a}, minimos, novos_max) for a in range(amin, A, 2)]"),
    ("min_strict_lists", "complete sets: an exponent equal to its lower bound (minimos) is dropped",
     "minimos.get(p, 2) <= a and",
     "(minimos[p] < a if p in minimos else 2 <= a) and"),
    # s0_sup_eq is equivalent on every run from the root: the prime added last before s = 0
    # (a pin, the index prime, the split pin B, a solver candidate) is never a key of fixos
    # or maximos, so the clause "some free prime has no upper bound" always holds there;
    # only a node-level test can see it (test_nodes_with_upper_bounds_attained)
    ("s0_sup_eq", "complete sets: killed when prod_sup equals the target",
     "        if prod_min > _o6.ALVO or (prod_sup < _o6.ALVO) or (",
     "        if prod_min > _o6.ALVO or (prod_sup <= _o6.ALVO) or ("),
    ("cap_nivel_off", "Cor. 6: level cap from maximos one below when M + 1 is a power of r",
     "    while r ** (j + 1) <= M + 1:",
     "    while r ** (j + 1) <= M:"),
    ("cor6_kill_eq", "Cor. 6: the case is killed when the bound equals the minimum",
     "            if A < amin:",
     "            if A <= amin:"),
    ("inj_greedy", "injective feasibility without backtracking",
     "                usados.add(r)\n                if rec(i + 1):\n                    return True\n"
     "                usados.discard(r)",
     "                usados.add(r)\n                return rec(i + 1)"),
    ("eps_C", "last unknown: eps = 1 only for ell among the extras, not for ell in C",
     "            epss = [0, 1] if (ell in C_set or ell in extras) else [0]",
     "            epss = [0, 1] if ell in extras else [0]"),
    ("caps_route_eps", "last unknown: the bound of the capped right-hand side forgets ell^eps",
     "            R_max = ell ** max(epss)",
     "            R_max = 1"),
    ("closure_no_extra_guard", "total-closure lemma applied with an unfactored residue",
     "    if s >= 1 and extra_fixos == 0 and fecho_fixos_completo and all(q in fixos for q in C):",
     "    if s >= 1 and fecho_fixos_completo and all(q in fixos for q in C):"),
    ("closure_no_piece_guard", "total-closure lemma applied with a piece skipped by the gates",
     "    if s >= 1 and extra_fixos == 0 and fecho_fixos_completo and all(q in fixos for q in C):",
     "    if s >= 1 and extra_fixos == 0 and all(q in fixos for q in C):"),
    ("pp_none", "a prime-power cofactor r^e taken as composite (2 unknowns)",
     "    tipo, base = _classifica_cofator(c)\n    resto = 1\n",
     "    tipo, base = _classifica_cofator(c)\n"
     "    tipo = \"composto\" if tipo == \"potencia\" else tipo\n    resto = 1\n"),
    ("composite_3", "a composite cofactor counted as 3 unknown primes",
     "        if len(novos) + 2 > s:\n            return None",
     "        if len(novos) + 3 > s:\n            return None"),
    ("no_coprime_base", "residues of different closures counted 2 each, no coprime base",
     "    for e in _coprime_base(list(restos) + list(pins)):",
     "    for e in list(restos):"),
    ("coprime_base_3", "a composite element of the coprime base counted as 3 unknown primes",
     "        elif tipo == \"composto\":\n            extra += 2",
     "        elif tipo == \"composto\":\n            extra += 3"),
    ("phi_composite", "Phi_d(q) off by 2 for orders d > 39 with two distinct primes",
     "        val = int(cyclotomic_poly(d, q))",
     "        val = int(cyclotomic_poly(d, q)) + 2 * (d > 39)"),
    ("tail_skip_A", "tails: the tail starts at A + 2",
     "            ramos.append((fixos, {**minimos, q: a}, maximos))    # cauda a_q >= a",
     "            ramos.append((fixos, {**minimos, q: a + 2}, maximos))    # cauda a_q >= a"),
    # --- large-prime lemma (no 9/5 complete set of k <= 9 reaches it; planted R24 and
    # tests/test_planted.py::test_node_of_the_large_prime_lemma_case_b1 do) ------------
    ("lemma_dead", "large prime: the complete set dies as soon as r has an exponent",
     "    num, den = _o6.ALVO.numerator, _o6.ALVO.denominator\n    A_r = max(exps_r)",
     "    return None\n    num, den = _o6.ALVO.numerator, _o6.ALVO.denominator\n    A_r = max(exps_r)"),
    ("lemma_D_3", "large-prime lemma: order witnesses modulo S' + {3}, not S' + extras",
     "    D = ordens_impares(p, S_peq, extras)\n",
     "    D = ordens_impares(p, S_peq)\n"),
    ("lemma_fecha_3", "large-prime lemma: reconstruction modulo S + {3}, not S + extras",
     "if sigma_fecha_em(p, m - 1, fs, extras)]",
     "if sigma_fecha_em(p, m - 1, fs)]"),
    ("lemma_A_r_den", "large-prime lemma: A_r too small when r divides den",
     "    A_r = max(exps_r) + v_p(r, num) - v_p(r, den)",
     "    A_r = max(exps_r) + v_p(r, num) - 2 * v_p(r, den)"),
    ("bigprime_Ar_minus1", "large-prime lemma: A_r one below (case (B1, prime) loses ell)",
     "    A_r = max(exps_r) + v_p(r, num) - v_p(r, den)",
     "    A_r = max(exps_r) + v_p(r, num) - v_p(r, den) - 1"),
]

# mutants of the verifier of primality certificates, judged by tests/test_primality.py
VERIFIER_MUTANTS: list[tuple[str, str, str, str]] = [
    ("ver_final_O", "verifier: [q]Q = O not checked",
     "        return _ec_mul(q, Q, a, N) is None",
     "        _ec_mul(q, Q, a, N)\n        return True"),
    ("ver_Q_infinity", "verifier: [m/q]P = O accepted",
     "        if Q is None:\n            return False\n        return _ec_mul(q, Q, a, N) is None",
     "        return _ec_mul(q, Q, a, N) is None"),
    ("ver_size_bound", "verifier: no lower bound on q",
     "    if q < (r + 2) ** 2:\n        return False\n",
     ""),
    ("ver_size_weak", "verifier: q >= (floor(N^(1/4)) + 1)^2 only",
     "    if q < (r + 2) ** 2:",
     "    if q < (r + 1) ** 2:"),
    ("ver_disc", "verifier: singular curves accepted",
     "    if gcd(4 * a * a * a + 27 * b * b, N) != 1:\n        return False\n",
     ""),
    ("ver_den_gcd", "verifier: a denominator that is not invertible taken for O",
     "    if gcd(den, N) != 1:\n        raise _Composite\n",
     "    if gcd(den, N) != 1:\n        return None\n"),
    ("ver_inconsistent", "verifier: same x, y1 != +-y2 treated as a doubling",
     "        if y1 != y2:\n            raise _Composite\n",
     ""),
]
TARGET_OF = {name: ("core/primality.py", "tests/test_primality.py") for name, *_ in VERIFIER_MUTANTS}

EXPECTED_SURVIVORS: dict[str, str] = {
    "cor6_wild_unknown": "not a defect: with one wildcard fewer for the unknowns the finite "
                         "exponent bound is still valid (each unknown U has slack: either "
                         "U = 1 mod r and om >= 1 is unused, or ord_r(U) is odd and > 1 and "
                         "every level has two primitive witnesses); results/PHASE_1.md 8.3. "
                         "Killed only by a pinned value, like the frozen counts: at s = 2 it "
                         "gives A = 8, a sharper valid bound, not the A = 10 that "
                         "tests/test_planted.py::"
                         "test_finite_exponent_bound_kills_exactly_below_the_bound pins",
    "cor6_drop_top": "not a defect in practice: the finite exponent bound branches only at "
                     "s = 2 on live nodes, where every friend has a_r <= A_r - 2 (slack >= 2, "
                     "results/PHASE_1.md 8.3), so the value A_r itself never holds a friend; "
                     "detected by the frozen counts, by "
                     "tests/test_omega_k.py::test_cor6_no_quase_justo_de_k9_da_cotas_finitas "
                     "and, at statement level, by the branches of tests/test_planted.py::"
                     "test_finite_exponent_bound_kills_exactly_below_the_bound",
    "ver_disc": "not needed by the step theorem: if the curve is singular modulo p, the "
                "nonsingular points form a group of order p - 1, p or p + 1 <= (sqrt(p) + 1)^2 "
                "and the chord-tangent formulas never leave it, while a singular P is rejected "
                "by the arithmetic; the check is kept as hygiene",
}

KNOWN_BLIND: dict[str, str] = {
    # cor6_wild_known (one wildcard fewer for a known feeder) was listed here until the
    # planted friends 5^2 7^2 29^6 and 5^2 11^2 23^10 attained the bound at s = 0
    # (A_r = a_r = 2, the level witnessed by one prime of num): with s - 1 = -1 wildcards
    # the mutant demands two witnesses for that level and gives 1, so it is detected at
    # the statement level. One wildcard fewer at s >= 1 still loses no friend end to end:
    # the certifier branches on the bound only at s = 2, where every friend keeps slack
    # >= 2 (results/PHASE_1.md 8.3)
}


def _copy_tree(dest: Path) -> None:
    shutil.copytree(ROOT / "core", dest / "core",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (dest / "tests").mkdir()
    shutil.copy2(ROOT / "tests" / "test_planted.py", dest / "tests" / "test_planted.py")
    shutil.copy2(ROOT / "tests" / "test_primality.py", dest / "tests" / "test_primality.py")
    shutil.copytree(ROOT / "data", dest / "data")
    (dest / "experiments").mkdir()
    shutil.copy2(ROOT / "experiments" / "planted_sweep.py", dest / "experiments" / "planted_sweep.py")
    if (ROOT / "conftest.py").exists():
        shutil.copy2(ROOT / "conftest.py", dest / "conftest.py")


def _run(name: str, old: str | None, new: str | None, timeout: int,
         frozen: bool = True, slow: bool = False, sweep: str = "",
         target: str = TARGET, testfile: str = "tests/test_planted.py") -> tuple[str, str, float]:
    t0 = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="planted_mut_") as tmp:
        dest = Path(tmp)
        _copy_tree(dest)
        if old is not None:
            path = dest / target
            text = path.read_text(encoding="utf-8")
            if text.count(old) != 1:
                return name, f"BAD MUTANT ({text.count(old)} matches)", 0.0
            path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")
        # COLUMNS: pytest leaves the exception out of a FAILED line that does not fit the
        # terminal width (80 when the output is captured), and the verdict below reads it
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8",
                   COLUMNS="1000")
        env.pop("SOLITARY_SLOW", None)
        if slow:
            env["SOLITARY_SLOW"] = "1"
        cmd = [sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", testfile]
        if not frozen and testfile.endswith("test_planted.py"):
            cmd += ["-k", "not reproduces_the_9_5_tree"]
        if sweep and testfile.endswith("test_planted.py"):
            cmd = [sys.executable, "experiments/planted_sweep.py", "--preset", sweep, "--jobs", "3"]
        try:
            proc = subprocess.run(
                cmd,
                cwd=dest, env=env, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return name, "INCONCLUSIVE (timeout)", time.perf_counter() - t0
        failed = re.findall(r"^FAILED (\S+)(?: - (\w+))?", proc.stdout, re.M)
        # the file the failure was raised in: the last "path:line: ExceptionName" line of
        # the report (-x: one failure). An AssertionError raised outside tests/ is an
        # internal check of core/ tripped by the mutant, a crash like any other
        raised = re.findall(r"^(\S+?\.py):\d+: \w+$", proc.stdout, re.M)
        in_test = bool(raised) and raised[-1].replace("\\", "/").startswith("tests/")
        lost = re.findall(r"^  (LOST|BADFRIEND|MASKED): (.*?) nodes=", proc.stdout, re.M)
        if proc.returncode == 0:
            verdict = "passed"
        elif lost:
            verdict = f"killed: {len(lost)} planted friends lost or dropped, first {lost[0][1]}"
        elif failed and failed[0][1] in ("AssertionError", "assert", "Failed") and in_test:
            # an assert, or an expected exception not raised ("Failed: DID NOT RAISE")
            verdict = "killed by " + failed[0][0].split("::", 1)[1]
        elif failed:
            verdict = (f"INCONCLUSIVE ({failed[0][1]} raised in {raised[-1] if raised else '?'} "
                       f"in {failed[0][0].split('::', 1)[1]})")
        else:
            verdict = f"INCONCLUSIVE (exit {proc.returncode} without a failed test)"
        return name, verdict, time.perf_counter() - t0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", type=int, default=6, help="mutants run in parallel (default 6)")
    ap.add_argument("--only", default="", help="comma-separated mutant names")
    ap.add_argument("--timeout", type=int, default=900, help="seconds per run (default 900)")
    ap.add_argument("--list", action="store_true", help="list the mutants and exit")
    ap.add_argument("--no-frozen", action="store_true",
                    help="deselect the frozen-count test of the 9/5 tree")
    ap.add_argument("--slow", action="store_true", help="include the slow planted friends")
    ap.add_argument("--sweep", choices=["small", "default"], default="",
                    help="judge each mutant by experiments/planted_sweep.py instead of the tests")
    args = ap.parse_args()
    allm = MUTANTS + VERIFIER_MUTANTS
    if args.list:
        for name, what, _, _ in allm:
            print(f"{name:22s} {what}")
        return 0
    names = {m[0] for m in allm}
    wanted = [n for n in args.only.split(",") if n]
    unknown = [n for n in wanted if n not in names]
    if unknown:
        ap.error(f"unknown mutant(s): {', '.join(unknown)}")
    chosen = [m for m in allm if not wanted or m[0] in wanted]

    frozen = not args.no_frozen
    if args.sweep:
        print(f"judged by planted_sweep.py --preset {args.sweep}", flush=True)
    else:
        print(f"frozen-count test {'included' if frozen else 'deselected'}; slow tier "
              f"{'included' if args.slow else 'skipped'}", flush=True)
    testfiles = sorted({TARGET_OF.get(m[0], (TARGET, "tests/test_planted.py"))[1] for m in chosen})
    ok = True
    for tf in testfiles:
        name, verdict, secs = _run("(control)", None, None, args.timeout, frozen, args.slow,
                                   args.sweep, TARGET, tf)
        print(f"{name:22s} {verdict:70s} {secs:6.1f}s   [{tf}]", flush=True)
        ok = ok and verdict == "passed"

    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as ex:
        futs = [ex.submit(_run, n, old, new, args.timeout, frozen, args.slow, args.sweep,
                          *TARGET_OF.get(n, (TARGET, "tests/test_planted.py")))
                for n, _, old, new in chosen]
        results = [f.result() for f in futs]
    survivors, bad, inconclusive = [], [], []
    for (n, what, _, _), (_, verdict, secs) in zip(chosen, results):
        shown = verdict
        if verdict == "passed":
            shown = ("survived (known blind spot)" if n in KNOWN_BLIND else
                     "survived (expected)" if n in EXPECTED_SURVIVORS else "SURVIVED")
        print(f"{n:22s} {shown:70s} {secs:6.1f}s   [{what}]", flush=True)
        if verdict == "passed" and n not in EXPECTED_SURVIVORS and n not in KNOWN_BLIND:
            survivors.append(n)
        if verdict.startswith("BAD MUTANT"):
            bad.append(n)
        if verdict.startswith("INCONCLUSIVE"):
            inconclusive.append(n)
    killed = sum(1 for _, v, _ in results if v.startswith("killed"))
    print(f"\ncontrols: {'passed' if ok else 'FAILED'}; mutants: {len(chosen)}, killed {killed}, "
          f"survived {sum(1 for _, v, _ in results if v == 'passed')}"
          + (f" (unexpected: {', '.join(survivors)})" if survivors else "")
          + (f"; not matching the code: {', '.join(bad)}" if bad else "")
          + (f"; inconclusive: {', '.join(inconclusive)}" if inconclusive else ""))
    for n in KNOWN_BLIND:
        if any(n == m[0] for m in chosen):
            print(f"known blind spot {n}: {KNOWN_BLIND[n]}")
    return 0 if ok and not survivors and not bad and not inconclusive else 1


if __name__ == "__main__":
    sys.exit(main())
