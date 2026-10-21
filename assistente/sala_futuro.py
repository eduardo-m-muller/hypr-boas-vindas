"""Consulta de tarefas pendentes no Sala do Futuro (em construcao)."""
import json
import os

import requests

import env

env.carregar()

BASE = "https://sedintegracoes.educacao.sp.gov.br/saladofuturobffapi"
RA = os.environ.get("SALA_RA", "")
DIGITO = os.environ.get("SALA_DIGITO", "")
UF = os.environ.get("SALA_UF", "SP")
SENHA = os.environ.get("SALA_SENHA", "")
CHAVE = os.environ.get("SALA_APIM_KEY", "")


def configurado():
    return bool(RA and SENHA and CHAVE)


def cabecalhos(token=None):
    h = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "X-Product-Name": "SalaDoFuturo",
        "Ocp-Apim-Subscription-Key": CHAVE,
        "Origin": "https://saladofuturo.educacao.sp.gov.br",
        "Referer": "https://saladofuturo.educacao.sp.gov.br/",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:154.0) Gecko/20100101 Firefox/154.0",
    }
    if token:
        h["Authorization"] = "Bearer " + token
    return h


def login(timeout=10):
    corpo = {"user": f"{RA}{DIGITO}{UF}", "senha": SENHA}
    r = requests.post(BASE + "/credenciais/api/LoginCompletoToken",
                      json=corpo, headers=cabecalhos(), timeout=timeout)
    r.raise_for_status()
    return r.json()


def estrutura(obj):
    """Copia a forma do JSON trocando todos os valores por tipo/tamanho."""
    if isinstance(obj, dict):
        return {k: estrutura(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [f"<lista de {len(obj)}>"] + ([estrutura(obj[0])] if obj else [])
    if isinstance(obj, str):
        return f"<texto {len(obj)} chars>"
    return f"<{type(obj).__name__}>"


def tarefas_pendentes():
    """Retorna o numero de tarefas pendentes, ou None se nao der."""
    if not configurado():
        return None
    # TODO: usar o token do login para listar as tarefas (proximo passo)
    return None


if __name__ == "__main__":
    print("configurado:", configurado())
    if configurado():
        try:
            print(json.dumps(estrutura(login()), indent=2, ensure_ascii=False))
        except requests.HTTPError as erro:
            print("erro HTTP:", erro.response.status_code)
        except requests.RequestException as erro:
            print("erro de rede:", type(erro).__name__)
