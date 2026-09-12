# Phase 0 — Foundations and reproduction

Date: 2026-08-20.
Scope: Phase 0 of the roadmap ONLY (`docs/METHODOLOGY.md`). No advance to Phase 1 without explicit approval.

---

## 0. Executive summary

- Environment set up (Python 3.13.2, venv, sympy 1.14.0, pytest 9.1.1); **all tests green**.
- Sanity searches run: no friend of 10 up to 2·10⁶ (unconditional) nor in the
  structural space up to 10¹² — and the structural sweep became **unconditional**
  after the proofs of this phase (Corollary of section 4).
- Re-derived from scratch, with complete proofs, the four basic constraints (Theorems A–D):
  a friend N of 10 is odd, is a perfect square, 25 | N, and its least prime divisor is 5.
  Each proof went through independent numerical verification (section 5) and an
  adversarial pass with 9 reviewers (section 6): **all SOUND**, cosmetic adjustments only.
- Exact lower bound: **N ≥ 1.53·10²⁴** `[PROVED-CONDITIONAL: A–D + ω ≥ 10]`, sharpened
  to **N ≥ 7.50·10²⁵** with Thm 1.9 of arXiv:2404.00624 (section 7).
- 6 papers read in full text, one note per paper in `literature/`; the overview table
  checked item by item (section 8). **Four divergences documented** (section 10),
  including two real defects in arXiv:2404.00624 (Lemma 2.3; an off-by-one in Remark 3.7
  that weakens Cor. 1.11) and the actual reach of arXiv:2412.02701 (only r ≤ 5, not
  "all primes").
- Web checks (section 9): nothing in 2025–26 beats ω ≥ 10; two new analogous papers
  (14 and 20); the statement "10 is solitary" is ALREADY formalised in DeepMind's
  formal-conjectures; mathlib has σ and `Nat.abundancyIndex`, but no friendly/solitary
  lemma.
- Three targets proposed for Phase 1 (section 11). **Stopped here, awaiting approval.**

---

## 1. Environment and tests

- Python 3.13.2 (venv in `venv/`), `sympy 1.14.0`, `pytest 9.1.1`, `mpmath 1.3.0`.
- `pytest -q`: **7 passed** (original suite) — see section 5 for the new tests of this phase.
- Git initialised in this directory (first commit at the end of the phase).

## 2. Sanity searches

| Search | Command | Space swept | Result |
|---|---|---|---|
| Direct (unconditional) | `python experiments/busca_direta.py --limite 2000000` | all n ∈ [1, 2·10⁶] | only n with I(n) = 9/5: `[10]` — **no friend** |
| Structural (conditional) | `python experiments/busca_estrutural.py --limite-m 1000000` | N = m², m odd, 5 \| m, m ≤ 10⁶ (N up to 10¹²) | **no friend** in the structural space |

Labels:
- `[VERIFIED-NUMERICALLY: 1 ≤ n ≤ 2·10⁶]` — 10 has no friend up to 2·10⁶.
- `[VERIFIED-NUMERICALLY: N = m², m odd, 5|m, m ≤ 10⁶]` — no structural friend up to
  10¹². Conditional on Ward's constraints; **the constraints used (odd, square, 5 | N) are
  exactly the ones proved in section 4**, so after this phase the sweep holds
  unconditionally: a friend N ≤ 10¹² would have to be an odd square multiple of 25
  (Theorems A–C), i.e. N = m² with m odd and 5 | m ≤ 10⁶ — a space swept in full.

## 3. Preliminaries

**Definitions.** σ(n) = sum of the positive divisors of n; I(n) = σ(n)/n (abundancy
index, always an exact rational). m, n are friends if m ≠ n and I(m) = I(n).

**The friend equation.** I(10) = σ(10)/10 = (1+2+5+10)/10 = 18/10 = 9/5. Hence

> N is a friend of 10 ⟺ N ≥ 1, N ≠ 10 and 5·σ(N) = 9·N.   (★)

Remark: N = 1 does not satisfy (★) since I(1) = 1 ≠ 9/5; thus N > 1 and N has a prime factor.

**Fact 0 (multiplicativity).** σ is multiplicative; if N = ∏ᵢ pᵢ^{eᵢ} (distinct primes),
σ(N) = ∏ᵢ σ(pᵢ^{eᵢ}) with σ(p^e) = 1 + p + ⋯ + p^e = (p^{e+1}−1)/(p−1). Consequently
I(N) = ∏ᵢ I(pᵢ^{eᵢ}), and each factor I(pᵢ^{eᵢ}) > 1, since in the canonical
factorisation eᵢ ≥ 1 (and I(p^e) = 1 + 1/p + ⋯ ≥ 1 + 1/p > 1).
*Proof:* standard (the divisors of mn with gcd(m,n)=1 are unique products d₁d₂, d₁|m, d₂|n). ∎

