"""Certificador RECURSIVO: nenhum amigo de 10 com omega(N) = k (Fase 1, Bloco 3).

Generaliza core/omega6.py para qualquer k. Estado = (C, s, lo):
  C  = primos JÁ CONHECIDOS de S (lista ordenada, sempre contém 5);
  s  = quantos primos de S ainda são desconhecidos;
  lo = cota: todo desconhecido é > lo e não está em C. Invariante: todo primo de S
       que seja <= lo está em C (os desconhecidos são enumerados do menor para o
       maior, e um primo pinado é sempre > lo no momento do pin).

Em cada nó (tudo exato, Fraction/int):
  MORTO   se s >= 1 e prod_{p em C} I(p^2) >= 9/5 (os s fatores restantes são > 1);
  s = 0   conjunto completo -> fase de expoentes (core/omega6._conjunto_completo:
          fecho por ordens + orçamentos v3/v5 + igualdade exata);
  senão   PARTIÇÃO por orçamentos (abaixo): partição completa de casos, válida em
          qualquer nó; cada caso pina >= 1 desconhecido (recorre com s menor) ou
          morre. Se a partição deixa algum caso aberto (NaoCertificavel), o
          fallback é o ÍNDICE: se prod_{p em C} p/(p-1) < 9/5, o MENOR desconhecido
          U é limitado (I(N) < prod_sup(C)·sup(U)·[sups dos s-1 menores primos > U
          fora de C], majoração não-crescente em U com limite prod_sup(C) < 9/5 —
          o laço termina) e recorre com (C + {U}, s-1, lo = U); senão o nó levanta
          NaoCertificavel com o estado residual. Nenhuma lacuna é silenciosa.

PARTIÇÃO POR ORÇAMENTOS (a peça nova do Bloco 3):
  Dois orçamentos EXATOS decorrem de sigma(N) = 9N/5 com 3 ∤ N:
     v5(sigma(N)) = a1 - 1   (a1 = v5(N))      e      v3(sigma(N)) = 2.
  Pelo Fato 2, só bases q ≡ 1 (mod ell) alimentam ell in {3, 5}, com
  v_ell(sigma(q^a)) = v_ell(a+1). Um alimentador q com k = v_ell(a_q+1) tem
  ell^j | a_q+1 para j = 1..k, logo Phi_{ell^j}(q) | sigma(q^{a_q}) | sigma(N):
  TODOS os fatores primos de Phi_{ell^j}(q) estão em S + {3}, então os que não
  estão em C + {3} são desconhecidos — ficam PINADOS (ou o caso morre: mais que s
  primos novos, ou algum <= lo, que pelo invariante estaria em C). Zsygmondy dá
  ainda um primo primitivo r_j ≡ 1 (mod ell^j) em S menos {q} para cada j.

  Cota universal para a1 (ell = 5): cada alimentador U tem v5(a_U+1) <=
  #{r em S menos {U} : r ≡ 1 (mod 5)} <= c5 + s - 1 (os r_j são distintos), com
  c5 = #{q em C : q ≡ 1 (mod 5)}; com no máximo c5 + s alimentadores,
        a1 <= 1 + (c5 + s)(c5 + s - 1)   [finita para qualquer s].
  Para cada a1 par nessa faixa: se sigma(5^{a1}) tem fatores fora de C + {3},
  esses fatores são desconhecidos (pin direto). Senão, distribui-se T = a1 - 1
  entre alimentadores conhecidos (k_q >= 1, pins de Phi_{5^j}(q)) e desconhecidos.
  Para ell = 3, T = 2 fixo: distribui-se do mesmo modo.

  As duas partições são independentes e completas; o nó usa o PRODUTO de casos:
  um par (caso5, caso3) é fechado se algum dos dois pina; se ambos são abertos e
  s = 1, o único desconhecido U precisa de 5^{k5}·3^{k3} | a_U + 1, e todo divisor
  d > 1 de a_U+1 é ord_r(U) para r em C (não há outro desconhecido), logo d | r-1
  para algum r em C — teste finito que mata ou deixa o par aberto. Um a1 escolhido
  é compromisso do ramo (propagado na recursão).

Honestidade estrutural: ou o caso é provadamente morto, ou pina, ou levanta
NaoCertificavel (sem certificado).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from functools import lru_cache

from sympy import cyclotomic_poly, factorint, nextprime

from core import omega6 as _o6
from core.motor import I_pp, sigma_pp, sup_pp
from core.omega6 import NaoCertificavel, _conjunto_completo


@dataclass
class StatsK:
    k: int = 0
    nos: int = 0
    mortos_min: int = 0
    ramo_i: int = 0
    particoes: int = 0
    conjuntos_completos: int = 0
    assinaturas_testadas: int = 0
    conjuntos: list[tuple[int, ...]] = field(default_factory=list)
    pins: list[tuple[tuple[int, ...], str, tuple[int, ...]]] = field(default_factory=list)
    amigos: list[dict[int, int]] = field(default_factory=list)


LIMITE_BITS = 256


@lru_cache(maxsize=None)
def _fatores_sigma_pp(p: int, a: int) -> tuple[int, ...]:
    """Fatores primos distintos de sigma(p^a) (memoizado; independe do alvo e de C).
    Guarda de honestidade: fatorar um inteiro grande poderia travar — recusa acima
    de LIMITE_BITS (nunca ocorre nas faixas usadas pela cota universal)."""
    valor = sigma_pp(p, a)
    if valor.bit_length() > LIMITE_BITS:
        raise NaoCertificavel(
            f"sigma({p}^{a}) tem {valor.bit_length()} bits - fatoracao fora do orcamento"
        )
    return tuple(sorted(factorint(valor)))


@lru_cache(maxsize=None)
def _fatores_phi(d: int, q: int) -> tuple[int, ...]:
    """Fatores primos distintos de Phi_d(q) (memoizado; mesma guarda de bits)."""
    valor = int(cyclotomic_poly(d, q))
    if valor.bit_length() > LIMITE_BITS:
        raise NaoCertificavel(f"Phi_{d}({q}) tem {valor.bit_length()} bits - fora do orcamento")
    return tuple(sorted(factorint(valor)))


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


def _divisores_impares(m: int) -> list[int]:
    return [d for d in range(3, m + 1, 2) if m % d == 0]


def _tem_atribuicao_injetiva(divs: list[int], C: list[int]) -> bool:
    """Existe injeção d -> r (r em C) com d | r - 1? (emparelhamento por backtracking;
    instâncias minúsculas: |divs| <= ~12, |C| <= ~12)."""
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
    injeção {d | m, d > 1} -> C com d | r - 1; em particular m <= max(C) - 1."""
    Cl = list(C)
    teto = max(Cl) - 1
    return tuple(m for m in range(3, teto + 1, 2)
                 if _tem_atribuicao_injetiva(_divisores_impares(m), Cl))


