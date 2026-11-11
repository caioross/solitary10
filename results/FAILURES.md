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

## [2026-11-11] Phase 1, Block 8 — ω = 10 by the method of Blocks 5–7 (current dead end)

- **What was tried:** `certifica_omega(10)` on the target-generic, reviewed code of Block 8
  (PHASE_1.md §8.8), and a survey run that records every refusal and goes on
  (on the code of 10 November, by the unversioned predecessor of
  `python experiments/survey_omega_k.py --k 10 --seconds 14400`, whose first 15 000 nodes on
  the code of the Block 8 commit give the same six refusals; not a certificate).
- **Why it failed (precise reason):** the run refuses after 10 804 nodes at
  C = {5, 7, 11, 13, 31, 97, 52361}, s = 3, a₁ = 2: the index interval of the smallest
  unknown, (102 507 528, 615 045 164], exceeds `MAX_INDEX_SPAN`. The split at B_min still
  works on side (a), U₁ ≤ B − 1. On side (b), U₁ > B, the finite exponent bound needs a
  bound L on *every* unknown, and with three unknowns there is none: for U₁ just above B
  the remainder R′ = t/(prod_sup·U₁/(U₁−1)) is just above 1 and U₂, U₃ are unbounded. What
  is left is to enumerate U₁ over about 26 million primes, each with an s = 2 subtree.
  The survey visited 47.5 million nodes in 4 hours, met six such refusals (seventh prime
  52361, 52363, 52369, 52379, 52387, 52391; all s = 3, a₁ = 2) and never left a₁ = 2; at
  the measured 130 primes per second the interval above alone is about 55 hours, and the
  family continues (the next node, seventh prime 52433, is under the limit (1.39·10⁸ wide)).
- **What to keep:** the enumeration left is finite but impractical (days per interval, and the family continues). The
  method closes near-tight nodes with at most two unknowns (the last unknown by
  cyclotomic equations, two unknowns by the finite exponent bound after the split).
  Three candidate ingredients, none attempted: a finite exponent bound that needs only the
  two largest unknowns bounded in terms of the smallest; a cyclotomic equation for the
  last *two* unknowns (σ(U₃^a) is made of primes of C ∪ extras, U₁ and U₂, all smaller
  than U₃); tails that work on side (b). Thackeray's paper stops at the same place (its §5).

## [2026-11-11] Phase 1, Block 8 — defects found while making the certifier generic and proving primality (all closed)

- **What was tried:** removing the guard that restricted the partition to 9/5, so that
  planted friends could be driven through it; recording the primality claims of the runs.
- **Why it failed (precise reason, one per defect):**
  1. *Statements true only because the numerator of 9/5 is a power of 3.* About a dozen
     steps of the partition (closures modulo C ∪ {3}, witnesses searched in C, the v₅ and
     v₃ budgets, the range of a₁, the caps of the last-unknown solver, the total-closure
     lemma) were sound for 9/5 only. With the guard removed and nothing else changed,
     the certifier *certified* the absence of friends for the target
     I(5²·7²·11²·13²·17²·19²) at k = 6 — a false certificate. Every statement was
     re-derived for t = num/den (PHASE_1.md §8.1); the 9/5 trees did not change.
  2. *An unbounded factorisation at the root.* A target whose num or den had two large
     primes hung for hours instead of being refused. Now: bounded Pollard rho, then refusal.
  3. *A ledger with a hole.* The first ledger of primality claims recorded the answers of
     `isprime` and `factorint` but not the factorisations made inside `sympy.n_order`
     (one claim of 67 bits at k = 9, below ψ₁₃). Orders are now computed in
     `core/cadeias.py` from a recorded factorisation of q − 1.
  4. *Trust where a check was cheap.* The small primes stripped from cyclotomic values
     were taken from `factorint` unchecked (now checked against our own sieve), and the
     certificate verifier read one field twice, so that an object imitating a dictionary
     could show a composite to one check and a prime to another (stored certificates were
     never affected; the verifier now accepts plain dicts and lists of plain ints only).
  5. *A refusal guard measured with the wrong bound.* The index fallback with one unknown
     measured its interval with L₁ ≈ 2·B_min instead of B_min and refused all-fixed nodes
     whose window holds one or two primes (two planted friends, now R25 and R26 of
     tests/test_planted.py). It changed no certificate, only refusals.
- **What to keep:** a certifier written for one target hides its assumptions in the
  arithmetic of that target; planted friends only test what they can reach, so the
  mutation harness (`experiments/planted_mutations.py`) and statement-level tests are
  needed alongside them (PHASE_1.md §8.3).

## [2026-11-11] Phase 1, Block 8 — a node with one unknown of 81 bits is refused (open)

- **What was tried:** the planted friend N₀ = 5²·q⁴·r² with q = 1050367 (q ≡ 1 mod 3) and
  r = Φ₅(q) = σ(q⁴), a prime of 81 bits (r ≡ 2 mod 3), from the root (k = 3) and from the
  node C = {5, q}, s = 1, a₅ = 2.
- **Why it failed (precise reason):** at that node both budgets are 0, so the
  last-unknown solver needs L(C). The prime 175061 of q − 1 has the free prime q in C_ℓ,
  and Φ₁₇₅₀₆₁(U_max) would have about 1.4·10⁷ bits: the size gate declines the whole
  solver (declining one ℓ alone would lose cases). The tails do not apply
  (prod_sup < t); the finite exponent bound is not offered at s = 1 (`_ramos_cor6`
  requires lo ≥ B_min, which never holds at a live node with s = 1); and the index
  interval of r is about 10²⁴ wide, above `MAX_INDEX_SPAN`. The certifier refuses
  (`NaoCertificavel`), at that node and from the root alike: the friend is never lost,
  and with a_q fixed the closure pins r and the friend is found. In the coverage the
  review measured on the 9/5 runs with k ≤ 9, neither the size gate nor this refusal
  is reached.
