# ERRATA — verified defects in the literature on friends of 10 and 20

Catalogue of the defects found in the literature, **re-verified from scratch on
2026-08-21** (second pass, independent of Phase 0) directly against the published
text, and certified by `experiments/verifica_erratas.py` + `tests/test_erratas.py`.

Publication material: `publication/errata_friends_of_10.tex` (the note) and
`publication/SUBMISSION_GUIDE.md` (procedure). Entry E6 was added on 2026-11-11
(Phase 1, Block 8) and is not yet in that note.

## Exact sources checked in this pass

| Tag | Paper | Version read | Editorial status |
|---|---|---|---|
| P1 | Chatterjee, S. Mandal, S. Mandal, *A note on necessary conditions for a friend of 10* | arXiv:2404.00624**v5** (17 Jan 2025), LaTeXML HTML | **preprint** (no journal-ref on arXiv as of 2026-08-21) |
| P2 | idem, *On Characterizing Potential Friends of 20* | arXiv:2409.04451**v4** | **published**: Ann. West Univ. Timisoara — Math. Comput. Sci. 61(1) (2025) 205–229 |
| P3 | S. Mandal, *Prime Divisors of 10's Friends: A Generalization of Prior Bounds* | arXiv:2412.02701**v4** (16 Oct 2025) | **published**: Analele Univ. Oradea Fasc. Mat. 33(1) (2026) 5–12 |
| P4 | S. Mandal, *Exploring the Relationships Between the Divisors of Friends of 10* | arXiv:2504.08295v1 | published: News Bull. Calcutta Math. Soc. 48(1–3) (2025) 21–32 — **inherits** defect E3 (cites Cor. 1.11 in its original form) |
| P5 | H. R. Thackeray, *Each friend of 10 has at least 10 nonidentical prime factors* | read on **2026-11-11** (Block 8, not in the 2026-08-21 pass): arXiv:2310.15900**v2** (28 Mar 2024, the current version), PDF text and ar5iv HTML; the statement and the proof step of E6 read the same in **v1** (24 Oct 2023) and in the published PDF (statement p. 600, proof step p. 601) | **published**: Indag. Math. 35(3) (2024) 595–607, doi:10.1016/j.indag.2024.04.011 (open-access copy in the University of Pretoria repository, UPSpace) |

Method of this re-verification: download of the arXiv HTML, extraction of the LaTeX
from the `alttext` attributes (character-by-character check of the cited statements)
and recomputation of all arithmetic with `int`/`Fraction`. No float supports any claim.

---

## E1 — [P1] Lemma 2.3 = [P2] Lemma 23: **false as stated** `[PROVED]`

**Paper's text (verbatim):** "Let (c₁,…,c_k) be any partition of n … then for any
integer a > e we have `an < Σ a^{c_i}`", with step (1) of the proof "`ac_i < a^{c_i}`
for each c_i ≥ 1".

**Defect:** ψ(x) = ax − a^x is strictly decreasing on [1,∞) for a > e, but
ψ(1) = 0 — hence `ac ≤ a^c` with **equality** at c = 1. For the all-ones partition
`a·n = Σ a^{c_i}` holds. Smallest counterexample: n = 1, a = 3 (3 = 3).

**Correction:** `a·n ≤ Σ a^{c_i}`, with equality **iff** every c_i = 1.

**Consequence:** none for the final results. Lemma 3.6 [P1] / Lemma 24 [P2]
("the minimum of L_{2a−1,5} is 8a−4") has a **correct statement**, but the displayed
proof concludes a **strict** inequality — which would deny that the minimum is attained.
The papers themselves record, in the note right after the proof, that the minimum lies
in A_{2a−1,5}(2a−1), that is, exactly in the equality case: an **internal contradiction
in the text**, resolved by the corrected version of the lemma.

**Certificate:** `verifica_erratas.py --bloco e1` (396 partitions, 3 ≤ a ≤ 8, n ≤ 8:
every violation of the strict form is an equality and all occur at the partition (1,…,1))
and `--bloco e2` (minimum 8a−4 attained, a = 1..7).

---

## E2 — [P1] Remark 3.7, eqs. (7) and (8): **off-by-one** `[PROVED]`

**Paper's text (verbatim):** "Since Ω(N) ≥ 2ω(N)+6a−4, … Ω(5^{2a}) + Ω(m²) =
2a + 2Ω(m) ≥ 2ω(N) + 6a − 4 i.e; **Ω(m) ≥ ω(N) + 2a − 1** (7)"; and from there
"**Ω(m) ≥ ω(m) + 2a** (8)".