**Lemma 1.** For every n ≥ 1: I(n) = Σ_{d|n} 1/d.
*Proof:* the map d ↦ n/d is a bijection of the set of divisors of n onto itself
(an involution; the possible fixed point d = √n is no obstacle — it is just a
re-indexing of the sum); hence
σ(n)/n = (Σ_{d|n} d)/n = Σ_{d|n} d/n = Σ_{d|n} 1/(n/d) = Σ_{e|n} 1/e. ∎

**Lemma 2 (strict monotonicity over divisors).** If d | n and d < n, then I(d) < I(n).
*Proof:* every divisor e of d is a divisor of n, hence by Lemma 1,
I(d) = Σ_{e|d} 1/e ≤ Σ_{e|n} 1/e = I(n). The inequality is strict because the term 1/n
occurs in the sum for I(n) but not in the one for I(d) (n ∤ d, since n > d). ∎

**Lemma 3 (growth in e).** For a fixed prime p, I(p^e) is strictly increasing in e,
and I(p^e) < p/(p−1) for every e ≥ 0.
*Proof:* I(p^e) = 1 + 1/p + ⋯ + 1/p^e (Lemma 1 applied to p^e); each increment of e adds
the positive term 1/p^{e+1}; the full series converges to p/(p−1), a strict bound for any
partial sum. ∎

**Lemma 4.** If N satisfies (★), then 5 | N and 9 | σ(N).
*Proof:* 5 | 5σ(N) = 9N and gcd(5,9) = 1 ⟹ 5 | N. Likewise 9 | 5σ(N) and gcd(9,5)=1
⟹ 9 | σ(N). ∎

## 4. The four basic constraints, re-derived

Let N be a friend of 10, i.e. N ≠ 10 satisfying (★).

### Theorem A — N is odd. `[PROVED]`

*Proof.* Suppose 2 | N. By Lemma 4, 5 | N; since gcd(2, 5) = 1, it follows that 10 = lcm(2,5) | N.
Since N ≥ 1 and 10 | N, we have N ≥ 10; with N ≠ 10, N ≥ 20, so the divisor 10 is proper
(10 < N) and Lemma 2 gives I(10) < I(N), i.e. 9/5 < 9/5 — absurd. ∎

### Theorem B — N is a perfect square. `[PROVED]`

*Proof.* By Theorem A, N is odd, so 9N is odd; by (★), 5σ(N) = 9N is odd, so
σ(N) is odd. Write N = ∏ᵢ pᵢ^{eᵢ} with all pᵢ odd. By Fact 0,
σ(N) = ∏ᵢ σ(pᵢ^{eᵢ}). Each factor σ(pᵢ^{eᵢ}) = 1 + pᵢ + ⋯ + pᵢ^{eᵢ} is a sum of eᵢ + 1
odd terms, therefore σ(pᵢ^{eᵢ}) ≡ eᵢ + 1 (mod 2). The product ∏ᵢ σ(pᵢ^{eᵢ}) is odd
if and only if every factor is odd, i.e. every eᵢ is even. Finally, all exponents
even ⟺ N is a perfect square: if eᵢ = 2fᵢ, then N = (∏ᵢ pᵢ^{fᵢ})²; conversely,
if N = M², unique factorisation gives eᵢ = 2·v_{pᵢ}(M), even. ∎

### Theorem C — 25 | N. `[PROVED]`

*Proof.* By Lemma 4, 5 | N, that is v₅(N) ≥ 1. By Theorem B, every exponent in the
factorisation of N is even; hence v₅(N) is even and ≥ 1, therefore v₅(N) ≥ 2, i.e. 25 | N. ∎

### Theorem D — the least prime divisor of N is 5 (equivalently: 3 ∤ N, given A and Lemma 4). `[PROVED]`

Since N > 1, N has primes; 2 ∤ N (Theorem A) and 5 | N (Lemma 4). It remains to prove 3 ∤ N.

