# Is 10 a solitary number?

A computational and structural attack on a small open problem in elementary number
theory, run under a strict labelling discipline: every statement in this repository
carries an explicit epistemic tag, nothing is called *proved* until it has a written
proof, an independent numerical check and an adversarial review that failed to break it,
and every search engine here is built so that it would rather refuse to certify than
certify something false.

**Where things stand (November 2026).** Every published lower bound on $\omega(N)$
for a friend of 10, up to and including $\omega(N) \ge 10$ — the best bound in the
literature — is now re-derived mechanically by exact arithmetic in under ten minutes
on one core. The least friend of 10, if it exists, exceeds
$10^{32}$ — a certified bound, two orders of magnitude beyond the uncertified one in
the literature. Along the way, seven defects in five recent papers were found and
proved; six of them are written up as a corrigenda note.

---

## The problem

For a positive integer $n$ let $\sigma(n)$ be the sum of its divisors and

$$I(n) = \frac{\sigma(n)}{n}$$

its **abundancy index**. Two integers $m \ne n$ are **friends** when $I(m) = I(n)$;
an integer with no friend is **solitary**. Primes are solitary, and so is every $n$ with
$\gcd(n, \sigma(n)) = 1$ (Greening's criterion) — but $\gcd(10, 18) = 2$, and whether
10 has a friend is open. Since $I(10) = 9/5$,

$$N \text{ is a friend of } 10 \iff N \ne 10 \ \text{ and } \ 5\,\sigma(N) = 9\,N .$$

The wider folklore conjecture is that $2p$ is solitary for every prime $p \ge 5$;
$10 = 2 \cdot 5$ is its smallest case. The published literature attacks the family one
number at a time (10, 14, 15, 20), and every argument runs through the same three
mechanisms — the multiplicativity of $I$, the exact divisibilities forced by the
equation $5\sigma(N) = 9N$, and the arithmetic of $\sigma(p^a)$ through cyclotomic
polynomials. This project turns those mechanisms into a certifier.

## What has been established

$N$ denotes a hypothetical friend of 10 and $\omega(N)$ its number of distinct prime
factors. Labels are explained in [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md); the
authoritative list, with full hypotheses, is
[`results/RESULTS.md`](results/RESULTS.md).

| | Statement | Label | Relation to the literature |
|---|---|---|---|
| **A–D** | $N$ is odd, a perfect square, $25 \mid N$, and 5 is its least prime factor | `PROVED` | Ward 2008; independent proofs, D by a different route |
| **E, E′** | $N \ge 1.53 \cdot 10^{24}$; with Thm 1.9 of arXiv:2404.00624, $N \ge 7.50 \cdot 10^{25}$ | `PROVED-CONDITIONAL` on $\omega(N) \ge 10$ | arithmetic consolidation of known constraints |
| **F** | $\omega(N) \ge 6$ | `PROVED-CONDITIONAL` (A–D + Zsygmondy) | Ward 2008, re-derived by the index engine in under 0.1 s; the "31 trick" of Ward's proof emerges from the cyclotomic closure by itself |
| **G** | the least friend of 10, if any, exceeds $\mathbf{10^{32}}$ | `PROVED-CONDITIONAL` (A–D + $\omega(N) \ge 10$) | certifies, and improves 100×, the uncertified $> 10^{30}$ of OEIS A074902; 34.5 million exact equality tests, sharded under a machine-checked partition |
| **H** | $\omega(N) \ge 7$ | `PROVED-CONDITIONAL` (A–D + Zsygmondy + LTE), adversarially reviewed | Thm 1.2 of arXiv:2404.00624, whose proof is a hand analysis of 19 divisibility chains; here 0.1 s, and the certifier rediscovers the pin $3221 \mid \Phi_5(11)$ — the entry $f^{11}_{3221} = 5$ of the paper's hand-built Table 4 — unaided |
| **I** | $\omega(N) \ge 9$ | `PROVED-CONDITIONAL`, adversarially reviewed (limits stated) | not new — Thackeray (arXiv:2310.15900) has $\omega(N) \ge 10$; an independent and mechanical reproduction in a few seconds, with a method built for $k \ge 9$ |
| **J** | $\omega(N) \ge 10$ | `PROVED-CONDITIONAL`, adversarially reviewed (limit stated) | not new — this *is* Thackeray's theorem (about 25 CPU-hours there); reproduced by a different method in about 6 minutes: 2 298 715 nodes for $\omega = 9$, zero friends, zero refusals, every primality claim above $2^{64}$ proved |

Results I and J come from the recursive certifier, which has had three adversarial passes
([`results/PHASE_1.md`](results/PHASE_1.md) §7.4, §8.4 and §8.9): no false kill and no false
certificate were found, and the defects found were closed or deferred with reasons (§8.8) — two of them latent
soundness holes that no completed run had triggered. The $\omega = 9$ run was replayed
and every decision in it re-derived independently, family by family (§7.6, §8.6). Since
Block 8 the certifier is generic in the target, so **planted friends** — any $N_0$ with
the structural hypotheses, its own $I(N_0)$ as target — are driven end to end through
the real partition: 76 of them in the test suite and the 9 145 of a deterministic
grid are all found, with no node on a friend's path dropping it, and a mutation harness
checks that deliberate defects are caught (74 of 75 are; the 75th removes a check of the certificate verifier that the proof does not need). Every integer the runs rely on being prime above $2^{64}$ is proved, by Miller–Rabin with
13 bases below $3.3 \cdot 10^{24}$ and by elliptic-curve certificates above (2 699 of them,
checked by an exact verifier). Both results stay marked as not load-bearing, and the
label states the one limit left: the finite exponent bound is tested on planted friends
statement by statement, not end to end, because where the certifier branches on it
every friend keeps a slack of at least 2 (§8.3).

Nothing above is claimed as a new theorem about 10. What is new is the *machinery*: a
single exact-arithmetic certifier that reproduces years of hand case analysis in seconds,
refuses honestly where the theory runs out, and documents exactly where that is.

### Corrigenda to the literature

Exact recomputation against the verbatim arXiv text turned up seven defects (six
catalogue entries), all proved and certified by
[`experiments/verifica_erratas.py`](experiments/verifica_erratas.py) and
31 tests. None of them topples a main theorem; one has already propagated
into a later paper.

| | Paper | Defect | Label |
|---|---|---|---|
| E1 | arXiv:2404.00624 Lemma 2.3 = arXiv:2409.04451 Lemma 23 | false as stated (equality in the all-ones partition); the downstream proofs need the corrected form | `PROVED` |
| E2 | arXiv:2404.00624 Remark 3.7, eq. (7) | the displayed derivation gives $\Omega(m) \ge \omega(N) + 2a - 2$, not $+\,2a-1$ | `PROVED` |
| E2 (cont.) | arXiv:2404.00624 Thm 1.10 | its bound is the exact optimum of the relaxation used — the missing unit in (7) is not recoverable by that argument | `PROVED` |
| E3 | arXiv:2404.00624 Cor. 1.11 (repeated in arXiv:2504.08295) | as proved, it only gives $N < 5 \cdot 6^{(2^{K-2a+2}-1)^2}$ | `PROVED` |
| E4 | arXiv:2412.02701 Thm 1.2 | effective only for the 2nd to 5th smallest prime ($X_6 < 1$); the title and abstract promise all primes | `PROVED` |
| E5 | arXiv:2404.00624 Thm 1.2, Case 12 | the printed factor $381/361 = I(19^2)$ should be $I(23^2) = 553/529$; the case still closes | `PROVED` |
| E6 | arXiv:2310.15900 Cor. 6 | false as printed: the hypothesis must hold for every prime $q > r$, not only for the prime factors of $n$ ($n = 11^2 \cdot 5^{604}$); the theorem $\omega(N) \ge 10$ is not affected | `PROVED` |

Catalogue (whose numbering the table follows): [`results/ERRATA.md`](results/ERRATA.md).
Manuscript, E1–E5 so far:
[`publication/errata_friends_of_10.tex`](publication/errata_friends_of_10.tex), with its
submission notes in [`publication/SUBMISSION_GUIDE.md`](publication/SUBMISSION_GUIDE.md).

## How the certifiers work

Write $N = \prod p_i^{a_i}$ with $p_1 = 5$. The equation $5\sigma(N) = 9N$ becomes the
**master equation**

$$\prod_{i} \sigma(p_i^{a_i}) \;=\; 9 \cdot 5^{a_1 - 1} \prod_{i \ge 2} p_i^{a_i},$$

and everything else follows from reading it one prime at a time.

- **Index pruning.** $I$ is multiplicative, $I(p^a)$ increases with $a$ and is bounded
  by $p/(p-1)$. At every node of the search the exact attainable interval of
  $\prod I(p_i^{a_i})$ is known, and a branch dies the moment $9/5$ leaves it. Ward's
  $\omega \ge 6$ is this pruning applied to the smallest primes.
- **Valuation budgets.** Since $3 \nmid N$, the right-hand side has $v_3 = 2$ exactly,
  so $\sum_{p \equiv 1 \ (3)} v_3(a_p + 1) = 2$; likewise $v_5$ gives
  $\sum_{q \equiv 1 \ (5)} v_5(a_q + 1) = a_1 - 1$. These are finite partitions of small
  integers, and they replace "some exponent is $\equiv 2 \pmod 6$" by an exhaustive
  case split.
- **Cyclotomic closure.** $\sigma(p^a) = \prod_{d \mid a+1,\ d > 1} \Phi_d(p)$, and by
  Zsygmondy each $\Phi_d(p)$ with $d \ge 3$ carries a prime whose multiplicative order
  modulo $p$ is exactly $d$. A candidate exponent survives only if every piece factors
  over the primes already in play. Valuations are computed from multiplicative orders
  and lifting-the-exponent — never by materialising $p^{a+1}$.
- **Pinning and tails.** Once an exponent is committed, the unknown primes it feeds are
  pinned to explicit divisors of $\Phi_d(p)$; when the index alone cannot bound the last
  unknown, a Nielsen-style tail branches on lower bounds for exponents under a strictly
  decreasing termination measure.
- **Honesty by construction.** A closure that would exceed a size budget (a cofactor
  above 90 bits to factor, a cyclotomic polynomial of too high degree) is never treated
  as closed: an unfactored composite cofactor counts as at least two unidentified
  primes, a skipped cyclotomic piece as no information, and a node left with no sound
  way forward raises `NaoCertificavel` instead of being pruned. A run either certifies
  a complete case partition or reports which case it could not close — never a silent
  truncation.

Soundness is tested with **planted targets**: a fabricated solution is injected into the
search space and the certifier is required to find it. Two boundary-case bugs of the
catastrophic kind (`<` where `≤` was meant) were caught this way before they could
certify anything. Since Block 8 the recursive certifier accepts any target
$t = I(N_0)$, and a mutation harness
([`experiments/planted_mutations.py`](experiments/planted_mutations.py)) checks that
deliberate defects in it are caught by the planted tests.

### Where the frontier is

$\omega = 9$ terminates, so the certifier stands where the literature stands:
$\omega(N) \ge 10$. The next case, $\omega = 10$, was attempted in Block 8, after the
partition was made target-generic, and it
**stops**: at a near-tight node with *three* unknown primes, such as
$C = \{5, 7, 11, 13, 31, 97, 52361\}$, the split below leaves about 26 million values of
the smallest unknown to enumerate, each with its own subtree, and the finite exponent
bound needs a bound on all the unknowns, which three of them do not have
([`results/PHASE_1.md`](results/PHASE_1.md) §8.8). The method closes near-tight nodes
with at most two unknowns; $\omega(N) \ge 11$ needs a new idea for three: the
enumeration left is finite but out of practical reach.

The obstruction at $\omega = 9$ was diagnosed rather than guessed. At "almost tight"
nodes such as $C = \{5, 7, 11, 13, 31, 97, 52361\}$ the product of suprema falls short
of $9/5$ by $1.8 \cdot 10^{-8}$, so the index bounds the smallest unknown prime only by
about $10^8$ and the search degenerates into enumeration — the same regime in which
Thackeray's SageMath run spent 25 CPU-hours.

Three blocks were spent on it:

- **Cyclotomic equations for the last unknown.** With one unknown $U$ left, some prime
  $\ell \mid a_U + 1$ has a witness among the known primes, and
  $\Phi_\ell(U) = \ell^{\varepsilon} \prod_{q \in C_\ell} q^{e_q}$ has a finite right-hand
  side; $U$ is recovered by an exact integer root instead of enumerating primes. Verified
  against independent brute force; it cut the $\omega = 8$ tree from 210 456 to 90 032
  nodes (36 s) with the same verdict. It moves the wall to nodes with **two** unknowns:
  a 12-hour run of $\omega = 9$ (196 million nodes) did not finish, and certifies nothing.
- **Thackeray's Corollary 6 and Proposition 9** (a finite bound on the exponent of a
  known prime, with Wieferich levels computed through the subgroup of order $r-1$ of
  $(\mathbb{Z}/r^a)^\times$) re-derived and implemented with tests against brute force.
  An unsafe bound on the unknowns was caught by a test that compares it with the real
  index loop; in its sound form the bound, on its own, never fired for $\omega \le 8$ —
  an honest negative result, recorded in [`results/FAILURES.md`](results/FAILURES.md).
  With the split of the next item it does fire: 17 branchings at $\omega = 8$, 44 403
  at $\omega = 9$.
