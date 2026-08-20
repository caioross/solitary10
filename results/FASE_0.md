# Fase 0 — Fundação e reprodução

Data: 2026-08-20. Executor: Claude (Fable 5) sob supervisão humana.
Escopo: SOMENTE Fase 0, conforme `PROMPT_FASE0.md`. Nenhum avanço para a Fase 1 sem aprovação explícita.

---

## 0. Resumo executivo

- Ambiente montado (Python 3.13.2, venv, sympy 1.14.0, pytest 9.1.1); **todos os testes verdes**.
- Buscas de sanidade executadas: nenhum amigo de 10 até 2·10⁶ (incondicional) nem no
  espaço estrutural até 10¹² — e a varredura estrutural tornou-se **incondicional**
  após as provas desta fase (Corolário da seção 4).
- Re-derivadas do zero, com prova completa, as quatro restrições básicas (Teoremas A–D):
  um amigo N de 10 é ímpar, é quadrado perfeito, 25 | N, e seu menor primo divisor é 5.
  Cada prova passou por verificação numérica independente (seção 5) e passada
  adversarial com 9 revisores (seção 6): **todas SÓLIDAS**, só ajustes cosméticos.
- Limite inferior exato: **N ≥ 1,53·10²⁴** `[PROVADO-CONDICIONAL: A–D + ω ≥ 10]`, afiado
  para **N ≥ 7,50·10²⁵** com o Teo. 1.9 de arXiv:2404.00624 (seção 7).
- 6 papers lidos em texto completo, uma nota por paper em `literatura/`; tabela do
  CLAUDE.md conferida item a item (seção 8). **Quatro divergências documentadas**
  (seção 10), incluindo dois defeitos reais em arXiv:2404.00624 (Lema 2.3; off-by-one
  no Remark 3.7 que enfraquece o Cor. 1.11) e o alcance real de arXiv:2412.02701
  (só r ≤ 5, não "todos os primos").
- Checagens web (seção 9): nada em 2025–26 supera ω ≥ 10; dois papers análogos novos
  (14 e 20); o enunciado "10 é solitário" JÁ está formalizado no formal-conjectures da
  DeepMind; a mathlib tem σ e `Nat.abundancyIndex`, mas nenhum lema de
  friendly/solitary.
- Três alvos propostos para a Fase 1 (seção 11). **Parado aqui, aguardando aprovação.**

---

## 1. Ambiente e testes

- Python 3.13.2 (venv em `venv/`), `sympy 1.14.0`, `pytest 9.1.1`, `mpmath 1.3.0`.
- `pytest -q`: **7 passed** (suíte original) — ver seção 5 para os testes novos desta fase.
- Git inicializado neste diretório (primeiro commit ao fim da fase).

## 2. Buscas de sanidade

| Busca | Comando | Espaço varrido | Resultado |
|---|---|---|---|
| Direta (incondicional) | `python experiments/busca_direta.py --limite 2000000` | todos os n ∈ [1, 2·10⁶] | únicos n com I(n) = 9/5: `[10]` — **nenhum amigo** |
| Estrutural (condicional) | `python experiments/busca_estrutural.py --limite-m 1000000` | N = m², m ímpar, 5 \| m, m ≤ 10⁶ (N até 10¹²) | **nenhum amigo** no espaço estrutural |

Rótulos:
- `[VERIFICADO-NUMERICAMENTE: 1 ≤ n ≤ 2·10⁶]` — 10 não tem amigo até 2·10⁶.
- `[VERIFICADO-NUMERICAMENTE: N = m², m ímpar, 5|m, m ≤ 10⁶]` — nenhum amigo estrutural
  até 10¹². Condicional às restrições de Ward; **as restrições usadas (ímpar, quadrado,
  5 | N) são exatamente as provadas na seção 4**, logo após esta fase a varredura passa a
  valer incondicionalmente: um amigo N ≤ 10¹² teria de ser quadrado ímpar múltiplo de 25
  (Teoremas A–C), i.e. N = m² com m ímpar e 5 | m ≤ 10⁶ — espaço integralmente varrido.

## 3. Preliminares

**Definições.** σ(n) = soma dos divisores positivos de n; I(n) = σ(n)/n (índice de
abundância, sempre racional exato). m, n são amigos se m ≠ n e I(m) = I(n).

**Equação do amigo.** I(10) = σ(10)/10 = (1+2+5+10)/10 = 18/10 = 9/5. Logo

> N é amigo de 10 ⟺ N ≥ 1, N ≠ 10 e 5·σ(N) = 9·N.   (★)

Observação: N = 1 não satisfaz (★) pois I(1) = 1 ≠ 9/5; assim N > 1 e N tem fator primo.

