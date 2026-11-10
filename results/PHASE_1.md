# Phase 1 — A certified computational frontier

Opened on 2026-08-20 after the closing of Phase 0. This file is the running report of
the phase; block by block, with a checkpoint between blocks.

Script outputs quoted below are verbatim; the scripts themselves still print in
Portuguese pending the code-side migration.

---

## Block 1 — Certified tree-search engine (Target 1 of the Phase 0 proposal)

### 1.1 What was built

`core/motor.py` — tree search over prime signatures (pᵢ, aᵢ) of a hypothetical friend
N of 10, using ONLY labelled facts:

- **Search space** (Theorems A–D of Phase 0, `[PROVED]`): N = ∏ pᵢ^{aᵢ} with
  5 = p₁ < p₂ < ⋯ < p_k, every pᵢ ≥ 5, every aᵢ even ≥ 2.
- **MIN-PRUNE**: if ∏_{chosen} I(p²) ≥ 9/5 and slots remain, every completion has
  I > 9/5 (exponents ≥ 2, I increasing in the exponent, extra prime factor > 1). Cut.
- **MAX-PRUNE**: I(N) < ∏ p/(p−1) (strict, Lemma 3 of Phase 0); bounding the remaining
  primes above by the smallest available ones (monotonicity: larger prime ⇒ smaller
  p/(p−1)), if the bound is ≤ 9/5, cut. The bound is non-increasing in the next
  candidate prime, which justifies ending the candidate loop once it drops to ≤ 9/5.
- **CLOSURE** (finiteness of the exponents in a complete set S): σ(p^a) =
  ∏_{d | a+1, d>1} Φ_d(p) divides σ(N) = 9N/5, whose prime factors lie in S ∪ {3};
  for odd d ≥ 3 and p ≥ 5, Zsygmondy (no exceptions in this regime) gives a primitive
  prime q | Φ_d(p) with ord_q(p) = d, hence d | q−1 and d ≤ max(S)−1 (q = 3 is
  impossible for odd d ≥ 3, since ord₃ ∈ {1,2}). Thus a+1 can only be an odd m ALL
  of whose divisors > 1 belong to D(p,S) = {odd d ≤ max(S)−1 : factors of Φ_d(p) ⊆ S∪{3}}
  — a finite, computable set. It is the automation of Ward's "31 trick".
- **Structural honesty**: a branch whose prime iteration does not close by index
  pruning (∏_{chosen} p/(p−1) ≥ 9/5) raises `RamoNaoLimitado` — the engine refuses to
  certify rather than terminate falsely.
- **Bounded variant** (`busca_limitada`): adds the ceiling N ≤ B; since exponents
  are ≥ 2, ∏ primes ≤ √B (an integer product ceiling), which bounds primes and
  exponents and guarantees termination without closure; every surviving signature
  is tested against the exact equality 5σ(N) = 9N.

Tests: `tests/test_motor.py` (9 tests) and `tests/test_motor_crosscheck.py`
(4 tests, references 100% independent of sympy) — cross-check of σ/I; CLOSURE
against brute force (soundness AND completeness in the tested range, including
without sympy); reproduction of Ward's structure; `RamoNaoLimitado` at ω = 6;
**completeness test with a planted target** (monkeypatch of the target to I(N₀),
N₀ = (5·7·11)²: the engine MUST find the signature of N₀ — and does, exactly once);
exact equivalence shard-union vs full sweep (1 and 2 levels); exponent enumeration
count against independent brute force; own sieve vs primerange/nextprime; trial-division
factorisation of the whole Φ_d(5) surface of the certificate.

### 1.2 Result 1 — independent reproduction of Ward: ω(N) ≥ 6

`python experiments/elimina_omega.py --k-max 6`:

