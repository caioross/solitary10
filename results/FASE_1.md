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

Cinco revisores independentes, instruídos a
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

---

## Bloco 2 — Cadeias de divisibilidade: ω(N) ≥ 7 (aprovado pelo usuário)

### 2.1 Ferramentas novas (`core/cadeias.py`)

Base matemática rotulada no cabeçalho do módulo. Peças, todas exatas e testadas
(`tests/test_cadeias.py`, 8 testes):

- **Fórmula de valuação** (Lema 2.1 de arXiv:2404.00624 = Nielsen/Voight, via LTE):
  v_q(σ(p^a)) por ordens multiplicativas, sem fatorar nada; testada exaustivamente
  contra a valuação direta (p, q ≤ 37, a ≤ 20).
- **f_p^q** (Teo. 1.3 de 2404.00624): reproduz as 12 amostras da Tabela 4 do paper
  registradas na nota de leitura (f_31^5 = 3, f_11^5 = 5, …, f_35671^5 = 29).
- **Fecho por ordens** (`expoentes_validos_ordens`): substitui o fecho ciclotômico do
  Bloco 1 — os divisores d > 1 de a+1 são ordens ord_r(p) de primos r ∈ S (Zsygmondy),
  e o teste de fecho é por RECONSTRUÇÃO: σ(p^a) == ∏ q^{v_q(σ(p^a))} (fórmula de
  valuação), sem fatoração. Equivalência com a implementação ciclotômica do Bloco 1
  verificada caso a caso (dois métodos independentes).
- **Orçamentos da equação-mestra**: ∏σ(pᵢ^{aᵢ}) = 9·5^{a₁−1}·∏pᵢ^{aᵢ} dá, exatamente:
  Σ_{p≡1(3)} v₃(aᵢ+1) = 2 e Σ_{q≡1(5)} v₅(a_q+1) = a₁ − 1 (Fato 2: só ordem 1
  contribui módulo 3 e 5, pois as demais ordens são pares).

### 2.2 O certificador de ω = 6 (`core/omega6.py`)

Estágio A: enumeração de prefixos C5 (DFS de índice; terminação porque nos níveis
1–4 o limite do laço é ∏ p/(p−1) de ≤ 4 primos ≤ 1001/576 < 9/5). Estágio B:

- **Ramo (i)** (∏sup(C5) < 9/5): p₆ limitado pelo índice; cada conjunto completo cai
  na fase de expoentes (fecho por ordens + orçamentos + igualdade exata).
- **Ramo (ii)** (∏sup(C5) ≥ 9/5; p₆ não limitado por índice): **pinagem pela
  alimentação do 5**: a₁ ≥ 2 ⟹ v₅(σ(N)) = a₁ − 1 ≥ 1 ⟹ o 5 tem alimentador, e só
  bases ≡ 1 (mod 5) alimentam. Caso um q ∈ C5 alimenta: 5 | a_q+1 e 5 ∉ D_q ⟹
  ord_P(q) = 5 ⟹ P | Φ₅(q) — P pinado nos fatores novos (finitos). Caso só P
  alimenta: P ≡ 1 (mod 10), v₅(a_P+1) limitado pelo conjunto E finito (divisores de
  a_P+1 dividem q−1 para q ∈ C5∪{3}) ⟹ a₁ percorre conjunto finito e σ(5^{a₁})
  pina P pelo resto do strip por C5∪{3}. Todo P pinado > p₅ vira conjunto completo
  (mesma fase exaustiva do ramo i). Lacunas de cobertura detectáveis levantam
  `NaoCertificavel` (falha honesta, sem certificado).

No espaço real, **três** prefixos têm ∏sup ≥ 9/5 — {5,7,11,13,17} (17017/9216),
{5,7,11,13,19} (19019/10368) e {5,7,11,13,23} (2093/1152) — mas os dois primeiros
morrem antes, pela poda-min (∏I(p²) = 1,8238 e 1,8120, ambos ≥ 9/5). Só
{5,7,11,13,23} chega à pinagem — o mesmo prefixo que causou `RamoNaoLimitado` no
Bloco 1. (Verificado: não há dependência de ordem — os três prefixos, se pinados,
dariam os mesmos P ∈ {31, 3221}.) A pinagem mecânica dá P ∈ {3221, 31}, e os
dois conjuntos completos morrem no fecho. É a automação exata do estilo de argumento
das "cadeias" de 2404.00624.

**Derivação conferida à mão** (independente do código, aritmética inteira):
- *Caso A*: o único q ∈ C5 com q ≡ 1 (mod 5) é 11; e 5 ∉ D₁₁, onde D₁₁ é calculado
  **apenas sobre os primos CONHECIDOS** — nenhum r ∈ C5∪{3} tem ord_r(11) = 5, pois
  isso exigiria 5 | r−1. (A restrição a C5∪{3} é essencial: P = 3221 ≡ 1 (mod 5) e
  ord_P(11) = 5 é justamente a *conclusão* do argumento, não uma hipótese.) Logo
  P | Φ₅(11) = σ(11⁴) = 16105 = 5 · **3221**, com 3221 primo (divisão por tentativa
  até 56). Pin: 3221.
- *Caso B*: divisores ímpares admissíveis de a_P+1 (dividem q−1 para q ∈ C5∪{3}) =
  {3, 5, 11} ⟹ E = {3,5,11} ⟹ v₅(a_P+1) ≤ 1 ⟹ a₁ = 2 ⟹ σ(5²) = **31**, que não
  está em C5∪{3}. Pin: 31.

> **Cross-validação com a literatura:** a Tabela 4 de arXiv:2404.00624 (construída à
> mão pelos autores) registra **f_3221^11 = 5** — exatamente o pin que o procedimento
> mecânico deste bloco deriva sozinho, sem consultar a tabela. O certificador
> redescobre a cadeia que os autores exibiram manualmente.

**Nota de projeto (honestidade):** a primeira versão do ramo (ii) usava "escadas" de
expoentes com kills de janela; o desenho tinha um caso de *straddle* real (no eixo
do 7 em {5,7,11,13,23}, ∏sup fica a 1,5·10⁻⁵ de 9/5 e nenhum kill dispara) e foi
substituído pela pinagem — registrado em FRACASSOS.md.