**Fato 0 (multiplicatividade).** σ é multiplicativa; se N = ∏ᵢ pᵢ^{eᵢ} (primos distintos),
σ(N) = ∏ᵢ σ(pᵢ^{eᵢ}) com σ(p^e) = 1 + p + ⋯ + p^e = (p^{e+1}−1)/(p−1). Consequentemente
I(N) = ∏ᵢ I(pᵢ^{eᵢ}), e cada fator I(pᵢ^{eᵢ}) > 1, pois na fatoração canônica eᵢ ≥ 1
(e I(p^e) = 1 + 1/p + ⋯ ≥ 1 + 1/p > 1).
*Prova:* padrão (divisores de mn com gcd(m,n)=1 são produtos únicos d₁d₂, d₁|m, d₂|n). ∎

**Lema 1.** Para todo n ≥ 1: I(n) = Σ_{d|n} 1/d.
*Prova:* a aplicação d ↦ n/d é uma bijeção do conjunto de divisores de n nele mesmo
(involução; o eventual ponto fixo d = √n não atrapalha — é só re-indexação da soma); logo
σ(n)/n = (Σ_{d|n} d)/n = Σ_{d|n} d/n = Σ_{d|n} 1/(n/d) = Σ_{e|n} 1/e. ∎

**Lema 2 (monotonia estrita sobre divisores).** Se d | n e d < n, então I(d) < I(n).
*Prova:* todo divisor e de d é divisor de n, logo pelo Lema 1,
I(d) = Σ_{e|d} 1/e ≤ Σ_{e|n} 1/e = I(n). A desigualdade é estrita porque o termo 1/n
ocorre na soma de I(n) mas não na de I(d) (n ∤ d, pois n > d). ∎

**Lema 3 (crescimento em e).** Para p primo fixo, I(p^e) é estritamente crescente em e,
e I(p^e) < p/(p−1) para todo e ≥ 0.
*Prova:* I(p^e) = 1 + 1/p + ⋯ + 1/p^e (Lema 1 aplicado a p^e); cada incremento de e soma
o termo positivo 1/p^{e+1}; a série completa converge a p/(p−1), cota estrita de qualquer
soma parcial. ∎

**Lema 4.** Se N satisfaz (★), então 5 | N e 9 | σ(N).
*Prova:* 5 | 5σ(N) = 9N e gcd(5,9) = 1 ⟹ 5 | N. Analogamente 9 | 5σ(N) e gcd(9,5)=1
⟹ 9 | σ(N). ∎

## 4. As quatro restrições básicas, re-derivadas

Seja N amigo de 10, i.e. N ≠ 10 satisfazendo (★).

### Teorema A — N é ímpar. `[PROVADO]`

*Prova.* Suponha 2 | N. Pelo Lema 4, 5 | N; como gcd(2, 5) = 1, segue 10 = lcm(2,5) | N.
Como N ≥ 1 e 10 | N, temos N ≥ 10; com N ≠ 10, N ≥ 20, logo o divisor 10 é próprio
(10 < N) e o Lema 2 dá I(10) < I(N), i.e. 9/5 < 9/5 — absurdo. ∎

### Teorema B — N é quadrado perfeito. `[PROVADO]`

*Prova.* Pelo Teorema A, N é ímpar, logo 9N é ímpar; por (★), 5σ(N) = 9N é ímpar, logo
σ(N) é ímpar. Escreva N = ∏ᵢ pᵢ^{eᵢ} com todos os pᵢ ímpares. Pelo Fato 0,
σ(N) = ∏ᵢ σ(pᵢ^{eᵢ}). Cada fator σ(pᵢ^{eᵢ}) = 1 + pᵢ + ⋯ + pᵢ^{eᵢ} é soma de eᵢ + 1
parcelas ímpares, portanto σ(pᵢ^{eᵢ}) ≡ eᵢ + 1 (mod 2). O produto ∏ᵢ σ(pᵢ^{eᵢ}) é ímpar
se e somente se todo fator é ímpar, i.e. todo eᵢ é par. Por fim, todos os expoentes
pares ⟺ N é quadrado perfeito: se eᵢ = 2fᵢ, então N = (∏ᵢ pᵢ^{fᵢ})²; reciprocamente,
se N = M², a fatoração única dá eᵢ = 2·v_{pᵢ}(M), par. ∎

### Teorema C — 25 | N. `[PROVADO]`

*Prova.* Pelo Lema 4, 5 | N, isto é v₅(N) ≥ 1. Pelo Teorema B, todo expoente na
fatoração de N é par; logo v₅(N) é par e ≥ 1, portanto v₅(N) ≥ 2, i.e. 25 | N. ∎

### Teorema D — o menor primo divisor de N é 5 (equivalente: 3 ∤ N, dado A e Lema 4). `[PROVADO]`

Como N > 1, N tem primos; 2 ∤ N (Teorema A) e 5 | N (Lema 4). Falta provar 3 ∤ N.