def _viavel_expoente(m: int, C: list[int]) -> bool:
    """Existe a_U + 1 viável (único desconhecido) divisível por m?"""
    return any(mv % m == 0 for mv in _expoentes_viaveis_unico(tuple(C)))


# caso = ("pin", pins) | ("aberto", kU)   kU = exigência ell^kU | a_U+1 sobre o
# desconhecido alimentador (0 = nenhum desconhecido alimenta; None = s >= 2, sem
# reasoning); pins = tupla ordenada de primos novos (todos > lo, no máximo s).
def _casos_ell(C: list[int], s: int, lo: int, ell: int, T: int) -> list[tuple]:
    permitidos = set(C) | {3}
    conhecidos = [q for q in C if q % ell == 1]
    casos: list[tuple] = []

    def fecha(assign: dict[int, int], restante: int) -> None:
        # restante = parte de T carregada por desconhecidos (cada um com k >= 1)
        if restante > 0 and s == 0:
            return  # morto: não há desconhecido para alimentar
        pins: set[int] = set()
        for q, k in assign.items():
            for j in range(1, k + 1):
                novos = [r for r in _fatores_phi(ell**j, q) if r not in permitidos]
                pins |= set(novos)
        if pins:
            if len(pins) > s or min(pins) <= lo:
                return  # morto
            casos.append(("pin", tuple(sorted(pins))))
            return
        if restante == 0:
            casos.append(("aberto", 0))
        elif s == 1:
            casos.append(("aberto", restante))
        else:
            casos.append(("aberto", None))

    def rec(i: int, restante: int, assign: dict[int, int]) -> None:
        if i == len(conhecidos):
            fecha(assign, restante)
            return
        q = conhecidos[i]
        for k in range(0, restante + 1):
            if k:
                assign[q] = k
            rec(i + 1, restante - k, assign)
            if k:
                del assign[q]

    rec(0, T, {})
    return casos


