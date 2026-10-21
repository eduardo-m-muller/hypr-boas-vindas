"""Coletor: abre o Sala do Futuro num navegador real, faz login sozinho com o .env,
le as tarefas pendentes e salva num cache local. Uso: coletor.py [--visivel]"""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

import env

env.carregar()

PERFIL = Path.home() / ".local/share/hypr-boas-vindas/perfil"
CACHE = Path.home() / ".cache/hypr-boas-vindas"
ARQUIVO = CACHE / "tarefas.json"
LOG = CACHE / "coletor.log"
URL_TAREFAS = "https://saladofuturo.educacao.sp.gov.br/tarefas"
URL_LOGIN = "https://saladofuturo.educacao.sp.gov.br/login-alunos"

JS = """async ([url, chave]) => {
  const r = await fetch(url, {headers: {"x-api-key": chave, "Accept": "application/json"}, cache: "no-store"});
  let corpo = null;
  try { corpo = await r.json(); } catch (e) {}
  return {status: r.status, corpo: corpo};
}"""


def preparar():
    CACHE.mkdir(parents=True, exist_ok=True)
    PERFIL.mkdir(parents=True, exist_ok=True)
    os.chmod(CACHE, 0o700)
    os.chmod(PERFIL, 0o700)


def registrar(msg):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(datetime.now().isoformat(timespec="seconds") + " " + msg + "\n")
    os.chmod(LOG, 0o600)
    linhas = LOG.read_text(encoding="utf-8").splitlines()
    if len(linhas) > 200:
        LOG.write_text("\n".join(linhas[-100:]) + "\n", encoding="utf-8")


def ler_antigo():
    try:
        return json.loads(ARQUIVO.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def salvar(estado, tarefas):
    agora = datetime.now().isoformat(timespec="seconds")
    antigo = ler_antigo()
    if estado == "ok":
        dados = {"atualizado_em": agora, "estado": "ok", "tarefas": tarefas}
    elif estado != "precisa_login" and antigo and antigo.get("estado") == "ok":
        dados = dict(antigo)
        dados["desatualizado"] = estado
    else:
        dados = {"atualizado_em": agora, "estado": estado, "tarefas": []}
    ARQUIVO.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    os.chmod(ARQUIVO, 0o600)


def resumir(tarefa):
    return {
        "id": tarefa.get("id"),
        "titulo": tarefa.get("title"),
        "prazo": tarefa.get("expire_at"),
        "prova": bool(tarefa.get("is_exam")),
        "redacao": bool(tarefa.get("is_essay")),
        "status": tarefa.get("answer_status"),
    }


def tem_credenciais():
    return bool(os.environ.get("SALA_RA") and os.environ.get("SALA_SENHA"))


def fazer_login(pagina):
    """Preenche o formulario de login. Retorna True se saiu da tela de login."""
    ra = os.environ.get("SALA_RA", "")
    digito = os.environ.get("SALA_DIGITO", "")
    senha = os.environ.get("SALA_SENHA", "")
    try:
        pagina.goto(URL_LOGIN, wait_until="domcontentloaded", timeout=30000)
        pagina.get_by_placeholder(re.compile("Ex")).first.fill(ra, timeout=15000)
        if digito:
            pagina.get_by_placeholder("0", exact=True).first.fill(digito, timeout=5000)
        pagina.get_by_placeholder("Digite sua senha").first.fill(senha, timeout=5000)
        pagina.get_by_role("button", name="Acessar").click(timeout=5000)
        pagina.wait_for_url(
            lambda u: "login-alunos" not in u and "escolha-de-perfil" not in u,
            timeout=25000,
        )
        return True
    except Exception as erro:
        registrar("login_falhou etapa=" + type(erro).__name__ + " url=" + pagina.url.split("?")[0])
        return False


def coletar(visivel=False):
    espera = 180 if visivel else 70
    achado = {}
    tentou_login = False

    def ao_responder(resp):
        req = resp.request
        caminho = resp.url.split("?")[0]
        if req.method == "GET" and "edusp-api.ip.tv" in caminho and caminho.endswith("/tms/task/todo"):
            achado["req"] = req

    with sync_playwright() as p:
        ctx = p.firefox.launch_persistent_context(str(PERFIL), headless=not visivel)
        try:
            ctx.on("response", ao_responder)
            pagina = ctx.pages[0] if ctx.pages else ctx.new_page()
            pagina.goto(URL_TAREFAS, wait_until="domcontentloaded", timeout=30000)
            for i in range(espera * 2):
                if "req" in achado:
                    break
                precisa = "login" in pagina.url or "escolha-de-perfil" in pagina.url
                if precisa:
                    if not tentou_login and tem_credenciais():
                        tentou_login = True
                        if fazer_login(pagina):
                            pagina.goto(URL_TAREFAS, wait_until="domcontentloaded", timeout=30000)
                            continue
                        if not visivel:
                            return "login_falhou", []
                    elif not visivel:
                        return ("login_falhou" if tentou_login else "precisa_login"), []
                elif i == 60 and not visivel:
                    try:
                        pagina.reload(wait_until="domcontentloaded", timeout=30000)
                    except Exception:
                        pass
                pagina.wait_for_timeout(500)
            if "req" not in achado:
                registrar("sem_dados url=" + pagina.url.split("?")[0] + " titulo=" + pagina.title())
                if "moment" in pagina.title().lower():
                    return "bloqueado_cloudflare", []
                return "sem_dados", []
            req = achado["req"]
            chave = req.all_headers().get("x-api-key")
            if not chave:
                return "sem_chave", []
            res = pagina.evaluate(JS, [req.url, chave])
            if res["status"] != 200 or not isinstance(res["corpo"], list):
                return "erro_http_" + str(res["status"]), []
            return "ok", [resumir(t) for t in res["corpo"]]
        finally:
            ctx.close()


def main():
    preparar()
    visivel = "--visivel" in sys.argv
    try:
        estado, tarefas = coletar(visivel=visivel)
    except Exception as erro:
        estado, tarefas = "erro_" + type(erro).__name__, []
    registrar("estado=" + estado + " tarefas=" + str(len(tarefas)))
    salvar(estado, tarefas)
    print("estado:", estado)
    print("tarefas:", len(tarefas))


main()
