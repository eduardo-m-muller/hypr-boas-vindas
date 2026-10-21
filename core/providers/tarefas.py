"""Tarefas do Sala do Futuro: usa o cache se estiver fresco, senao roda o coletor."""
import fcntl
import json
import subprocess
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from ..config import RAIZ
from ..models import Tarefa, Tarefas

CACHE = Path.home() / ".cache/hypr-boas-vindas"
ARQUIVO = CACHE / "tarefas.json"
PYTHON = RAIZ / "venv/bin/python"
COLETOR = RAIZ / "assistente/coletor.py"


def _ler():
    try:
        return json.loads(ARQUIVO.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _fresco(dados, validade_min):
    if not dados or dados.get("estado") != "ok" or dados.get("desatualizado"):
        return False
    try:
        idade = datetime.now() - datetime.fromisoformat(dados["atualizado_em"])
    except (KeyError, ValueError):
        return False
    return idade.total_seconds() < validade_min * 60


def _horas_restantes(prazo_iso):
    try:
        prazo = datetime.fromisoformat(prazo_iso.replace("Z", "+00:00"))
        return round((prazo - datetime.now(prazo.tzinfo)).total_seconds() / 3600, 1)
    except (ValueError, AttributeError, TypeError):
        return None


def coletar(cfg, timeout=100):
    validade = cfg["tarefas"]["cache_validade_min"]
    dados = _ler()
    if not _fresco(dados, validade):
        CACHE.mkdir(parents=True, exist_ok=True)
        with open(CACHE / "coletor.lock", "w") as trava:
            fcntl.flock(trava, fcntl.LOCK_EX)
            dados = _ler()
            if not _fresco(dados, validade):
                subprocess.run([str(PYTHON), str(COLETOR)], timeout=timeout, capture_output=True)
                dados = _ler()
    if not dados:
        raise RuntimeError("sem_cache")
    if dados.get("estado") != "ok":
        raise RuntimeError(dados.get("estado", "desconhecido"))

    itens = []
    for t in dados.get("tarefas", []):
        itens.append(Tarefa(
            id=t.get("id"),
            titulo=t.get("titulo") or "sem título",
            prazo_iso=t.get("prazo"),
            horas_restantes=_horas_restantes(t.get("prazo")),
            prova=bool(t.get("prova")),
            redacao=bool(t.get("redacao")),
        ))
    itens.sort(key=lambda t: (t.horas_restantes is None, t.horas_restantes or 0))
    return asdict(Tarefas(
        pendentes=len(itens),
        itens=itens,
        atualizado_em=dados.get("atualizado_em"),
        desatualizado=bool(dados.get("desatualizado")),
    ))
