# FRACASSOS — linhas de ataque abandonadas e becos sem saída

Regra (CLAUDE.md, rigor #6): toda linha de ataque abandonada entra aqui com a razão
precisa da falha. Fracassos são dados.

Formato de entrada:

```
## [data] Título curto da linha de ataque
- **O que se tentou:**
- **Por que falhou (razão precisa):**
- **O que aproveitar:**
```

---

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