### 2.3 Bugs de solidez pegos pelos testes de alvo plantado

Dois bugs de borda de igualdade — ambos na direção CATASTRÓFICA (certificariam em
falso a ausência de um amigo) — foram pegos pelos testes de completude com alvo
plantado antes de qualquer execução real, e corrigidos:

1. Admissão de p₆ no ramo (i) usava `<` onde igualdade exata (assinatura toda-mínima
   com I == alvo) é candidato vivo — corrigido para `<=`.
2. Na folha da fase de expoentes, a PODA-MAX degenerava em `prod_I ≤ ALVO` (produto
   vazio de sups) e matava a igualdade exata — folha movida para antes das podas.

Os testes plantados (assinaturas de 6 primos com expoentes 2 e 4, inclusive no 5)
agora passam: o certificador ACHA cada assinatura plantada exatamente.

### 2.4 Resultado

`python experiments/elimina_omega6.py` (código deste commit):

```
prefixos C5: 19 (ramo i: 16, ramo ii: 1, mortos por poda-min: 2)
conjuntos completos: 2745; folhas alcancadas na fase de expoentes: 0
pins de P testados no ramo ii: [31, 3221]
tempo: 0.1s
```

(O contador de folhas ser 0 implica **zero testes de igualdade executados**: o
`rec` da fase de expoentes nunca chega a uma folha, porque em cada um dos 2 745
conjuntos algum primo já fica sem expoente válido.)

Todos os 2 745 conjuntos completos (incluindo a cadeia longa {5,7,11,13,29,p₆} com
p₆ até 20 731 (2 312 conjuntos), análoga à "cadeia 13" da literatura) morrem no fecho de ordens —
algum primo fica sem expoente válido — sem que NENHUMA igualdade precise ser
testada. O único prefixo do ramo (ii) é {5,7,11,13,23} (o mesmo `RamoNaoLimitado`
do Bloco 1), fechado por pinagem com P ∈ {31, 3221}.

> **Resultado H: todo amigo de 10 tem ω(N) ≥ 7.**
> `[PROVADO-CONDICIONAL: Teoremas A–D e Lemas/Fato 0 da Fase 0 + Zsygmondy e
> fórmula de valuação de Nielsen/Voight (clássicos; fórmula re-testada
> exaustivamente contra valuação direta) + correção de core/omega6.py e
> core/cadeias.py (passada adversarial em §2.5) + correção de
> sympy.n_order/factorint/nextprime nas chamadas consumidas]`
> Reprodução independente e mecânica do Teorema 1.2 de arXiv:2404.00624
> (prova manual de 19 cadeias) — em 0,1 s.

### 2.5 Passada adversarial do Bloco 2

Cinco revisores independentes (workflow `fase1-adversarial-bloco2`), instruídos a
QUEBRAR a certificação ω = 6. Três concluíram nesta rodada (dois caíram por limite de
sessão e foram relançados):

| Alvo | Veredicto | Síntese |
|---|---|---|
| Pinagem do ramo (ii) | **SÓLIDA** | replay instrumentado: **todas** as 18 102 chamadas de `v_q_sigma`, 3 017 de `sigma_fecha_em`, 35 222 de `ordem_mod`, 2 924 de `nextprime` e 2 747 de `factorint` consumidas pelo certificado re-verificadas contra implementações próprias — **0 erros**; re-enumeração independente dos prefixos (17 vivos; os 19 do código são superconjunto exato, com 2 mortos por poda-min válida); cobertura dos conjuntos completos: 2 743 esperados vs 2 743 processados, faltando 0 / sobrando 0; morte dos 2 745 re-verificada com código 100% próprio (0 vivos); pinagem inteira reimplementada e varrida sobre 1 001 prefixos sintéticos — 0 divergências |
| Cobertura do Estágio A + ramo (i) | LACUNA_MENOR | 441 alvos plantados próprios, **todos achados exatamente 1×**; campanha de **mutação dirigida** com 12 mutantes na direção perigosa, todos detectados (perdendo de 26 a 136 dos 136 alvos). Fecho re-derivado do zero (sem D, sem fórmula de valuação, sem sympy): 0 sobreviventes. **Um defeito sério** (corrigido, abaixo) |
| Dependências e execução real | LACUNA_MENOR | pins conferidos dígito a dígito; fecho reimplementado de forma *estritamente mais permissiva* → 0 sobreviventes em 2 745; distribuição do matador: o primo 5 mata 2 669 conjuntos, o 7 mata 74, o 19 e o 13 um cada. **Rótulo desonesto** (corrigido, abaixo) |
| Fórmula de valuação e fecho | LACUNA_MENOR | fórmula re-derivada por LTE e verificada exaustivamente para todos p,q < 220 e a = 1..45 **inclusive a ímpar** (0 divergências); os 4 elos da prova (prefixos, p₆, pinagem, morte dos 2 745) re-verificados por caminhos independentes; kills re-checados por fatoração inteira direta (2 855 candidatos m, maior m = 9 689, **zero kills falsos**) e por força bruta a = 2..160 |
| Completude por plantios | LACUNA_MENOR | 72 assinaturas plantadas achadas (incl. o caso-borda I(N) == ALVO exato); **3 mutantes cegos descobertos** (corrigidos, abaixo) |

**Correções aplicadas neste bloco em resposta:**

1. **[SÉRIO] Faltava o raise de terminação em `_prefixos_c5`.** O laço de candidatos
   só termina se ∏ p/(p−1) < 9/5 **estritamente**; se um nó tivesse ∏sup ≥ 9/5 o laço
   rodaria **para sempre, sem exceção e sem diagnóstico** — falha por travamento, não
   pela recusa honesta que o módulo promete. Não afeta o certificado atual (o máximo
   de ∏sup em qualquer nó de nível ≤ 4 é 1001/576 < 9/5, verificado), mas era **mina
   para o Bloco 3**: no nível 5 o máximo já é 17017/9216 ≥ 9/5, ou seja, reaproveitar
   este DFS para ω = 7 travaria silenciosamente **no alvo real**. Corrigido com raise
   `NaoCertificavel` + teste `test_prefixos_c5_recusa_em_vez_de_travar` (que, sem a
   correção, não terminaria).
