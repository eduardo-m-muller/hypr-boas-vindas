"""Tempo de PC: uptime atual e quanto tempo ficou ligado ontem (historico de boots do journalctl)."""
import json
import subprocess
from dataclasses import asdict
from datetime import datetime, timedelta

from ..models import Pc


def _uptime_min():
    with open("/proc/uptime", encoding="utf-8") as f:
        return int(float(f.read().split()[0]) / 60)


def _boots():
    saida = subprocess.run(
        ["journalctl", "--list-boots", "-o", "json", "--no-pager"],
        capture_output=True, text=True, timeout=10, check=True,
    ).stdout
    return json.loads(saida)


def _minutos_no_intervalo(boots, inicio, fim):
    total = 0.0
    for boot in boots:
        a = max(float(boot["first_entry"]) / 1e6, inicio.timestamp())
        z = min(float(boot["last_entry"]) / 1e6, fim.timestamp())
        if z > a:
            total += z - a
    return int(total / 60)


def coletar(cfg):
    agora = datetime.now().astimezone()
    hoje_0h = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    ontem_0h = hoje_0h - timedelta(days=1)
    ontem_min = None
    try:
        ontem_min = _minutos_no_intervalo(_boots(), ontem_0h, hoje_0h)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
        pass
    return asdict(Pc(uptime_min=_uptime_min(), ontem_min=ontem_min))
