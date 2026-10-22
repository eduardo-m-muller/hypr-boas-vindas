"""Curiosidades de tecnologia e ciencia para o assistente soltar no ar."""
import random
from dataclasses import asdict

from ..models import Curiosidade

CURIOSIDADES = [
    "O primeiro bug de computador de verdade foi uma mariposa presa num relé do Harvard Mark II, em 1947.",
    "A primeira mensagem da ARPANET, em 1969, era a palavra login, mas o sistema caiu depois das duas primeiras letras.",
    "O nome da linguagem Python vem do grupo de humor Monty Python, não da cobra.",
    "O Git foi criado por Linus Torvalds em 2005, em poucas semanas, para cuidar do código do kernel Linux.",
    "O Hyprland, o gerenciador de janelas, é escrito em C++ e foi criado por um desenvolvedor conhecido como Vaxry.",
    "A palavra robô vem do tcheco robota, que significa trabalho forçado.",
    "Um dia em Vênus dura mais que um ano em Vênus.",
    "A luz do Sol leva cerca de oito minutos para chegar até a Terra.",
    "Polvos têm três corações.",
    "O Linux foi anunciado por Linus Torvalds em 1991, como um projeto de hobby.",
]


def coletar(cfg):
    return asdict(Curiosidade(texto=random.choice(CURIOSIDADES)))