- **What to keep:** the condition lo ≥ B_min of `_ramos_cor6` is needed only for
  s ≥ 2 (at s = 1, L = L1 bounds the only unknown). Offering the bound at s = 1, with
  `R_MAX_PROP9` ≥ q (here q > 10⁶), is the candidate fix: a trial on a modified copy
  gave A_q = 9 and found the friend, left the trees of k ≤ 8 unchanged, and added
  Prop. 9 work at many later nodes with s = 1. It is a change of strategy and must be
  measured on the k = 9 tree, by a versioned script, before k = 10. Dropping a single ℓ
  by a size comparison is sound only when every prime of C_ℓ has a cap, and does not
  resolve this node. Before k = 10, count on the k = 9 tree, by a versioned script, the
  size-gate declines, the calls of `_ramos_cor6` at s = 1 and the `MAX_INDEX_SPAN`
  refusals. Pinned by
  `tests/test_planted.py::test_known_refusal_one_unknown_with_both_budgets_zero`.

## [2026-11-10] Phase 1, Block 7 — defects of the recursive certifier found on the way to ω = 9 (all closed)

- **What was tried:** closing k = 9 with the split at B_min (PHASE_1.md §7), and then
  attacking the whole recursive certifier adversarially before trusting the answer.
- **Why it failed (precise reason, one per defect):**
  1. *Silent stall.* The partition by the v₅ budget enumerated C(T + c, c) vectors
     before testing any: 3.9·10⁸ at the child a₁ = 54 of the k = 9 root. Two runs were
     lost, each stopped after more than 45 minutes without output. Not unsound, but a
     certifier that does not answer certifies nothing.
  2. *A lemma whose premise was not what the code had checked.* The total-closure
     lemma needs "no σ(q^{a_q}) has a prime outside C ∪ {3}"; a cyclotomic piece skipped
     by a size gate counted as "no new prime". Latent since Block 6, never fired.
  3. *A count that depended on the order of processing.* Since Block 4 a pin found
     from a later fixed prime and dividing the unfactored residue of an earlier one
     was counted twice, so a node could die in one insertion order of the fixed
     exponents and live in the other. By audit of the Block 6 trees (k = 7, 8), and
     by the same count repeated on the code of Blocks 4 and 5, it never decided a
     node for k ≤ 8.
  4. *A float inside a kill path*, hidden in a library call (`sympy.perfect_power`
     filters odd exponents with a floating-point comparison below 2⁴⁰).
  5. *A written derivation that was not the one implemented.* The Cor. 6 header and
     PHASE_1.md §6.1 had the sign of v_r(num) − v_r(den) reversed and claimed an
     agreement with the universal bound of Block 3 that no test checked and that is
     false; the code was right.
  6. *Loops and asserts where a refusal was due.* A tail equal to its own parent, an
     index interval longer than 2·10⁸ walked instead of refused, a solver past its
     size gate. In the same family, caught on the prototype: two split children that
     the case de-duplication would have merged because they differ only in (lo, hi).
- **What to keep:**
  - Every enumeration needs either a proof that it is small or a guard that refuses
    (`MAX_ASSIGNMENTS`, `MAX_INDEX_SPAN`, `SOLVER_BITS`). A stack watchdog on a thread
    finds the stalled frame in minutes; elapsed time must be read from the process
    clock, not guessed.
  - The premise of a kill has to be computed from what was actually examined
    ("every piece examined and none had a new prime"), never from the absence of a
    finding.
  - Any count of unknowns must be invariant under the order in which the information
    arrives: test it by permuting the order against full factorisation.
  - Library calls in kill paths have to be read for floats, not assumed exact.
  - A reviewer attacking the written proof finds errors that tests of the code cannot:
    the derivation and the code must be checked against each other, both ways.
  - A guard is part of the certifier too: the first version of `MAX_ASSIGNMENTS`
    compared a crude product with its limit and would have refused nodes with 120
    real cases. Count exactly what is guarded.
  - A long run should be audited as a run: replaying it with spies and re-deriving
    every decision family by family (PHASE_1.md §7.6) showed which paths carry the
    certificate and which never execute, which no unit test can show.
  - Outcome: with these closed, k = 9 certifies in about 6 minutes (PHASE_1.md §7.5).

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
- **Outcome (2026-11-10, Block 7):** the split was implemented and works: the node
  {5,7,11,13,31,97,52361} closes in 54 nodes and 0.1 s, and the finite exponent bound
  finally fires where it is valid (case (b), s = 2). Two further defects of this
  block's code surfaced on the way: the bound L = 1 + 2·b·L₁ was valid but
  astronomically loose once exponents are fixed or bounded (replaced by the exact
  bound U₂ < 1 + 1/(R′_min − 1)), and the total-closure lemma ignored cyclotomic
  pieces skipped by the size gates — latent unsoundness found by the adversarial
  panel and closed (PHASE_1.md §7.3–7.4).

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
- **Outcome (2026-11-10, Block 7):** no longer a dead end. The finite exponent bound
  alone did not fire (Block 6); what closed the node was splitting on the position of
  the smallest unknown relative to B_min, with a virtual factor that lets the tails
  work without enumerating it (PHASE_1.md §7.1–7.2). k = 9 is certified.

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
