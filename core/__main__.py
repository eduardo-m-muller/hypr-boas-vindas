"""Uso:
  python3 -m core              conversa de teste, sem cores, no terminal atual, SEM abrir programas
  python3 -m core --visual     igual ao kitty (cores, digitacao) numa janela separada, SEM abrir programas
  python3 -m core --executar   conversa de verdade numa janela separada (abre Steam, Firefox, etc.)
  python3 -m core --aqui       com --visual/--executar, roda no terminal atual em vez de abrir janela
  python3 -m core --cofre      so o teste do cofre (tempos de cada modulo)
  python3 -m core --cofre --json
"""
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path

from .cerebro import Cerebro
from .config import carregar
from .registro import criar_cofre
from .saida import SaidaTeste
from .saida_kitty import SaidaKitty

RAIZ = Path(__file__).resolve().parent.parent


def reabrir_em_janela():
    """Abre uma janela kitty separada rodando o mesmo comando e volta na hora."""
    ambiente = dict(os.environ, HBV_JANELA="1")
    comando = ["kitty", "--class", "boas-vindas", "-e", sys.executable, "-m", "core"] + sys.argv[1:]
    subprocess.Popen(comando, cwd=RAIZ, env=ambiente, start_new_session=True)


def teste_cofre(cofre):
    inicio = time.time()
    cofre.iniciar()
    faltam = set(cofre.nomes())
    while faltam and time.time() - inicio < 120:
        for nome in sorted(faltam):
            r = cofre.obter(nome)
            if r:
                estado = "ok" if r.ok else "ERRO " + str(r.erro)
                print(f"[{time.time() - inicio:5.1f}s] {nome}: {estado} ({r.ms} ms)")
                faltam.discard(nome)
        time.sleep(0.2)
    for nome in sorted(faltam):
        print(nome + ": nao ficou pronto em 120 s")
    if "--json" in sys.argv:
        resumo = {n: asdict(cofre.obter(n)) for n in cofre.nomes() if cofre.pronto(n)}
        print(json.dumps(resumo, indent=2, ensure_ascii=False))


def main():
    executar = "--executar" in sys.argv
    visual = executar or "--visual" in sys.argv

    if visual and "--aqui" not in sys.argv and not os.environ.get("HBV_JANELA"):
        reabrir_em_janela()
        return

    cfg = carregar()
    cofre = criar_cofre(cfg)
    if "--cofre" in sys.argv:
        teste_cofre(cofre)
        return
    cofre.iniciar()
    saida = SaidaKitty(cfg) if visual else SaidaTeste()
    Cerebro(cfg, cofre, saida, de_verdade=executar).executar()
    saida.fechar()


main()
