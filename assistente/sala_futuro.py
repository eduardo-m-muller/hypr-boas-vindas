"""Consulta de tarefas pendentes no Sala do Futuro (em construcao)."""
import os

import env

env.carregar()

RA = os.environ.get("SALA_RA", "")
SENHA = os.environ.get("SALA_SENHA", "")


def configurado():
    return bool(RA and SENHA)


def tarefas_pendentes():
    """Retorna o numero de tarefas pendentes, ou None se nao der."""
    if not configurado():
        return None
    # TODO: login + leitura da lista de tarefas (etapa 4b)
    return None


if __name__ == "__main__":
    print("configurado:", configurado())
    print("pendentes:", tarefas_pendentes())