2. **Rótulo do experimento declarava dependências erradas**: citava `isprime` e
   `integer_nthroot` (não usados em lugar nenhum) e **omitia `factorint`**, que é
   load-bearing — é ele que produz os dois pins que fecham o ramo (ii), o único ramo
   de espaço infinito. Rótulo corrigido.
3. **As duas guardas de honestidade não tinham teste algum** (mutação: removê-las
   sobrevivia à suíte inteira e o experimento seguia imprimindo CERTIFICADO).
   Adicionados `test_guarda_caso_a_pin_indisponivel` (C5 = {5,7,11,13,31}, onde
   ord₁₁(31) = 5) e `test_guarda_caso_b_sem_pin` (C5 = {5,7,13,17,31}, onde
   σ(5²) = 31 ∈ C5).
4. **Afirmação factualmente errada na minha primeira redação**: eu escrevera que os
   dois conjuntos do ramo (ii) morrem porque "13 fica sem ordem ímpar" — falso. O 13
   **tem** ordem ímpar (ord₂₃(13) = 11) e m = 11 é candidato legítimo, morto só na
   reconstrução. **Quem mata os dois conjuntos é o primo 7**; e o 5 ainda tem expoente
   válido em {5,7,11,13,23,31}. Corrigido no texto e fixado em
   `test_quem_mata_os_conjuntos_do_ramo_ii`.
5. Contadores honestos: `prefixos_mortos_min` (a saída antes não fechava:
   16 + 1 ≠ 19) e `assinaturas_ramo_i` → `assinaturas_testadas` (o contador serve os
   dois ramos e conta folhas alcançadas, não testes de igualdade executados).
6. Fragmentos de docstring truncados em `omega6.py` e o número exato do maior p₆
   ({5,7,11,13,29}: p₆ ≤ **20 731**, 2 312 conjuntos) corrigidos.

7. **[SÉRIO] Três mutantes catastróficos sobreviviam à suíte inteira** — descobertos
   pela lane de plantios. O pior: fazer o orçamento v₅ **esquecer a contribuição do
   sexto primo** passava nos 78 testes e o experimento seguia imprimindo CERTIFICADO,
   mas **perdia um amigo genuíno** (demonstrado com o alvo I({5²,7²,11²,13²,17²,31⁴}),
   onde 31 ≡ 1 mod 5 é o único alimentador do 5). Os outros dois: descartar o último
   expoente de cada lista (invisível porque em toda a execução real existe **uma única**
   lista com 2 entradas — (5, {5,7,11,13,31,71}) → [2,4]) e truncar as ordens grandes
   (a execução real usa candidatos até m ≈ 10⁴). Os três agora morrem em testes
   dedicados — verificado re-aplicando cada mutação: as 3 falham, uma por teste.
8. **Retratação honesta:** a frase original desta seção — "os 6 na direção perigosa
   foram todos detectados — o arnês tem dentes" — era **verdadeira só para os
   mutantes daquela lane**. A lane de plantios exibiu 3 mutantes perigosos que
   passavam. A frase foi corrigida e os buracos, fechados.
9. Endurecimento sugerido pela revisão e aplicado: `ALVO / prod_sup > 1` →
   `ALVO > prod_sup` (o empate agora vai comprovadamente para o ramo (ii); sob a
   mutação oposta o laço de p₆ nunca terminaria); `v_q_sigma` recusa q = 2
   explicitamente (a fórmula LTE só vale para q ímpar, e um alvo plantado com
   numerador par colocaria 2 em `extras`); guarda de tamanho antes de fatorar o
   resto do strip (fatoração ilimitada seria travamento, não falha honesta);
   `_candidatos_m` passa a enumerar divisores em O(√m) no lugar de varrer todos os
   ímpares até m — parede de desempenho identificada para ω ≥ 7.

**Segunda perna independente para o ramo (ii)** (achado da revisão, registrado como
dado): para **todos os 216 807 primos P ∈ (23, 3·10⁶]**, o conjunto {5,7,11,13,23,P}
morre no fecho de ordens **sem usar a pinagem**. Além disso, estruturalmente,
D(7) = ∅ nesse prefixo, o que força a₇+1 a ser primo ímpar e restringe fortemente P
para qualquer tamanho. Isso dá ao ramo (ii) uma verificação independente até 3·10⁶,
restando à pinagem a responsabilidade por P > 3·10⁶. Registre-se também que a
pinagem **não é redundante**: em P = 2801 o primo 7 tem expoente válido ([4]), isto
é, o "matador 7" falha e o conjunto só cai por outro primo.

**Limitação registrada (não corrigida):** o ramo (ii) é estruturalmente **intestável
por alvo plantado** — `_ramo_ii_pinagem` levanta `NaoCertificavel` para qualquer alvo
≠ 9/5, então o arnês que pegou os dois bugs de borda anteriores é cego ali. A
completude do ramo repousa sobre a derivação manual (§2.2), a re-implementação
independente feita pela revisão (1 001 prefixos, 0 divergências) e os testes de saída
congelada. A cláusula `P > p₅` também é código morto na execução real (ambos os pins
são > 23) — **não presumir que foi validada por uso** num futuro ω = 7.

---

## Bloco 3 — Certificador recursivo e cota universal para a₁ (aprovado: "continue")

### 3.1 A ideia: um certificador para qualquer ω, com honestidade em cada nó

`core/omega_k.py` substitui o desenho "Estágio A + dois ramos" do Bloco 2 por uma
recursão uniforme sobre estados (C, s, lo): C = primos já conhecidos (contém 5),
s = quantos primos ainda são desconhecidos, lo = cota inferior dos desconhecidos
(invariante: todo primo de S que seja ≤ lo está em C). Em cada nó:

- **morto** se s ≥ 1 e ∏_{C} I(p²) ≥ 9/5 (os s fatores restantes são > 1);
- **s = 0**: conjunto completo → a mesma fase de expoentes do Bloco 2
  (`omega6._conjunto_completo`: fecho por ordens + orçamentos v₃/v₅ + igualdade);