*Prova de 3 ∤ N.* Suponha 3 | N. Pelo Teorema B os expoentes são pares: escreva
v₃(N) = 2a ≥ 2 e v₅(N) = 2b ≥ 2 (Teorema C). Pelo Fato 0, I(N) = 9/5 é o produto dos
fatores I(p^{v_p}), todos > 1; logo, para qualquer subconjunto S dos primos de N,
∏_{p∈S} I(p^{v_p}) = (9/5) / ∏_{p∉S} I(p^{v_p}) ≤ 9/5, i.e. **qualquer subproduto de
fatores satisfaz ∏_{p∈S} I(p^{v_p}) ≤ 9/5**, com igualdade só se S contém todos os
primos de N. (O Lema 3 será usado nas minorações dos casos abaixo.)

Três casos:

**Caso 1: a ≥ 2** (i.e. 81 | N). Então, pelo Lema 3,
I(3^{2a})·I(5^{2b}) ≥ I(3⁴)·I(5²) = (121/81)·(31/25) = 3751/2025 > 3645/2025 = 9/5.
Subproduto excede 9/5 — contradição.

**Caso 2: a = 1, b ≥ 2** (i.e. 3² ‖ N e 625 | N). Então
I(3²)·I(5^{2b}) ≥ (13/9)·(781/625) = 10153/5625 > 10125/5625 = 9/5 — contradição.

**Caso 3: a = 1, b = 1** (i.e. v₃(N) = 2 e v₅(N) = 2 exatamente). Então σ(3²) = 13 e
σ(5²) = 31 são fatores de σ(N) = ∏ σ(p^{v_p}), logo 13 | σ(N). Por (★),
σ(N) = 9N/5 = 9·(N/5) com N/5 inteiro; de 13 | 9·(N/5) e gcd(13,9) = 1 vem
13 | N/5, em particular **13 | N**. Como 13 ∉ {3,5}, o primo 13 comparece na fatoração
com expoente par ≥ 2 (Teorema B), logo I(13^{v₁₃}) ≥ I(13²) = 183/169. Mas então o
subproduto
I(3²)·I(5²)·I(13²) = (13/9)·(31/25)·(183/169) = 73749/38025 > 68445/38025 = 9/5
— contradição. (Verificação exata: 13·31·183 = 73749; 9·25·169 = 38025; 9·38025/5 = 68445.)

Nos três casos chegamos a absurdo; logo 3 ∤ N, e o menor primo divisor de N é 5. ∎

**Observação (quase-amigo 225).** O Caso 3 "quase" produz um amigo: N = 3²·5² = 225 tem
5σ(225) = 5·403 = 2015, contra 9·225 = 2025 — diferença de apenas 10 (I(225) = 403/225
contra 405/225 = 9/5). É o mecanismo exato que a prova explora: o déficit só poderia ser
coberto pelo primo 13 forçado, que estoura 9/5.

### Corolário (usado na seção 2)

Todo amigo de 10 é da forma N = m² com m ímpar e 5 | m. Portanto a busca estrutural da
seção 2 é exaustiva para N ≤ 10¹², **incondicionalmente**:
`[PROVADO]` + `[VERIFICADO-NUMERICAMENTE: N ≤ 10¹²]` ⟹ **o menor amigo de 10, se
existir, excede 10¹²** (e de fato muito mais — seção 7).

## 5. Verificação numérica independente

Arquivo: `tests/test_fase0_proofs.py` (roda no `pytest -q`). Independência: os testes
usam uma implementação de σ por divisão por tentativa (`_sigma_trial`), sem sympy, e
cruzam-na com `core.abundancy.sigma` num intervalo; todas as comparações por inteiros /
`Fraction` exatos. Verifica:

1. Cross-check `_sigma_trial(n) == sigma(n)` para n ≤ 20 000.
2. Lema 1 (I(n) = Σ 1/d) para n ≤ 2 000, com `Fraction`.
3. Lema 2 (monotonia estrita em divisores próprios) para n ≤ 3 000.
4. Lema 3 (I(p^e) crescente, < p/(p−1)) para p ≤ 37, e ≤ 12.
5. Paridade de σ (mecanismo do Teorema B): para n ímpar ≤ 60 000, σ(n) ímpar ⟺ n quadrado.
6. As três desigualdades exatas do Teorema D (casos 1–3), por multiplicação cruzada de inteiros.
7. Mecanismo do Teorema A: para todo múltiplo de 10 com 10 < n ≤ 300 000, 5σ(n) > 9n.
8. Mecanismo do Teorema A (ramo par completo, sugerido pela passada adversarial):
   nenhum n par ≤ 200 000, n ≠ 10, satisfaz 5σ(n) = 9n.
9. Mecanismo do Teorema D: para todo N = m² com 15 | m, m ≤ 4 000, 5σ(N) ≠ 9N.
10. 225: 5σ(225) = 2015 ≠ 2025 = 9·225.

Resultado: **verde** (ver saída de `pytest -q` registrada na seção 12).

Varreduras adversariais adicionais (executadas pelos revisores da seção 6, com crivos
exatos independentes; registradas aqui como reforço, não como substituto dos testes):
- única solução de 5σ(n) = 9n em [1, 10⁷] (todas as paridades) é n = 10;
- nenhum n ímpar ≤ 10⁸ com 5σ(n) = 9n; paridade de σ ⟺ quadrado confirmada nos
  5·10⁷ ímpares ≤ 10⁸;
