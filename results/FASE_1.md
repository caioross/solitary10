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
