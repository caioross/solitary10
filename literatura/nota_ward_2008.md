# Nota de leitura — Ward (2008), "Does Ten Have a Friend?"

## 1. Cabeçalho

- **Título:** Does Ten Have a Friend?
- **Autor:** Jeffrey Ward (wardjm@clarkson.edu). Trabalho feito no REU da Auburn University em 2007, apoio NSF grant 0353723.
- **Ano:** 2008.
- **arXiv:** [arXiv:0806.1001](https://arxiv.org/abs/0806.1001) (v1: 05/jun/2008; v2: 06/jun/2008; lido: v2). Classificação: math.NT; MSC 11A25.
- **Publicação:** International Journal of Mathematics and Computer Science, vol. 3, n. 3, pp. 153–158 (2008). Sem DOI conhecido. (A página do arXiv não traz journal-ref; a referência ao IJMCS é confirmada pelas bibliografias de arXiv:2404.05771 e arXiv:2412.02701.)
- **Fonte lida:** texto completo — PDF baixado de https://arxiv.org/pdf/0806.1001 (5 páginas), com conferência pontual da versão HTML em https://ar5iv.labs.arxiv.org/html/0806.1001.
- **Extensão:** 5 páginas; 1 teorema numerado (Teorema 1), uma lista numerada de propriedades elementares (Seção 1.1), sem lemas ou corolários numerados.

## 2. Enunciados exatos

### 2.1 Definições usadas no paper

- σ(n) = soma dos divisores positivos de n; I(n) = σ(n)/n ("abundancy ratio" ou "abundancy index"); n é perfeito sse I(n) = 2.
- m e n (inteiros positivos) são **amigos** ("friends") sse m ≠ n e I(m) = I(n). Um inteiro é **amigável** ("friendly") se tem pelo menos um amigo. (O paper NÃO usa a palavra "solitary".)
- Distinção explícita de números **amicáveis** ("amicable": m ≠ n e σ(m) − m = σ(n) − n) — conceito diferente, mencionado só para evitar confusão.
- Pergunta de fundo (Anderson–Hickerson [1] do paper): a densidade natural dos inteiros amigáveis é 1? (Aberta.)

### 2.2 Propriedades elementares (Seção 1.1 do paper, lista numerada; provas remetidas a Laatsch [5] e Weiner [6])

Sejam m, n inteiros positivos; todos os primos são positivos.

1. I(n) ≥ 1, com igualdade somente se n = 1.
2. Se m | n, então I(m) ≤ I(n), com igualdade somente se m = n.
   (Consequência usada na Seção 2: se m | n e m ≠ n, então m e n não são amigos; em particular um amigo de 10 não é múltiplo de 10.)
3. Se p_1, …, p_k são primos distintos e e_1, …, e_k inteiros positivos, então
   I(∏_{j=1}^k p_j^{e_j}) = ∏_{j=1}^k (∑_{i=0}^{e_j} p_j^{−i}) = ∏_{j=1}^k (p_j^{e_j+1} − 1) / (p_j^{e_j} (p_j − 1)),
   fórmula análoga à de σ: σ(∏ p_j^{e_j}) = ∏ (∑_{i=0}^{e_j} p_j^{i}) = ∏ (p_j^{e_j+1} − 1)/(p_j − 1).
4. I é fracamente multiplicativa: se mdc(m, n) = 1, então I(mn) = I(m)·I(n).
5. (Troca de primos por menores.) Se p_1, …, p_k são primos distintos, q_1, …, q_k são primos distintos, e_1, …, e_k são inteiros positivos e p_j ≤ q_j para j = 1, …, k, então
   I(∏_{j=1}^k p_j^{e_j}) ≥ I(∏_{j=1}^k q_j^{e_j}),
   com igualdade somente se p_j = q_j para todo j.
6. Se os fatores primos distintos de n são p_1, …, p_k, então I(n) < ∏_{j=1}^k p_j/(p_j − 1) (desigualdade estrita).
   A justificativa dada: pela propriedade 3 e pela observação de que, para p > 1, I(p^e) = (p^{e+1} − 1)/(p^{e+1} − p^e) = (p − p^{−e})/(p − 1) **cresce estritamente em e** com limite p/(p−1) quando e → ∞.

**ERRATA DO PAPER (numeração):** a lista impressa termina no item 6 (conferido no PDF e no ar5iv), mas o texto do próprio item 6 e a prova do Teorema 1 referem-se a uma "propriedade 7" ("Although related to 5, 7 is most easily seen…"; "applying 6 and 7 of Section 1"; "will use 5, 6, and 7 from Section 1"). Aparentemente uma versão anterior tinha 7 itens (o item extra sendo a monotonia estrita de I(p^e) em e com limite p/(p−1), hoje embutida na explicação do item 6) e as referências cruzadas não foram atualizadas. O conteúdo matemático usado é inequívoco: monotonia por divisibilidade (item 2), troca de primos (item 5), cota ∏ p/(p−1) (item 6) e crescimento de I(p^e) em e. Ao citar, usar os enunciados, não os números.

### 2.3 Observações da Seção 2 (sem número no paper)

- Se m e n são amigos e k é um inteiro positivo com mdc(k, m) = mdc(k, n) = 1, então mk e nk são amigos (pela propriedade 4). O paper afirma (sem prova detalhada) que o conjunto dos múltiplos amigáveis de qualquer inteiro amigável tem densidade (inferior) positiva.
- Nenhuma potência de primo tem amigo (afirmado como "fácil de ver", sem prova no paper). Logo, dentre 1, 2, …, 9, apenas 6 (perfeito) tem amigo. A pergunta do título (10 tem amigo?) foi feita em [1] (Anderson–Hickerson 1977) e em [3] (Ford–Konyagin) e segue aberta.

### 2.4 Teorema 1 (único teorema numerado; enunciado fiel)

**Teorema 1.** Se n é amigo de 10, então:
(a) n é um quadrado perfeito com **pelo menos 6 fatores primos distintos** (ω(n) ≥ 6), o menor deles sendo 5;
(b) pelo menos um fator primo p de n satisfaz **p ≡ 1 (mod 3)** e aparece na fatoração de n com **expoente ≡ 2 (mod 6)** (isto é, p^{2e} ‖ n com 2e ≡ 2 (mod 6), equivalentemente e ≡ 1 (mod 3));
(c) se existe **um único tal primo** dividindo n, então ele aparece com **expoente ≡ 8 (mod 18)**.

Cuidados de leitura:
- Em (b) e (c), o expoente citado é o expoente **na fatoração de n** (o número 2e), não a metade e. "Expoente ≡ 2 (mod 6)" = 2e ∈ {2, 8, 14, 20, …}; "expoente ≡ 8 (mod 18)" = 2e ∈ {8, 26, 44, …}. Note que 8 ≡ 2 (mod 6), consistente.
- Em (c), "um único tal primo" refere-se, pela redação do teorema e da prova, a um único primo com **ambas** as propriedades de (b) (≡ 1 mod 3 **e** expoente ≡ 2 mod 6). A prova de fato funciona sob essa hipótese mais fraca (logo enunciado mais forte): se p_i é o único primo de n cujo fator σ(p_i^{2e_i}) é divisível por 3 — o que equivale a p_i ≡ 1 (mod 3) com e_i ≡ 1 (mod 3) —, então 9 | σ(p_i^{2e_i}) e segue 2e_i ≡ 8 (mod 18). O caso particular "único primo ≡ 1 (mod 3) dividindo n" está coberto.
- O enunciado NÃO diz explicitamente "n é ímpar" nem "25 | n", mas ambos seguem imediatamente: menor primo = 5 ⟹ 2, 3 ∤ n; 5 | n e n quadrado ⟹ 5² | n. Ambos os fatos são estabelecidos dentro da prova (n é ímpar logo no primeiro parágrafo; n = 5^{2a}·∏ p_i^{2e_i} com a ≥ 1).

### 2.5 Observações finais do paper (sem número)

- **Finitude por nível:** o método da prova, para cada valor fixado de k (número de primos além do 5), reduz a busca a **finitas** possibilidades a verificar: com k = 5 há finitas configurações; esgotadas, passa-se a k = 6, etc. (Afirmado sem detalhes; é o germe do método de árvore com poda.)
- **"Amigo teórico de proximidade t"** (definição introduzida no paper): uma sequência (n_k) de inteiros positivos com lim_{k→∞} I(n_k) = I(m) e tal que o conjunto de todos os primos que dividem algum n_k tem cardinalidade t. Exemplo: lim_{k→∞} I(3^k·5) = (3/2)(6/5) = 9/5 = I(10), logo (3^k·5) é amigo teórico de 10 de proximidade 2. Pergunta aberta proposta: todo inteiro positivo tem amigo teórico de proximidade finita?

## 3. Método de prova do Teorema 1

Tudo aritmética elementar com as propriedades 1–6; nenhuma computação além de comparações de racionais explícitos.

1. **5 | n, n ímpar:** I(n) = 9/5 ⟺ 5σ(n) = 9n ⟹ 5 | n; se 2 | n então 10 | n e a propriedade 2 (com n ≠ 10) impede I(n) = I(10). De 5σ(n) = 9n com n ímpar segue σ(n) ímpar; n e σ(n) ímpares ⟹ n é quadrado (fato de Weiner [6], via a fórmula de σ: todos os fatores ∑ p^i ímpares com p ímpar forçam todos os expoentes pares).
2. **3 ∤ n:** se 3 | n, escreve n = 3^{2a}·5^{2b}·m² com mdc(m, 30) = 1. Como I(3⁴·5²) = 3751/2025 > 9/5 e I(3²·5⁴) = 10153/5625 > 9/5, a propriedade 2 força a = b = 1. Então 9n = 3⁴5²m² = 5σ(3²)σ(5²)σ(m²) = 5·13·31·σ(m²) ⟹ 13, 31 | m ⟹ I(n) ≥ I(3²5²13²31²) = 20191/10075 > 9/5. Contradição.
3. **ω(n) ≥ 6:** escreve n = 5^{2a}·∏_{i=1}^k p_i^{2e_i}, primos distintos p_i > 5. Se k ≤ 3: I(n) ≤ I(5^{2a}7^{2e₁}11^{2e₂}13^{2e₃}) < (5/4)(7/6)(11/10)(13/12) = 1001/576 < 9/5 (troca de primos + cota ∏ p/(p−1)). Para k = 4: (i) I(5²7²11²13²19²) > 9/5 e, por troca de primos, I(5²7²11²13²17²) > 9/5 — junto com a propriedade 2 isso elimina p₄ ∈ {17, 19}; (ii) para p₄ = 23: I(5⁴7²11²13²23²) > 9/5 força a = 1, e então σ(5²) = 31 divide σ(n) = (9/5)n, logo 31 | n — impossível pois os primos de n seriam {5,7,11,13,23}; (iii) todos os demais casos k = 4 caem por duas desigualdades justas: (5/4)(7/6)(11/10)(13/12)(29/28) = 4147/2304 < 9/5 e (5/4)(7/6)(11/10)(17/16)(19/18) = 24871/13824 < 9/5. Logo k ≥ 5 e ω(n) = k + 1 ≥ 6.
4. **Congruências (b) e (c):** de 5σ(n) = 9n e 3 ∤ n vem 9 | σ(n). Para p ≡ 2 (mod 3), σ(p^{2e}) = 1 + p + ⋯ + p^{2e} ≡ 1 (mod 3) (isso cobre também o fator σ(5^{2a})); logo algum p_i ≡ 1 (mod 3) precisa ter 3 | σ(p_i^{2e_i}) ≡ 2e_i + 1 (mod 3), forçando e_i ≡ 1 (mod 3), i.e., 2e_i ≡ 2 (mod 6). Se p_i é o único tal primo, então 9 | σ(p_i^{2e_i}); a checagem dos casos p_i ≡ 1, 4, 7 (mod 9) dá 2e_i ≡ 8 (mod 18) em todos.

**Verificação numérica independente (feita nesta leitura, aritmética exata com `fractions.Fraction`):** todas as 9 comparações de racionais citadas acima conferem, e a varredura do argumento mod 9 (representantes p = 19, 13, 7 para p ≡ 1, 4, 7 mod 9; expoentes 2e ≤ 200) confirma que 9 | σ(p^{2e}) ocorre exatamente para 2e ≡ 8 (mod 18). Duas observações que a verificação revelou:
- As duas desigualdades finais do passo k = 4 são **apertadíssimas**: 4147/2304 ≈ 1,799913 e 24871/13824 ≈ 1,799117, contra 9/5 = 1,8. O método está no limite da sua força em k = 4 — estender a k = 5 por pura desigualdade global é inviável; é preciso poda ramo a ramo (consistente com a observação de finitude do próprio Ward e com o método de arXiv:2310.15900).
- I(5²7²11²13²23²) = 485364861/270438025 ≈ 1,7947 < 9/5: o caso p₄ = 23 realmente NÃO sai por desigualdade, o que explica o desvio pelo argumento de divisibilidade σ(5²) = 31 | 9n. Esse padrão (poda aritmética quando a poda analítica falha) é o ingrediente-chave reutilizável.

## 4. Fidelidade à tabela do CLAUDE.md

Resumo da tabela em avaliação: "N é ímpar, quadrado perfeito, menor primo divisor = 5 (logo 2,3 ∤ N e 25 | N)" + "existe primo ≡ 1 (mod 3) dividindo N com expoente ≡ 2 (mod 6); se for único, expoente ≡ 8 (mod 18)" + "ω(N) ≥ 6 é mencionado como resultado de Ward na literatura".

| Item da tabela | Veredicto | Comentário |
|---|---|---|
| N é ímpar | FIEL | Não está literalmente no enunciado do Teorema 1, mas é provado no primeiro parágrafo da prova (2 ∤ n) e é consequência imediata de "menor primo = 5". |
| N é quadrado perfeito | FIEL | Literal no enunciado ("n is a square"). |
| Menor primo divisor = 5 | FIEL | Literal no enunciado ("the smallest being 5"). |
| Logo 2, 3 ∤ N | FIEL | Consequência imediata correta; ambos também provados explicitamente na prova. |
| Logo 25 \| N | FIEL | Não literal no enunciado, mas dedução imediata correta: 5 \| N e N quadrado ⟹ 5² \| N; a prova escreve N = 5^{2a}·(…) com a ≥ 1. |
| Existe primo ≡ 1 (mod 3) dividindo N com expoente ≡ 2 (mod 6) | FIEL | Exato, inclusive no ponto delicado: o expoente citado é o da fatoração de N (2e ≡ 2 mod 6), como no paper ("appear … to a power congruent to 2 modulo 6"). É UM MESMO primo com as duas propriedades (a tabela preserva isso). |
| Se for único, expoente ≡ 8 (mod 18) | FIEL | Exato. Nuance herdada do paper: "único" = único primo com ambas as propriedades (≡ 1 mod 3 E expoente ≡ 2 mod 6); a prova vale sob essa hipótese mais fraca, e cobre em particular a leitura "único primo ≡ 1 (mod 3)". Nenhuma das duas leituras torna a tabela incorreta. |
| ω(N) ≥ 6 como resultado de Ward | FIEL | O Teorema 1 prova literalmente "at least 6 distinct prime factors", i.e., ω(N) ≥ 6. Atribuição correta na literatura. A linha 1 da tabela não lista ω ≥ 6 sob Ward, mas isso é omissão inócua (superado por ω ≥ 7 e ω ≥ 10 nas linhas 3–4). |

**Veredicto global: FIEL.** Nenhuma divergência de conteúdo; os itens "logo 2,3 ∤ N e 25 | N" são deduções imediatas corretas e estão marcados como tais ("logo") na tabela.

## 5. Uso no projeto

**Para re-derivar (Fase 0):** o Teorema 1 inteiro é o alvo natural da re-derivação com prova completa exigida pela Fase 0 (ímpar, quadrado, 25 | N, menor primo 5 — e vale incluir ω ≥ 6 e as congruências (b)/(c), que são baratas). A verificação numérica desta nota (racionais exatos + varredura mod 9) deve virar script versionado em `experiments/` com teste.

**Técnicas reutilizáveis (Fases 1–2):**
1. **As quatro regras de poda da Fase 1 já estão todas aqui:** monotonia por divisibilidade (prop. 2), fórmula produto exata (prop. 3), troca de primos por menores (prop. 5) e cota estrita I(n) < ∏ p/(p−1) com I(p^e) ↑ p/(p−1) (prop. 6). São exatamente os intervalos exatos de ∏ I(p_i^{2e_i}) planejados para a busca em árvore.
2. **Propagação de divisibilidade via σ:** o truque "expoente de 5 fixado ⟹ σ(5^{2a}) | 9N ⟹ novo primo forçado em N" (usado duas vezes: 13·31 no caso 3 | n; 31 no caso p₄ = 23) é a regra "propagar divisibilidades impostas por 5σ(N) = 9N" do roteiro da Fase 1. Crucial porque a poda analítica sozinha falha (caso 23, e as desigualdades k = 4 já estão a <0,001 do limiar).
3. **Observação de finitude por nível:** Ward já nota que, fixado k, restam finitas configurações — antecipa o programa de arXiv:2310.15900 (ω ≥ 10). Replicar/estender rumo a ω ≥ 11 (Fase 1) é literalmente industrializar este método.

**Para a família 2p (Fase 3):** o esqueleto da prova usa pouquíssimo o "10" específico e é candidato a uniformização. Para N amigo de 2p (p primo ≥ 5): I(N) = I(2p) = 3(p+1)/(2p) dá 2p·σ(N) = 3(p+1)·N, donde p | N, N ímpar (senão 2p | N), σ(N) ímpar ⟹ N quadrado — os passos 1–2 generalizam quase verbatim. O passo mod 3/mod 9 usa 9 | σ(n), que veio de 9 = numerador de I(10); para 2p geral o análogo é a valuação 3-ádica de 3(p+1), que depende de p (mod 3) — aqui está o trabalho real de uniformização. Registrar como primeira tentativa concreta da Fase 3.

**Alertas de citação:**
- Citar as propriedades da Seção 1.1 pelo enunciado, nunca pelo número (errata de numeração documentada na Seção 2.2 desta nota).
- O paper NÃO prova ω ≥ 7 nem nada sobre primos ≡ 1 (mod 10) — isso é arXiv:2404.00624 (linha 3 da tabela), não Ward.
- "Nenhuma potência de primo tem amigo" é afirmado sem prova; se o projeto usar, re-derivar (é curto: I(p^e) < p/(p−1) ≤ 2 e injetividade de I em potências de primo — fazer direito na Fase 0 se necessário).

---
*Nota produzida em 2026-08-20 a partir do texto completo do arXiv:0806.1001v2 (PDF, 5 pp.). Checagens numéricas: aritmética exata (`fractions.Fraction`), script `verifica_ward.py` (scratchpad; promover a `experiments/` com teste na Fase 0).*
