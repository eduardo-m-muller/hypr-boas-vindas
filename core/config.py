"""Carrega config.toml (ajustes) e .env (segredos)."""
import copy
import os
import tomllib
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

PADRAO = {
    "usuario": {"nome": "Eduardo"},
    "clima": {
        "ativo": True,
        "cidade": "Santo André",
        "latitude": -23.6639,
        "longitude": -46.5383,
        "fuso": "America/Sao_Paulo",
    },
    "tarefas": {"ativo": True, "cache_validade_min": 30},
    "visual": {"atraso_digitacao": 0.03, "linha_em_branco_entre_blocos": False, "fechar_apos_s": 6},
    "sono": {"ativo": True, "aviso_a_partir_de": 22, "critico_a_partir_de": 23, "madrugada_ate": 5},
    "alertas": {
        "tarefa": {"aviso_horas": 72, "critico_horas": 24},
        "chuva": {"aviso_acima_de": 50},
    },
}


def _mesclar(base, extra):
    for chave, valor in extra.items():
        if isinstance(valor, dict) and isinstance(base.get(chave), dict):
            _mesclar(base[chave], valor)
        else:
            base[chave] = valor
    return base


def carregar_env():
    arquivo = RAIZ / ".env"
    if not arquivo.exists():
        return
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        os.environ.setdefault(chave.strip(), valor.strip().strip(chr(34)))


def carregar():
    """Retorna a configuracao: padroes + config.toml. Tambem carrega o .env."""
    carregar_env()
    cfg = copy.deepcopy(PADRAO)
    arquivo = RAIZ / "config.toml"
    if arquivo.exists():
        with arquivo.open("rb") as f:
            _mesclar(cfg, tomllib.load(f))
    return cfg
