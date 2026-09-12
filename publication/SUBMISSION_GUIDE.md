# Submission guide for the corrigenda note

Material: `errata_friends_of_10.tex` (the note, ready to compile) +
`results/ERRATA.md` (internal catalogue) + `experiments/verifica_erratas.py` and
`tests/test_erratas.py` (reproducible certificates).

Read section 0 before sending anything.

---

## 0. Honest framing — what this is and what it is not

**It is:** a legitimate, verifiable corrigenda note on a handful of points in three
papers (two of them published in journals). Correcting the record has real value: defect
E3 (Corollary 1.11) has already propagated into a later paper by the same author.

**It is not:** a new result on the problem of 10. No main theorem of the literature
falls. The note is worth publishing as a service to the community and as a calling card
of rigour — not as mathematical progress. Treating it as progress would be an
overstatement and would damage credibility exactly where it matters.

**The etiquette rule that dominates everything else:** authors first, publication
second. A corrigendum posted without prior notice is technically correct and socially
poor; with prior notice, the most likely outcome is that the authors fix the preprint
and/or ask to cite it — which is better for everyone.

---

## 1. Recommended sequence

| Step | Action | Suggested timing |
|---|---|---|
| 1 | Re-run the verification and re-check the current arXiv versions (§2) | day D |
| 2 | E-mail the authors of P1/P2 and the author of P3 (§4.1, §4.2) | D+0 |
| 3 | Wait for a reply | 21–30 days |
| 4a | If they correct the preprints: decide whether publishing is still worthwhile (§5) | D+30 |
| 4b | If no reply or disagreement: post the note on arXiv (§3) | D+30 |
| 5 | Notify the editors of the two journals that published P2 and P3 (§4.3) | after 4b |

Do not skip step 2. And, when writing, make it clear that you are **not** asking for a
retraction of anything: defects E1 and E5 are harmless, E2/E3 weaken one corollary and
E4 is a matter of scope/wording.

---

## 2. Checklist before any submission

- [ ] `pytest -q` green in the repo and `python experiments/verifica_erratas.py`
      without failures.
- [ ] Re-check **today** whether there is a new arXiv version of 2404.00624, 2409.04451
      and 2412.02701 (the defects may already have been fixed). If so, re-read the cited
      passages before sending anything.
- [ ] Search again for an already published erratum/corrigendum (arXiv full text, Google
      Scholar, zbMATH). Record the search in `results/ERRATA.md`.
- [ ] Check that every citation in the note carries the **exact version** (v5, v4) and
      the lemma/theorem numbering of the cited text.
- [ ] In the `.tex`: confirm the repository link, decide on the affiliation
      ("Independent researcher" is fine) and, if desired, add acknowledgements.
- [ ] Tone: re-read looking for any sentence that sounds like an accusation. Replace
      "the authors err" with "the argument as displayed gives …". The current note is
      already in that tone; keep it.

