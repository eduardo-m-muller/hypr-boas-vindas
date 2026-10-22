"""Roteiro de falas: textos com variacoes, escolhidos ao acaso para nao repetir."""
import random
from datetime import datetime


def _v(*opcoes):
    return random.choice(opcoes)


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


def aviso_sono(cfg, hora):
    s = cfg["sono"]
    if not s["ativo"]:
        return []
    h = int(hora["hora"][:2])
    if h >= s["critico_a_partir_de"] or h < s["madrugada_ate"]:
        return [_v("Já está bem tarde, hein. Seu corpo agradece se você for dormir logo.",
                   "Está tarde demais. Não esquece de dormir hoje.")]
    if h >= s["aviso_a_partir_de"]:
        limite = s["aviso_a_partir_de"]
        return [_v(f"Já passou das {limite} horas. Vai pensando em descansar.",
                   "A noite já vai longe. Não demora muito hoje.")]
    return []


def fala_clima(cfg, clima):
    cidade = clima["cidade"]
    desc = clima["descricao"]
    temp = round(clima["temperatura"])
    minima = round(clima["minima"])
    maxima = round(clima["maxima"])
    chuva = clima["chuva_pct"]
    linhas = [
        _v(f"Em {cidade} está {desc}, {temp} graus.",
           f"Lá fora, {desc} e {temp} graus."),
        f"Hoje a mínima é {minima} e a máxima {maxima}.",
    ]
    if chuva >= cfg["alertas"]["chuva"]["aviso_acima_de"]:
        linhas.append(_v(f"Tem {chuva} por cento de chance de chuva, leva o guarda-chuva.",
                         f"Atenção: {chuva} por cento de chance de chuva. Guarda-chuva na mochila."))
    return linhas


def abertura(cfg, hora, clima):
    nome = cfg["usuario"]["nome"]
    falas = []
    if hora:
        saud = hora["saudacao"]
        falas.append(_v(f"{saud}, {nome}!",
                        f"E aí, {nome}! {saud}.",
                        f"{saud}, {nome}. Tudo bem?"))
        data = hora["data_extenso"]
        h = hora["hora"]
        falas.append(_v(f"Hoje é {data}, e são {h}.",
                        f"São {h} de {data}."))
        falas.extend(aviso_sono(cfg, hora))
    else:
        falas.append(f"Oi, {nome}!")
    if clima:
        falas.extend(fala_clima(cfg, clima))
    return falas


def pergunta():
    return _v("E aí, o que vai ser hoje?",
              "Me diz, o que você quer fazer agora?",
              "Bora, o que vai ser: jogar, estudar, programar ou só mexer no PC?")


def esperando_tarefas():
    return _v("Deixa eu ver o Sala do Futuro...",
              "Só um instante, estou olhando suas tarefas.")


def _estudar(res):
    if res is None:
        return ["O Sala do Futuro está demorando demais. Tenta de novo daqui a pouco."]
    if not res.ok:
        return ["Não consegui ver o Sala do Futuro agora."]
    dados = res.dados
    n = dados["pendentes"]
    if n == 0:
        return [_v("Você não tem nenhuma tarefa pendente. Estudo livre hoje.",
                   "Nenhuma tarefa pendente. Dá pra estudar o que quiser.")]
    total = "1 tarefa pendente" if n == 1 else f"{n} tarefas pendentes"
    proxima = dados["itens"][0]
    titulo = proxima["titulo"]
    quando = prazo_humano(proxima["prazo_iso"])
    linhas = [_v(f"Você tem {total}.", f"Tem {total} esperando por você."),
              f"A mais urgente é {titulo}, e vence {quando}."]
    if dados.get("desatualizado"):
        linhas.append("Esses dados podem estar um pouco desatualizados.")
    return linhas


def _jogar(res):
    if res is not None and res.ok and res.dados["itens"]:
        proxima = res.dados["itens"][0]
        horas = proxima["horas_restantes"]
        if horas is not None and horas < 24:
            titulo = proxima["titulo"]
            quando = prazo_humano(proxima["prazo_iso"])
            return [f"Só um aviso antes de jogar: {titulo} vence {quando}. Mas a decisão é sua.",
                    "Bom jogo!"]
    return [_v("Bom jogo!", "Boa partida!", "Diverte-se.")]


def modo(chave, cfg, tarefas):
    """tarefas: Resultado do cofre, ou None se ainda nao ficou pronto."""
    if chave == "estudar":
        return _estudar(tarefas)
    if chave == "jogar":
        return _jogar(tarefas)
    if chave == "programar":
        return [_v("Bora codar.", "Boa, bom código hoje.", "Terminal aberto, boa sessão.")]
    return [_v("Beleza, fico por aqui. É só chamar.", "Fechou. Qualquer coisa, me chama.")]
