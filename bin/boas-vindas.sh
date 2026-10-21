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
    # marca que esta coletando e dispara a coleta em segundo plano
    mkdir -p "$HOME/.cache/hypr-boas-vindas"
    touch "$HOME/.cache/hypr-boas-vindas/coletando"
    setsid "$DIR/coletar-tarefas.sh" >/dev/null 2>&1 &
    "$DIR/modo-animado.sh"
    ;;
  *)
    # rapida, Esc ou fechar o menu: nao faz nada
    exit 0
    ;;
esac