*Proof of 3 ∤ N.* Suppose 3 | N. By Theorem B the exponents are even: write
v₃(N) = 2a ≥ 2 and v₅(N) = 2b ≥ 2 (Theorem C). By Fact 0, I(N) = 9/5 is the product of
the factors I(p^{v_p}), all > 1; hence, for any subset S of the primes of N,
∏_{p∈S} I(p^{v_p}) = (9/5) / ∏_{p∉S} I(p^{v_p}) ≤ 9/5, i.e. **any sub-product of
factors satisfies ∏_{p∈S} I(p^{v_p}) ≤ 9/5**, with equality only if S contains all the
primes of N. (Lemma 3 will be used in the lower bounds of the cases below.)

Three cases:

**Case 1: a ≥ 2** (i.e. 81 | N). Then, by Lemma 3,
I(3^{2a})·I(5^{2b}) ≥ I(3⁴)·I(5²) = (121/81)·(31/25) = 3751/2025 > 3645/2025 = 9/5.
A sub-product exceeds 9/5 — contradiction.

**Case 2: a = 1, b ≥ 2** (i.e. 3² ‖ N and 625 | N). Then
I(3²)·I(5^{2b}) ≥ (13/9)·(781/625) = 10153/5625 > 10125/5625 = 9/5 — contradiction.

**Case 3: a = 1, b = 1** (i.e. v₃(N) = 2 and v₅(N) = 2 exactly). Then σ(3²) = 13 and
σ(5²) = 31 are factors of σ(N) = ∏ σ(p^{v_p}), so 13 | σ(N). By (★),
σ(N) = 9N/5 = 9·(N/5) with N/5 an integer; from 13 | 9·(N/5) and gcd(13,9) = 1 comes
13 | N/5, in particular **13 | N**. Since 13 ∉ {3,5}, the prime 13 appears in the
factorisation with even exponent ≥ 2 (Theorem B), hence I(13^{v₁₃}) ≥ I(13²) = 183/169. But then the
sub-product
I(3²)·I(5²)·I(13²) = (13/9)·(31/25)·(183/169) = 73749/38025 > 68445/38025 = 9/5
— contradiction. (Exact check: 13·31·183 = 73749; 9·25·169 = 38025; 9·38025/5 = 68445.)

In all three cases we reach an absurdity; hence 3 ∤ N, and the least prime divisor of N is 5. ∎

**Remark (the near-friend 225).** Case 3 "almost" produces a friend: N = 3²·5² = 225 has
5σ(225) = 5·403 = 2015, against 9·225 = 2025 — a difference of only 10 (I(225) = 403/225
against 405/225 = 9/5). This is exactly the mechanism the proof exploits: the deficit
could only be covered by the forced prime 13, which overshoots 9/5.

### Corollary (used in section 2)

Every friend of 10 has the form N = m² with m odd and 5 | m. Therefore the structural
search of section 2 is exhaustive for N ≤ 10¹², **unconditionally**:
`[PROVED]` + `[VERIFIED-NUMERICALLY: N ≤ 10¹²]` ⟹ **the least friend of 10, if it
exists, exceeds 10¹²** (and in fact much more — section 7).

## 5. Independent numerical verification

File: `tests/test_fase0_proofs.py` (runs under `pytest -q`). Independence: the tests
use an implementation of σ by trial division (`_sigma_trial`), without sympy, and
cross it against `core.abundancy.sigma` over an interval; all comparisons in exact
integers / `Fraction`. It verifies:

1. Cross-check `_sigma_trial(n) == sigma(n)` for n ≤ 20 000.
2. Lemma 1 (I(n) = Σ 1/d) for n ≤ 2 000, with `Fraction`.
3. Lemma 2 (strict monotonicity on proper divisors) for n ≤ 3 000.
4. Lemma 3 (I(p^e) increasing, < p/(p−1)) for p ≤ 37, e ≤ 12.
5. Parity of σ (the mechanism of Theorem B): for odd n ≤ 60 000, σ(n) odd ⟺ n a square.
6. The three exact inequalities of Theorem D (cases 1–3), by cross-multiplication of integers.
7. Mechanism of Theorem A: for every multiple of 10 with 10 < n ≤ 300 000, 5σ(n) > 9n.
8. Mechanism of Theorem A (full even branch, suggested by the adversarial pass):
   no even n ≤ 200 000, n ≠ 10, satisfies 5σ(n) = 9n.
9. Mechanism of Theorem D: for every N = m² with 15 | m, m ≤ 4 000, 5σ(N) ≠ 9N.
10. 225: 5σ(225) = 2015 ≠ 2025 = 9·225.

Result: **green** (see the `pytest -q` output recorded in section 12).

