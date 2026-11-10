import re

import pytest
from playwright.sync_api import Page, expect


def test_sem_login_a_aplicacao_redireciona_para_a_tela_de_entrada(page: Page):
    page.goto("/")

    expect(page).to_have_url(re.compile(r"/login$"))


def test_senha_errada_mostra_mensagem_de_erro(page: Page):
    page.goto("/login")
    page.get_by_label("Usuário").fill("admin")
    page.get_by_label("Senha").fill("errada")
    page.get_by_role("button", name="Entrar").click()

    expect(page.get_by_role("alert")).to_have_text("Usuário ou senha inválidos.")


@pytest.fixture
def pagina(page: Page) -> Page:
    page.goto("/login")
    page.get_by_label("Usuário").fill("admin")
    page.get_by_label("Senha").fill("admin123")
    page.get_by_role("button", name="Entrar").click()
    expect(page.get_by_role("heading", name="Títulos")).to_be_visible()
    return page


def test_titulo_cadastrado_aparece_na_lista(pagina: Page):
    pagina.get_by_role("link", name="Novo título").click()
    pagina.get_by_label("Tipo").select_option(label="A receber")
    pagina.get_by_label("Descrição").fill("Mensalidade")
    pagina.get_by_label("Valor").fill("1000,00")
    pagina.get_by_label("Vencimento").fill("2026-11-10")
    pagina.get_by_role("button", name="Salvar").click()

    expect(pagina.get_by_role("status")).to_have_text("Título cadastrado.")
    linha = pagina.get_by_role("row").filter(has_text="Mensalidade")
    expect(linha.locator("[data-campo=saldo]")).to_have_text("1000.00")
    expect(linha.locator("[data-campo=status]")).to_have_text("aberto")
