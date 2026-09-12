# RESULTS — labelled statements (rigour rules: `docs/METHODOLOGY.md`)

Last update: 2026-09-12 (Phase 1, Block 6). Details: `PHASE_0.md`, `PHASE_1.md`.

## Notation

N denotes a hypothetical friend of 10: N ≠ 10 and 5·σ(N) = 9·N (equivalently I(N) = 9/5).

## Theorems re-derived in Phase 0 (own proof + numerical verification + adversarial pass)

| # | Statement | Label |
|---|---|---|
| A | N is odd | `[PROVED]` (PHASE_0.md §4; adversarial §6) |
| B | N is a perfect square | `[PROVED]` |
| C | 25 \| N | `[PROVED]` |
| D | the least prime divisor of N is 5 (2 ∤ N, 3 ∤ N, 5 \| N) | `[PROVED]` |
| E | N ≥ (5·7·11·13·17·19·23·29·31·37)² = 1 529 648 735 150 649 937 048 225 ≈ 1.53·10²⁴ | `[PROVED-CONDITIONAL: A–D + ω(N) ≥ 10 (arXiv:2310.15900)]` |
| E′ | N ≥ 49·(5·7·⋯·37)² = 74 952 788 022 381 846 915 363 025 ≈ 7.50·10²⁵ | `[PROVED-CONDITIONAL: A–D + ω(N) ≥ 10 + Thm 1.9 of arXiv:2404.00624]` |

