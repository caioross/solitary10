# Key papers (one reading note per paper in this directory)

Status: ALL read in full text during Phase 0 (2026-08-20), each with a reading note,
numerical verification of the constants and a fidelity check — see `note_*.md`.

1. J. Ward (2008), "Does Ten Have a Friend?", Int. J. Math. Comput. Sci. 3(3), 153–158.
   arXiv:0806.1001 — https://arxiv.org/abs/0806.1001 → `note_ward_2008.md`
2. T. Chatterjee, Sagar Mandal, Sourav Mandal (2024), "A note on necessary conditions
   for a friend of 10" — https://arxiv.org/abs/2404.00624 (v5, Jan 2025; preprint)
   → `note_2404.00624.md` — ⚠ contains documented local defects (Lemma 2.3,
   Remark 3.7/Cor. 1.11); see results/PHASE_0.md §10.
3. H. R. Thackeray (2024), "Each friend of 10 has at least 10 nonidentical prime
   factors" — https://arxiv.org/abs/2310.15900, Indagationes Mathematicae 35(3),
   595–607 (2024). **CURRENT BEST BOUND: ω(N) ≥ 10.** → `note_2310.15900.md`
4. Sourav Mandal, Sagar Mandal (2024), "Upper bounds for the prime divisors of friends
   of 10" — https://arxiv.org/abs/2404.05771, Resonance 30 (2025). → `note_2404.05771.md`
5. Sagar Mandal (2024), "Prime Divisors of 10's Friends: A Generalization of Prior
   Bounds" — https://arxiv.org/abs/2412.02701 (**v4**, Oct 2025; Analele Univ. Oradea
   33(1), 5–12, 2026). → `note_2412.02701.md` — ⚠ the method only yields bounds for the
   r-th smallest prime with 2 ≤ r ≤ 5 (title/abstract promise more); see PHASE_0.md §10.
6. Sagar Mandal (2025), "Exploring the Relationships Between the Divisors of Friends
   of 10" — https://arxiv.org/abs/2504.08295, News Bull. Calcutta Math. Soc. 48(1–3),
   21–32 (2025). → `note_2504.08295.md`

## Adjacent context (same machinery: the 2p family and its neighbours)

- Analogue for 14: Sagar Mandal, "A note on solitary numbers" (v1 "Is 14 a Solitary
  Number?") — https://arxiv.org/abs/2503.11694, NNTDM 31(3) (2025), 617–623.
- Analogue for 20: Chatterjee, S. Mandal, S. Mandal, "On Characterizing Potential
  Friends of 20" — https://arxiv.org/abs/2409.04451, Ann. West Univ. Timisoara 61(1)
  (2025), 205–229. (20 = 2²·5, outside the 2p family.) ⚠ its Lemma 23 is the same false
  lemma as Lemma 2.3 of arXiv:2404.00624; the passage analogous to Remark 3.7, however,
  is CORRECT there — see `results/ERRATA.md`.
- **There is no** (as of 2026-08-20) paper devoted to 15, no improvement on ω ≥ 10, and
  no uniform theorem for the 2p family — novelty check in results/PHASE_0.md §9.1.
- Folklore conjecture: 2p is solitary for every prime p ≥ 5.
- OEIS: A014567 (solitary by gcd), A074902 (known friendly numbers; source of the
  UNCERTIFIED claim "least friend of 10 > 10^30").
- formal-conjectures (Google DeepMind): the statement IS formalised —
  `FormalConjectures/Wikipedia/SolitaryNumber.lean` (`is_ten_solitary`, research open);
  details and Lean transcription in results/PHASE_0.md §9.2.
- Peripheral (Phase 4): "Formalization of Amicable Numbers Theory" (Lean 4) —
  https://arxiv.org/abs/2601.07444 (amicable ≠ friendly; prior art on σ in Lean).
