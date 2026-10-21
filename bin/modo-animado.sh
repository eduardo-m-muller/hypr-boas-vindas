#!/usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$DIR/.."
MARCA="$HOME/.cache/hypr-boas-vindas/coletando"

mkdir -p "$(dirname "$MARCA")"
touch "$MARCA"
( "$RAIZ/venv/bin/python" "$RAIZ/assistente/coletor.py" >/dev/null 2>&1; rm -f "$MARCA" ) &

if command -v kitty >/dev/null 2>&1; then
	kitty --class boas-vindas -e "$RAIZ/venv/bin/python" "$RAIZ/assistente/assistente.py" --terminal
else
	printf 'Kitty não encontrado; executando nesta sessão do terminal.\n' >&2
	"$RAIZ/venv/bin/python" "$RAIZ/assistente/assistente.py" --terminal
fi
