#!/usr/bin/env python3
"""Troca segredos do .env por XXX e remove headers sensiveis de um cURL.
Uso: wl-paste | python3 tools/redigir.py | wl-copy"""
import sys
from pathlib import Path

SENSIVEIS = ("authorization", "cookie", "x-api-key", "csrf", "token", "x-auth")


def segredos_do_env():
    arquivo = Path(__file__).resolve().parent.parent / ".env"
    valores = []
    if arquivo.exists():
        for linha in arquivo.read_text(encoding="utf-8").splitlines():
            if "=" in linha and not linha.strip().startswith("#"):
                valor = linha.split("=", 1)[1].strip().strip(chr(34))
                if len(valor) >= 3:
                    valores.append(valor)
    return valores


texto = sys.stdin.read()
for valor in segredos_do_env():
    texto = texto.replace(valor, "XXX")

saida = []
for linha in texto.splitlines():
    baixa = linha.lower().strip()
    cabecalho = baixa.startswith("-h") and any(s in baixa for s in SENSIVEIS)
    cookie = baixa.startswith("-b ") or baixa.startswith("--cookie")
    if cabecalho or cookie:
        saida.append("[removido: header/cookie sensivel]")
    else:
        saida.append(linha)

print(chr(10).join(saida))
