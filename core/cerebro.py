"""Cerebro: conduz a conversa. Nao sabe de tela nem de voz, so usa a Saida."""
from . import falas, modos


class Cerebro:
    def __init__(self, cfg, cofre, saida, de_verdade=True):
        self.cfg = cfg
        self.cofre = cofre
        self.saida = saida
        self.de_verdade = de_verdade
        self.modos = modos.carregar(cfg)

    def _dados(self, nome, esperar=0):
        resultado = self.cofre.obter(nome, esperar=esperar)
        return resultado.dados if resultado and resultado.ok else None

    def abertura(self):
        hora = self._dados("hora", esperar=2)
        clima = self._dados("clima", esperar=4)
        extras = {nome: self._dados(nome, esperar=2) for nome in ("pc", "noticias", "curiosidade")}
        for fala in falas.abertura(self.cfg, hora, clima, extras):
            self.saida.falar(fala)

    def escolher_modo(self):
        opcoes = [(chave, modo["rotulo"]) for chave, modo in self.modos.items()]
        return self.saida.perguntar(falas.pergunta(), opcoes)

    def rodar_modo(self, chave):
        modo = self.modos[chave]
        if chave == "estudar" and not self.cofre.pronto("tarefas"):
            self.saida.falar(falas.esperando_tarefas())
        tarefas = self.cofre.obter("tarefas", esperar=90 if chave == "estudar" else 0)
        feitos = modos.executar(modo["acao"], self.de_verdade)
        if not self.de_verdade:
            for comando in feitos:
                print("[teste] abriria:", " ".join(comando))
        for fala in falas.modo(chave, self.cfg, tarefas):
            self.saida.falar(fala)

    def executar(self):
        """O cofre ja deve ter sido iniciado por quem chamou (no clique)."""
        self.abertura()
        chave = self.escolher_modo()
        self.rodar_modo(chave)
        return chave
