# FRACASSOS — linhas de ataque abandonadas e becos sem saída

Regra de rigor #6 (`docs/METHODOLOGY.md`): toda linha de ataque abandonada entra aqui com a razão
precisa da falha. Fracassos são dados.

Formato de entrada:

```
## [data] Título curto da linha de ataque
- **O que se tentou:**
- **Por que falhou (razão precisa):**
- **O que aproveitar:**
```

---

## [2026-09-10] Fase 1, Bloco 5 — nós quase justos com s = 2 (beco atual para ω = 9)

- **O que se tentou:** fechar k = 9 com o certificador recursivo depois de eliminar
  a enumeração pelo índice nos nós com s = 1 (equações ciclotômicas para o último
  desconhecido, FASE_1.md §5.1).
- **Por que falhou (razão precisa):** o nó C = {5,7,11,13,31,97,52361}, a₁ = 2, tem
  ∏sup = 9/5 − 1,76·10⁻⁸ com **dois** desconhecidos; o índice limita só o menor,
  U₁ < 1,03·10⁸ (≈ 5,9 milhões de primos com U₂ > U₁, ~11 milhões no laço), e cada
  filho, embora resolvido em ~1 ms, é um nó. A equação Φ_ℓ(U₁) = ℓ^ε·K·U₂^f não
  fecha com f ≥ 1 (U₂ sem cota) nem com expoentes livres em C_ℓ. É o mesmo regime
  em que Thackeray gastou 25 h de CPU (Proposição 3 + DFS).
- **O que aproveitar:** o solver de s = 1 é definitivo e barato; o que falta para
  s = 2 são cotas sobre v_U(q^{ord_U(q)} − 1) (Corolário 6 de Thackeray com c
  limitado pela Proposição 9 — Wieferich generalizado por cálculo finito), ou uma
  contabilidade global de v_r. Alternativa bruta: deixar o k = 9 rodar por horas
  (a enumeração é finita e honesta).

## [2026-09-08] Fase 1, Bloco 3 — ω = 7 pela partição por orçamentos (parede honesta)

- **O que se tentou:** certificar ω(N) ≥ 8 com o certificador recursivo
  (`core/omega_k.py`): partição completa de casos pelos orçamentos exatos
  v₅(σ(N)) = a₁−1 e v₃(σ(N)) = 2 (cota universal a₁ ≤ 1 + (c₅+s)(c₅+s−1); pins pelos
  fatores novos de Φ_{ℓʲ}(q); produto de casos; viabilidade injetiva das testemunhas
  do último desconhecido), com o índice como fallback.
- **Por que falhou (razão precisa):** o estado {5,7,11,13,31,331}+P (a₁ = 2, 331 de
  Φ₃(31)) fica aberto: P carrega o 5 e um dos 3's (15 | a_P+1, e 331 ≡ 1 mod 15 é
  testemunha legítima), a_P = 14 é forçado, e ∏sup = 1,8012 ≥ 9/5 tira o índice de
  jogo. Fechar exige v_P(N) = 14 = Σ_q v_P(q^{ord_P(q)} − 1) sobre ≤ 6 alimentadores —
  contabilidade de valuação do desconhecido (Thackeray, Cor. 6 / Prop. 9), que os
  dois orçamentos não capturam. Também caiu no caminho a primeira arquitetura
  (índice primeiro): explosão combinatória em {5,7,11,13,29} com 2 slots (> 590 s).
- **O que aproveitar:** tudo o que funcionou ficou no repo e é reutilizável — a cota
  universal para a₁, a partição pelo 3, o pin pelos fatores não-primitivos de
  Φ_{ℓʲ}(q), e o emparelhamento injetivo (que é o argumento do fecho do Bloco 1
  aplicado ao primo desconhecido). k ≤ 6 passou de 2 745 conjuntos para 27. O
  Bloco 4 deve acrescentar o orçamento de v_P.
