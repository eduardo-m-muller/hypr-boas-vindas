"""Hora, data e saudacao."""
from dataclasses import asdict
from datetime import datetime

from ..models import Hora

DIAS = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
        "sexta-feira", "sábado", "domingo"]
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]


def periodo(h):
    if h < 5:
        return "madrugada"
    if h < 12:
        return "manha"
    if h < 18:
        return "tarde"
    return "noite"


def saudacao(h):
    if 5 <= h < 12:
        return "Bom dia"
    if 12 <= h < 18:
        return "Boa tarde"
    return "Boa noite"


def coletar(cfg):
    agora = datetime.now().astimezone()
    return asdict(Hora(
        saudacao=saudacao(agora.hour),
        periodo=periodo(agora.hour),
        hora=f"{agora:%H:%M}",
        data_extenso=f"{DIAS[agora.weekday()]}, {agora.day} de {MESES[agora.month - 1]}",
        iso=agora.isoformat(timespec="seconds"),
    ))
