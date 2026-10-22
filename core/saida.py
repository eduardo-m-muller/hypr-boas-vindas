"""Interface de saida e entrada do assistente. Qualquer front (terminal, GUI, voz) implementa isto."""
import time


class Saida:
    def falar(self, texto, pausa=0.4):
        raise NotImplementedError

    def perguntar(self, texto, opcoes):
        """opcoes: lista de (chave, rotulo). Retorna a chave escolhida."""
        raise NotImplementedError


class SaidaTeste(Saida):
    """Implementacao minima para testar o back: print e input."""

    def falar(self, texto, pausa=0.4):
        print(texto, flush=True)
        time.sleep(pausa)

    def perguntar(self, texto, opcoes):
        print(texto, flush=True)
        for i, (_, rotulo) in enumerate(opcoes, 1):
            print(f"  {i}) {rotulo}")
        while True:
            try:
                resposta = input("> ").strip().lower()
            except EOFError:
                return opcoes[-1][0]
            if resposta.isdigit() and 1 <= int(resposta) <= len(opcoes):
                return opcoes[int(resposta) - 1][0]
            for chave, rotulo in opcoes:
                if resposta and (resposta == chave or rotulo.lower().startswith(resposta)):
                    return chave
            print("Não entendi, tenta de novo.")
