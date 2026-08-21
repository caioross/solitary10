# RESULTADOS — enunciados com rótulo (regras de rigor: `docs/METHODOLOGY.md`)

Última atualização: 2026-08-21 (Fase 1, Bloco 2). Detalhes: `FASE_0.md`, `FASE_1.md`.

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

## Fase 1, Bloco 1 — certificados do motor de busca (FASE_1.md)

| # | Enunciado | Rótulo |
|---|---|---|
| F | Todo amigo de 10 tem ω(N) ≥ 6 (reprodução independente de Ward 2008 pelo motor: podas exatas + fecho ciclotômico) | `[PROVADO-CONDICIONAL: Teoremas A–D e Lemas da Fase 0 + Zsygmondy/identidade ciclotômica (clássicos) + correção do motor (passada adversarial FASE_1.md §1.5) + correção do sympy nas chamadas consumidas (re-verificadas sem sympy em tests/test_motor_crosscheck.py)]` |
| G | O menor amigo de 10, se existir, excede **10³²** (varredura exaustiva certificada de todas as assinaturas com ω ∈ {10,11,12} e N ≤ 10³²; ω ≥ 13 impossível para N ≤ 10³² pela regra do produto; 34,5 milhões de igualdades exatas testadas, zero amigos) | `[PROVADO-CONDICIONAL: Teoremas A–D e Lemas da Fase 0 + ω(N) ≥ 10 (arXiv:2310.15900) + correção do motor (§1.5)]` |

Contexto de G: certifica e supera em 100× a alegação NÃO certificada "menor amigo
> 10³⁰" (OEIS A074902, citada em arXiv:2404.00624). Fronteira honesta do motor:
ω = 6 não é certificável só com podas de índice (`RamoNaoLimitado`) — coincide com o
ponto onde a literatura precisou de cadeias de divisibilidade (alvo do Bloco 2).

## Fase 1, Bloco 2 — cadeias de divisibilidade (FASE_1.md, Bloco 2)

| # | Enunciado | Rótulo |
|---|---|---|
| H | **Todo amigo de 10 tem ω(N) ≥ 7** (nenhum amigo tem ω = 6: 19 prefixos, 2 745 conjuntos completos, todos mortos pelo fecho de ordens; o único prefixo de espaço infinito, {5,7,11,13,23}, fechado por pinagem do 6º primo em P ∈ {31, 3221}) | `[PROVADO-CONDICIONAL: Teoremas A–D e Lemas/Fato 0 da Fase 0 + Zsygmondy e fórmula de valuação de Nielsen/Voight (clássicos; fórmula re-testada exaustivamente) + correção de core/omega6.py e core/cadeias.py (passada adversarial FASE_1.md §2.5) + correção de sympy.n_order/factorint/nextprime nas chamadas consumidas (todas re-verificadas por implementações próprias)]` |

Contexto de H: reprodução **independente e mecânica** (0,1 s) do Teorema 1.2 de
arXiv:2404.00624, cuja prova publicada é uma análise manual de 19 cadeias. A pinagem
automática redescobre sozinha a entrada **f_3221^11 = 5** da Tabela 4 do paper
(construída à mão pelos autores). Não é resultado novo — é validação cruzada da
literatura por via independente, e a infraestrutura para atacar ω = 8 no Bloco 3.

## Verificações numéricas

| Enunciado | Rótulo |
|---|---|
| Nenhum n ≠ 10 com I(n) = 9/5 em [1, 2·10⁶] | `[VERIFICADO-NUMERICAMENTE: crivo exato, experiments/busca_direta.py]` |
| Nenhum amigo de 10 até 10¹² | `[PROVADO (A–C) + VERIFICADO-NUMERICAMENTE: N = m², m ímpar, 5\|m, m ≤ 10⁶ — experiments/busca_estrutural.py; incondicional após a Fase 0]` |
| Única solução de 5σ(n) = 9n em [1, 10⁷] é n = 10 | `[VERIFICADO-NUMERICAMENTE: revisor adversarial, crivo exato independente]` |

## Correções à literatura (catálogo completo: `results/ERRATA.md`)

Re-verificadas em 2026-08-21 numa segunda passada independente, sobre o texto verbatim
do arXiv, com certificado em `experiments/verifica_erratas.py` e `tests/test_erratas.py`
(28 testes). Material de publicação: `publicacao/`.

| Achado | Rótulo |
|---|---|
| arXiv:2404.00624 v5 Lema 2.3 = arXiv:2409.04451 v4 Lema 23: falso como enunciado (igualdade na partição toda de 1's); enunciados do Lema 3.6/24 e do Teo. 1.10 intactos, provas precisam da forma corrigida | `[PROVADO: contraexemplo exato + correção provada]` |
| arXiv:2404.00624 v5, Remark 3.7 eq. (7): a derivação exibida dá Ω(m) ≥ ω(N) + 2a − 2, não +2a−1; eq. (8) vira Ω(m) ≥ ω(m) + 2a − 1 | `[PROVADO: álgebra re-derivada + 152 testemunhas inteiras]` |
| O limite do Teo. 1.10 (2ω+6a−4) é o **ótimo exato** da relaxação usada na sua prova — a unidade que falta na eq. (7) não é recuperável por esse argumento | `[PROVADO: minimização exaustiva, 48 pares (a, ω)]` |
| arXiv:2404.00624 v5, Cor. 1.11: como provado sustenta só N < 5·6^((2^{K−2a+2}−1)²); forma original é repetida em arXiv:2504.08295 §1 | `[PROVADO: consequência direta do item acima]` |
| arXiv:2412.02701 v4, Teo. 1.2: efetivo apenas para 2 ≤ r ≤ 5 (X₆ = 82944/85085 < 1, F₆ = 17017/9216 > 9/5); título/abstract prometem todos os primos | `[PROVADO: aritmética exata, ambas as leituras da condição]` |
| arXiv:2404.00624 v5, Caso-12 do Teo. 1.2: fator impresso 381/361 = I(19²) no lugar de I(23²) = 553/529; conclusão do caso mantida | `[PROVADO: recomputação exata]` |

## Candidatos anotados (SEM prova própria ainda — não usar como hipótese)

- q₅ < p_{28ω} (esboço na nota de 2404.05771) e r = 5 admissível em 2412.02701 v4 — `[HEURÍSTICA/PENDENTE]`
- Recíproca do mod 18 de Ward (p ≡ 1 mod 3, 2e ≡ 8 mod 18 ⟹ 9 | σ(p^{2e})) — `[VERIFICADO-NUMERICAMENTE: p ≤ 73, e ≤ 199; prova curta esboçada na nota de Ward]`
- Lemas uniformes candidatos p/ família 2p: Cor. 6 de Thackeray (quadrados ímpares); N > d(N)²/r² generalizando Teo. 1.5 de 2504.08295 — `[CONJECTURA/PENDENTE]`
