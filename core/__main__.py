"""Uso:
  python3 -m core              conversa de teste (NAO abre programas)
  python3 -m core --executar   conversa de verdade (abre Steam, Firefox, etc.)
  python3 -m core --cofre      so o teste do cofre (tempos de cada modulo)
  python3 -m core --cofre --json
"""
import json
import sys
import time
from dataclasses import asdict

from .cerebro import Cerebro
from .config import carregar
from .registro import criar_cofre
from .saida import SaidaTeste


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
    cfg = carregar()
    cofre = criar_cofre(cfg)
    if "--cofre" in sys.argv:
        teste_cofre(cofre)
        return
    cofre.iniciar()
    Cerebro(cfg, cofre, SaidaTeste(), de_verdade="--executar" in sys.argv).executar()


main()