- **ramo (i)** se ∏_{C} p/(p−1) < 9/5: o menor desconhecido U é limitado pelo índice
  (majoração não-crescente em U com limite ∏sup(C) < 9/5 — o laço termina, sem raise
  necessário: a condição de entrada É a condição de terminação); recorre com lo = U;
- **ramo (ii)** senão: pinagem (abaixo) e recursão com s reduzido.

A armadilha mapeada no Bloco 2 (o DFS de prefixos travaria no nível 5, onde
∏sup{5,7,11,13,17} = 17017/9216 ≥ 9/5) desaparece por construção: um nó com
∏sup ≥ 9/5 nunca entra no laço de índice — vai para a pinagem.

### 3.2 A peça nova: cota universal para a₁ = v₅(N)

v₅(σ(N)) = a₁ − 1 = Σ_{alimentadores U} v₅(a_U + 1), e só bases ≡ 1 (mod 5) alimentam
(Fato 2). Para um alimentador U com k = v₅(a_U+1): para cada j = 1..k, Φ_{5^j}(U)
divide σ(N) e tem primo primitivo r_j com ord_{r_j}(U) = 5^j (Zsygmondy, sem exceções
para U ≥ 5 e 5^j ímpar ≥ 5), logo r_j ≡ 1 (mod 5^j), r_j ∉ {3, U}, e os r_j são
**distintos** (ordens distintas). Portanto k ≤ #{r ∈ S∖{U} : r ≡ 1 (mod 5)} ≤
c₅ + s − 1, com c₅ = #{q ∈ C : q ≡ 1 (mod 5)}. Com no máximo c₅ + s alimentadores:

> **a₁ ≤ 1 + (c₅ + s)·(c₅ + s − 1)** — finita para qualquer número de slots.

Enumera-se a₁ par nessa faixa; σ(5^{a₁}) tem de fatorar em S ∪ {3}, então os fatores
primos do resto do strip por C ∪ {3} são desconhecidos: mais que s, ou algum ≤ lo
(estaria em C pelo invariante) ⟹ caso morto; senão **todos ficam pinados**. Se o resto
é 1, o 5 ainda precisa de alimentador: para cada q ∈ C com q ≡ 1 (mod 5), o caso "q
alimenta" pina via Φ₅(q) (se 5 ∉ D_q(C)); o caso "só desconhecidos alimentam" é
fechado quando é impossível (s = 1 e C sem os primos ≡ 1 (mod 5^j) exigidos) e,
caso contrário, levanta `NaoCertificavel`. Nenhuma lacuna é silenciosa.

### 3.3 Cross-check com os Blocos 1–2

Para k ≤ 6 o recursivo reproduz as certificações anteriores, com uma diferença
**explicável e mais apertada**: para k = 6 testa 2 744 conjuntos completos (o Bloco 2
testou 2 745) e pina só {31}. A cota universal dá, em {5,7,11,13,23} com s = 1,
a₁ ≤ 1 + 2·1 = 3 ⟹ **a₁ = 2 forçado** ⟹ σ(25) = 31 ocupa o único slot; o caso
"11 alimenta ⟹ 3221" do Bloco 2 exigiria um segundo slot e é subsumido. Ambas as
coberturas são completas; o Bloco 2 testou um conjunto redundante. Para k ≤ 5 o índice
mata na folha o que o Bloco 1 matava pelo fecho (mesmo veredito). Testes em
`tests/test_omega_k.py` (consistência k ≤ 6, cota de a₁ com dois slots, guarda de alvo,
plantios de 7 primos no regime do ramo (i)).

### 3.4 O que mais entrou no bloco (três iterações honestas)

A primeira versão do certificador (índice primeiro, pinagem só onde o índice falha)
**explodia em k = 7**: no prefixo {5,7,11,13,29} com 2 slots, U vai a ~41 500 pelo
índice e, para cada U > 20 744, p₇ sobe a centenas de milhares (∏sup a 10⁻⁶ de 9/5)
— milhões de conjuntos de 7 primos, todos mortos no fecho, tarde demais (> 590 s).
A resposta foi matemática: a pinagem é uma partição completa **em qualquer nó**, e
"a₁ = 2 ⟹ 31 ∈ S, 31 ≤ lo" mata toda a cadeia instantaneamente. Com **partição
primeiro** (índice como fallback), k = 6 cai de 2 745 conjuntos para 27.

As três iterações seguintes, cada uma disparada por um estado residual concreto de
k = 7:

1. **a₁ comprometido**: um ramo vindo de a₁ = 4 re-enumerava a₁ = 2 mais fundo —
   sub-caso impossível no ramo. O a₁ escolhido numa partição é propagado.
2. **Orçamento do 3** (v₃(σ(N)) = 2 exato; residual {5,7,11,13,31,71}+P): mesma
   estrutura de Zsygmondy, total fixo; e a correção de uma fraqueza minha —
   quando a testemunha primitiva de Φ_{ℓʲ}(q) é conhecida eu não pinava nada, mas
   os **demais** fatores novos de Φ_{ℓʲ}(q) continuam obrigados a estar em S
   (Φ₅(31) = 5·11·17351 pina 17351 mesmo com 11 conhecido).
3. **Produto de casos + viabilidade injetiva** (residual {5,7,11,13,31,181}+P):
   com um único desconhecido, todo divisor d > 1 de a_P+1 é a ordem de um primo
   primitivo r_d ∈ C com d | r_d − 1, e divisores distintos têm testemunhas
   **distintas** — um emparelhamento. 45 | a_P+1 exigiria testemunhas para 9 e 45,
   e só 181 serve às duas. O caso morre.

### 3.5 Resultado para ω = 7: NÃO certificado — fronteira caracterizada

`python experiments/elimina_omega_k.py --k-max 7` (saída verbatim, linhas de pins
omitidas):

