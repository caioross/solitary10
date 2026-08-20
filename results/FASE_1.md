# Fase 1 — Fronteira computacional certificada

Aberta em 2026-08-20 após aprovação humana da Fase 0. Este arquivo é o relatório
corrente da fase; bloco a bloco, com checkpoint humano entre blocos.

---

## Bloco 1 — Motor de busca em árvore certificado (Alvo 1 da proposta da Fase 0)

### 1.1 O que foi construído

`core/motor.py` — busca em árvore sobre assinaturas de primos (pᵢ, aᵢ) de um
hipotético amigo N de 10, usando SOMENTE fatos rotulados:

- **Espaço de busca** (Teoremas A–D da Fase 0, `[PROVADO]`): N = ∏ pᵢ^{aᵢ} com
  5 = p₁ < p₂ < ⋯ < p_k, todo pᵢ ≥ 5, todo aᵢ par ≥ 2.
- **PODA-MIN**: se ∏_{escolhidos} I(p²) ≥ 9/5 e restam slots, todo completamento tem
  I > 9/5 (expoentes ≥ 2, I crescente no expoente, fator de primo extra > 1). Corta.
- **PODA-MAX**: I(N) < ∏ p/(p−1) (estrito, Lema 3 da Fase 0); majorando os primos
  restantes pelos menores disponíveis (monotonia: primo maior ⇒ p/(p−1) menor), se a
  majoração ≤ 9/5, corta. A majoração é não-crescente no próximo primo candidato, o
  que justifica encerrar o laço de candidatos quando ela cai a ≤ 9/5.
- **FECHO** (finitude dos expoentes num conjunto completo S): σ(p^a) =
  ∏_{d | a+1, d>1} Φ_d(p) divide σ(N) = 9N/5, cujos fatores primos estão em S ∪ {3};
  para d ímpar ≥ 3 e p ≥ 5, Zsygmondy (sem exceções nesse regime) dá primo primitivo
  q | Φ_d(p) com ord_q(p) = d, logo d | q−1 e d ≤ max(S)−1 (q = 3 é impossível para
  d ímpar ≥ 3, pois ord₃ ∈ {1,2}). Assim a+1 só pode ser um m ímpar cujo TODO divisor
  > 1 pertence a D(p,S) = {d ímpar ≤ max(S)−1 : fatores de Φ_d(p) ⊆ S∪{3}} — conjunto
  finito e computável. É a automação do "truque do 31" de Ward.
- **Honestidade estrutural**: ramo cuja iteração de primos não fecha por poda de
  índice (∏_{escolhidos} p/(p−1) ≥ 9/5) levanta `RamoNaoLimitado` — o motor se recusa
  a certificar em vez de terminar em falso.
- **Variante limitada** (`busca_limitada`): acrescenta o teto N ≤ B; como expoentes
  ≥ 2, ∏ primos ≤ √B (teto inteiro de produto), o que limita primos e expoentes e
  garante terminação sem fecho; toda assinatura sobrevivente é testada na igualdade
  exata 5σ(N) = 9N.

Testes: `tests/test_motor.py` (9 testes) e `tests/test_motor_crosscheck.py`
(4 testes, referências 100% independentes de sympy) — cross-check de σ/I; FECHO
contra força bruta (solidez E completude na faixa testada, inclusive sem sympy);
reprodução da estrutura de Ward; `RamoNaoLimitado` em ω = 6; **teste de completude
com alvo plantado** (monkeypatch do alvo para I(N₀), N₀ = (5·7·11)²: o motor DEVE
achar a assinatura de N₀ — e acha, exatamente uma vez); equivalência exata
shard-união vs varredura íntegra (1 e 2 níveis); contagem de enumeração de
expoentes contra força bruta independente; crivo próprio vs primerange/nextprime;
fatoração por divisão por tentativa de toda a superfície Φ_d(5) do certificado.

### 1.2 Resultado 1 — reprodução independente de Ward: ω(N) ≥ 6

`python experiments/elimina_omega.py --k-max 6`:

