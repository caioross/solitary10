# Research protocol

The aim of this project is a small, new, verifiable contribution to the open question
*"is 10 a solitary number?"* — a new structural constraint, an improved bound, or a
theorem covering the whole family `2p` — documented rigorously enough for a short note.

This is not a "solve it any way you can" project. A wrong result that looks right is
worse than no result at all.

## Notation

- `σ(n)` — sum of the positive divisors of `n`.
- `I(n) = σ(n)/n` — the abundancy index, always handled as an exact `Fraction`.
- `m` and `n` are **friends** when `m ≠ n` and `I(m) = I(n)`. No friend ⇒ **solitary**.
- `I(10) = 18/10 = 9/5`, hence

  > `N` is a friend of 10 ⟺ `N ≠ 10` and `5·σ(N) = 9·N`.

- `ω(n)` — number of distinct prime factors; `p^e ‖ n` means `p^e | n` and `p^(e+1) ∤ n`.
- `I` is multiplicative, `I(N) = ∏ I(pᵢ^{eᵢ})`, with `I(p^e)` strictly increasing in `e`
  and `I(p^e) < p/(p−1)`. Consequently, if `d | n` and `d < n` then `I(d) < I(n)` — in
  particular no friend of 10 is a multiple of 10.

## Known constraints on a hypothetical friend `N`

Every entry below was re-derived, or at least verified numerically, before being used as
a hypothesis anywhere in this repository. Reading notes with exact statements are in
`literatura/`.

| # | Constraint | Source |
|---|---|---|
| 1 | `N` is odd, a perfect square, its least prime factor is 5 (so `2, 3 ∤ N` and `25 \| N`) | Ward 2008 |
| 2 | Some prime `≡ 1 (mod 3)` divides `N` with exponent `≡ 2 (mod 6)`; if unique, the exponent is `≡ 8 (mod 18)` | Ward 2008 |
| 3 | `ω(N) ≥ 7`; primes `p ≡ 1 (mod 10)` and `q ≡ 1 (mod 6)` divide `N`; if `5^{2a} ‖ N` then some prime `p \| N` has `2a+1 ≡ 0 (mod f)`, where `f` is the least odd `f > 1` with `5^f ≡ 1 (mod p)`; writing `N = 5^{2a}·m²`, the integer `m` is not squarefree | arXiv:2404.00624 |
| 4 | **`ω(N) ≥ 10`** — the current record | arXiv:2310.15900 (*Indag. Math.*, 2024) |
| 5 | Upper bounds for the 2nd, 3rd and 4th smallest prime divisors in terms of `ω(N)` | arXiv:2404.05771 (*Resonance* 30, 2025) |
| 6 | A parametric family of upper bounds for the `r`-th smallest prime divisor, effective for `2 ≤ r ≤ 5` | arXiv:2412.02701 (v4) |
| 7 | Not all halved exponents are `≡ 1 (mod 3)`; conditions mod 8 on `σ(5^{2a}) + σ(Q²)`; `N > (25/81)·∏(2aᵢ+1)²`, in particular `N > 625·9^{ω(N)−3}` | arXiv:2504.08295 |

Rows 3 and 6 are stated here as *verified* rather than as printed: the published forms
are stronger, and the gap is documented in `results/FASE_0.md` §10.

Strategic context: the folklore conjecture is that `2p` is solitary for every prime
`p ≥ 5`, of which `10 = 2·5` is the smallest case. The literature attacks one number at
a time — analogous papers exist for 14, 15 and 20 — so any lemma that works for all `p`
at once is worth more than a further result about 10 in isolation.

## Rules of rigour

These are not negotiable.

1. **Exact arithmetic, always.** `int`, `fractions.Fraction`, `sympy.Rational`. Floating
   point is forbidden in any step that supports a mathematical claim; it is allowed only
   for human-readable display.

2. **Every statement carries a label:**
   - `[PROVADO]` / *proved* — complete written proof, adversarially reviewed.
   - `[PROVADO-CONDICIONAL: hypotheses]` — proved modulo explicitly listed inputs.
   - `[VERIFICADO-NUMERICAMENTE: range]` — exhaustively checked over a stated range.
   - `[HEURÍSTICA]` / `[CONJECTURA]`.

   Conditional labels name every external dependency, including the library routines
   whose output the argument consumes.

3. **Three steps before anything is called proved:** (a) a written step-by-step proof;
   (b) an independent numerical verification, implemented without sharing code with the
   thing it checks; (c) an adversarial pass, in which independent reviewers are tasked
   with finding a counterexample, a gap, or a hidden hypothesis — not with confirming.

4. **Novelty requires a search.** Before any result is described as new: arXiv, Google
   Scholar and OEIS are searched for identical or stronger statements, and the search is
   recorded with its date.

5. **Reproducibility.** Every computation cited in a result is a versioned deterministic
   script with a test. Nothing is accepted on the strength of "I ran it in the REPL".

6. **Failures are data.** Every abandoned line of attack goes into `results/FRACASSOS.md`
   with the precise reason it failed.

7. **Divergence is a finding.** When computation contradicts the literature it is
   documented prominently — never hidden, never "adjusted" to agree.

8. **Re-read as an enemy.** Before labelling any proof, read it again looking for the
   error rather than for the confirmation.

## Roadmap

Each phase ends with a report and a commit before the next one opens.

- **Phase 0 — Foundations and reproduction.** Environment and green test suite; sanity
  searches; full-text reading of every paper; re-derivation with complete proofs of the
  basic constraints (odd, square, `25 | N`, least prime 5); the exact lower bound they
  imply; survey of what `formal-conjectures` and mathlib already contain. *Closed.*

- **Phase 1 — A certified computational frontier.** Tree search over prime signatures
  `(pᵢ, eᵢ)` pruned by exact rationals: at each node, the exact attainable interval of
  `∏ I(pᵢ^{2eᵢ})`, pruning as soon as `9/5` becomes unreachable, propagating the
  divisibility forced by `5·σ(N) = 9·N`. Targets: a certified lower bound for the least
  friend of 10, and an attempt to extend the `ω(N) ≥ 10` method toward `ω(N) ≥ 11`.
  *In progress.*

- **Phase 2 — New structural constraints.** New congruences, constraints on exponents,
  and the intersection of the prime upper bounds with `ω ≥ 10`, looking for
  contradictions that eliminate whole families of candidates.

- **Phase 3 — Generalisation.** A uniform theorem for the family `2p`, `p ≥ 5` prime.

- **Phase 4 — Writing and formalisation.** A short note in English, and Lean 4 / mathlib
  formalisation of whichever new lemmas are within reach.

## Repository layout

```
core/         verified utilities (exact arithmetic; everything covered by tests)
tests/        pytest — must be green before any commit
experiments/  search and exploration scripts (reproducible, each with --help)
results/      RESULTADOS.md (labelled statements), FASE_N.md (reports), FRACASSOS.md
literatura/   PAPERS.md plus one reading note per paper, theorems stated verbatim
```

Reports in `results/` and reading notes in `literatura/` are written in Portuguese; they
are being migrated to English. The labels themselves stay in their original form so that
older reports remain searchable.
