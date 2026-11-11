"""Systematic sweep of planted friends through the recursive certifier (Phase 1, Block 8).

For every N0 = 5^{a1} * prod q^{a_q} of a grid (odd square, 5 its least prime, 3 not
dividing it), the target is t = I(N0) and certifica_omega(omega(N0)) is run with
core.omega6.ALVO = t. Outcomes:
  FOUND    N0 is among the friends found (and every friend found has I = t);
  LOST     the run finished without N0: a soundness defect (the exit status is 1);
  BADFRIEND a reported friend does not have I = t (also a defect);
  MASKED   N0 was found, but some node that contains it had no child that contains it
           (or, with no unknown left, did not report it): a false kill hidden by another
           path of the cover (also a defect);
  REFUSED  NaoCertificavel (no certificate either way);
  BUDGET   stopped after --max-nodes nodes (inconclusive).
The grid is deterministic; --stride n keeps every n-th signature of each family.

Usage:
  python experiments/planted_sweep.py                  # the default grid (a few minutes)
  python experiments/planted_sweep.py --preset small   # quick check
  python experiments/planted_sweep.py --jobs 8 --max-nodes 50000
"""
from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sympy import primerange  # noqa: E402

import core.omega6 as o6  # noqa: E402
import core.omega_k as ok  # noqa: E402
from core.motor import I_pp  # noqa: E402

# family: (k, largest free prime, exponents of the free primes, exponents of 5)
PRESETS = {
    "small": [(2, 200, (2, 4, 6), (2, 4, 6)), (3, 60, (2, 4), (2, 4)), (4, 30, (2,), (2, 4))],
    "default": [(2, 1000, (2, 4, 6), (2, 4, 6, 8, 10)), (3, 100, (2, 4), (2, 4, 6)),
                (4, 50, (2, 4), (2, 4)), (5, 40, (2,), (2, 4)), (6, 37, (2,), (2,))],
}


class _Budget(Exception):
    pass


def _I(sig: dict[int, int]) -> Fraction:
    x = Fraction(1)
    for p, a in sig.items():
        x *= I_pp(p, a)
    return x


def signatures(families, stride: int):
    for k, pmax, exps, exps5 in families:
        free = list(primerange(7, pmax + 1))
        n = 0
        for qs in combinations(free, k - 1):
            for a1 in exps5:
                for es in product(exps, repeat=k - 1):
                    if n % stride == 0:
                        yield {5: a1, **dict(zip(qs, es))}
                    n += 1


def _contains(sig, C, s, lo, fixos, minimos, maximos, hi) -> bool:
    """Does the node (C, s, lo, fixos, minimos, maximos, hi) contain N0 = sig? (as in
    tests/test_planted.py)"""
    S = set(sig)
    unk = S - set(C)
    return (set(C) <= S and s == len(unk)
            and all(sig.get(p) == a for p, a in fixos.items())
            and all(sig.get(p, a) >= a for p, a in minimos.items())
            and all(sig.get(p, a) <= a for p, a in maximos.items())
            and all(u > lo for u in unk)
            and (hi is None or (len(unk) > 0 and min(unk) <= hi)))


def run_one(args):
    sig, max_nodes = args
    t = _I(sig)
    o6.ALVO = t
    st = ok.StatsK(k=len(sig), light=True)
    real = ok._certifica
    key = tuple(sorted(sig.items()))
    stack, dropped = [], []

    def guarded(C, s, lo, stats, fixos=None, minimos=None, maximos=None, hi=None):
        if st.nos > max_nodes:
            raise _Budget()
        inside = _contains(sig, C, s, lo, fixos or {}, minimos or {}, maximos or {}, hi)
        if inside and stack:
            stack[-1][0] = True                 # the parent has a child that contains N0
        stack.append([False])
        before = len(stats.amigos)
        try:
            real(C, s, lo, stats, fixos, minimos, maximos, hi)
        finally:
            had_child = stack.pop()[0]
        if inside and (not had_child if s >= 1 else
                       key not in {tuple(sorted(a.items())) for a in stats.amigos[before:]}):
            dropped.append((list(C), s, lo))

    ok._certifica = guarded
    t0 = time.perf_counter()
    try:
        ok.certifica_omega(len(sig), st, light=True)
        found = {tuple(sorted(a.items())) for a in st.amigos}
        if not all(_I(a) == t for a in st.amigos):
            status = "BADFRIEND"
        elif key not in found:
            status = "LOST"
        elif dropped:
            status = "MASKED"
        else:
            status = "FOUND"
    except _Budget:
        status = "BUDGET"
    except o6.NaoCertificavel:
        status = "REFUSED"
    finally:
        ok._certifica = real
        o6.ALVO = Fraction(9, 5)
    used = {"partition": st.particoes > 0, "pins": st.n_pins > 0,
            "solver": st.ultimos_resolvidos > 0, "tails": st.caudas > 0,
            "cor6": st.cor6_ramos > 0, "split": st.splits > 0}
    return sig, status, st.nos, time.perf_counter() - t0, used


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preset", choices=sorted(PRESETS), default="default")
    ap.add_argument("--stride", type=int, default=1, help="keep every n-th signature (default 1)")
    ap.add_argument("--max-nodes", type=int, default=20000, help="node budget per run (default 20000)")
    ap.add_argument("--jobs", type=int, default=4, help="worker processes (default 4)")
    args = ap.parse_args()

    sigs = list(signatures(PRESETS[args.preset], args.stride))
    print(f"preset={args.preset} stride={args.stride} max_nodes={args.max_nodes}: "
          f"{len(sigs)} planted friends", flush=True)
    t0 = time.perf_counter()
    counts: dict[str, int] = {}
    used_tot: dict[str, int] = {}
    by_k: dict[int, dict[str, int]] = {}
    bad = []
    with ProcessPoolExecutor(max_workers=max(1, args.jobs)) as ex:
        for sig, status, nos, secs, used in ex.map(run_one, [(s, args.max_nodes) for s in sigs],
                                                   chunksize=8):
            counts[status] = counts.get(status, 0) + 1
            by_k.setdefault(len(sig), {}).setdefault(status, 0)
            by_k[len(sig)][status] += 1
            if status == "FOUND":
                for f, v in used.items():
                    used_tot[f] = used_tot.get(f, 0) + int(v)
            if status in ("LOST", "BADFRIEND", "MASKED"):
                bad.append((sig, status))
                print(f"  {status}: {sig} nodes={nos}", flush=True)
    print(f"done in {time.perf_counter() - t0:.0f}s")
    for k in sorted(by_k):
        print(f"  k = {k}: " + ", ".join(f"{s} {n}" for s, n in sorted(by_k[k].items())))
    print("total: " + ", ".join(f"{s} {n}" for s, n in sorted(counts.items())))
    print("found runs whose tree used (anywhere, not necessarily on the path of N0): "
          + ", ".join(f"{f} {n}" for f, n in sorted(used_tot.items())))
    print("LOST, BADFRIEND or MASKED: " + (str(len(bad)) if bad else "none"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