| ω | Desfecho | Detalhe |
|---|---|---|
| 1 | eliminado | {5} morto pelo FECHO (σ(5^a) exigiria 31, 11·71, 19531, … ∉ {5}) |
| 2–4 | eliminados na raiz | PODA-MAX: ∏ p/(p−1) dos menores primos ≤ 9/5 (para ω=4: 1001/576 < 9/5, a majoração de Ward) |
| 5 | eliminado | só sobrevivem {5,7,11,13,q}, q ∈ {17,19,23}; os três morrem pelo FECHO em p = 5 — nenhum expoente válido (o caso q = 23 é exatamente o que na prova manual de Ward exige o truque σ(5²) = 31) |
| 6 | **não certificado** | `RamoNaoLimitado` em [5,7,11,13,23]: ∏ p/(p−1) = 2093/1152 ≥ 9/5 — poda de índice não limita o 6º primo; exige propagação de divisibilidade (Bloco 2) |

> **Todo amigo de 10 tem ω(N) ≥ 6.**
> `[PROVADO-CONDICIONAL: Teoremas A–D e Lemas/Fato 0 da Fase 0 + Zsygmondy e
> identidade ciclotômica (clássicos) + correção do motor (§1.5) + correção de
> sympy nas chamadas consumidas (re-verificadas sem sympy em
> tests/test_motor_crosscheck.py)]` — reprodução independente de Ward 2008; < 0,1 s.

A fronteira honesta do método puro de índice fica documentada: ω = 6 é exatamente
onde a literatura (2404.00624) precisou das cadeias de divisibilidade.

### 1.3 Resultado 2 — cota certificada: nenhum amigo de 10 até 10³⁰

Moldura lógica (tudo exato em `experiments/cota_certificada.py`):

1. Amigo N ≤ B ⟹ ∏ primos de N ≤ √B (expoentes pares ≥ 2, `[PROVADO]`).
2. (∏ dos k menores primos ≥ 5)² > B ⟹ nenhum amigo N ≤ B tem ω ≥ k.
   Para B = 10³⁰: k_teto = 12, logo ω ∈ {10, 11} (usando ω ≥ 10 de arXiv:2310.15900).
3. `busca_limitada(k, B)` varre exaustivamente ω = k com N ≤ B (terminação por teto
   de produto; igualdade exata testada em cada assinatura).

Execução com o código final do bloco (B = 10³⁰): ω = 10 varrido em ~11 s —
712 341 nós, 393 158 conjuntos completos, **400 135 assinaturas testadas na
igualdade exata, zero amigos**; ω = 11 varrido em < 0,01 s (nenhum conjunto
sobrevive às podas).

*Nota de reprodutibilidade (regra 7; apontada pela passada adversarial):* uma versão
intermediária do motor, sem as podas de índice na folha, produziu para o mesmo B os
mesmos 712 341 nós mas 649 083 assinaturas testadas (superconjunto do espaço da
versão final; também zero amigos) — os revisores reproduziram exatamente os dois
comportamentos ligando/desligando as podas de folha. Os números desta seção são os
do código versionado neste commit. Portanto:

> **O menor amigo de 10, se existir, excede 10³⁰.**
> `[PROVADO-CONDICIONAL: Teoremas A–D + ω(N) ≥ 10 (arXiv:2310.15900) + correção do
> motor (seção 1.5)]`

Contexto: a literatura (conclusão de arXiv:2404.00624, citando OEIS A074902) alegava
"menor amigo > 10³⁰" **sem certificação publicada**. Este resultado certifica a
alegação — e o bloco tenta superá-la (B = 10³², seção 1.4).

### 1.4 Empurrando a fronteira: B = 10³¹ e B = 10³²

**B = 10³¹ certificado em peça única** (101,9 s com o código final; ω ∈ {10,11,12}
pela regra do produto): ω = 10 com 5 891 561 nós e 4 065 923 assinaturas testadas,
zero amigos; ω = 11 e 12 morrem nas podas. Mesmo rótulo condicional do 10³⁰.