```
omega = 1: nos=1 mortos_min=0 ramo_i=0 particoes=0 conjuntos_completos=1 folhas=0 amigos=0 tempo=0.0s
omega = 2: nos=1 mortos_min=0 ramo_i=0 particoes=1 conjuntos_completos=0 folhas=0 amigos=0 tempo=0.0s
omega = 3: nos=3 mortos_min=0 ramo_i=0 particoes=2 conjuntos_completos=1 folhas=0 amigos=0 tempo=0.0s
omega = 4: nos=4 mortos_min=0 ramo_i=3 particoes=4 conjuntos_completos=0 folhas=0 amigos=0 tempo=0.0s
omega = 5: nos=7 mortos_min=0 ramo_i=6 particoes=7 conjuntos_completos=0 folhas=0 amigos=0 tempo=0.5s
omega = 6: nos=57 mortos_min=0 ramo_i=25 particoes=30 conjuntos_completos=27 folhas=0 amigos=0 tempo=1.6s
omega = 7: NAO CERTIFICADO apos 0.1s
   estado residual: C=[5, 7, 11, 13, 31, 331], s=1: casos abertos ['a1=2:k5=1,k3=1']
```

Caracterização exata do residual (aritmética registrada em `tests/test_omega_k.py`):
- C = {5,7,11,13,31,331}, um desconhecido P > 331; a₁ = 2 (ramo); 331 veio de
  Φ₃(31) = 3·331 ("31 alimenta o 3").
- Único caso aberto: P alimenta o 5 (k₅ = 1) **e** carrega um dos dois 3's (k₃ = 1);
  o outro 3 vem do 31. Logo 15 | a_P + 1, e 331 ≡ 1 (mod 15) é testemunha legítima.
- Os m = a_P + 1 viáveis (injeção de testemunhas em C) são **{3, 5, 11, 15}** ⟹
  **a_P = 14 forçado**.
- **13 não tem alimentador possível em C** (nenhum ord₁₃(q) ímpar) ⟹ só P alimenta
  o 13; ord₁₃(P) = 1 exigiria 13 | 15 ⟹ ord₁₃(P) = 3 ⟹ P ≡ 3 ou 9 (mod 13).
- ∏sup(C) = 1,8012 ≥ 9/5: o índice não limita P. ∏I(q²) = 1,7794.

