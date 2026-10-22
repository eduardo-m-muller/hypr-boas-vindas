"""Roteiro de falas: textos com variacoes, tom e pausa. O front decide cor/voz."""
import random
from datetime import datetime

from . import soltas
from .models import Fala


def _v(*opcoes):
    return random.choice(opcoes)


def _bloco(falas):
    """Marca o fim de um bloco com uma pausa."""
    if falas:
        falas[-1].pausa = 0.4
    return falas


def prazo_humano(prazo_iso):
    try:
        prazo = datetime.fromisoformat(prazo_iso.replace("Z", "+00:00")).astimezone()
    except (ValueError, AttributeError):
        return "sem prazo definido"
    dias = (prazo.date() - datetime.now().astimezone().date()).days
    hora = f"{prazo:%H:%M}"
    if dias <= 0:
        return f"hoje às {hora}"
    if dias == 1:
        return f"amanhã às {hora}"
    return f"dia {prazo:%d/%m} às {hora}"


def _tom_prazo(cfg, horas):
    if horas is None:
        return "normal"
    a = cfg["alertas"]["tarefa"]
    if horas < a["critico_horas"]:
        return "critico"
    if horas < a["aviso_horas"]:
        return "aviso"
    return "normal"


def aviso_sono(cfg, hora):
    s = cfg["sono"]
    if not s["ativo"]:
        return []
    h = int(hora["hora"][:2])
    if h >= s["critico_a_partir_de"] or h < s["madrugada_ate"]:
        return [Fala(_v("Já está bem tarde, hein. Seu corpo agradece se você for dormir logo.",
                        "Está tarde demais. Não esquece de dormir hoje."), "critico")]
    if h >= s["aviso_a_partir_de"]:
        limite = s["aviso_a_partir_de"]
        return [Fala(_v(f"Já passou das {limite} horas. Vai pensando em descansar.",
                        "A noite já vai longe. Não demora muito hoje."), "aviso")]
    return []


def fala_clima(cfg, clima):
    cidade = clima["cidade"]
    desc = clima["descricao"]
    temp = round(clima["temperatura"])
    minima = round(clima["minima"])
    maxima = round(clima["maxima"])
    chuva = clima["chuva_pct"]
    falas = [
        Fala(_v(f"Em {cidade} está {desc}, {temp} graus.",
                f"Lá fora, {desc} e {temp} graus."), "normal"),
        Fala(f"Hoje a mínima é {minima} e a máxima {maxima}.", "normal"),
    ]
    if chuva >= cfg["alertas"]["chuva"]["aviso_acima_de"]:
        falas.append(Fala(_v(f"Tem {chuva} por cento de chance de chuva, leva o guarda-chuva.",
                             f"Atenção: {chuva} por cento de chance de chuva. Guarda-chuva na mochila."),
                          "aviso"))
    return falas


def abertura(cfg, hora, clima, extras=None):
    nome = cfg["usuario"]["nome"]
    falas = []
    if hora:
        saud = hora["saudacao"]
        data = hora["data_extenso"]
        h = hora["hora"]
        falas.append(Fala(_v(f"{saud}, {nome}!",
                             f"E aí, {nome}! {saud}.",
                             f"{saud}, {nome}. Tudo bem?"), "titulo", 0.4))
        falas.append(Fala(_v(f"Hoje é {data}.", f"Estamos em {data}."), "normal"))
        falas.append(Fala(_v(f"Agora são {h}.", f"São {h}."), "normal", 0.4))
    else:
        falas.append(Fala(f"Oi, {nome}!", "titulo", 0.4))
    if clima:
        falas.extend(_bloco(fala_clima(cfg, clima)))
    falas.extend(soltas.escolher(cfg, extras or {}))
    if hora:
        falas.extend(_bloco(aviso_sono(cfg, hora)))
    return falas


def pergunta():
    return _v("E aí, o que vai ser hoje?",
              "Me diz, o que você quer fazer agora?",
              "Bora, o que vai ser: jogar, estudar, programar ou só mexer no PC?")


def esperando_tarefas():
    return Fala(_v("Deixa eu ver o Sala do Futuro...",
                   "Só um instante, estou olhando suas tarefas."), "suave")


def _estudar(cfg, res):
    if res is None:
        return [Fala("O Sala do Futuro está demorando demais. Tenta de novo daqui a pouco.", "aviso")]
    if not res.ok:
        erro = str(res.erro)
        if "login_falhou" in erro:
            return [Fala("Não consegui entrar no Sala do Futuro. Confere o RA e a senha no .env.", "aviso")]
        return [Fala("Não consegui ver o Sala do Futuro agora.", "aviso")]
    dados = res.dados
    n = dados["pendentes"]
    if n == 0:
        return [Fala(_v("Você não tem nenhuma tarefa pendente. Estudo livre hoje.",
                        "Nenhuma tarefa pendente. Dá pra estudar o que quiser."), "normal")]
    total = "1 tarefa pendente" if n == 1 else f"{n} tarefas pendentes"
    proxima = dados["itens"][0]
    titulo = proxima["titulo"]
    quando = prazo_humano(proxima["prazo_iso"])
    tom = _tom_prazo(cfg, proxima["horas_restantes"])
    falas = [Fala(_v(f"Você tem {total}.", f"Tem {total} esperando por você."), "aviso"),
             Fala(f"A mais urgente é {titulo}, e vence {quando}.", tom)]
    if dados.get("desatualizado"):
        falas.append(Fala("Esses dados podem estar um pouco desatualizados.", "suave"))
    return falas


def _jogar(cfg, res):
    if res is not None and res.ok and res.dados["itens"]:
        proxima = res.dados["itens"][0]
        horas = proxima["horas_restantes"]
        if horas is not None and horas < 24:
            titulo = proxima["titulo"]
            quando = prazo_humano(proxima["prazo_iso"])
            return [Fala(f"Só um aviso antes de jogar: {titulo} vence {quando}. Mas a decisão é sua.", "aviso"),
                    Fala("Bom jogo!", "normal")]
    return [Fala(_v("Bom jogo!", "Boa partida!", "Diverte-se."), "normal")]


def modo(chave, cfg, tarefas):
    """tarefas: Resultado do cofre, ou None se ainda nao ficou pronto."""
    if chave == "estudar":
        return _estudar(cfg, tarefas)
    if chave == "jogar":
        return _jogar(cfg, tarefas)
    if chave == "programar":
        return [Fala(_v("Bora codar.", "Boa, bom código hoje.", "Terminal aberto, boa sessão."), "normal")]
    return [Fala(_v("Beleza, fico por aqui. É só chamar.", "Fechou. Qualquer coisa, me chama."), "normal")]