- **Desfecho (2026-09-10, Bloco 4):** o diagnóstico "falta o orçamento de v_P"
  estava errado — a parede era um DEFEITO DE APERTO, não de matemática nova: o
  a₁ = 2 comprometido no ramo não entrava nas cotas de índice. Com I(5^{a₁}) no
  lugar de 5/4, ∏sup{5,7,11,13,31,331} cai de 1,8012 para 1,7868 < 9/5 e o índice
  limita P. Nenhuma contabilidade de v_P foi necessária para ω = 7. Lição: antes
  de pedir teoria nova, verificar se toda informação já comprometida no ramo entra
  em TODAS as podas (ver FASE_1.md, Bloco 4). A mesma lição bateu duas vezes mais
  no Bloco 4: a cota universal a₁ ≤ 1 + (c₅+s)(c₅+s−1) não era re-checada com a₁
  já fixo (ramo a₁ = 40 de k = 8 explodia a > 3·10⁶ nós; em {5,7} a cota dá
  a₁ ≤ 31), e uma fatoração fora do orçamento descartava os pins já identificados
  (informação certa nunca se descarta: FASE_1.md §4.6).

## [2026-08-21] Fase 1, Bloco 2 — escadas de expoentes com kills de janela (abandonada)

- **O que se tentou:** para o ramo não limitado por índice do certificador ω = 6
  (prefixo com ∏ p/(p−1) ≥ 9/5), enumerar expoentes dos 5 primos conhecidos com
  "escadas" (a+1 = ord_P(p), família infinita) mortas por dois kills de índice
  (K1: x ≤ 1 para sempre; K2: janela x < 1 + 1/(2m) impossível para sempre) e
  extração exata do 6º primo do denominador de x = (9/5)/∏I.
- **Por que falhou (razão precisa):** existe *straddle* real — no prefixo
  {5,7,11,13,23}, o eixo do 7 tem ∏ p/(p−1)·resto a 1,5·10⁻⁵ de 9/5: K1 exige
  I(7^a) ≥ um valor ACIMA de sup(7) (nunca) e K2 exige limite ≥ 1 (é < 1); com os
  eixos mais profundos ainda abertos, a iteração não termina e a recursão explode
  (constatado: timeout de 600 s nos testes plantados). A extração do último slot
  continua correta, mas os kills de janela não fecham eixos externos.
- **O que aproveitar:** a extração exata do último slot pelo denominador de x
  (fração já reduzida) é válida e pode voltar a ser útil; o substituto que funcionou
  foi a PINAGEM pela alimentação do 5 (v₅(σ(N)) = a₁−1 ≥ 1 força alimentador
  ≡ 1 (mod 5), que pina P via Φ₅(q) ou σ(5^{a₁})) — exatamente o estilo de cadeia
  da literatura, e fecha o ramo em duas linhas de caso.

## [2026-08-20] Fase 0 — nenhuma linha de ataque matemática abandonada

A Fase 0 foi de fundação/reprodução; todas as metas foram cumpridas. Registram-se
apenas becos metodológicos (úteis para não repetir):

- **Busca de código do GitHub sem autenticação** para checar o repo formal-conjectures
  falhou (exige login; grep.app devolveu HTTP 429). Solução que funcionou e fica como
  método padrão: `git clone --depth 1` + grep local, registrando o commit exato.
- **v₃-contagem pura não descarta 3 | N** (tentativa natural na re-derivação do
  Teorema D): de 5σ(N) = 9N segue v₃(σ(N)) = v₃(N) + 2, mas σ(3^e) ≡ 1 (mod 3) e
  primos ≡ 1 (mod 3) podem fornecer qualquer v₃ via v₃(e_p + 1) — não há contradição
  por valuação isolada. O que fecha o argumento é o **aperto do índice de abundância**
  (subprodutos de I não podem exceder 9/5) combinado com o divisor forçado σ(3²) = 13.
  Aproveitar: em qualquer congruência futura, valuação sozinha tende a ser insuficiente;
  procurar sempre o par (valuação, aperto multiplicativo).