| ω | Outcome | Detail |
|---|---|---|
| 1 | eliminated | {5} killed by CLOSURE (σ(5^a) would require 31, 11·71, 19531, … ∉ {5}) |
| 2–4 | eliminated at the root | MAX-PRUNE: ∏ p/(p−1) of the smallest primes ≤ 9/5 (for ω=4: 1001/576 < 9/5, Ward's bound) |
| 5 | eliminated | only {5,7,11,13,q}, q ∈ {17,19,23} survive; all three die by CLOSURE at p = 5 — no valid exponent (the case q = 23 is exactly the one where Ward's manual proof needs the trick σ(5²) = 31) |
| 6 | **not certified** | `RamoNaoLimitado` at [5,7,11,13,23]: ∏ p/(p−1) = 2093/1152 ≥ 9/5 — index pruning does not bound the 6th prime; requires divisibility propagation (Block 2) |

> **Every friend of 10 has ω(N) ≥ 6.**
> `[PROVED-CONDITIONAL: Theorems A–D and Lemmas/Fact 0 of Phase 0 + Zsygmondy and
> the cyclotomic identity (classical) + correctness of the engine (§1.5) + correctness
> of sympy in the calls consumed (re-verified without sympy in
> tests/test_motor_crosscheck.py)]` — independent reproduction of Ward 2008; < 0.1 s.

The honest frontier of the pure index method is documented: ω = 6 is exactly where
the literature (2404.00624) needed divisibility chains.

### 1.3 Result 2 — certified bound: no friend of 10 up to 10³⁰

Logical frame (all exact, in `experiments/cota_certificada.py`):

1. Friend N ≤ B ⟹ ∏ primes of N ≤ √B (even exponents ≥ 2, `[PROVED]`).
2. (∏ of the k smallest primes ≥ 5)² > B ⟹ no friend N ≤ B has ω ≥ k.
   For B = 10³⁰: k_ceiling = 12, hence ω ∈ {10, 11} (using ω ≥ 10 from arXiv:2310.15900).
3. `busca_limitada(k, B)` sweeps ω = k with N ≤ B exhaustively (termination by the
   product ceiling; exact equality tested at each signature).

Run with the block's final code (B = 10³⁰): ω = 10 swept in ~11 s —
712 341 nodes, 393 158 complete sets, **400 135 signatures tested for exact
equality, zero friends**; ω = 11 swept in < 0.01 s (no set survives the prunings).

*Reproducibility note (rule 7; pointed out by the adversarial pass):* an intermediate
version of the engine, without the leaf index prunings, produced for the same B the
same 712 341 nodes but 649 083 tested signatures (a superset of the final version's
space; also zero friends) — the reviewers reproduced both behaviours exactly by
switching the leaf prunings on/off. The numbers in this section are those of the code
versioned in this commit. Therefore:

> **The least friend of 10, if it exists, exceeds 10³⁰.**
> `[PROVED-CONDITIONAL: Theorems A–D + ω(N) ≥ 10 (arXiv:2310.15900) + correctness of
> the engine (section 1.5)]`

Context: the literature (conclusion of arXiv:2404.00624, citing OEIS A074902) claimed
"least friend > 10³⁰" **without a published certificate**. This result certifies the
claim — and the block tries to beat it (B = 10³², section 1.4).

### 1.4 Pushing the frontier: B = 10³¹ and B = 10³²

**B = 10³¹ certified in one piece** (101.9 s with the final code; ω ∈ {10,11,12} by the
product rule): ω = 10 with 5 891 561 nodes and 4 065 923 signatures tested, zero
friends; ω = 11 and 12 die in the prunings. Same conditional label as for 10³⁰.

Cost grows ~10× per decade of B (measured: 10.8 s → 107.9 s). For B = 10³² the sweep of
ω = 10 was **sharded by ranges of the 2nd prime** — explicit partition {7}, {11–13},
{17–31}, {37–∞} (covers [7, ∞); the internal product ceiling bounds p₂ anyway) — with
shards in parallel. Soundness of the sharding: the filter acts only at the depth of the
2nd prime and the prunings are monotone in the candidate (independent of the filter);
the test `test_shards_por_p2_cobrem_exatamente_a_varredura_inteira` confirms that the
union of the shards tests EXACTLY the same signatures as the full sweep (nothing missing,
nothing extra) at a test B.

**B = 10³² certified by union of shards** (possible ω: {10, 11, 12}, since
(∏ of the 13 smallest primes ≥ 5)² > 10³²):

| Shard | Nodes | Signatures tested | Friends |
|---|---:|---:|---:|
| ω=10, p₂=7, p₃=11 | 11 271 609 | 7 402 508 | 0 |
| ω=10, p₂=7, p₃=13 | 16 656 681 | 12 646 158 | 0 |
| ω=10, p₂=7, p₃=17 | 7 602 865 | 7 122 447 | 0 |
| ω=10, p₂=7, p₃∈[19,23] | 691 426 | 864 031 | 0 |
| ω=10, p₂=7, p₃≥29 | 2 | 0 (MAX-PRUNE at the shard root) | 0 |
| ω=10, p₂∈[11,13] | 5 602 546 | 6 475 561 | 0 |
| ω=10, p₂∈[17,31] | 1 | 0 (MAX-PRUNE) | 0 |
| ω=10, p₂≥37 | 1 | 0 (MAX-PRUNE) | 0 |
| ω=11 (whole) | 17 777 | 3 633 | 0 |
| ω=12 (whole) | 13 | 0 (prunings) | 0 |
| **Total** | | **34 514 338** | **0** |

Coverage of the partition: p₂ > 5 ⟹ p₂ ≥ 7, and {7} ∪ [11,13] ∪ [17,31] ∪ [37,∞) covers
[7,∞); within p₂ = 7, p₃ > 7 ⟹ p₃ ≥ 11, and {11} ∪ {13} ∪ {17} ∪ [19,23] ∪ [29,∞)
covers [11,∞). The shards with 0 signatures die by MAX-PRUNE for a verifiable
mathematical reason (e.g. p₂ ≥ 17 ⟹ I < (5/4)(17/16)·∏ sup of the 8 smallest primes > 17 < 9/5).

Reproducibility (rule 5): each row of the table was produced by
`python -u experiments/cota_certificada.py --log10-bound 32 --somente-k K
[--prefixo-intervalos ...]` with the code of this commit (the light shards and ω = 11/12
were re-run after the adversarial round to guarantee this; identical numbers). The
script `experiments/shards_10e32.py` reproduces the WHOLE partition sequentially and
verifies the coverage of the partition programmatically before sweeping (run in this
session: "particao de shards verificada"). Shard-union vs full-sweep equivalence
covered by a test (`test_shards_por_p2_cobrem_exatamente_a_varredura_inteira`).

> **The least friend of 10, if it exists, exceeds 10³².**
> `[PROVED-CONDITIONAL: Theorems A–D + ω(N) ≥ 10 (arXiv:2310.15900) + correctness of
> the engine (section 1.5)]` — 100× beyond the uncertified OEIS claim (10³⁰).

Cost to go further: ~10×/decade in CPU (10³⁴ ≈ 3 h sharded; 10³⁶ ≈ 30 h). Before
spending that, it is worth porting the hot loop to pure integers/PyPy or using the
congruence prunings of Block 2 — a decision for the next checkpoint.

### 1.5 Adversarial pass on the engine

Five independent reviewers, instructed to BREAK the certifications — they rebuilt the
monotonicity proofs, planted ~300 synthetic targets, reimplemented the closure without
sympy and re-ran the experiments:

| Target | Verdict | Summary |
|---|---|---|
| Index prunings + loop termination | **SOUND** | monotonicity of the bound proved; strict/non-strict correct at every point (including the leaf); RamoNaoLimitado is exactly the negation of termination; 30 all-2 targets (equality case) all found |
| CLOSURE (Zsygmondy + cyclotomics + filter) | **SOUND** | identity σ(p^a) = ∏Φ_d(p) verified; no Zsygmondy exceptions in the regime; q = 3 is never primitive (ord₃ ∈ {1,2}); 134 cases (p,S) against brute force: exact equality; closure re-verified by hand on Ward's 3 sets |
| Completeness of the enumeration | MINOR_GAP (process only) | ~260 planted targets all found exactly 1×, including edges (N = bound, prime at the list boundary, high exponents, shards); no live branch cut |
| Logical frame of the certificates | MINOR_GAP (process only) | k = 5 enumeration checked WITHOUT the engine (brute force + monotonicity); exact k_maximo; labels needed to declare Zsygmondy/Lemmas/sympy — **fixed** |
| Hidden dependencies (sympy, caches, floats) | MINOR_GAP (process only) | instrumented replay of both certificates with verifying wrappers: ALL sympy calls consumed by the certificates re-verified by own implementations (sieve, Miller–Rabin, Pollard-rho, cyclotomic via Möbius) — no wrong value; zero floats on any decision path; caches safe |

**No mathematical problem found.** Process problems pointed out and fixed in this
same block:

1. *Statistics of §1.3 generated by an earlier version of the engine* → section
   regenerated with the final code; divergence recorded (rule 7).
2. *Phase 1 without a commit / 10³² shards without a versioned script* → commit of this
   block; reproducible partition in `experiments/shards_10e32.py`, with programmatic
   verification of the partition's coverage (ω ∈ {10,11,12}; p₂ partitions [7,∞);
   p₃|p₂=7 partitions [11,∞)); light shards re-run with the final code.
3. *Tacit hypothesis of sympy's correctness* → declared in the labels; factorisation
   surface of the ω ≥ 6 certificate (Φ_d(5), odd d ≤ 21) re-factored by pure trial
   division in `tests/test_motor_crosscheck.py`; own sieve vs primerange/nextprime;
   cyclotomic and telescoping identities.
4. *Common-mode failure in the closure test* (the reference used the same factorint) →
   `test_fecho_dos_tres_conjuntos_de_ward_sem_sympy` re-derives the killing of Ward's 3
   sets with 100% own factorisation.
5. *`test_lema3` of Phase 0 costing minutes* (trial division up to p¹²) → reference
   replaced by a direct sum of powers (the divisors of p^e are p⁰..p^e by unique
   factorisation) — independence kept, trivial cost.
6. Cosmetics: docstring of `elimina_omega.py` (k = 1 dies by closure, not by index; and
   only {5,7,11,13,23} needs the closure — in the other two the leaf min-prune would
   suffice), dead import, assert → raise, exception message in ASCII (avoids
   UnicodeEncodeError on a cp1252 console), the ω ≥ 10 condition embedded in the
   certificate sentence.

With that, the labels of sections 1.2–1.4 hold with the adversarial pass completed.

### 1.6 Next steps of the block / phase

- Block 2: divisibility propagation (Theorems 1.3/1.7 and Lemma 2.1 of 2404.00624,
  Remark 3.1 — "chains") to close ω = 6 and ω = 7 automatically; then Thackeray's
  method (Cor. 6/7 + special primes) toward ω ≥ 11 (Target 2).
- Harvest of corollaries (Target 3) in parallel when cheap.

---

## Block 2 — Divisibility chains: ω(N) ≥ 7

### 2.1 New tools (`core/cadeias.py`)

Mathematical basis labelled in the module header. Pieces, all exact and tested
(`tests/test_cadeias.py`, 8 tests):

- **Valuation formula** (Lemma 2.1 of arXiv:2404.00624 = Nielsen/Voight, via LTE):
  v_q(σ(p^a)) by multiplicative orders, without factoring anything; tested exhaustively
  against direct valuation (p, q ≤ 37, a ≤ 20).
- **f_p^q** (Thm 1.3 of 2404.00624): reproduces the 12 samples of the paper's Table 4
  recorded in the reading note (f_31^5 = 3, f_11^5 = 5, …, f_35671^5 = 29).
- **Closure by orders** (`expoentes_validos_ordens`): replaces the cyclotomic closure of
  Block 1 — the divisors d > 1 of a+1 are orders ord_r(p) of primes r ∈ S (Zsygmondy),
  and the closure test is by RECONSTRUCTION: σ(p^a) == ∏ q^{v_q(σ(p^a))} (valuation
  formula), without factorisation. Equivalence with Block 1's cyclotomic implementation
  verified case by case (two independent methods).
- **Master-equation budgets**: ∏σ(pᵢ^{aᵢ}) = 9·5^{a₁−1}·∏pᵢ^{aᵢ} gives, exactly:
  Σ_{p≡1(3)} v₃(aᵢ+1) = 2 and Σ_{q≡1(5)} v₅(a_q+1) = a₁ − 1 (Fact 2: only order 1
  contributes modulo 3 and 5, since the other orders are even).

### 2.2 The ω = 6 certifier (`core/omega6.py`)

Stage A: enumeration of C5 prefixes (index DFS; termination because at levels 1–4 the
loop bound is ∏ p/(p−1) of ≤ 4 primes ≤ 1001/576 < 9/5). Stage B:

- **Branch (i)** (∏sup(C5) < 9/5): p₆ bounded by the index; each complete set goes to
  the exponent phase (closure by orders + budgets + exact equality).
- **Branch (ii)** (∏sup(C5) ≥ 9/5; p₆ not bounded by the index): **pinning through the
  feeding of the 5**: a₁ ≥ 2 ⟹ v₅(σ(N)) = a₁ − 1 ≥ 1 ⟹ the 5 has a feeder, and only
  bases ≡ 1 (mod 5) feed. Case some q ∈ C5 feeds: 5 | a_q+1 and 5 ∉ D_q ⟹
  ord_P(q) = 5 ⟹ P | Φ₅(q) — P pinned to the new factors (finitely many). Case only P
  feeds: P ≡ 1 (mod 10), v₅(a_P+1) bounded by the finite set E (divisors of a_P+1 divide
  q−1 for q ∈ C5∪{3}) ⟹ a₁ runs over a finite set and σ(5^{a₁}) pins P through the
  remainder of the strip by C5∪{3}. Every pinned P > p₅ becomes a complete set (same
  exhaustive phase as branch i). Detectable coverage gaps raise `NaoCertificavel`
  (honest failure, no certificate).

In the real space, **three** prefixes have ∏sup ≥ 9/5 — {5,7,11,13,17} (17017/9216),
{5,7,11,13,19} (19019/10368) and {5,7,11,13,23} (2093/1152) — but the first two die
earlier, by min-prune (∏I(p²) = 1.8238 and 1.8120, both ≥ 9/5). Only {5,7,11,13,23}
reaches the pinning — the same prefix that caused `RamoNaoLimitado` in Block 1.
(Verified: there is no order dependence — the three prefixes, if pinned, would give the
same P ∈ {31, 3221}.) The mechanical pinning gives P ∈ {3221, 31}, and the two complete
sets die in the closure. It is the exact automation of the "chains" style of argument
of 2404.00624.

**Derivation checked by hand** (independent of the code, integer arithmetic):
- *Case A*: the only q ∈ C5 with q ≡ 1 (mod 5) is 11; and 5 ∉ D₁₁, where D₁₁ is computed
  **only over the KNOWN primes** — no r ∈ C5∪{3} has ord_r(11) = 5, since that would
  require 5 | r−1. (The restriction to C5∪{3} is essential: P = 3221 ≡ 1 (mod 5) and
  ord_P(11) = 5 is precisely the *conclusion* of the argument, not a hypothesis.) Hence
  P | Φ₅(11) = σ(11⁴) = 16105 = 5 · **3221**, with 3221 prime (trial division up to 56).
  Pin: 3221.
- *Case B*: admissible odd divisors of a_P+1 (they divide q−1 for q ∈ C5∪{3}) =
  {3, 5, 11} ⟹ E = {3,5,11} ⟹ v₅(a_P+1) ≤ 1 ⟹ a₁ = 2 ⟹ σ(5²) = **31**, which is not
  in C5∪{3}. Pin: 31.

> **Cross-validation with the literature:** Table 4 of arXiv:2404.00624 (built by hand
> by the authors) records **f_3221^11 = 5** — exactly the pin that this block's
> mechanical procedure derives on its own, without consulting the table. The certifier
> rediscovers the chain the authors exhibited manually.

**Design note (honesty):** the first version of branch (ii) used exponent "ladders" with
window kills; the design had a real *straddle* case (on the 7 axis in {5,7,11,13,23},
∏sup is within 1.5·10⁻⁵ of 9/5 and no kill fires) and was replaced by the pinning —
recorded in FAILURES.md.

### 2.3 Soundness bugs caught by the planted-target tests

Two equality-boundary bugs — both in the CATASTROPHIC direction (they would falsely
certify the absence of a friend) — were caught by the planted-target completeness tests
before any real run, and fixed:

1. Admission of p₆ in branch (i) used `<` where exact equality (an all-minimal signature
   with I == target) is a live candidate — fixed to `<=`.
2. At the leaf of the exponent phase, MAX-PRUNE degenerated into `prod_I ≤ TARGET` (empty
   product of sups) and killed the exact equality — leaf moved before the prunings.

The planted tests (6-prime signatures with exponents 2 and 4, including on the 5) now
pass: the certifier FINDS each planted signature exactly.

### 2.4 Result

`python experiments/elimina_omega6.py` (code of this commit):

```
prefixos C5: 19 (ramo i: 16, ramo ii: 1, mortos por poda-min: 2)
conjuntos completos: 2745; folhas alcancadas na fase de expoentes: 0
pins de P testados no ramo ii: [31, 3221]
tempo: 0.1s
```

(The leaf counter being 0 implies **zero equality tests executed**: the `rec` of the
exponent phase never reaches a leaf, because in each of the 2 745 sets some prime is
already left without a valid exponent.)

All 2 745 complete sets (including the long chain {5,7,11,13,29,p₆} with p₆ up to
20 731 (2 312 sets), analogous to "chain 13" of the literature) die in the closure by
orders — some prime is left without a valid exponent — without ANY equality needing to
be tested. The only branch-(ii) prefix is {5,7,11,13,23} (the same `RamoNaoLimitado` of
Block 1), closed by pinning with P ∈ {31, 3221}.

> **Result H: every friend of 10 has ω(N) ≥ 7.**
> `[PROVED-CONDITIONAL: Theorems A–D and Lemmas/Fact 0 of Phase 0 + Zsygmondy and the
> Nielsen/Voight valuation formula (classical; formula re-tested exhaustively against
> direct valuation) + correctness of core/omega6.py and core/cadeias.py (adversarial
> pass in §2.5) + correctness of sympy.n_order/factorint/nextprime in the calls consumed]`
> Independent, mechanical reproduction of Theorem 1.2 of arXiv:2404.00624
> (a manual proof of 19 chains) — in 0.1 s.

### 2.5 Adversarial pass on Block 2

Five independent reviewers, instructed to BREAK the ω = 6 certification. Three finished
in this round; the other two reviews were interrupted and redone:

| Target | Verdict | Summary |
|---|---|---|
| Pinning of branch (ii) | **SOUND** | instrumented replay: **all** 18 102 calls of `v_q_sigma`, 3 017 of `sigma_fecha_em`, 35 222 of `ordem_mod`, 2 924 of `nextprime` and 2 747 of `factorint` consumed by the certificate re-verified against own implementations — **0 errors**; independent re-enumeration of the prefixes (17 alive; the code's 19 are an exact superset, with 2 killed by a valid min-prune); coverage of the complete sets: 2 743 expected vs 2 743 processed, 0 missing / 0 extra; death of the 2 745 re-verified with 100% own code (0 alive); the whole pinning reimplemented and swept over 1 001 synthetic prefixes — 0 divergences |
| Coverage of Stage A + branch (i) | MINOR_GAP | 441 own planted targets, **all found exactly 1×**; **directed mutation** campaign with 12 mutants in the dangerous direction, all detected (losing 26 to 136 of the 136 targets). Closure re-derived from scratch (no D, no valuation formula, no sympy): 0 survivors. **One serious defect** (fixed, below) |
| Dependencies and real run | MINOR_GAP | pins checked digit by digit; closure reimplemented in a *strictly more permissive* way → 0 survivors out of 2 745; distribution of the killer: the prime 5 kills 2 669 sets, 7 kills 74, 19 and 13 one each. **Dishonest label** (fixed, below) |
| Valuation formula and closure | MINOR_GAP | formula re-derived by LTE and verified exhaustively for all p,q < 220 and a = 1..45 **including odd a** (0 divergences); the 4 links of the proof (prefixes, p₆, pinning, death of the 2 745) re-verified by independent routes; kills re-checked by direct integer factorisation (2 855 candidates m, largest m = 9 689, **zero false kills**) and by brute force a = 2..160 |
| Completeness by plantings | MINOR_GAP | 72 planted signatures found (incl. the edge case I(N) == TARGET exactly); **3 blind mutants discovered** (fixed, below) |

**Corrections applied in this block in response:**

1. **[SERIOUS] The termination raise was missing in `_prefixos_c5`.** The candidate loop
   only terminates if ∏ p/(p−1) < 9/5 **strictly**; if a node had ∏sup ≥ 9/5 the loop
   would run **forever, without exception and without diagnosis** — failure by hanging,
   not the honest refusal the module promises. It does not affect the current
   certificate (the maximum of ∏sup at any node of level ≤ 4 is 1001/576 < 9/5,
   verified), but it was a **landmine for Block 3**: at level 5 the maximum is already
   17017/9216 ≥ 9/5, i.e. reusing this DFS for ω = 7 would hang silently **on the real
   target**. Fixed with a `NaoCertificavel` raise + test
   `test_prefixos_c5_recusa_em_vez_de_travar` (which, without the fix, would not terminate).
2. **The experiment's label declared the wrong dependencies**: it cited `isprime` and
   `integer_nthroot` (used nowhere) and **omitted `factorint`**, which is load-bearing —
   it is what produces the two pins that close branch (ii), the only branch with an
   infinite space. Label fixed.
3. **The two honesty guards had no test at all** (mutation: removing them survived the
   whole suite and the experiment kept printing CERTIFIED). Added
   `test_guarda_caso_a_pin_indisponivel` (C5 = {5,7,11,13,31}, where ord₁₁(31) = 5) and
   `test_guarda_caso_b_sem_pin` (C5 = {5,7,13,17,31}, where σ(5²) = 31 ∈ C5).
4. **A factually wrong claim in my first write-up**: I had written that the two sets of
   branch (ii) die because "13 is left without an odd order" — false. 13 **does** have
   an odd order (ord₂₃(13) = 11) and m = 11 is a legitimate candidate, killed only in the
   reconstruction. **What kills both sets is the prime 7**; and 5 still has a valid
   exponent in {5,7,11,13,23,31}. Fixed in the text and pinned by
   `test_quem_mata_os_conjuntos_do_ramo_ii`.
5. Honest counters: `prefixos_mortos_min` (the output did not add up before:
   16 + 1 ≠ 19) and `assinaturas_ramo_i` → `assinaturas_testadas` (the counter serves
   both branches and counts leaves reached, not equality tests executed).
6. Truncated docstring fragments in `omega6.py` and the exact number of the largest p₆
   ({5,7,11,13,29}: p₆ ≤ **20 731**, 2 312 sets) fixed.

7. **[SERIOUS] Three catastrophic mutants survived the whole suite** — discovered by the
   plantings lane. The worst: making the v₅ budget **forget the sixth prime's
   contribution** passed the 78 tests and the experiment kept printing CERTIFIED, but
   **lost a genuine friend** (demonstrated with the target I({5²,7²,11²,13²,17²,31⁴}),
   where 31 ≡ 1 mod 5 is the only feeder of the 5). The other two: discarding the last
   exponent of each list (invisible because in the whole real run there is **a single**
   list with 2 entries — (5, {5,7,11,13,31,71}) → [2,4]) and truncating the large orders
   (the real run uses candidates up to m ≈ 10⁴). The three now die in dedicated tests —
   verified by re-applying each mutation: the 3 fail, one per test.
8. **Honest retraction:** the original sentence of this section — "the 6 in the
   dangerous direction were all detected — the harness has teeth" — was **true only for
   the mutants of that lane**. The plantings lane exhibited 3 dangerous mutants that
   passed. The sentence was corrected and the holes closed.
9. Hardening suggested by the review and applied: `TARGET / prod_sup > 1` →
   `TARGET > prod_sup` (the tie now provably goes to branch (ii); under the opposite
   mutation the p₆ loop would never terminate); `v_q_sigma` refuses q = 2 explicitly (the
   LTE formula only holds for odd q, and a planted target with even numerator would put 2
   into `extras`); size guard before factoring the remainder of the strip (unbounded
   factorisation would be a hang, not an honest failure); `_candidatos_m` now enumerates
   divisors in O(√m) instead of sweeping all odd numbers up to m — a performance wall
   identified for ω ≥ 7.

**Second independent leg for branch (ii)** (a finding of the review, recorded as data):
for **all 216 807 primes P ∈ (23, 3·10⁶]**, the set {5,7,11,13,23,P} dies in the
closure by orders **without using the pinning**. Moreover, structurally, D(7) = ∅ in
this prefix, which forces a₇+1 to be an odd prime and strongly restricts P at any size.
This gives branch (ii) an independent verification up to 3·10⁶, leaving the pinning
responsible for P > 3·10⁶. Note also that the pinning is **not redundant**: at P = 2801
the prime 7 has a valid exponent ([4]), i.e. the "killer 7" fails and the set only falls
by another prime.

**Recorded limitation (not fixed):** branch (ii) is structurally **untestable by planted
target** — `_ramo_ii_pinagem` raises `NaoCertificavel` for any target ≠ 9/5, so the
harness that caught the two earlier boundary bugs is blind there. The completeness of
the branch rests on the manual derivation (§2.2), the independent re-implementation done
by the review (1 001 prefixes, 0 divergences) and the frozen-output tests. The clause
`P > p₅` is also dead code in the real run (both pins are > 23) — **do not presume it was
validated by use** in a future ω = 7.

---

## Block 3 — Recursive certifier and universal bound for a₁

### 3.1 The idea: a certifier for any ω, with honesty at every node

`core/omega_k.py` replaces Block 2's design "Stage A + two branches" by a uniform
recursion over states (C, s, lo): C = primes already known (contains 5), s = how many
primes are still unknown, lo = lower bound for the unknowns (invariant: every prime of S
that is ≤ lo is in C). At each node:

- **dead** if s ≥ 1 and ∏_{C} I(p²) ≥ 9/5 (the s remaining factors are > 1);
- **s = 0**: complete set → the same exponent phase as Block 2
  (`omega6._conjunto_completo`: closure by orders + v₃/v₅ budgets + equality);
- **branch (i)** if ∏_{C} p/(p−1) < 9/5: the smallest unknown U is bounded by the index
  (a non-increasing bound in U with limit ∏sup(C) < 9/5 — the loop terminates, no raise
  needed: the entry condition IS the termination condition); recurse with lo = U;
- **branch (ii)** otherwise: pinning (below) and recursion with s reduced.

The trap mapped in Block 2 (the prefix DFS would hang at level 5, where
∏sup{5,7,11,13,17} = 17017/9216 ≥ 9/5) disappears by construction: a node with
∏sup ≥ 9/5 never enters the index loop — it goes to the pinning.

### 3.2 The new piece: a universal bound for a₁ = v₅(N)

v₅(σ(N)) = a₁ − 1 = Σ_{feeders U} v₅(a_U + 1), and only bases ≡ 1 (mod 5) feed
(Fact 2). For a feeder U with k = v₅(a_U+1): for each j = 1..k, Φ_{5^j}(U) divides σ(N)
and has a primitive prime r_j with ord_{r_j}(U) = 5^j (Zsygmondy, no exceptions for
U ≥ 5 and 5^j odd ≥ 5), hence r_j ≡ 1 (mod 5^j), r_j ∉ {3, U}, and the r_j are
**distinct** (distinct orders). Therefore k ≤ #{r ∈ S∖{U} : r ≡ 1 (mod 5)} ≤
c₅ + s − 1, with c₅ = #{q ∈ C : q ≡ 1 (mod 5)}. With at most c₅ + s feeders:

> **a₁ ≤ 1 + (c₅ + s)·(c₅ + s − 1)** — finite for any number of slots.

Even a₁ is enumerated in that range; σ(5^{a₁}) has to factor over S ∪ {3}, so the prime
factors of the remainder of the strip by C ∪ {3} are unknowns: more than s, or some
≤ lo (it would be in C by the invariant) ⟹ dead case; otherwise **all are pinned**. If
the remainder is 1, the 5 still needs a feeder: for each q ∈ C with q ≡ 1 (mod 5), the
case "q feeds" pins via Φ₅(q) (if 5 ∉ D_q(C)); the case "only unknowns feed" is closed
when impossible (s = 1 and C without the primes ≡ 1 (mod 5^j) required) and otherwise
raises `NaoCertificavel`. No gap is silent.

### 3.3 Cross-check with Blocks 1–2

For k ≤ 6 the recursive certifier reproduces the earlier certifications, with one
**explainable and tighter** difference: for k = 6 it tests 2 744 complete sets (Block 2
tested 2 745) and pins only {31}. The universal bound gives, in {5,7,11,13,23} with
s = 1, a₁ ≤ 1 + 2·1 = 3 ⟹ **a₁ = 2 forced** ⟹ σ(25) = 31 occupies the only slot; the
case "11 feeds ⟹ 3221" of Block 2 would require a second slot and is subsumed. Both
coverages are complete; Block 2 tested one redundant set. For k ≤ 5 the index kills at
the leaf what Block 1 killed by closure (same verdict). Tests in `tests/test_omega_k.py`
(consistency k ≤ 6, a₁ bound with two slots, target guard, 7-prime plantings in the
branch-(i) regime).

### 3.4 What else went into the block (three honest iterations)

The first version of the certifier (index first, pinning only where the index fails)
**exploded at k = 7**: in the prefix {5,7,11,13,29} with 2 slots, U goes up to ~41 500
by the index and, for each U > 20 744, p₇ climbs to hundreds of thousands (∏sup within
10⁻⁶ of 9/5) — millions of 7-prime sets, all killed in the closure, too late (> 590 s).
The answer was mathematical: the pinning is a complete partition **at any node**, and
"a₁ = 2 ⟹ 31 ∈ S, 31 ≤ lo" kills the whole chain instantly. With **partition first**
(index as fallback), k = 6 drops from 2 745 sets to 27.

The next three iterations, each triggered by a concrete residual state of k = 7:

1. **Committed a₁**: a branch coming from a₁ = 4 re-enumerated a₁ = 2 deeper — an
   impossible sub-case in the branch. The a₁ chosen in a partition is propagated.
2. **Budget of 3** (v₃(σ(N)) = 2 exactly; residual {5,7,11,13,31,71}+P): same Zsygmondy
   structure, fixed total; and the correction of a weakness of mine — when the primitive
   witness of Φ_{ℓʲ}(q) was known I pinned nothing, but the **other** new factors of
   Φ_{ℓʲ}(q) are still obliged to be in S (Φ₅(31) = 5·11·17351 pins 17351 even with 11 known).
3. **Product of cases + injective feasibility** (residual {5,7,11,13,31,181}+P): with a
   single unknown, every divisor d > 1 of a_P+1 is the order of a primitive prime
   r_d ∈ C with d | r_d − 1, and distinct divisors have **distinct** witnesses — a
   matching. 45 | a_P+1 would require witnesses for 9 and 45, and only 181 serves both.
   The case dies.

### 3.5 Result for ω = 7: NOT certified — frontier characterised

`python experiments/elimina_omega_k.py --k-max 7` (verbatim output, pin lines omitted):

```
omega = 1: nos=1 mortos_min=0 ramo_i=0 particoes=0 conjuntos_completos=1 folhas=0 amigos=0 tempo=0.0s
omega = 2: nos=1 mortos_min=0 ramo_i=0 particoes=1 conjuntos_completos=0 folhas=0 amigos=0 tempo=0.0s
omega = 3: nos=3 mortos_min=0 ramo_i=0 particoes=2 conjuntos_completos=1 folhas=0 amigos=0 tempo=0.0s
omega = 4: nos=4 mortos_min=0 ramo_i=3 particoes=4 conjuntos_completos=0 folhas=0 amigos=0 tempo=0.0s
omega = 5: nos=7 mortos_min=0 ramo_i=6 particoes=7 conjuntos_completos=0 folhas=0 amigos=0 tempo=0.5s
omega = 6: nos=57 mortos_min=0 ramo_i=25 particoes=30 conjuntos_completos=27 folhas=0 amigos=0 tempo=1.6s
omega = 7: NAO CERTIFICADO apos 0.1s
   estado residual: C=[5, 7, 11, 13, 31, 331], s=1: casos abertos ['a1=2:k5=1,k3=1']
```

Exact characterisation of the residual (arithmetic recorded in `tests/test_omega_k.py`):
- C = {5,7,11,13,31,331}, one unknown P > 331; a₁ = 2 (branch); 331 came from
  Φ₃(31) = 3·331 ("31 feeds the 3").
- The only open case: P feeds the 5 (k₅ = 1) **and** carries one of the two 3's (k₃ = 1);
  the other 3 comes from 31. Hence 15 | a_P + 1, and 331 ≡ 1 (mod 15) is a legitimate witness.
- The feasible m = a_P + 1 (injection of witnesses into C) are **{3, 5, 11, 15}** ⟹
  **a_P = 14 forced**.
- **13 has no possible feeder in C** (no ord₁₃(q) is odd) ⟹ only P feeds the 13;
  ord₁₃(P) = 1 would require 13 | 15 ⟹ ord₁₃(P) = 3 ⟹ P ≡ 3 or 9 (mod 13).
- ∏sup(C) = 1.8012 ≥ 9/5: the index does not bound P. ∏I(q²) = 1.7794.

What is missing to close it: v_P(N) = a_P = 14 has to be supplied entirely by the
σ(q^{a_q}), q ∈ C (P ∤ a_q+1, since a divisor P of a_q+1 would require a witness ≡ 1
(mod P) in S, impossible) — that is, Σ_{q∈C} v_P(q^{ord_P(q)} − 1) ≥ 14 with only 6
terms: it requires **v_P(q^{ord_P(q)} − 1) ≥ 3 for some q** (a "high-order Wieferich
pair" with P > 331). It is exactly the territory of Corollary 6 / Proposition 9 of
Thackeray (arXiv:2310.15900): v_r bookkeeping with computer-verified bounds for special
primes. **Candidate Block 4:** a v_P budget for the unknown, with Thackeray's bound
(k−1)² + c re-derived.

**Labels:** no new statement. ω(N) ≥ 7 (Result H) becomes **doubly certified** — by the
Block 2 certifier (2 745 sets; adversarial pass §2.5) and, independently and much more
briefly, by this block's recursive certifier (27 sets; still **without** its own
adversarial pass — not load-bearing until it goes through one). ω = 7 remains open for
this method.

---

## Block 4 — Beyond the ω = 7 wall: tightening, direct valuations, tails

Approved objective: push the recursive certifier past the residual state
{5,7,11,13,31,331}+P of Block 3. The block ended with **ω = 7 and ω = 8 certified** by
the recursive certifier (ω(N) ≥ 9), four new pieces in the method and a methodological
lesson recorded in FAILURES.md. Everything below is exact arithmetic (`Fraction`/`int`);
the decimals in the text are only human-readable views of the rationals.

### 4.1 Diagnosis: the Block 3 wall was a tightening defect, not a theory gap

The Block 3 report (§3.5) asked for "v_P bookkeeping" to close the residual. It was
wrong. The a₁ = 2 chosen by the partition was a **commitment of the branch** but did not
enter the index bounds: prod_sup used 5/4 in place of I(5²) = 31/25. With the exact
commitment,

  ∏sup{5,7,11,13,31,331} = (31/25)(7/6)(11/10)(13/12)(31/30)(331/330) = 1.7868 < 9/5

(it was 1.8012 with 5/4), and the index bounds P: the node falls into the fallback and
closes. The same tightening holds at any node (exact I(p^{a_p}) for every committed
prime, in both bounds) and, in complete sets, allows killing for free before the
exponent phase: prod_min > 9/5, or prod_sup ≤ 9/5 with some free exponent (I(N) < prod_sup
strictly), or prod_sup < 9/5 with all fixed. At k = 6 the 22 complete sets all die there
(`completos_mortos_indice = 22`, 51 nodes, 0 leaves).
[Precision added in Block 7: since exponents can carry upper bounds (`maximos`,
Block 6), the inequality I(N) < prod_sup is strict exactly when some free prime has
*no* upper bound; the code tests that condition.]

Lesson (FAILURES.md, outcome of the Block 3 entry): before asking for new theory, check
that every piece of information already committed in the branch enters ALL the prunings.

### 4.2 Second obstacle: giant exponents materialised

With the wall removed, k = 7 hung (> 560 s, no progress) at the complete set
{5, 11, 31, 71, 181, 1741, 167140584971}. Diagnosis by stack dump (`faulthandler`):
`cadeias.sigma_fecha_em` computing `p**(a+1)`. Cause: 167140584971 − 1 = 2·5·16714058497
with the cofactor **prime**, hence ord_r(p) ∈ {16714058497, 83570292485, …} for the
other p, and m = ord_r(p) is a legitimate candidate for a_p + 1 in the closure by orders
(all its divisors > 1 are {m} ⊆ D). The reconstruction tried σ(5^{16714058496}) —
3.9·10¹⁰ bits.

Fix in `core/cadeias.py`, identical semantics, only the computation changes:

- **Direct valuations.** v_q(σ(p^a)) = v_q(p^{a+1} − 1) − v_q(p − 1), with
  v_q(p^{n} − 1) by modular exponentiation (p^n mod q^j for j = 1, 2, …). Holds for
  EVERY prime q ≠ p (including q = 2) and needs no ord_q(p) — hence no factorisation of
  q − 1. `v_q_sigma` (the Nielsen/Voight formula by orders) stays in the module and in
  the tests; `_v_q_de_p_ordem_menos_1` also became modular.
- **Exact size gate.** The product P = ∏ q^{v_q(σ(p^a))} always divides σ(p^a). If
  bl(P) ≤ a·(bl(p) − 1) (bl = bit length) then
  P < 2^{bl(P)} ≤ 2^{a(bl(p)−1)} ≤ p^a < σ(p^a), and the answer is False without
  materialising p^{a+1}. Where the power is computable the answer is the same
  (`test_gate_de_tamanho_e_so_atalho`).
- Odd divisors of m by factorisation (`sympy.divisors`, m divides a q − 1 already
  factored by `n_order`) instead of trial division up to √m.

The set that hung resolves in 0.00 s: valid exponents 5 → [2, 4, 14], 11 → [] (dead).
New tests in `tests/test_cadeias.py`: direct valuation against brute force (exhaustive,
q = 2 included), modular against integer power, the real set above in < 5 s, divisors
against brute force.

### 4.3 Large primes without factoring r − 1 (implemented and tested; not yet triggered)

Pins such as Φ₅(q) exceed 100 bits, and r − 1 may not be factorable — which makes
ord_r(p) inaccessible precisely where the closure by orders needs it. Lemma implemented
in `omega_k._expoentes_com_primo_grande` (header of `core/omega_k.py`, "LARGE PRIMES"):
in a complete set S = S′ ∪ {r} with r large ((r−1) with more than `ORDEM_BITS` = 80
bits), for p ∈ S′ every divisor d > 1 of a_p + 1 is ord_{r′}(p) with distinct witnesses
for distinct divisors, and r witnesses at most ONE divisor, o = ord_r(p). With D′ = the
orders of p modulo S′∖{p} (computable), the cases are exhaustive: (A) all divisors in
D′; (B2) a_p + 1 ∈ D′ with exactly one divisor d* outside D′ and ord_r(p) = d* (modular
test); (B1) a_p + 1 = o ∉ D′ with all proper divisors in D′ — o composite ⟹ o = ℓ·e with
ℓ prime ∈ D′, e ∈ D′ (finite); o = ℓ prime ⟹ Φ_ℓ(p) = ℓ^ε·r^v (the only possible
primitive factor is r; the non-primitive one is only ℓ, ε ≤ 1 by LTE), with
v ≤ v_r(σ(N)) = a_r ≤ A_r, where A_r comes from the valid exponents of r (the orders of r
modulo the small primes are accessible; empty list = dead set). Hence
p^{ℓ−1} < Φ_ℓ(p) ≤ ℓ·r^{A_r} bounds ℓ, which is enumerated and tested (ℓ | r − 1 and
p^ℓ ≡ 1 mod r). The valuations of the reconstruction are the direct ones of §4.2. Two
large primes in the same set: `NaoCertificavel`.

Validation: forcing `ORDEM_BITS = 12` in the tests, the real complete sets of k = 7 with
exactly one "large" prime (13 sets with the current tree; the test requires ≥ 10 —
corrected in Block 7, the text said ≥ 20) produce through the new route **exactly** the
lists of the direct route (`expoentes_validos_ordens`); and the prime case (B1) is
exercised in {5,7,11,13,31}+19 (ord₁₉(7) = 3, 3 is not an order of 7 modulo any other
prime of the set; σ(7²) = 3·19 closes). Honesty: for k ≤ 8 no prime of a complete set
exceeded 65 bits (`conjuntos_com_primo_grande = 0`), the route was only exercised by
the tests.

### 4.4 ω = 7 closes

`certifica_omega(7)` (final version of the block): 549 nodes, 172 partitions, 51 index
fallbacks, 153 complete sets (224 killed by the cheap pruning), 0 leaves, 0 friends,
1.5 s, no `NaoCertificavel`. Counts frozen in `tests/test_omega_k.py`. (Before the
pruning of §4.6 it was 648 nodes and 164 sets — same verdict.)

### 4.5 ω = 8: general commitments and branching by exponent with a tail

First wall of k = 8: C = {5,7,11,13,31,71}, s = 2, a₁ = 2 — the two budgets
(v₅ = 1, v₃ = 2) can be carried by the two unknowns (no finite reasoning with s = 2) and
∏sup = 1.80686 ≥ 9/5. But the node is **tight**: ∏I(p²) = 1.79935 and a₇ = 4 already
gives 1.80451 > 9/5 (dead with s ≥ 1); hence a₇ = 2 is forced and σ(7²) = 57 = 3·19
forces 19 ∈ S — a pin (or death, if 19 ≤ lo). This is Nielsen's branching by exponent,
which requires generalising the commitment: the state now carries `fixos = {p: a_p}` for
any known prime. A commitment enters the bounds exactly, forces v_ℓ(a_p + 1) in the
budgets (a fixed feeder has a forced k), restricts the list in the complete set and — the
essential point — **closes σ(p^{a_p}) in S ∪ {3}** piece by piece (Φ_d(p) for
d | a_p + 1, each much smaller than σ(p^{a_p})): new primes are pins, more than s or some
≤ lo is death.

Second wall: C = {5,7,11,13,31,89}, s = 2, a₁ = 2 — a **loose** node: no single prime
has a finite window (7 → ∞ gives 1.79942 < 9/5), although ∏sup = 1.80166 > 9/5.
Classical solution (Nielsen): **tails**. Each free prime q has gain
g_q = sup(q)/I(q^{min_q}); ordering by decreasing gain q₁, q₂, …, let m be minimal with
prod_min·g_{q₁}⋯g_{q_m} > 9/5 (it exists: the total product is prod_sup). Branch on
q = q_m into a_q ∈ {min_q, …, A − 2} EXACT and the TAIL a_q ≥ A, with A the least even
number such that prod_min·g_{q₁}⋯g_{q_{m−1}}·I(q^A)/I(q^{min_q}) > 9/5 (a complete
partition of a_q). Progress: A > min_q by the minimality of m; in the tail the m − 1
larger gains already suffice (m decreases); with m = 1 the tail dies. The measure
(s, #free primes, m) strictly decreases along every edge ⟹ the tree is finite. In the
residual: gains g₇ = 1.00292 > g₁₁ = 1.00075 > …; prod_min·g₇ = 1.79942 ≤ 9/5 < prod_min·g₇·g₁₁
⟹ branch on 11: a₁₁ = 2 exact (σ(121) = 7·19 pins 19) and tail a₁₁ ≥ 4; in the tail
m = 1 ⟹ branch on 7: a₇ = 2 exact (57 = 3·19) and tail a₇ ≥ 4, dead
(prod_min = 1.8005 > 9/5). Frozen in `test_ramificacao_por_expoente_com_cauda_no_residual_de_k8`.

Result (final version of the block): **k = 8 certified** — 210 456 nodes, 45 254
partitions, 323 branchings by exponent (323 tails), 839 index fallbacks, 145 659
complete sets (19 350 killed by the cheap pruning), 467 cases without closure, 0 leaves,
0 friends, 72 s, no `NaoCertificavel`. Largest prime in C: 20796629989288946761
(65 bits). (The first version that closed k = 8 — without cache and without the pruning
of §4.6 — took 312 s over 214 200 nodes; same verdict.)

### 4.6 Closures beyond the budget: partial information is never discarded

The first attempt at k = 9 stopped honestly at 108 s: `NaoCertificavel` "composite
cofactor of 91 bits with s = 2 — factorisation beyond the budget" (`FATORA_BITS = 90`).
The exception was born inside the partition and aborted the whole node, even when the
other cases of the node pinned and the tails/index would close the problematic case.
Two iterations until the right semantics:

1. *First version* — the case with closure beyond the budget simply became "open"
   (without pins). Sound, but it **discarded correct information**: at k = 8 the branch
   a₁ = 40 (σ(5⁴⁰) = Φ₄₁(5), 95 bits) lost the small pins already found (20743,
   45985571) and the index had to rediscover them by enumerating the smallest unknown up
   to 4.6·10⁷ — the run went from 214 200 to > 3 000 000 nodes and was aborted. (In the
   previous version that branch did not even exist: the exception aborted the root's
   partition, which fell to the index, and the children's partitions, with smaller s,
   had a₁ ≤ 31.)
2. *Final version* — `_novos_e_resto` returns (new primes already identified,
   remainder): the identified ones are valid pins **regardless** of the remainder, and a
   composite remainder beyond the budget guarantees ≥ 2 new primes not yet identified (a
   composite that is not a prime power, coprime to the allowed and to the identified
   ones): death if they do not fit in the slots. Distinct pieces of σ(p^a) have coprime
   remainders (a prime common to Φ_d(p) and Φ_{d′}(p), d < d′, divides d′; the examined
   pieces have φ(d′) ≤ `GRAU_PHI_MAX` = 200, so that prime is at most 199 and the small
   division removes it — corrected in Block 7: the text justified this by
   "≤ a + 1 < 10⁵", a bound on a that the code never enforces), so
   they count 2 each; remainders of distinct bases may share primes and count 2 in
   total (refined in Block 7 by a coprime base, §7.3). A piece beyond the Φ gates (`PIN_BITS`, `GRAU_PHI_MAX`) is just less
   information (`casos_sem_fecho` in the statistics). No exception leaves the partition
   any more; `NaoCertificavel` is reserved for the node with no way out (an open case
   with no branch and no index) and for the complete set with two large primes.

3. *The missing pruning* — even with the pins preserved, the branch a₁ = 40 still went by
   the index: Φ₄₁(5) has no factor < 10⁵ (only the 95-bit remainder, extra = 2), and the
   **universal bound** a₁ ≤ 1 + (c₅+s)(c₅+s−1) was only applied when enumerating a free
   a₁. It holds at EVERY node: in {5, 7} with s = 6 it gives a₁ ≤ 31 < 40 — the child
   dies at once. With a₁ fixed, the bound is re-checked at every partition
   (`test_cota_universal_vale_tambem_para_a1_comprometido`). This also trims k ≤ 7
   (k = 6: 60 → 51 nodes; k = 7: 648 → 549 nodes), without changing any verdict.

A cache went in alongside (`_phi_valor`, trial division, cofactor classification: the
k = 8 profile showed `_novos_de` + `cyclotomic_poly` with ~45% of the time). The first
version of the cache had a **false-death bug**: trial division may stop early (q² > c)
leaving in c a small *allowed* prime (e.g. Φ₃(5) = 31 with 31 ∈ C), which the
classification counted as new and which consumed a slot; `_novos_de_sigma(5, 8, ·, s = 2)`
returned "dead" (σ(5⁸) = 31·19·829 needs 2 new slots, not 3) and k = 6 dropped from 60
to 35 nodes. Two tests caught it: the equivalence `_novos_de_sigma` ≡ `_novos_de` over
the whole σ(p^a) and the frozen counts of k = 6/7. It is recorded as one more "mutant"
the battery detects (in the line of the three of Block 2); the methodological lesson
goes to FAILURES.md.

### 4.7 Official script output

`python experiments/elimina_omega_k.py --k-max 8` (pin lines omitted):

```
omega = 1: nos=1 mortos_min=0 ramo_i=0 particoes=0 ramos_expoente=0 caudas=0 conjuntos_completos=0 completos_mortos_indice=1 com_primo_grande=0 casos_sem_fecho=0 folhas=0 amigos=0 tempo=0.0s
omega = 2: nos=1 mortos_min=0 ramo_i=0 particoes=1 ramos_expoente=0 caudas=0 conjuntos_completos=0 completos_mortos_indice=0 com_primo_grande=0 casos_sem_fecho=0 folhas=0 amigos=0 tempo=0.0s
omega = 3: nos=3 mortos_min=0 ramo_i=0 particoes=2 ramos_expoente=0 caudas=0 conjuntos_completos=0 completos_mortos_indice=1 com_primo_grande=0 casos_sem_fecho=0 folhas=0 amigos=0 tempo=0.1s
omega = 4: nos=5 mortos_min=0 ramo_i=2 particoes=4 ramos_expoente=0 caudas=0 conjuntos_completos=0 completos_mortos_indice=1 com_primo_grande=0 casos_sem_fecho=0 folhas=0 amigos=0 tempo=0.0s
omega = 5: nos=7 mortos_min=0 ramo_i=5 particoes=7 ramos_expoente=0 caudas=0 conjuntos_completos=0 completos_mortos_indice=0 com_primo_grande=0 casos_sem_fecho=0 folhas=0 amigos=0 tempo=0.1s
omega = 6: nos=51 mortos_min=0 ramo_i=17 particoes=29 ramos_expoente=0 caudas=0 conjuntos_completos=0 completos_mortos_indice=22 com_primo_grande=0 casos_sem_fecho=3 folhas=0 amigos=0 tempo=0.6s
omega = 7: nos=549 mortos_min=0 ramo_i=51 particoes=172 ramos_expoente=0 caudas=0 conjuntos_completos=153 completos_mortos_indice=224 com_primo_grande=0 casos_sem_fecho=41 folhas=0 amigos=0 tempo=0.9s
omega = 8: nos=210456 mortos_min=193 ramo_i=839 particoes=45254 ramos_expoente=323 caudas=323 conjuntos_completos=145659 completos_mortos_indice=19350 com_primo_grande=0 casos_sem_fecho=467 folhas=0 amigos=0 tempo=71.6s

CERTIFICADO: todo amigo de 10 tem omega(N) >= 9.
Rotulo: [PROVADO-CONDICIONAL: Teoremas A-D e Lemas/Fato 0 da Fase 0 + Zsygmondy, LTE e formula de valuacao de Nielsen/Voight (classicos) + correcao de core/omega_k.py (certificador recursivo AINDA SEM passada adversarial propria - nao e load-bearing), core/omega6.py e core/cadeias.py (passada adversarial em results/FASE_1.md §2.5) + correcao de sympy.n_order/factorint/isprime/nextprime/cyclotomic_poly nas chamadas consumidas]
Nota: para omega >= 7 o certificado load-bearing e o do Bloco 2 (experiments/elimina_omega6.py); acima disso so este recursivo cobre, e o rotulo fica pendente da passada adversarial propria.
```

### 4.8 Labels, honesty and what is missing

- **Result I.** Every friend of 10 has **ω(N) ≥ 9**.
  `[PROVED-CONDITIONAL: Theorems A–D and Lemmas/Fact 0 of Phase 0 + Zsygmondy, LTE and
  the Nielsen/Voight valuation formula (classical) + correctness of core/omega_k.py
  (STILL WITHOUT its own adversarial pass) and of core/cadeias.py/core/omega6.py
  (adversarial pass §2.5, but with the changes of §4.2 and the extension of
  _conjunto_completo not yet adversarially reviewed) + correctness of
  sympy.n_order/factorint/isprime/nextprime/cyclotomic_poly/divisors in the calls
  consumed]`. **Not load-bearing** until its own adversarial pass; and not new —
  Thackeray (arXiv:2310.15900) has ω(N) ≥ 10. The value is the mechanical, independent
  and short (75 s) reproduction of part of the state of the art, with a reusable method
  for k ≥ 9.
- Targets of the recursive certifier's adversarial pass (mandatory before any label
  upgrade): (i) completeness of the partition of a_q in `_ramos_expoente` and the claim
  "the tail with prod_min > 9/5 dies with s ≥ 1"; (ii) the witness count `faltam` in
  `_casos_ell` (levels without a known witness require distinct unknowns) and the forced
  k of fixed feeders; (iii) the equivalence of `_viavel_m0` (feasible multiple ⟺ m₀
  feasible); (iv) `_novos_de` with a prime-power / composite cofactor and the gates
  (`FATORA_BITS`, `PIN_BITS`, `GRAU_PHI_MAX`), which may only raise `NaoCertificavel`,
  never kill; (v) the equality pruning at s = 0 with all exponents fixed; (vi) the
  large-prime lemma (B1), in particular v_r(σ(N)) = a_r (r ∉ {3, 5}) and the use of A_r;
  (vii) the invariant "pin ≤ lo ⟹ dead" in the presence of commitments.
- k = 9: running as this block closes, and **will not finish** within the 4 h limit — a
  live diagnosis. The first attempt (before §4.6) stopped honestly at 108 s on a 91-bit
  cofactor; the final version gets past that (at 885 s: 903 000 nodes, 121 000 complete
  sets, 31 777 tails, 15 016 sets with one large prime — the route of §4.3 genuinely
  triggered) but enters **almost-tight nodes with s = 1**, where the index fallback
  degenerates into enumeration: at C = {5, 7, 11, 13, 31, 97, 52361} with a₁ = 2,
  ∏sup = 9/5 − 1.76e-08 (the factor 52361/52360 almost exactly cancels the deficit of
  3.4·10⁻⁵ of the first six), so the last unknown U is bounded only by U < 1.03e+08 —
  5.9 million primes, each a complete set with an exponent phase (~1 000 nodes/s).
  The remedy is no longer the index: with s = 1, every prime divisor ℓ of a_U + 1 has a
  witness r ∈ C with ℓ | r − 1 (a finite set of ℓ), and Φ_ℓ(U) | σ(N) factors over
  C ∪ {3} with factors only of order ℓ (or ℓ itself): **Φ_ℓ(U) = ℓ^ε·∏ q^{e_q}** is a
  polynomial equation in U whose right-hand side runs over a finite set of exponent
  vectors (bounded by Φ_ℓ(U_max)) — solved by an exact integer root, without enumerating
  primes. It is the "extraction of the last slot" that FAILURES.md (Block 2) said to
  keep, now with the right ℓ. **Candidate Block 5.** Second pending point: σ(5^{a₁})
  with a₁ + 1 prime (Φ₅₃(5), 121 bits) at the root of k = 9 stays as a remainder of ≥ 2
  primes (sound, but without pins); an oracle of factorisations certified by
  multiplication (Cunningham tables) would recover the pins.

---

## Block 5 — The last unknown by cyclotomic equations

Approved objective (§4.8): replace the index enumeration of the last unknown by a
polynomial equation with a finite right-hand side. Delivered and tested; the effect on
k ≤ 8 is large (k = 8: 210 456 → 90 032 nodes), and k = 9 changed walls — the
degenerate enumeration moved from the nodes with s = 1 (solved in 0.00 s) to the
almost-tight nodes with **s = 2**, whose analysis closes this block.

### 5.1 The lemma and the implementation

At a node with a single unknown U (S = C ∪ {U}), a_U + 1 is odd ≥ 3 and has a prime
factor ℓ. Then Φ_ℓ(U) | σ(U^{a_U}) | σ(N), and every prime factor of Φ_ℓ(U) is in
S ∪ {3}. A prime q | Φ_ℓ(U) either has ord_q(U) = ℓ — hence q ≡ 1 (mod ℓ), q ≠ 3
(ord₃ ≤ 2), q ≠ U — or is q = ℓ, non-primitive (U ≡ 1 mod ℓ, and then v_ℓ(Φ_ℓ(U)) = 1
by LTE), in which case ℓ ∈ C or ℓ = 3. Zsygmondy (ℓ odd ≥ 3, U ≥ 2: no exceptions)
gives a primitive prime r ∈ C, hence ℓ | r − 1: ℓ ∈ L(C) = {odd primes dividing some
r − 1, r ∈ C}, a finite set. Thus

> **Φ_ℓ(U) = ℓ^ε · ∏_{q ∈ C_ℓ} q^{e_q}**, C_ℓ = {q ∈ C : ℓ | q − 1}, ε ∈ {0, 1}, e_q ≤ a_q.

The right-hand side runs over a **finite** set of vectors when there is a bound: by the
index (prod_sup(C) < 9/5 ⟹ U < 1 + 1/δ, δ = (9/5)/prod_sup − 1, hence Φ_ℓ(U) ≤ Φ_ℓ(U_max))
or because all q ∈ C_ℓ have fixed exponents. For each value R of the right-hand side
there is at most one U, since U^{ℓ−1} < Φ_ℓ(U) < (U+1)^{ℓ−1}: **U = ⌊R^{1/(ℓ−1)}⌋**, an
exact integer root (`integer_nthroot`), verified by Φ_ℓ(U) = R, U prime, U > lo, U ∉ C.
No prime enumeration.

Which ℓ: with s = 1 the budgets are exact for U (Fact 2): k₅ ≥ 1 ⟹ ℓ = 5 with
U ≡ 1 (mod 5), ε = 1; otherwise k₃ ≥ 1 ⟹ ℓ = 3, ε = 1; with (k₅, k₃) = (0, 0), ℓ runs
over L(C), with ε = 0 forced for ℓ ∈ {3, 5} (U ≡ 1 mod ℓ would feed ℓ) and ε ∈ {0, 1}
only if ℓ ∈ C. One ℓ suffices for completeness (the union over the possible ℓ covers
every U); the complete-set phase re-verifies the rest. Without a bound (prod_sup ≥ 9/5
with a free exponent in C_ℓ) or with L(C) incomplete (a large prime in C), the solver
returns None and the case proceeds to tails/index as before.

Implementation: `_cota_indice_U`, `_L_de`, `_solucoes_phi` (DFS over exponent vectors
with pruning by the product), `_ultimo_desconhecido`; enters `_particao` as step 3
(before the tails) for open pairs with s = 1; the candidates become pins (complete
sets). Counters `ultimos_resolvidos` and `candidatos_ultimo`.

### 5.2 Verification

- `test_solucoes_phi_batem_com_forca_bruta`: independent brute force (enumerate primes
  U ≤ U_max and test the closure of Φ_ℓ(U) by divisions) against the solver, on four
  prefixes, ℓ ∈ {3, 5, 7, 11}, ε ∈ {0, 1}; non-vacuity guaranteed by the case
  {5,7,11,13,31}, ℓ = 3, ε = 1: **67² + 67 + 1 = 4557 = 3·7²·31**, found by both.
- `test_ultimo_desconhecido_e_completo_contra_forca_bruta`: the three modes (k₅ ≥ 1,
  k₃ ≥ 1, (0,0) = union over L(C)) against brute force.
- `test_ultimo_desconhecido_resolve_o_no_quase_justo_de_k9`: the node of §4.8
  ({5,7,11,13,31,97,52361}, a₁ = 2, U < 1.03·10⁸) resolves in the three modes in
  < 5 s (0.00 s in practice: zero candidates), and the solver refuses honestly without
  a bound.
- Frozen counts updated (k = 6: 55 nodes; k = 7: 459 nodes, 40 complete sets,
  `ultimos_resolvidos ≥ 1`); the residual of Block 3 now closes by the solver
  (`ramo_i == 0`).

Two constant-factor optimisations went in alongside, with no change of semantics: small
factors by gcd with the primorial of the primes < 10⁵ (one long division instead of
9 592 moduli) and Φ_{ℓʲ}(q) by the direct formula ((q^{ℓʲ} − 1)/(q^{ℓʲ⁻¹} − 1)) instead
of `cyclotomic_poly`.

### 5.3 Effect on k ≤ 8

| k | nodes (Block 4) | nodes (Block 5) | complete sets | last unknowns solved | time |
|---|---|---|---|---|---|
| 6 | 51 | 55 | 0 | 1 | 0.6 s |
| 7 | 549 | 459 | 40 (was 153) | 5 | 1.3 s |
| 8 | 210 456 | 90 032 | 23 931 (was 145 659) | 537 | 36 s |

Same verdict in all (0 friends, 0 `NaoCertificavel`); the solver never produced a
candidate for k ≤ 8 (`candidatos_ultimo = 0`): every open case with s = 1 dies by
non-existence of a solution.

Official script output (`python experiments/elimina_omega_k.py --k-max 8`, lines for
k = 7 and 8):

```
omega = 7: nos=459 mortos_min=0 ramo_i=46 particoes=172 ramos_expoente=0 caudas=0 conjuntos_completos=40 completos_mortos_indice=247 com_primo_grande=0 casos_sem_fecho=41 ultimos_resolvidos=5 candidatos_ultimo=0 folhas=0 amigos=0 tempo=0.7s
omega = 8: nos=90032 mortos_min=193 ramo_i=361 particoes=45254 ramos_expoente=323 caudas=323 conjuntos_completos=23931 completos_mortos_indice=20654 com_primo_grande=0 casos_sem_fecho=467 ultimos_resolvidos=537 candidatos_ultimo=0 folhas=0 amigos=0 tempo=36.8s
```

### 5.4 k = 9: the wall moves — almost-tight nodes with s = 2

The node of §4.8 was not a node with s = 1: it was the **parent**,
C = {5,7,11,13,31,97,52361} with **s = 2** and prod_sup = 9/5 − 1.76·10⁻⁸. With two
unknowns the index bounds only the smaller one, U₁ < ~2·10⁸ (≈ 11 million primes), and
each child (s = 1) is now solved in ~1 ms by the solver — but there are 11 million
children (~3–4 h for this node alone, and it is not the only one). Thackeray's programme
(arXiv:2310.15900, section 3) enumerates the same kind of interval (B_low, B_high) of
its Proposition 3 and took 25 h of CPU for k = 9; k = 8 took 28 500 s there, against
36 s here — the difference is the partition by budgets + tails + solver, not brute force.

Why the solver does not extend to s = 2 directly: if U₁ carries a budget,
Φ_ℓ(U₁) = ℓ^ε·K·U₂^f with K over C_ℓ; f = 0 is the solved case, but f ≥ 1 leaves U₂
(with no index bound) inside the equation, and the same holds for the free exponents of
the q ∈ C_ℓ. Closing this requires bounds on v_{U}(q^{ord} − 1) — Thackeray's "special
primes" (Corollary 6 with c bounded by Proposition 9: a finite computation of
generalised Wieferich) — or a global bookkeeping of v_r that the project does not yet
have. Recorded in FAILURES.md as the current dead end, with what to keep.

**Addendum — the 12 h run.** k = 9 ran for 12 h (the limit) and **did not finish**:
196 048 873 nodes, 20 857 084 complete sets, 15 911 216 killed by the cheap pruning,
4 172 676 tails, 1 518 505 sets with one large prime; 0 friends in what was explored —
which **certifies nothing**. When stopped it was in the family
C = {5,7,11,13,31,97} + p₇ (a₁ = 2, ∏sup = 9/5 − 3.4·10⁻⁵): p₇ goes by the index from
52 361 to ~157 000 (9 084 primes) and each child with s = 2 enumerates U₁ up to
2/δ(p₇), with δ(p₇) = (9/5)/(∏sup·sup(p₇)) − 1 ≈ 1.9·10⁻⁵ − 1/p₇ — 5.4 million primes at
p₇ = 52 361 (the near-cancellation), tens of thousands at the neighbours. In 12 h it
advanced from p₇ = 52 361 to 54 251; the whole family would take days, and it is not
the only one.

I analysed live the natural idea of tightening the interval from below: with
x = ∏ I(U_i^{a_i}) > 1 + 1/U₁ and x ≤ (9/5)/prod_min, one has U₁ > B_low = 1/((9/5)/prod_min − 1),
and the tails push prod_min → prod_sup. Not enough: B_high assumes the s unknowns all
≈ U₁ and B_low assumes the other s − 1 huge, so the interval tends to
[1/(r − 1), s/(r − 1)] with r = (9/5)/prod_sup — an inherent width of a factor s. In the
family above, with all tails at infinity: s = 3 gives [52 333, 157 001] (9 084 primes);
the child p₇ = 52 361 (s = 2) gives [1.03·10⁸, 2.05·10⁸] (5.4 million). Index bounds,
alone, do not close almost-tight nodes.

What closes them, from the reading of the note on arXiv:2310.15900 (§2, Cor. 6 and
Prop. 9): a **finite bound for the exponent of a known prime r** —
a_r ≤ (k − 1)² + c − v_r(I(N)), where (k−1)² counts the levels v_r(a_q + 1) (each level
requires a distinct witness ≡ 1 mod rʲ, as in our universal bound for a₁, which is the
case r = 5 with c = 0) and c sums the "Wieferich excesses" v_r(q^{ord_r(q)} − 1) − 1 of
the q ∈ S with ord_r(q) | a_q + 1 — computable for q ∈ C and bounded for the unknowns
≤ L by Proposition 9 (Lemma 8: the solutions of x^{r−1} ≡ 1 mod r^a are the Hensel lifts
y^{r^{a−1}} mod r^a, y = 1..r−1; if the smallest of them is > L, no q ≤ L has level ≥ a).
With a_r finite, the tail of r becomes exact branches, and each σ(r^{a_r}) closes in
S ∪ {3} with pins — exactly what Thackeray used with (r, log_r L, δ) = (31, 14, 1) and
(19531, 6, 1) at the last two levels. **Candidate Block 6:** re-derive Corollary 6 (own
proof + adversarial), implement Proposition 9 and apply the bound to the known primes of
the almost-tight nodes.

### 5.5 Labels

No new statement: ω(N) ≥ 9 (Result I) keeps the conditional label of Block 4, now with
the k = 8 tree reduced by 2.3× and the same verdicts. `omega_k.py` remains **without its
own adversarial pass**; the list of targets of §4.8 gains item (viii): the completeness
of the solver (the argument "one ℓ suffices" and the treatment of ε for ℓ ∈ {3, 5} in
the (0, 0) case).

---

## Block 6 — Finite exponent bound (Thackeray's Cor. 6 + Prop. 9): implemented, sound, and still inert

Approved objective (§5.4): re-derive Corollary 6 and Proposition 9 of arXiv:2310.15900
and apply them to the almost-tight nodes. The block delivered both pieces with own
proof, tests against brute force and a soundness hole caught and closed by the battery —
and ended with an honest negative result: in its **sound** form, the bound never fires at
the real nodes of k ≤ 8, and the gain the first version showed came from an unsafe
bound. The diagnosis of why is the main product of the block and defines Block 7.

### 6.1 Corollary 6 re-derived (header of `core/omega_k.py`, block "FINITE bound")

For r ∈ S (r ≠ 3): v_r(σ(N)) = a_r + v_r(num) − v_r(den) = Σ_{q ≠ r} v_r(σ(q^{a_q}))
[σ(N) = num·N/den; sign corrected in Block 7 — the text had − v_r(num) + v_r(den), which
contradicts the bound below and gives a₁ + 1 instead of a₁ − 1 for r = 5], and
with a_q even and o = ord_r(q) (LTE): the contribution of q is v_r(a_q + 1) if o = 1;
w_r(q) + v_r((a_q+1)/o) if o is odd > 1 and o | a_q + 1; 0 otherwise, where
w_r(q) = v_r(q^o − 1) ≥ 1 is the Wieferich level of q at r.

- **Levels.** r^j | (a_q+1)/o (j = 1..v) ⟹ Φ_{r^j o}(q) | σ(N) has a primitive prime t_j
  with ord_{t_j}(q) = r^j o (Zsygmondy, no exception), hence t_j ≡ 1 (mod r^j),
  t_j ∈ S∖{q, r} (t_j ≠ 3; t_j ≠ r since o < r^j o), distinct per level. With
  W_j = {t ∈ C∖{r,q} : r^j | t − 1} (nested) and the unknowns as wildcards, the maximal
  level is the largest v with |W_j| + #wildcards ≥ v − j + 1 for every j ≤ v (Hall for
  nested sets). It is the universal bound of Block 3 generalised: r = 5 is the case
  without a Wieferich term (ord₅ ∈ {1, 2, 4}).
