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
