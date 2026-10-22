"""Modos: o que cada escolha abre no PC. Configuravel em [modos.*] no config.toml."""
import os
import subprocess

PADRAO = {
    "jogar": {"rotulo": "Jogar", "acao": [["steam"]]},
    "estudar": {"rotulo": "Estudar", "acao": [["firefox", "https://saladofuturo.educacao.sp.gov.br"]]},
    "programar": {"rotulo": "Programar / trabalhar", "acao": [["kitty", "--directory", "~/projetos"]]},
    "livre": {"rotulo": "Só mexer no PC", "acao": []},
}


def carregar(cfg):
    modos = {chave: dict(valor) for chave, valor in PADRAO.items()}
    for chave, extra in cfg.get("modos", {}).items():
        modos.setdefault(chave, {"rotulo": chave, "acao": []}).update(extra)
    return modos


def executar(acoes, de_verdade=True):
    """Dispara cada comando solto do terminal. Retorna os comandos (com ~ expandido)."""
    feitos = []
    for comando in acoes:
        comando = [os.path.expanduser(parte) for parte in comando]
        feitos.append(comando)
        if de_verdade:
            try:
                subprocess.Popen(comando, start_new_session=True,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except OSError:
                pass
    return feitos
