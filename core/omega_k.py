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
          passo 4); entram em prod_min (I(p^A) no lugar de I(p^2)) e filtram a
          lista de expoentes no conjunto completo;
  maximos = cotas superiores a_p <= M (Cor. 6, passo 5), fatos sobre o amigo
          herdados por todo descendente e só melhorados; entram em prod_sup
          (I(p^M) no lugar de p/(p-1)), limitam as caudas e filtram as listas.

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
  3. ÚLTIMO DESCONHECIDO POR EQUAÇÃO CICLOTÔMICA (Bloco 5): num par aberto com
     s = 1, Phi_ell(U) = ell^eps · prod_{q em C_ell} q^{e_q} para um ell | a_U + 1
     com testemunha em C; o lado direito é finito (cota do índice ou expoentes
     fixos) e cada valor dá no máximo um U por raiz inteira — os candidatos
     viram pins (conjuntos completos), sem enumerar primos. Ver o comentário
     longo antes de _ultimo_desconhecido.
  5. COTA FINITA DE EXPOENTE (Bloco 6; Cor. 6 + Prop. 9 de Thackeray): num par
     aberto em que o índice degeneraria (prod_sup < 9/5 mas intervalo do próximo
     primo com mais de LIMIAR_INDICE primos), o expoente de um conhecido livre r
     é limitado por A_r = v_r(num) - v_r(den) + níveis + Wieferich (comentário
     longo antes de _min_residuo_teichmuller); ramifica-se a_r em {min_r, ..., A_r}
     EXATOS (cada filho fecha sigma(r^{a_r}) no passo 1) — sem cauda. A_r < min_r
     mata o caso. Escolhe-se o r com menos ramos.
  4. RAMIFICAÇÃO POR EXPOENTE COM CAUDA (Bloco 4, estilo Nielsen): num par
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

BLOCK 7 — B_min SPLIT OF A NEAR-TIGHT NODE (written in English, as everything new).
  The state gains `hi` (None or an integer): "s >= 1 and the smallest unknown U_1
  satisfies U_1 <= hi". Write v(h) = 1 + 1/h + 1/h^2 (= I(h^2) when h is prime;
  decreasing in h).
  Virtual factor: with hi set, I(N) >= prod_min · v(hi), since I(U_1^a) >= I(U_1^2)
  >= v(hi), every other unknown contributes a factor > 1 and every known prime at
  least its prod_min factor. So the node is dead if prod_min·v(hi) > 9/5, or if
  = 9/5 with s >= 2; also dead if hi <= lo or if s = 0.
  Index facts: let prod_sup < 9/5, R = (9/5)/prod_sup, B = floor(1 + 1/(R-1)). For an
  integer U >= 2, prod_sup·sup(U) >= 9/5 iff U <= B; and v(B-1) = sup(B) + 1/(B-1)^2,
  so prod_sup·v(B-1) > 9/5, while prod_sup·v(h) < 9/5 for h > B.
  Split (step 6 of the partition, only where the index interval of U_1 is long and
  s >= 2, lo < B-1, and B-1 < hi if hi is already set): every friend has exactly one of
    (a)  U_1 <= B-1 -> same node with hi := B-1. Here the tails (step 4) apply with
         prod_min·v(hi) in place of prod_min, because their limit prod_sup·v(hi)
         exceeds 9/5: the smallest unknown is never enumerated;
    (a2) U_1 = B    -> pin B (if B is a prime > lo outside C), lo := B, hi dropped;
    (b)  U_1 > B    -> same node with lo := B (hi kept): all unknowns have an index
         bound, which is where the finite exponent bound of step 5 is valid (s = 2).
  Inheritance of hi: children without pins inherit it; a child whose pins are all
  > hi keeps it (U_1 is still unknown); a child with a pin <= hi drops it (the
  pinned prime then contributes at least v(hi) to prod_min explicitly); children of
  the index enumeration drop it (U_1 became known), and that loop stops at hi.
  With s = 1 and hi set the last-unknown solver uses U_max = min(hi, index bound).
  Termination: order nodes by (s, number of free known exponents); pins decrease s,
  exact branches and a1 commitments decrease the second entry, tail chains are finite
  (m decreases; hi and prod_sup do not change along them, so no split occurs inside),
  and after a split no second split happens before (s, free) decreases: after (a)
  the tails apply, after (b) the precondition lo < B-1 fails.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from functools import lru_cache
from math import gcd, isqrt
from typing import NamedTuple

from sympy import (cyclotomic_poly, divisors, factorint, integer_nthroot, isprime,
                   nextprime, perfect_power, primerange)

from core.cadeias import (
    _candidatos_m,
    _divisores_impares_maiores_que_1,
    expoentes_validos_ordens,
    ordens_impares,
    sigma_fecha_em,
    v_p,
    v_q_sigma_direto,
)
from core import omega6 as _o6
from core.motor import I_pp, sigma_pp, sup_pp
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
    ultimos_resolvidos: int = 0        # casos abertos com s = 1 fechados por equação ciclotômica
    candidatos_ultimo: int = 0         # primos U candidatos produzidos por elas
    cor6_ramos: int = 0                # casos abertos partidos pela cota finita de expoente
    cor6_mortos: int = 0               # casos abertos mortos por cota < expoente mínimo
    fecho_total_mortos: int = 0        # nós com todos os expoentes fixos e sem pins (lema)
    splits: int = 0                    # Block 7: near-tight open cases split at B_min
    dead_hi: int = 0                   # Block 7: nodes killed by the hi constraint
    conjuntos_completos: int = 0
    conjuntos_com_primo_grande: int = 0
    assinaturas_testadas: int = 0
    conjuntos: list[tuple[int, ...]] = field(default_factory=list)
    pins: list[tuple[tuple[int, ...], str, tuple[int, ...]]] = field(default_factory=list)
    amigos: list[dict[int, int]] = field(default_factory=list)
    n_pins: int = 0                    # number of pin cases (always counted)
    light: bool = False                # True: do not keep the `conjuntos` and `pins` lists
                                       # (millions of entries in long runs); counters only