- **Wieferich (Prop. 9).** For q ≢ 1 (mod r): w_r(q) ≥ a ⟺ q^{r−1} ≡ 1 (mod r^a)
  [(Z/r^a)* is cyclic; q^o ≡ 1 (mod r^a) iff ord_{r^a}(q) = o iff ord | r−1] ⟺
  q ≡ y^{r^{a−1}} (mod r^a) for some y ∈ 2..r−1 (the r−1 images are the subgroup of
  order r−1; y = 1 is excluded by q ≢ 1). Hence q ≥ m_a(r) := min_y (y^{r^{a−1}} mod
  r^a), and q < m_a(r) ⟹ w_r(q) ≤ a − 1. For known primes, w_r(q) is exact by
  pow(q, r−1, r^a); odd order by q^{(r−1)_odd} ≡ 1 (mod r) — nothing requires factoring
  r − 1. For unknowns ≤ L, ω_max(r, L) = a − 1 for the least a with m_a(r) > L
  (cost O(r) per level; `R_MAX_PROP9`).
- **Bound.** a_r ≤ v_r(den) − v_r(num) + Σ_{q fixed} v_r(σ(q^{a_q})) + Σ_{q free, o odd}
  [w_r(q)·[o > 1] + level(q)] + s·(ω_max(r, L) + level(unknown)), with
  level(q) ≤ ⌊log_r(M_q + 1)⌋ if q already has an upper bound M_q.

