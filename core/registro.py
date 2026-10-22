"""Monta o cofre com os modulos ativos no config.toml. Modulo novo = uma linha na lista."""
from .cofre import Cofre
from .providers import clima, curiosidade, hora, noticias, pc, tarefas

MODULOS = (
    ("clima", clima),
    ("tarefas", tarefas),
    ("pc", pc),
    ("noticias", noticias),
    ("curiosidade", curiosidade),
)


def criar_cofre(cfg):
    cofre = Cofre(cfg)
    cofre.registrar("hora", hora.coletar)
    for nome, modulo in MODULOS:
        if cfg[nome]["ativo"]:
            cofre.registrar(nome, modulo.coletar)
    return cofre