ORDEM_BITS = 80           # (r-1) com mais bits: r é "grande" — nunca fatoramos r - 1
FATORA_BITS = 90          # acima disto, factorint do sympy pode nao terminar
GRAU_PHI_MAX = 200        # cyclotomic_poly(d, q) com phi(d) > isto e proibitivo
PIN_BITS = 20000          # Phi_d(q) com mais bits que isto nao e testado (gate exato)
CACHE_MAX = 1 << 16       # bound of every memo cache (long runs must not grow without limit)
SOLVER_BITS = 60_000      # last-unknown solver declines when Phi_ell(U_max) has more bits than this
MAX_INDEX_SPAN = 2 * 10**8  # the index enumeration refuses (NaoCertificavel) wider intervals
R_MAX_PROP9 = 1_000_000   # Prop. 9 custa O(r) exponenciacoes por nivel: acima disto, nao se aplica
R_CHEAP_PROP9 = 2_000     # Cor. 6 bounds for r above this are computed only when no cheaper one exists
LIMIAR_INDICE = 300       # intervalos do indice com ate isto primos sao enumerados; alem, Cor. 6
_PEQUENOS = None


def _primos_pequenos() -> list[int]:
    global _PEQUENOS
    if _PEQUENOS is None:
        from sympy import primerange
        _PEQUENOS = list(primerange(2, 100_000))
    return _PEQUENOS


_LIMITE_PEQUENOS = 100_000


_PRIMORIAL = None


def _primorial_pequeno() -> int:
    """Produto de todos os primos < 10^5 (~144 000 bits), para achar de uma vez os
    fatores pequenos de um valor por gcd (uma divisao longa no lugar de 9 592
    modulos)."""
    global _PRIMORIAL
    if _PRIMORIAL is None:
        from math import prod
        _PRIMORIAL = prod(_primos_pequenos())
    return _PRIMORIAL


@lru_cache(maxsize=CACHE_MAX)
def _divisao_pequena(valor: int) -> tuple[tuple[int, ...], int]:
    """(primos < 10^5 de valor, cofator sem eles). O cofator e 1, primo, potencia
    de primo ou composto com todos os primos > 10^5. g = gcd(valor, primorial) e
    o produto dos primos pequenos de valor (sem multiplicidade); fatora-se g (so
    primos < 10^5: factorint e imediato) e tiram-se esses primos de valor.
    Cache: o mesmo Phi_d(q) e consultado em muitos nos."""
    g = gcd(valor, _primorial_pequeno())
    if g == 1:
        return (), valor
    peq = sorted(int(q) for q in factorint(g))
    c = valor
    for q in peq:
        while c % q == 0:
            c //= q
    return tuple(peq), c


@lru_cache(maxsize=CACHE_MAX)
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


@lru_cache(maxsize=CACHE_MAX)
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


@lru_cache(maxsize=CACHE_MAX)
def _phi_valor(d: int, q: int) -> int | None:
    """Phi_d(q) inteiro, ou None se o grau phi(d) excede GRAU_PHI_MAX ou o valor
    excede PIN_BITS bits (gates exatos e deterministicos). Cache: o mesmo par
    (d, q) e consultado em muitos nos."""
    from sympy import totient
    if int(totient(d)) > GRAU_PHI_MAX:
        return None
    fat = factorint(d)
    if len(fat) == 1:
        # d = ell^j: Phi_{ell^j}(q) = Phi_ell(q^{ell^{j-1}}) = (q^{ell^j} - 1)/(q^{ell^{j-1}} - 1)
        (ell, j), = fat.items()
        base = q ** (ell ** (j - 1))
        val = (base**ell - 1) // (base - 1)
    else:
        val = int(cyclotomic_poly(d, q))
    if val.bit_length() > PIN_BITS:
        return None
    return val


