"""Busca o clima atual na Open-Meteo (gratis, sem chave de API)."""
import json
import urllib.parse
import urllib.request

from config import FUSO, LATITUDE, LONGITUDE

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


def descricao(codigo):
    return CODIGOS.get(codigo, "tempo indefinido")


def obter_clima(timeout=4):
    """Retorna um dicionario com o clima, ou None se der qualquer erro."""
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "temperature_2m,apparent_temperature,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": FUSO,
        "forecast_days": 1,
    }
    url = URL + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resposta:
            dados = json.load(resposta)
        atual = dados["current"]
        dia = dados["daily"]
        return {
            "descricao": descricao(atual["weather_code"]),
            "temp": atual["temperature_2m"],
            "sensacao": atual["apparent_temperature"],
            "maxima": dia["temperature_2m_max"][0],
            "minima": dia["temperature_2m_min"][0],
            "chuva": dia["precipitation_probability_max"][0] or 0,
        }
    except (OSError, ValueError, KeyError, IndexError):
        return None


if __name__ == "__main__":
    print(obter_clima())
