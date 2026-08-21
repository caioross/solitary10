"""Verificação certificada das erratas encontradas na literatura de amigos de 10/20.

Cada bloco Ex re-verifica, com aritmética EXATA (int / Fraction) e sem depender de
sympy, um dos defeitos catalogados em `results/ERRATA.md`. Determinístico e sem
entrada externa: `python experiments/verifica_erratas.py` reproduz tudo.

Papers cobertos (texto conferido em arxiv.org/html):
  [P1] arXiv:2404.00624v5  — Chatterjee, S. Mandal, S. Mandal, "A note on necessary
                             conditions for a friend of 10" (preprint).
  [P2] arXiv:2409.04451v4  — idem, "On Characterizing Potential Friends of 20",
                             Ann. West Univ. Timisoara 61(1) (2025) 205-229.
  [P3] arXiv:2412.02701v4  — S. Mandal, "Prime Divisors of 10's Friends: A
                             Generalization of Prior Bounds", Analele Univ. Oradea
                             Fasc. Mat. 33(1) (2026) 5-12.

Blocos:
  E1  [P1] Lema 2.3 = [P2] Lema 23: `a*n < sum a^{c_i}` é FALSO (igualdade na
      partição toda de 1's). Contraexemplos exaustivos + versão corrigida.
  E2  [P1] Lema 3.6 = [P2] Lema 24: o ENUNCIADO (mínimo = 8a-4) é verdadeiro, mas o
      mínimo é ATINGIDO — logo a prova exibida (desigualdade estrita) não vale.
  E3  [P1] Teorema 1.10: o valor 2w+6a-4 é exatamente o ótimo da relaxação usada na
      prova; não há folga para 2w+6a-2 (que seria necessária para a eq. (7)).
  E4  [P1] Remark 3.7: da desigualdade exibida segue Omega(m) >= w+2a-2, não +2a-1;
      idem eq. (8): Omega(m) >= w(m)+2a-1, não +2a. Certificado por busca exaustiva
      de testemunhas inteiras.
  E5  [P3] Teorema 1.2: X_r > 1 somente para 2 <= r <= 5; para r >= 6 o passo final
      da prova (1 + B/A < X_r) é impossível para qualquer (A, B) positivo.
  E6  [P1] Caso-12 do Teorema 1.2: fator impresso 381/361 = I(19^2) no lugar de
      I(23^2) = 553/529; recomputado, a conclusão do caso se mantém.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from itertools import count


# ----------------------------------------------------------------------------- utils
def eh_primo(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def primo(i: int) -> int:
    """i-ésimo primo, 1-indexado: primo(1) = 2, primo(4) = 7. Sem sympy."""
    if i < 1:
        raise ValueError("i >= 1")
    vistos = 0
    for n in count(2):
        if eh_primo(n):
            vistos += 1
            if vistos == i:
                return n
    raise AssertionError  # inalcançável


def particoes(n: int) -> list[tuple[int, ...]]:
    """Todas as partições de n como tuplas não crescentes (c_1 >= ... >= c_k >= 1)."""
    if n == 0:
        return [()]
    saida = []

    def rec(resto: int, maximo: int, atual: tuple[int, ...]) -> None:
        if resto == 0:
            saida.append(atual)
            return
        for c in range(min(resto, maximo), 0, -1):
            rec(resto - c, c, atual + (c,))

    rec(n, n, ())
    return saida


def I(p: int, e: int) -> Fraction:
    """Índice de abundância de p^e, exato."""
    return Fraction(p ** (e + 1) - 1, p ** e * (p - 1))


def falha(msg: str) -> None:
    raise AssertionError(f"VERIFICAÇÃO FALHOU: {msg}")


# -------------------------------------------------------------------------------- E1
def e1_lema_particao(a_max: int = 8, n_max: int = 8, verboso: bool = True) -> dict:
    """[P1] Lema 2.3 / [P2] Lema 23: `a*n < sum_i a^{c_i}` para toda partição de n.

    Testa exaustivamente todas as partições de n <= n_max para todo inteiro
    a com e < a <= a_max. Registra em que partições a desigualdade ESTRITA falha.
    """
    falhas = []
    total = 0
    for a in range(3, a_max + 1):  # inteiros a > e = 2.718...
        for n in range(1, n_max + 1):
            for c in particoes(n):
                total += 1
                lhs = a * n
                rhs = sum(a ** ci for ci in c)
                if not lhs < rhs:  # desigualdade do paper
                    falhas.append((a, n, c, lhs, rhs))
                if lhs > rhs:  # versão corrigida (<=) nunca pode falhar
                    falha(f"a*n <= sum a^c_i violado em a={a}, c={c}")
    so_uns = all(set(c) == {1} for _, _, c, _, _ in falhas)
    so_igualdade = all(lhs == rhs for _, _, _, lhs, rhs in falhas)
    todos_uns_falham = True
    for a in range(3, a_max + 1):
        for n in range(1, n_max + 1):
            c = tuple([1] * n)
            if a * n != sum(a ** ci for ci in c):
                todos_uns_falham = False
    if not (so_uns and so_igualdade and todos_uns_falham):
        falha("caracterização do caso de igualdade do Lema 2.3")
    if verboso:
        print("E1  [P1] Lema 2.3 / [P2] Lema 23 — desigualdade estrita")
        print(f"    partições testadas: {total} (3 <= a <= {a_max}, 1 <= n <= {n_max})")
        print(f"    violações da forma estrita: {len(falhas)} — TODAS com igualdade")
        print("    e TODAS na partição (1,1,...,1); menor contraexemplo:")
        a, n, c, lhs, rhs = falhas[0]
        print(f"      a={a}, n={n}, partição={c}: a*n = {lhs} = {rhs} = soma a^c_i")
        print("    corrigido: a*n <= soma a^{c_i}, com igualdade sse todo c_i = 1  [OK]")
    return {"falhas": len(falhas), "todas_igualdade": so_igualdade, "todas_uns": so_uns}


# -------------------------------------------------------------------------------- E2
def conjunto_L(n: int, a: int) -> set[int]:
    """L_{n,a} = { sum_{i=1..r} a^{c_i} - r : (c_i) partição de n }."""
    return {sum(a ** ci for ci in c) - len(c) for c in particoes(n)}


def e2_minimo_L(a_max: int = 7, verboso: bool = True) -> dict:
    """[P1] Lema 3.6 / [P2] Lema 24: min L_{2a-1,5} = 8a-4, e é ATINGIDO."""
    linhas = []
    for a in range(1, a_max + 1):
        n = 2 * a - 1
        L = conjunto_L(n, 5)
        m = min(L)
        atingido = (8 * a - 4) in L
        if m != 8 * a - 4:
            falha(f"min L_(2a-1,5) != 8a-4 para a={a} (obtido {m})")
        if not atingido:
            falha(f"8a-4 não atingido para a={a}")
        linhas.append((a, n, m, 8 * a - 4))
    if verboso:
        print("E2  [P1] Lema 3.6 / [P2] Lema 24 — mínimo de L_{2a-1,5}")
        for a, n, m, alvo in linhas:
            print(f"    a={a}: min L_{{{n},5}} = {m} = 8a-4 = {alvo}  (ATINGIDO)")
        print("    enunciado correto; a prova exibida conclui `>` estrito — impossível,")
        print("    pois o mínimo é atingido exatamente na partição (1,...,1)  [OK]")
    return {"linhas": linhas}


# -------------------------------------------------------------------------------- E3
def e3_otimo_teorema_110(a_max: int = 6, w_max: int = 14, verboso: bool = True) -> dict:
    """[P1] Teorema 1.10: ótimo EXATO da relaxação usada na prova.

    Restrições usadas na prova (e só elas):
      N = 5^{2a} * prod_{i=1}^{w-1} p_i^{2 gamma_i};
      sum_{i in T} v_i = 2a-1 com v_i >= 1  (T = primos que carregam a valuação 5);
      i in T  =>  2 gamma_i >= 5^{v_i} - 1;   i não em T  =>  2 gamma_i >= 2.
    Minimiza Omega(N) = 2a + sum 2 gamma_i sobre todas as escolhas de |T| = t e (v_i).
    """
    linhas = []
    for a in range(1, a_max + 1):
        n = 2 * a - 1
        for w in range(max(2 * a, 2), w_max + 1):  # precisa de t <= w-1 primos
            melhor = None
            for c in particoes(n):
                t = len(c)
                if t > w - 1:
                    continue
                omega_total = 2 * a + sum(5 ** vi - 1 for vi in c) + 2 * (w - 1 - t)
                if melhor is None or omega_total < melhor:
                    melhor = omega_total
            if melhor is None:
                continue
            alvo = 2 * w + 6 * a - 4
            if melhor != alvo:
                falha(f"ótimo da relaxação != 2w+6a-4 em a={a}, w={w}: {melhor} vs {alvo}")
            linhas.append((a, w, melhor))
    if verboso:
        print("E3  [P1] Teorema 1.10 — o limite é o ótimo EXATO da relaxação da prova")
        for a, w, m in linhas[:6]:
            print(f"    a={a}, w={w}: min Omega(N) = {m} = 2w+6a-4  (config: {2*a-1}"
                  f" primos ~ 1 mod 10 com expoente 4, demais com expoente 2)")
        print(f"    ... {len(linhas)} pares (a, w) testados, todos com min = 2w+6a-4")
        print("    consequência: a prova NÃO pode entregar 2w+6a-3 nem 2w+6a-2,")
        print("    que seriam necessários para a eq. (7) do Remark 3.7  [OK]")
    return {"pares": len(linhas)}


# -------------------------------------------------------------------------------- E4
def e4_remark_37(a_max: int = 8, w_max: int = 20, verboso: bool = True) -> dict:
    """[P1] Remark 3.7: eq. (7) e eq. (8) não seguem da desigualdade exibida.

    A desigualdade exibida é  2a + 2*Omega(m) >= 2w + 6a - 4.
    Testemunha = tripla (a, w, Omega(m)) que a satisfaz mas viola a eq. (7)
    `Omega(m) >= w + 2a - 1`. Também confere a versão corrigida.
    """
    testemunhas = []
    for a in range(1, a_max + 1):
        for w in range(2, w_max + 1):
            om = w + 2 * a - 2  # valor mínimo permitido pela desigualdade exibida
            exibida_ok = 2 * a + 2 * om >= 2 * w + 6 * a - 4
            eq7_ok = om >= w + 2 * a - 1
            if not exibida_ok:
                falha(f"aritmética da testemunha (a={a}, w={w})")
            if eq7_ok:
                falha("testemunha não viola a eq. (7) — revisar")
            testemunhas.append((a, w, om))
            # versão corrigida nunca falha:
            menor_om = -(-(2 * w + 6 * a - 4 - 2 * a) // 2)  # teto da divisão por 2
            if menor_om != w + 2 * a - 2:
                falha("derivação corrigida da eq. (7)")
    if verboso:
        a, w, om = testemunhas[0]
        print("E4  [P1] Remark 3.7 — off-by-one nas eqs. (7) e (8)")
        print("    exibido:  2a + 2*Omega(m) >= 2w(N) + 6a - 4")
        print("    logo:     Omega(m) >= w(N) + 2a - 2   (teto exato; ambos os lados"
              " são pares, não há ganho de paridade)")
        print("    paper:    Omega(m) >= w(N) + 2a - 1   (eq. 7)  <-- não segue")
        print(f"    testemunha mínima: a={a}, w(N)={w}, Omega(m)={om}:"
              f" {2*a} + {2*om} = {2*a+2*om} >= {2*w+6*a-4}, mas {om} < {w+2*a-1}")
        print("    eq. (8): como w(N) = w(m)+1 (pois 5^{2a} || N), a versão correta é")
        print("             Omega(m) >= w(m) + 2a - 1, não Omega(m) >= w(m) + 2a")
        print(f"    {len(testemunhas)} triplas testadas  [OK]")
    return {"testemunhas": len(testemunhas)}


# -------------------------------------------------------------------------------- E5
def X_r(r: int) -> Fraction:
    """X_r = (36/25) * prod_{i=4..r+1} (1 - 1/p_i)  (produto vazio = 1 para r = 2)."""
    x = Fraction(36, 25)
    for i in range(4, r + 2):
        p = primo(i)
        x *= Fraction(p - 1, p)
    return x


def parte_fixa(r: int) -> Fraction:
    """(5/4) * prod_{j=4..r+1} p_j/(p_j - 1) — o fator fixo da majoração de I(n)."""
    v = Fraction(5, 4)
    for j in range(4, r + 2):
        p = primo(j)
        v *= Fraction(p, p - 1)
    return v


def e5_escopo_teorema_12(r_max: int = 12, verboso: bool = True) -> dict:
    """[P3] Teorema 1.2: o método só fecha para 2 <= r <= 5."""
    linhas = []
    for r in range(2, r_max + 1):
        x = X_r(r)
        fixa = parte_fixa(r)
        if fixa * x != Fraction(9, 5):
            falha(f"identidade (5/4)*prod * X_r = 9/5 falhou em r={r}")
        viavel = x > 1  # existe (A,B) com 1 + B/A < X_r  <=>  X_r > 1
        limiar = Fraction(1, x - 1) if x != 1 else None
        linhas.append((r, x, fixa, viavel, limiar))
        if viavel and fixa >= Fraction(9, 5):
            falha(f"inconsistência em r={r}")
        if not viavel and fixa < Fraction(9, 5):
            falha(f"inconsistência em r={r}")
    if any(not v for _, _, _, v, _ in linhas[: 5 - 2 + 1]):
        falha("algum r <= 5 marcado como inviável")
    if any(v for r, _, _, v, _ in linhas if r >= 6):
        falha("algum r >= 6 marcado como viável")
    if verboso:
        print("E5  [P3] Teorema 1.2 — escopo real do método")
        print("    passo final da prova exige  1 + B/A < X_r ; como 1 + B/A > 1,")
        print("    isso é possível SE E SOMENTE SE X_r > 1.")
        print("    r |            X_r (exato) | X_r > 1 | limiar 1/(X_r - 1)"
              " | parte fixa vs 9/5")
        for r, x, fixa, viavel, limiar in linhas:
            lim = f"{limiar}" if limiar is not None and viavel else "—"
            cmpf = ">= 9/5" if fixa >= Fraction(9, 5) else "< 9/5"
            print(f"   {r:2d} | {str(x):>22} | {str(viavel):>7} | {lim:>18} |"
                  f" {cmpf}")
        print(f"    F_6 = {parte_fixa(6)} > 9/5 (a parte fixa sozinha já estoura o"
              " alvo em r = 6)")
        print("    para r >= 6 o limiar da condição (1) é NEGATIVO: na leitura"
              " pretendida")
        print("    não há par (A,B) admissível; na leitura literal a condição é vazia")
        print("    e o passo final da prova não fecha  [OK]")
    return {"linhas": [(r, str(x), v) for r, x, _, v, _ in linhas]}


def e5b_instancias(w: int = 10, verboso: bool = True) -> dict:
    """Instâncias admissíveis (A,B) para r <= 5 e o limite afiado q_r < p_L."""
    escolhas = {2: (7, 3), 3: (427, 100), 4: (41, 5), 5: (113, 4)}
    saida = []
    for r, (A, B) in escolhas.items():
        x = X_r(r)
        limiar = Fraction(1, x - 1)
        if not Fraction(A, B) > limiar:
            falha(f"(A,B)=({A},{B}) não satisfaz a condição (1) para r={r}")
        L = -(-A * w // B)  # teto de A*w/B
        saida.append((r, A, B, str(limiar), L, primo(L)))
    if verboso:
        print("E5b [P3] instâncias admissíveis e forma afiada q_r < p_L, com w(n) = 10")
        for r, A, B, limiar, L, pL in saida:
            print(f"    r={r}: (A,B)=({A},{B}) > {limiar} = limiar;"
                  f" L={L}, q_{r} < p_{L} = {pL}")
        print("    r=5 com (A,B)=(113,4) é admissível mas NÃO é explicitado no paper")
    return {"instancias": saida}


# -------------------------------------------------------------------------------- E6
def e6_caso12(verboso: bool = True) -> dict:
    """[P1] Caso-12 do Teorema 1.2: 381/361 = I(19^2) impresso onde cabe I(23^2)."""
    impresso = Fraction(381, 361)
    correto = I(23, 2)
    if impresso != I(19, 2):
        falha("381/361 != I(19^2)")
    if correto != Fraction(553, 529):
        falha("I(23^2) != 553/529")
    p1 = I(5, 4) * I(7, 2) * I(11, 2) * I(13, 2) * impresso
    c1 = I(5, 4) * I(7, 2) * I(11, 2) * I(13, 2) * correto
    p2 = I(5, 2) * I(7, 2) * I(11, 2) * I(13, 2) * impresso * I(31, 2)
    c2 = I(5, 2) * I(7, 2) * I(11, 2) * I(13, 2) * correto * I(31, 2)
    alvo = Fraction(9, 5)
    for nome, v in (("1o impresso", p1), ("1o correto", c1),
                    ("2o impresso", p2), ("2o correto", c2)):
        if not v > alvo:
            falha(f"produto {nome} não excede 9/5 — a conclusão do caso mudaria")
    if verboso:
        print("E6  [P1] Caso-12 do Teorema 1.2 — erro de digitação, sem consequência")
        print(f"    impresso 381/361 = I(19^2); a cadeia do caso tem 23, não 19")
        print(f"    correto: I(23^2) = {correto}")
        print(f"    1a desigualdade, com o valor correto: {c1} > 9/5  ({float(c1):.6f})")
        print(f"    2a desigualdade, com o valor correto: {c2} > 9/5  ({float(c2):.6f})")
        print("    conclusão do Caso-12 permanece válida  [OK]")
    return {"c1": str(c1), "c2": str(c2)}


# ------------------------------------------------------------------------------ main
def main() -> int:
    ap = argparse.ArgumentParser(
        description="Verifica, com aritmética exata, as erratas catalogadas em "
                    "results/ERRATA.md (papers arXiv:2404.00624, 2409.04451, "
                    "2412.02701).")
    ap.add_argument("--bloco", choices=["e1", "e2", "e3", "e4", "e5", "e6", "todos"],
                    default="todos", help="qual bloco de verificação rodar")
    ap.add_argument("--a-max", type=int, default=8,
                    help="limite de a nas buscas exaustivas (E1/E4)")
    args = ap.parse_args()

    blocos = {
        "e1": lambda: e1_lema_particao(a_max=args.a_max),
        "e2": lambda: e2_minimo_L(),
        "e3": lambda: e3_otimo_teorema_110(),
        "e4": lambda: e4_remark_37(a_max=args.a_max),
        "e5": lambda: (e5_escopo_teorema_12(), e5b_instancias()),
        "e6": lambda: e6_caso12(),
    }
    ordem = ["e1", "e2", "e3", "e4", "e5", "e6"] if args.bloco == "todos" else [args.bloco]
    for nome in ordem:
        blocos[nome]()
        print()
    print("TODAS AS VERIFICAÇÕES PASSARAM (aritmética exata, sem float nos testes).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
