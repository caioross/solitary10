"""Motor de busca em árvore sobre assinaturas de primos, com poda por racionais exatos.

Contexto (results/FASE_0.md): um amigo N de 10 satisfaz 5·σ(N) = 9·N, é quadrado
ímpar, todo primo divisor é >= 5 com 5 | N (Teoremas A-D, [PROVADO]), logo
N = ∏ p_i^{a_i} com 5 = p_1 < p_2 < ... < p_k e todo a_i PAR >= 2.

Este módulo certifica enunciados da forma "não existe amigo de 10 com ω(N) = k"
(e a variante limitada "... com N <= bound") por busca exaustiva finita com três
mecanismos, todos exatos (int/Fraction):

  PODA-MIN  Se ∏_{p escolhido} I(p²) >= 9/5 e ainda faltam primos, todo completamento
            tem I > 9/5 (expoentes >= 2, I(p^a) crescente em a, e cada fator de primo
            extra é > 1). Ramo morto.
  PODA-MAX  I(N) < ∏_{p em N} p/(p-1) (estrito, Lema 3 da Fase 0). Majorando os primos
            restantes pelos menores primos ainda disponíveis (trocar um primo por um
            maior diminui p/(p-1)), se a majoração for <= 9/5 o ramo está morto.
            A majoração é NÃO-CRESCENTE no próximo primo candidato q, o que justifica
            encerrar o laço de candidatos assim que ela cai a <= 9/5.
  FECHO     σ(p^a) = ∏_{d | a+1, d>1} Φ_d(p) divide σ(N) = 9N/5, cujos fatores primos
            estão em S ∪ {3} (S = conjunto dos primos de N; 5 incluído). Para d ímpar
            >= 3 e p >= 5, Zsygmondy (sem exceções nesse regime) dá primo primitivo
            q | Φ_d(p) com ord_q(p) = d, logo d | q - 1 e d <= max(S) - 1. Portanto o
            conjunto de expoentes possíveis de cada primo é FINITO e computável:
            m = a+1 (ímpar) precisa ter TODO divisor > 1 dentro de
            D(p, S) = {d ímpar, 3 <= d <= max(S)-1 : fatores primos de Φ_d(p) ⊆ S∪{3}};
            em particular m ∈ D, então basta filtrar D.

SOLIDEZ: nenhuma poda usa desigualdade não-estrita onde a igualdade ainda permitiria
uma solução; ramos cuja iteração de primos não termina por poda de índice NÃO são
podados silenciosamente — levantam RamoNaoLimitado e nada é certificado.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from functools import lru_cache

from sympy import cyclotomic_poly, factorint, nextprime, primerange

ALVO = Fraction(9, 5)


class RamoNaoLimitado(Exception):
    """A iteração de primos deste ramo não termina só com poda de índice.

    Certificação impossível por este método; o chamador NÃO deve concluir nada.
    """


def sigma_pp(p: int, a: int) -> int:
    """σ(p^a) exato."""
    return (p ** (a + 1) - 1) // (p - 1)


@lru_cache(maxsize=None)
def I_pp(p: int, a: int) -> Fraction:
    """I(p^a) = σ(p^a)/p^a exato."""
    return Fraction(sigma_pp(p, a), p**a)


@lru_cache(maxsize=None)
def sup_pp(p: int) -> Fraction:
    """Cota estrita: I(p^a) < p/(p-1) para todo a (Lema 3 da Fase 0)."""
    return Fraction(p, p - 1)


@lru_cache(maxsize=None)
def _fatores_phi(d: int, p: int) -> tuple[int, ...]:
    """Fatores primos distintos de Φ_d(p), inteiro exato via polinômio ciclotômico."""
    valor = int(cyclotomic_poly(d, p))
    return tuple(sorted(factorint(valor)))


def expoentes_validos(p: int, conjunto: frozenset[int]) -> list[int]:
    """Expoentes a (pares >= 2) possíveis para p^a || N, N amigo de 10 cujo conjunto
    de primos é exatamente `conjunto` (deve conter p). Lista FINITA (ver FECHO).
    """
    if p not in conjunto:
        raise ValueError("p deve pertencer ao conjunto")
    permitidos = set(conjunto) | {3}
    d_max = max(conjunto) - 1
    D: set[int] = set()
    for d in range(3, d_max + 1, 2):
        if all(q in permitidos for q in _fatores_phi(d, p)):
            D.add(d)
    validos = []
    for m in sorted(D):
        # todo divisor > 1 de m precisa estar em D (m ímpar => divisores ímpares)
        if all((m % d != 0) or (d in D) for d in range(3, m, 2)):
            validos.append(m - 1)  # a = m - 1, automaticamente par
    return validos


def _e_amigo(assinatura: dict[int, int]) -> bool:
    """Teste exato final: σ(N)/N == ALVO, por multiplicação cruzada de inteiros.
    Para ALVO = 9/5 é exatamente 5·σ(N) == 9·N (N = 10 nunca ocorre aqui, pois
    todos os expoentes gerados são >= 2). ALVO é lido no momento da chamada para
    permitir testes de completude com alvo plantado."""
    n = 1
    s = 1
    for p, a in assinatura.items():
        n *= p**a
        s *= sigma_pp(p, a)
    return ALVO.denominator * s == ALVO.numerator * n


@lru_cache(maxsize=None)
def _proximos_primos(depois_de: int, quantos: int) -> tuple[int, ...]:
    primos = []
    q = depois_de
    for _ in range(quantos):
        q = int(nextprime(q))
        primos.append(q)
    return tuple(primos)


@lru_cache(maxsize=None)
def _sup_restante(depois_de: int, slots: int) -> Fraction:
    """Majoração estrita do produto dos fatores I de `slots` primos distintos
    > depois_de: produto dos sups dos `slots` MENORES primos disponíveis."""
    prod = Fraction(1)
    for q in _proximos_primos(depois_de, slots):
        prod *= sup_pp(q)
    return prod


# ---------------------------------------------------------------------------
# Eliminação de omega(N) = k (sem teto em N)
# ---------------------------------------------------------------------------

@dataclass
class Estatisticas:
    nos_visitados: int = 0
    podas_min: int = 0
    podas_max: int = 0
    conjuntos_completos: int = 0
    conjuntos_mortos_por_fecho: int = 0
    assinaturas_testadas: int = 0
    amigos_encontrados: list[dict[int, int]] = field(default_factory=list)


def elimina_omega_k(k: int, stats: Estatisticas | None = None) -> Estatisticas:
    """Certifica por exaustão finita: NENHUM amigo de 10 tem ω(N) = k.

    Se um amigo existir no espaço varrido, aparece em stats.amigos_encontrados.
    Se algum ramo não fechar por poda de índice, levanta RamoNaoLimitado e NADA
    é certificado para este k.
    """
    stats = stats or Estatisticas()
    if k < 1:
        raise ValueError("k >= 1")
    # Teorema D: o menor primo é 5; logo o conjunto começa em {5}.
    _dfs_conjuntos([5], sup_pp(5), I_pp(5, 2), k, stats)
    return stats


def _dfs_conjuntos(
    escolhidos: list[int],
    prod_sup: Fraction,
    prod_min: Fraction,
    k: int,
    stats: Estatisticas,
) -> None:
    """DFS sobre conjuntos {5 = p_1 < ... < p_k}. prod_sup = ∏ sup_pp(escolhidos);
    prod_min = ∏ I(p², escolhidos)."""
    stats.nos_visitados += 1
    restantes = k - len(escolhidos)

    if restantes == 0:
        stats.conjuntos_completos += 1
        _testa_conjunto_completo(escolhidos, stats)
        return

    # PODA-MIN (>= é correto: com restantes >= 1 sobra fator estritamente > 1)
    if prod_min >= ALVO:
        stats.podas_min += 1
        return
    # PODA-MAX no nó
    if prod_sup * _sup_restante(escolhidos[-1], restantes) <= ALVO:
        stats.podas_max += 1
        return
    # Terminação do laço de candidatos: a majoração do filho tende a prod_sup quando
    # q -> infinito. Se prod_sup >= ALVO, nenhum q fecha o laço por índice.
    if prod_sup >= ALVO:
        raise RamoNaoLimitado(
            f"conjunto parcial {escolhidos}: prod p/(p-1) = {prod_sup} >= 9/5; "
            "a poda de indice nao limita o proximo primo (seria necessaria "
            "propagacao de divisibilidade -- fora do escopo deste motor)"
        )

    q = escolhidos[-1]
    while True:
        q = int(nextprime(q))
        filho_sup = prod_sup * sup_pp(q)
        if filho_sup * _sup_restante(q, restantes - 1) <= ALVO:
            # majoração não-crescente em q => todos os primos maiores também caem
            stats.podas_max += 1
            return
        _dfs_conjuntos(escolhidos + [q], filho_sup, prod_min * I_pp(q, 2), k, stats)


def _testa_conjunto_completo(conjunto: list[int], stats: Estatisticas) -> None:
    """Conjunto de primos fechado: enumera os expoentes FINITOS (FECHO) e testa a
    igualdade exata em cada combinação."""
    S = frozenset(conjunto)
    listas = []
    for p in conjunto:
        exps = expoentes_validos(p, S)
        if not exps:
            stats.conjuntos_mortos_por_fecho += 1
            return
        listas.append(exps)

    def enumera(i: int, assinatura: dict[int, int]) -> None:
        if i == len(conjunto):
            stats.assinaturas_testadas += 1
            if _e_amigo(assinatura):
                stats.amigos_encontrados.append(dict(assinatura))
            return
        for a in listas[i]:
            assinatura[conjunto[i]] = a
            enumera(i + 1, assinatura)
        del assinatura[conjunto[i]]

    enumera(0, {})


# ---------------------------------------------------------------------------
# Busca limitada: "nenhum amigo de 10 com omega(N) = k e N <= bound".
# Com k = 10 e 11 dá a cota condicional a omega >= 10 (arXiv:2310.15900);
# k >= 12 é impossível para bound <= (5·7·...·43)² — verificado pelo chamador.
# ---------------------------------------------------------------------------

@dataclass
class EstatisticasCota:
    nos_visitados: int = 0
    podas_min: int = 0
    podas_max: int = 0
    podas_produto: int = 0
    conjuntos_completos: int = 0
    assinaturas_testadas: int = 0
    amigos_encontrados: list[dict[int, int]] = field(default_factory=list)


def busca_limitada(
    k: int,
    bound: int,
    stats: EstatisticasCota | None = None,
    p2_intervalo: tuple[int, int | None] | None = None,
    prefixo_intervalos: list[tuple[int, int | None]] | None = None,
) -> EstatisticasCota:
    """Exaustiva sobre N = ∏_{i<=k} p_i^{a_i} <= bound (p_1 = 5, primos >= 5
    distintos, a_i pares >= 2). Sempre termina: como todo expoente é >= 2,
    N >= (∏ p_i)², logo ∏ p_i <= isqrt(bound) — teto inteiro de produto.

    prefixo_intervalos = [(lo2, hi2), (lo3, hi3), ...]: restringe o i-ésimo primo
    (i = 2, 3, ...) a lo <= p_i <= hi (hi = None: sem teto), para fragmentar a
    varredura em shards paralelos. A união de shards cujos intervalos particionam o
    espaço equivale à varredura completa: o filtro só descarta candidatos na
    profundidade correspondente, e as podas de encerramento de laço são monotônicas
    no candidato (uma vez mortas, mortas para todo candidato maior), logo continuam
    válidas com candidatos filtrados. p2_intervalo é atalho para um só intervalo.
    """
    from math import isqrt

    stats = stats or EstatisticasCota()
    cap = isqrt(bound)
    if prefixo_intervalos is None:
        prefixo_intervalos = [p2_intervalo] if p2_intervalo else []

    # lista de primos até o maior primo possível: q_k <= cap / ∏(k-1 menores primos >= 5)
    menores = [5]
    while len(menores) < k:
        menores.append(int(nextprime(menores[-1])))
    prod_k_menos_1 = 1
    for p in menores[:-1]:
        prod_k_menos_1 *= p
    maior_primo = max(5, cap // prod_k_menos_1)
    primos = list(primerange(5, maior_primo + 1))
    if not primos or primos[0] != 5:
        raise ValueError("lista de primos deve começar em 5")

    _dfs_cota([5], 0, 5, sup_pp(5), I_pp(5, 2), k, cap, bound, primos, stats,
              prefixo_intervalos)
    return stats


def _dfs_cota(
    escolhidos: list[int],
    idx_ultimo: int,
    prod_primos: int,
    prod_sup: Fraction,
    prod_min: Fraction,
    k: int,
    cap: int,
    bound: int,
    primos: list[int],
    stats: EstatisticasCota,
    intervalos: list[tuple[int, int | None]] | None = None,
) -> None:
    stats.nos_visitados += 1
    restantes = k - len(escolhidos)

    if restantes == 0:
        # podas de índice na folha (o conjunto está fechado, expoentes livres):
        # I(N) >= prod_min (expoentes >= 2) e I(N) < prod_sup, para QUALQUER
        # escolha de expoentes; > e <= estritos preservam o caso de igualdade
        # prod_min == 9/5 (assinatura toda-2), que segue para o teste exato.
        if prod_min > ALVO:
            stats.podas_min += 1
            return
        if prod_sup <= ALVO:
            stats.podas_max += 1
            return
        stats.conjuntos_completos += 1
        _enumera_expoentes_cota(escolhidos, bound, stats)
        return

    if prod_min >= ALVO:
        stats.podas_min += 1
        return

    # menores primos disponíveis para os slots restantes
    proximos = primos[idx_ultimo + 1: idx_ultimo + 1 + restantes]
    if len(proximos) < restantes:
        # não há primos suficientes na lista <=> produto estouraria o teto
        stats.podas_produto += 1
        return
    prod_prox = 1
    sup_prox = Fraction(1)
    for r in proximos:
        prod_prox *= r
        sup_prox *= sup_pp(r)
    if prod_primos * prod_prox > cap:
        stats.podas_produto += 1
        return
    if prod_sup * sup_prox <= ALVO:
        stats.podas_max += 1
        return

    # janela deslizante: para o candidato primos[j], o resto mínimo obrigatório é
    # primos[j+1 .. j+restantes-1]; ao avançar j, a janela desloca uma posição
    # (divisão/multiplicação exatas — mantém tudo incremental).
    j0 = idx_ultimo + 1
    janela = primos[j0 + 1: j0 + restantes]
    if len(janela) < restantes - 1:
        stats.podas_produto += 1
        return
    resto_min = 1
    sup_resto = Fraction(1)
    for r in janela:
        resto_min *= r
        sup_resto *= sup_pp(r)

    # filtro de shard na profundidade atual (escolhendo o (d+1)-ésimo primo, d = len)
    filtro = None
    if intervalos and len(escolhidos) - 1 < len(intervalos):
        filtro = intervalos[len(escolhidos) - 1]
    for j in range(j0, len(primos)):
        q = primos[j]
        if j > j0:
            # desloca a janela: sai primos[j] (agora é o candidato), entra primos[j+restantes-1]
            entra_idx = j + restantes - 1
            if entra_idx >= len(primos):
                stats.podas_produto += 1
                return
            entra = primos[entra_idx]
            resto_min = (resto_min // primos[j]) * entra if restantes > 1 else 1
            if restantes > 1:
                sup_resto = sup_resto / sup_pp(primos[j]) * sup_pp(entra)
        # teto de produto: crescente em q => uma vez estourado, retorna
        # (válido mesmo com filtro de shard: a condição é monotônica em q)
        if prod_primos * q * resto_min > cap:
            stats.podas_produto += 1
            return
        # PODA-MAX antecipada: majoração do filho é não-crescente em q
        filho_sup = prod_sup * sup_pp(q)
        if filho_sup * sup_resto <= ALVO:
            stats.podas_max += 1
            return
        if filtro is not None:
            if filtro[1] is not None and q > filtro[1]:
                return
            if q < filtro[0]:
                continue
        _dfs_cota(
            escolhidos + [q], j, prod_primos * q, filho_sup,
            prod_min * I_pp(q, 2), k, cap, bound, primos, stats,
            intervalos,
        )


def _enumera_expoentes_cota(conjunto: list[int], bound: int, stats: EstatisticasCota) -> None:
    """Expoentes pares >= 2 com N <= bound; testa σ(N)/N == ALVO em cada folha,
    por multiplicação cruzada de inteiros, com N e σ(N) carregados incrementalmente
    (equivale a _e_amigo; a equivalência é coberta por teste)."""
    alvo_num, alvo_den = ALVO.numerator, ALVO.denominator
    sufixo_min = [1] * (len(conjunto) + 1)
    for i in range(len(conjunto) - 1, -1, -1):
        sufixo_min[i] = sufixo_min[i + 1] * conjunto[i] * conjunto[i]

    def enumera(i: int, n_parcial: int, s_parcial: int, expoentes: list[int]) -> None:
        if i == len(conjunto):
            stats.assinaturas_testadas += 1
            if alvo_den * s_parcial == alvo_num * n_parcial:
                stats.amigos_encontrados.append(dict(zip(conjunto, expoentes)))
            return
        p = conjunto[i]
        a = 2
        pa = p * p
        while n_parcial * pa * sufixo_min[i + 1] <= bound:
            expoentes.append(a)
            enumera(i + 1, n_parcial * pa, s_parcial * ((pa * p - 1) // (p - 1)), expoentes)
            expoentes.pop()
            a += 2
            pa *= p * p

    enumera(0, 1, 1, [])


__all__ = [
    "ALVO",
    "RamoNaoLimitado",
    "Estatisticas",
    "EstatisticasCota",
    "sigma_pp",
    "I_pp",
    "sup_pp",
    "expoentes_validos",
    "elimina_omega_k",
    "busca_limitada",
]
