# Hypr Boas-Vindas

Menu de inicialização para o Hyprland. O modo animado exibe saudação, data,
hora, aviso de sono, clima e tarefas pendentes do Sala do Futuro.

## Requisitos

- Hyprland, Wofi e Kitty
- Python 3.8 ou superior e FFmpeg (`ffplay`)
- Firefox instalado pelo Playwright para coletar tarefas

## Instalação

Na raiz do projeto, crie o ambiente Python e instale a dependência:

```sh
python3 -m venv venv
venv/bin/python -m pip install -r requirements.txt
venv/bin/python -m playwright install firefox
```

Para consultar tarefas, copie `.env.example` para `.env` e preencha as
credenciais do Sala do Futuro. Sem credenciais, o assistente continua
funcionando, mas não consegue atualizar as tarefas.

A voz usa o Edge TTS em português (Francisca), sem chave de API. Ela requer
internet; as frases exibidas no terminal são enviadas ao serviço para síntese.
Se a voz ou a rede falhar, o texto continua normalmente.

Configure o Hyprland para executar `bin/boas-vindas.sh` após o login. O menu
rápido fecha sem iniciar o assistente; a opção animada abre o assistente e
atualiza as tarefas em segundo plano.

## Recursos

- [x] Menu de inicialização rápida ou animada
- [x] Assistente com data, hora e aviso de sono
- [x] Clima via Open-Meteo
- [x] Coleta e cache local de tarefas do Sala do Futuro
- [x] Exibição progressiva do texto
