# ERRATA — defeitos verificados na literatura de amigos de 10 e 20

Catálogo dos defeitos encontrados na literatura, **re-verificados do zero em
2026-08-21** (segunda passada, independente da Fase 0) diretamente sobre o texto
publicado, e certificados por `experiments/verifica_erratas.py` + `tests/test_erratas.py`.

Material de publicação: `publicacao/errata_friends_of_10.tex` (nota em inglês) e
`publicacao/GUIA_PUBLICACAO.md` (procedimento).

## Fontes exatas conferidas nesta passada

| Sigla | Paper | Versão lida | Status editorial |
|---|---|---|---|
| P1 | Chatterjee, S. Mandal, S. Mandal, *A note on necessary conditions for a friend of 10* | arXiv:2404.00624**v5** (17/jan/2025), HTML LaTeXML | **preprint** (sem journal-ref no arXiv em 2026-08-21) |
| P2 | idem, *On Characterizing Potential Friends of 20* | arXiv:2409.04451**v4** | **publicado**: Ann. West Univ. Timisoara — Math. Comput. Sci. 61(1) (2025) 205–229 |
| P3 | S. Mandal, *Prime Divisors of 10's Friends: A Generalization of Prior Bounds* | arXiv:2412.02701**v4** (16/out/2025) | **publicado**: Analele Univ. Oradea Fasc. Mat. 33(1) (2026) 5–12 |
| P4 | S. Mandal, *Exploring the Relationships Between the Divisors of Friends of 10* | arXiv:2504.08295v1 | publicado: News Bull. Calcutta Math. Soc. 48(1–3) (2025) 21–32 — **herda** o defeito E4 (cita o Cor. 1.11 na forma original) |

Método desta re-verificação: download do HTML do arXiv, extração do LaTeX via
atributos `alttext` (conferência caractere a caractere dos enunciados citados) e
recomputação de toda aritmética com `int`/`Fraction`. Nenhum float sustenta afirmação.

---

## E1 — [P1] Lema 2.3 = [P2] Lema 23: **falso como enunciado** `[PROVADO]`

**Texto do paper (verbatim):** "Let (c₁,…,c_k) be any partition of n … then for any
integer a > e we have `an < Σ a^{c_i}`", com o passo (1) da prova "`ac_i < a^{c_i}`
para cada c_i ≥ 1".

**Defeito:** ψ(x) = ax − a^x é estritamente decrescente em [1,∞) para a > e, mas
ψ(1) = 0 — logo `ac ≤ a^c` com **igualdade** em c = 1. Na partição toda de 1's vale
`a·n = Σ a^{c_i}`. Menor contraexemplo: n = 1, a = 3 (3 = 3).

**Correção:** `a·n ≤ Σ a^{c_i}`, com igualdade **sse** todo c_i = 1.

**Consequência:** nenhuma nos resultados finais. O Lema 3.6 [P1] / Lema 24 [P2]
("mínimo de L_{2a−1,5} é 8a−4") tem **enunciado correto**, mas a prova exibida conclui
desigualdade **estrita** — o que negaria que o mínimo seja atingido. Os próprios papers
registram, na nota logo após a prova, que o mínimo está em A_{2a−1,5}(2a−1), isto é,
exatamente no caso de igualdade: **contradição interna ao texto**, resolvida pela
versão corrigida do lema.

**Certificado:** `verifica_erratas.py --bloco e1` (396 partições, 3 ≤ a ≤ 8, n ≤ 8:
todas as violações da forma estrita são igualdades e todas na partição (1,…,1)) e
`--bloco e2` (mínimo 8a−4 atingido, a = 1..7).

---

## E2 — [P1] Remark 3.7, eqs. (7) e (8): **off-by-one** `[PROVADO]`

