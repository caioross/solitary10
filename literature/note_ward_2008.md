# Reading note — Ward (2008), "Does Ten Have a Friend?"

## 1. Header

- **Title:** Does Ten Have a Friend?
- **Author:** Jeffrey Ward (wardjm@clarkson.edu). Work done at the Auburn University REU in 2007, supported by NSF grant 0353723.
- **Year:** 2008.
- **arXiv:** [arXiv:0806.1001](https://arxiv.org/abs/0806.1001) (v1: 5 Jun 2008; v2: 6 Jun 2008; read: v2). Classification: math.NT; MSC 11A25.
- **Publication:** International Journal of Mathematics and Computer Science, vol. 3, no. 3, pp. 153–158 (2008). No known DOI. (The arXiv page carries no journal-ref; the IJMCS reference is confirmed by the bibliographies of arXiv:2404.05771 and arXiv:2412.02701.)
- **Source read:** full text — PDF downloaded from https://arxiv.org/pdf/0806.1001 (5 pages), with spot checks against the HTML version at https://ar5iv.labs.arxiv.org/html/0806.1001.
- **Length:** 5 pages; 1 numbered theorem (Theorem 1), one numbered list of elementary properties (Section 1.1), no numbered lemmas or corollaries.

## 2. Exact statements

### 2.1 Definitions used in the paper

- σ(n) = sum of the positive divisors of n; I(n) = σ(n)/n ("abundancy ratio" or "abundancy index"); n is perfect iff I(n) = 2.
- Positive integers m and n are **friends** iff m ≠ n and I(m) = I(n). An integer is **friendly** if it has at least one friend. (The paper does NOT use the word "solitary".)
- Explicit distinction from **amicable** numbers (m ≠ n and σ(m) − m = σ(n) − n) — a different concept, mentioned only to avoid confusion.
- Background question (Anderson–Hickerson, [1] of the paper): is the natural density of the friendly integers equal to 1? (Open.)

### 2.2 Elementary properties (Section 1.1 of the paper, numbered list; proofs referred to Laatsch [5] and Weiner [6])

Let m, n be positive integers; all primes are positive.

1. I(n) ≥ 1, with equality only if n = 1.
2. If m | n, then I(m) ≤ I(n), with equality only if m = n.
   (Consequence used in Section 2: if m | n and m ≠ n, then m and n are not friends; in particular a friend of 10 is not a multiple of 10.)
3. If p_1, …, p_k are distinct primes and e_1, …, e_k positive integers, then
   I(∏_{j=1}^k p_j^{e_j}) = ∏_{j=1}^k (∑_{i=0}^{e_j} p_j^{−i}) = ∏_{j=1}^k (p_j^{e_j+1} − 1) / (p_j^{e_j} (p_j − 1)),
   the analogue of the formula for σ: σ(∏ p_j^{e_j}) = ∏ (∑_{i=0}^{e_j} p_j^{i}) = ∏ (p_j^{e_j+1} − 1)/(p_j − 1).
4. I is weakly multiplicative: if gcd(m, n) = 1, then I(mn) = I(m)·I(n).
5. (Swapping primes for smaller ones.) If p_1, …, p_k are distinct primes, q_1, …, q_k are distinct primes, e_1, …, e_k are positive integers and p_j ≤ q_j for j = 1, …, k, then
   I(∏_{j=1}^k p_j^{e_j}) ≥ I(∏_{j=1}^k q_j^{e_j}),
   with equality only if p_j = q_j for every j.
6. If the distinct prime factors of n are p_1, …, p_k, then I(n) < ∏_{j=1}^k p_j/(p_j − 1) (strict inequality).
   The justification given: by property 3 and by the observation that, for p > 1, I(p^e) = (p^{e+1} − 1)/(p^{e+1} − p^e) = (p − p^{−e})/(p − 1) **increases strictly in e** with limit p/(p−1) as e → ∞.

**ERRATUM IN THE PAPER (numbering):** the printed list ends at item 6 (checked in the PDF and on ar5iv), but the text of item 6 itself and the proof of Theorem 1 refer to a "property 7" ("Although related to 5, 7 is most easily seen…"; "applying 6 and 7 of Section 1"; "will use 5, 6, and 7 from Section 1"). Apparently an earlier version had 7 items (the extra one being the strict monotonicity of I(p^e) in e with limit p/(p−1), now folded into the explanation of item 6) and the cross-references were not updated. The mathematical content used is unambiguous: monotonicity under divisibility (item 2), prime swapping (item 5), the bound ∏ p/(p−1) (item 6) and the growth of I(p^e) in e. When citing, use the statements, not the numbers.

### 2.3 Remarks in Section 2 (unnumbered in the paper)

- If m and n are friends and k is a positive integer with gcd(k, m) = gcd(k, n) = 1, then mk and nk are friends (by property 4). The paper asserts (without a detailed proof) that the set of friendly multiples of any friendly integer has positive (lower) density.
- No prime power has a friend (stated as "easy to see", without proof in the paper). Hence among 1, 2, …, 9 only 6 (perfect) has a friend. The title question (does 10 have a friend?) was asked in [1] (Anderson–Hickerson 1977) and in [3] (Ford–Konyagin) and remains open.

### 2.4 Theorem 1 (the only numbered theorem; faithful statement)

**Theorem 1.** If n is a friend of 10, then:
(a) n is a perfect square with **at least 6 distinct prime factors** (ω(n) ≥ 6), the smallest of which is 5;
(b) at least one prime factor p of n satisfies **p ≡ 1 (mod 3)** and appears in the factorisation of n with **exponent ≡ 2 (mod 6)** (that is, p^{2e} ‖ n with 2e ≡ 2 (mod 6), equivalently e ≡ 1 (mod 3));
(c) if there is **a unique such prime** dividing n, then it appears with **exponent ≡ 8 (mod 18)**.

Reading cautions:
- In (b) and (c) the exponent referred to is the exponent **in the factorisation of n** (the number 2e), not its half e. "Exponent ≡ 2 (mod 6)" means 2e ∈ {2, 8, 14, 20, …}; "exponent ≡ 8 (mod 18)" means 2e ∈ {8, 26, 44, …}. Note that 8 ≡ 2 (mod 6), consistently.
- In (c), "a unique such prime" refers, by the wording of the theorem and its proof, to a unique prime with **both** properties from (b) (≡ 1 mod 3 **and** exponent ≡ 2 mod 6). The proof in fact works under this weaker hypothesis (hence a stronger statement): if p_i is the only prime of n whose factor σ(p_i^{2e_i}) is divisible by 3 — which is equivalent to p_i ≡ 1 (mod 3) with e_i ≡ 1 (mod 3) — then 9 | σ(p_i^{2e_i}) and 2e_i ≡ 8 (mod 18) follows. The special case "unique prime ≡ 1 (mod 3) dividing n" is covered.
- The statement does NOT explicitly say "n is odd" or "25 | n", but both follow immediately: least prime = 5 ⟹ 2, 3 ∤ n; 5 | n and n a square ⟹ 5² | n. Both facts are established inside the proof (n is odd in the very first paragraph; n = 5^{2a}·∏ p_i^{2e_i} with a ≥ 1).

### 2.5 Closing remarks of the paper (unnumbered)

- **Finiteness level by level:** the method of the proof, for each fixed value of k (the number of primes besides 5), reduces the search to **finitely many** possibilities to check: with k = 5 there are finitely many configurations; once exhausted, one moves to k = 6, and so on. (Asserted without details; it is the germ of the pruned tree-search method.)
- **"Theoretical friend of proximity t"** (a definition introduced in the paper): a sequence (n_k) of positive integers with lim_{k→∞} I(n_k) = I(m) and such that the set of all primes dividing some n_k has cardinality t. Example: lim_{k→∞} I(3^k·5) = (3/2)(6/5) = 9/5 = I(10), so (3^k·5) is a theoretical friend of 10 of proximity 2. Open question proposed: does every positive integer have a theoretical friend of finite proximity?

## 3. Proof method of Theorem 1

All elementary arithmetic with properties 1–6; no computation beyond comparisons of explicit rationals.

1. **5 | n, n odd:** I(n) = 9/5 ⟺ 5σ(n) = 9n ⟹ 5 | n; if 2 | n then 10 | n and property 2 (with n ≠ 10) forbids I(n) = I(10). From 5σ(n) = 9n with n odd, σ(n) is odd; n and σ(n) both odd ⟹ n is a square (Weiner's fact [6], via the formula for σ: all factors ∑ p^i odd with p odd forces every exponent even).
2. **3 ∤ n:** if 3 | n, write n = 3^{2a}·5^{2b}·m² with gcd(m, 30) = 1. Since I(3⁴·5²) = 3751/2025 > 9/5 and I(3²·5⁴) = 10153/5625 > 9/5, property 2 forces a = b = 1. Then 9n = 3⁴5²m² = 5σ(3²)σ(5²)σ(m²) = 5·13·31·σ(m²) ⟹ 13, 31 | m ⟹ I(n) ≥ I(3²5²13²31²) = 20191/10075 > 9/5. Contradiction.
3. **ω(n) ≥ 6:** write n = 5^{2a}·∏_{i=1}^k p_i^{2e_i}, distinct primes p_i > 5. If k ≤ 3: I(n) ≤ I(5^{2a}7^{2e₁}11^{2e₂}13^{2e₃}) < (5/4)(7/6)(11/10)(13/12) = 1001/576 < 9/5 (prime swapping + bound ∏ p/(p−1)). For k = 4: (i) I(5²7²11²13²19²) > 9/5 and, by prime swapping, I(5²7²11²13²17²) > 9/5 — together with property 2 this rules out p₄ ∈ {17, 19}; (ii) for p₄ = 23: I(5⁴7²11²13²23²) > 9/5 forces a = 1, and then σ(5²) = 31 divides σ(n) = (9/5)n, so 31 | n — impossible since the primes of n would be {5,7,11,13,23}; (iii) all remaining k = 4 cases fall to two tight inequalities: (5/4)(7/6)(11/10)(13/12)(29/28) = 4147/2304 < 9/5 and (5/4)(7/6)(11/10)(17/16)(19/18) = 24871/13824 < 9/5. Hence k ≥ 5 and ω(n) = k + 1 ≥ 6.
4. **Congruences (b) and (c):** from 5σ(n) = 9n and 3 ∤ n we get 9 | σ(n). For p ≡ 2 (mod 3), σ(p^{2e}) = 1 + p + ⋯ + p^{2e} ≡ 1 (mod 3) (this also covers the factor σ(5^{2a})); hence some p_i ≡ 1 (mod 3) must have 3 | σ(p_i^{2e_i}) ≡ 2e_i + 1 (mod 3), forcing e_i ≡ 1 (mod 3), i.e. 2e_i ≡ 2 (mod 6). If p_i is the only such prime, then 9 | σ(p_i^{2e_i}); checking the cases p_i ≡ 1, 4, 7 (mod 9) gives 2e_i ≡ 8 (mod 18) in every case.

**Independent numerical verification (done during this reading, exact arithmetic with `fractions.Fraction`):** all 9 rational comparisons cited above check out, and the sweep of the mod 9 argument (representatives p = 19, 13, 7 for p ≡ 1, 4, 7 mod 9; exponents 2e ≤ 200) confirms that 9 | σ(p^{2e}) happens exactly for 2e ≡ 8 (mod 18). Two observations the verification brought out:
- The two final inequalities of the k = 4 step are **extremely tight**: 4147/2304 ≈ 1.799913 and 24871/13824 ≈ 1.799117, against 9/5 = 1.8. The method is at the limit of its strength at k = 4 — extending to k = 5 by a single global inequality is hopeless; branch-by-branch pruning is needed (consistent with Ward's own finiteness remark and with the method of arXiv:2310.15900).
- I(5²7²11²13²23²) = 485364861/270438025 ≈ 1.7947 < 9/5: the case p₄ = 23 really does NOT fall to an inequality, which explains the detour through the divisibility argument σ(5²) = 31 | 9n. This pattern (arithmetic pruning when analytic pruning fails) is the key reusable ingredient.

## 4. Fidelity to the overview table (docs/METHODOLOGY.md)

Summary of the table entry under review: "N is odd, a perfect square, least prime divisor = 5 (so 2,3 ∤ N and 25 | N)" + "some prime ≡ 1 (mod 3) divides N with exponent ≡ 2 (mod 6); if unique, exponent ≡ 8 (mod 18)" + "ω(N) ≥ 6 is mentioned as Ward's result in the literature".

| Table item | Verdict | Comment |
|---|---|---|
| N is odd | FAITHFUL | Not literally in the statement of Theorem 1, but proved in the first paragraph of the proof (2 ∤ n) and an immediate consequence of "least prime = 5". |
| N is a perfect square | FAITHFUL | Literal in the statement ("n is a square"). |
| Least prime divisor = 5 | FAITHFUL | Literal in the statement ("the smallest being 5"). |
| Hence 2, 3 ∤ N | FAITHFUL | Correct immediate consequence; both are also proved explicitly in the proof. |
| Hence 25 \| N | FAITHFUL | Not literal in the statement, but a correct immediate deduction: 5 \| N and N a square ⟹ 5² \| N; the proof writes N = 5^{2a}·(…) with a ≥ 1. |
| Some prime ≡ 1 (mod 3) divides N with exponent ≡ 2 (mod 6) | FAITHFUL | Exact, including the delicate point: the exponent referred to is the one in the factorisation of N (2e ≡ 2 mod 6), as in the paper ("appear … to a power congruent to 2 modulo 6"). It is ONE prime with both properties (the table preserves this). |
| If unique, exponent ≡ 8 (mod 18) | FAITHFUL | Exact. Nuance inherited from the paper: "unique" = unique prime with both properties (≡ 1 mod 3 AND exponent ≡ 2 mod 6); the proof holds under this weaker hypothesis, and in particular covers the reading "unique prime ≡ 1 (mod 3)". Neither reading makes the table incorrect. |
| ω(N) ≥ 6 as Ward's result | FAITHFUL | Theorem 1 literally proves "at least 6 distinct prime factors", i.e. ω(N) ≥ 6. The attribution in the literature is correct. Row 1 of the table does not list ω ≥ 6 under Ward, but that is a harmless omission (superseded by ω ≥ 7 and ω ≥ 10 in rows 3–4). |

**Overall verdict: FAITHFUL.** No divergence of content; the items "hence 2,3 ∤ N and 25 | N" are correct immediate deductions and are marked as such ("hence") in the table.

## 5. Use in the project

**To re-derive (Phase 0):** Theorem 1 in full is the natural target of the complete-proof re-derivation required by Phase 0 (odd, square, 25 | N, least prime 5 — and it is worth including ω ≥ 6 and the congruences (b)/(c), which are cheap). The numerical verification of this note (exact rationals + mod 9 sweep) should become a versioned script in `experiments/` with a test.

**Reusable techniques (Phases 1–2):**
1. **All four pruning rules of Phase 1 are already here:** monotonicity under divisibility (prop. 2), exact product formula (prop. 3), swapping primes for smaller ones (prop. 5) and the strict bound I(n) < ∏ p/(p−1) with I(p^e) ↑ p/(p−1) (prop. 6). These are exactly the exact intervals for ∏ I(p_i^{2e_i}) planned for the tree search.
2. **Divisibility propagation through σ:** the trick "exponent of 5 fixed ⟹ σ(5^{2a}) | 9N ⟹ a new prime forced into N" (used twice: 13·31 in the case 3 | n; 31 in the case p₄ = 23) is the rule "propagate the divisibilities imposed by 5σ(N) = 9N" of the Phase 1 roadmap. Crucial because analytic pruning alone fails (the case 23, and the k = 4 inequalities are already within 0.001 of the threshold).
3. **Finiteness level by level:** Ward already notes that, for fixed k, finitely many configurations remain — anticipating the programme of arXiv:2310.15900 (ω ≥ 10). Replicating/extending it toward ω ≥ 11 (Phase 1) is literally the industrialisation of this method.

**For the 2p family (Phase 3):** the skeleton of the proof uses very little that is specific to "10" and is a candidate for uniformisation. For N a friend of 2p (p prime ≥ 5): I(N) = I(2p) = 3(p+1)/(2p) gives 2p·σ(N) = 3(p+1)·N, whence p | N, N odd (otherwise 2p | N), σ(N) odd ⟹ N a square — steps 1–2 generalise almost verbatim. The mod 3/mod 9 step uses 9 | σ(n), which came from 9 = numerator of I(10); for general 2p the analogue is the 3-adic valuation of 3(p+1), which depends on p (mod 3) — this is where the real uniformisation work lies. Recorded as the first concrete attempt of Phase 3.

**Citation warnings:**
- Cite the properties of Section 1.1 by statement, never by number (numbering erratum documented in Section 2.2 of this note).
- The paper does NOT prove ω ≥ 7 nor anything about primes ≡ 1 (mod 10) — that is arXiv:2404.00624 (row 3 of the table), not Ward.
- "No prime power has a friend" is asserted without proof; if the project uses it, re-derive it (it is short: I(p^e) < p/(p−1) ≤ 2 and injectivity of I on prime powers — do it properly in Phase 0 if needed).

---
*Note produced on 2026-08-20 from the full text of arXiv:0806.1001v2 (PDF, 5 pp.). Numerical checks: exact arithmetic (`fractions.Fraction`), script `verifica_ward.py` (scratch; to be promoted to `experiments/` with a test in Phase 0).*
