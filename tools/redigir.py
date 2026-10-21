#!/usr/bin/env python3
"""Mascara segredos de um cURL: valores do .env, campos de senha/usuario e headers sensiveis.
Uso: wl-paste | python3 tools/redigir.py | wl-copy"""
import re
import sys
from pathlib import Path

A = chr(34)
SENSIVEIS = ("authorization", "cookie", "x-api-key", "csrf", "token", "x-auth", "subscription")
PADRAO = re.compile(
    "(" + A + "(?:senha|password|pass|user|username|login|cpf|ra|rg)" + A + r"\s*:\s*)"
    + A + "[^" + A + "]*" + A,
    re.I,
)


def segredos_do_env():
    arquivo = Path(__file__).resolve().parent.parent / ".env"
    valores = []
    if arquivo.exists():
        for linha in arquivo.read_text(encoding="utf-8").splitlines():
            if "=" in linha and not linha.strip().startswith("#"):
                valor = linha.split("=", 1)[1].strip().strip(A)
                if len(valor) >= 3:
                    valores.append(valor)
    return valores


texto = sys.stdin.read()
for valor in segredos_do_env():
    texto = texto.replace(valor, "XXX")
texto = PADRAO.sub(lambda m: m.group(1) + A + "XXX" + A, texto)

saida = []
for linha in texto.splitlines():
    baixa = linha.lower().strip()
    cabecalho = baixa.startswith("-h") and any(s in baixa for s in SENSIVEIS)
    cookie = baixa.startswith("-b ") or baixa.startswith("--cookie")
    saida.append("[removido: header/cookie sensivel]" if (cabecalho or cookie) else linha)

print(chr(10).join(saida))