**Texto do paper (verbatim):** "Since Ω(N) ≥ 2ω(N)+6a−4, … Ω(5^{2a}) + Ω(m²) =
2a + 2Ω(m) ≥ 2ω(N) + 6a − 4 i.e; **Ω(m) ≥ ω(N) + 2a − 1** (7)"; e daí
"**Ω(m) ≥ ω(m) + 2a** (8)".

**Defeito:** da linha exibida segue 2Ω(m) ≥ 2ω(N) + 4a − 4, ou seja
**Ω(m) ≥ ω(N) + 2a − 2**. Ambos os lados são pares — não há ganho de paridade a
extrair. Como 5^{2a} ‖ N implica 5 ∤ m e ω(N) = ω(m) + 1, a forma correta de (8) é
**Ω(m) ≥ ω(m) + 2a − 1**.

**A lacuna não é fechável pelo argumento do próprio paper:** para obter (7) seria
preciso Ω(N) ≥ 2ω(N) + 6a − 2, mas o valor 2ω(N) + 6a − 4 é o **ótimo exato** da
relaxação usada na prova do Teorema 1.10 (Proposição em `publicacao/`): a configuração
com 2a−1 primos ≡ 1 (mod 10) de expoente 4 e os demais de expoente 2 satisfaz todas as
restrições empregadas e atinge o limite. Se (7) é verdadeira, exige argumento novo.

**Evidência de que é deslize isolado:** em [P2] (amigos de 20) a passagem análoga está
**correta**: de Ω(N) ≥ 2ω(N)+6a−5 com N = 2·5^{2a}m² sai 1 + 2a + 2Ω(m) ≥ 2ω(N)+6a−5,
logo Ω(m) ≥ ω(N) + 2a − 3 — exatamente a consequência inteira.

**Certificado:** `verifica_erratas.py --bloco e3` (ótimo da relaxação = 2ω+6a−4 em 48
pares (a, ω)) e `--bloco e4` (152 testemunhas inteiras que satisfazem a desigualdade
exibida e violam a eq. (7)).

---

## E3 — [P1] Corolário 1.11: expoente enfraquece de K−2a+1 para **K−2a+2** `[PROVADO]`

**Texto do paper:** "Since Ω(m) ≤ K, we have from (7) that K − 2a + 1 ≥ ω(N)", donde
`N < 5·6^{(2^{K−2a+1}−1)²}`.

**Correção (consequência direta de E2):** de (7′) sai ω(N) ≤ K − 2a + 2, logo o que a
prova sustenta é

> **N < 5·6^{(2^{ω(N)}−1)²} < 5·6^{(2^{K−2a+2}−1)²}.**

**Propagação:** [P4] (arXiv:2504.08295, §1) cita o Corolário 1.11 na forma original —
mesma substituição se aplica lá.

---

## E4 — [P3] Teorema 1.2: efetivo só para **2 ≤ r ≤ 5** `[PROVADO]`

**Texto do paper:** título e abstract prometem "upper bounds for **each** of the prime
divisors of a friend of 10"; o Teorema 1.2 vale sob a condição
`A/B > 1 / ( (36/25)·∏_{4≤i≤r+1}(1 − 1/p_i) − 1 )`.

**Defeito:** escrevendo X_r = (36/25)·∏_{4≤i≤r+1}(1 − 1/p_i), o passo final da prova
exige `1 + B/A < X_r`; como `1 + B/A > 1` para A, B > 0, isso só é possível se
**X_r > 1**. E X_r é estritamente decrescente com

| r | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|
| X_r | 36/25 | 216/175 | 432/385 | 5184/5005 | **82944/85085 < 1** |

Logo, para r ≥ 6: na leitura pretendida (limiar positivo, que é a usada nas próprias
instanciações do paper — 25/11, 175/41, 385/47 são exatamente 1/(X_r − 1)) **não
existe par (A,B) admissível**; na leitura literal (limiar negativo ⇒ condição vazia) a
prova não sustenta a conclusão, pois já a parte fixa F_r = (5/4)·∏_{4≤j≤r+1} p_j/(p_j−1)
satisfaz F_r ≥ 9/5 para r ≥ 6 (F_6 = 17017/9216 > 9/5) — a contradição não fecha com
nenhuma escolha de primos da cauda. Em ambas as leituras: **nenhum limite para q_r com
r ≥ 6**.