Remark: A–D reproduce results of Ward 2008 (they are not new); the proof of D here is an
independent variant (it uses only the forced prime 13, not Ward's pair {13, 31}).
E/E′ are direct arithmetic consolidations of the constraints in the literature — no
novelty claim (no search for an identical statement was made; the value is internal to
the project).

## Phase 1, Block 1 — certificates of the search engine (PHASE_1.md)

| # | Statement | Label |
|---|---|---|
| F | Every friend of 10 has ω(N) ≥ 6 (independent reproduction of Ward 2008 by the engine: exact prunings + cyclotomic closure) | `[PROVED-CONDITIONAL: Theorems A–D and the Phase 0 Lemmas + Zsygmondy/cyclotomic identity (classical) + correctness of the engine (adversarial pass PHASE_1.md §1.5) + correctness of sympy in the calls consumed (re-verified without sympy in tests/test_motor_crosscheck.py)]` |
| G | The least friend of 10, if it exists, exceeds **10³²** (certified exhaustive sweep of every signature with ω ∈ {10,11,12} and N ≤ 10³²; ω ≥ 13 impossible for N ≤ 10³² by the product rule; 34.5 million exact equalities tested, zero friends) | `[PROVED-CONDITIONAL: Theorems A–D and the Phase 0 Lemmas + ω(N) ≥ 10 (arXiv:2310.15900) + correctness of the engine (§1.5)]` |

Context for G: certifies, and improves 100×, the UNCERTIFIED claim "least friend
> 10³⁰" (OEIS A074902, cited in arXiv:2404.00624). Honest frontier of the engine:
ω = 6 is not certifiable by index pruning alone (`RamoNaoLimitado`) — coinciding with
the point where the literature needed divisibility chains (target of Block 2).

## Phase 1, Block 2 — divisibility chains (PHASE_1.md, Block 2)

| # | Statement | Label |
|---|---|---|
| H | **Every friend of 10 has ω(N) ≥ 7** (no friend has ω = 6: 19 prefixes, 2 745 complete sets, all killed by the closure by orders; the only prefix with an infinite space, {5,7,11,13,23}, closed by pinning the 6th prime to P ∈ {31, 3221}) | `[PROVED-CONDITIONAL: Theorems A–D and Lemmas/Fact 0 of Phase 0 + Zsygmondy and the Nielsen/Voight valuation formula (classical; formula re-tested exhaustively) + correctness of core/omega6.py and core/cadeias.py (adversarial pass PHASE_1.md §2.5) + correctness of sympy.n_order/factorint/nextprime in the calls consumed (all re-verified by own implementations)]` |

Context for H: **independent, mechanical** reproduction (0.1 s) of Theorem 1.2 of
arXiv:2404.00624, whose published proof is a manual analysis of 19 chains. The
automatic pinning rediscovers by itself the entry **f_3221^11 = 5** of Table 4 of the
paper (built by hand by the authors). Not a new result — it is cross-validation of the
literature by an independent route, and the infrastructure for attacking ω = 8 in Block 3.

## Phase 1, Block 3 — recursive certifier (PHASE_1.md, Block 3)

No new statement. The recursive certifier `core/omega_k.py` (complete case partition
by the budgets v₅ and v₃, with the universal bound a₁ ≤ 1 + (c₅+s)(c₅+s−1) and injective
feasibility of witnesses) **re-certifies ω(N) ≥ 7 independently and briefly** (27
complete sets, 57 nodes) — still without its own adversarial pass, therefore NOT
load-bearing for the label of H, which continues to rest on Block 2.
**ω = 7 remains open** for the method; the frontier is characterised in PHASE_1.md §3.5
and FAILURES.md (state {5,7,11,13,31,331}+P, a_P = 14 forced). *(Superseded in Block 4.)*

## Phase 1, Block 4 — tightening, direct valuations, tails (PHASE_1.md, Block 4)

| # | Statement | Label |
|---|---|---|
| I | **Every friend of 10 has ω(N) ≥ 9** (no friend has ω = 7: 549 nodes, 153 complete sets, 1.5 s; none has ω = 8: 210 456 nodes, 145 659 complete sets, 323 tails, 72 s; zero friends, zero `NaoCertificavel`) | `[PROVED-CONDITIONAL: Theorems A–D and Lemmas/Fact 0 of Phase 0 + Zsygmondy, LTE and the Nielsen/Voight valuation formula (classical) + correctness of core/omega_k.py (STILL WITHOUT its own adversarial pass — NOT load-bearing) and of this block's changes to core/cadeias.py and core/omega6.py (§4.2, not yet adversarially reviewed) + correctness of sympy.n_order/factorint/isprime/nextprime/cyclotomic_poly/divisors in the calls consumed]` |

Context for I: **not new** — Thackeray (arXiv:2310.15900) proves ω(N) ≥ 10. The value is
the mechanical, independent and short (75 s of CPU) reproduction of part of the state of
the art, and the method (exponent commitments closed piece by piece through cyclotomic
factors, branching with a Nielsen tail under a termination measure, complete sets with one
large prime without factoring r − 1) is the instrument for k ≥ 9. The Block 3 wall was a
tightening defect (a₁ committed but left out of the index bounds), not missing theory —
recorded in FAILURES.md. The label of H (ω ≥ 7) continues to rest on Block 2; I only
moves up in label after the recursive certifier's own adversarial pass (targets listed in
PHASE_1.md §4.8 and §5.5).

## Phase 1, Block 5 — the last unknown by cyclotomic equations (PHASE_1.md, Block 5)

No new statement. The lemma Φ_ℓ(U) = ℓ^ε·∏_{q∈C_ℓ} q^{e_q} (ℓ | a_U + 1 with a
witness in C, finite right-hand side, U by exact integer root) replaces the index
enumeration of the last unknown; verified against independent brute force. k = 8 drops
from 210 456 to 90 032 nodes (36 s), same verdict. k = 9 stays blocked by almost-tight
nodes with **two** unknowns (FAILURES.md), the regime in which Thackeray spent 25 h of
CPU; 12 h of brute force were not enough.

## Phase 1, Block 6 — Cor. 6 + Prop. 9 (PHASE_1.md, Block 6)

