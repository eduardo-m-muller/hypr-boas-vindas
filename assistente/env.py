"""Carrega variaveis do arquivo .env na raiz do projeto."""
import os
from pathlib import Path


def carregar(caminho=None):
    raiz = Path(__file__).resolve().parent.parent
    arquivo = Path(caminho) if caminho else raiz / ".env"
    if not arquivo.exists():
        return
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        os.environ.setdefault(chave.strip(), valor.strip().strip(chr(34)))