def _particao(C: list[int], s: int, lo: int, stats: StatsK,
              a1_fixo: int | None = None) -> list[tuple[tuple[int, ...], int]]:
    """Partição completa de casos do nó: lista de (pins, a1). Levanta
    NaoCertificavel se algum par (caso5, caso3) fica aberto."""
    if _o6.ALVO != Fraction(9, 5):
        raise NaoCertificavel("particao por orcamentos e especifica do alvo 9/5")
    stats.particoes += 1
    permitidos = set(C) | {3}
    c5 = sum(1 for q in C if q % 5 == 1)
    a1_max = 1 + (c5 + s) * (c5 + s - 1)
    faixa = [a1_fixo] if a1_fixo is not None else range(2, a1_max + 1, 2)

    casos5: list[tuple[int, tuple]] = []
    for a1 in faixa:
        novos = [r for r in _fatores_sigma_pp(5, a1) if r not in permitidos]
        if novos:
            if len(novos) > s or novos[0] <= lo:
                continue  # morto
            casos5.append((a1, ("pin", tuple(novos))))
            continue
        for caso in _casos_ell(C, s, lo, 5, a1 - 1):
            casos5.append((a1, caso))

    casos3 = _casos_ell(C, s, lo, 3, 2)

    resultado: list[tuple[tuple[int, ...], int]] = []
    abertos: list[str] = []

    def registra(pins: tuple[int, ...], a1: int, rotulo: str) -> None:
        if (pins, a1) not in resultado:
            resultado.append((pins, a1))
            stats.pins.append((tuple(C), rotulo, pins))

    for a1, (tipo5, dado5) in casos5:
        if tipo5 == "pin":
            registra(dado5, a1, f"a1={a1}")
            continue
        for tipo3, dado3 in casos3:
            if tipo3 == "pin":
                registra(dado3, a1, f"a1={a1}:v3")
                continue
            # ambos abertos
            if s == 1 and dado5 is not None and dado3 is not None:
                m = 5**dado5 * 3**dado3
                if m > 1 and not _viavel_expoente(m, C):
                    continue  # morto: a_U+1 exigiria ordens que C não oferece
            abertos.append(f"a1={a1}:k5={dado5},k3={dado3}")
    if abertos:
        raise NaoCertificavel(f"C={C}, s={s}: casos abertos {abertos[:4]}")
    return resultado


def _pinagem(C: list[int], s: int, lo: int, stats: StatsK,
             a1_fixo: int | None = None) -> list[tuple[int, ...]]:
    """Compatibilidade: só os pins da partição (na ordem)."""
    return [pins for pins, _ in _particao(C, s, lo, stats, a1_fixo)]


def _certifica(C: list[int], s: int, lo: int, stats: StatsK,
               a1_fixo: int | None = None) -> None:
    stats.nos += 1
    prod_min = Fraction(1)
    prod_sup = Fraction(1)
    for p in C:
        prod_min *= I_pp(p, 2)
        prod_sup *= sup_pp(p)

    if s == 0:
        stats.conjuntos.append(tuple(C))
        _conjunto_completo(C, stats)
        return
    if prod_min >= _o6.ALVO:            # s fatores restantes > 1: I(N) > prod_min >= 9/5
        stats.mortos_min += 1
        return

    fs = frozenset(C)
    try:
        casos = _particao(C, s, lo, stats, a1_fixo)
    except NaoCertificavel:
        if prod_sup >= _o6.ALVO:
            raise
        casos = None
    if casos is not None:
        for pins, a1 in casos:
            _certifica(sorted(C + list(pins)), s - len(pins), lo, stats, a1)
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
        _certifica(sorted(C + [q]), s - 1, q, stats, a1_fixo)


def certifica_omega(k: int, stats: StatsK | None = None) -> StatsK:
    """Varre exaustivamente o espaço omega(N) = k. stats.amigos vazio ao retornar
    => NENHUM amigo de 10 tem exatamente k fatores primos distintos. Levanta
    NaoCertificavel (sem certificado) se alguma cobertura não fechar."""
    if k < 1:
        raise ValueError("k >= 1")
    stats = stats or StatsK(k=k)
    stats.k = k
    _certifica([5], k - 1, 5, stats)   # Teorema D: 5 é o menor primo
    return stats


__all__ = ["StatsK", "certifica_omega", "NaoCertificavel"]
