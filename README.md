# Is 10 a solitary number?

A computational and structural attack on a small open problem in elementary number
theory, run under a strict labelling discipline: every statement in this repository
carries an explicit epistemic tag, and nothing is called *proved* until it has a written
proof, an independent numerical check, and an adversarial review that failed to break it.

## The problem

For a positive integer `n`, let `σ(n)` be the sum of its positive divisors and

```
I(n) = σ(n) / n        (the abundancy index)
```

Two integers `m ≠ n` are **friends** when `I(m) = I(n)`. An integer with no friend is
**solitary**. Whether 10 is solitary is open.

Since `I(10) = 18/10 = 9/5`, the question is equivalent to the solvability of a single
Diophantine condition:

```
N is a friend of 10   ⟺   N ≠ 10   and   5·σ(N) = 9·N
```

Greening's classical criterion (`gcd(n, σ(n)) = 1 ⇒ n solitary`) does not decide the
case, because `gcd(10, 18) = 2`. The wider folklore conjecture is that `2p` is solitary
for every prime `p ≥ 5`; `10 = 2·5` is the smallest instance, and the literature has so
far attacked the family one number at a time (10, 14, 15, 20).

## Status

Let `N` denote a hypothetical friend of 10 and `ω(N)` its number of distinct prime
factors. Results currently in the repository:

| | Statement | Label |
|---|---|---|
| A–D | `N` is odd, a perfect square, divisible by 25, and its least prime factor is 5 | `PROVED` (independent re-derivation of Ward 2008) |
| E | `N ≥ (5·7·11·13·17·19·23·29·31·37)² ≈ 1.53·10²⁴` | `PROVED-CONDITIONAL` (A–D + `ω(N) ≥ 10`) |
| E′ | `N ≥ 49·(5·7·…·37)² ≈ 7.50·10²⁵` | `PROVED-CONDITIONAL` (E + Thm 1.9 of arXiv:2404.00624) |
| F | every friend of 10 has `ω(N) ≥ 6` | `PROVED-CONDITIONAL` (A–D + Zsygmondy; machine re-derivation of Ward 2008 in < 0.1 s) |
| G | the least friend of 10, if it exists, exceeds **10³²** | `PROVED-CONDITIONAL` (A–D + `ω(N) ≥ 10`); 34.5 million exact equality tests, no friend |

Result G certifies, and improves by two orders of magnitude, the uncertified bound
`> 10³⁰` recorded in OEIS A074902 and quoted in the recent literature.

Three discrepancies between the published literature and exact recomputation are
documented in [`results/FASE_0.md`](results/FASE_0.md) §10 — including a lemma that is
false as stated (its downstream use survives a repair) and an off-by-one that weakens a
published corollary. Divergences are reported, never silently reconciled.

Work in progress: divisibility-chain machinery aimed at `ω(N) ≥ 7`, and the uniform
`2p` family.

## Layout

```
core/          verified exact-arithmetic primitives and the certified search engine
tests/         pytest suite — independent re-implementations, no shared code paths
experiments/   reproducible command-line searches (every one takes --help)
results/       labelled statements, phase reports, and the log of abandoned attacks
literatura/    one reading note per paper, with theorems stated verbatim
docs/          research protocol and labelling rules
```

## Getting started

```bash
python -m venv venv
venv/Scripts/activate          # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
pytest -q
```

Reproducing the headline computations:

```bash
python experiments/busca_direta.py --limite 2000000
python experiments/busca_estrutural.py --limite-m 1000000
python experiments/elimina_omega.py
python experiments/cota_certificada.py --log10-bound 30
```

Every computation cited in a result is a versioned, deterministic script with a test.
All arithmetic that supports a mathematical claim uses `int`, `fractions.Fraction` or
`sympy.Rational`; floating point is confined to display.

## Method

See [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) for the notation, the table of known
constraints on `N` with sources, the labelling rules, and the phase roadmap.

Reports and reading notes are currently written in Portuguese; the mathematical content
is being migrated to English.

## References

Papers, with links and the exact version consulted, are listed in
[`literatura/PAPERS.md`](literatura/PAPERS.md). The main ones:

- J. Ward, *Does Ten Have a Friend?*, arXiv:0806.1001, *Int. J. Math. Comput. Sci.* 3(3), 153–158 (2008)
- T. Chatterjee, Sagar Mandal, Sourav Mandal, arXiv:2404.00624 — `ω(N) ≥ 7` and further constraints
- H. R. Thackeray, arXiv:2310.15900, *Indag. Math.* 35(3), 595–607 (2024) — `ω(N) ≥ 10`, the current record
- OEIS [A014567](https://oeis.org/A014567) (solitary by gcd), [A074902](https://oeis.org/A074902) (known friendly numbers)

The statement is formalised in Google DeepMind's `formal-conjectures` repository as
`FormalConjectures/Wikipedia/SolitaryNumber.lean`; Lean 4 formalisation of the new
lemmas is a stated goal of the final phase.

## License

Code is released under the MIT License ([`LICENSE`](LICENSE)); prose, proofs and reports
under CC BY 4.0 ([`LICENSE-DOCS`](LICENSE-DOCS)).