Verification: `test_prop9_nivel_wieferich_contra_forca_bruta` (r ≤ 31, primes up to
10⁵: real w_r(q) ≤ bound; every q < m_a(r) has level < a; 3¹⁰ ≡ 1 mod 11² ⟹ w₁₁(3) = 2),
`test_cor6_majora_os_expoentes_de_amigos_plantados` (at partial nodes of three planted
signatures the bound is ≥ the true exponent).
[Corrected in Block 7: this paragraph ended with "the bound for 5 reproduces the
universal one of Block 3". It does not. Mathematically r = 5 has no Wieferich term,
but the code adds s·ω_max(5, L) for the unknowns all the same, so for s ≥ 1 its bound
for 5 is looser than the universal one (and for s = 0 it can be smaller, e.g. 4
against 7 at C = {5, 11, 31, 41}). The claim was never tested and is inert: 5 is always
committed where Cor. 6 is called, so r = 5 is never bounded this way.]

### 6.2 The soundness hole in the bound L on the unknowns — caught by the test

The Wieferich bound of the unknowns requires a bound L on ALL of them. I derived it
level by level from the index: at the level with t remaining, sup(U)^t > R := (9/5)/prod_sup
and (U/(U−1))^t ≤ e^{t/(U−1)}, ln R ≥ (R−1)/R, R < 2 give U < 1 + 2t/(R − 1); at the
next level, with R − 1 = a/b reduced, R′ − 1 = (aU − a − b)/(bU) has a denominator
dividing b·U ≤ b·L₁, hence R′ − 1 ≥ 1/(b·L₁) — **if the numerator is positive**. In
general it is not: R′ > 1 ⟺ U > B_min := 1 + 1/(R−1). The children with U₁ ≤ B_min
have prod_sup ≥ 9/5 and **no** index bound for the following unknowns; the recursion
assumed positivity silently. What caught it was `test_cota_L_desconhecidos_e_uma_cota`,
which compares the bound with the real index loop in the child: it failed at
738 786 089 > L = 738 786 049 (the first prime above L, in a child without a bound).
Before that, an intermediate version (raw denominator 5·σ(5^{a₁})·∏q, which forgot the
σ(q^{a_q}) of the fixed primes) was also unsafe, and the "exact" version was so loose
after a large fixed exponent (b ∋ σ(31⁴⁰)) that k = 8 went from 18 s to > 10 min.