Custo cresce ~10× por década de B (medido: 10,8 s → 107,9 s). Para B = 10³² a
varredura de ω = 10 foi **fragmentada por faixas do 2º primo** — partição explícita
{7}, {11–13}, {17–31}, {37–∞} (cobre [7, ∞); o teto de produto interno limita p₂ de
qualquer forma) — com shards em paralelo. Solidez da fragmentação: o filtro age só na
profundidade do 2º primo e as podas são monotônicas no candidato (independem do
filtro); teste `test_shards_por_p2_cobrem_exatamente_a_varredura_inteira` confirma
que a união dos shards testa EXATAMENTE as mesmas assinaturas da varredura íntegra
(nem falta, nem sobra) em B de teste.

**B = 10³² certificado por união de shards** (ω possível: {10, 11, 12}, pois
(∏ dos 13 menores primos ≥ 5)² > 10³²):

| Shard | Nós | Assinaturas testadas | Amigos |
|---|---:|---:|---:|
| ω=10, p₂=7, p₃=11 | 11 271 609 | 7 402 508 | 0 |
| ω=10, p₂=7, p₃=13 | 16 656 681 | 12 646 158 | 0 |
| ω=10, p₂=7, p₃=17 | 7 602 865 | 7 122 447 | 0 |
| ω=10, p₂=7, p₃∈[19,23] | 691 426 | 864 031 | 0 |
| ω=10, p₂=7, p₃≥29 | 2 | 0 (PODA-MAX na raiz do shard) | 0 |
| ω=10, p₂∈[11,13] | 5 602 546 | 6 475 561 | 0 |
| ω=10, p₂∈[17,31] | 1 | 0 (PODA-MAX) | 0 |
| ω=10, p₂≥37 | 1 | 0 (PODA-MAX) | 0 |
| ω=11 (íntegro) | 17 777 | 3 633 | 0 |
| ω=12 (íntegro) | 13 | 0 (podas) | 0 |
| **Total** | | **34 514 338** | **0** |

Cobertura da partição: p₂ > 5 ⟹ p₂ ≥ 7, e {7} ∪ [11,13] ∪ [17,31] ∪ [37,∞) cobre
[7,∞); dentro de p₂ = 7, p₃ > 7 ⟹ p₃ ≥ 11, e {11} ∪ {13} ∪ {17} ∪ [19,23] ∪ [29,∞)
cobre [11,∞). Os shards com 0 assinaturas morrem pela PODA-MAX por razão matemática
verificável (ex.: p₂ ≥ 17 ⟹ I < (5/4)(17/16)·∏ sup dos 8 menores primos > 17 < 9/5).

Reprodutibilidade (regra 5): cada linha da tabela foi produzida por
`python -u experiments/cota_certificada.py --log10-bound 32 --somente-k K
[--prefixo-intervalos ...]` com o código deste commit (os shards leves e ω = 11/12
foram re-executados após a rodada adversarial para garantir isso; números idênticos).
O script `experiments/shards_10e32.py` reproduz a partição INTEIRA sequencialmente e
verifica programaticamente a cobertura da partição antes de varrer (executado nesta
sessão: "particao de shards verificada"). Equivalência shard-união vs varredura
íntegra coberta por teste (`test_shards_por_p2_cobrem_exatamente_a_varredura_inteira`).

> **O menor amigo de 10, se existir, excede 10³².**
> `[PROVADO-CONDICIONAL: Teoremas A–D + ω(N) ≥ 10 (arXiv:2310.15900) + correção do
> motor (seção 1.5)]` — 100× além da alegação não certificada da OEIS (10³⁰).

Custo para ir além: ~10×/década em CPU (10³⁴ ≈ 3 h fragmentado; 10³⁶ ≈ 30 h). Antes
de gastar isso, vale portar o laço quente para inteiros puros/PyPy ou usar as podas
de congruência do Bloco 2 — decisão para o checkpoint humano.

### 1.5 Passada adversarial do motor

Cinco revisores independentes (workflow `fase1-adversarial-motor`), instruídos a
QUEBRAR as certificações — reconstruíram provas de monotonia, plantaram ~300 alvos
sintéticos, reimplementaram o fecho sem sympy e re-executaram os experimentos:

| Alvo | Veredicto | Síntese |
|---|---|---|
| Podas de índice + terminação dos laços | **SÓLIDA** | monotonia da majoração provada; estrito/não-estrito corretos em todos os pontos (inclusive folha); RamoNaoLimitado é exatamente a negação da terminação; 30 alvos toda-2 (caso de igualdade) todos achados |
| FECHO (Zsygmondy + ciclotômicos + filtro) | **SÓLIDA** | identidade σ(p^a) = ∏Φ_d(p) verificada; sem exceções de Zsygmondy no regime; q = 3 nunca é primitivo (ord₃ ∈ {1,2}); 134 casos (p,S) contra força bruta: igualdade exata; fecho re-verificado à mão nos 3 conjuntos de Ward |
| Completude da enumeração | LACUNA_MENOR (só processo) | ~260 alvos plantados todos achados exatamente 1×, incluindo bordas (N = bound, primo na borda da lista, expoentes altos, shards); nenhum ramo vivo cortado |
| Moldura lógica dos certificados | LACUNA_MENOR (só processo) | enumeração k = 5 conferida SEM o motor (força bruta + monotonia); k_maximo exato; rótulos precisavam declarar Zsygmondy/Lemas/sympy — **corrigido** |
| Dependências ocultas (sympy, caches, floats) | LACUNA_MENOR (só processo) | replay instrumentado dos dois certificados com wrappers verificadores: TODAS as chamadas a sympy consumidas pelos certificados re-verificadas por implementações próprias (crivo, Miller–Rabin, Pollard-rho, ciclotômico via Möbius) — nenhum valor errado; zero floats em caminho decisório; caches seguros |

**Nenhum problema matemático encontrado.** Problemas de processo apontados e
corrigidos neste mesmo bloco:

1. *Estatísticas de §1.3 geradas por versão anterior do motor* → seção regenerada
   com o código final; divergência registrada (regra 7).
2. *Fase 1 sem commit / shards de 10³² sem script versionado* → commit deste bloco;
   partição reproduzível em `experiments/shards_10e32.py`, com verificação
   programática de cobertura da partição (ω ∈ {10,11,12}; p₂ particiona [7,∞);
   p₃|p₂=7 particiona [11,∞)); shards leves re-executados com o código final.
3. *Hipótese tácita de correção do sympy* → declarada nos rótulos; superfície de
   fatoração do certificado ω ≥ 6 (Φ_d(5), d ímpar ≤ 21) re-fatorada por divisão
   por tentativa pura em `tests/test_motor_crosscheck.py`; crivo próprio vs
   primerange/nextprime; identidades ciclotômica e telescópica.
4. *Falha de modo comum no teste do fecho* (referência usava o mesmo factorint) →
   `test_fecho_dos_tres_conjuntos_de_ward_sem_sympy` re-deriva o abate dos 3
   conjuntos com fatoração 100% própria.
5. *`test_lema3` da Fase 0 com custo de minutos* (divisão por tentativa até p¹²) →
   referência trocada por soma direta de potências (divisores de p^e são p⁰..p^e
   por fatoração única) — independência mantida, custo trivial.
6. Cosméticos: docstring de `elimina_omega.py` (k = 1 morre por fecho, não por
   índice; e só {5,7,11,13,23} exige o fecho — nos outros dois a poda-min de folha
   bastaria), import morto, assert → raise, mensagem de exceção em ASCII (evita
   UnicodeEncodeError em console cp1252), condição ω ≥ 10 embutida na frase do
   certificado.

Com isso, os rótulos das seções 1.2–1.4 valem com a passada adversarial concluída.

### 1.6 Próximos passos do bloco / da fase

- Bloco 2: propagação de divisibilidade (Teoremas 1.3/1.7 e Lema 2.1 de 2404.00624,
  Remark 3.1 — "cadeias") para fechar ω = 6 e ω = 7 automaticamente; depois o método
  de Thackeray (Cor. 6/7 + primos especiais) rumo a ω ≥ 11 (Alvo 2).
- Colheita de corolários (Alvo 3) em paralelo quando barato.
