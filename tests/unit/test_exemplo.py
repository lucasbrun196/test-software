"""Primeiro exemplo de teste automatizado. Use como modelo para os seus."""
from datetime import date

from app.regras import proximo_dia_util


def test_vencimento_no_sabado_e_prorrogado_para_segunda():
    sabado = date(2026, 10, 10)

    resultado = proximo_dia_util(sabado)

    assert resultado == date(2026, 10, 12)
