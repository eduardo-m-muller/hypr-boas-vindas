"""Voz online opcional usando Edge TTS e ffplay."""
import asyncio
import queue
import shutil
import subprocess
import threading

try:
    import edge_tts
except ImportError:
    edge_tts = None

VOZ = "pt-BR-FranciscaNeural"
FILA = queue.Queue()
CONDICAO = threading.Condition()
PENDENTES = 0
TRABALHADOR = None


def disponivel():
    return edge_tts is not None and shutil.which("ffplay") is not None


async def _falar(texto):
    reprodutor = subprocess.Popen(
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", "-f", "mp3", "-i", "pipe:0"],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    loop = asyncio.get_running_loop()
    try:
        comunicacao = edge_tts.Communicate(texto, VOZ)
        async for parte in comunicacao.stream():
            if parte["type"] == "audio":
                reprodutor.stdin.write(parte["data"])
        reprodutor.stdin.close()
        codigo = await loop.run_in_executor(None, reprodutor.wait)
        if codigo:
            raise subprocess.CalledProcessError(codigo, "ffplay")
    finally:
        if reprodutor.poll() is None:
            reprodutor.kill()
            await loop.run_in_executor(None, reprodutor.wait)


def _processar_fila():
    global PENDENTES
    while True:
        texto = FILA.get()
        try:
            asyncio.run(asyncio.wait_for(_falar(texto), timeout=18))
        except Exception:
            pass
        finally:
            FILA.task_done()
            with CONDICAO:
                PENDENTES -= 1
                CONDICAO.notify_all()


def enfileirar(texto):
    global PENDENTES, TRABALHADOR
    if not disponivel() or not texto.strip():
        return

    with CONDICAO:
        PENDENTES += 1
        FILA.put(texto)
        if TRABALHADOR is None or not TRABALHADOR.is_alive():
            TRABALHADOR = threading.Thread(target=_processar_fila, daemon=True)
            TRABALHADOR.start()


def aguardar(timeout=35):
    with CONDICAO:
        return CONDICAO.wait_for(lambda: PENDENTES == 0, timeout=timeout)