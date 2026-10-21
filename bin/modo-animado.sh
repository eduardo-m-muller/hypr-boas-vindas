#!/usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$DIR/.."
MARCA="$HOME/.cache/hypr-boas-vindas/coletando"

mkdir -p "$(dirname "$MARCA")"
touch "$MARCA"
( "$RAIZ/venv/bin/python" "$RAIZ/assistente/coletor.py" >/dev/null 2>&1; rm -f "$MARCA" ) &

kitty --class boas-vindas -e python3 "$RAIZ/assistente/assistente.py"