- **Splitting at $B_{\min}$.** With $R = (9/5)/\prod\sup$ and
  $B = \lfloor 1 + 1/(R-1) \rfloor$, a node is split on the smallest unknown $U_1$:
  if $U_1 \le B - 1$, the factor $1 + 1/h + 1/h^2$ with $h = B - 1$ is a known lower
  bound for its contribution, and the exponent tails then kill the node *without
  enumerating* $U_1$; if $U_1 = B$, that one prime is pinned like any known prime; if
  $U_1 > B$ and two unknowns are left, every unknown has an index bound, which is
  exactly where the finite exponent bound is valid (with three or more unknowns, $U_1$
  is enumerated over the reduced interval above $B$). The node above went from hours
  to 54 nodes and 0.1 s, and $\omega = 9$ closes in about 6 minutes.

## Reproducing

```bash
python -m venv venv
venv/Scripts/activate            # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
pytest -q                        # 618 tests (15 skipped by default), about 5 min
```

| Command | Certifies | Time |
|---|---|---|
| `python experiments/busca_direta.py --limite 2000000` | no $n \ne 10$ with $I(n) = 9/5$ up to $2 \cdot 10^6$ (exact sieve) | seconds |
| `python experiments/busca_estrutural.py --limite-m 1000000` | no friend up to $10^{12}$ (uses A–C) | seconds |
| `python experiments/limite_inferior.py` | the exact lower bounds E and E′ | instant |
| `python experiments/elimina_omega.py --k-max 6` | F: $\omega \ge 6$, and the honest refusal at $\omega = 6$ | under 0.1 s |
| `python experiments/cota_certificada.py --log10-bound 30` | no friend up to $10^{30}$ | ≈ 10 s (≈ 100 s for $10^{31}$) |
| `python experiments/shards_10e32.py` | G: the $10^{32}$ sweep as a verified partition of shards | tens of minutes |
| `python experiments/elimina_omega6.py` | H: $\omega \ge 7$ by divisibility chains | 0.1 s |
| `python experiments/elimina_omega_k.py --k-max 9` | I, J: $\omega \ge 10$ by the recursive certifier | ≈ 6 min (`--k-max 8`: seconds) |
| `python experiments/certify_primes.py --k-max 9` | every primality claim of the runs above $2^{64}$ (certificates in `data/`) | ≈ 15 min |
| `python experiments/planted_sweep.py` | 9 145 planted friends found end to end, none dropped on its path | ≈ 2 min |
| `python experiments/planted_mutations.py --no-frozen` | 75 deliberate defects of the certifier and of the certificate verifier, each caught by a planted friend, a node check or a statement test, except one check proved unnecessary | ≈ 11 min |
| `python experiments/verifica_erratas.py` | the corrigenda | seconds |

