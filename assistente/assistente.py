#!/usr/bin/env python3
"""Assistente de boas-vindas: saudacao, data, hora, clima e aviso de sono."""
import sys
import time
from datetime import datetime

from clima import obter_clima
from config import CIDADE, NOME
from tarefas import linhas_tarefas

DIAS = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
        "sexta-feira", "sábado", "domingo"]
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]

CIANO = "\033[96m"
AMARELO = "\033[93m"
VERMELHO = "\033[91m"
NEGRITO = "\033[1m"
RESET = "\033[0m"


def saudacao(hora):
    if 5 <= hora < 12:
        return "Bom dia"
    if 12 <= hora < 18:
        return "Boa tarde"
    return "Boa noite"


def aviso_sono(hora):
    """Retorna (mensagem, cor) ou None se ainda nao for tarde."""
    if hora >= 23 or hora < 5:
        return "Já é tarde! Salva o que estiver fazendo e vai dormir.", VERMELHO
    if hora >= 22:
        return "Já passou das 22h. Vai pensando em descansar.", AMARELO
    return None


def digitar(texto, cor="", atraso=0.03):
    sys.stdout.write(cor)
    for letra in texto:
        sys.stdout.write(letra)
        sys.stdout.flush()
        time.sleep(atraso)
    sys.stdout.write(RESET + "\n")


def mostrar_clima():
    clima = obter_clima()
    if clima is None:
        digitar("Não consegui ver o clima agora (sem internet?).", AMARELO)
        return

    desc = clima["descricao"]
    temp = round(clima["temp"])
    sensacao = round(clima["sensacao"])
    minima = round(clima["minima"])
    maxima = round(clima["maxima"])
    chuva = round(clima["chuva"])

    digitar(f"Em {CIDADE}: {desc}, {temp}°C (sensação de {sensacao}°C).", CIANO)
    digitar(f"Hoje: mínima de {minima}°C e máxima de {maxima}°C.", CIANO)
    if chuva >= 50:
        digitar(f"Chance de chuva de {chuva}%: leva o guarda-chuva!", AMARELO + NEGRITO)


def mostrar_tarefas():
    for texto, cor in linhas_tarefas():
        digitar(texto, cor)


def main():
    agora = datetime.now()
    dia_semana = DIAS[agora.weekday()]
    mes = MESES[agora.month - 1]

    print()
    digitar(f"{saudacao(agora.hour)}, {NOME}!", CIANO + NEGRITO)
    time.sleep(0.4)
    digitar(f"Hoje é {dia_semana}, {agora.day} de {mes}.", CIANO)
    digitar(f"Agora são {agora:%H:%M}.", CIANO)
    time.sleep(0.4)

    mostrar_clima()

    mostrar_tarefas()
    time.sleep(0.4)

    aviso = aviso_sono(agora.hour)
    if aviso:
        time.sleep(0.4)
        mensagem, cor = aviso
        digitar(mensagem, cor + NEGRITO)

    time.sleep(5)


if __name__ == "__main__":
    main()
