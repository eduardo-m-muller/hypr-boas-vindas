"""Manchetes de um feed RSS (configuravel em [noticias] no config.toml)."""
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict

from ..models import Noticia, Noticias


def coletar(cfg, timeout=6):
    c = cfg["noticias"]
    pedido = urllib.request.Request(c["feed"], headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"})
    with urllib.request.urlopen(pedido, timeout=timeout) as resposta:
        raiz = ET.fromstring(resposta.read())
    itens = []
    for item in raiz.iter("item"):
        titulo = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if titulo:
            itens.append(Noticia(titulo=titulo, link=link))
        if len(itens) >= c["max_itens"]:
            break
    if not itens:
        raise RuntimeError("feed_vazio")
    return asdict(Noticias(fonte=c["fonte"], itens=itens))