**Correção sugerida:** restringir título/abstract/enunciado a "o r-ésimo menor divisor
primo, para 2 ≤ r ≤ 5". Nada mais no paper é afetado (Teo. 1.1 e Cor. 1.1 usam r ≤ 4).

**Bônus disponível e não enunciado:** para r = 5 o limiar é 5005/179, então
(A,B) = (113,4) é admissível e a forma afiada da prova dá `q_5 < p_{⌈113·ω(n)/4⌉}`;
com ω(n) = 10, `q_5 < p_283 = 1847`.

**Erratas menores no mesmo paper:** "From (3) and (4)" deveria ser "From (1) and (4)";
o `A > B > 1` invocado no Remark 1.1 só decorre das hipóteses quando 1/(X_r − 1) > 1,
isto é, no mesmo intervalo 2 ≤ r ≤ 5.

**Certificado:** `verifica_erratas.py --bloco e5` (X_r e F_r exatos para 2 ≤ r ≤ 12,
identidade F_r·X_r = 9/5, inexistência de (A,B) para r ≥ 6).

---

## E5 — [P1] Caso-12 do Teorema 1.2: erro de digitação, sem consequência `[PROVADO]`

A cadeia do Caso-12 é 5, 7, 11, 13, **23**, p₆, mas o último fator impresso nas duas
desigualdades é 381/361 = I(19²), no lugar de I(23²) = 553/529. Recomputando exato:
I(5⁴·7²·11²·13²·23²) = 1111642101/614631875 > 9/5 e
I(5²·7²·11²·13²·23²·31²) = 15547332483/8383578775 > 9/5 — a conclusão do caso
permanece.

**Certificado:** `verifica_erratas.py --bloco e6`.

---

## O que NÃO está em questão

- ω(N) ≥ 7 para amigo de 10 (Teorema 1.2 de [P1]) — intacto.
- ω(N) ≥ 10 (Thackeray, arXiv:2310.15900) — intacto, e independente de [P1]–[P3].
- Teorema 1.10 de [P1] (Ω(N) ≥ 2ω(N)+6a−4) — **verdadeiro**; só a prova do lema
  auxiliar precisa da forma corrigida (E1). É inclusive ótimo (não melhorável pelo
  argumento).
- Teoremas 1, 2, 3 de arXiv:2404.05771 (limites para q₂, q₃, q₄) e Cor. 1.1 de [P3] —
  intactos.
- Não afirmamos que os enunciados (7), (8), Cor. 1.11 e o Teo. 1.2 de [P3] para r ≥ 6
  sejam **falsos**: como nenhum amigo de 10 é conhecido, enunciados condicionais desse
  tipo não podem ser refutados por contraexemplo. O que está provado aqui é que **as
  provas dadas não os estabelecem** (e, no caso de (7), que o argumento usado não pode
  estabelecê-los). A única falsidade demonstrada é a do Lema 2.3/23 (E1), que é um
  enunciado autocontido sobre partições.

## Busca de novidade (regra de rigor #4)

Feita em 2026-08-21: arXiv (listagem completa dos papers de Sagar Mandal e do grupo,
via API), busca web por errata/corrigenda para 2404.00624 e 2412.02701, e verificação
de que as versões atuais no arXiv (v5 de jan/2025 e v4 de out/2025, respectivamente)
ainda contêm os defeitos. **Nenhuma errata publicada encontrada.** O paper posterior
[P4] repete o Corolário 1.11 na forma original, o que indica que o defeito não foi
notado. Registrar nova busca imediatamente antes de qualquer submissão.