**Defect:** from the displayed line follows 2Ω(m) ≥ 2ω(N) + 4a − 4, that is
**Ω(m) ≥ ω(N) + 2a − 2**. Both sides are even — there is no parity gain to extract.
Since 5^{2a} ‖ N implies 5 ∤ m and ω(N) = ω(m) + 1, the correct form of (8) is
**Ω(m) ≥ ω(m) + 2a − 1**.

**The gap cannot be closed by the paper's own argument:** to obtain (7) one would need
Ω(N) ≥ 2ω(N) + 6a − 2, but the value 2ω(N) + 6a − 4 is the **exact optimum** of the
relaxation used in the proof of Theorem 1.10 (Proposition in `publication/`): the
configuration with 2a−1 primes ≡ 1 (mod 10) of exponent 4 and all others of exponent 2
satisfies every constraint employed and attains the bound. If (7) is true, it requires
a new argument.

**Evidence that it is an isolated slip:** in [P2] (friends of 20) the analogous passage
is **correct**: from Ω(N) ≥ 2ω(N)+6a−5 with N = 2·5^{2a}m² comes 1 + 2a + 2Ω(m) ≥ 2ω(N)+6a−5,
hence Ω(m) ≥ ω(N) + 2a − 3 — exactly the integer consequence.

**Certificate:** `verifica_erratas.py --bloco e3` (optimum of the relaxation = 2ω+6a−4
over 48 pairs (a, ω)) and `--bloco e4` (152 integer witnesses satisfying the displayed
inequality and violating eq. (7)).

---

## E3 — [P1] Corollary 1.11: exponent weakens from K−2a+1 to **K−2a+2** `[PROVED]`

**Paper's text:** "Since Ω(m) ≤ K, we have from (7) that K − 2a + 1 ≥ ω(N)", whence
`N < 5·6^{(2^{K−2a+1}−1)²}`.

**Correction (direct consequence of E2):** from (7′) comes ω(N) ≤ K − 2a + 2, so what
the proof supports is

> **N < 5·6^{(2^{ω(N)}−1)²} < 5·6^{(2^{K−2a+2}−1)²}.**

**Propagation:** [P4] (arXiv:2504.08295, §1) cites Corollary 1.11 in its original form —
the same substitution applies there.

---

## E4 — [P3] Theorem 1.2: effective only for **2 ≤ r ≤ 5** `[PROVED]`

**Paper's text:** title and abstract promise "upper bounds for **each** of the prime
divisors of a friend of 10"; Theorem 1.2 holds under the condition
`A/B > 1 / ( (36/25)·∏_{4≤i≤r+1}(1 − 1/p_i) − 1 )`.

**Defect:** writing X_r = (36/25)·∏_{4≤i≤r+1}(1 − 1/p_i), the final step of the proof
requires `1 + B/A < X_r`; since `1 + B/A > 1` for A, B > 0, this is possible only if
**X_r > 1**. And X_r is strictly decreasing with

| r | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|
| X_r | 36/25 | 216/175 | 432/385 | 5184/5005 | **82944/85085 < 1** |

