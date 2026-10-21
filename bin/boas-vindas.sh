#!/usr/bin/env bash
# Menu de inicializacao do Hyprland

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ESCOLHA=$(printf "⚡ Inicialização rápida\n✨ Inicialização com animação" | \
  wofi --dmenu \
       --prompt "Como quer iniciar?" \
       --width 420 --height 170 \
       --cache-file /dev/null)

case "$ESCOLHA" in
  *animação*)
    "$DIR/modo-animado.sh"
    ;;
  *)
    # rapida, Esc ou fechar o menu: nao faz nada
    exit 0
    ;;
esac
