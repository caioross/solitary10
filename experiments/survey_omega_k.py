"""Survey of omega(N) = k by the recursive certifier: measures the open frontier, certifies NOTHING.

Runs core.omega_k.certifica_omega(k) at the target 9/5, but every NaoCertificavel raised by a
node is recorded and the run goes on with the next sibling, so that the refusals of a k that
does not close can be counted and their kind seen. A run that skips refused nodes is not a
certificate of anything; this script exists to measure the size of the obstruction of
results/PHASE_1.md §8.8 (Block 8: 47.5 million nodes in 4 hours at k = 10, six refusals, all
with s = 3 and a1 = 2).

Prints the first node of each value of a1, every refusal (node state and message), a heartbeat
with the current node every --beat seconds, and a summary by a1, by s and by kind of refusal.
Stops at --max-nodes nodes (deterministic) or after --seconds of wall-clock time, whichever
comes first.

Usage:
  python experiments/survey_omega_k.py --k 10 --seconds 14400     # the run of Block 8
  python experiments/survey_omega_k.py --k 10 --max-nodes 20000   # a few seconds
"""
from __future__ import annotations

import argparse
import sys
import threading
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import core.omega_k as ok  # noqa: E402


class _Stop(Exception):
    pass


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--k", type=int, default=10, help="number of distinct primes (default 10)")
    ap.add_argument("--seconds", type=float, default=4 * 3600, help="wall-clock limit (default 4 h)")
    ap.add_argument("--max-nodes", type=int, default=None, help="node limit (deterministic stop)")
    ap.add_argument("--beat", type=float, default=600, help="heartbeat period in seconds")
    args = ap.parse_args()

    t0 = time.perf_counter()
    original = ok._certifica
    st = ok.StatsK(k=args.k, light=True)
    first: dict = {}
    refusals: list = []
    current: dict = {"a1": None, "state": None}

    def surveyed(C, s, lo, stats, *rest):
        if time.perf_counter() - t0 > args.seconds or (args.max_nodes is not None and stats.nos >= args.max_nodes):
            raise _Stop()
        fixos = rest[0] if rest else {}
        a1 = (fixos or {}).get(5)
        current["a1"] = a1
        current["state"] = (list(C), s, lo, dict(fixos or {}))
        if a1 not in first:
            first[a1] = (time.perf_counter() - t0, stats.nos)
            print(f"a1={a1} first at {first[a1][0]:.0f}s, node {stats.nos}: C={C} s={s}", flush=True)
        try:
            return original(C, s, lo, stats, *rest)
        except ok.NaoCertificavel as e:          # recorded, and the survey goes on
            refusals.append((a1, s, len(C), str(e)))
            print(f"  REFUSAL #{len(refusals)} a1={a1} s={s} |C|={len(C)} at "
                  f"{time.perf_counter() - t0:.0f}s, node {stats.nos}: {str(e)[:240]}", flush=True)
            return None

    def beat():
        while True:
            time.sleep(args.beat)
            print(f"[{time.perf_counter() - t0:8.0f}s] nodes={st.nos} refusals={len(refusals)} "
                  f"a1={current['a1']} state={str(current['state'])[:220]}", flush=True)

    ok._certifica = surveyed                   # the recursion calls the module-level name
    threading.Thread(target=beat, daemon=True).start()
    status = "complete"
    try:
        ok.certifica_omega(args.k, st, light=True)
    except _Stop:
        status = "stopped at the limit"
    finally:
        ok._certifica = original
    print(f"SURVEY k={args.k} ({status}; NOT a certificate): nodes={st.nos} friends={len(st.amigos)} "
          f"refusals={len(refusals)} time={time.perf_counter() - t0:.0f}s", flush=True)
    print("refusals by a1:", dict(Counter(r[0] for r in refusals)))
    print("refusals by s:", dict(Counter(r[1] for r in refusals)))
    print("refusals by kind:", dict(Counter("index span" if "MAX_INDEX_SPAN" in r[3] else r[3][:40]
                                            for r in refusals)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