- nenhum N = m², 15 | m, m ≤ 150 000 (N até 2,25·10¹⁰) satisfaz a equação do amigo.

## 6. Passada adversarial

Executada em 2026-08-20 por 9 subagentes revisores independentes (workflow
`fase0-passada-adversarial`), cada um instruído a **refutar** — recalcular toda fração
com aritmética exata, caçar lacunas, hipóteses escondidas, circularidade e
contraexemplos numéricos. Veredictos:

| Alvo | Revisor(es) | Veredicto | Problemas |
|---|---|---|---|
| Fato 0 + Lemas 1–4 | 1 | **SÓLIDA** | 2 cosméticos (redação) — corrigidos |
| Teorema A | 2 (lógica + contraexemplo) | **SÓLIDA** ×2 | 3 cosméticos — corrigidos; varredura até 10⁷ sem contraexemplo |
| Teorema B | 2 (lógica + contraexemplo) | **SÓLIDA** ×2 | 4 cosméticos — corrigidos; mecanismo verificado até 10⁸ |
| Teorema C | 1 | **SÓLIDA** | 1 cosmético — corrigido |
| Teorema D | 2 (lógica + contraexemplo) | **SÓLIDA** ×2 | 4 cosméticos — corrigidos; todas as desigualdades re-verificadas por multiplicação cruzada de inteiros; varredura de quadrados múltiplos de 225 até 2,25·10¹⁰ |
| Limite inferior (seção 7) | 1 | **LACUNA_MENOR** | a desigualdade e o rótulo estavam corretos, mas a "Nota" do script era enganosa (dizia que as congruências não elevam o limite, omitindo que o Teo. 1.9 de arXiv:2404.00624 **invalida a configuração mínima** e dá fator ≥ 49 de graça) e a docstring tinha hipótese fantasma. **Ambos corrigidos**; limite afiado incorporado à seção 7 |