Final, sound version: L only exists when every unknown is bounded without a partition
— s = 1 (L = L₁) or s = 2 with lo ≥ B_min (then L = 1 + 2·b·L₁; replaced in Block 7 by
the exact bound of §7.3, item 4); s ≥ 3 → no L.
`_ramos_cor6` refuses in the other cases. With that the bound **never fires** for k ≤ 8
(`cor6_ramos = 0`): the almost-tight nodes always have lo < B_min. The k = 8 tree
returns to the 90 032 nodes of Block 5 (same verdict).

Also left in the code, sound and tested: `maximos` in the state (upper exponent bounds
are facts about the friend, inherited by every descendant and only ever improved; they
enter prod_sup, bound the tails and filter the lists), and the **total-closure lemma**:
with all known exponents fixed and no σ(q^{a_q}) with a prime outside C ∪ {3}, each
unknown U only divides σ's of unknowns, hence ∏_U σ(U^{a_U}) = (∏_U U^{a_U})·K with K
an integer over C ∪ {3}, and x = (9/5)/∏_C I(q^{a_q}) = ∏_U I(U^{a_U}) = K would be an
integer in (1, 9/5) — the node dies (`fecho_total_mortos`; unit-tested by simulating
"no new prime"). It did not fire for k ≤ 8 (no node arrives with everything fixed and
no pins).