def _coprime_base(nums: list[int]) -> list[int]:
    """Pairwise coprime integers > 1 with the same set of prime divisors as prod(nums)
    (gcd refinement: {a, b} with g = gcd > 1 is replaced by {g, a/g, b/g}; the total
    product strictly decreases, so the loop ends)."""
    base: list[int] = []
    stack = [n for n in nums if n > 1]
    while stack:
        a = stack.pop()
        if a == 1:
            continue
        for i, b in enumerate(base):
            g = gcd(a, b)
            if g > 1:
                base.pop(i)
                stack.extend(x for x in (g, a // g, b // g) if x > 1)
                break
        else:
            base.append(a)
    return base


def _residue_unknowns(restos: list[int], pins: set[int]) -> tuple[set[int], int]:
    """Unfactored residues of DIFFERENT closures may share primes, so they cannot simply
    be counted 2 each. Refine residues and already identified pins into a coprime
    base: every base element is a product of unknown primes of S, and distinct
    elements have disjoint primes. Returns (pins, extra): the identified primes (the
    given pins plus primes or prime-power bases revealed by the gcds) and the minimum
    number of further unknown primes (2 per base element that is composite and not a
    prime power). The number of unknown primes involved is >= len(pins) + extra."""
    if not restos:
        return set(pins), 0
    out: set[int] = set(pins)
    extra = 0
    for e in _coprime_base(list(restos) + list(pins)):
        tipo, b = _classifica_cofator(e)
        if tipo in ("primo", "potencia"):
            out.add(b)
        elif tipo == "composto":
            extra += 2
    return out, extra


def _novos_de_sigma(p: int, a: int, permitidos: set[int], s: int,
                    sem_fecho: list[int] | None = None,
                    restos: list[int] | None = None) -> tuple[tuple[int, ...], int] | None:
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
            if restos is not None:
                restos.append(resto)     # for the cross-closure refinement of the caller
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


@lru_cache(maxsize=CACHE_MAX)
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


# ---------------------------------------------------------------------------
# Último desconhecido por equações ciclotômicas (Bloco 5)
# ---------------------------------------------------------------------------
#
# Com s = 1 (S = C + {U}), a_U + 1 é ímpar >= 3 e tem um fator primo ell. Então
# Phi_ell(U) | sigma(U^{a_U}) | sigma(N), e todo fator primo de Phi_ell(U) está em
# S + {3}. Um primo q | Phi_ell(U) ou tem ord_q(U) = ell (q ≡ 1 mod ell, q != 3 pois
# ord_3 <= 2, q != U) — logo q em C_ell = {q em C : ell | q - 1} — ou é q = ell
# (não primitivo: U ≡ 1 mod ell, e então v_ell(Phi_ell(U)) = 1 por LTE), e ell tem
# de estar em S + {3}, i.e. ell em C ou ell = 3. Zsygmondy (ell ímpar >= 3, U >= 2:
# sem exceções) dá um primo primitivo r em C_ell, logo ell | r - 1: ell em L(C) =
# {primos ímpares que dividem algum r - 1, r em C}, finito. Assim
#
#     Phi_ell(U) = ell^eps · prod_{q em C_ell} q^{e_q},   eps em {0, 1},
#
# e_q <= v_q(sigma(N)) = a_q (q >= 7). O lado direito percorre um conjunto FINITO
# de vetores quando há cota: U < U_max pelo índice (prod_sup(C) < 9/5) dá
# Phi_ell(U) <= Phi_ell(U_max); ou todos os q em C_ell têm expoente fixo. Para cada
# valor R do lado direito há no máximo um U: U^{ell-1} < Phi_ell(U) < (U+1)^{ell-1},
# logo U = floor(R^{1/(ell-1)}) — raiz inteira exata, sem enumerar primos.
#
# Qual ell: com s = 1 os orçamentos são exatos para U — k5 = v5(a_U+1) se U ≡ 1
# (mod 5) e k3 = v3(a_U+1) se U ≡ 1 (mod 3) (Fato 2). k5 >= 1 => ell = 5 e U ≡ 1
# (mod 5) (eps = 1); senão k3 >= 1 => ell = 3, eps = 1. Com (k5, k3) = (0, 0),
# ell percorre L(C), com eps = 0 forçado para ell em {3, 5} (U ≡ 1 mod ell
# alimentaria ell) e eps em {0, 1} só se ell em C. Um ell basta para a completude
# (a união sobre os ell possíveis cobre todo U); a fase de conjunto completo
# re-verifica tudo o mais.


def _phi_primo(ell: int, u: int) -> int:
    """Phi_ell(u) = (u^ell - 1)/(u - 1) para ell primo e u >= 2."""
    return (u**ell - 1) // (u - 1)


def _cota_indice_U(prod_sup: Fraction) -> int | None:
    """Maior U compatível com o índice: I(U^{a_U}) < U/(U-1) e I(U^{a_U}) >=
    (9/5)/prod_sup, logo U/(U-1) > (9/5)/prod_sup =: 1 + delta, U < 1 + 1/delta.
    None se prod_sup >= 9/5 (sem cota)."""
    delta = _o6.ALVO / prod_sup - 1
    if delta <= 0:
        return None
    return int(1 + 1 / delta)


def _L_de(C: list[int]) -> set[int] | None:
    """Primos ímpares ell com ell | r - 1 para algum r em C; None se C tem primo
    grande (r - 1 sem fatorar: L(C) seria incompleto)."""
    if _grandes(C):
        return None
    out: set[int] = set()
    for r in C:
        out.update(ell for ell in factorint(r - 1) if ell > 2)
    return out


def _solucoes_phi(ell: int, eps: int, C_ell: list[int], R_max: int,
                  exp_max: dict[int, int], lo: int, C_set: set[int]) -> set[int]:
    """Primos U > lo, fora de C, com Phi_ell(U) = ell^eps · prod_{q em C_ell} q^{e_q},
    produto <= R_max e e_q <= exp_max[q] quando q tem expoente fixo."""
    P_max = R_max // ell**eps
    R_min = _phi_primo(ell, int(nextprime(lo)))
    out: set[int] = set()

    def dfs(i: int, P: int) -> None:
        if i == len(C_ell):
            R = P * ell**eps
            if R < R_min:
                return
            u = int(integer_nthroot(R, ell - 1)[0])
            if u >= 2 and _phi_primo(ell, u) == R and u > lo and u not in C_set and isprime(u):
                out.add(u)
            return
        q = C_ell[i]
        emax = exp_max.get(q)
        e = 0
        Pq = P
        while Pq <= P_max and (emax is None or e <= emax):
            dfs(i + 1, Pq)
            Pq *= q
            e += 1

    dfs(0, 1)
    return out


def _ultimo_desconhecido(C: list[int], lo: int, fixos: dict[int, int], k5: int, k3: int,
                         prod_sup: Fraction, hi: int | None = None) -> list[int] | None:
    """Candidatos finitos para o único desconhecido U num caso aberto (k5, k3);
    None se nenhuma cota limita o lado direito (prod_sup >= 9/5 com expoente livre
    em C_ell, ou L(C) incompleto por primo grande). Block 7: with hi set, U <= hi is
    one more bound on U (the only one when prod_sup >= 9/5)."""
    C_set = set(C)
    U_max = _cota_indice_U(prod_sup)
    if hi is not None:
        U_max = hi if U_max is None else min(U_max, hi)

    def resolve(ell: int, epss: list[int]) -> set[int] | None:
        C_ell = [q for q in C if (q - 1) % ell == 0]
        # size gate: Phi_ell of the bounds would have too many bits (large ell): decline
        # the WHOLE solver (skipping one ell would lose cases); the caller goes on
        if (ell - 1) * max(lo.bit_length(), (U_max or 2).bit_length()) > SOLVER_BITS:
            return None
        if U_max is not None:
            R_max = _phi_primo(ell, U_max)
        elif C_ell and all(q in fixos for q in C_ell):
            R_max = ell ** max(epss)
            for q in C_ell:
                R_max *= q ** fixos[q]
        else:
            return None
        out: set[int] = set()
        for eps in epss:
            out |= _solucoes_phi(ell, eps, C_ell, R_max, fixos, lo, C_set)
        return out

    if k5 >= 1:
        r = resolve(5, [1])
        return None if r is None else sorted(r)
    if k3 >= 1:
        r = resolve(3, [1])
        return None if r is None else sorted(r)
    L = _L_de(C)
    if L is None:
        return None
    cands: set[int] = set()
    for ell in sorted(L):
        if ell in (3, 5):
            epss = [0]
        else:
            epss = [0, 1] if ell in C_set else [0]
        r = resolve(ell, epss)
        if r is None:
            return None
        cands |= r
    return sorted(cands)


# ---------------------------------------------------------------------------
# Cota FINITA para o expoente de um primo conhecido (Bloco 6): Corolário 6 e
# Proposição 9 de Thackeray (arXiv:2310.15900), re-derivados na nossa notação.
# ---------------------------------------------------------------------------
#
# Para r em S (r != 3):  v_r(sigma(N)) = a_r - v_r(num) + v_r(den)   [sigma(N) = num·N/den],
# e v_r(sigma(N)) = soma_{q em S, q != r} v_r(sigma(q^{a_q})). Com a_q par e o = ord_r(q)
# (LTE):  contribuicao = v_r(a_q + 1)                       se o = 1 (q ≡ 1 mod r);
#                      = w_r(q) + v_r((a_q + 1)/o)          se o impar > 1 e o | a_q + 1;
#                      = 0                                  caso contrario (o par, ou o ∤ a_q+1),
# onde w_r(q) = v_r(q^o - 1) >= 1 e o "nivel de Wieferich" de q em r.
#
# NIVEIS. Se r^j | (a_q + 1)/o (j = 1..v), entao Phi_{r^j o}(q) | sigma(q^{a_q}) | sigma(N)
# tem primo primitivo t_j (Zsygmondy: r^j o impar >= 3, sem excecao) com
# ord_{t_j}(q) = r^j o, logo t_j ≡ 1 (mod r^j), t_j em S \ {q, r} (t_j != 3: ord_3 <= 2;
# t_j != r: ord_r(q) = o < r^j o), e niveis distintos tem testemunhas DISTINTAS.
# Com W_j = {t em C \ {r, q} : r^j | t - 1} (encaixados) e os desconhecidos como
# coringas, o nivel maximo e o maior v com |W_j| + (#coringas) >= v - j + 1 para todo
# j <= v (condicao de Hall para conjuntos encaixados).
#
# WIEFERICH (Prop. 9). Para q ≢ 1 (mod r): w_r(q) >= a  <=>  q^{r-1} ≡ 1 (mod r^a)
# [(Z/r^a)^* e ciclico de ordem r^{a-1}(r-1); ord_{r^a}(q) = o·r^i, e q^o ≡ 1 sse i = 0
# sse ord | r - 1 sse q^{r-1} ≡ 1]  <=>  q ≡ y^{r^{a-1}} (mod r^a) para algum y em
# 2..r-1 (os r - 1 elementos do subgrupo de ordem r - 1 sao as imagens de y = 1..r-1,
# distintas mod r; y = 1 da 1, excluido pois q ≢ 1 mod r). Logo q >= m_a(r) :=
# min_y (y^{r^{a-1}} mod r^a), e q < m_a(r) implica w_r(q) <= a - 1. Para os
# desconhecidos basta uma cota L sobre todos eles. Para conhecidos, w_r(q) e exato
# (pow(q, r-1, r^a)); nada exige fatorar r - 1 (ordem impar? q^{parte impar de r-1} ≡ 1).
#
# COTA L PARA OS DESCONHECIDOS (indice nivel a nivel). No nivel com t desconhecidos
# restantes e conhecidos C': sup(U)^t > R := (9/5)/prod_sup(C') para o menor U, e
# (U/(U-1))^t <= exp(t/(U-1)) e ln R >= (R-1)/R com R < 2 dao U < 1 + 2t/(R - 1).
# ATENCAO (buraco fechado no Bloco 6): o nivel seguinte so tem cota se R' > 1, i.e.
# U > B_min = 1 + 1/(R-1); com s = 2 a cota L so vale se lo >= B_min, e com s >= 3
# nao e usada (cada nivel exigiria a mesma condicao).
# Alem disso R - 1 = (inteiro positivo)/D(C') com D(C') = 5·sigma(5^{a1})·prod_{q livre} q·
# prod_{q fixo != 5} sigma(q^{a_q}) (ou 5·prod q com a1 livre), logo R - 1 >= 1/D(C') e, no
# nivel seguinte, D cresce no maximo pelo fator L_anterior. Recursao exata em inteiros;
# L = cota do ultimo.
# COTA: a_r <= v_r(den) - v_r(num) + soma_{q fixo} v_r(sigma(q^{a_q}))
#            + soma_{q livre conhecido, o impar} [w_r(q)·[o > 1] + nivel_max(q)]
#            + s · (omega_max(r, L) + nivel_max(desconhecido)).
# Com a cota A_r finita a cauda de r desaparece: a_r percorre {min_r, ..., A_r} pares,
# e cada ramo fecha sigma(r^{a_r}) em S + {3} (pins). Cota < min_r: caso morto.


_TEICH_MIN: dict[int, list[int]] = {}      # r -> [m_2(r), m_3(r), ...] computed so far


def _teich_minima(r: int, niveis: int | None = None, L: int | None = None) -> list[int]:
    """Minima m_2(r), m_3(r), ... of the Teichmuller lifts, m_a(r) = min_{y=2..r-1}
    (y^{r^{a-1}} mod r^a), computed incrementally: if x ≡ y^{r^{a-1}} (mod r^a) then
    x^r ≡ y^{r^a} (mod r^{a+1}) (binomial expansion of (y^{r^{a-1}} + t·r^a)^r), so one
    exponentiation by r per residue and per level suffices. Each lift is congruent
    mod r^a to the previous one, hence m_a(r) is non-decreasing in a. Extends the
    cached list until it has `niveis` entries or its last entry exceeds L. Only the
    minima are cached (the r - 2 lifts are temporary)."""
    mins = _TEICH_MIN.get(r, [])

    def falta() -> bool:
        if niveis is not None and len(mins) < niveis:
            return True
        return L is not None and (not mins or mins[-1] <= L)

    if not falta():
        return mins
    lifts = list(range(2, r))
    mod = r
    novos: list[int] = []
    while True:
        mod *= r
        lifts = [pow(x, r, mod) for x in lifts]
        novos.append(min(lifts))
        mins = novos if len(novos) >= len(mins) else mins
        if len(novos) >= len(_TEICH_MIN.get(r, [])) and not falta():
            break
    _TEICH_MIN[r] = mins
    return mins


def _min_residuo_teichmuller(r: int, a: int) -> int:
    """m_a(r) = min_{y = 2..r-1} (y^{r^{a-1}} mod r^a), a >= 2."""
    return _teich_minima(r, niveis=a - 1)[a - 2]


def _nivel_wieferich_max(r: int, L: int) -> int | None:
    """Maior w_r(q) possivel para um primo q <= L com q ≢ 1 (mod r); None se r e
    grande demais para a Prop. 9 (custo O(r) por nivel). w_r(q) >= a implica
    q >= m_a(r); logo, se a e o menor nivel com m_a(r) > L, w_r(q) <= a - 1."""
    if r > R_MAX_PROP9:
        return None
    mins = _teich_minima(r, L=L)
    for i, m in enumerate(mins):
        if m > L:
            return i + 1               # a = i + 2 is the first level with m_a > L
    raise AssertionError("teichmuller minima not extended past L")


def _nivel_max(W: list[int], coringas: int) -> int:
    """Maior v com W[j] + coringas >= v - j + 1 para todo 1 <= j <= v (W[0] nao usado;
    W[j] = 0 alem do fim)."""
    v = 0
    while True:
        cand = v + 1
        if all((W[j] if j < len(W) else 0) + coringas >= cand - j + 1 for j in range(1, cand + 1)):
            v = cand
        else:
            return v


_INHERIT = "inherit"      # Case.hi sentinel: apply the inheritance rule of Block 7


def _virtual(hi: int) -> Fraction:
    """v(hi) = 1 + 1/hi + 1/hi^2: lower bound for I(U^a) when U <= hi (a >= 2)."""
    return Fraction(hi * hi + hi + 1, hi * hi)


def _first_live_q(prod_min: Fraction) -> int:
    """Least integer q >= 2 with prod_min · v(q) <= 9/5 (v(q) = 1 + 1/q + 1/q^2), for
    prod_min < 9/5. Every smaller q has prod_min · I(q^2) > 9/5, so a child of the index
    enumeration with that q as a new prime is dead (v decreases with q). Exact: with
    x = (9/5)/prod_min - 1 = a/b the condition is a·q^2 - b·q - b >= 0."""
    x = _o6.ALVO / prod_min - 1
    a, b = x.numerator, x.denominator
    q = max(2, (b + isqrt(b * b + 4 * a * b)) // (2 * a))
    while a * q * q - b * q - b < 0:
        q += 1
    while q > 2 and a * (q - 1) * (q - 1) - b * (q - 1) - b >= 0:
        q -= 1
    return q


def _long_interval(lo: int, top: int) -> bool:
    """Does (lo, top] hold more than LIMIAR_INDICE primes? STRATEGY ONLY: the answer
    selects between sound alternatives (enumerate the interval, or branch/split), so a
    crude shortcut for wide intervals is harmless."""
    if top <= lo:
        return False
    if top - lo > 64 * LIMIAR_INDICE:
        return True
    n = 0
    for _ in primerange(lo + 1, top + 1):
        n += 1
        if n > LIMIAR_INDICE:
            return True
    return False


def _cota_L_desconhecidos(C: list[int], s: int, fixos: dict[int, int],
                          minimos: dict[int, int],
                          maximos: dict[int, int] | None = None,
                          hi: int | None = None,
                          lo: int | None = None) -> tuple[int, int, int | None] | None:
    """(L1, B_min, L). L1 bounds the smallest unknown (index; also <= hi if set).
    B_min = floor(1 + 1/(R-1)) is the largest integer U with prod_sup·sup(U) >= 9/5:
    children with U_1 <= B_min have NO index bound for the other unknowns. L bounds
    ALL the unknowns and exists only when that cannot happen:
      s = 1: L = L1;
      s = 2 and lo >= B_min: U_1 >= U_min, the least prime > lo outside C, so
         R' = R·(U_1 - 1)/U_1 >= R'_min := R·(U_min - 1)/U_min > 1 (U_min > B_min), and
         the last unknown has sup(U_2) > R' (from 9/5 < prod_sup·sup(U_1)·sup(U_2)),
         i.e. U_2 < 1 + 1/(R' - 1) <= 1 + 1/(R'_min - 1);
      otherwise None (s = 2 with lo < B_min or lo unknown; s >= 3 would need the same
      condition at every level).
    Block 6 used 1 + 2·b·L1 for s = 2 (b = reduced denominator of R - 1): valid, but b
    is astronomically large once exponents are fixed or bounded, which made the
    Wieferich levels of Prop. 9 both useless and slow. None if prod_sup >= 9/5."""
    _, prod_sup = _prod_min_sup(C, fixos, minimos, maximos)
    R = _o6.ALVO / prod_sup
    if R <= 1:
        return None
    L1 = int(1 + 2 * s / (R - 1))
    if hi is not None:
        L1 = min(L1, hi)                # Block 7: the smallest unknown is also <= hi
    # filho com o menor desconhecido U: R' = R·(U-1)/U > 1  <=>  U > R/(R-1) = 1 + 1/(R-1)
    B_min = int(1 + 1 / (R - 1))
    if s == 1:
        return L1, B_min, L1
    if s == 2 and lo is not None and lo >= B_min:
        U = lo
        while True:
            U = int(nextprime(U))
            if U not in C:
                break
        R_min = R * Fraction(U - 1, U)   # > 1 because U > B_min
        return L1, B_min, int(1 + 1 / (R_min - 1))
    return L1, B_min, None


def _cap_nivel(r: int, M: int | None) -> int | None:
    """v_r(a_q + 1) <= floor(log_r(M + 1)) quando a_q <= M."""
    if M is None:
        return None
    j = 0
    while r ** (j + 1) <= M + 1:
        j += 1
    return j


def _cota_expoente_conhecido(r: int, C: list[int], s: int, fixos: dict[int, int],
                             L: int | None, maximos: dict[int, int] | None = None) -> int | None:
    """Cota A_r >= a_r (Cor. 6) para r em C livre; None se nao computavel."""
    maximos = maximos or {}
    num, den = _o6.ALVO.numerator, _o6.ALVO.denominator
    total = v_p(r, den) - v_p(r, num)          # a_r = v_r(sigma(N)) - v_r(num) + v_r(den)
    # testemunhas conhecidas por nivel: W[j] = #{t em (C ∪ extras) \ {r} : r^j | t - 1}
    # (extras = primos de num: no alvo real so o 3, que nunca e ≡ 1 mod r^j)
    extras = _o6._parametros_do_alvo()[0]
    pool = sorted(set(C) | set(extras))
    W = [0]
    j = 1
    while True:
        rj = r ** j
        cnt = sum(1 for t in pool if t != r and (t - 1) % rj == 0)
        W.append(cnt)
        if cnt == 0:
            break
        j += 1
    m_impar = r - 1
    while m_impar % 2 == 0:
        m_impar //= 2
    for q in C:
        if q == r:
            continue
        if q in fixos:
            total += v_q_sigma_direto(r, q, fixos[q])
            continue
        cap = _cap_nivel(r, maximos.get(q))            # niveis <= log_r(max_q + 1)
        if q % r == 1:
            Wq = [0] + [W[jj] - (1 if (q - 1) % r**jj == 0 else 0) for jj in range(1, len(W))]
            niv = _nivel_max(Wq, s)
            total += niv if cap is None else min(niv, cap)
            continue
        if pow(q, m_impar, r) != 1:
            continue                                   # ordem par: nunca alimenta r
        w = 1
        while pow(q, r - 1, r ** (w + 1)) == 1:
            w += 1
        niv = _nivel_max(W, s)
        total += w + (niv if cap is None else min(niv, cap))
    if s:
        if L is None:
            return None
        om = _nivel_wieferich_max(r, L)
        if om is None:
            return None
        total += s * (om + _nivel_max(W, s - 1))
    return total


def _ramos_cor6(C: list[int], s: int, lo: int, fixos: dict[int, int],
                minimos: dict[int, int],
                maximos: dict[int, int] | None = None,
                hi: int | None = None) -> list[Ramo] | None:
    """Ramificação EXATA pela cota finita de expoente (Bloco 6): escolhe o primo
    conhecido livre com menos ramos. As cotas calculadas para TODOS os livres são
    fatos sobre o amigo (valem em todo descendente) e vão para `maximos` dos
    filhos — só melhoradas, nunca pioradas (a cota L recomputada num filho com
    expoentes grandes fixos é bem mais frouxa). [] = caso morto (cota < expoente
    mínimo); None = não se aplica (sem cota L, sem primo livre, intervalo do índice
    curto, Prop. 9 fora do orçamento)."""
    maximos = maximos or {}
    livres = [r for r in C if r not in fixos]
    if not livres:
        return None
    cotas = _cota_L_desconhecidos(C, s, fixos, minimos, maximos, hi, lo)
    if cotas is None:
        return None
    L1, B_min, L = cotas
    if L is None or lo < B_min:
        return None            # algum desconhecido pode ficar sem cota de indice: sem L
    if not _long_interval(lo, L1):
        return None                                    # o índice resolve barato
    novos_max = dict(maximos)
    melhor: tuple[int, int, int] | None = None
    # cheap primes first: the Prop. 9 term costs O(r) per level, and exact branches of
    # small primes mostly die at once in this regime (their pins would have to be > lo);
    # the bounds of expensive primes are computed only if no cheap prime can be branched
    for grupo in ([r for r in livres if r <= R_CHEAP_PROP9],
                  [r for r in livres if r > R_CHEAP_PROP9]):
        for r in grupo:
            A = _cota_expoente_conhecido(r, C, s, fixos, L, maximos)
            if A is not None and (r not in novos_max or A < novos_max[r]):
                novos_max[r] = A
        for r in grupo:
            if r not in novos_max:
                continue
            A = novos_max[r]
            amin = minimos.get(r, 2)
            if A < amin:
                return []                              # morto: r não tem expoente possível
            n = (A - amin) // 2 + 1
            if melhor is None or n < melhor[0]:
                melhor = (n, r, A)
        if melhor is not None:
            break
    if melhor is None:
        return None
    _, r, A = melhor
    amin = minimos.get(r, 2)
    return [({**fixos, r: a}, minimos, novos_max) for a in range(amin, A + 1, 2)]


def _prod_min_sup(C: list[int], fixos: dict[int, int], minimos: dict[int, int],
                  maximos: dict[int, int] | None = None) -> tuple[Fraction, Fraction]:
    """(prod_min, prod_sup) dos conhecidos: I(p^{a_p}) exato se fixo, senão
    [I(p^{min_p}), sup] com min_p = minimos.get(p, 2) e sup = I(p^{max_p}) se p tem
    cota superior em maximos (atingível), senão p/(p-1) (não atingível)."""
    maximos = maximos or {}
    prod_min = Fraction(1)
    prod_sup = Fraction(1)
    for p in C:
        if p in fixos:
            x = I_pp(p, fixos[p])
            prod_min *= x
            prod_sup *= x
        else:
            prod_min *= I_pp(p, minimos.get(p, 2))
            prod_sup *= I_pp(p, maximos[p]) if p in maximos else sup_pp(p)
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
        restos: list[int] = []     # unfactored residues (each has >= 2 unknown primes)
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
                    restos.append(resto)
                elif not novos and j in faltam:
                    return             # impossivel (Zsygmondy exige primitivo novo)
                pins |= set(novos)
        # residues of different closures may share primes: coprime-base refinement
        pins, extra = _residue_unknowns(restos, pins)
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


Ramo = tuple[dict[int, int], dict[int, int], dict[int, int]]   # (fixos, minimos, maximos)


def _ramos_expoente(C: list[int], fixos: dict[int, int], minimos: dict[int, int],
                    maximos: dict[int, int] | None = None,
                    hi: int | None = None) -> list[Ramo] | None:
    """Ramificação por expoente com cauda (passo 4 do cabeçalho). None sse
    prod_sup <= 9/5 (nenhuma cauda mata; o índice é o caminho). Com cota superior
    M_q (maximos) o ganho de q é I(q^{M_q})/I(q^{min_q}) e a cauda a_q >= A só existe
    se A <= M_q (senão os ramos exatos até M_q já cobrem tudo).
    Block 7: with hi set, the constant virtual factor v(hi) multiplies prod_min and
    prod_sup (I(N) >= prod_min·v(hi)); the construction is otherwise unchanged."""
    maximos = maximos or {}
    prod_min, prod_sup = _prod_min_sup(C, fixos, minimos, maximos)
    if hi is not None:
        v = _virtual(hi)
        prod_min *= v
        prod_sup *= v
    if prod_sup <= _o6.ALVO:
        return None
    if prod_min > _o6.ALVO:
        return []      # dead: I(N) >= prod_min (· v(hi)) > 9/5 (the caller has s >= 1)
    livres = [p for p in C if p not in fixos]

    def topo(p: int) -> Fraction:
        return I_pp(p, maximos[p]) if p in maximos else sup_pp(p)

    ganhos = sorted(livres, key=lambda p: topo(p) / I_pp(p, minimos.get(p, 2)), reverse=True)
    acc = prod_min
    for q in ganhos:
        base = acc                                   # prod_min · ganhos anteriores
        amin = minimos.get(q, 2)
        acc *= topo(q) / I_pp(q, amin)
        if acc <= _o6.ALVO:
            continue
        # q = q_m: base <= ALVO (minimalidade) e base·topo(q)/I(q^{amin}) > ALVO
        fator = base / I_pp(q, amin)
        M = maximos.get(q)
        exatos: list[int] = []
        a = amin
        while fator * I_pp(q, a) <= _o6.ALVO and (M is None or a <= M):
            exatos.append(a)                         # termina: fator·I(q^a) -> acc > ALVO
            a += 2
        ramos: list[Ramo] = [({**fixos, q: e}, minimos, maximos) for e in exatos]
        if M is None or a <= M:
            ramos.append((fixos, {**minimos, q: a}, maximos))    # cauda a_q >= a
        return ramos                                  # [] = morto (sem expoente possível)
    raise AssertionError("prod_sup > ALVO mas nenhum prefixo de ganhos excede o alvo")


class Case(NamedTuple):
    """One child of a partition. `lo` overrides the node's lo when not None; `hi` is
    _INHERIT (inheritance rule of Block 7), None (drop) or an integer (set)."""
    pins: tuple[int, ...]
    fixos: dict[int, int]
    minimos: dict[int, int]
    maximos: dict[int, int]
    lo: int | None = None
    hi: object = _INHERIT


def _split_cases(C: list[int], s: int, lo: int, fixos: dict[int, int],
                 minimos: dict[int, int], maximos: dict[int, int],
                 hi: int | None) -> list[tuple[tuple[int, ...], int | None, object]] | None:
    """B_min split (Block 7, step 6): list of (pins, lo override, hi override) for the
    cases (a) U_1 <= B-1, (a2) U_1 = B, (b) U_1 > B. None = not applicable (s < 2, no
    index bound, lo >= B-1, no progress on hi, or a short index interval that is
    cheaper to enumerate)."""
    if s < 2:
        return None
    _, prod_sup = _prod_min_sup(C, fixos, minimos, maximos)
    if prod_sup >= _o6.ALVO:
        return None
    R = _o6.ALVO / prod_sup
    B = int(1 + 1 / (R - 1))                      # floor (exact rational arithmetic)
    if not lo < B - 1:
        return None
    if hi is not None and not B - 1 < hi:
        return None
    L1 = int(1 + 2 * s / (R - 1))
    if not _long_interval(lo, L1 if hi is None else min(hi, L1)):
        return None
    cases: list[tuple[tuple[int, ...], int | None, object]] = [((), None, B - 1)]   # (a)
    if B not in C and isprime(B) and (hi is None or B <= hi):                       # (a2)
        cases.append(((B,), B, None))
    if hi is None or hi > B:                                                        # (b)
        cases.append(((), B, _INHERIT))
    return cases


def _particao(C: list[int], s: int, lo: int, stats: StatsK,
              fixos: dict[int, int], minimos: dict[int, int],
              maximos: dict[int, int] | None = None,
              hi: int | None = None) -> list[Case]:
    """Partição completa de casos do nó: lista de Case (pins, fixos, minimos,
    maximos, lo/hi overrides) do filho. Levanta NaoCertificavel se algum par
    (caso5, caso3) fica aberto sem ramo."""
    if _o6.ALVO != Fraction(9, 5):
        raise NaoCertificavel("particao por orcamentos e especifica do alvo 9/5")
    maximos = maximos or {}
    stats.particoes += 1
    permitidos = set(C) | {3}
    resultado: list[Case] = []

    def registra(pins: tuple[int, ...], f: dict[int, int], m: dict[int, int],
                 mx: dict[int, int], rotulo: str, lo_new: int | None = None,
                 hi_new: object = _INHERIT) -> None:
        caso = Case(pins, f, m, mx, lo_new, hi_new)
        if caso not in resultado:
            resultado.append(caso)
            if pins:
                stats.n_pins += 1
                if not stats.light:
                    stats.pins.append((tuple(C), rotulo, pins))

    sem_fecho = [0]

    # 1. fecho dos expoentes comprometidos (um fecho fora do orçamento é apenas
    #    informação a menos: o passo segue com os outros)
    pins_fixos: set[int] = set()
    restos_fixos: list[int] = []
    for p, a in fixos.items():
        r = _novos_de_sigma(p, a, permitidos | pins_fixos, s - len(pins_fixos), sem_fecho,
                            restos_fixos)
        if r is None:
            return []                       # morto
        pins_fixos |= set(r[0])
    # the total-closure lemma below needs EVERY cyclotomic piece of every fixed prime
    # examined: a piece skipped by the gates of _phi_valor may hide a new prime
    fecho_fixos_completo = sem_fecho[0] == 0
    # residues of different fixed primes may share primes: coprime-base refinement
    # (coprime residues add up; a common factor is revealed by the gcd)
    pins_fixos, extra_fixos = _residue_unknowns(restos_fixos, pins_fixos)
    if len(pins_fixos) + extra_fixos > s:
        return []                           # morto
    if pins_fixos:
        if min(pins_fixos) <= lo:
            return []                       # morto
        registra(tuple(sorted(pins_fixos)), fixos, minimos, maximos, "fixos=" + ",".join(
            f"{p}^{a}" for p, a in sorted(fixos.items())))
        return resultado
    # LEMA DO FECHO TOTAL: todos os expoentes conhecidos fixos, nenhum sigma(q^{a_q})
    # com primo fora de C + {3} (nem resto sem fatorar, nem peça pulada): cada desconhecido U so
    # divide sigma's de desconhecidos, logo prod_U sigma(U^{a_U}) = (prod_U U^{a_U})·K
    # com K inteiro sobre C + {3}, e x = ALVO / prod_C I(q^{a_q}) = prod_U I(U^{a_U}) = K
    # seria inteiro; morto se x nao e inteiro (no alvo 9/5, 1 < x < 9/5).
    if s >= 1 and extra_fixos == 0 and fecho_fixos_completo and all(q in fixos for q in C):
        x = _o6.ALVO / _prod_min_sup(C, fixos, minimos, maximos)[0]
        if x.denominator != 1:
            stats.fecho_total_mortos += 1
            return []                       # morto

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
            registra(dado5, f1, minimos, maximos, f"a1={a1}")
            continue
        for tipo3, dado3 in casos3:
            if tipo3 == "pin":
                registra(dado3, f1, minimos, maximos, f"a1={a1}:v3")
                continue
            # ambos abertos
            if s == 1 and dado5 is not None and dado3 is not None:
                if (dado5, dado3) != (0, 0) and not _viavel_m0(dado5, dado3, C):
                    continue  # morto: a_U+1 exigiria ordens que C não oferece
                # 3. último desconhecido por equação ciclotômica (Bloco 5)
                cands = _ultimo_desconhecido(C, lo, f1, dado5, dado3,
                                             _prod_min_sup(C, f1, minimos, maximos)[1], hi)
                if cands is not None:
                    stats.ultimos_resolvidos += 1
                    stats.candidatos_ultimo += len(cands)
                    for U in cands:
                        registra((U,), f1, minimos, maximos,
                                 f"a1={a1}:ultimo(k5={dado5},k3={dado3})")
                    continue
            # 4. ramificação por expoente com cauda
            ramos = _ramos_expoente(C, f1, minimos, maximos, hi)
            if ramos is None:
                # 5. cota finita de expoente (Bloco 6) quando o índice degeneraria
                ramos6 = _ramos_cor6(C, s, lo, f1, minimos, maximos, hi)
                if ramos6 is not None:
                    if not ramos6:
                        stats.cor6_mortos += 1
                        continue                       # morto
                    stats.cor6_ramos += 1
                    for f2, m2, mx2 in ramos6:
                        registra((), f2, m2, mx2, "")
                    continue
                # 6. B_min split (Block 7) when the index interval of U_1 is long
                split = _split_cases(C, s, lo, f1, minimos, maximos, hi)
                if split is not None:
                    stats.splits += 1
                    for pins_s, lo_s, hi_s in split:
                        registra(pins_s, f1, minimos, maximos, f"a1={a1}:split", lo_s, hi_s)
                    continue
                if f1 != fixos:
                    # a1 recém-fixado e prod_sup(f1) <= 9/5: o filho (mesmo nó com
                    # a1 fixo) cai no fallback pelo índice
                    registra((), f1, minimos, maximos, "")
                else:
                    abertos.append(f"a1={a1}:k5={dado5},k3={dado3}")
                continue
            stats.ramos_expoente += 1
            for f2, m2, mx2 in ramos:
                if m2 is not minimos:
                    stats.caudas += 1
                registra((), f2, m2, mx2, "")
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
    return [caso.pins for caso in _particao(C, s, lo, stats, fixos, {}, {}) if caso.pins]


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
                      fixos: dict[int, int], minimos: dict[int, int],
                      maximos: dict[int, int] | None = None) -> list[list[int]] | None:
    """Listas de expoentes válidos por primo do conjunto completo C (restritas aos
    fixos e aos minimos), ou None se alguma é vazia (conjunto morto). Sem primo grande:
    expoentes_validos_ordens (idêntico ao Bloco 2). Com UM primo grande r: r
    primeiro (ordens de r módulo primos pequenos), depois os outros por
    _expoentes_com_primo_grande."""
    fs = frozenset(C)

    maximos = maximos or {}

    def restringe(p: int, exps: list[int]) -> list[int]:
        if p in fixos:
            return [a for a in exps if a == fixos[p]]
        return [a for a in exps if minimos.get(p, 2) <= a and (p not in maximos or a <= maximos[p])]

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
               minimos: dict[int, int] | None = None,
               maximos: dict[int, int] | None = None,
               hi: int | None = None) -> None:
    fixos = fixos or {}
    minimos = minimos or {}
    maximos = maximos or {}
    stats.nos += 1
    prod_min, prod_sup = _prod_min_sup(C, fixos, minimos, maximos)

    if hi is not None:
        # Block 7: "s >= 1 and the smallest unknown is <= hi" (and > lo)
        if s == 0 or hi <= lo:
            stats.dead_hi += 1
            return
        U = lo                              # is there any prime in (lo, hi] outside C?
        while True:
            U = int(nextprime(U))
            if U > hi:
                stats.dead_hi += 1
                return
            if U not in C:
                break
        pv = prod_min * _virtual(hi)        # I(N) >= prod_min · v(hi)
        if pv > _o6.ALVO or (s >= 2 and pv == _o6.ALVO):
            stats.dead_hi += 1
            return

    if s == 0:
        # I(N) >= prod_min (igualdade = candidato vivo) e I(N) < prod_sup (estrito
        # se algum expoente é livre; com todos fixos I(N) = prod_min = prod_sup)
        if prod_min > _o6.ALVO or (prod_sup < _o6.ALVO) or (
                prod_sup == _o6.ALVO and any(q not in fixos and q not in maximos for q in C)):
            stats.completos_mortos_indice += 1
            return
        if not stats.light:
            stats.conjuntos.append(tuple(C))
        extras = _o6._parametros_do_alvo()[0]
        listas = _listas_expoentes(C, extras, stats, fixos, minimos, maximos)
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
        casos = _particao(C, s, lo, stats, fixos, minimos, maximos, hi)
    except NaoCertificavel:
        if prod_sup >= _o6.ALVO:
            raise
        casos = None
    if casos is not None:
        for caso in casos:
            if caso.hi == _INHERIT:
                # keep hi unless a pinned prime is <= hi (then U_1 may be that pin)
                filho_hi = hi if (hi is None or not caso.pins or min(caso.pins) > hi) else None
            else:
                filho_hi = caso.hi
            _certifica(sorted(C + list(caso.pins)), s - len(caso.pins),
                       lo if caso.lo is None else caso.lo, stats,
                       caso.fixos, caso.minimos, caso.maximos, filho_hi)
        return

    # FALLBACK pelo índice: o menor desconhecido U > lo, U fora de C, é limitado
    stats.ramo_i += 1
    # skip the dead prefix of the loop: every q < _first_live_q(prod_min) gives a child
    # with prod_min · I(q^2) > 9/5 (the tests below would `continue` on each of them)
    q = max(lo, _first_live_q(prod_min) - 1)
    # no silent multi-day loop: refuse when the interval of the smallest unknown is huge
    # (prod_sup < 9/5 here, so L1 = 1 + 2s/(R-1) bounds it; hi, if set, bounds it too)
    topo = int(1 + 2 * s / (_o6.ALVO / prod_sup - 1))
    if hi is not None:
        topo = min(topo, hi)
    if topo - q > MAX_INDEX_SPAN:
        raise NaoCertificavel(
            f"C={C}, s={s}, fixos={fixos}, hi={hi}: index enumeration over ({q}, {topo}] "
            f"exceeds MAX_INDEX_SPAN = {MAX_INDEX_SPAN}")
    while True:
        q = int(nextprime(q))
        if hi is not None and q > hi:
            return                      # Block 7: the smallest unknown is <= hi
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
        _certifica(sorted(C + [q]), s - 1, q, stats, fixos, minimos, maximos, None)


def certifica_omega(k: int, stats: StatsK | None = None, light: bool = False) -> StatsK:
    """Varre exaustivamente o espaço omega(N) = k. stats.amigos vazio ao retornar
    => NENHUM amigo de 10 tem exatamente k fatores primos distintos. Levanta
    NaoCertificavel (sem certificado) se alguma cobertura não fechar.
    light=True keeps only counters (no lists of complete sets and pins): for long runs."""
    if k < 1:
        raise ValueError("k >= 1")
    stats = stats or StatsK(k=k, light=light)
    stats.k = k
    _certifica([5], k - 1, 5, stats, {}, {}, {}, None)   # Teorema D: 5 é o menor primo
    return stats


__all__ = ["StatsK", "certifica_omega", "NaoCertificavel"]
