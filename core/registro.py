"""Monta o cofre com os modulos ativos no config.toml. Modulo novo = uma linha aqui."""
from .cofre import Cofre
from .providers import clima, hora, tarefas


def criar_cofre(cfg):
    cofre = Cofre(cfg)
    cofre.registrar("hora", hora.coletar)
    if cfg["clima"]["ativo"]:
        cofre.registrar("clima", clima.coletar)
    if cfg["tarefas"]["ativo"]:
        cofre.registrar("tarefas", tarefas.coletar)
    return cofre
