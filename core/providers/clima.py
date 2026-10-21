"""Clima atual via Open-Meteo (gratis, sem chave de API)."""
import json
import urllib.parse
import urllib.request
from dataclasses import asdict

from ..models import Clima

URL = "https://api.open-meteo.com/v1/forecast"

CODIGOS = {
    0: "céu limpo", 1: "quase sem nuvens", 2: "parcialmente nublado",
    3: "nublado", 45: "neblina", 48: "neblina",
    51: "garoa fraca", 53: "garoa", 55: "garoa forte",
    61: "chuva fraca", 63: "chuva", 65: "chuva forte",
    80: "pancadas de chuva fracas", 81: "pancadas de chuva",
    82: "pancadas de chuva fortes",
    95: "tempestade", 96: "tempestade com granizo", 99: "tempestade com granizo",
}


def coletar(cfg, timeout=6):
    c = cfg["clima"]
    params = {
        "latitude": c["latitude"],
        "longitude": c["longitude"],
        "current": "temperature_2m,apparent_temperature,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": c["fuso"],
        "forecast_days": 1,
    }
    with urllib.request.urlopen(URL + "?" + urllib.parse.urlencode(params), timeout=timeout) as resposta:
        dados = json.load(resposta)
    atual = dados["current"]
    dia = dados["daily"]
    return asdict(Clima(
        cidade=c["cidade"],
        descricao=CODIGOS.get(atual["weather_code"], "tempo indefinido"),
        temperatura=atual["temperature_2m"],
        sensacao=atual["apparent_temperature"],
        minima=dia["temperature_2m_min"][0],
        maxima=dia["temperature_2m_max"][0],
        chuva_pct=int(dia["precipitation_probability_max"][0] or 0),
    ))