Nenhum problema `fatal` ou `sério` em nenhuma prova. Todos os apontamentos cosméticos
foram aplicados ao texto das seções 3–4 (citação explícita do Fato 0 na prova de B,
justificativa da equivalência "expoentes pares ⟺ quadrado" via fatoração única,
positividade explícita no Teorema A, notação do Caso 2 de D, redação dos Lemas 1 e do
Fato 0). Só após essa rodada os Teoremas A–D receberam o rótulo `[PROVADO]`
(regra de rigor #3).

## 7. Limite inferior para N

Script: `experiments/limite_inferior.py` (aritmética 100% inteira; floats só em exibição).

**Teorema E (limite inferior).** Se N é amigo de 10, então

> N ≥ (5·7·11·13·17·19·23·29·31·37)² = 1236789689135² = **1 529 648 735 150 649 937 048 225** ≈ 1,53·10²⁴.

Rótulo: `[PROVADO-CONDICIONAL: Teoremas A–D (provados nesta fase) + ω(N) ≥ 10
(arXiv:2310.15900, Thackeray, Indagationes Math. 2024 — verificado por leitura,
NÃO re-derivado)]`

*Prova.* Pelos Teoremas A e D, todo primo divisor de N é ≥ 5; pelo Teorema B, todo
expoente é par, logo ≥ 2. Se q₁ < q₂ < ⋯ < q_k são os primos de N com k = ω(N) ≥ 10,
então qⱼ ≥ sⱼ (o j-ésimo menor primo ≥ 5), donde
N = ∏ qⱼ^{eⱼ} ≥ ∏_{j=1}^{10} qⱼ² ≥ ∏_{j=1}^{10} sⱼ² = (5·7·⋯·37)². ∎

**As congruências conhecidas não elevam este limite:** o conjunto mínimo
{5,7,11,13,17,19,23,29,31,37} já contém witnesses para todas — 11 e 31 ≡ 1 (mod 10);
7, 13, 19, 31, 37 ≡ 1 (mod 6); e primos ≡ 1 (mod 3) podem carregar expoente 2, que já
satisfaz 2 ≡ 2 (mod 6) (Ward). Logo nenhuma delas força primo fora do conjunto mínimo.

**Teorema E′ (limite afiado, acrescentado após a passada adversarial).** A configuração
mínima do Teorema E (todos os expoentes = 2) tem N = 5²·m² com m = 7·11·⋯·37 **livre de
quadrados** — proibida pelo Teorema 1.9 de arXiv:2404.00624 (e, independentemente, pela
restrição de expoentes do Teorema 1.2 de arXiv:2504.08295). Logo algum primo ≠ 5 tem
expoente ≥ 4, e o custo mínimo é elevar o 7 (fator 7² = 49):

> N ≥ 49·(5·7·⋯·37)² = **74 952 788 022 381 846 915 363 025** ≈ 7,50·10²⁵ (26 dígitos).

Rótulo: `[PROVADO-CONDICIONAL: Teoremas A–D + ω(N) ≥ 10 (arXiv:2310.15900) +
Teorema 1.9 de arXiv:2404.00624]`. A configuração mínima ajustada (expoente 4 no 7)
satisfaz todas as demais restrições conhecidas da tabela (witnesses conferidos no
script), então nenhuma outra restrição eleva o limite "de graça".

Comparações (todas exatas, verificadas no script):
- Corolário 1.6 de arXiv:2504.08295 com ω = 10: N > 625·9⁷ = 2 989 355 625 ≈ 3,0·10⁹ — **muito mais fraco**.
- Varredura estrutural desta fase: N > 10¹² — mais fraco.
- Ou seja: o argumento de assinatura de primos supera em 12–14 ordens de grandeza a fronteira computacional atual do repo.
- Alegação **não certificada** da literatura: "menor amigo de 10 > 10³⁰" (OEIS A074902,
  citada na conclusão de arXiv:2404.00624 sem certificação publicada). É mais forte que
  os Teoremas E/E′, mas NÃO deve ser usada como hipótese; produzir uma cota certificada
  ≥ 10³⁰ é exatamente o alvo (a) da Fase 1.

## 8. Literatura — notas de leitura e fidelidade da tabela do CLAUDE.md

Todos os 6 papers foram lidos em **texto completo** (nenhuma nota baseada só em
abstract); uma nota por paper em `literatura/`, com enunciados exatos, método de prova,
verificação numérica das constantes (Fraction exata) e seção de fidelidade à tabela.

| Paper | Nota | Fidelidade da tabela | Destaques da leitura |
|---|---|---|---|
| Ward 2008 (arXiv:0806.1001; IJMCS 3(3) 153–158) | `nota_ward_2008.md` | **FIEL** | ω ≥ 6 é do próprio Ward, incondicional e sem computador; "se for único" em (v) = único primo com AMBAS as propriedades; errata de numeração no paper (a "propriedade 7" citada não existe como item impresso); as 9 comparações racionais da prova re-verificadas — duas apertadíssimas (4147/2304 e 24871/13824, a < 9·10⁻⁴ de 9/5); caso {7,11,13,23} só fecha com o truque σ(5²) = 31 \| σ(N) |
| Chatterjee–Mandal–Mandal (arXiv:2404.00624 v5) | `nota_2404.00624.md` | **FIEL**, com omissões (Teo. 1.10 e Cor. 1.11 não estão na tabela) | ver §10: Lema 2.3 falso como enunciado (caso de igualdade), off-by-one no Remark 3.7 herdado pelo Cor. 1.11, typo no Caso 12; tabela de f_p^q amostrada e conferida |
| Thackeray (arXiv:2310.15900; Indagationes Math. 35(3) 595–607, 2024) | `nota_2310.15900.md` | **FIEL** (precisão: método de Nielsen **2007**; autor é H. R. Thackeray, não o trio Mandal) | Cor. 6/7 novos: v₅(N) ≤ (ω(N)−1)² + 1; gargalos para ω ≥ 11 identificados: v₅ ∈ {2,6,10,12,46} com σ(5^{v₅}) primo; v₅ = 46 exigiria análogo da Prop. 9 para um primo de 33 dígitos; Cor. 6 vale para qualquer quadrado ímpar — candidato a lema uniforme 2p |
| Mandal–Mandal (arXiv:2404.05771; Resonance 30, 2025) | `nota_2404.05771.md` | **FIEL** (a forma em índice de primo, q₂ < p_⌈7ω/3⌉ etc., é mais forte que a logarítmica publicada) | com ω = 10: q₂ ≤ 83 (< p₂₄ = 89), q₃ < 193, q₄ < 431 — poda forte para a Fase 1; achado do revisor (rotulado pendente): o método parece estender-se a q₅ < p_{28ω} |
| Mandal (arXiv:2412.02701 **v4**; Analele Oradea 33(1) 5–12, 2026) | `nota_2412.02701.md` | **DIVERGENTE** — ver §10 | família paramétrica (A,B) de limites para q_r efetiva só para 2 ≤ r ≤ 5; melhora q₃, q₄ de 2404.05771 (427/100 e 41/5); com ω = 10 (forma afiada): q₂ < 89, q₃ < 191, q₄ < 421, q₅ < 1847; r = 5 admissível é bônus não explicitado no paper |
| Mandal (arXiv:2504.08295; News Bull. Calcutta Math. Soc. 48, 2025) | `nota_2504.08295.md` | **FIEL** | 9 ‖ σ(F) (Remark 2.4) é o motor mod-3; Teo. 1.5 generaliza para qualquer quadrado com I(N) = r: N > d(N)²/r² — candidato a lema uniforme 2p; congruências-chave das provas re-verificadas à mão |

Papers analisados = estado da arte completo do nicho até 2026-08-20 (checagem de
novidade na seção 9.1).

## 9. Checagens web

Data das buscas: 2026-08-20. Executadas por subagentes com WebSearch/WebFetch;
IDs arXiv verificados individualmente nas páginas `/abs`.

### 9.1 Novidades 2025–2026 no nicho (regra de rigor #4)

**Novos papers encontrados (não constavam do CLAUDE.md):**

| Paper | O que traz | Impacto aqui |
|---|---|---|
| arXiv:2503.11694 — Sagar Mandal, "A note on solitary numbers" (v1 mar/2025 era "Is 14 a Solitary Number?"; NNTDM 31(3) 2025, 617–623) | Amigo F de 14: ímpar e NÃO-quadrado; 7 \| F com expoente par; ≤ 2 primos com expoente ímpar; restrições mod 8; 3 e 5 não dividem F simultaneamente | Análogo da família 2p para p = 7. Não supera nada sobre o 10. Item que faltava na lista de análogos |
| arXiv:2409.04451 — Chatterjee, S. Mandal, S. Mandal, "On Characterizing Potential Friends of 20" (v4 set/2025; Ann. West Univ. Timisoara 61(1) 2025, 205–229) | Amigo de 20 é 2·5^{2a}·m², gcd(3,m) = gcd(7,m) = 1, ω ≥ 6, limites p/ maior primo | 20 = 2²·5 (fora da família 2p); útil para comparação de técnicas na Fase 3 |

**Atualizações de papers já listados:**
- **arXiv:2412.02701 ganhou v4 (2025-10-16)**, publicada em Analele Univ. Oradea 33(1)
  2026, 5–12; o abstract atual alega limites **melhores** para o 3º e 4º menores primos
  que os de 2404.05771. A nota de leitura deste repo é da versão atual (v4).
- arXiv:2504.08295 publicado: News Bull. Calcutta Math. Soc. 48(1–3) 2025, 21–32.

**Periféricos 2026** (registrados por completude): arXiv:2601.07444 (formalização Lean 4
de números *amicable* — conceito ≠ friendly; arte prévia para a Fase 4); arXiv:2606.25849
(Erdős 1061 sobre σ(a)+σ(b)=σ(a+b)); arXiv:2607.25278 (weird numbers com abundância alta).

**Negativos importantes (estado da arte inalterado):** nenhuma melhoria de ω(N) ≥ 10
(alvo ω ≥ 11 segue aberto); nenhum paper dedicado ao 15; nenhum teorema uniforme para a
família 2p; nada novo do trio vigiado após abr/2025.

### 9.2 formal-conjectures (Google DeepMind)

**SIM — o enunciado está lá.** Verificação decisiva e reprodutível: `git clone --depth 1`
+ grep completo (commit `9f5ee773841921f460b4a26a3552f5eca4accaa0`, 2026-08-19).

- Arquivo: `FormalConjectures/Wikipedia/SolitaryNumber.lean`, namespace `SolitaryNumber`.
- `Friendly (m n : ℕ) : Prop := 0 < m ∧ 0 < n ∧ σ 1 m * n = σ 1 n * m` — **reflexiva**
  (não exige m ≠ n; multiplicação cruzada para evitar racionais).
- `IsSolitary (n : ℕ) : Prop := 0 < n ∧ ∀ m, Friendly m n → m = n` — equivalente à
  definição deste projeto (todo amigo é o próprio n).
- `theorem is_ten_solitary : answer(sorry) ↔ IsSolitary 10` com `@[category research open, AMS 11]`.
- No mesmo arquivo: `infinite_club_exists` (clube infinito de abundância, também aberta).
- Vizinho: `ErdosProblems/470.lean` define `AbundancyIndex (n : ℕ) : ℚ` (weird numbers);
  não compartilha definições com SolitaryNumber.lean.
- **Não** há formalização das restrições de Ward/Mandal — só o enunciado bruto (provas `sorry`).

### 9.3 mathlib (Lean 4) — estado para a Fase 4

O que **existe** (docs oficiais, ago/2026):
- `ArithmeticFunction.sigma (k : ℕ)` em `Mathlib/NumberTheory/ArithmeticFunction/Misc.lean`
  (o monólito antigo foi dividido); `sigma_one_apply`, `sigma_apply_prime_pow`, etc.
  Convenção: `σ 1 0 = 0`.
- Multiplicatividade: `ArithmeticFunction.isMultiplicative_sigma`.
- `Nat.Perfect` em `Mathlib/NumberTheory/Divisors.lean`; Euclides–Euler no **Archive**
  (`Archive/Wiedijk100Theorems/PerfectNumbers.lean`), não na mathlib propriamente.
- `Mathlib/NumberTheory/FactorisationProperties.lean`: `Nat.Abundant/Deficient/
  Pseudoperfect/Weird` **e `Nat.abundancyIndex : ℕ → ℚ`** (exatamente o I(n) do projeto),
  com `Nat.abundant_iff_two_lt_abundancyIndex` e `Nat.abundancyIndex_le_of_dvd`
  (desigualdade **não-estrita**).

O que **não existe** (buscas Loogle com 0 hits relevantes): friendly/solitary/amicable;
multiplicatividade do abundancyIndex; fórmula e monotonia de I(p^e); **versão estrita**
do Lema 2 deste relatório (d | n, d < n ⟹ I(d) < I(n)); critério de Greening.
Consequência: `IsSolitary 10` é enunciável hoje (e o formal-conjectures já o faz), mas
todos os lemas de prova teriam de ser formalizados do zero. O critério de Greening seria
contribuição natural e pequena à mathlib (candidata para a Fase 4).

## 10. Divergências encontradas

Regra de rigor #7: divergência é achado. Quatro divergências reais, nenhuma escondida:

### 10.1 arXiv:2404.00624 (v5) — três defeitos no paper, um deles com consequência

1. **Lema 2.3 é falso como enunciado** (desigualdade estrita a·n < Σ a^{c_i} falha na
   partição toda de 1's, onde vale igualdade). Correção: a·n ≤ Σ a^{c_i}, igualdade sse
   todos c_i = 1. O Lema 3.6 e o Teorema 1.10 **não** são afetados (usam só o valor do
   mínimo, que está certo). `[VERIFICADO: exaustivamente para a ≤ 5]`
2. **Remark 3.7, eq. (7): off-by-one na derivação exibida.** O paper escreve
   "2a + 2Ω(m) ≥ 2ω(N) + 6a − 4" e conclui "Ω(m) ≥ ω(N) + 2a − 1"; a linha exibida dá
   apenas **Ω(m) ≥ ω(N) + 2a − 2**. Não há ganho de paridade possível (ambos os lados
   são pares). **Consequência: o Corolário 1.11, como provado, sustenta apenas
   N < 5·6^((2^{K−2a+2}−1)²)** — mais fraco que o enunciado. O enunciado original pode
   ser verdadeiro, mas exigiria melhorar o Teorema 1.10; até lá, usar SÓ a versão
   corrigida. `[VERIFICADO: no texto v5 via arxiv.org/html/2404.00624v5, por duas
   leituras independentes + álgebra re-derivada nesta fase]`
3. **Typo no Caso 12 do Teorema 1.2:** fator impresso 381/361 = I(19²) deveria ser
   I(23²) = 553/529; refeita a conta com o valor certo, a conclusão do caso permanece.

### 10.2 arXiv:2412.02701 (v4) — enunciado principal mais fraco do que o título/abstract

A linha #6 da tabela do CLAUDE.md ("limites superiores para TODOS os primos
divisores") reproduz a alegação do título/abstract, mas o Teorema 1.2 do paper só
produz limites para o r-ésimo menor primo com **2 ≤ r ≤ 5**: para r ≥ 6 o denominador
do limiar de admissibilidade fica negativo (X₆ = 82944/85085 < 1, verificado com
aritmética exata) e não existe par (A,B) admissível — o método não fecha.
**Correção sugerida para a tabela:** "família paramétrica de limites para o r-ésimo
menor primo divisor, efetiva para 2 ≤ r ≤ 5 (inclui q₅, novo; constantes melhores para
q₃, q₄ que #5); r ≥ 6 fora do alcance do método".

### 10.3 Ward 2008 — errata menor de numeração

A lista de propriedades impressa termina no item 6, mas a prova cita "6 and 7"; a
"propriedade 7" (monotonia de I(p^e) com supremo p/(p−1)) existe no texto corrido, sem
rótulo. Sem impacto matemático; citar propriedades pelo enunciado, não pelo número.

### 10.4 Nota interna (corrigida nesta fase)

A primeira versão do script `limite_inferior.py` desta fase afirmava que "as
congruências conhecidas não elevam o limite", omitindo que o Teo. 1.9 de 2404.00624
invalida a configuração mínima (fator 49 disponível). Detectado pela passada
adversarial; corrigido (Teorema E′). Registrado por honestidade metodológica.

**Nenhuma divergência entre nossas computações e os RESULTADOS PRINCIPAIS da
literatura**: todas as constantes e desigualdades re-verificadas bateram; os defeitos
acima são pontuais e não derrubam nenhum teorema usado como hipótese neste projeto
(em particular ω(N) ≥ 10 permanece intacto).

## 11. Propostas de alvos para a Fase 1

Três alvos concretos, em ordem de recomendação (aguardando aprovação humana):

### Alvo 1 — Motor de busca em árvore certificado + reprodução automática de ω ≤ 7
**O quê:** implementar em `core/` a busca em árvore sobre assinaturas (pᵢ, 2eᵢ) com os
três mecanismos de poda já mapeados na literatura: (a) poda inferior — configuração
mínima divide N, I(config) > 9/5 mata o ramo; (b) poda superior — ∏ p/(p−1) < 9/5 mata
o ramo; (c) **propagação de divisibilidade** — σ(p^{2a}) | σ(N) = 9N/5 força primos
novos (Teoremas 1.3/1.7 e Lema 2.1 de 2404.00624, tudo por ordem multiplicativa,
exato). Validação: reproduzir automaticamente ω ≥ 6 (Ward, incl. o caso {7,11,13,23})
e as 19 cadeias de ω ≥ 7 (2404.00624). Meta quantitativa: **cota inferior certificada
para o menor amigo de 10 ≥ 10³⁰** (superando a alegação não certificada da OEIS).
**Esforço estimado:** 2–4 sessões. Risco baixo; entrega verificável por testes.

### Alvo 2 — Atacar ω(N) ≥ 11 pelo método de Thackeray
**O quê:** replicar a DFS de 2310.15900 (poda por racionais exatos, Prop. 3 com
t_min = t_max = 9/5) usando o motor do Alvo 1 + Cor. 7 (v₅(N) ≤ (ω−1)² + 1) + primos
especiais (31, 19531). Os gargalos já estão mapeados na nota de leitura: os casos
v₅ ∈ {2, 6, 10, 12, 46} em que σ(5^{v₅}) é primo; v₅ = 46 exigiria um análogo da
Prop. 9 para um primo de 33 dígitos. Submeta realista: fechar sistematicamente os
casos (k, v₅) para k = 10 e **quantificar** a parede do v₅ = 46 (mesmo que ω ≥ 11
não saia, o mapa dos casos residuais é publicável como nota).
**Esforço estimado:** 3–6 sessões, exploratório. Risco médio-alto; fracassos parciais
vão para FRACASSOS.md com o caso exato que resistiu.

### Alvo 3 — Colheita de corolários pequenos e novos (com busca de novidade)
**O quê:** três frutos baixos identificados nas leituras, cada um exigindo prova
escrita + passada adversarial + busca de novidade antes de qualquer alegação:
(i) o limite q₅ (r = 5 admissível em 2412.02701 v4, não explicitado no paper; e o
esboço independente q₅ < p_{28ω} da nota de 2404.05771); (ii) as instâncias afiadas
em ω = 10: q₂ < 89, q₃ < 191, q₄ < 421, q₅ < 1847 — cruzá-las com o motor do Alvo 1
para elevar o Teorema E′; (iii) comunicar aos autores (ou registrar em nota) as
correções da seção 10 (Lema 2.3, Remark 3.7/Cor. 1.11, r ≥ 6 em 2412.02701) — é
contribuição real e barata ao nicho.
**Esforço estimado:** 1–2 sessões. Risco baixo.

**Recomendação:** Alvo 1 primeiro (é pré-requisito de 2 e turbina 3.ii); Alvo 3 pode
correr em paralelo por ser barato. Fase 3 (família 2p) ganhou dois candidatos a lema
uniforme nas leituras (Cor. 6 de Thackeray para quadrados ímpares; Teo. 1.5 de
2504.08295 generalizado N > d(N)²/r²) — registrados para quando a Fase 3 abrir.

## 12. Registro de execução

Ambiente: Windows 11, Python 3.13.2, venv local; sympy 1.14.0, pytest 9.1.1, mpmath 1.3.0.

```
> pytest -q                                   # suíte inicial (7 testes originais)
7 passed in 0.65s

> pytest -q                                   # suíte final (com tests/test_fase0_proofs.py)
17 passed in 556.85s (0:09:16)                # a suíte é lenta de propósito (varreduras
                                              # exaustivas exatas); rodar em background

> python experiments/busca_direta.py --limite 2000000
Intervalo varrido: [1, 2000000]
n com I(n) = 9/5: [10]
[VERIFICADO-NUMERICAMENTE] Nenhum amigo de 10 no intervalo.

> python experiments/busca_estrutural.py --limite-m 1000000
Espaço varrido: N = m^2, m ímpar múltiplo de 5, m <= 1000000
(cobre candidatos estruturais até N = 1.00e+12)
[VERIFICADO-NUMERICAMENTE | condicional a Ward] Nenhum amigo no espaço varrido.

> python experiments/limite_inferior.py
Produto dos 10 primos: 1236789689135
LIMITE BASE:   N >= 1529648735150649937048225      (25 dígitos, ~1.5296e+24)
LIMITE AFIADO: N >= 74952788022381846915363025     (26 dígitos, ~7.4953e+25)
(rótulos e comparações na saída completa do script)
```

Subagentes (reprodutibilidade da parte não-computacional): workflow de literatura/web —
9 agentes, ~1,6M tokens (incluindo re-execução após limite de sessão); workflow
adversarial — 9 agentes, ~0,6M tokens. Prompts e retornos completos nos transcripts da
sessão. Toda computação citada como evidência está em scripts versionados neste repo;
as varreduras extras dos revisores (10⁷/10⁸/2,25·10¹⁰) são reforço não versionado e
estão registradas como tal na seção 5.

**Fase 0 encerrada. Aguardando aprovação humana explícita para abrir a Fase 1.**
