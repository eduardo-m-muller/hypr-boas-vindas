"""Papo solto: o assistente joga frases no ar, como um amigo puxando assunto."""
import random

from .models import Fala

RITMO = 0.6

ABRIDORES = [
    "Ah, antes que eu esqueça...",
    "Cara, deixa eu te contar uma coisa.",
    "Mudando de assunto...",
    "Sabe o que me veio na cabeça agora?",
    "Olha, não é nada demais, mas...",
    "Aproveitando que estamos aqui...",
    "Ei, lembrei de uma coisa.",
]

CONECTORES = [
    "Ah, e outra coisa.",
    "Aliás...",
    "E já que estamos aqui...",
    "Ah, lembrei de mais uma.",
    "Ah, e também...",
]

PAPO = [
    "Sei lá, deu vontade de puxar assunto.",
    "Tava aqui pensando em nada, como sempre.",
    "Bateu uma saudade de papo furado.",
    "Esse silêncio aqui tá estranho, né?",
    "Sempre dizem que café resolve tudo. Eu não tenho como testar, mas confio.",
    "Hoje o dia tá com cara de que vai render, sei lá.",
    "Sabe quando você tem vontade de falar e não tem assunto? Então.",
    "Nada de mais por aqui, só passando pra bater um papo.",
]

REACOES_CURIOSIDADE = [
    "Doido, né?",
    "Enfim, só queria dividir isso.",
    "Pronto, falei.",
    "Eu acho isso incrível, sei lá.",
    "Fica aí na cabeça, né?",
]


def _v(*opcoes):
    return random.choice(opcoes)


def _fecha(texto):
    texto = texto.strip()
    return texto if texto and texto[-1] in ".!?" else texto + "."


def _duracao(minutos):
    h, m = divmod(int(minutos), 60)
    partes = []
    if h:
        partes.append("1 hora" if h == 1 else f"{h} horas")
    if m:
        partes.append("1 minuto" if m == 1 else f"{m} minutos")
    return " e ".join(partes) if partes else "menos de um minuto"


def _pc(dados):
    falas = []
    ontem = dados.get("ontem_min")
    uptime = dados.get("uptime_min", 0)
    if ontem is not None and ontem >= 10:
        d = _duracao(ontem)
        falas.append(Fala(_v(f"Ontem o PC ficou ligado por {d}.",
                             f"Fazendo as contas aqui: ontem foram {d} de PC ligado.",
                             f"Sabia que ontem o PC passou {d} ligado?"), "normal"))
        if ontem >= 600:
            falas.append(Fala(_v("Foi bastante tempo, hein.", "Haja disposição."), "normal"))
        elif ontem <= 120:
            falas.append(Fala("Dia tranquilo, então.", "normal"))
    elif uptime >= 120:
        falas.append(Fala(_v(f"O PC tá ligado há {_duracao(uptime)}, hein.",
                             f"Faz {_duracao(uptime)} que esse PC não desliga."), "normal"))
    return falas or None


def _noticia(dados):
    if not dados["itens"]:
        return None
    titulo = _fecha(random.choice(dados["itens"])["titulo"])
    fonte = dados["fonte"]
    return [Fala(_v(f"Vi essa manchete em {fonte}: {titulo}",
                    f"Olha o que saiu em {fonte}: {titulo}",
                    f"Você viu isso? Em {fonte} saiu: {titulo}",
                    f"Sei lá se você viu, mas em {fonte} saiu: {titulo}",
                    f"Passando os olhos por {fonte}, apareceu isso: {titulo}"), "normal")]


def _curiosidade(dados):
    texto = _fecha(dados["texto"])
    falas = [Fala(_v("Cara, você sabia? " + texto,
                     "Curiosidade aleatória: " + texto,
                     "Jogando conversa fora aqui: " + texto,
                     "Sabe o que eu lembrei do nada? " + texto,
                     "Sei lá, mas achei isso interessante: " + texto), "normal")]
    if random.random() < 0.5:
        falas.append(Fala(random.choice(REACOES_CURIOSIDADE), "normal"))
    return falas


def _papo():
    return [Fala(random.choice(PAPO), "normal")]


CONSTRUTORES = {"pc": _pc, "noticias": _noticia, "curiosidade": _curiosidade}


def escolher(cfg, extras):
    """extras: nome do modulo -> dados (ou None). Monta o papo solto da abertura."""
    candidatos = []
    for nome, construir in CONSTRUTORES.items():
        dados = extras.get(nome)
        if dados:
            falas = construir(dados)
            if falas:
                candidatos.append(falas)
    if cfg["soltas"].get("papo_furado", True):
        candidatos.append(_papo())

    n = min(cfg["soltas"]["quantidade"], len(candidatos))
    saida = []
    for i, falas in enumerate(random.sample(candidatos, n)):
        if i == 0 and random.random() < 0.7:
            saida.append(Fala(random.choice(ABRIDORES), "normal", 0.3))
        elif i > 0:
            saida.append(Fala(random.choice(CONECTORES), "normal", 0.3))
        saida.extend(falas)
    for fala in saida:
        fala.ritmo = RITMO
    if saida:
        saida[-1].pausa = 0.4
    return saida