Hence, for r ≥ 6: in the intended reading (positive threshold, which is the one used in
the paper's own instantiations — 25/11, 175/41, 385/47 are exactly 1/(X_r − 1)) **no
admissible pair (A,B) exists**; in the literal reading (negative threshold ⇒ empty
condition) the proof does not support the conclusion, since already the fixed part
F_r = (5/4)·∏_{4≤j≤r+1} p_j/(p_j−1) satisfies F_r ≥ 9/5 for r ≥ 6 (F_6 = 17017/9216 > 9/5)
— the contradiction does not close for any choice of tail primes. In both readings:
**no bound for q_r with r ≥ 6**.

**Suggested correction:** restrict title/abstract/statement to "the r-th smallest prime
divisor, for 2 ≤ r ≤ 5". Nothing else in the paper is affected (Thm 1.1 and Cor. 1.1 use r ≤ 4).

**Available bonus, not stated:** for r = 5 the threshold is 5005/179, so
(A,B) = (113,4) is admissible and the sharp form of the proof gives `q_5 < p_{⌈113·ω(n)/4⌉}`;
with ω(n) = 10, `q_5 < p_283 = 1847`.

**Minor errata in the same paper:** "From (3) and (4)" should read "From (1) and (4)";
the `A > B > 1` invoked in Remark 1.1 follows from the hypotheses only when 1/(X_r − 1) > 1,
that is, in the same range 2 ≤ r ≤ 5.

**Certificate:** `verifica_erratas.py --bloco e5` (exact X_r and F_r for 2 ≤ r ≤ 12,
identity F_r·X_r = 9/5, non-existence of (A,B) for r ≥ 6).

---

## E5 — [P1] Case 12 of Theorem 1.2: misprint, no consequence `[PROVED]`

The chain of Case 12 is 5, 7, 11, 13, **23**, p₆, but the last factor printed in the two
inequalities is 381/361 = I(19²), in place of I(23²) = 553/529. Recomputing exactly:
I(5⁴·7²·11²·13²·23²) = 1111642101/614631875 > 9/5 and
I(5²·7²·11²·13²·23²·31²) = 15547332483/8383578775 > 9/5 — the conclusion of the case
stands.

**Certificate:** `verifica_erratas.py --bloco e6`.

---

## E6 — [P5] Corollary 6: the hypothesis is too weak as printed `[PROVED]`

**Paper's text (verbatim):** "Let n be some odd square such that ω(n) = k > 1. Let r be
some prime factor of gcd(n, σ(n)). Let c be a nonnegative integer such that
Σ v_r(q^{o_r(q)} − 1) ≤ c [sum over the primes q | n with gcd(r, q(q−1)) = 1 and
o_r(q) | v_q(n) + 1]. Suppose that each prime factor q of n such that q > r satisfies
v_q(σ₋₁(n)) = 0. It follows that v_r(n) ≤ (k − 1)² + c − v_r(σ₋₁(n))."

**Defect:** the proof takes the primes q_{r^i} (i = 1, …, b) that Proposition 5 finds in
σ(q^{v_q(n)}), notes that q_{r^i} > r, and concludes "so v_{q_{r^i}}(n) =
v_{q_{r^i}}(σ(n)) > 0". That step uses v_{q′}(σ₋₁(n)) = 0 for q′ = q_{r^i}, which the
hypothesis grants only to the prime factors of n. The q_{r^i} are prime factors of σ(n);
nothing makes them divide n.

**Counterexamples** (exact; the hypotheses hold as printed, the conclusion fails):

- n = 11²·5⁶⁰⁴, k = 2, r = 11. 11 divides n and σ(n). The only term of the sum is q = 5
  (o₁₁(5) = 5 divides 605): v₁₁(5⁵ − 1) = 1, so c = 1. No prime factor of n exceeds 11,
  so the hypothesis is vacuous. v₁₁(σ(n)) = v₁₁(5⁵ − 1) + v₁₁(605/5) = 3, hence
  v₁₁(σ₋₁(n)) = 1 and the bound is (k − 1)² + c − 1 = **1**, while v₁₁(n) = **2**. The
  primes the proof needs, 12207031 = Φ₁₁(5) and a prime of Φ₁₂₁(5), divide σ(n) and not n.
- n = 13²·3⁵⁰⁶, r = 13: the same with o₁₃(3) = 3, 507 = 3·13², the prime 797161 = Φ₁₃(3);
  bound 1, exponent 2.

**Correction:** impose the hypothesis on **every prime q > r**, not only on the prime
factors of n. More generally, with no hypothesis on σ₋₁(n) at all: if e primes ≡ 1 (mod r)
divide σ(n) without dividing n, the same proof gives b ≤ k − 2 + e (the b primes q_{r^i}
are neither r nor q) and v_r(n) ≤ (k − 1)(k − 2 + e) + c − v_r(σ₋₁(n)).

**Consequence:** none for the results of [P5]. For a friend of 10, σ₋₁(n) = 9/5, so
v_q(σ₋₁(n)) = 0 for every prime q > 5: the repaired hypothesis holds, and Corollary 7
(v₅(n) ≤ (k − 1)² + 1) and the theorem ω(n) ≥ 10 stand. The defect matters when
Corollary 6 is reused for another abundancy index, as its general wording invites: the
primes of the numerator of σ₋₁(n) that are ≡ 1 (mod r) have to be counted. The recursive
certifier of this project does count them (witnesses in C ∪ primes(num):
`core/omega_k.py`, `_cota_expoente_conhecido` and `_faixa_a1`; results/PHASE_1.md, Block
8), and its own counts, which rest on the counting argument of the printed proof, show
what happens without them. Its finite exponent bound, at the node where every prime of n
is known and only v₅(n) is fixed, is attained (it equals 2) for the planted friends
5²·7²·29⁶, 5²·11²·23¹⁰, 5²·7²·43⁶ and 5²·13²·53¹² (exponent of 7, 11, 7 and 13) only
because a prime of the numerator of I(n) witnesses a level; with the witnesses
restricted to the prime factors of n, as in the printed proof, it would be 1
(`tests/test_planted.py::test_exponent_bound_counts_the_primes_of_num_as_witnesses`),
although end to end these four friends are still found. This is a defect of the formula,
not a friend lost by the certifier: on the path of a friend the certifier evaluates this
bound only at nodes with two unknowns (with one unknown U the bound needs lo ≥ B_min,
while B_min ≥ U > lo; with three or more there is no bound L), and no planted friend is
known to be lost end to end through it with the witnesses restricted that way. Its range
of v₅(n), the same count at r = 5, loses five of the planted friends of
`tests/test_planted.py` end to end without those witnesses: 5²·11⁴, 5²·11²⁴·31⁴,
5¹⁶·7²·461⁴, 5¹⁶·7²·521⁴ and 5²·7²·13²·17²·19²·41⁴ (mutant `a1max_no_e5` of
`experiments/planted_mutations.py`). None of these nine n is an instance of the printed
corollary at the prime in question (r = 7, 11, 7 and 13 for the first four, r = 5 for the
other five): its hypothesis fails there (e.g. v₂₉(σ₋₁(5²·7²·29⁶)) = −6), and its printed
bound (k − 1)² + c − v_r(σ₋₁(n)) holds there (it is 5 for the first four). At another
prime the printed corollary can apply: for 5²·11²⁴·31⁴ and r = 31 its hypothesis holds
vacuously and its bound holds (8 against v₃₁(n) = 4).

**Certificate:** `verifica_erratas.py --bloco e7` (the script's blocks are numbered
by its own history: block e5 certifies E4, e6 certifies E5, e7 certifies E6);
`tests/test_erratas.py::test_corollary_6_of_thackeray_is_false_as_printed`.

---

## What is NOT in question

- ω(N) ≥ 7 for a friend of 10 (Theorem 1.2 of [P1]) — intact.
- ω(N) ≥ 10 (Thackeray, arXiv:2310.15900) — intact, and independent of [P1]–[P3]. E6
  concerns only the generality of that paper's Corollary 6; for friends of 10 its
  hypothesis holds in the repaired form.
- Theorem 1.10 of [P1] (Ω(N) ≥ 2ω(N)+6a−4) — **true**; only the proof of the auxiliary
  lemma needs the corrected form (E1). It is in fact optimal (not improvable by the
  argument).
- Theorems 1, 2, 3 of arXiv:2404.05771 (bounds for q₂, q₃, q₄) and Cor. 1.1 of [P3] —
  intact.
- We do not claim that the statements (7), (8), Cor. 1.11 and Thm 1.2 of [P3] for r ≥ 6
  are **false**: since no friend of 10 is known, conditional statements of this kind
  cannot be refuted by counterexample. What is proved here is that **the given proofs do
  not establish them** (and, in the case of (7), that the argument used cannot establish
  them). The demonstrated falsities are those of Lemma 2.3/23 (E1), a self-contained
  statement about partitions, and of Corollary 6 of [P5] as printed (E6), which is not
  conditional on a friend of 10 and has explicit counterexamples.

## Novelty search (rigour rule #4)

Done on 2026-08-21: arXiv (complete listing of the papers of Sagar Mandal and the group,
via the API), web search for an erratum/corrigendum to 2404.00624 and 2412.02701, and
verification that the current arXiv versions (v5 of Jan 2025 and v4 of Oct 2025,
respectively) still contain the defects. **No published erratum found.** The later paper
[P4] repeats Corollary 1.11 in its original form, which indicates the defect went
unnoticed. Record a fresh search immediately before any submission.

For E6, done on 2026-11-11: arXiv listing of 2310.15900 (v2 of 28 Mar 2024 is the current
version, "minor revision as per journal peer review"; the statement is the same in the
PDF and in the ar5iv HTML) and a web search for an erratum or corrigendum to the paper.
**None found.** The statement and the proof step of E6 are the same in v1, in v2 and in
the published version (Indag. Math. 35 (2024), statement on p. 600, proof step on
p. 601), so the defect is in the journal text as well.