Every command prints its result together with the full conditional label it is entitled
to. All arithmetic supporting a claim is `int`, `fractions.Fraction` or
`sympy.Rational`; floating point appears only in display (and in the untrusted
certificate generator, whose output an exact verifier checks). Where a result depends
on a library routine (`sympy.factorint`, `isprime` below $2^{64}$, …) the label says so,
and the routine is cross-checked against an independent implementation in the tests.

## Layout

```
core/          exact-arithmetic primitives and the three certifiers
                 abundancy.py   σ, I, friend test           motor.py    index-pruned tree search
                 cadeias.py     valuations by orders        omega6.py   ω = 6 by chains and pinning
                 omega_k.py     recursive certifier for any ω and any target
                 primality.py   primality proofs: 13-base Miller–Rabin, elliptic-curve certificates
data/          primality certificates for the claims of the ω ≤ 9 runs
tests/         618 tests: independent re-implementations, planted friends, frozen counts
experiments/   reproducible command-line scripts (each takes --help)
results/       RESULTS.md (labelled statements) · PHASE_0.md, PHASE_1.md (phase reports)
               ERRATA.md (corrigenda catalogue) · FAILURES.md (abandoned attacks, with reasons)
literature/    one full-text reading note per paper, theorems stated verbatim
publication/   the corrigenda manuscript and its submission notes
docs/          research protocol and labelling rules
```

