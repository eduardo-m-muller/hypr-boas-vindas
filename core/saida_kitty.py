"""Front de terminal (kitty): texto digitado, colorido por tom, com pausas entre os blocos."""
import sys
import time

from .saida import Saida

CIANO = "\033[96m"
AMARELO = "\033[93m"
VERMELHO = "\033[91m"
NEGRITO = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

CORES = {
    "titulo": CIANO + NEGRITO,
    "normal": CIANO,
    "aviso": AMARELO + NEGRITO,
    "critico": VERMELHO + NEGRITO,
    "suave": DIM,
}


class SaidaKitty(Saida):
    def __init__(self, cfg):
        v = cfg["visual"]
        self.atraso = v["atraso_digitacao"]
        self.linha_em_branco = v["linha_em_branco_entre_blocos"]
        self.fechar_apos = v["fechar_apos_s"]
        print()

    def _digitar(self, texto, cor, atraso=None):
        atraso = self.atraso if atraso is None else atraso
        sys.stdout.write(cor)
        for letra in texto:
            sys.stdout.write(letra)
            sys.stdout.flush()
            time.sleep(atraso)
        sys.stdout.write(RESET + "\n")
        sys.stdout.flush()

    def falar(self, fala):
        self._digitar(fala.texto, CORES.get(fala.tom, CIANO), self.atraso * fala.ritmo)
        if fala.pausa > 0:
            if self.linha_em_branco:
                print()
            time.sleep(fala.pausa)

    def perguntar(self, texto, opcoes):
        print()
        self._digitar(texto, CORES["titulo"])
        cor = CORES["normal"]
        for i, (_, rotulo) in enumerate(opcoes, 1):
            print(f"{cor}  {i}) {rotulo}{RESET}")
        while True:
            try:
                resposta = input(CORES["aviso"] + "> " + RESET)
            except EOFError:
                return opcoes[-1][0]
            escolha = self.interpretar(resposta, opcoes)
            if escolha:
                print()
                return escolha
            self._digitar("Não entendi, tenta de novo.", CORES["suave"], 0.01)

    def fechar(self):
        time.sleep(self.fechar_apos)
