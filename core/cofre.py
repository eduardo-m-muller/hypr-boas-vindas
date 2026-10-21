"""Cofre: roda as fontes de dados em segundo plano e guarda os resultados ate alguem precisar."""
import threading
import time

from .models import Resultado


class Cofre:
    def __init__(self, cfg):
        self.cfg = cfg
        self._fontes = {}
        self._eventos = {}
        self._dados = {}
        self._lock = threading.Lock()

    def registrar(self, nome, funcao):
        """funcao(cfg) -> dict. Se levantar excecao, o resultado vira ok=False."""
        self._fontes[nome] = funcao
        self._eventos[nome] = threading.Event()

    def nomes(self):
        return list(self._fontes)

    def iniciar(self):
        """Dispara todas as fontes em paralelo e volta na hora."""
        for nome in self._fontes:
            threading.Thread(target=self._rodar, args=(nome,), daemon=True).start()

    def _rodar(self, nome):
        inicio = time.time()
        try:
            resultado = Resultado(nome, True, self._fontes[nome](self.cfg))
        except Exception as erro:
            texto = type(erro).__name__ + (": " + str(erro) if str(erro) else "")
            resultado = Resultado(nome, False, None, texto)
        resultado.ms = int((time.time() - inicio) * 1000)
        with self._lock:
            self._dados[nome] = resultado
        self._eventos[nome].set()

    def pronto(self, nome):
        evento = self._eventos.get(nome)
        return bool(evento and evento.is_set())

    def obter(self, nome, esperar=0):
        """Retorna o Resultado, esperando ate `esperar` segundos. None se ainda nao ficou pronto."""
        evento = self._eventos.get(nome)
        if evento is None:
            return None
        evento.wait(timeout=esperar)
        with self._lock:
            return self._dados.get(nome)
