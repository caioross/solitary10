# RESULTADOS — enunciados com rótulo (regras de rigor do CLAUDE.md)

Última atualização: 2026-08-20 (Fase 0). Detalhes, provas e verificações: `FASE_0.md`.

## Notação

N denota um hipotético amigo de 10: N ≠ 10 e 5·σ(N) = 9·N (equivalente a I(N) = 9/5).

## Teoremas re-derivados nesta fase (prova própria + verificação numérica + passada adversarial)

| # | Enunciado | Rótulo |
|---|---|---|
| A | N é ímpar | `[PROVADO]` (FASE_0.md §4; adversarial §6) |
| B | N é quadrado perfeito | `[PROVADO]` |
| C | 25 \| N | `[PROVADO]` |
| D | o menor primo divisor de N é 5 (2 ∤ N, 3 ∤ N, 5 \| N) | `[PROVADO]` |
| E | N ≥ (5·7·11·13·17·19·23·29·31·37)² = 1 529 648 735 150 649 937 048 225 ≈ 1,53·10²⁴ | `[PROVADO-CONDICIONAL: A–D + ω(N) ≥ 10 (arXiv:2310.15900)]` |
| E′ | N ≥ 49·(5·7·⋯·37)² = 74 952 788 022 381 846 915 363 025 ≈ 7,50·10²⁵ | `[PROVADO-CONDICIONAL: A–D + ω(N) ≥ 10 + Teo. 1.9 de arXiv:2404.00624]` |

Observação: A–D reproduzem resultados de Ward 2008 (não são novos); a prova de D aqui
é variante independente (usa só o primo forçado 13, não o par {13, 31} de Ward).
E/E′ são consolidações aritméticas diretas das restrições da literatura — sem alegação
de novidade (nenhuma busca por enunciado idêntico feita; valor é interno ao projeto).

## Verificações numéricas

| Enunciado | Rótulo |
|---|---|
| Nenhum n ≠ 10 com I(n) = 9/5 em [1, 2·10⁶] | `[VERIFICADO-NUMERICAMENTE: crivo exato, experiments/busca_direta.py]` |
| Nenhum amigo de 10 até 10¹² | `[PROVADO (A–C) + VERIFICADO-NUMERICAMENTE: N = m², m ímpar, 5\|m, m ≤ 10⁶ — experiments/busca_estrutural.py; incondicional após a Fase 0]` |
| Única solução de 5σ(n) = 9n em [1, 10⁷] é n = 10 | `[VERIFICADO-NUMERICAMENTE: revisor adversarial, crivo exato independente]` |

## Correções à literatura (divergências documentadas — FASE_0.md §10)

| Achado | Rótulo |
|---|---|
| arXiv:2404.00624 v5, Lema 2.3: falso como enunciado (caso de igualdade na partição toda de 1's); Lema 3.6/Teo. 1.10 intactos | `[VERIFICADO: contraexemplo exato + correção provada]` |
| arXiv:2404.00624 v5, Remark 3.7 eq. (7): derivação exibida dá Ω(m) ≥ ω(N) + 2a − 2, não +2a−1; Cor. 1.11 como provado sustenta só N < 5·6^((2^{K−2a+2}−1)²) | `[VERIFICADO: álgebra re-derivada + texto v5 conferido]` |
| arXiv:2412.02701 v4, Teo. 1.2: efetivo apenas para 2 ≤ r ≤ 5 (X₆ = 82944/85085 < 1); título/abstract prometem todos os primos | `[VERIFICADO: aritmética exata]` |

## Candidatos anotados (SEM prova própria ainda — não usar como hipótese)

- q₅ < p_{28ω} (esboço na nota de 2404.05771) e r = 5 admissível em 2412.02701 v4 — `[HEURÍSTICA/PENDENTE]`
- Recíproca do mod 18 de Ward (p ≡ 1 mod 3, 2e ≡ 8 mod 18 ⟹ 9 | σ(p^{2e})) — `[VERIFICADO-NUMERICAMENTE: p ≤ 73, e ≤ 199; prova curta esboçada na nota de Ward]`
- Lemas uniformes candidatos p/ família 2p: Cor. 6 de Thackeray (quadrados ímpares); N > d(N)²/r² generalizando Teo. 1.5 de 2504.08295 — `[CONJECTURA/PENDENTE]`