O que falta para fechar: v_P(N) = a_P = 14 tem de ser inteiramente fornecido pelos
σ(q^{a_q}), q ∈ C (P ∤ a_q+1, pois um divisor P de a_q+1 exigiria testemunha ≡ 1
(mod P) em S, impossível) — ou seja, Σ_{q∈C} v_P(q^{ord_P(q)} − 1) ≥ 14 com apenas
6 termos: exige **v_P(q^{ord_P(q)} − 1) ≥ 3 para algum q** ("par de Wieferich de
ordem alta" com P > 331). É exatamente o terreno do Corolário 6 / Proposição 9 de
Thackeray (arXiv:2310.15900): contabilidade de v_r com cotas verificadas por
computador para primos especiais. **Bloco 4 candidato:** orçamento de v_P para o
desconhecido, com a cota (k−1)² + c de Thackeray re-derivada.

**Rótulos:** nenhum enunciado novo. ω(N) ≥ 7 (Resultado H) fica **duplamente
certificado** — pelo certificador do Bloco 2 (2 745 conjuntos; passada adversarial
§2.5) e, de forma independente e muito mais curta, pelo recursivo deste bloco
(27 conjuntos; ainda **sem** passada adversarial própria — não é load-bearing
enquanto não passar por ela). ω = 7 permanece aberto para este método.

---

## Bloco 4 — Além da parede de ω = 7: aperto, valuações diretas, caudas (aprovado: "continue")

Objetivo aprovado: empurrar o certificador recursivo para além do estado residual
{5,7,11,13,31,331}+P do Bloco 3. O bloco terminou com **ω = 7 e ω = 8 certificados**
pelo recursivo (ω(N) ≥ 9), quatro peças novas no método e uma lição de método
registrada em FRACASSOS.md. Tudo abaixo é aritmética exata (`Fraction`/`int`); os
decimais no texto são só leitura humana dos racionais.

### 4.1 Diagnóstico: a parede do Bloco 3 era um defeito de aperto, não de teoria

O relatório do Bloco 3 (§3.5) pedia "contabilidade de v_P" para fechar o residual.
Estava errado. O a₁ = 2 escolhido pela partição era **compromisso do ramo** mas não
entrava nas cotas de índice: prod_sup usava 5/4 no lugar de I(5²) = 31/25. Com o
compromisso exato,

  ∏sup{5,7,11,13,31,331} = (31/25)(7/6)(11/10)(13/12)(31/30)(331/330) = 1,7868 < 9/5

(era 1,8012 com 5/4), e o índice limita P: o nó cai no fallback e fecha. O mesmo
aperto vale em qualquer nó (I(p^{a_p}) exato para todo primo comprometido, nas duas
cotas) e, em conjuntos completos, permite matar de graça antes da fase de
expoentes: prod_min > 9/5, ou prod_sup ≤ 9/5 com algum expoente livre (I(N) < prod_sup
estrito), ou prod_sup < 9/5 com todos fixos. Em k = 6 os 22 conjuntos completos
morrem todos aí (`completos_mortos_indice = 22`, 51 nós, 0 folhas).

Lição (FRACASSOS.md, desfecho da entrada do Bloco 3): antes de pedir teoria nova,
verificar se toda informação já comprometida no ramo entra em TODAS as podas.

### 4.2 Segundo obstáculo: expoentes gigantes materializados

Com a parede removida, k = 7 travava (> 560 s, sem progresso) no conjunto completo
{5, 11, 31, 71, 181, 1741, 167140584971}. Diagnóstico por dump de pilha
(`faulthandler`): `cadeias.sigma_fecha_em` calculando `p**(a+1)`. Causa: 167140584971
− 1 = 2·5·16714058497 com o cofator **primo**, logo ord_r(p) ∈ {16714058497,
83570292485, …} para os demais p, e m = ord_r(p) é candidato legítimo a a_p + 1 no
fecho por ordens (todos os seus divisores > 1 são {m} ⊆ D). A reconstrução
tentava σ(5^{16714058496}) — 3,9·10¹⁰ bits.

Correção em `core/cadeias.py`, semântica idêntica, só o cálculo muda:

- **Valuações diretas.** v_q(σ(p^a)) = v_q(p^{a+1} − 1) − v_q(p − 1), com
  v_q(p^{n} − 1) por exponenciação modular (p^n mod q^j para j = 1, 2, …). Vale para
  TODO primo q ≠ p (inclusive q = 2) e não precisa de ord_q(p) — logo não precisa
  fatorar q − 1. `v_q_sigma` (fórmula de Nielsen/Voight por ordens) continua no
  módulo e nos testes; `_v_q_de_p_ordem_menos_1` também passou a modular.
- **Gate de tamanho exato.** O produto P = ∏ q^{v_q(σ(p^a))} sempre divide σ(p^a).
  Se bl(P) ≤ a·(bl(p) − 1) (bl = comprimento em bits) então
  P < 2^{bl(P)} ≤ 2^{a(bl(p)−1)} ≤ p^a < σ(p^a), e a resposta é False sem
  materializar p^{a+1}. Onde a potência é calculável a resposta é a mesma
  (`test_gate_de_tamanho_e_so_atalho`).
- Divisores ímpares de m por fatoração (`sympy.divisors`, m divide um q − 1 já
  fatorado por `n_order`) no lugar da divisão por tentativa até √m.

O conjunto que travava resolve em 0,00 s: expoentes válidos 5 → [2, 4, 14],
11 → [] (morto). Testes novos em `tests/test_cadeias.py`: valuação direta contra
força bruta (exaustivo, q = 2 incluído), modular contra potência inteira, o
conjunto real acima em < 5 s, divisores contra força bruta.

### 4.3 Primos grandes sem fatorar r − 1 (implementado e testado; ainda não acionado)

Pins como Φ₅(q) passam de 100 bits, e r − 1 pode não ser fatorável — o que torna
ord_r(p) inacessível justamente onde o fecho por ordens precisa dele. Lema
implementado em `omega_k._expoentes_com_primo_grande` (cabeçalho de
`core/omega_k.py`, "PRIMOS GRANDES"): num conjunto completo S = S′ ∪ {r} com r
grande ((r−1) com mais de `ORDEM_BITS` = 80 bits), para p ∈ S′ todo divisor d > 1 de
a_p + 1 é ord_{r′}(p) com testemunhas distintas para divisores distintos, e r
testemunha no máximo UM divisor, o = ord_r(p). Com D′ = ordens de p módulo S′∖{p}
(computáveis), os casos são exaustivos: (A) todos os divisores em D′; (B2) a_p + 1 ∈
D′ com exatamente um divisor d* fora de D′ e ord_r(p) = d* (teste modular);
(B1) a_p + 1 = o ∉ D′ com todos os divisores próprios em D′ — o composto ⟹ o = ℓ·e
com ℓ primo ∈ D′, e ∈ D′ (finito); o = ℓ primo ⟹ Φ_ℓ(p) = ℓ^ε·r^v (o único fator
primitivo possível é r; o não-primitivo só ℓ, ε ≤ 1 por LTE), com
v ≤ v_r(σ(N)) = a_r ≤ A_r, onde A_r vem dos expoentes válidos de r (as ordens de r
módulo os primos pequenos são acessíveis; lista vazia = conjunto morto). Logo
p^{ℓ−1} < Φ_ℓ(p) ≤ ℓ·r^{A_r} limita ℓ, que é enumerado e testado (ℓ | r − 1 e
p^ℓ ≡ 1 mod r). As valuações da reconstrução são as diretas de §4.2. Dois primos
grandes no mesmo conjunto: `NaoCertificavel`.

Validação: forçando `ORDEM_BITS = 12` nos testes, os conjuntos completos reais de
k = 7 com exatamente um primo "grande" (≥ 20 conjuntos) produzem pela via nova
**exatamente** as listas da via direta (`expoentes_validos_ordens`); e o caso (B1)
primo é exercitado em {5,7,11,13,31}+19 (ord₁₉(7) = 3, 3 não é ordem de 7 módulo
nenhum outro primo do conjunto; σ(7²) = 3·19 fecha). Honestidade: em k ≤ 8 nenhum
primo de conjunto completo passou de 65 bits (`conjuntos_com_primo_grande = 0`), a
via só foi exercitada pelos testes.

### 4.4 ω = 7 fecha

`certifica_omega(7)` (versão final do bloco): 549 nós, 172 partições, 51 fallbacks
de índice, 153 conjuntos completos (224 mortos pela poda barata), 0 folhas,
0 amigos, 1,5 s, sem `NaoCertificavel`. Contagens congeladas em
`tests/test_omega_k.py`. (Antes da poda de §4.6 eram 648 nós e 164 conjuntos —
mesmo veredito.)

### 4.5 ω = 8: compromissos gerais e ramificação por expoente com cauda

Primeira parede de k = 8: C = {5,7,11,13,31,71}, s = 2, a₁ = 2 — os dois orçamentos
(v₅ = 1, v₃ = 2) podem ser carregados pelos dois desconhecidos (sem raciocínio
finito com s = 2) e ∏sup = 1,80686 ≥ 9/5. Mas o nó é **apertado**:
∏I(p²) = 1,79935 e a₇ = 4 já dá 1,80451 > 9/5 (morto com s ≥ 1); logo a₇ = 2 é
forçado e σ(7²) = 57 = 3·19 obriga 19 ∈ S — pin (ou morte, se 19 ≤ lo). É a
ramificação por expoente de Nielsen, que exige generalizar o compromisso: o estado
passa a carregar `fixos = {p: a_p}` para qualquer primo conhecido. Um compromisso
entra exato nas cotas, força v_ℓ(a_p + 1) nos orçamentos (alimentador fixo tem k
forçado), restringe a lista no conjunto completo e — o essencial — **fecha
σ(p^{a_p}) em S ∪ {3}** peça a peça (Φ_d(p) para d | a_p + 1, cada uma bem menor que
σ(p^{a_p})): primos novos são pins, mais que s ou algum ≤ lo é morte.

Segunda parede: C = {5,7,11,13,31,89}, s = 2, a₁ = 2 — nó **solto**: nenhum primo
sozinho tem janela finita (7 → ∞ dá 1,79942 < 9/5), embora ∏sup = 1,80166 > 9/5.
Solução clássica (Nielsen): **caudas**. Cada primo livre q tem ganho
g_q = sup(q)/I(q^{min_q}); ordenando por ganho decrescente q₁, q₂, …, seja m mínimo com
prod_min·g_{q₁}⋯g_{q_m} > 9/5 (existe: o produto total é prod_sup). Ramifica-se
q = q_m em a_q ∈ {min_q, …, A − 2} EXATOS e a CAUDA a_q ≥ A, com A o menor par tal que
prod_min·g_{q₁}⋯g_{q_{m−1}}·I(q^A)/I(q^{min_q}) > 9/5 (partição completa de a_q).
Progresso: A > min_q pela minimalidade de m; na cauda os m − 1 ganhos maiores já
bastam (m decresce); com m = 1 a cauda morre. Medida (s, #primos livres, m)
estritamente decrescente em toda aresta ⟹ a árvore é finita. No residual: ganhos
g₇ = 1,00292 > g₁₁ = 1,00075 > …; prod_min·g₇ = 1,79942 ≤ 9/5 < prod_min·g₇·g₁₁
⟹ ramifica o 11: a₁₁ = 2 exato (σ(121) = 7·19 pina o 19) e cauda a₁₁ ≥ 4; na cauda
m = 1 ⟹ ramifica o 7: a₇ = 2 exato (57 = 3·19) e cauda a₇ ≥ 4, morta
(prod_min = 1,8005 > 9/5). Congelado em `test_ramificacao_por_expoente_com_cauda_no_residual_de_k8`.

Resultado (versão final do bloco): **k = 8 certificado** — 210 456 nós, 45 254
partições, 323 ramificações por expoente (323 caudas), 839 fallbacks de índice,
145 659 conjuntos completos (19 350 mortos pela poda barata), 467 casos sem fecho,
0 folhas, 0 amigos, 72 s, sem `NaoCertificavel`. Maior primo em C:
20796629989288946761 (65 bits). (A primeira versão que fechou k = 8 — sem cache e
sem a poda de §4.6 — levou 312 s em 214 200 nós; mesmo veredito.)

### 4.6 Fechos fora do orçamento: informação parcial nunca é descartada

A primeira tentativa de k = 9 parou honestamente aos 108 s: `NaoCertificavel`
"cofator composto de 91 bits com s = 2 — fatoração fora do orçamento"
(`FATORA_BITS = 90`). A exceção nascia dentro da partição e abortava o nó inteiro,
mesmo quando os outros casos do nó pinavam e as caudas/índice fechariam o caso
problemático. Duas iterações até a semântica certa:

1. *Primeira versão* — o caso com fecho fora do orçamento virava simplesmente
   "aberto" (sem pins). Sólido, mas **descartava informação certa**: em k = 8 o
   ramo a₁ = 40 (σ(5⁴⁰) = Φ₄₁(5), 95 bits) perdia os pins pequenos já achados
   (20743, 45985571) e o índice tinha de reencontrá-los enumerando o menor
   desconhecido até 4,6·10⁷ — o run passou de 214 200 para > 3 000 000 nós e foi
   abortado. (Na versão anterior o mesmo ramo nem existia: a exceção abortava a
   partição da raiz, que caía no índice, e as partições dos filhos, com s menor,
   tinham a₁ ≤ 31.)
2. *Versão final* — `_novos_e_resto` devolve (primos novos já identificados, resto):
   os identificados são pins válidos **independentemente** do resto, e um resto
   composto fora do orçamento garante ≥ 2 primos novos ainda não identificados
   (composto que não é potência de primo, coprimo com os permitidos e com os
   identificados): morte se não cabem nos slots. Peças distintas de σ(p^a) têm restos
   coprimos (um primo comum a Φ_d(p) e Φ_{d′}(p) divide d/d′ ≤ a + 1 < 10⁵), logo
   contam 2 cada; restos de bases distintas podem partilhar primos e contam 2 no
   total. Uma peça fora dos gates de Φ (`PIN_BITS`, `GRAU_PHI_MAX`) é só informação
   a menos (`casos_sem_fecho` nas estatísticas). Nenhuma exceção sai mais da
   partição; `NaoCertificavel` fica reservada ao nó sem saída (caso aberto sem
   ramo e sem índice) e ao conjunto completo com dois primos grandes.

3. *Poda que faltava* — mesmo com os pins conservados, o ramo a₁ = 40 seguia
   pelo índice: Φ₄₁(5) não tem fator < 10⁵ (só o resto de 95 bits, extra = 2), e
   a **cota universal** a₁ ≤ 1 + (c₅+s)(c₅+s−1) só era aplicada ao enumerar a₁
   livre. Ela vale em TODO nó: em {5, 7} com s = 6 dá a₁ ≤ 31 < 40 — o filho morre
   na hora. Com a₁ fixo, a cota é re-checada em cada partição (`test_cota_universal_
   vale_tambem_para_a1_comprometido`). Isto enxuga também k ≤ 7 (k = 6: 60 → 51
   nós; k = 7: 648 → 549 nós), sem mudar veredito algum.

Junto entrou cache
(`_phi_valor`, divisão por tentativa, classificação do cofator: o perfil de k = 8
mostrava `_novos_de` + `cyclotomic_poly` com ~45% do tempo). A primeira versão do
cache tinha um **bug de falso morto**: a divisão por tentativa pode parar cedo
(q² > c) deixando em c um primo *permitido* pequeno (ex.: Φ₃(5) = 31 com 31 ∈ C),
que a classificação contava como novo e consumia um slot; `_novos_de_sigma(5, 8,
·, s = 2)` devolvia "morto" (σ(5⁸) = 31·19·829 precisa de 2 slots novos, não 3) e
k = 6 caía de 60 para 35 nós. Pegaram-no dois testes: a equivalência
`_novos_de_sigma` ≡ `_novos_de` sobre σ(p^a) inteiro e as contagens congeladas de
k = 6/7. Fica registrado como mais um "mutante" que a bateria detecta (na linha
dos três do Bloco 2); a lição de método vai para FRACASSOS.md.

### 4.7 Saída do script oficial

`python experiments/elimina_omega_k.py --k-max 8` (linhas de pins omitidas):

```
omega = 1: nos=1 mortos_min=0 ramo_i=0 particoes=0 ramos_expoente=0 caudas=0 conjuntos_completos=0 completos_mortos_indice=1 com_primo_grande=0 casos_sem_fecho=0 folhas=0 amigos=0 tempo=0.0s
omega = 2: nos=1 mortos_min=0 ramo_i=0 particoes=1 ramos_expoente=0 caudas=0 conjuntos_completos=0 completos_mortos_indice=0 com_primo_grande=0 casos_sem_fecho=0 folhas=0 amigos=0 tempo=0.0s
omega = 3: nos=3 mortos_min=0 ramo_i=0 particoes=2 ramos_expoente=0 caudas=0 conjuntos_completos=0 completos_mortos_indice=1 com_primo_grande=0 casos_sem_fecho=0 folhas=0 amigos=0 tempo=0.1s
omega = 4: nos=5 mortos_min=0 ramo_i=2 particoes=4 ramos_expoente=0 caudas=0 conjuntos_completos=0 completos_mortos_indice=1 com_primo_grande=0 casos_sem_fecho=0 folhas=0 amigos=0 tempo=0.0s
omega = 5: nos=7 mortos_min=0 ramo_i=5 particoes=7 ramos_expoente=0 caudas=0 conjuntos_completos=0 completos_mortos_indice=0 com_primo_grande=0 casos_sem_fecho=0 folhas=0 amigos=0 tempo=0.1s
omega = 6: nos=51 mortos_min=0 ramo_i=17 particoes=29 ramos_expoente=0 caudas=0 conjuntos_completos=0 completos_mortos_indice=22 com_primo_grande=0 casos_sem_fecho=3 folhas=0 amigos=0 tempo=0.6s
omega = 7: nos=549 mortos_min=0 ramo_i=51 particoes=172 ramos_expoente=0 caudas=0 conjuntos_completos=153 completos_mortos_indice=224 com_primo_grande=0 casos_sem_fecho=41 folhas=0 amigos=0 tempo=0.9s
omega = 8: nos=210456 mortos_min=193 ramo_i=839 particoes=45254 ramos_expoente=323 caudas=323 conjuntos_completos=145659 completos_mortos_indice=19350 com_primo_grande=0 casos_sem_fecho=467 folhas=0 amigos=0 tempo=71.6s

CERTIFICADO: todo amigo de 10 tem omega(N) >= 9.
Rotulo: [PROVADO-CONDICIONAL: Teoremas A-D e Lemas/Fato 0 da Fase 0 + Zsygmondy, LTE e formula de valuacao de Nielsen/Voight (classicos) + correcao de core/omega_k.py (certificador recursivo AINDA SEM passada adversarial propria - nao e load-bearing), core/omega6.py e core/cadeias.py (passada adversarial em results/FASE_1.md §2.5) + correcao de sympy.n_order/factorint/isprime/nextprime/cyclotomic_poly nas chamadas consumidas]
Nota: para omega >= 7 o certificado load-bearing e o do Bloco 2 (experiments/elimina_omega6.py); acima disso so este recursivo cobre, e o rotulo fica pendente da passada adversarial propria.
```

### 4.8 Rótulos, honestidade e o que falta

- **Resultado I.** Todo amigo de 10 tem **ω(N) ≥ 9**.
  `[PROVADO-CONDICIONAL: Teoremas A–D e Lemas/Fato 0 da Fase 0 + Zsygmondy, LTE e
  fórmula de valuação de Nielsen/Voight (clássicos) + correção de core/omega_k.py
  (AINDA SEM passada adversarial própria) e de core/cadeias.py/core/omega6.py
  (passada adversarial §2.5, mas com as alterações de §4.2 e a extensão de
  _conjunto_completo ainda não revisadas adversarialmente) + correção de
  sympy.n_order/factorint/isprime/nextprime/cyclotomic_poly/divisors nas chamadas
  consumidas]`. **Não é load-bearing** até a passada adversarial própria; e não é
  novo — Thackeray (arXiv:2310.15900) tem ω(N) ≥ 10. O valor é a reprodução
  mecânica, independente e curta (75 s) de uma parte do estado da arte, com
  método reutilizável para k ≥ 9.
- Alvos da passada adversarial do recursivo (obrigatória antes de qualquer subida de
  rótulo): (i) completude da partição de a_q em `_ramos_expoente` e a alegação "a
  cauda com prod_min > 9/5 morre com s ≥ 1"; (ii) a contagem de testemunhas
  `faltam` em `_casos_ell` (níveis sem testemunha conhecida exigem desconhecidos
  distintos) e o k forçado dos alimentadores fixos; (iii) a equivalência de
  `_viavel_m0` (múltiplo viável ⟺ m₀ viável); (iv) `_novos_de` com cofator
  potência de primo / composto e os gates (`FATORA_BITS`, `PIN_BITS`,
  `GRAU_PHI_MAX`), que só podem levantar `NaoCertificavel`, nunca matar; (v) a poda
  de igualdade em s = 0 com todos os expoentes fixos; (vi) o lema de primo grande
  (B1), em especial v_r(σ(N)) = a_r (r ∉ {3, 5}) e o uso de A_r; (vii) o invariante
  "pin ≤ lo ⟹ morto" na presença de compromissos.
- k = 9: em execução ao fechar este bloco (a₁ ≤ 1 + 8·7 = 57 na raiz; σ(5^{a₁})
  com a₁ + 1 primo chega a Φ₅₃(5) de 121 bits — se o cofator composto exceder
  `FATORA_BITS`, a saída honesta é `NaoCertificavel` na raiz, e o caminho é um
  oráculo de fatorações certificadas por multiplicação, tabelas de Cunningham).
