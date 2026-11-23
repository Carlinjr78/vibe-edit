"""Gera os efeitos sonoros padrao do kit (pop, whoosh e stamp) por sintese, sem amostra de terceiros.

Uso: python scripts/sfx_sinteticos.py [pasta]   (padrao: assets/livre/sfx)

Sao originais, entao podem ir em qualquer video publicado. Para trocar por outro som, basta
colocar um .wav com o mesmo nome na pasta.
"""
import sys
import wave
from pathlib import Path

import numpy as np

SR = 48000
KIT = Path(__file__).resolve().parent.parent


def _tempo(dur: float) -> np.ndarray:
    return np.arange(int(SR * dur)) / SR


def _rampa(n: int, ataque: float = 0.003) -> np.ndarray:
    """Evita clique no comeco e no fim."""
    env = np.ones(n)
    a = max(1, int(SR * ataque))
    env[:a] = np.linspace(0, 1, a)
    env[-a:] *= np.linspace(1, 0, a)
    return env


def pop(dur: float = 0.2) -> np.ndarray:
    """Bolha curta: seno que sobe de tom e some rapido."""
    t = _tempo(dur)
    freq = 380 + 900 * (1 - np.exp(-t * 60))
    fase = 2 * np.pi * np.cumsum(freq) / SR
    som = np.sin(fase) * np.exp(-t * 28)
    return som * _rampa(len(t))


def whoosh(dur: float = 0.5, semente: int = 7) -> np.ndarray:
    """Ar passando: ruido filtrado com o corte subindo e descendo, volume em sino."""
    t = _tempo(dur)
    ruido = np.random.default_rng(semente).standard_normal(len(t))
    corte = 300 + 4200 * np.sin(np.pi * t / dur) ** 2  # Hz
    alfa = 1 - np.exp(-2 * np.pi * corte / SR)
    saida, y = np.empty_like(ruido), 0.0
    for i, x in enumerate(ruido):  # passa-baixa de 1 polo com corte variavel
        y += alfa[i] * (x - y)
        saida[i] = y
    env = np.sin(np.pi * t / dur) ** 1.5
    return saida * env * _rampa(len(t))


def stamp(dur: float = 0.4, semente: int = 3) -> np.ndarray:
    """Carimbo: batida grave com um estalo de ruido no comeco."""
    t = _tempo(dur)
    freq = 55 + 110 * np.exp(-t * 30)
    corpo = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t * 11)
    estalo = np.random.default_rng(semente).standard_normal(len(t)) * np.exp(-t * 90) * 0.6
    return (corpo + estalo) * _rampa(len(t), 0.001)


def gravar(destino: Path, som: np.ndarray, pico: float = 0.89) -> None:
    som = som / (np.abs(som).max() or 1) * pico
    pcm = (np.clip(som, -1, 1) * 32767).astype(np.int16)
    estereo = np.repeat(pcm[:, None], 2, axis=1)
    with wave.open(str(destino), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(estereo.tobytes())


def main() -> None:
    pasta = Path(sys.argv[1]) if len(sys.argv) > 1 else KIT / "assets" / "livre" / "sfx"
    pasta.mkdir(parents=True, exist_ok=True)
    for nome, gerar in (("pop", pop), ("whoosh", whoosh), ("stamp", stamp)):
        gravar(pasta / f"{nome}.wav", gerar())
        print(f"[sfx] {pasta / f'{nome}.wav'}")


if __name__ == "__main__":
    main()