No new statement. Re-derived and implemented with tests against brute force:
Proposition 9 (Wieferich levels through the subgroup of order r−1 of (Z/rᵃ)*) and
Corollary 6 (finite bound a_r ≤ v_r(den) − v_r(num) + levels + Wieferich). An unsafe
bound L on the unknowns was caught by the test comparing it with the real index loop and
closed; in its sound form the bound never fires for k ≤ 8 (same tree as Block 5). The code
keeps `maximos` (inherited upper bounds) and the total-closure lemma. k = 9 remains
open; the diagnosis of §6.3 (partition by B′ with a virtual factor in the tails) is the
candidate Block 7.

## Numerical verifications

| Statement | Label |
|---|---|
| No n ≠ 10 with I(n) = 9/5 in [1, 2·10⁶] | `[VERIFIED-NUMERICALLY: exact sieve, experiments/busca_direta.py]` |
| No friend of 10 up to 10¹² | `[PROVED (A–C) + VERIFIED-NUMERICALLY: N = m², m odd, 5\|m, m ≤ 10⁶ — experiments/busca_estrutural.py; unconditional after Phase 0]` |
| The only solution of 5σ(n) = 9n in [1, 10⁷] is n = 10 | `[VERIFIED-NUMERICALLY: adversarial reviewer, independent exact sieve]` |

## Corrections to the literature (full catalogue: `results/ERRATA.md`)

Re-verified on 2026-08-21 in a second independent pass, on the verbatim arXiv text, with
certificates in `experiments/verifica_erratas.py` and `tests/test_erratas.py` (28 tests).
Publication material: `publication/`.

| Finding | Label |
|---|---|
| arXiv:2404.00624 v5 Lemma 2.3 = arXiv:2409.04451 v4 Lemma 23: false as stated (equality at the all-ones partition); statements of Lemma 3.6/24 and Thm 1.10 intact, proofs need the corrected form | `[PROVED: exact counterexample + proved correction]` |
| arXiv:2404.00624 v5, Remark 3.7 eq. (7): the displayed derivation gives Ω(m) ≥ ω(N) + 2a − 2, not +2a−1; eq. (8) becomes Ω(m) ≥ ω(m) + 2a − 1 | `[PROVED: re-derived algebra + 152 integer witnesses]` |
| The bound of Thm 1.10 (2ω+6a−4) is the **exact optimum** of the relaxation used in its proof — the unit missing in eq. (7) is not recoverable by that argument | `[PROVED: exhaustive minimisation, 48 pairs (a, ω)]` |
| arXiv:2404.00624 v5, Cor. 1.11: as proved it supports only N < 5·6^((2^{K−2a+2}−1)²); the original form is repeated in arXiv:2504.08295 §1 | `[PROVED: direct consequence of the item above]` |
| arXiv:2412.02701 v4, Thm 1.2: effective only for 2 ≤ r ≤ 5 (X₆ = 82944/85085 < 1, F₆ = 17017/9216 > 9/5); title/abstract promise all primes | `[PROVED: exact arithmetic, both readings of the condition]` |
| arXiv:2404.00624 v5, Case 12 of Thm 1.2: printed factor 381/361 = I(19²) in place of I(23²) = 553/529; conclusion of the case maintained | `[PROVED: exact recomputation]` |

## Annotated candidates (WITHOUT own proof yet — do not use as hypotheses)

- q₅ < p_{28ω} (sketch in the note on 2404.05771) and r = 5 admissible in 2412.02701 v4 — `[HEURISTIC/PENDING]`
- Converse of Ward's mod 18 (p ≡ 1 mod 3, 2e ≡ 8 mod 18 ⟹ 9 | σ(p^{2e})) — `[VERIFIED-NUMERICALLY: p ≤ 73, e ≤ 199; short proof sketched in the Ward note]`
- Candidate uniform lemmas for the 2p family: Thackeray's Cor. 6 (odd squares); N > d(N)²/r² generalising Thm 1.5 of 2504.08295 — `[CONJECTURE/PENDING]`