Compilation: no LaTeX is installed on this machine. Use [Overleaf](https://overleaf.com)
(new project → upload the `.tex` → compile with pdfLaTeX) or install MiKTeX.

---

## 3. arXiv: how to submit (and the real obstacle)

1. An account at arxiv.org with a personal e-mail.
2. **Endorsement.** New submissions in `math.NT` require an endorsement from someone
   already established in that category. With no prior submissions, an endorser is
   needed. Routes, in order of effectiveness:
   - ask one of the authors of the papers themselves (common and graceful: if they
     agree with the corrigenda, endorsing is the natural gesture);
   - ask a number theorist at a Brazilian university (USP/IMPA/UNICAMP/UFMG) who
     already publishes in `math.NT`, attaching the PDF;
   - arXiv generates an *endorsement code* in the account; endorsement is per category.
3. Category: primary `math.NT`; the note is about `11A25`. (P3 was posted in `math.GM`,
   which also requires endorsement.)
4. Fields: `Comments:` something like *"6 pages. Corrigenda to arXiv:2404.00624v5,
   arXiv:2409.04451v4 and arXiv:2412.02701v4"*; MSC `11A25`; licence CC BY 4.0.
5. Title/abstract are already in the `.tex`.

**If the endorsement does not come through**, real alternatives:
- **Zenodo** (immediate DOI, no gatekeeping) + sending the link to the authors and
  editors. Not indexed like arXiv, but citable and dated.
- **A small, fast journal** suitable for short corrigenda notes: *Notes on Number Theory
  and Discrete Mathematics* (NNTDM — where the author of P3 himself has published),
  *INTEGERS*, *Journal of Integer Sequences*. There the note is refereed, which is a
  better seal than arXiv alone.
- **A letter to the editor** of one of the two journals that published P2/P3 (§4.3): the
  formally correct channel for correcting the record of a published article.

Recommendation: arXiv (or Zenodo) first, to date it; letters to the editors afterwards.

---

## 4. Draft messages

Adjust before sending. Addresses: look them up on the arXiv page of each paper (the
author's e-mail appears in the PDF of 2412.02701 itself; confirm the others on the
current institutional pages — IIT Ropar, IIT Kanpur, RKMVERI).

### 4.1 To the authors of P1 (arXiv:2404.00624) and P2 (arXiv:2409.04451)

> **Subject:** Two small remarks on "A note on necessary conditions for a friend of 10"
> (arXiv:2404.00624v5)
>
> Dear Prof. Chatterjee, Dear Sagar Mandal, Dear Sourav Mandal,
>
> I have been working through your papers on friends of 10 and 20 in detail, and I
> would like to bring two small points to your attention before doing anything else
> with them. Both are local; none of your main theorems is affected.
>
> 1. Lemma 2.3 of arXiv:2404.00624v5 (and, verbatim, Lemma 23 of arXiv:2409.04451v4)
>    states that a·n < Σ a^{c_i} for every partition of n and every integer a > e.
>    Equality holds for the all-ones partition (the proof uses ψ strictly decreasing
>    on [1,∞), but ψ(1) = 0, so a·c < a^c only for c > 1). The correct statement is
>    a·n ≤ Σ a^{c_i}, with equality if and only if every c_i = 1. This does not affect
>    Lemma 3.6 / Lemma 24, whose statements are correct — in fact your own note after
>    the proof (that the minimum lies in A_{2a−1,5}(2a−1)) is precisely the equality
>    case.
>
> 2. In Remark 3.7 of arXiv:2404.00624v5, the displayed inequality
>    2a + 2Ω(m) ≥ 2ω(N) + 6a − 4 gives Ω(m) ≥ ω(N) + 2a − 2, one unit weaker than
>    equation (7); both sides being even, no parity gain is available. Equation (8)
>    then reads Ω(m) ≥ ω(m) + 2a − 1, and Corollary 1.11 becomes
>    N < 5·6^((2^{K−2a+2}−1)²). I also checked that the counting in the proof of
>    Theorem 1.10 is exactly optimal — the configuration with 2a−1 primes ≡ 1 (mod 10)
>    of exponent 4 and all remaining primes of exponent 2 meets every constraint used
>    there and attains 2ω(N) + 6a − 4 — so the missing unit does not seem recoverable
>    from that argument. (The analogous passage in the friends-of-20 paper is correct.)
>
> There is also a misprint in Case 12 of the proof of Theorem 1.2: the last factor is
> printed as 381/361 = I(19²) where the chain has 23; with I(23²) = 553/529 both
> inequalities still hold, so the case is unaffected.
>
> I have exact-arithmetic scripts verifying all of the above and would be glad to
> share them. If you find these remarks correct, the simplest outcome would be a
> revised version of the preprint; I have drafted a short corrigendum note but would
> much rather not post it if you are updating the papers. I am happy to be wrong on
> any of these points — please tell me if I have misread something.
>
> With thanks for your work on this problem, which is what made a careful reading
> worthwhile,
>
> Caio Comitre Rossi
> (independent researcher, Brazil)

### 4.2 To the author of P3 (arXiv:2412.02701 / Analele Oradea 33(1) 2026)

> **Subject:** Range of validity of Theorem 1.2 in "Prime Divisors of 10's Friends"
>
> Dear Sagar Mandal,
>
> I have a question about Theorem 1.2 of arXiv:2412.02701v4 (Analele Univ. Oradea
> 33(1), 5–12, 2026). Writing X_r = (36/25)·∏_{4≤i≤r+1}(1 − 1/p_i), the hypothesis is
> A/B > 1/(X_r − 1) — this is the reading confirmed by your own instantiations, since
> 25/11, 175/41 and 385/47 are exactly 1/(X_r − 1) for r = 2, 3, 4. The final step of
> the proof requires 1 + B/A < X_r, which for positive A, B is possible only when
> X_r > 1. Now X_r is strictly decreasing and X_6 = 82944/85085 < 1, so for r ≥ 6 the
> threshold is negative: on the intended reading there is no admissible pair (A, B),
> and on a literal reading the proof does not close, since the fixed factor
> F_r = (5/4)·∏_{4≤j≤r+1} p_j/(p_j−1) already satisfies F_r ≥ 9/5 for r ≥ 6
> (F_6 = 17017/9216).
>
> So, unless I am misreading, the theorem gives bounds for q_r only for 2 ≤ r ≤ 5,
> rather than for each prime divisor as the title and abstract state. Nothing else in
> the paper seems affected: Theorem 1.1 and Corollary 1.1 use only r ≤ 4.
>
> Incidentally, r = 5 is admissible — the threshold is 5005/179, so (A, B) = (113, 4)
> works and the sharper form q_r < p_L inside your proof gives q_5 < p_{⌈113ω(n)/4⌉},
> i.e. q_5 < p_283 = 1847 when ω(n) = 10. That corollary seems worth stating
> explicitly; it is new relative to [4].
>
> (Two typographical points: "From (3) and (4)" in the proof should read "From (1) and
> (4)", and the inequality A > B > 1 used in Remark 1.1 follows from the hypotheses
> only when 1/(X_r − 1) > 1, i.e. in the same range 2 ≤ r ≤ 5.)
>
> All of this is checked with exact rational arithmetic and I am glad to share the
> code. If you agree, I would be happy to see it fixed in a new arXiv version and in a
> corrigendum to the journal; I have a short note drafted but would prefer to hold it.
>
> Best regards,
> Caio Comitre Rossi

### 4.3 To the editors (only after step 3, and mentioning that the authors were notified)

> **Subject:** Corrigendum concerning [author, title, vol., pages]
>
> Dear Editors,
>
> I am writing about [full reference]. In Theorem 1.2 of that paper the hypothesis
> A/B > 1/(X_r − 1), with X_r = (36/25)·∏_{4≤i≤r+1}(1 − 1/p_i), can be met only when
> X_r > 1, which holds exactly for 2 ≤ r ≤ 5 (X_6 = 82944/85085 < 1). The theorem
> therefore bounds the r-th smallest prime divisor only in that range, and not every
> prime divisor as stated in the title and abstract. The remaining results of the
> paper are unaffected.
>
> I contacted the author on [date] with the details. I attach a short note with the
> full argument and the exact computations, and I am at your disposal if a formal
> corrigendum would be useful.
>
> Yours sincerely,
> Caio Comitre Rossi

---

## 5. If the authors correct first

The likely and **good** scenario. In that case:

- **Do not publish the whole note.** Reduce it to whatever remains uncorrected (for
  instance, if P3 comes out corrected but P1 stays as is, the note becomes a note about
  P1 only) or shelve it.
- Ask — without insisting — that the correction mention the source ("we thank
  C. C. Rossi for pointing out…"). That is the usual currency and is worth more than
  the note.
- Record the outcome in `results/ERRATA.md` in any case: the verification work remains
  the foundation of what the project uses as hypotheses.

## 6. Risks

- **Your own error.** Every item was checked twice (Phase 0 and this pass) against the
  verbatim text and by exact arithmetic, but the only item whose reading involves
  interpretation is E4 (which reading of the condition on A/B is intended). The note
  already presents **both** readings and shows that neither yields the result for
  r ≥ 6 — keep that structure, it is what makes it irrefutable.
- **Escalating the tone.** Do not use "wrong", "flawed", "error" in the title or the
  abstract. "Corrigenda and remarks" is enough.
- **Claiming too much.** The note must not suggest that the problem of 10 has advanced.
- **Priority.** If someone publishes the same observation in the meantime, fine — the
  value of the work for the project (knowing exactly which hypotheses from the
  literature are usable) does not depend on credit.
