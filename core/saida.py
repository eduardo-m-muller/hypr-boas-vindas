"""Interface de saida/entrada do assistente. Qualquer front (terminal, GUI, voz) implementa isto."""
import time


class Saida:
    def falar(self, fala):
        """fala: models.Fala."""
        raise NotImplementedError

    def perguntar(self, texto, opcoes):
        """opcoes: lista de (chave, rotulo). Retorna a chave escolhida."""
        raise NotImplementedError

    def fechar(self):
        pass

    @staticmethod
    def interpretar(resposta, opcoes):
        resposta = resposta.strip().lower()
        if resposta.isdigit() and 1 <= int(resposta) <= len(opcoes):
            return opcoes[int(resposta) - 1][0]
        for chave, rotulo in opcoes:
            if resposta and (resposta == chave or rotulo.lower().startswith(resposta)):
                return chave
        return None


class SaidaTeste(Saida):
    """Minima: print e input, sem cores."""

    def falar(self, fala):
        print(fala.texto, flush=True)
        time.sleep(fala.pausa)

    def perguntar(self, texto, opcoes):
        print(texto, flush=True)
        for i, (_, rotulo) in enumerate(opcoes, 1):
            print(f"  {i}) {rotulo}")
        while True:
            try:
                resposta = input("> ")
            except EOFError:
                return opcoes[-1][0]
            escolha = self.interpretar(resposta, opcoes)
            if escolha:
                return escolha
            print("Não entendi, tenta de novo.")
