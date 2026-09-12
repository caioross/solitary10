# Phase 1 — A certified computational frontier

Opened on 2026-08-20 after the closing of Phase 0. This file is the running report of
the phase; block by block, with a human checkpoint between blocks.

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
congruence prunings of Block 2 — a decision for the human checkpoint.

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
in this round (two were cut by a session limit and relaunched):

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
exactly one "large" prime (≥ 20 sets) produce through the new route **exactly** the
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
   remainders (a prime common to Φ_d(p) and Φ_{d′}(p) divides d/d′ ≤ a + 1 < 10⁵), so
   they count 2 each; remainders of distinct bases may share primes and count 2 in
   total. A piece beyond the Φ gates (`PIN_BITS`, `GRAU_PHI_MAX`) is just less
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

For r ∈ S (r ≠ 3): v_r(σ(N)) = a_r − v_r(num) + v_r(den) = Σ_{q ≠ r} v_r(σ(q^{a_q})), and
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
signatures the bound is ≥ the true exponent), and the bound for 5 reproduces the
universal one of Block 3.

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
— s = 1 (L = L₁) or s = 2 with lo ≥ B_min (then L = 1 + 2·b·L₁); s ≥ 3 → no L.
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

At the almost-tight node {5,7,11,13,31,97,52361} + U₁ + U₂ (a₁ = 2, R − 1 = 1.76·10⁻⁸):
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
