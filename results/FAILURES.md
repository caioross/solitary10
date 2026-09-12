# FAILURES — abandoned lines of attack and dead ends

Rigour rule #6 (`docs/METHODOLOGY.md`): every abandoned line of attack goes here with
the precise reason for the failure. Failures are data.

Entry format:

```
## [date] Short title of the line of attack
- **What was tried:**
- **Why it failed (precise reason):**
- **What to keep:**
```

---

## [2026-09-12] Phase 1, Block 6 — Wieferich bound on the unknowns with an unsafe bound L

- **What was tried:** Thackeray's Cor. 6 + Prop. 9 to bound the exponent of the
  known primes at the almost-tight nodes (PHASE_1.md §6). The Wieferich term of the
  unknowns needs a bound L on ALL of them; I derived it level by level from the index
  (R′ − 1 ≥ 1/(b·U) via the reduced denominator of R − 1).
- **Why it failed (precise reason):** the recursion assumes R′ > 1 in the child, which
  only holds for U₁ > B_min = 1 + 1/(R − 1); the children with U₁ ≤ B_min have
  prod_sup ≥ 9/5 and no index bound for the remaining unknowns. The test comparing the
  bound with the real index loop in the child failed at 738 786 089 > L = 738 786 049.
  An earlier version (raw denominator, without the σ(q^{a_q}) of the fixed primes) was
  also unsafe; the "exact" version was far too loose after a large fixed exponent
  (k = 8: 18 s → > 10 min). In its sound form (s ≤ 2 and lo ≥ B_min) the bound never
  fires for k ≤ 8 — the gain seen before (90 032 → 69 644 nodes) was an artefact of the
  unsafe bound.
- **What to keep:** Prop. 9 and Cor. 6 are correct and tested; `maximos` and the
  total-closure lemma stay in the code. The lesson: a bound on "all the unknowns" has
  to hold in EVERY branch, and the test against the real index loop is mandatory for
  any new bound. The way forward (Block 7, PHASE_1.md §6.3): split the node into
  "smallest unknown ≤ B′" (a virtual factor I(B′²) in prod_min makes the tails die
  without enumeration) and "all > B′" (where Cor. 6 holds).

## [2026-09-10] Phase 1, Block 5 — almost-tight nodes with s = 2 (current dead end for ω = 9)

- **What was tried:** closing k = 9 with the recursive certifier after eliminating the
  index enumeration at the nodes with s = 1 (cyclotomic equations for the last unknown,
  PHASE_1.md §5.1).
- **Why it failed (precise reason):** the node C = {5,7,11,13,31,97,52361}, a₁ = 2, has
  ∏sup = 9/5 − 1.76·10⁻⁸ with **two** unknowns; the index bounds only the smaller one,
  U₁ < 1.03·10⁸ (≈ 5.9 million primes with U₂ > U₁, ~11 million in the loop), and each
  child, although solved in ~1 ms, is a node. The equation Φ_ℓ(U₁) = ℓ^ε·K·U₂^f does
  not close with f ≥ 1 (U₂ unbounded) nor with free exponents in C_ℓ. It is the same
  regime in which Thackeray spent 25 h of CPU (Proposition 3 + DFS).
- **What to keep:** the s = 1 solver is definitive and cheap; what is missing for
  s = 2 are bounds on v_U(q^{ord_U(q)} − 1) (Thackeray's Corollary 6 with c bounded by
  Proposition 9 — generalised Wieferich by finite computation), or a global bookkeeping
  of v_r. Brute alternative: let k = 9 run for hours (the enumeration is finite and honest).
- **Outcome (same day):** 12 h of brute force were not enough (196 M nodes, still in
  the same family; estimate: days). The lower bound B_low = 1/((9/5)/prod_min − 1)
  with tails is not enough either: the interval for the next prime tends to
  [1/(r−1), s/(r−1)] — an inherent width of a factor s (PHASE_1.md §5.4, addendum).
  What is missing is the FINITE exponent bound for known primes (Thackeray's Cor. 6 +
  Prop. 9), which turns tails into exact branches with pins — candidate Block 6.

## [2026-09-08] Phase 1, Block 3 — ω = 7 by the budget partition (honest wall)

- **What was tried:** certifying ω(N) ≥ 8 with the recursive certifier
  (`core/omega_k.py`): complete case partition by the exact budgets
  v₅(σ(N)) = a₁−1 and v₃(σ(N)) = 2 (universal bound a₁ ≤ 1 + (c₅+s)(c₅+s−1); pins by
  the new factors of Φ_{ℓʲ}(q); product of cases; injective feasibility of the
  witnesses of the last unknown), with the index as fallback.