### 6.3 Why the index degenerates, exactly, and how to break it (Block 7)

At the almost-tight node {5,7,11,13,31,97,52361} + U₁ + U₂ (a₁ = 2, prod_sup = 9/5 − 1.76·10⁻⁸,
R − 1 = 9.76·10⁻⁹ [corrected in Block 7: the text gave 1.76·10⁻⁸ as R − 1]):
B_min = 1.03·10⁸ and L₁ = 2.05·10⁸. The half (B_min, L₁] has a bound L₂ and Cor. 6
would apply; the half (lo, B_min] — 5.9 million primes — is where prod_sup·sup(U₁)
≥ 9/5, and each child goes to the tails. The enumeration is in the "unbounded" half,
which Cor. 6 does not reach. But precisely there the **tails** reach, if the node knows
that the smallest unknown is ≤ B′: I(U₁^{a}) ≥ I(B′²) is a known factor of prod_min, and
prod_sup(C)·I(B′²) > 9/5 (the definition of B′) guarantees that the chain of tails kills
— without enumerating U₁. Proposal for **Block 7**: split the node into (a) "smallest
unknown ≤ B′", with `hi = B′` in the state and the virtual factor I(B′²) in prod_min
(exact tails + total-closure lemma in the branches with everything fixed), and (b) "all
> B′" (lo := B′), where s = 2 gains Cor. 6 and s ≥ 3 enumerates an already reduced
interval. All with the same termination measure (s, #free, m).

### 6.4 Official script output and labels

`python experiments/elimina_omega_k.py --k-max 8` (k = 6, 7, 8):

```
omega = 6: nos=55 mortos_min=0 ramo_i=16 particoes=29 ramos_expoente=0 caudas=0 conjuntos_completos=0 completos_mortos_indice=26 com_primo_grande=0 casos_sem_fecho=3 ultimos_resolvidos=1 candidatos_ultimo=0 cor6_ramos=0 cor6_mortos=0 folhas=0 amigos=0 tempo=0.7s
omega = 7: nos=459 mortos_min=0 ramo_i=46 particoes=172 ramos_expoente=0 caudas=0 conjuntos_completos=40 completos_mortos_indice=247 com_primo_grande=0 casos_sem_fecho=41 ultimos_resolvidos=5 candidatos_ultimo=0 cor6_ramos=0 cor6_mortos=0 folhas=0 amigos=0 tempo=0.9s
omega = 8: nos=90032 mortos_min=193 ramo_i=361 particoes=45254 ramos_expoente=323 caudas=323 conjuntos_completos=23931 completos_mortos_indice=20654 com_primo_grande=0 casos_sem_fecho=467 ultimos_resolvidos=537 candidatos_ultimo=0 cor6_ramos=0 cor6_mortos=0 folhas=0 amigos=0 tempo=55.4s
```

No new statement; ω(N) ≥ 9 (Result I) keeps the conditional label; k = 9 remains open
(§5.4). Additional targets for the adversarial pass: (ix) the derivation of Cor. 6
(levels, Wieferich, the sign v_r(den) − v_r(num)); (x) the bound L and the condition
lo ≥ B_min; (xi) the total-closure lemma (the integrality of K and the exclusion of the
case x integer by the target 9/5).

---

## Block 7 — Splitting near-tight nodes at B_min; adversarial pass of the recursive certifier; ω = 9 closes

Approved objective (§6.3): stop enumerating the smallest unknown prime at near-tight
nodes by splitting on its position relative to B_min. Delivered, together with seven
further tightenings that the k = 9 runs forced one after another, with the adversarial
pass that `core/omega_k.py` had been owing since Block 4, and with a replay audit of the
k = 9 run itself. Outcome: **k = 9 is certified (2 298 715 nodes, 0 friends, no refusal,
about 6 minutes on one core)**, which reproduces the state of the art ω(N) ≥ 10 of
Thackeray (arXiv:2310.15900) by a different method. Nothing here is new mathematics
about the number 10; what is new with respect to the earlier blocks is that the
certifier now reaches the frontier of the literature, and that it has been attacked.

### 7.1 The state field `hi` and the virtual factor

The state becomes (C, s, lo, fixos, minimos, maximos, hi). `hi` (None or an integer)
means "s ≥ 1 and the smallest unknown U₁ satisfies U₁ ≤ hi". Write
v(h) = 1 + 1/h + 1/h² (= I(h²) for h prime; decreasing in h).

- **Virtual factor.** With hi set, I(N) ≥ prod_min · v(hi): I(U₁^a) ≥ I(U₁²) ≥ v(hi), every
  other unknown contributes a factor > 1, and every known prime at least its prod_min
  factor. The node is dead if prod_min·v(hi) > 9/5, or = 9/5 with s ≥ 2; also if
  s = 0, or if (lo, hi] holds no prime outside C.
- **Index facts.** Let prod_sup < 9/5, R = (9/5)/prod_sup, B = ⌊1 + 1/(R−1)⌋. For an
  integer U ≥ 2: prod_sup·sup(U) ≥ 9/5 ⟺ U ≤ B. Moreover v(B−1) = sup(B) + 1/(B−1)², so
  prod_sup·v(B−1) > 9/5, while prod_sup·v(h) < 9/5 for every h > B.

### 7.2 The split and why each side closes

At an open (k₅, k₃) pair with s ≥ 2, lo < B − 1 (and B − 1 < hi if hi is already set),
where the tails and Cor. 6 both decline and the index interval of U₁ is long (more
than `LIMIAR_INDICE` = 300 primes; a strategy threshold, both alternatives are
sound), every friend lies in exactly one of:

| case | hypothesis | child | why it closes |
|---|---|---|---|
| (a) | U₁ ≤ B − 1 | same node, hi := B − 1 | the tails of Block 4 apply with prod_min·v(hi) in place of prod_min: their limit prod_sup·v(B−1) exceeds 9/5 |
| (a2) | U₁ = B | pin B (if prime, > lo, ∉ C); lo := B; hi dropped | ordinary pin |
| (b) | U₁ > B | same node, lo := B (hi kept) | prod_sup·sup(U₁) < 9/5, so U₂ has an index bound as well as U₁. For s = 2 that is every unknown, which is exactly where the finite exponent bound of Block 6 is valid; for s ≥ 3 the later unknowns need not have one, and the child enumerates U₁ over the reduced index interval above B (§6.3) |

Inheritance of hi: children without pins inherit it; a child whose pins are all > hi
keeps it (U₁ is still unknown; if no unknown is left the child is dead); a child with
a pin ≤ hi drops it (the pinned prime then contributes at least v(hi) to prod_min
explicitly); the children of the index enumeration drop it, and that loop stops at hi.
With s = 1 and hi set, the last-unknown solver of Block 5 uses U_max = min(hi, index
bound), and applies even when prod_sup ≥ 9/5. Every node that carries hi has a₁
already committed, so its prod_min and prod_sup are those of the node itself.

Termination: order nodes by (s, number of free known exponents). Pins decrease s;
exact branches and a₁ commitments decrease the second entry; tail chains are finite (m
decreases; hi and prod_sup are unchanged along them, so no split occurs inside); after
a split no second split occurs before (s, free) decreases — after (a) the tails apply,
after (b) the precondition lo < B − 1 fails and prod_sup·v(hi) < 9/5 for hi > B. The
kill of the virtual factor runs at node entry, before the tail step (otherwise a node
with prod_min·v(hi) > 9/5 would produce a tail equal to itself).

Effect on the node that defeated Blocks 5 and 6, C = {5,7,11,13,31,97,52361}, s = 2,
a₁ = 2 (prod_sup = 9/5 − 1.76·10⁻⁸, R − 1 = 9.76·10⁻⁹, B = 102 507 528): before, an
enumeration of ~11 million primes (hours); now **54 nodes, 0.1 s**, with the index
enumeration never used (`test_block7_near_tight_k9_node_closes_without_enumeration`).
(The message of the first commit of this block says 57 nodes and 0.2 s; that was the
count before tightening 4 of §7.3.) In case (a) the margin is tiny (v(B−1) exceeds
sup(B) by 1/(B−1)² ≈ 10⁻¹⁶), so every free prime has to be pushed by a tail — six tail
edges, with thresholds a₅₂₃₆₁ ≥ 4, a₉₇ ≥ 8, a₃₁ ≥ 10, a₁₃ ≥ 14, a₁₁ ≥ 16, a₇ ≥ 20 — and
each exact branch dies at its closure or one node later (25 of the 30 at the closure;
the other 5 pin one new prime, and that child, with s = 1, dies without descendants).

Precision about the title of the proposal: the smallest unknown is no longer
enumerated *at the split*. Short index intervals (up to `LIMIAR_INDICE` primes) are
still enumerated, also under hi (9 such nodes at k = 8, up to 256 primes each).

### 7.3 Seven tightenings forced by k = 9

Each was found by a stack watchdog on a stalled k = 9 run, or by the adversarial pass
of §7.4; each is sound on its own.

1. **Prop. 9 incrementally.** The Teichmüller lifts are compatible across levels: if
   x ≡ y^{r^{a−1}} (mod r^a) then x^r ≡ y^{r^a} (mod r^{a+1}). One exponentiation by r per
   residue and level replaces exponents r^{a−1}; only the minima m_a(r) are cached.
   Checked against the direct definition
   (`test_teichmuller_minima_match_the_direct_definition`). Near-tight node: 38 s → 3 s.
2. **Cheap primes first in the Cor. 6 branching.** The Prop. 9 term costs O(r) per
   level. In case (b) lo is huge, so exact branches of small primes die at once (their
   pins would have to exceed lo); the bound of an expensive prime
   (r > `R_CHEAP_PROP9` = 2000) is computed only if no cheap prime can be branched.
   3 s → 0.2 s.
3. **Coprime-base refinement of unfactored residues.** A composite cofactor beyond
   the factoring budget hides ≥ 2 unknown primes. Residues of *different* closures may
   share primes with each other and with pins identified elsewhere. Residues and pins
   are now refined into a pairwise coprime base by gcds: coprime residues add up (two
   coprime residues need ≥ 4 unknown primes — dead with s ≤ 3), and a common factor
   is revealed and becomes a pin. k = 8, measured with the Block 6 bound L still in
   place (before item 4): 72 945 → 18 551 nodes; with the exact L of item 4 the k = 8
   tree has 18 390 nodes with or without this refinement. The refinement also closed
   a false kill latent since Block 4 (§7.4, defect 2).
4. **Exact bound L for s = 2.** Block 6 used L = 1 + 2·b·L₁ with b the reduced
   denominator of R − 1 — valid, but b is astronomically large once exponents are fixed
   or bounded (b ~ 10²⁶⁰ at real nodes), which made the Wieferich levels useless and
   slow. With lo ≥ B: U₁ ≥ U_min (least prime > lo outside C), so
   R′ = R(U₁−1)/U₁ ≥ R(U_min−1)/U_min > 1 and U₂ < 1 + 1/(R′_min − 1): of the order of
   L₁², no denominators. The test compares it with the real index loop of every child
   and checks it is nearly attained at the first child.
5. **Dead prefix of the index loop skipped exactly.** Every q below the least q with
   prod_min·v(q) ≤ 9/5 gives a dead child; that q is computed by an integer square
   root (`_first_live_q`) instead of walking the primes. Equivalence with the unskipped
   loop is tested on five nodes.
6. **Memory.** A k = 9 run grew to 2.8 GB: the statistics kept every complete set and
   every pin, and the memo caches were unbounded. Long runs use a light mode (counters
   only) and the `lru_cache` memos of `core/omega_k.py` and `core/cadeias.py` are
   bounded to 2¹⁶ entries (`I_pp`/`sup_pp` of `core/motor.py` and the Teichmüller minima
   stay unbounded, and small); the run stays near 100 MB.
7. **Per-feeder cap in the budget enumeration.** The partition by the v₅ budget
   enumerated every vector (k_q) over the known primes ≡ 1 (mod 5) with Σ k_q ≤ a₁ − 1,
   that is C(T + c, c) vectors, and only then tested each. At the child a₁ = 54 of the
   k = 9 root (σ(5⁵⁴) has exactly the primes 11, 71, 103511, 511831, 12207031,
   65628751, 190295821; T = 53, c = 7) that is C(60, 7) = 386 206 920 vectors — about
   three hours inside one node, silently (extrapolated: the 18 643 560 vectors of the
   a₁ = 34 node took 581 s). But the first test applied to a vector (more than s
   levels of q without a witness in C) depends only on (q, k_q) and is monotone in
   k_q, so the largest admissible k_q is computed once per feeder and the enumeration
   never goes beyond it. The case list is
   identical (tested on every affordable real call of the k ≤ 7 trees and on the whole
   k = 7 tree); the two nodes above take 0.1 s; k = 8 drops from 15–23 s to 2 s with
   the same 18 390 nodes. A guard (`MAX_ASSIGNMENTS`) turns any remaining blow-up into
   an honest refusal, after counting the vectors exactly. A side effect on the
   statistics only: `casos_sem_fecho` now counts fewer cases (28 against 41 at k = 7,
   338 against 467 at k = 8), because pruned vectors no longer reach that counter.

### 7.4 Adversarial pass of the recursive certifier

Set-up: independent reviewers, each on a frozen copy of the code, exact arithmetic
only, instructed to refute and to report anything they could not check. Ten claims of
this block (index facts, completeness of the split, virtual factor, tails under hi,
pin rules, index under hi, solver under hi, termination, the lo invariant, strategy
independence) were each attacked twice, once as mathematics and once against the
code. Their frozen copy was the commit *before* this block (the Block 6 code, without
`hi` and without the split): the claims were attacked as a specification, against the
machinery they extend and against models and prototypes of the split written by the
reviewers, not against the implementation. The eleven targets accumulated since
Block 4 (§4.8 (i)–(vii), §5.5 (viii), §6.4 (ix)–(xi)) were attacked once each, on the
first commit of this block. Every claimed refutation went to two further reviewers,
also on that commit, instructed to dismiss it if they could.

**Verdicts.** No false kill and no false certificate were found in the code as
committed. Claims: 19 of 20 reviews not refuted; they speak for the mathematics and
the design of the split, not for its implementation. The remaining review (claim 10,
code) reported two holes of the older code, both real there (defects 1 and 2 below);
both were closed in the first commit of this block, which is why the two second
reviewers, working on that commit, dismissed the refutation. Targets: 9 of 11 not
refuted; 2 refutations confirmed twice, neither about soundness (defects 4 and 6).

| Target | Verdict | Decisive evidence reported |
|---|---|---|
| (i) tails (`_ramos_expoente`) | not refuted | ~150 000 random states (30 925 branching), the 869 real calls of k ≤ 8, ~1 900 planted runs through a generic partition, three mutants all detected |
| (ii) witness count and forced k (`_casos_ell`) | sound; **stall confirmed** | ~91 000 model-based trials with planted consistent configurations, exact comparison with an independent specification on 3 670 real nodes; the silent stall of tightening 7 |
| (iii) `_viavel_m0` | not refuted | 230 160 calls against an independent Hall test; the 5 208 real kills of k ≤ 8 re-checked by brute force over the primes of an interval |
| (iv) closures, residues and gates | not refuted; **float found** | 80 064 closure calls against full factorisation over four factoring budgets; gate monotonicity on ~6 000 real nodes; defect 3 |
| (v) complete sets (s = 0) | not refuted | 21 807 list comparisons with brute force; 16 439 planted runs including the equality cases |
| (vi) large-prime lemma | not refuted | ~6 900 closure-built sets covering every case of the lemma; 930 planted runs |
| (vii) a₁ bound, "pin ≤ lo is dead" | not refuted | instrumented runs k ≤ 8 (18 921 nodes, 0 violations of five invariants); differential of the real partition on 6 185 nodes |
| (viii) last-unknown solver | not refuted | 1 257 planted (U, a) with 4 626 solver calls; 2 500 random C against full brute force; replay of the 706 real calls of k = 8 |
| (ix) Cor. 6 | code sound; **written derivation wrong** | ~113 000 planted-node checks of A_r ≥ a_r, ~9 400 firings on planted s = 2 nodes; defect 6 |
| (x) bound L, lo ≥ B_min, Prop. 9 | not refuted | 5 147 nodes against exact extremal search; ~4 000 planted N₀ built from Wieferich gadgets; the 17 real firings of k = 8 recomputed independently |
| (xi) total-closure lemma | not refuted (and inert) | 2 494 random all-fixed states against full factorisation; 0 firings in 371 938 partitions of a partial, time-boxed k = 9 run (the complete run of §7.5 also has 0, in 1 338 903 partitions) |

**Defects found, all fixed in this block.**

1. *Total-closure lemma with skipped pieces (latent unsoundness, since Block 6).* The
   lemma needs "no σ(q^{a_q}) has a prime outside C ∪ {3}", but a cyclotomic piece
   skipped by the size gates was treated as examined: C = {5, 31} with a₃₁ = 210 was
   declared dead although 2111 and 4643 divide σ(31²¹⁰). The lemma now requires every
   piece of every fixed prime to have been examined. It never fired in any run
   (`fecho_total_mortos = 0` for k ≤ 9), so no certificate depended on it.
2. *Order-dependent double count (latent unsoundness since Block 4; found on the
   Block 6 code).* A pin identified from a later fixed prime that divides the
   unfactored residue of an earlier one was counted twice (1 + 2 > s): with C = {5,7,11,13,31,97,60013,20849069},
   s = 2 and the fixed exponents taken in the order (5², 20849069⁴, 97⁴) the node was
   declared dead, although its closure needs exactly the two new primes 262321 and
   720300353869246791671341 and the node is index-alive; in the order (5², 97⁴,
   20849069⁴) it was not. Tightening 3 had already removed it when the reviewer found
   it on the older code; both second reviewers then failed to revive it (53 640
   node-and-order checks on 3 492 fuzzed nodes, and 7 500 fuzzed nodes in up to 24
   orders each, judged against full factorisation: 0 false kills; the old count,
   emulated with the same generators, gives 699 false kills in 4 636 checks of a
   separate run of the first and 3 269 on the same 7 500 nodes of the second).
   According to the reviewer's
   audit of the Block 6 trees, that kill line never fired for k = 7, 8, and none of
   the analogous kills in the budget closures (82 at k = 7, 635 at k = 8) shared a
   prime; the same count, repeated on the code of Blocks 4 and 5 while this report
   was being checked, gives the same figures (no firing for k ≤ 8). The earlier
   certificates did not depend on it. Regression test:
   `test_unknown_count_does_not_depend_on_the_order_of_the_fixed_primes`.
3. *A float inside a kill path.* The cofactor classification used
   `sympy.perfect_power`, which filters odd exponents with a floating-point
   comparison for bases below 2⁴⁰. A false negative would turn a prime power into
   "composite, ≥ 2 unknown primes" and could kill a node. No failing input was found
   (worst observed deviation 0.0061 against a threshold of 0.01), but rule 1 forbids
   it. Replaced by an exact integer root (Newton iteration on integers) with r^e = c
   verified; tested on prime powers with bases around 2²⁰, 2³³, 2⁴⁰, 2⁶¹.
4. *Silent stall* — tightening 7. A certifier that does not answer is as useless as
   one that answers wrongly; two k = 9 runs were lost to it, each stopped after more
   than 45 minutes without output.
5. *Refusals instead of loops or asserts.* A case with prod_min·v(hi) > 9/5 is dead
   instead of yielding a tail equal to its parent; the last-unknown solver declines as
   a whole beyond a size gate; the index enumeration refuses intervals longer than
   2·10⁸ instead of walking them. One item of this kind is older: the case
   de-duplication compares (lo, hi) as well, because children (a) and (b) of a split
   differ only there; a reviewer noticed on the prototype that (b) would otherwise be
   lost, before the first commit of the block.
6. *Wrong written derivation of Cor. 6.* §6.1 and the code header stated
   v_r(σ(N)) = a_r − v_r(num) + v_r(den); the correct identity is
   a_r + v_r(num) − v_r(den) (for r = 5: a₁ − 1). The code and the displayed bound were
   right. §6.1 also claimed that the bound for r = 5 "reproduces the universal one of
   Block 3": false as stated (the code adds a Wieferich term for the unknowns; the
   bound is looser for s ≥ 1 and is never used for r = 5). Both corrected in place,
   marked. Smaller errors corrected in §4.1, §4.3, §4.6, §6.3 and in docstrings.

