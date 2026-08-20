"""Cross-checks independentes de sympy para o motor da Fase 1.

Motivação (passada adversarial do Bloco 1): os certificados dependem da correção de
sympy.factorint / cyclotomic_poly / nextprime / primerange, e o teste de fecho
original usava o MESMO factorint como referência (falha de modo comum). Aqui toda
referência é aritmética inteira pura: crivo de Eratóstenes próprio, fatoração por
divisão por tentativa própria, identidades telescópica e ciclotômica.

A superfície de fatoração do certificado "omega(N) >= 6" é exatamente Phi_d(5) para
d ímpar 3..21 (o fecho mata os três conjuntos de Ward já em p = 5, então nenhum outro
Phi é consultado) — coberta INTEIRA aqui por referência independente.
"""
from sympy import nextprime, primerange

from core.motor import _fatores_phi, expoentes_validos, sigma_pp


def _crivo(limite: int) -> list[int]:
    marcado = bytearray(limite + 1)
    primos = []
    for n in range(2, limite + 1):
        if not marcado[n]:
            primos.append(n)
            for m in range(n * n, limite + 1, n):
                marcado[m] = 1
    return primos


def _fatora_trial(n: int) -> dict[int, int]:
    fatores: dict[int, int] = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            fatores[d] = fatores.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        fatores[n] = fatores.get(n, 0) + 1
    return fatores


def _phi_d_p(d: int, p: int) -> int:
    """Phi_d(p) por aritmética inteira pura: prod_{e | d} (p^e - 1)^{mu(d/e)}.
    Implementado como quociente de produtos para ficar 100% inteiro."""
    def mu(n: int) -> int:
        f = _fatora_trial(n)
        if any(e > 1 for e in f.values()):
            return 0
        return -1 if len(f) % 2 else 1

    num = 1
    den = 1
    for e in range(1, d + 1):
        if d % e == 0:
            m = mu(d // e)
            if m == 1:
                num *= p**e - 1
            elif m == -1:
                den *= p**e - 1
    assert num % den == 0
    return num // den


def test_crivo_proprio_vs_primerange_e_nextprime():
    proprio = [p for p in _crivo(100_000) if p >= 5]
    sympy_lista = list(primerange(5, 100_001))
    assert proprio == sympy_lista
    # cadeia nextprime consistente com o crivo
    q = 5
    for esperado in proprio[1:200]:
        q = int(nextprime(q))
        assert q == esperado


def test_superficie_do_certificado_omega6_por_divisao_por_tentativa():
    # todos os Phi_d(5), d ímpar 3..21: fatoração completa por divisão por tentativa,
    # comparada com o que o motor usa (_fatores_phi, via sympy)
    for d in range(3, 22, 2):
        valor = _phi_d_p(d, 5)
        fatores = _fatora_trial(valor)
        # reconstrução exata e primalidade de cada fator por divisão por tentativa
        prod = 1
        for q, e in fatores.items():
            assert all(q % r != 0 for r in range(2, int(q**0.5) + 1))
            prod *= q**e
        assert prod == valor
        assert tuple(sorted(fatores)) == _fatores_phi(d, 5)


def test_identidade_ciclotomica_e_telescopica():
    for p in (5, 7, 11, 13, 23):
        # prod_{d | m} Phi_d(p) == p^m - 1 (valida cyclotomic_poly indiretamente)
        for m in (3, 9, 15, 21):
            prod = p - 1  # Phi_1(p)
            for d in range(2, m + 1):
                if m % d == 0:
                    prod *= _phi_d_p(d, p)
            assert prod == p**m - 1
        # telescópica: (p-1)*sigma(p^a) + 1 == p^(a+1)
        for a in range(1, 30):
            assert (p - 1) * sigma_pp(p, a) + 1 == p ** (a + 1)


def test_fecho_dos_tres_conjuntos_de_ward_sem_sympy():
    # referência independente: para S = {5,7,11,13,q}, q em {17,19,23}, NENHUM a par
    # com a+1 <= max(S)-1 (teto de Zsygmondy) tem sigma(5^a) com fatores em S∪{3};
    # fatoração por divisão por tentativa (valores <= sigma(5^22) ~ 6e15, tratável)
    for q in (17, 19, 23):
        S = frozenset({5, 7, 11, 13, q})
        permitidos = set(S) | {3}
        for a in range(2, max(S) - 1, 2):  # a+1 <= max(S)-1, a par
            fatores = _fatora_trial(sigma_pp(5, a))
            assert not all(r in permitidos for r in fatores), (q, a)
        # e o motor concorda: nenhum expoente válido para p = 5
        assert expoentes_validos(5, S) == []
