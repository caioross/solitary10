"""Certificador RECURSIVO: nenhum amigo de 10 com omega(N) = k (Fase 1, Blocos 3-4).

Generaliza core/omega6.py para qualquer k. Estado = (C, s, lo, fixos, minimos):
  C     = primos JÁ CONHECIDOS de S (lista ordenada, sempre contém 5);
  s     = quantos primos de S ainda são desconhecidos;
  lo    = cota: todo desconhecido é > lo e não está em C. Invariante: todo primo de
          S que seja <= lo está em C (os desconhecidos são enumerados do menor
          para o maior, e um primo pinado é sempre > lo no momento do pin);
  fixos = expoentes COMPROMETIDOS no ramo, {p: a_p} (Bloco 3: só a1; Bloco 4:
          qualquer primo conhecido). Um compromisso entra EXATO nas cotas de
          índice (I(p^{a_p}) no lugar de I(p^2) e de p/(p-1)), força a
          contribuição v_ell(a_p+1) nos orçamentos, restringe a lista de expoentes
          no conjunto completo e — o essencial — fecha sigma(p^{a_p}) em S + {3}:
          seus primos novos são PINADOS (ou o caso morre);
  minimos = cotas inferiores PARES a_p >= A comprometidas no ramo (caudas do
          passo 3); entram em prod_min (I(p^A) no lugar de I(p^2)) e filtram a
          lista de expoentes no conjunto completo.

Em cada nó (tudo exato, Fraction/int):
  s = 0   conjunto completo: podas de índice baratas; listas de expoentes por
          _listas_expoentes (fecho por ordens + reconstrução exata; trata UM primo
          "grande" sem fatorar r - 1, ver abaixo); core/omega6._conjunto_completo
          (orçamentos v3/v5 + igualdade exata) restrito aos fixos;
  MORTO   se s >= 1 e prod_{p em C} I(p^{a_p ou 2}) >= 9/5 (os s fatores restantes
          são > 1);
  senão   PARTIÇÃO (abaixo): partição completa de casos, válida em qualquer nó;
          cada caso pina >= 1 desconhecido (recorre com s menor), ou compromete o
          expoente de um primo conhecido (recorre com |fixos| maior), ou morre.
          Se a partição deixa algum caso aberto (NaoCertificavel), o fallback é o
          ÍNDICE: se prod_{p em C} sup(p) < 9/5 (sup = I(p^{a_p}) exato se fixo),
          o MENOR desconhecido U é limitado (I(N) < prod_sup(C)·sup(U)·[sups dos
          s-1 menores primos > U fora de C], majoração não-crescente em U com
          limite prod_sup(C) < 9/5 — o laço termina) e recorre com
          (C + {U}, s-1, lo = U); senão o nó levanta NaoCertificavel com o estado
          residual. Nenhuma lacuna é silenciosa.
  Terminação: cada caso reduz s ou aumenta |fixos| <= |C|; com todos os expoentes
  fixos prod_sup = prod_min é exato e o índice limita os desconhecidos.

PARTIÇÃO (Blocos 3-4), nesta ordem:
  1. FECHO DOS FIXOS: para cada (p, a) em fixos, os primos de sigma(p^a) =
     prod_{d | a+1, d > 1} Phi_d(p) estão em S + {3}; os que não estão em C + {3}
     são desconhecidos (pin; > s primos novos ou algum <= lo => morto). Fatora-se
     peça a peça (Phi_d(p) é bem menor que sigma(p^a)), com gates exatos. Um fecho
     PARCIAL nunca é descartado: os primos já identificados são pins, e um cofator
     composto fora do orçamento de fatoração (FATORA_BITS) garante >= 2 primos
     novos ainda não identificados (morte se não cabem nos slots). Uma peça fora
     dos gates de Phi (PIN_BITS, GRAU_PHI_MAX) é só informação a menos (contada em
     casos_sem_fecho); o caso segue para os passos 2-3 e o índice.
  2. ORÇAMENTOS (Bloco 3): dois orçamentos EXATOS decorrem de sigma(N) = 9N/5 com
     3 ∤ N:  v5(sigma(N)) = a1 - 1  e  v3(sigma(N)) = 2.  Pelo Fato 2, só bases
     q ≡ 1 (mod ell) alimentam ell in {3, 5}, com v_ell(sigma(q^a)) = v_ell(a+1).
     Um alimentador q com k = v_ell(a_q+1) tem Phi_{ell^j}(q) | sigma(N) para
     j = 1..k: seus fatores fora de C + {3} são pins. Zsygmondy dá um primo
     primitivo r_j com ord_{r_j}(q) = ell^j em S menos {q} para cada j; um
     desconhecido tem UMA só ordem módulo q, logo os níveis j sem testemunha em C
     (teste: q^{ell^j} ≡ 1 e q^{ell^{j-1}} ≢ 1 mod r) exigem desconhecidos
     DISTINTOS. Alimentadores com expoente fixo têm k forçado.
     Cota universal para a1: cada alimentador U tem v5(a_U+1) <= c5 + s - 1 (os
     r_j são distintos e ≡ 1 mod 5), com c5 = #{q em C : q ≡ 1 (mod 5)}; com no
     máximo c5 + s alimentadores,  a1 <= 1 + (c5 + s)(c5 + s - 1).
     Para cada a1 par (ou o fixo): pins de sigma(5^{a1}) ou distribuição de
     T = a1 - 1 entre alimentadores conhecidos e desconhecidos; para ell = 3,
     T = 2. As duas partições são independentes: o nó usa o PRODUTO de casos; um
     par (caso5, caso3) fecha se algum dos dois pina. Se ambos são abertos e
     s = 1, o único desconhecido U precisa de m0 = 5^{k5}·3^{k3} | a_U + 1, e todo
     divisor d > 1 de a_U+1 é ord_r(U) para r em C, logo d | r-1, com testemunhas
     distintas para divisores distintos: existe a_U+1 viável múltiplo de m0 sse
     os divisores de m0 admitem injeção em C (a injeção de um múltiplo restringe-se
     a m0) — teste finito que mata ou deixa o par aberto.
  3. RAMIFICAÇÃO POR EXPOENTE COM CAUDA (Bloco 4, estilo Nielsen): num par
     aberto com prod_sup > 9/5 (senão o índice resolve), cada primo livre q tem
     ganho g_q = sup(q)/I(q^{min_q}) (o quanto I(q^{a_q}) ainda pode subir).
     Ordenando por ganho decrescente q_1, q_2, ..., seja m mínimo com
     prod_min · g_{q_1} ··· g_{q_m} > 9/5 (existe: o produto total é prod_sup).
     Ramifica-se q = q_m:  a_q em {min_q, ..., A-2} EXATOS (cada ramo compromete
     a_q; o filho o fecha no passo 1) e a CAUDA a_q >= A, com A o menor par tal
     que prod_min · g_{q_1} ··· g_{q_{m-1}} · I(q^A)/I(q^{min_q}) > 9/5. Partição
     completa de a_q. Progresso garantido: A > min_q (por minimalidade de m o
     produto até q_{m-1} é <= 9/5) e, na cauda, os m-1 ganhos maiores já bastam
     (m decresce); com m = 1 a cauda morre (prod_min > 9/5). Medida
     (s, #primos livres, m) estritamente decrescente em toda aresta => termina.

PRIMOS GRANDES (Bloco 4): pins como Phi_5(q) passam de 100 bits e r - 1 pode não
ser fatorável, o que torna ord_r(p) inacessível. Num conjunto completo S = S' + {r}
com r grande ((r-1) com mais de ORDEM_BITS bits), para cada p em S':
  todo divisor d > 1 de a_p + 1 é ord_{r'}(p) para algum r' em S menos {p}, com
  testemunhas distintas para divisores distintos (Zsygmondy + cada r' tem uma só
  ordem); r testemunha no máximo UM divisor, o = ord_r(p). Com D' = ordens ímpares
  de p módulo S' menos {p} (computáveis), os casos são exaustivos:
   (A)  todos os divisores em D'                          -> candidatos de D';
   (B2) a_p + 1 em D' com exatamente um divisor d* fora de D' e ord_r(p) = d*
        (teste modular: p^{d*} ≡ 1 e p^{d*/ell} ≢ 1 mod r para ell | d*);
   (B1) a_p + 1 = o fora de D', todos os divisores PRÓPRIOS em D':
        o composto -> o = ell·e com ell primo em D', e em D' (finito; testa a ordem);
        o = ell primo -> Phi_ell(p) = ell^eps · r^v: um fator primo q != ell tem
        ord_q(p) = ell fora de D', logo q = r; o não-primitivo só pode ser ell, com
        eps <= 1 (LTE). v = v_r(sigma(p^{ell-1})) <= v_r(sigma(N)) = a_r <= A_r,
        onde A_r vem dos expoentes válidos de r (as ordens de r módulo os primos
        pequenos são acessíveis; lista vazia = conjunto morto). Assim
        p^{ell-1} < Phi_ell(p) <= ell · r^{A_r}, o que limita ell; enumera-se ell
        e sobrevive só se ell | r - 1 e p^ell ≡ 1 (mod r).
  As valuações da reconstrução (cadeias.sigma_fecha_em) são diretas, por
  exponenciação modular — sem ordens. Dois primos grandes no mesmo conjunto:
  NaoCertificavel (caso não tratado).

Honestidade estrutural: ou o caso é provadamente morto, ou pina, ou compromete
(expoente exato ou cauda), ou levanta NaoCertificavel (sem certificado).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from functools import lru_cache

from sympy import cyclotomic_poly, divisors, factorint, isprime, nextprime, perfect_power

from core.cadeias import (
    _candidatos_m,
    _divisores_impares_maiores_que_1,
    expoentes_validos_ordens,
    ordens_impares,
    sigma_fecha_em,
    v_p,
)
from core import omega6 as _o6
from core.motor import I_pp, sup_pp
from core.omega6 import NaoCertificavel, _conjunto_completo


@dataclass
class StatsK:
    k: int = 0
    nos: int = 0
    mortos_min: int = 0
    completos_mortos_indice: int = 0
    ramo_i: int = 0
    particoes: int = 0
    ramos_expoente: int = 0
    caudas: int = 0
    casos_sem_fecho: int = 0
    conjuntos_completos: int = 0
    conjuntos_com_primo_grande: int = 0
    assinaturas_testadas: int = 0
    conjuntos: list[tuple[int, ...]] = field(default_factory=list)
    pins: list[tuple[tuple[int, ...], str, tuple[int, ...]]] = field(default_factory=list)
    amigos: list[dict[int, int]] = field(default_factory=list)


ORDEM_BITS = 80           # (r-1) com mais bits: r é "grande" — nunca fatoramos r - 1
FATORA_BITS = 90          # acima disto, factorint do sympy pode nao terminar
GRAU_PHI_MAX = 200        # cyclotomic_poly(d, q) com phi(d) > isto e proibitivo
PIN_BITS = 20000          # Phi_d(q) com mais bits que isto nao e testado (gate exato)
_PEQUENOS = None


def _primos_pequenos() -> list[int]:
    global _PEQUENOS
    if _PEQUENOS is None:
        from sympy import primerange
        _PEQUENOS = list(primerange(2, 100_000))
    return _PEQUENOS


_LIMITE_PEQUENOS = 100_000


@lru_cache(maxsize=None)
def _divisao_pequena(valor: int) -> tuple[tuple[int, ...], int]:
    """(primos < 10^5 de valor, cofator sem eles). O cofator e 1, primo, potencia
    de primo ou composto com todos os primos > 10^5 (se o laco parou por q^2 > c,
    o cofator e 1 ou primo). Cache: o mesmo Phi_d(q) e consultado em muitos nos."""
    c = valor
    peq: list[int] = []
    for q in _primos_pequenos():
        if q * q > c:
            break
        if c % q == 0:
            peq.append(q)
            while c % q == 0:
                c //= q
    return tuple(peq), c


@lru_cache(maxsize=None)
def _classifica_cofator(c: int) -> tuple[str, int]:
    """("um", 0) | ("primo", c) | ("potencia", base prima) | ("composto", 0)."""
    if c == 1:
        return ("um", 0)
    if isprime(c):
        return ("primo", int(c))
    pp = perfect_power(c)
    if pp and isprime(pp[0]):
        return ("potencia", int(pp[0]))
    return ("composto", 0)


@lru_cache(maxsize=None)
def _fatora(c: int) -> tuple[int, ...]:
    """Primos distintos de c (c com no maximo FATORA_BITS bits — o chamador garante)."""
    return tuple(sorted(int(r) for r in factorint(c)))


def _novos_e_resto(valor: int, permitidos: set[int], s: int) -> tuple[tuple[int, ...], int] | None:
    """(primos NOVOS conhecidos de `valor`, resto) — todos os primos de `valor` fora
    de `permitidos` tem de ser desconhecidos. resto = 1, ou um cofator COMPOSTO que
    ficou fora do orcamento de fatoracao (FATORA_BITS): ele tem >= 2 primos
    distintos, todos > 10^5, nenhum permitido, nenhum ja em `novos` — isto e, >= 2
    desconhecidos AINDA NAO identificados. None = caso morto (conhecidos + os >= 2 do
    resto excedem os slots). Nunca levanta: informacao parcial e devolvida como
    tal, e o chamador decide o que fazer com o resto (nunca o descarta como "nada").

    Sem fatoracao completa: divisao por tentativa ate 10^5 (cache), remocao de TODOS
    os permitidos do cofator (um permitido pequeno pode sobrar quando a divisao
    para cedo por q^2 > c; conta-lo como novo produziria falsos mortos), e o cofator
    restante e 1, primo, potencia de primo, ou composto com >= 2 primos > 10^5."""
    peq, c = _divisao_pequena(valor)
    novos: set[int] = {q for q in peq if q not in permitidos}
    if len(novos) > s:
        return None
    for q in permitidos:
        while c % q == 0:
            c //= q
    tipo, base = _classifica_cofator(c)
    resto = 1
    if tipo == "primo" or tipo == "potencia":
        novos.add(base)
    elif tipo == "composto":
        if len(novos) + 2 > s:
            return None
        if c.bit_length() > FATORA_BITS:
            resto = c
        else:
            novos |= set(_fatora(c))
    if len(novos) + (2 if resto > 1 else 0) > s:
        return None
    return tuple(sorted(novos)), resto


def _novos_de(valor: int, permitidos: set[int], s: int) -> tuple[int, ...] | None:
    """Fecho COMPLETO: primos de `valor` fora de `permitidos`, ou None (morto).
    Levanta NaoCertificavel se sobra um resto sem fatorar (usada onde informacao
    parcial nao serve; a particao usa _novos_e_resto)."""
    r = _novos_e_resto(valor, permitidos, s)
    if r is None:
        return None
    novos, resto = r
    if resto > 1:
        raise NaoCertificavel(
            f"cofator composto de {resto.bit_length()} bits - fatoracao fora do orcamento"
        )
    return novos


@lru_cache(maxsize=None)
def _phi_valor(d: int, q: int) -> int | None:
    """Phi_d(q) inteiro, ou None se o grau phi(d) excede GRAU_PHI_MAX ou o valor
    excede PIN_BITS bits (gates exatos e deterministicos). Cache: o mesmo par
    (d, q) e consultado em muitos nos."""
    from sympy import totient
    if int(totient(d)) > GRAU_PHI_MAX:
        return None
    val = int(cyclotomic_poly(d, q))
    if val.bit_length() > PIN_BITS:
        return None
    return val


def _novos_de_sigma(p: int, a: int, permitidos: set[int], s: int,
                    sem_fecho: list[int] | None = None) -> tuple[tuple[int, ...], int] | None:
    """(primos novos conhecidos de sigma(p^a), extra) com sigma(p^a) =
    prod_{d | a+1, d > 1} Phi_d(p), peça a peça (cada Phi_d(p) tem phi(d)·log2(p)
    bits, muito menos que sigma(p^a)). extra = numero MINIMO de desconhecidos ainda
    nao identificados: 2 por peça com resto sem fatorar (restos de peças distintas
    sao coprimos apos tirar os primos < 10^5: um primo comum a Phi_d(p) e Phi_d'(p)
    divide d/d' <= a+1 < 10^5). None = morto (conhecidos + extra > s). Uma peça fora
    dos gates de _phi_valor e apenas informacao a menos (contada em sem_fecho);
    nunca levanta."""
    novos: set[int] = set()
    extra = 0
    for d in divisors(a + 1):
        if d == 1:
            continue
        val = _phi_valor(d, p)
        if val is None:
            if sem_fecho is not None:
                sem_fecho[0] += 1
            continue
        parte = _novos_e_resto(val, permitidos | novos, s - len(novos) - extra)
        if parte is None:
            return None
        pecas, resto = parte
        novos |= set(pecas)
        if resto > 1:
            extra += 2
        if len(novos) + extra > s:
            return None
    return tuple(sorted(novos)), extra


def _ordem_e_potencia(q: int, r: int, ell: int, j: int) -> bool:
    """ord_r(q) == ell^j?  (r primo != q; sem fatorar r - 1: ord | ell^j e ord ∤ ell^{j-1})"""
    return pow(q, ell**j, r) == 1 and pow(q, ell ** (j - 1), r) != 1


def _e_ordem(p: int, r: int, m: int) -> bool:
    """ord_r(p) == m?  (r primo, r ∤ p, m pequeno — só m é fatorado, nunca r - 1)"""
    if pow(p, m, r) != 1:
        return False
    return all(pow(p, m // ell, r) != 1 for ell in factorint(m))


def _grandes(C: list[int]) -> list[int]:
    return [r for r in C if (r - 1).bit_length() > ORDEM_BITS]


def _sup_prox_excl(depois_de: int, slots: int, excl: frozenset[int]) -> Fraction:
    """Produto dos sups dos `slots` MENORES primos > depois_de que não estão em excl
    (majoração dos fatores dos desconhecidos restantes; não-crescente em depois_de)."""
    prod = Fraction(1)
    q = depois_de
    n = 0
    while n < slots:
        q = int(nextprime(q))
        if q in excl:
            continue
        prod *= sup_pp(q)
        n += 1
    return prod


def _tem_atribuicao_injetiva(divs: list[int], C: list[int]) -> bool:
    """Existe injeção d -> r (r em C) com d | r - 1? (emparelhamento por backtracking;
    instâncias minúsculas: |divs| <= |C| <= ~12, senão False de imediato)."""
    if len(divs) > len(C):
        return False
    usados: set[int] = set()

    def rec(i: int) -> bool:
        if i == len(divs):
            return True
        d = divs[i]
        for r in C:
            if r not in usados and (r - 1) % d == 0:
                usados.add(r)
                if rec(i + 1):
                    return True
                usados.discard(r)
        return False

    return rec(0)


@lru_cache(maxsize=None)
def _expoentes_viaveis_unico(C: tuple[int, ...]) -> tuple[int, ...]:
    """Com um ÚNICO desconhecido U, o conjunto (finito) dos m = a_U + 1 possíveis.

    Todo divisor d > 1 de a_U + 1 é a ordem ord_{r_d}(U) do primo primitivo r_d de
    Phi_d(U) (Zsygmondy; d ímpar >= 3, U >= 5), com r_d em S menos {U} = C (r_d != 3,
    pois ord_3(U) <= 2), logo d | r_d - 1; e divisores DISTINTOS têm testemunhas
    DISTINTAS (cada r tem uma única ordem módulo U). Assim m é viável sse há uma
    injeção {d | m, d > 1} -> C com d | r - 1. Em particular m | r - 1 para algum
    r em C: os candidatos são os divisores ímpares dos r - 1 (conjunto pequeno).
    (Usada na caracterização de residuais e nos testes; a partição usa o teste
    direto _viavel_m0, que não enumera divisores de r - 1.)"""
    Cl = list(C)
    candidatos: set[int] = set()
    for r in Cl:
        n = r - 1
        while n % 2 == 0:
            n //= 2
        candidatos.update(_divisores_impares_maiores_que_1(n))
    return tuple(m for m in sorted(candidatos)
                 if _tem_atribuicao_injetiva(sorted(_divisores_impares_maiores_que_1(m)), Cl))


def _viavel_m0(k5: int, k3: int, C: list[int]) -> bool:
    """Existe a_U + 1 viável (único desconhecido U) múltiplo de m0 = 5^{k5}·3^{k3}?
    Sse os divisores > 1 de m0 admitem injeção em C com d | r - 1: a injeção de um
    múltiplo restringe-se a m0, e m0 é o seu próprio múltiplo."""
    divs = sorted(5**i * 3**j for i in range(k5 + 1) for j in range(k3 + 1)
                  if (i, j) != (0, 0))
    return _tem_atribuicao_injetiva(divs, C)


def _prod_min_sup(C: list[int], fixos: dict[int, int],
                  minimos: dict[int, int]) -> tuple[Fraction, Fraction]:
    """(prod_min, prod_sup) dos conhecidos: I(p^{a_p}) exato se fixo, senão
    [I(p^{min_p}), p/(p-1)) com min_p = minimos.get(p, 2)."""
    prod_min = Fraction(1)
    prod_sup = Fraction(1)
    for p in C:
        if p in fixos:
            x = I_pp(p, fixos[p])
            prod_min *= x
            prod_sup *= x
        else:
            prod_min *= I_pp(p, minimos.get(p, 2))
            prod_sup *= sup_pp(p)
    return prod_min, prod_sup


# caso = ("pin", pins) | ("aberto", kU)   kU = exigência ell^kU | a_U+1 sobre o
# desconhecido alimentador (0 = nenhum desconhecido alimenta; None = s >= 2, sem
# reasoning); pins = tupla ordenada de primos novos (todos > lo, no máximo s).
def _casos_ell(C: list[int], s: int, lo: int, ell: int, T: int,
               fixos: dict[int, int], sem_fecho: list[int] | None = None) -> list[tuple]:
    permitidos = set(C) | {3}
    conhecidos = [q for q in C if q % ell == 1]
    casos: list[tuple] = []
    sem_fecho = sem_fecho if sem_fecho is not None else [0]

    def aberto(restante: int) -> None:
        if restante == 0:
            casos.append(("aberto", 0))
        elif s == 1:
            casos.append(("aberto", restante))
        else:
            casos.append(("aberto", None))

    def fecha(assign: dict[int, int], restante: int) -> None:
        # restante = parte de T carregada por desconhecidos (cada um com k >= 1)
        if restante > 0 and s == 0:
            return  # morto: não há desconhecido para alimentar
        _fecha(assign, restante)

    def _fecha(assign: dict[int, int], restante: int) -> None:
        pins: set[int] = set()
        extra = 0          # desconhecidos garantidos por restos sem fatorar (>= 2 se houver)
        for q, k in assign.items():
            # cada nível j precisa de testemunha r com ord_r(q) = ell^j; um mesmo
            # desconhecido tem UMA só ordem módulo q, logo os níveis sem testemunha
            # conhecida em C exigem desconhecidos DISTINTOS: mais que s => morto
            faltam = [j for j in range(1, k + 1)
                      if not any(_ordem_e_potencia(q, r, ell, j) for r in C if r != q)]
            if len(faltam) > s:
                return
            for j in range(1, k + 1):
                val = _phi_valor(ell**j, q)
                if val is None:
                    # fora do orçamento (grau > GRAU_PHI_MAX ou > PIN_BITS bits):
                    # informação a menos, nunca errada — o caso segue sem este pin
                    sem_fecho[0] += 1
                    continue
                r = _novos_e_resto(val, permitidos, s)
                if r is None:
                    return             # morto: mais primos novos do que slots
                novos, resto = r
                if resto > 1:
                    extra = 2          # restos de q's distintos podem partilhar primos: só 2
                elif not novos and j in faltam:
                    return             # impossivel (Zsygmondy exige primitivo novo)
                pins |= set(novos)
        if len(pins) + extra > s:
            return  # morto
        if pins:
            if min(pins) <= lo:
                return  # morto
            casos.append(("pin", tuple(sorted(pins))))
            return
        aberto(restante)

    def rec(i: int, restante: int, assign: dict[int, int]) -> None:
        if i == len(conhecidos):
            fecha(assign, restante)
            return
        q = conhecidos[i]
        if q in fixos:                      # contribuição forçada pelo compromisso
            k_fixo = v_p(ell, fixos[q] + 1)
            if k_fixo > restante:
                return                      # morto: estoura o orçamento
            ks: range | list[int] = [k_fixo]
        else:
            ks = range(0, restante + 1)
        for k in ks:
            if k:
                assign[q] = k
            rec(i + 1, restante - k, assign)
            if k:
                del assign[q]

    rec(0, T, {})
    return casos


Ramo = tuple[dict[int, int], dict[int, int]]   # (fixos, minimos) do filho


def _ramos_expoente(C: list[int], fixos: dict[int, int],
                    minimos: dict[int, int]) -> list[Ramo] | None:
    """Ramificação por expoente com cauda (passo 3 do cabeçalho). None sse
    prod_sup <= 9/5 (nenhuma cauda mata; o índice é o caminho)."""
    prod_min, prod_sup = _prod_min_sup(C, fixos, minimos)
    if prod_sup <= _o6.ALVO:
        return None
    livres = [p for p in C if p not in fixos]
    ganhos = sorted(livres, key=lambda p: sup_pp(p) / I_pp(p, minimos.get(p, 2)),
                    reverse=True)
    acc = prod_min
    for q in ganhos:
        base = acc                                   # prod_min · ganhos anteriores
        amin = minimos.get(q, 2)
        acc *= sup_pp(q) / I_pp(q, amin)
        if acc <= _o6.ALVO:
            continue
        # q = q_m: base <= ALVO (minimalidade) e base·sup(q)/I(q^{amin}) > ALVO
        fator = base / I_pp(q, amin)
        exatos: list[int] = []
        a = amin
        while fator * I_pp(q, a) <= _o6.ALVO:      # termina: fator·I(q^a) -> acc > ALVO
            exatos.append(a)
            a += 2
        ramos: list[Ramo] = [({**fixos, q: e}, minimos) for e in exatos]
        ramos.append((fixos, {**minimos, q: a}))    # cauda a_q >= a (A > amin)
        return ramos
    raise AssertionError("prod_sup > ALVO mas nenhum prefixo de ganhos excede o alvo")


Caso = tuple[tuple[int, ...], dict[int, int], dict[int, int]]   # (pins, fixos, minimos)


def _particao(C: list[int], s: int, lo: int, stats: StatsK,
              fixos: dict[int, int], minimos: dict[int, int]) -> list[Caso]:
    """Partição completa de casos do nó: lista de (pins, fixos, minimos) do filho.
    Levanta NaoCertificavel se algum par (caso5, caso3) fica aberto sem ramo."""
    if _o6.ALVO != Fraction(9, 5):
        raise NaoCertificavel("particao por orcamentos e especifica do alvo 9/5")
    stats.particoes += 1
    permitidos = set(C) | {3}
    resultado: list[Caso] = []

    def registra(pins: tuple[int, ...], f: dict[int, int], m: dict[int, int],
                 rotulo: str) -> None:
        if (pins, f, m) not in resultado:
            resultado.append((pins, f, m))
            if pins:
                stats.pins.append((tuple(C), rotulo, pins))

    sem_fecho = [0]

    # 1. fecho dos expoentes comprometidos (um fecho fora do orçamento é apenas
    #    informação a menos: o passo segue com os outros)
    pins_fixos: set[int] = set()
    extra_fixos = 0
    for p, a in fixos.items():
        r = _novos_de_sigma(p, a, permitidos | pins_fixos, s - len(pins_fixos), sem_fecho)
        if r is None:
            return []                       # morto
        novos, extra = r
        pins_fixos |= set(novos)
        extra_fixos = max(extra_fixos, extra)   # restos de p's distintos podem partilhar primos
    if len(pins_fixos) + extra_fixos > s:
        return []                           # morto
    if pins_fixos:
        if min(pins_fixos) <= lo:
            return []                       # morto
        registra(tuple(sorted(pins_fixos)), fixos, minimos, "fixos=" + ",".join(
            f"{p}^{a}" for p, a in sorted(fixos.items())))
        return resultado

    # 2. orçamentos
    c5 = sum(1 for q in C if q % 5 == 1)
    a1_max = 1 + (c5 + s) * (c5 + s - 1)
    if 5 in fixos and fixos[5] > a1_max:
        return []                           # morto: a cota universal encolhe quando
                                            # C ganha primos que nao alimentam o 5
    faixa = [fixos[5]] if 5 in fixos else range(2, a1_max + 1, 2)

    casos5: list[tuple[int, tuple]] = []
    for a1 in faixa:
        if 5 not in fixos:
            r = _novos_de_sigma(5, a1, permitidos, s, sem_fecho)
            if r is None:
                continue  # morto: mais primos novos do que slots
            novos, extra = r
            if len(novos) + extra > s:
                continue  # morto
            if novos:
                if novos[0] <= lo:
                    continue  # morto: um primo novo <= lo estaria em C (invariante)
                casos5.append((a1, ("pin", tuple(novos))))
                continue
        for caso in _casos_ell(C, s, lo, 5, a1 - 1, {**fixos, 5: a1}, sem_fecho):
            casos5.append((a1, caso))

    casos3 = _casos_ell(C, s, lo, 3, 2, fixos, sem_fecho)
    stats.casos_sem_fecho += sem_fecho[0]

    abertos: list[str] = []
    for a1, (tipo5, dado5) in casos5:
        f1 = {**fixos, 5: a1}
        if tipo5 == "pin":
            registra(dado5, f1, minimos, f"a1={a1}")
            continue
        for tipo3, dado3 in casos3:
            if tipo3 == "pin":
                registra(dado3, f1, minimos, f"a1={a1}:v3")
                continue
            # ambos abertos
            if s == 1 and dado5 is not None and dado3 is not None:
                if (dado5, dado3) != (0, 0) and not _viavel_m0(dado5, dado3, C):
                    continue  # morto: a_U+1 exigiria ordens que C não oferece
            # 3. ramificação por expoente com cauda
            ramos = _ramos_expoente(C, f1, minimos)
            if ramos is None:
                if f1 != fixos:
                    # a1 recém-fixado e prod_sup(f1) <= 9/5: o filho (mesmo nó com
                    # a1 fixo) cai no fallback pelo índice
                    registra((), f1, minimos, "")
                else:
                    abertos.append(f"a1={a1}:k5={dado5},k3={dado3}")
                continue
            stats.ramos_expoente += 1
            for f2, m2 in ramos:
                if m2 is not minimos:
                    stats.caudas += 1
                registra((), f2, m2, "")
    if abertos:
        raise NaoCertificavel(
            f"C={C}, s={s}, fixos={fixos}, minimos={minimos}: casos abertos {abertos[:4]}"
            + (f" ({sem_fecho[0]} fecho(s) fora do orcamento de fatoracao neste no)"
               if sem_fecho[0] else ""))
    return resultado


def _pinagem(C: list[int], s: int, lo: int, stats: StatsK,
             a1_fixo: int | None = None) -> list[tuple[int, ...]]:
    """Compatibilidade (testes): só os pins não-vazios da partição (na ordem)."""
    fixos = {} if a1_fixo is None else {5: a1_fixo}
    return [pins for pins, _, _ in _particao(C, s, lo, stats, fixos, {}) if pins]


# ---------------------------------------------------------------------------
# Conjuntos completos com um primo grande (Bloco 4)
# ---------------------------------------------------------------------------

def _expoentes_com_primo_grande(p: int, S_peq: frozenset[int], r: int,
                                extras: frozenset[int], A_r: int) -> list[int]:
    """Expoentes válidos de p (p != r) em S = S_peq + {r} sem conhecer ord_r(p).
    Casos (A), (B2), (B1) do cabeçalho; depois reconstrução exata."""
    fs = S_peq | {r}
    D = ordens_impares(p, S_peq, extras)
    cand: set[int] = set(_candidatos_m(D))                              # (A)
    for m in D:                                                          # (B2)
        fora = [d for d in _divisores_impares_maiores_que_1(m) if d not in D]
        if len(fora) == 1 and _e_ordem(p, r, fora[0]):
            cand.add(m)
    Dl = sorted(D)
    for ell in Dl:                                                       # (B1) composto
        if not isprime(ell):
            continue
        for e in Dl:
            m = ell * e
            if m in D or m in cand:
                continue
            proprios = [d for d in _divisores_impares_maiores_que_1(m) if d != m]
            if all(d in D for d in proprios) and _e_ordem(p, r, m):
                cand.add(m)
    # (B1) primo: p^{ell-1} < Phi_ell(p) <= ell · r^{A_r}. Impossível assim que
    # (ell-1)(bl(p)-1) >= bl(ell) + A_r·bl(r)  [p^{ell-1} >= 2^{(ell-1)(bl(p)-1)} e
    # ell·r^{A_r} < 2^{bl(ell) + A_r·bl(r)}]; o lado esquerdo cresce linearmente.
    bl_p = p.bit_length() - 1
    bl_r = r.bit_length()
    ell = 3
    while (ell - 1) * bl_p < ell.bit_length() + A_r * bl_r:
        if ell not in D and isprime(ell) and (r - 1) % ell == 0 and pow(p, ell, r) == 1:
            cand.add(ell)
        ell += 2
    return [m - 1 for m in sorted(cand) if sigma_fecha_em(p, m - 1, fs, extras)]


def _listas_expoentes(C: list[int], extras: frozenset[int], stats: StatsK,
                      fixos: dict[int, int], minimos: dict[int, int]) -> list[list[int]] | None:
    """Listas de expoentes válidos por primo do conjunto completo C (restritas aos
    fixos e aos minimos), ou None se alguma é vazia (conjunto morto). Sem primo grande:
    expoentes_validos_ordens (idêntico ao Bloco 2). Com UM primo grande r: r
    primeiro (ordens de r módulo primos pequenos), depois os outros por
    _expoentes_com_primo_grande."""
    fs = frozenset(C)

    def restringe(p: int, exps: list[int]) -> list[int]:
        if p in fixos:
            return [a for a in exps if a == fixos[p]]
        return [a for a in exps if a >= minimos.get(p, 2)]

    grandes = _grandes(C)
    if len(grandes) >= 2:
        raise NaoCertificavel(
            f"C={C}: {len(grandes)} primos com r-1 acima de {ORDEM_BITS} bits "
            "(caso de dois primos grandes nao tratado)"
        )
    if not grandes:
        listas = []
        for p in C:
            exps = restringe(p, expoentes_validos_ordens(p, fs, extras))
            if not exps:
                return None
            listas.append(exps)
        return listas
    r = grandes[0]
    stats.conjuntos_com_primo_grande += 1
    exps_r = restringe(r, expoentes_validos_ordens(r, fs, extras))
    if not exps_r:
        return None
    num, den = _o6.ALVO.numerator, _o6.ALVO.denominator
    A_r = max(exps_r) + v_p(r, num) - v_p(r, den)     # v_r(sigma(N)) = a_r + v_r(num) - v_r(den)
    S_peq = fs - {r}
    listas = []
    for p in C:
        exps = exps_r if p == r else restringe(
            p, _expoentes_com_primo_grande(p, S_peq, r, extras, A_r))
        if not exps:
            return None
        listas.append(exps)
    return listas


def _certifica(C: list[int], s: int, lo: int, stats: StatsK,
               fixos: dict[int, int] | None = None,
               minimos: dict[int, int] | None = None) -> None:
    fixos = fixos or {}
    minimos = minimos or {}
    stats.nos += 1
    prod_min, prod_sup = _prod_min_sup(C, fixos, minimos)

    if s == 0:
        # I(N) >= prod_min (igualdade = candidato vivo) e I(N) < prod_sup (estrito
        # se algum expoente é livre; com todos fixos I(N) = prod_min = prod_sup)
        if prod_min > _o6.ALVO or (prod_sup < _o6.ALVO) or (
                prod_sup == _o6.ALVO and len(fixos) < len(C)):
            stats.completos_mortos_indice += 1
            return
        stats.conjuntos.append(tuple(C))
        extras = _o6._parametros_do_alvo()[0]
        listas = _listas_expoentes(C, extras, stats, fixos, minimos)
        if listas is None:
            stats.conjuntos_completos += 1
            return
        _conjunto_completo(C, stats, listas=listas, fixos=fixos)
        return
    if prod_min >= _o6.ALVO:            # s fatores restantes > 1: I(N) > prod_min >= 9/5
        stats.mortos_min += 1
        return

    fs = frozenset(C)
    try:
        casos = _particao(C, s, lo, stats, fixos, minimos)
    except NaoCertificavel:
        if prod_sup >= _o6.ALVO:
            raise
        casos = None
    if casos is not None:
        for pins, f, m in casos:
            _certifica(sorted(C + list(pins)), s - len(pins), lo, stats, f, m)
        return

    # FALLBACK pelo índice: o menor desconhecido U > lo, U fora de C, é limitado
    stats.ramo_i += 1
    q = lo
    while True:
        q = int(nextprime(q))
        if q in fs:
            continue
        filho_sup = prod_sup * sup_pp(q)
        # majoração não-crescente em q com limite prod_sup < ALVO => break definitivo
        if filho_sup * _sup_prox_excl(q, s - 1, fs) <= _o6.ALVO:
            return
        filho_min = prod_min * I_pp(q, 2)
        if s - 1 >= 1 and filho_min >= _o6.ALVO:
            continue                    # morto só para ESTE q (não monotone)
        if s - 1 == 0 and filho_min > _o6.ALVO:
            continue                    # igualdade é candidato vivo (toda-2)
        _certifica(sorted(C + [q]), s - 1, q, stats, fixos, minimos)


def certifica_omega(k: int, stats: StatsK | None = None) -> StatsK:
    """Varre exaustivamente o espaço omega(N) = k. stats.amigos vazio ao retornar
    => NENHUM amigo de 10 tem exatamente k fatores primos distintos. Levanta
    NaoCertificavel (sem certificado) se alguma cobertura não fechar."""
    if k < 1:
        raise ValueError("k >= 1")
    stats = stats or StatsK(k=k)
    stats.k = k
    _certifica([5], k - 1, 5, stats, {}, {})   # Teorema D: 5 é o menor primo
    return stats


__all__ = ["StatsK", "certifica_omega", "NaoCertificavel"]