**Review of the fixes.** Tightening 7, the exact root of defect 3, and one further
change (in the composite case of the large-prime lemma the divisors of ℓ·e are now
taken from those of e, as div(e) ∪ ℓ·div(e), without factoring) were made after the
pass, so they went to two further reviewers on a frozen copy. None of their ten
claims was refuted.

- *Per-feeder cap.* Pruned and unpruned enumerations give the same case list in
  29 697 random trials, 35 857 engineered configurations and all 9 536 distinct real
  calls of the k = 5, …, 8 trees. At the a₁ = 34 node all C(40, 7) = 18 643 560
  unpruned assignments were run through the unpruned function: same list, same order.
  At the a₁ = 54 node only the 8 575 992 assignments that respect the caps of the
  first three feeders were enumerated unpruned; the other 377 630 928 are excluded by
  those caps and were not run. One defect of completeness was found: the guard
  compared the product of the (k_max + 1) with its limit and ignored Σ k_q ≤ T, so it
  could refuse a small node (ℓ = 3, T = 2, 14 feeders: 2 125 764 against 120 real
  vectors). The guard now counts the vectors exactly; it never fired on a real call.
- *Exact prime-power test.* The integer root is proved (the Newton step never goes
  below the floor root, by AM–GM) and checked on 2 260 169 cases; the classification
  is exhaustive against a sieve for c ≤ 1 500 000 and agrees on about 16 000
  structured inputs (prime powers on both sides of 10⁵, composite exponents, powers
  of composites) and 30 000 end-to-end closure checks. One finding, about cost only:
  on a composite of 20 000 bits the exact test takes about 17 s against 0.05 s for the
  float-filtered routine (prime exponents only would take about 2.6 s). Kept as it
  is; recorded as a candidate improvement.
- *Divisors of ℓ·e.* The identity is proved and checked on 231 077 exhaustive pairs
  and 5 030 special or large ones; old and new code agree on 581 inputs.

**What the pass did not establish** (recorded so that the label stays honest):

- The implementation of `hi` and of the split was not read by the twenty claim
  reviews, which ran on the previous commit (see Set-up). It is exercised by the
  target reviews wherever they meet it, on the first commit of this block, and
  decision by decision by the replay audit, on the snapshot described in §7.6.
- No end-to-end run with a *planted friend* goes through the real partition, because
  the budgets v₅ = a₁ − 1 and v₃ = 2 are specific to the target 9/5. The partition
  rests on derivations, model-based tests and differentials; the planted evidence
  covers everything around it (tails, split, Cor. 6, index, complete sets) through a
  generic stand-in partition.
- In the Cor. 6 bound, mutants with one wildcard fewer are *not* detected by any
  planted test (the unknown term always carries slack); the wildcard counts rest on
  the proof alone.
- Paths that no real run with k ≤ 8 exercises: the (0, 0) mode of the solver, tails
  with `maximos`, Cor. 6 with hi set. The first and the third occur at k = 9 (344
  solver calls and 367 Cor. 6 firings of these kinds, counted by the replay audit of
  §7.6); the second only in part: 2 936 tail calls of k = 9 carry a non-empty
  `maximos`, but none of them branches on a prime that has an upper bound. Paths that
  no real run with k ≤ 9 exercises, so that only unit, planted and differential tests
  cover them: the large-prime lemma for the other primes of a set (the 201 sets with
  a large prime at k = 9 die one step earlier, the large prime itself having no
  admissible exponent), the exact signature test of a complete set (no complete set
  of k = 9 survives the exponent lists), the total-closure lemma, prime-power
  cofactors, a common factor in the coprime-base refinement, a tail whose branching
  prime has an upper bound (exact values stopping at M, no tail), the dead return of
  `_ramos_expoente`, the kill by hi ≤ lo, a split without case (b), and every
  equality branch (a product equal to 9/5).
- `isprime` is documented as definitive only below 2⁶⁴; above that the label assumes
  strong BPSW (no known counterexample). In the environment used here (sympy 1.14.0
  without gmpy2) its fixed Miller–Rabin bases are still deterministic below
  3.317·10²⁴, and BPSW starts there.

### 7.5 Results

`python experiments/elimina_omega_k.py --k-max 9` (k = 6, …, 9), on the code of this
commit:

```
omega = 6: nos=55 mortos_min=0 ramo_i=16 particoes=29 ramos_expoente=0 caudas=0 conjuntos_completos=0 completos_mortos_indice=26 com_primo_grande=0 casos_sem_fecho=3 ultimos_resolvidos=1 candidatos_ultimo=0 cor6_ramos=0 cor6_mortos=0 fecho_total_mortos=0 splits=0 dead_hi=0 folhas=0 amigos=0 tempo=0.5s
omega = 7: nos=459 mortos_min=0 ramo_i=46 particoes=172 ramos_expoente=0 caudas=0 conjuntos_completos=40 completos_mortos_indice=247 com_primo_grande=0 casos_sem_fecho=28 ultimos_resolvidos=5 candidatos_ultimo=0 cor6_ramos=0 cor6_mortos=0 fecho_total_mortos=0 splits=0 dead_hi=0 folhas=0 amigos=0 tempo=0.8s
omega = 8: nos=18390 mortos_min=243 ramo_i=357 particoes=5970 ramos_expoente=311 caudas=311 conjuntos_completos=3642 completos_mortos_indice=8327 com_primo_grande=0 casos_sem_fecho=338 ultimos_resolvidos=487 candidatos_ultimo=37 cor6_ramos=17 cor6_mortos=0 fecho_total_mortos=0 splits=20 dead_hi=208 folhas=0 amigos=0 tempo=1.8s
omega = 9: nos=2298715 mortos_min=18869 ramo_i=10074 particoes=1338903 ramos_expoente=129289 caudas=129289 conjuntos_completos=213615 completos_mortos_indice=585665 com_primo_grande=201 casos_sem_fecho=4128 ultimos_resolvidos=67329 candidatos_ultimo=1304 cor6_ramos=44403 cor6_mortos=4 fecho_total_mortos=0 splits=22653 dead_hi=141663 folhas=0 amigos=0 tempo=308.9s
```