Additional adversarial sweeps (run by the reviewers of section 6, with independent
exact sieves; recorded here as reinforcement, not as a substitute for the tests):
- the only solution of 5σ(n) = 9n in [1, 10⁷] (all parities) is n = 10;
- no odd n ≤ 10⁸ with 5σ(n) = 9n; parity of σ ⟺ square confirmed over the
  5·10⁷ odd numbers ≤ 10⁸;
- no N = m², 15 | m, m ≤ 150 000 (N up to 2.25·10¹⁰) satisfies the friend equation.

## 6. Adversarial pass

Run on 2026-08-20 by 9 independent reviewers, each instructed to **refute** — recompute
every fraction with exact arithmetic, hunt for gaps, hidden hypotheses, circularity and
numerical counterexamples. Verdicts:

| Target | Reviewer(s) | Verdict | Issues |
|---|---|---|---|
| Fact 0 + Lemmas 1–4 | 1 | **SOUND** | 2 cosmetic (wording) — fixed |
| Theorem A | 2 (logic + counterexample) | **SOUND** ×2 | 3 cosmetic — fixed; sweep up to 10⁷ with no counterexample |
| Theorem B | 2 (logic + counterexample) | **SOUND** ×2 | 4 cosmetic — fixed; mechanism verified up to 10⁸ |
| Theorem C | 1 | **SOUND** | 1 cosmetic — fixed |
| Theorem D | 2 (logic + counterexample) | **SOUND** ×2 | 4 cosmetic — fixed; all inequalities re-verified by cross-multiplication of integers; sweep of squares that are multiples of 225 up to 2.25·10¹⁰ |
| Lower bound (section 7) | 1 | **MINOR_GAP** | the inequality and the label were correct, but the script's "Note" was misleading (it said the congruences do not raise the bound, omitting that Thm 1.9 of arXiv:2404.00624 **invalidates the minimal configuration** and gives a factor ≥ 49 for free) and the docstring had a phantom hypothesis. **Both fixed**; sharpened bound incorporated into section 7 |

