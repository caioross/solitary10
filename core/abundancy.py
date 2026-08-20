"""Fundamentos do projeto Solitary 10.

Regra de ouro: aritmética EXATA sempre (int, Fraction). Float é proibido
em qualquer passo que sustente uma afirmação matemática.

N é amigo de 10  <=>  N != 10  e  I(N) = sigma(N)/N = 9/5  <=>  5*sigma(N) = 9*N.
"""
from __future__ import annotations

from fractions import Fraction
from math import gcd

from sympy import factorint

ALVO = Fraction(9, 5)  # I(10) = 18/10


def sigma_de_fatoracao(fatores: dict[int, int]) -> int:
    """sigma(n) a partir da fatoração {p: e}. Exato."""
    s = 1
    for p, e in fatores.items():
        s *= (p ** (e + 1) - 1) // (p - 1)
    return s


def sigma(n: int) -> int:
    """Soma dos divisores positivos de n (exata, via fatoração sympy)."""
    if n < 1:
        raise ValueError("n deve ser um inteiro positivo")
    if n == 1:
        return 1
    return sigma_de_fatoracao(factorint(n))


def sigma_do_quadrado(m: int) -> int:
    """sigma(m^2) fatorando apenas m (mais rápido para buscas estruturais)."""
    if m == 1:
        return 1
    return sigma_de_fatoracao({p: 2 * e for p, e in factorint(m).items()})


def abundancia(n: int) -> Fraction:
    """I(n) = sigma(n)/n como fração exata."""
    return Fraction(sigma(n), n)


def e_amigo_de_10(n: int) -> bool:
    return n != 10 and 5 * sigma(n) == 9 * n


def solitario_por_gcd(n: int) -> bool:
    """Critério suficiente clássico (Greening): gcd(n, sigma(n)) = 1 => n solitário.

    Não decide o caso do 10: gcd(10, 18) = 2.
    """
    return gcd(n, sigma(n)) == 1


def crivo_sigma(limite: int) -> list[int]:
    """s[k] = sigma(k) para 0 <= k <= limite, por crivo de divisores.

    O(N log N), sem fatoração. Base das buscas exaustivas certificadas.
    """
    s = [0] * (limite + 1)
    for d in range(1, limite + 1):
        for multiplo in range(d, limite + 1, d):
            s[multiplo] += d
    return s


def amigos_no_intervalo(alvo: Fraction, limite: int) -> list[int]:
    """Todos os n <= limite com I(n) = alvo (inclui o próprio n de referência)."""
    p, q = alvo.numerator, alvo.denominator
    s = crivo_sigma(limite)
    return [n for n in range(1, limite + 1) if q * s[n] == p * n]