k ≤ 8: same verdicts as before; the k = 6, 7 trees keep the node counts of Block 6
(55 and 459) and the k = 8 tree is much smaller (90 032 nodes and 55 s in Block 6,
18 390 nodes and 2 s now). k = 9: zero friends, zero refusals. For k = 9 the official
run above took 309 s on an otherwise idle machine; the instrumented run below, made
with other runs in parallel, took 546 s.

Cost by a₁ = v₅(N), from one instrumented run on the same code (node counts are
deterministic; the times are those of that run, 546 s in total with other runs in
parallel, and only indicative), next to the times of Table 1 of arXiv:2310.15900
(SageMath, a different machine):

| a₁ | first prime set of the subtree | nodes | time here | time in arXiv:2310.15900 |
|---|---|---|---|---|
| 2 | {5, 31} | 993 297 | 226 s | 7 105 s + 3 s |
| 4 | {5, 11, 71} | 164 256 | 32 s | 23 s |
| 6 | {5, 19531} | 740 440 | 210 s | 452 s + 61 s |
| 8 | {5, 19, 31, 829} | 1 558 | 0.1 s | < 1 s |
| 10 | {5, 12207031} | 198 288 | 38 s | 26 721 s |
| 12 | {5, 305175781} | 199 762 | 32 s | 27 642 s |
| 46 | {5, σ(5⁴⁶)} | 4 | 3.5 s | 27 913 s |
| other 14, …, 56 | | 1 109 | 3.8 s | 3 s (14 ≤ a₁ ≤ 64) |

(Plus the root: 1 + 993 297 + … + 1 109 = 2 298 715.) The comparison is between
different machines, languages and methods and says nothing precise about speed. What
it shows is that the profile is different: the three cases that take 7.4 to 7.8 hours
each there (a₁ = 10, 12, 46, with σ(5^{a₁}) prime) are minor here. For a₁ = 46 the
reason is elementary: the index leaves only 7 or 11 as the next prime (and, after 11,
only 13), and the universal bound of Block 3, a₁ ≤ 1 + m(m − 1) with m the number of
known primes ≡ 1 (mod 5) plus the free slots, gives 43 < 46 at {5, 7, σ(5⁴⁶)}
(m = 1 + 6) and at {5, 11, 13, σ(5⁴⁶)} (m = 2 + 5). With one more prime (k = 10) the
same bound gives 57, so that case will open.

Strategy variants of k = 9, on the code of this commit up to comments and docstrings
(one threshold changed; the trees differ, the verdicts must not). The times are those
of runs made partly in parallel and are only indicative; the default row is the
instrumented run of the table above:

| variant | nodes | splits | Cor. 6 branchings / kills | sets with a large prime | friends, refusals | time |
|---|---|---|---|---|---|---|
| default | 2 298 715 | 22 653 | 44 403 / 4 | 201 | 0, 0 | 546 s |
| `LIMIAR_INDICE` = 100 | 1 847 389 | 24 943 | 49 115 / 4 | 168 | 0, 0 | 379 s |
| `LIMIAR_INDICE` = 1000 | 3 973 534 | 20 554 | 39 855 / 0 | 210 | 0, 0 | 732 s |
| `FATORA_BITS` = 60 | 2 424 403 | 23 101 | 57 200 / 4 | 201 | 0, 0 | 527 s |

A fourth variant, `R_CHEAP_PROP9` = 0 (tightening 2 switched off, every O(r) bound
computed at every firing), was run only on the code as it stood before the exact
count in the `MAX_ASSIGNMENTS` guard (§7.4) and was not repeated; it was stopped
after 2 h 12 min without finishing. It gives no verdict at k = 9. The same variant is in the test suite on k = 6, 7, but it is
inert there (the finite exponent bound never fires, so the threshold is never
consulted); on k = 8 it changes the tree (18 383 nodes against 18 390) with the same
verdict. The default threshold is not the best one in nodes (`LIMIAR_INDICE` = 100
needs 20 % fewer).

Tests: 147 green (32 new in this block).

### 7.6 Replay audit of the k = 9 run

The certificate for k = 9 is one run of 2 298 715 nodes that nobody reads. After the
pass of §7.4 the run itself was audited. Six reviewers, one per family of decisions,
each replayed `certifica_omega(9)` on a frozen copy of the code with recording spies
and re-derived every decision of that family with code written from the mathematics
(exact integers and Fractions; the audited functions were never used to check
themselves). A seventh looked for what the six had left uncovered. Every reviewer
reproduced the 19 counters of the official run; two auxiliary replays recorded only
some of them (the node count; the node count, splits and kills by hi), and those
agree. **No defect was claimed.**

| Family | Coverage (always 100 % of the run unless stated) | What was re-derived |
|---|---|---|
| Node entry, index kills, index fallback, children | 2 298 715 nodes | the entry outcome of every node, twice (integers; Fractions): 141 663 kills by hi = 112 127 (s = 0) + 29 524 (prod_min·v(hi) > 9/5) + 12 (no free prime in (lo, hi]); 18 869 kills by prod_min, all strict; 585 665 complete sets dead by index = 31 624 + 554 041; the 10 074 index fallbacks re-enumerated (303 065 children, identical); the 1 995 649 children of partitions identical to an independent construction. Tightest kill margin about 3·10⁻²⁰ |
| Split and tails | 22 653 splits, 209 379 tail calls | B recomputed; prod_sup·v(B−1) > 9/5 > prod_sup·v(B+1) at every split; 20 506 splits into (a)+(b), 2 147 into (a)+(a2)+(b), no child lost; every tail list (129 289) and every refusal to branch (80 090) re-derived |
| Finite exponent bound | 44 407 firings | preconditions (s = 2, lo ≥ B_min), L, and the 189 693 bounds A_r term by term; the 4 kills (two nodes, C = {5,7,11,17,19,2213,19531} and the same with 2221; r = 17 bounded by 8 against a minimum of 12 and 10) confirmed by enumerating all 3 735 and 3 504 admissible pairs of unknowns |
| Last unknown, injective feasibility | 99 355 solver calls, 709 358 feasibility calls | the whole domain (lo, U_max] of the 46 891 distinct list-returning calls by brute force (19 343 629 primes tested exactly): 315 candidates required, 315 returned; every distinct feasibility call (418 273) against an independent matching and a Hall test |
| Closures, pins, dead partitions, budgets | 1 338 903 partitions | every partition re-executed and compared with an independent implementation; 1 225 718 pins, each with a modular certificate; the 653 228 dead partitions re-derived; pruned and unpruned budget enumeration equal on 892 131 of the 892 132 distinct calls (the exception is the a₁ = 54 node, compared feeder by feeder) |
| Complete sets | 213 615 sets | every one dies because some prime has no admissible exponent; the 511 030 exponent lists recomputed; each of the 132 861 distinct sets has an elementary certificate that does not use the branch constraints |

Five of the seven reviewers also planted defects (false kills, a dropped split case,
a dropped exact branch, a wrong prime test: 37 in all) and checked that their own
detectors flagged every one: 26 as in-memory mutations of the code on k = 8 (node
entry 12, split and tails 8, seventh reviewer 6), 5 as in-memory mutations on a
13 389-partition slice of k = 9 (closures), and 6 in copies of recorded calls of
k = 9 (complete sets). The reviewer of the last unknown instead dropped one candidate
from each non-empty recorded list (297 of 297 flagged); the reviewer of the finite
exponent bound planted no defect.

What the seventh reviewer added, on 100 % of the run unless a sample is stated. The
detectors for de-duplication, order, caches, aliasing and the two library primality
calls each flagged a defect planted in memory on k = 8, and the certificate verifier
rejected corrupted and forged chains; the count of swallowed exceptions, the root
check and the two plain re-runs have no negative control:

- *Primality.* Every number the run treats as prime was proved prime by independent
  code: the 33 157 distinct primes that enter some C and the 20 942 values classified
  as prime, by trial division or 13 Miller–Rabin bases below 3.317·10²⁴, and above
  that by 2 699 elliptic-curve certificate chains (up to 1 797 bits) checked by an
  exact integer verifier.
- *Composition.* The only exceptions swallowed are the 10 074 "open cases" refusals
  of a node's own partition, all with prod_sup < 9/5; the case de-duplication drops
  214 810 cases, each identical to one kept; reversing the order of the fixed
  exponents changes nothing in the 852 974 partitions that have at least two; the
  memo caches return what an uncached call returns on a sample (840 825 of the
  92 727 412 calls to seven memoised functions, 0.9 %; the caches of `I_pp` and
  `sup_pp` were not instrumented) and never evict; no node mutates a dictionary of
  its parent.
- *Library primality in two decisions.* The primality of B at the 22 653 splits and
  the next prime in the 53 352 bounds L were redone by trial division.
- *Platform and code identity.* A second interpreter and library version
  (Python 3.12.10, sympy 1.13.2 against 3.13.2 and 1.14.0) gives the same counters.
  The audited snapshot differs from the code of this commit by the exact count inside
  the `MAX_ASSIGNMENTS` guard, which this run never reaches, and by comments and
  docstrings; the code of this commit gives the same counters (§7.5).
- *Root.* The 28 values of a₁ and their 24 sets of pins equal the full factorisation
  of σ(5^{a₁}); a₁ = 44 is dead (10 primes for 8 slots); a₁ = 40, 42, 52 are committed
  without pins.

What the audit shows about the run:

- The equality branches never occur, and neither do the total-closure lemma, a
  prime-power cofactor, or a common factor in the coprime-base refinement (0 of
  88 546 refinements). The large-prime lemma and the signature test are never
  reached (§7.4).
- 97 197 node visits (4.2 %) repeat a state already visited; a memo of states would
  remove them.
- Two firings of the finite exponent bound sit on a node where L is below the least
  admissible unknown: the code branches where it could kill. Performance only.
- The pin counter printed by the script counts cases with pins, not pinned primes;
  it includes 32 647 cases of partitions that are then discarded in favour of the
  index fallback.
- With `FATORA_BITS` = 90 the root leaves Φ₄₁(5), Φ₄₃(5) and Φ₅₃(5) unfactored, which
  is why a₁ = 40, 42, 52 carry no pins.

What it leaves open:

- The composition of the families rests on the derivations. A planted friend cannot
  be driven through the partition of the target 9/5: any integer that satisfies the
  hypotheses the partition uses is a friend of 10.
- Four steps are checked only against a second derivation of the same lemma, not
  against the definition: the witness-level counting of the budgets, the injective
  feasibility test, the universal bound for a₁, and the finite exponent bound in its
  44 403 branchings (all pairs of unknowns were enumerated for the 4 kills and for
  124 branchings only, every 20th of the 2 490 firings with L < 16 384; on those
  branchings the bound was evaluated pair by pair on a subsample of the pairs when
  there were many).
- Branches with no occurrence at k = 9 carry no weight in this certificate and no
  evidence from it.
- Only k = 9 was replayed (k = 8 for the controls); k ≤ 8 has the evidence of §7.4.
- Every run and every replay was made on one machine. The second interpreter and
  library version ran on the same hardware; a run on different hardware is missing.
- Negative controls exist for most detectors of the audit, not for all: the
  tree-only check of the `hi` mechanism in the split family has none of its own (the
  kills by hi and the inheritance of hi are also re-derived by replays that have
  them).
- The audit code, the certificate verifier included, is itself unreviewed, and none
  of it is part of the repository. It is cited here as review evidence, not as a
  result; the label keeps the BPSW assumption.

### 7.7 Labels and what is missing

- **Result J.** Every friend of 10 has **ω(N) ≥ 10**.
  `[PROVED-CONDITIONAL: Theorems A–D and Lemmas/Fact 0 of Phase 0 + Zsygmondy, LTE and
  the Nielsen/Voight valuation formula (classical) + correctness of core/omega_k.py,
  core/cadeias.py and core/omega6.py (adversarial passes §2.5 and §7.4 and replay audit
  §7.6, with the limits listed there: no end-to-end planted friend through the
  9/5-specific partition; BPSW primality above 2⁶⁴) and of the primitives ALVO, I_pp,
  sigma_pp and sup_pp they import from core/motor.py (Block 1 engine, adversarial
  pass §1.5) + correctness of
  sympy.n_order/factorint/isprime/nextprime/primerange/integer_nthroot/cyclotomic_poly/divisors/totient
  in the calls consumed]`. **Not new**: it is Thackeray's theorem (arXiv:2310.15900),
  reproduced by a different method (partition by valuation budgets, closures through
  cyclotomic pieces, tails, split at B_min, last unknown by exact roots; the finite
  exponent bound it also uses comes from Thackeray's own Cor. 6 and Prop. 9,
  re-derived in §6.1) and a different implementation, in minutes. **Not
  load-bearing**: Theorems E and E′ and Result G keep citing the published result.
- Result I (ω(N) ≥ 9) is the k ≤ 8 part of the same run and carries the same label.
- What a result *beyond* the literature (k = 10, i.e. ω(N) ≥ 11) would need first.
  **Candidate Block 8**, in this order:
  1. a target-generic partition (budgets v_r for the primes of the target), so that
     planted friends can be driven through the whole machine end to end;
  2. the primality certificates and an exact verifier inside the repository, with
     tests, so that the label can drop BPSW for the runs;
  3. the open items of §7.6: enumeration of the admissible pairs at every firing of
     the finite exponent bound where it is affordable, an independent derivation of
     the witness-level counting, of the injective feasibility test and of the a₁
     bound written from arXiv:2310.15900 alone, the replay spies on k ≤ 8, a run on
     different hardware;
  4. an adversarial pass of the final code as a whole rather than of a diff;
  5. only then the k = 10 run, whose cost is unknown. Known in advance: the case
     a₁ = 46 opens (§7.5), the a₁ = 54 node appears with s = 2, and the branches that
     never occurred at k = 9 have to be audited as they appear. Cheap gains
     available: a memo of states, the missed prune of §7.6, a faster exact
     prime-power test, a better `LIMIAR_INDICE`, the project's own exact root in the
     last-unknown solver in place of the library call.