The code base still carries its original Portuguese identifiers and prints labels in
their original form (`[PROVADO-CONDICIONAL: …]` = `PROVED-CONDITIONAL`), except
`experiments/elimina_omega_k.py`, whose label and closing note are already printed in
English; renaming them is a separate, test-guarded refactor.

## Method

The protocol is short and non-negotiable — see
[`docs/METHODOLOGY.md`](docs/METHODOLOGY.md). In one paragraph: exact arithmetic
always; a label on every statement; three steps (proof, independent verification,
adversarial review) before anything is called proved; a documented search before
anything is called new; every cited computation is a versioned script with a test;
abandoned attacks are logged with the precise reason; and a divergence from the
literature is a finding to be reported, never a discrepancy to be smoothed over.

## References

Full list, with links and the exact versions consulted, in
[`literature/PAPERS.md`](literature/PAPERS.md).

- J. Ward, *Does Ten Have a Friend?*, Int. J. Math. Comput. Sci. 3(3), 153–158 (2008). arXiv:0806.1001
- H. R. Thackeray, *Each friend of 10 has at least 10 nonidentical prime factors*, Indag. Math. 35(3), 595–607 (2024). arXiv:2310.15900 — the current record
- T. Chatterjee, Sagar Mandal, Sourav Mandal, *A note on necessary conditions for a friend of 10*. arXiv:2404.00624
- Sourav Mandal, Sagar Mandal, *Upper bounds for the prime divisors of friends of 10*, Resonance 30 (2025). arXiv:2404.05771
- Sagar Mandal, *Prime divisors of 10's friends: a generalization of prior bounds*, An. Univ. Oradea Fasc. Mat. 33(1), 5–12 (2026). arXiv:2412.02701
- Sagar Mandal, *Exploring the relationships between the divisors of friends of 10*, News Bull. Calcutta Math. Soc. 48 (2025). arXiv:2504.08295
- P. P. Nielsen, *Odd perfect numbers, Diophantine equations, and upper bounds*, Math. Comp. 84 (2015) — the valuation formula and the tail argument
- OEIS [A014567](https://oeis.org/A014567), [A074902](https://oeis.org/A074902)

The statement *10 is solitary* is formalised in Google DeepMind's `formal-conjectures`
repository (`FormalConjectures/Wikipedia/SolitaryNumber.lean`). Lean 4 formalisation of
whichever new lemmas prove tractable is the goal of the final phase.

## Citing

```bibtex
@software{solitary10,
  author = {Comitre Rossi, Caio},
  title  = {solitary10: a certified computational attack on the solitude of 10},
  year   = {2026},
  url    = {https://github.com/caioross/solitary10}
}
```

Code is released under the MIT License ([`LICENSE`](LICENSE)); prose, proofs and
reports under CC BY 4.0 ([`LICENSE-DOCS`](LICENSE-DOCS)).
