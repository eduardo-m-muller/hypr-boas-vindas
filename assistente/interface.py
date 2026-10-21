"""Abre a tela de boas-vindas em uma janela Firefox local."""
import queue
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright


def mostrar(carregar_dados):
    resultado = queue.Queue()
    fechar = threading.Event()

    def carregar():
        try:
            resultado.put(carregar_dados())
        except Exception as erro:
            resultado.put({"erro": str(erro)})

    with sync_playwright() as playwright:
        navegador = playwright.firefox.launch(
            headless=False,
            args=["--kiosk"],
        )
        pagina = navegador.new_page(viewport={"width": 1280, "height": 800})
        pagina.expose_function("fecharBoasVindas", fechar.set)
        pagina.goto(Path(__file__).with_name("tela.html").as_uri())
        threading.Thread(target=carregar, daemon=True).start()

        try:
            while not fechar.is_set() and not pagina.is_closed():
                try:
                    dados = resultado.get(timeout=0.1)
                except queue.Empty:
                    pagina.wait_for_timeout(100)
                    continue
                pagina.evaluate("dados => window.atualizarBoasVindas(dados)", dados)
                break

            while not fechar.is_set() and not pagina.is_closed():
                pagina.wait_for_timeout(100)
        finally:
            navegador.close()