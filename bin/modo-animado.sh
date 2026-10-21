#!/usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
kitty --class boas-vindas -e python3 "$DIR/../assistente/assistente.py"