- **Why it failed (precise reason):** the state {5,7,11,13,31,331}+P (a₁ = 2, 331 from
  Φ₃(31)) stays open: P carries the 5 and one of the 3's (15 | a_P+1, and 331 ≡ 1 mod 15
  is a legitimate witness), a_P = 14 is forced, and ∏sup = 1.8012 ≥ 9/5 takes the index
  out of play. Closing it requires v_P(N) = 14 = Σ_q v_P(q^{ord_P(q)} − 1) over ≤ 6
  feeders — valuation bookkeeping of the unknown (Thackeray, Cor. 6 / Prop. 9), which
  the two budgets do not capture. The first architecture (index first) also fell along
  the way: combinatorial explosion in {5,7,11,13,29} with 2 slots (> 590 s).
- **What to keep:** everything that worked stayed in the repo and is reusable — the
  universal bound for a₁, the partition by 3, the pin by the non-primitive factors of
  Φ_{ℓʲ}(q), and the injective matching (which is the closure argument of Block 1
  applied to the unknown prime). k ≤ 6 went from 2 745 complete sets to 27. Block 4
  should add the v_P budget.
- **Outcome (2026-09-10, Block 4):** the diagnosis "the v_P budget is missing" was
  wrong — the wall was a TIGHTENING DEFECT, not new mathematics: the a₁ = 2 committed
  in the branch was not entering the index bounds. With I(5^{a₁}) in place of 5/4,
  ∏sup{5,7,11,13,31,331} drops from 1.8012 to 1.7868 < 9/5 and the index bounds P. No
  v_P bookkeeping was needed for ω = 7. Lesson: before asking for new theory, check
  that every piece of information already committed in the branch enters ALL the
  prunings (see PHASE_1.md, Block 4). The same lesson struck twice more in Block 4: the
  universal bound a₁ ≤ 1 + (c₅+s)(c₅+s−1) was not re-checked with a₁ already fixed
  (the a₁ = 40 branch of k = 8 exploded to > 3·10⁶ nodes; in {5,7} the bound gives
  a₁ ≤ 31), and a factorisation outside the budget discarded pins already identified
  (correct information is never discarded: PHASE_1.md §4.6).

## [2026-08-21] Phase 1, Block 2 — exponent ladders with window kills (abandoned)

- **What was tried:** for the branch of the ω = 6 certifier not bounded by the index
  (prefix with ∏ p/(p−1) ≥ 9/5), enumerate exponents of the 5 known primes with
  "ladders" (a+1 = ord_P(p), an infinite family) killed by two index kills
  (K1: x ≤ 1 forever; K2: window x < 1 + 1/(2m) impossible forever) and exact
  extraction of the 6th prime from the denominator of x = (9/5)/∏I.
- **Why it failed (precise reason):** there is a real *straddle* — in the prefix
  {5,7,11,13,23}, the 7 axis has ∏ p/(p−1)·rest within 1.5·10⁻⁵ of 9/5: K1 requires
  I(7^a) ≥ a value ABOVE sup(7) (never) and K2 requires a limit ≥ 1 (it is < 1); with the
  deeper axes still open, the iteration does not terminate and the recursion explodes
  (observed: 600 s timeout in the planted tests). The extraction of the last slot
  remains correct, but the window kills do not close outer axes.
- **What to keep:** the exact extraction of the last slot from the denominator of x
  (already reduced fraction) is valid and may become useful again; the substitute that
  worked was PINNING through the feeding of the 5 (v₅(σ(N)) = a₁−1 ≥ 1 forces a feeder
  ≡ 1 (mod 5), which pins P via Φ₅(q) or σ(5^{a₁})) — exactly the chain style of the
  literature, and it closes the branch in two lines of cases.

## [2026-08-20] Phase 0 — no mathematical line of attack abandoned

Phase 0 was about foundations/reproduction; all goals were met. Only methodological dead
ends are recorded (useful so as not to repeat them):

- **GitHub code search without authentication** to check the formal-conjectures repo
  failed (requires login; grep.app returned HTTP 429). The solution that worked and stays
  as the standard method: `git clone --depth 1` + local grep, recording the exact commit.
- **Pure v₃-counting does not rule out 3 | N** (a natural attempt in the re-derivation of
  Theorem D): from 5σ(N) = 9N follows v₃(σ(N)) = v₃(N) + 2, but σ(3^e) ≡ 1 (mod 3) and
  primes ≡ 1 (mod 3) can supply any v₃ via v₃(e_p + 1) — there is no contradiction by
  valuation alone. What closes the argument is the **tightness of the abundancy index**
  (sub-products of I cannot exceed 9/5) combined with the forced divisor σ(3²) = 13.
  Keep: in any future congruence, valuation alone tends to be insufficient; always look
  for the pair (valuation, multiplicative tightness).
