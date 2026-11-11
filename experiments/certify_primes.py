"""Prove every primality claim of the recursive certifier above 2^64 (Phase 1, Block 8).

Runs certifica_omega(k) for k = 1..K at the target 9/5 with the ledger of primality claims
enabled (core.omega_k.enable_prime_ledger): every integer n >= 2^64 that the run asserts
to be prime is recorded. Each one is then proved exactly (core/primality.py):
  n < 3.317·10^24: trial division and 13 Miller-Rabin bases (a proof, Sorenson-Webster);
  n >= 3.317·10^24: an elliptic-curve certificate from the store
                    data/primality_certificates.json.gz, checked by verify_chain.
Below 2^64 sympy.isprime is itself a proof; a False answer of isprime is always right.

With --generate, missing certificates are produced by experiments/ecpp_generator.py
(untrusted: floating point inside), verified, and added to the store.

Usage:
  python experiments/certify_primes.py --k-max 9              # about 10 minutes
  python experiments/certify_primes.py --k-max 9 --generate   # first time: much longer
Exit status 0 iff the number of claims after each k <= 9 is the reference one
(EXPECTED_CLAIMS) and every recorded claim is proved.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from concurrent.futures.process import BrokenProcessPool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

from core import primality as pr  # noqa: E402

STORE = ROOT / "data" / "primality_certificates.json.gz"
CHECKPOINT_SECONDS = 300      # checkpoint rule of --generate: see main()

# Number of claims >= 2^64 recorded after k = 1, ..., 8 (cumulative, ledger enabled before
# the first k; tests/test_primality.py freezes the total, 10). A different count means a
# recording site was lost or added, and "every recorded claim is proved" would then not
# cover every claim. Extend the table only from a complete run of this script.
# k = 9: from a complete run on the code of the Block 8 commit (results/PHASE_1.md 8.5)
EXPECTED_CLAIMS = {1: 0, 2: 0, 3: 0, 4: 0, 5: 4, 6: 5, 7: 7, 8: 10, 9: 3890}


def _save(store: dict, meta: dict) -> None:
    """Write the store to a temporary file, then rename it over STORE: an interruption
    during the write leaves the previous store whole."""
    tmp = STORE.with_name(STORE.name + ".tmp")
    pr.save_store(tmp, store, meta)
    os.replace(tmp, STORE)


def _generate(n: int):
    import ecpp_generator as gen
    t0 = time.perf_counter()
    chain = gen.certify(n)
    ok = chain is not None and pr.verify_chain(n, chain)
    return n, (chain if ok else None), time.perf_counter() - t0


def _verify(item):
    n, chain = item
    return n, pr.verify_chain(n, chain)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--k-max", type=int, default=9)
    ap.add_argument("--generate", action="store_true", help="produce missing certificates")
    ap.add_argument("--jobs", type=int, default=8,
                    help="worker processes (default 8); 1 verifies in this process")
    args = ap.parse_args()

    import core.omega6 as o6
    import core.omega_k as ok
    from fractions import Fraction
    assert o6.ALVO == Fraction(9, 5)
    ledger = ok.enable_prime_ledger()
    t0 = time.perf_counter()
    count_changed = []
    for k in range(1, args.k_max + 1):
        st = ok.certifica_omega(k, light=True)
        ref = EXPECTED_CLAIMS.get(k)
        if ref is not None and len(ledger) != ref:
            count_changed.append(k)
        print(f"k = {k}: {st.nos} nodes, {len(st.amigos)} friends, claims >= 2^64 so far "
              f"{len(ledger)}" + ("" if ref is None else f" (reference {ref})")
              + f", {time.perf_counter() - t0:.0f}s", flush=True)
    if count_changed:
        print(f"LEDGER COUNT CHANGED at k = {count_changed}: a recording site was lost or "
              "added; NOT ALL CLAIMS PROVED")
        return 1
    claims = sorted(ledger)
    if args.k_max >= 5 and not claims:
        print("NO PRIMALITY CLAIM WAS RECORDED (k >= 5 always makes some): the ledger is broken")
        return 1
    small = [n for n in claims if n < pr.MR_LIMIT]
    large = [n for n in claims if n >= pr.MR_LIMIT]
    small_bad = [n for n in small if not pr.small_proved_prime(n)]
    print(f"claims >= 2^64: {len(claims)}; below 3.317e24: {len(small)} "
          f"(proved {len(small) - len(small_bad)}); above: {len(large)}, "
          f"largest {max((n.bit_length() for n in claims), default=0)} bits", flush=True)

    store = pr.load_store(STORE)
    missing = [n for n in large if n not in store]
    if missing and args.generate:
        print(f"generating {len(missing)} certificates ...", flush=True)
        meta = {"produced_by": "experiments/certify_primes.py --generate",
                "k_max": args.k_max, "claims_above_limit": len(large),
                "generator": "experiments/ecpp_generator.certify (deterministic: seeded "
                             "from n, fixed SCHEDULE); every chain checked by verify_chain"}
        made = unsaved = 0
        last_save = time.perf_counter()
        # completion order (as_completed), so that one slow claim does not hold the later
        # chains out of a checkpoint. The store is saved when a chain that took
        # CHECKPOINT_SECONDS or more completes, when any chain completes CHECKPOINT_SECONDS
        # or more after the last save, and on the way out (Ctrl-C, a dead worker); a rerun
        # resumes from it through `missing`
        with ProcessPoolExecutor(max_workers=args.jobs) as ex:
            futures = [ex.submit(_generate, n) for n in sorted(missing, key=int.bit_length)]
            try:
                for fut in as_completed(futures):
                    n, chain, secs = fut.result()
                    if chain is not None:
                        store[n] = chain
                        made += 1
                        unsaved += 1
                    else:
                        print(f"  no certificate for a {n.bit_length()}-bit claim ({secs:.0f}s)", flush=True)
                    if unsaved and (secs >= CHECKPOINT_SECONDS
                                    or time.perf_counter() - last_save >= CHECKPOINT_SECONDS):
                        _save(store, meta)
                        unsaved, last_save = 0, time.perf_counter()
            finally:
                for fut in futures:
                    fut.cancel()
                if unsaved:
                    _save(store, meta)
        print(f"  {made} generated; store has {len(store)} certificates", flush=True)

    t1 = time.perf_counter()
    todo = [(n, store[n]) for n in large if n in store]
    if args.jobs <= 1:
        verdicts = dict(map(_verify, todo))      # in this process: no worker can be lost
    else:
        try:
            with ProcessPoolExecutor(max_workers=args.jobs) as ex:
                verdicts = dict(ex.map(_verify, todo, chunksize=16))
        except BrokenProcessPool:
            # a worker died (on a loaded machine): verify_chain is pure integer
            # arithmetic, so the same verdicts are computed here, one after another
            print("the worker pool broke; verifying in this process", flush=True)
            verdicts = dict(map(_verify, todo))
    unproved = [n for n in large if not verdicts.get(n, False)]
    print(f"verified {len(todo)} certificates in {time.perf_counter() - t1:.0f}s; "
          f"unproved claims above 3.317e24: {len(unproved)}"
          + (f" (largest {max(n.bit_length() for n in unproved)} bits)" if unproved else ""))
    ok_all = not small_bad and not unproved
    print("ALL PRIMALITY CLAIMS >= 2^64 PROVED" if ok_all else "NOT ALL CLAIMS PROVED")
    if ok_all and args.k_max > max(EXPECTED_CLAIMS):
        print(f"(the number of claims, {len(claims)}, is checked against the reference only "
              f"up to k = {max(EXPECTED_CLAIMS)})")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
