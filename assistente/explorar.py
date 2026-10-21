"""Uso: python3 assistente/explorar.py GET /caminho [corpo_json]
Faz login, chama o endpoint e mostra so a ESTRUTURA da resposta."""
import json
import sys

import requests

import sala_futuro as sf


def main():
    metodo = sys.argv[1].upper()
    caminho = sys.argv[2]
    corpo = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
    token = sf.login()["token"]
    r = requests.request(metodo, sf.BASE + caminho, json=corpo,
                         headers=sf.cabecalhos(token), timeout=15)
    print("status:", r.status_code)
    try:
        print(json.dumps(sf.estrutura(r.json()), indent=2, ensure_ascii=False))
    except ValueError:
        print("resposta nao-JSON,", len(r.text), "chars")


main()