No `fatal` or `serious` issue in any proof. All cosmetic remarks were applied to the
text of sections 3–4 (explicit citation of Fact 0 in the proof of B, justification of
the equivalence "even exponents ⟺ square" via unique factorisation, explicit positivity
in Theorem A, notation of Case 2 of D, wording of Lemma 1 and of Fact 0). Only after this
round did Theorems A–D receive the label `[PROVED]` (rigour rule #3).

## 7. Lower bound for N

Script: `experiments/limite_inferior.py` (100% integer arithmetic; floats only for display).

**Theorem E (lower bound).** If N is a friend of 10, then

> N ≥ (5·7·11·13·17·19·23·29·31·37)² = 1236789689135² = **1 529 648 735 150 649 937 048 225** ≈ 1.53·10²⁴.

Label: `[PROVED-CONDITIONAL: Theorems A–D (proved in this phase) + ω(N) ≥ 10
(arXiv:2310.15900, Thackeray, Indagationes Math. 2024 — verified by reading,
NOT re-derived)]`

*Proof.* By Theorems A and D, every prime divisor of N is ≥ 5; by Theorem B, every
exponent is even, hence ≥ 2. If q₁ < q₂ < ⋯ < q_k are the primes of N with k = ω(N) ≥ 10,
then qⱼ ≥ sⱼ (the j-th smallest prime ≥ 5), whence
N = ∏ qⱼ^{eⱼ} ≥ ∏_{j=1}^{10} qⱼ² ≥ ∏_{j=1}^{10} sⱼ² = (5·7·⋯·37)². ∎

**The known congruences do not raise this bound:** the minimal set
{5,7,11,13,17,19,23,29,31,37} already contains witnesses for all of them — 11 and 31 ≡ 1 (mod 10);
7, 13, 19, 31, 37 ≡ 1 (mod 6); and primes ≡ 1 (mod 3) may carry exponent 2, which already
satisfies 2 ≡ 2 (mod 6) (Ward). Hence none of them forces a prime outside the minimal set.

**Theorem E′ (sharpened bound, added after the adversarial pass).** The minimal
configuration of Theorem E (all exponents = 2) has N = 5²·m² with m = 7·11·⋯·37
**squarefree** — forbidden by Theorem 1.9 of arXiv:2404.00624 (and, independently, by the
exponent constraint of Theorem 1.2 of arXiv:2504.08295). Hence some prime ≠ 5 has
exponent ≥ 4, and the cheapest way is to raise the 7 (factor 7² = 49):

> N ≥ 49·(5·7·⋯·37)² = **74 952 788 022 381 846 915 363 025** ≈ 7.50·10²⁵ (26 digits).

Label: `[PROVED-CONDITIONAL: Theorems A–D + ω(N) ≥ 10 (arXiv:2310.15900) +
Theorem 1.9 of arXiv:2404.00624]`. The adjusted minimal configuration (exponent 4 on 7)
satisfies all the other known constraints of the table (witnesses checked in the
script), so no other constraint raises the bound "for free".

Comparisons (all exact, verified in the script):
- Corollary 1.6 of arXiv:2504.08295 with ω = 10: N > 625·9⁷ = 2 989 355 625 ≈ 3.0·10⁹ — **much weaker**.
- Structural sweep of this phase: N > 10¹² — weaker.
- That is: the prime-signature argument beats the repo's current computational frontier by 12–14 orders of magnitude.
- **Uncertified** claim in the literature: "least friend of 10 > 10³⁰" (OEIS A074902,
  cited in the conclusion of arXiv:2404.00624 without a published certificate). It is
  stronger than Theorems E/E′, but must NOT be used as a hypothesis; producing a certified
  bound ≥ 10³⁰ is exactly target (a) of Phase 1.

## 8. Literature — reading notes and fidelity of the overview table

All 6 papers were read in **full text** (no note based on the abstract alone); one note
per paper in `literature/`, with exact statements, proof method, numerical verification
of the constants (exact Fraction) and a table-fidelity section.

| Paper | Note | Table fidelity | Reading highlights |
|---|---|---|---|
| Ward 2008 (arXiv:0806.1001; IJMCS 3(3) 153–158) | `note_ward_2008.md` | **FAITHFUL** | ω ≥ 6 is Ward's own, unconditional and without a computer; "if unique" in (v) = the unique prime with BOTH properties; numbering erratum in the paper (the cited "property 7" does not exist as a printed item); the 9 rational comparisons of the proof re-verified — two extremely tight (4147/2304 and 24871/13824, within 9·10⁻⁴ of 9/5); the case {7,11,13,23} only closes with the trick σ(5²) = 31 \| σ(N) |
| Chatterjee–Mandal–Mandal (arXiv:2404.00624 v5) | `note_2404.00624.md` | **FAITHFUL**, with omissions (Thm 1.10 and Cor. 1.11 are not in the table) | see §10: Lemma 2.3 false as stated (equality case), off-by-one in Remark 3.7 inherited by Cor. 1.11, typo in Case 12; the f_p^q table sampled and checked |
| Thackeray (arXiv:2310.15900; Indagationes Math. 35(3) 595–607, 2024) | `note_2310.15900.md` | **FAITHFUL** (precision: Nielsen's **2007** method; the author is H. R. Thackeray, not the Mandal trio) | new Cor. 6/7: v₅(N) ≤ (ω(N)−1)² + 1; bottlenecks for ω ≥ 11 identified: v₅ ∈ {2,6,10,12,46} with σ(5^{v₅}) prime; v₅ = 46 would require an analogue of Prop. 9 for a 33-digit prime; Cor. 6 holds for any odd square — candidate uniform 2p lemma |
| Mandal–Mandal (arXiv:2404.05771; Resonance 30, 2025) | `note_2404.05771.md` | **FAITHFUL** (the prime-index form, q₂ < p_⌈7ω/3⌉ etc., is stronger than the published logarithmic one) | with ω = 10: q₂ ≤ 83 (< p₂₄ = 89), q₃ < 193, q₄ < 431 — strong pruning for Phase 1; reviewer's finding (labelled pending): the method appears to extend to q₅ < p_{28ω} |
| Mandal (arXiv:2412.02701 **v4**; Analele Oradea 33(1) 5–12, 2026) | `note_2412.02701.md` | **DIVERGENT** — see §10 | parametric family (A,B) of bounds for q_r effective only for 2 ≤ r ≤ 5; improves q₃, q₄ of 2404.05771 (427/100 and 41/5); with ω = 10 (sharp form): q₂ < 89, q₃ < 191, q₄ < 421, q₅ < 1847; admissible r = 5 is a bonus not made explicit in the paper |
| Mandal (arXiv:2504.08295; News Bull. Calcutta Math. Soc. 48, 2025) | `note_2504.08295.md` | **FAITHFUL** | 9 ‖ σ(F) (Remark 2.4) is the mod-3 engine; Thm 1.5 generalises to any square with I(N) = r: N > d(N)²/r² — candidate uniform 2p lemma; key congruences of the proofs re-verified by hand |

Papers analysed = the complete state of the art of the niche as of 2026-08-20 (novelty
check in section 9.1).

## 9. Web checks

Date of the searches: 2026-08-20 (arXiv, Google Scholar, OEIS); arXiv IDs verified
individually on the `/abs` pages.

### 9.1 New 2025–2026 work in the niche (rigour rule #4)

**New papers found (not in the initial overview):**

| Paper | What it brings | Impact here |
|---|---|---|
| arXiv:2503.11694 — Sagar Mandal, "A note on solitary numbers" (v1 Mar 2025 was "Is 14 a Solitary Number?"; NNTDM 31(3) 2025, 617–623) | A friend F of 14: odd and NOT a square; 7 \| F with even exponent; ≤ 2 primes with odd exponent; mod 8 constraints; 3 and 5 do not divide F simultaneously | Analogue of the 2p family for p = 7. Beats nothing about 10. The item missing from the list of analogues |
| arXiv:2409.04451 — Chatterjee, S. Mandal, S. Mandal, "On Characterizing Potential Friends of 20" (v4 Sep 2025; Ann. West Univ. Timisoara 61(1) 2025, 205–229) | A friend of 20 is 2·5^{2a}·m², gcd(3,m) = gcd(7,m) = 1, ω ≥ 6, bounds for the largest prime | 20 = 2²·5 (outside the 2p family); useful for comparing techniques in Phase 3 |

**Updates of papers already listed:**
- **arXiv:2412.02701 got a v4 (2025-10-16)**, published in Analele Univ. Oradea 33(1)
  2026, 5–12; the current abstract claims **better** bounds for the 3rd and 4th smallest
  primes than those of 2404.05771. The reading note in this repo is of the current version (v4).
- arXiv:2504.08295 published: News Bull. Calcutta Math. Soc. 48(1–3) 2025, 21–32.

**Peripheral 2026 items** (recorded for completeness): arXiv:2601.07444 (Lean 4
formalisation of *amicable* numbers — a concept ≠ friendly; prior art for Phase 4);
arXiv:2606.25849 (Erdős 1061 on σ(a)+σ(b)=σ(a+b)); arXiv:2607.25278 (weird numbers with
high abundancy).

**Important negatives (state of the art unchanged):** no improvement on ω(N) ≥ 10 (the
target ω ≥ 11 remains open); no paper devoted to 15; no uniform theorem for the 2p
family; nothing new from the watched trio after Apr 2025.

### 9.2 formal-conjectures (Google DeepMind)

**YES — the statement is there.** Decisive and reproducible check: `git clone --depth 1`
+ full grep (commit `9f5ee773841921f460b4a26a3552f5eca4accaa0`, 2026-08-19).

- File: `FormalConjectures/Wikipedia/SolitaryNumber.lean`, namespace `SolitaryNumber`.
- `Friendly (m n : ℕ) : Prop := 0 < m ∧ 0 < n ∧ σ 1 m * n = σ 1 n * m` — **reflexive**
  (does not require m ≠ n; cross-multiplication to avoid rationals).
- `IsSolitary (n : ℕ) : Prop := 0 < n ∧ ∀ m, Friendly m n → m = n` — equivalent to
  this project's definition (every friend is n itself).
- `theorem is_ten_solitary : answer(sorry) ↔ IsSolitary 10` with `@[category research open, AMS 11]`.
- In the same file: `infinite_club_exists` (infinite abundancy club, also open).
- Neighbour: `ErdosProblems/470.lean` defines `AbundancyIndex (n : ℕ) : ℚ` (weird numbers);
  it shares no definitions with SolitaryNumber.lean.
- There is **no** formalisation of the Ward/Mandal constraints — only the raw statement (`sorry` proofs).

### 9.3 mathlib (Lean 4) — state for Phase 4

What **exists** (official docs, Aug 2026):
- `ArithmeticFunction.sigma (k : ℕ)` in `Mathlib/NumberTheory/ArithmeticFunction/Misc.lean`
  (the old monolith was split); `sigma_one_apply`, `sigma_apply_prime_pow`, etc.
  Convention: `σ 1 0 = 0`.
- Multiplicativity: `ArithmeticFunction.isMultiplicative_sigma`.
- `Nat.Perfect` in `Mathlib/NumberTheory/Divisors.lean`; Euclid–Euler in the **Archive**
  (`Archive/Wiedijk100Theorems/PerfectNumbers.lean`), not in mathlib proper.
- `Mathlib/NumberTheory/FactorisationProperties.lean`: `Nat.Abundant/Deficient/
  Pseudoperfect/Weird` **and `Nat.abundancyIndex : ℕ → ℚ`** (exactly the project's I(n)),
  with `Nat.abundant_iff_two_lt_abundancyIndex` and `Nat.abundancyIndex_le_of_dvd`
  (**non-strict** inequality).

What **does not exist** (Loogle searches with 0 relevant hits): friendly/solitary/amicable;
multiplicativity of abundancyIndex; formula and monotonicity of I(p^e); the **strict
version** of Lemma 2 of this report (d | n, d < n ⟹ I(d) < I(n)); Greening's criterion.
Consequence: `IsSolitary 10` is statable today (and formal-conjectures already does it), but
all the proof lemmas would have to be formalised from scratch. Greening's criterion would be
a natural, small contribution to mathlib (a candidate for Phase 4).

## 10. Divergences found

Rigour rule #7: divergence is a finding. Four real divergences, none hidden:

### 10.1 arXiv:2404.00624 (v5) — three defects in the paper, one of them with consequences

1. **Lemma 2.3 is false as stated** (the strict inequality a·n < Σ a^{c_i} fails at the
   all-ones partition, where equality holds). Correction: a·n ≤ Σ a^{c_i}, equality iff
   all c_i = 1. Lemma 3.6 and Theorem 1.10 are **not** affected (they use only the value
   of the minimum, which is right). `[VERIFIED: exhaustively for a ≤ 5]`
2. **Remark 3.7, eq. (7): off-by-one in the displayed derivation.** The paper writes
   "2a + 2Ω(m) ≥ 2ω(N) + 6a − 4" and concludes "Ω(m) ≥ ω(N) + 2a − 1"; the displayed line
   gives only **Ω(m) ≥ ω(N) + 2a − 2**. No parity gain is possible (both sides are even).
   **Consequence: Corollary 1.11, as proved, supports only N < 5·6^((2^{K−2a+2}−1)²)** —
   weaker than the statement. The original statement may be true, but it would require
   improving Theorem 1.10; until then, use ONLY the corrected version. `[VERIFIED: in the
   v5 text via arxiv.org/html/2404.00624v5, by two independent readings + algebra
   re-derived in this phase]`
3. **Typo in Case 12 of Theorem 1.2:** the printed factor 381/361 = I(19²) should be
   I(23²) = 553/529; redoing the computation with the right value, the conclusion of the case stands.

### 10.2 arXiv:2412.02701 (v4) — main statement weaker than the title/abstract

Row #6 of the overview table ("upper bounds for ALL prime divisors") reproduces the
claim of the title/abstract, but Theorem 1.2 of the paper only produces bounds for the
r-th smallest prime with **2 ≤ r ≤ 5**: for r ≥ 6 the denominator of the admissibility
threshold becomes negative (X₆ = 82944/85085 < 1, verified with exact arithmetic) and no
admissible pair (A,B) exists — the method does not close.
**Suggested correction for the table:** "parametric family of bounds for the r-th
smallest prime divisor, effective for 2 ≤ r ≤ 5 (includes q₅, new; better constants for
q₃, q₄ than #5); r ≥ 6 out of the method's reach".

### 10.3 Ward 2008 — minor numbering erratum

The printed list of properties ends at item 6, but the proof cites "6 and 7"; "property 7"
(monotonicity of I(p^e) with supremum p/(p−1)) exists in the running text, unlabelled.
No mathematical impact; cite properties by statement, not by number.

### 10.4 Internal note (fixed in this phase)

The first version of this phase's script `limite_inferior.py` stated that "the known
congruences do not raise the bound", omitting that Thm 1.9 of 2404.00624 invalidates the
minimal configuration (a factor 49 available). Detected by the adversarial pass; fixed
(Theorem E′). Recorded for methodological honesty.

**No divergence between our computations and the MAIN RESULTS of the literature**: all
re-verified constants and inequalities matched; the defects above are local and topple no
theorem used as a hypothesis in this project (in particular ω(N) ≥ 10 remains intact).

## 11. Proposed targets for Phase 1

Three concrete targets, in order of recommendation:

### Target 1 — Certified tree-search engine + automatic reproduction of ω ≤ 7
**What:** implement in `core/` the tree search over signatures (pᵢ, 2eᵢ) with the three
pruning mechanisms already mapped in the literature: (a) lower pruning — the minimal
configuration divides N, I(config) > 9/5 kills the branch; (b) upper pruning — ∏ p/(p−1) < 9/5
kills the branch; (c) **divisibility propagation** — σ(p^{2a}) | σ(N) = 9N/5 forces new
primes (Theorems 1.3/1.7 and Lemma 2.1 of 2404.00624, all by multiplicative order, exact).
Validation: reproduce automatically ω ≥ 6 (Ward, incl. the case {7,11,13,23}) and the 19
chains of ω ≥ 7 (2404.00624). Quantitative goal: **certified lower bound for the least
friend of 10 ≥ 10³⁰** (beating the uncertified OEIS claim).
**Estimated effort:** 2–4 sessions. Low risk; deliverable verifiable by tests.

### Target 2 — Attack ω(N) ≥ 11 by Thackeray's method
**What:** replicate the DFS of 2310.15900 (exact rational pruning, Prop. 3 with
t_min = t_max = 9/5) using the engine of Target 1 + Cor. 7 (v₅(N) ≤ (ω−1)² + 1) + special
primes (31, 19531). The bottlenecks are already mapped in the reading note: the cases
v₅ ∈ {2, 6, 10, 12, 46} where σ(5^{v₅}) is prime; v₅ = 46 would require an analogue of
Prop. 9 for a 33-digit prime. Realistic sub-goal: close systematically the cases (k, v₅)
for k = 10 and **quantify** the v₅ = 46 wall (even if ω ≥ 11 does not come out, the map of
the residual cases is publishable as a note).
**Estimated effort:** 3–6 sessions, exploratory. Medium-high risk; partial failures go to
FAILURES.md with the exact case that resisted.

### Target 3 — Harvest of small new corollaries (with novelty search)
**What:** three low-hanging fruits identified in the readings, each requiring a written
proof + adversarial pass + novelty search before any claim:
(i) the q₅ bound (r = 5 admissible in 2412.02701 v4, not made explicit in the paper; and
the independent sketch q₅ < p_{28ω} in the note on 2404.05771); (ii) the sharp instances
at ω = 10: q₂ < 89, q₃ < 191, q₄ < 421, q₅ < 1847 — cross them with the engine of Target 1
to raise Theorem E′; (iii) communicate to the authors (or record in a note) the
corrections of section 10 (Lemma 2.3, Remark 3.7/Cor. 1.11, r ≥ 6 in 2412.02701) — a
real and cheap contribution to the niche.
**Estimated effort:** 1–2 sessions. Low risk.

**Recommendation:** Target 1 first (it is a prerequisite of 2 and boosts 3.ii); Target 3
can run in parallel since it is cheap. Phase 3 (the 2p family) gained two candidate uniform
lemmas from the readings (Thackeray's Cor. 6 for odd squares; Thm 1.5 of 2504.08295
generalised as N > d(N)²/r²) — recorded for when Phase 3 opens.

## 12. Execution log

Environment: Windows 11, Python 3.13.2, local venv; sympy 1.14.0, pytest 9.1.1, mpmath 1.3.0.

```
> pytest -q                                   # initial suite (7 original tests)
7 passed in 0.65s

> pytest -q                                   # final suite (with tests/test_fase0_proofs.py)
17 passed in 556.85s (0:09:16)                # the suite is slow on purpose (exhaustive
                                              # exact sweeps); run in the background

> python experiments/busca_direta.py --limite 2000000
Intervalo varrido: [1, 2000000]
n com I(n) = 9/5: [10]
[VERIFICADO-NUMERICAMENTE] Nenhum amigo de 10 no intervalo.

> python experiments/busca_estrutural.py --limite-m 1000000
Espaço varrido: N = m^2, m ímpar múltiplo de 5, m <= 1000000
(cobre candidatos estruturais até N = 1.00e+12)
[VERIFICADO-NUMERICAMENTE | condicional a Ward] Nenhum amigo no espaço varrido.

> python experiments/limite_inferior.py
Produto dos 10 primos: 1236789689135
LIMITE BASE:   N >= 1529648735150649937048225      (25 dígitos, ~1.5296e+24)
LIMITE AFIADO: N >= 74952788022381846915363025     (26 dígitos, ~7.4953e+25)
(rótulos e comparações na saída completa do script)
```

(The script outputs above are quoted verbatim; the scripts themselves still print in
Portuguese pending the code-side migration.)

Review (reproducibility of the non-computational part): 9 reviewers on the
literature/web front and 9 in the adversarial pass, with full records of the searches and
verdicts. Every computation cited as evidence is in versioned scripts in this repo; the
reviewers' extra sweeps (10⁷/10⁸/2.25·10¹⁰) are unversioned reinforcement and are
recorded as such in section 5.

**Phase 0 closed. Phase 1 opens after review of this report.**
