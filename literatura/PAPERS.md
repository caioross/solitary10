# Papers-chave (uma nota de leitura por paper neste diretório)

Estado: TODOS lidos em texto completo na Fase 0 (2026-08-20), com nota de leitura,
verificação numérica das constantes e checagem de fidelidade — ver `nota_*.md`.

1. J. Ward (2008), "Does Ten Have a Friend?", Int. J. Math. Comput. Sci. 3(3), 153–158.
   arXiv:0806.1001 — https://arxiv.org/abs/0806.1001 → `nota_ward_2008.md`
2. T. Chatterjee, Sagar Mandal, Sourav Mandal (2024), "A note on necessary conditions
   for a friend of 10" — https://arxiv.org/abs/2404.00624 (v5, jan/2025; preprint)
   → `nota_2404.00624.md` — ⚠ contém defeitos pontuais documentados (Lema 2.3,
   Remark 3.7/Cor. 1.11); ver results/FASE_0.md §10.
3. H. R. Thackeray (2024), "Each friend of 10 has at least 10 nonidentical prime
   factors" — https://arxiv.org/abs/2310.15900, Indagationes Mathematicae 35(3),
   595–607 (2024). **MELHOR LIMITE ATUAL: ω(N) ≥ 10.** → `nota_2310.15900.md`
4. Sourav Mandal, Sagar Mandal (2024), "Upper bounds for the prime divisors of friends
   of 10" — https://arxiv.org/abs/2404.05771, Resonance 30 (2025). → `nota_2404.05771.md`
5. Sagar Mandal (2024), "Prime Divisors of 10's Friends: A Generalization of Prior
   Bounds" — https://arxiv.org/abs/2412.02701 (**v4**, out/2025; Analele Univ. Oradea
   33(1), 5–12, 2026). → `nota_2412.02701.md` — ⚠ o método só entrega limites para o
   r-ésimo menor primo com 2 ≤ r ≤ 5 (título/abstract prometem mais); ver FASE_0.md §10.
6. Sagar Mandal (2025), "Exploring the Relationships Between the Divisors of Friends
   of 10" — https://arxiv.org/abs/2504.08295, News Bull. Calcutta Math. Soc. 48(1–3),
   21–32 (2025). → `nota_2504.08295.md`

## Contexto adjacente (mesma maquinaria, família 2p e vizinhos)

- Análogo para 14: Sagar Mandal, "A note on solitary numbers" (v1 "Is 14 a Solitary
  Number?") — https://arxiv.org/abs/2503.11694, NNTDM 31(3) (2025), 617–623.
- Análogo para 20: Chatterjee, S. Mandal, S. Mandal, "On Characterizing Potential
  Friends of 20" — https://arxiv.org/abs/2409.04451, Ann. West Univ. Timisoara 61(1)
  (2025), 205–229. (20 = 2²·5, fora da família 2p.)
- **Não existe** (até 2026-08-20) paper dedicado ao 15, melhoria de ω ≥ 10, nem
  teorema uniforme para a família 2p — checagem de novidade em results/FASE_0.md §9.1.
- Conjectura folclórica: 2p solitário para todo primo p ≥ 5.
- OEIS: A014567 (solitários por gcd), A074902 (amigáveis conhecidos; fonte da alegação
  NÃO certificada "menor amigo de 10 > 10^30").
- formal-conjectures (Google DeepMind): o enunciado ESTÁ formalizado —
  `FormalConjectures/Wikipedia/SolitaryNumber.lean` (`is_ten_solitary`, research open);
  detalhes e transcrição Lean em results/FASE_0.md §9.2.
- Periférico (Fase 4): "Formalization of Amicable Numbers Theory" (Lean 4) —
  https://arxiv.org/abs/2601.07444 (amicable ≠ friendly; arte prévia de σ em Lean).
