"""Le o cache do coletor e monta as linhas sobre as tarefas do Sala do Futuro."""
import json
import time
from datetime import datetime
from pathlib import Path

CACHE = Path.home() / ".cache/hypr-boas-vindas"
ARQUIVO = CACHE / "tarefas.json"
MARCA = CACHE / "coletando"

CIANO = "\033[96m"
AMARELO = "\033[93m"
VERMELHO = "\033[91m"
NEGRITO = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def esperar_coletor(limite=75):
    fim = time.time() + limite
    while MARCA.exists() and time.time() < fim:
        time.sleep(0.5)


def ler():
    try:
        return json.loads(ARQUIVO.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def prazo_local(texto):
    try:
        return datetime.fromisoformat(texto.replace("Z", "+00:00")).astimezone()
    except (ValueError, AttributeError):
        return None


def cor_do_prazo(prazo, agora):
    horas = (prazo - agora).total_seconds() / 3600
    if horas < 24:
        return VERMELHO + NEGRITO
    if horas < 72:
        return AMARELO + NEGRITO
    return CIANO


def linhas_tarefas():
    """Retorna lista de (texto, cor)."""
    if MARCA.exists():
        print(DIM + "Consultando o Sala do Futuro..." + RESET)
        esperar_coletor()

    dados = ler()
    if dados is None:
        return [("Sala do Futuro: sem dados ainda.", AMARELO)]

    estado = dados.get("estado")
    if estado == "precisa_login":
        return [("Sessão do Sala do Futuro expirou. Rode no terminal: sala-login", AMARELO)]
    if estado == "login_falhou":
        return [("Login no Sala do Futuro falhou. Confira SALA_RA, SALA_DIGITO e SALA_SENHA no .env.", AMARELO)]
    if estado != "ok":
        return [(f"Sala do Futuro indisponível agora ({estado}).", AMARELO)]

    tarefas = dados.get("tarefas", [])
    if not tarefas:
        return [("Sala do Futuro: nenhuma tarefa pendente!", CIANO)]

    agora = datetime.now().astimezone()
    com_prazo = []
    for t in tarefas:
        prazo = prazo_local(t.get("prazo"))
        if prazo:
            com_prazo.append((prazo, t))
    com_prazo.sort(key=lambda par: par[0])

    n = len(tarefas)
    plural = "tarefa pendente" if n == 1 else "tarefas pendentes"
    linhas = [(f"Sala do Futuro: você tem {n} {plural}.", AMARELO + NEGRITO)]
    if com_prazo:
        prazo, t = com_prazo[0]
        titulo = (t.get("titulo") or "sem título")[:50]
        linhas.append((f"Mais próxima: {titulo}", CIANO))
        linhas.append((f"Prazo: {prazo:%d/%m} às {prazo:%H:%M}", cor_do_prazo(prazo, agora)))
    if dados.get("desatualizado"):
        linhas.append(("(dados de " + dados.get("atualizado_em", "?")[11:16] + ", atualização falhou: " + dados["desatualizado"] + ")", DIM))
    return linhas


if __name__ == "__main__":
    for texto, cor in linhas_tarefas():
        print(cor + texto + RESET)
