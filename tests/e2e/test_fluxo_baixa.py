import os
from datetime import date

import pytest
from playwright.sync_api import Page, expect

USUARIO = os.environ.get("USUARIO", "admin")
SENHA = os.environ.get("SENHA", "admin123")

VENCIMENTO = "2026-11-10"
PAGAMENTO_EM_DIA = "2026-11-05"
INICIO_DO_PERIODO = "2026-11-01"
FIM_DO_PERIODO = VENCIMENTO


@pytest.fixture
def pagina(page: Page) -> Page:
    page.goto("/login")
    page.get_by_label("Usuário").fill(USUARIO)
    page.get_by_label("Senha").fill(SENHA)
    page.get_by_role("button", name="Entrar").click()
    expect(page.get_by_role("heading", name="Títulos")).to_be_visible()
    return page


def menu(pagina: Page):
    return pagina.get_by_role("navigation", name="Principal")


def cadastrar_titulo_a_receber(pagina: Page, descricao: str, valor: str) -> None:
    menu(pagina).get_by_role("link", name="Novo título").click()
    pagina.get_by_label("Tipo").select_option(label="A receber")
    pagina.get_by_label("Descrição").fill(descricao)
    pagina.get_by_label("Valor").fill(valor)
    pagina.get_by_label("Vencimento").fill(VENCIMENTO)
    pagina.get_by_role("button", name="Salvar").click()
    expect(pagina.get_by_role("status")).to_have_text("Título cadastrado.")


def linha_do_titulo(pagina: Page, descricao: str):
    return pagina.get_by_role("row").filter(has_text=descricao)


def abrir_lista_de_titulos(pagina: Page) -> None:
    menu(pagina).get_by_role("link", name="Títulos", exact=True).click()
    expect(pagina.get_by_role("heading", name="Títulos")).to_be_visible()


def registrar_baixa(pagina: Page, descricao: str, valor: str) -> None:
    linha_do_titulo(pagina, descricao).get_by_role("link", name="Baixar").click()
    expect(pagina.get_by_role("heading", name="Baixa do título")).to_be_visible()
    pagina.get_by_label("Valor da baixa").fill(valor)
    pagina.get_by_label("Data do pagamento").fill(PAGAMENTO_EM_DIA)
    pagina.get_by_role("button", name="Registrar baixa").click()


def calcular_fluxo_de_caixa(pagina: Page, inicio: str, fim: str) -> None:
    menu(pagina).get_by_role("link", name="Fluxo de caixa").click()
    pagina.get_by_label("Início").fill(inicio)
    pagina.get_by_label("Fim").fill(fim)
    pagina.get_by_role("button", name="Calcular").click()
    periodo = f"{_br(inicio)} a {_br(fim)}"
    expect(pagina.get_by_role("heading", name=f"Saldo projetado de {periodo}")).to_be_visible()


def _br(data_iso: str) -> str:
    return date.fromisoformat(data_iso).strftime("%d/%m/%Y")


def test_baixa_parcial_atualiza_saldo_status_e_fluxo_de_caixa(pagina: Page):
    cadastrar_titulo_a_receber(pagina, "Mensalidade", "1000,00")

    registrar_baixa(pagina, "Mensalidade", "400,00")

    expect(pagina.get_by_role("status")).to_contain_text("Baixa registrada")

    abrir_lista_de_titulos(pagina)
    linha = linha_do_titulo(pagina, "Mensalidade")
    expect(linha).to_have_count(1)
    expect(linha.locator("[data-campo=saldo]")).to_have_text("600.00")
    expect(linha.locator("[data-campo=status]")).to_have_text("parcial")

    calcular_fluxo_de_caixa(pagina, INICIO_DO_PERIODO, FIM_DO_PERIODO)
    expect(pagina.locator("[data-campo=saldo-projetado]")).to_have_text("600.00")


def test_baixa_maior_que_o_saldo_mostra_erro_e_nao_altera_o_saldo(pagina: Page):
    cadastrar_titulo_a_receber(pagina, "Mensalidade", "1000,00")

    registrar_baixa(pagina, "Mensalidade", "1000,01")

    expect(pagina.get_by_role("alert")).to_have_text(
        "O valor da baixa não pode ser maior que o saldo do título."
    )
    expect(pagina.get_by_text("Nenhuma baixa registrada.")).to_be_visible()

    abrir_lista_de_titulos(pagina)
    linha = linha_do_titulo(pagina, "Mensalidade")
    expect(linha.locator("[data-campo=saldo]")).to_have_text("1000.00")
    expect(linha.locator("[data-campo=status]")).to_have_text("aberto")
