"""Mede o deslocamento entre o audio de uma camera e uma gravacao de voz (correlacao cruzada).

Uso: python scripts/sincronizar.py videos/<projeto> cam1 voz2

O resultado "tempo_voz = tempo_cam + X" e o numero que vai na tabela TAKES de cortes.py.
Pico perto de 1 indica sincronia confiavel; abaixo de ~0.5, nao confie.
"""
import sys

import numpy as np

from kit_comum import Projeto, carregar_audio, volume_db


def envelope(x: np.ndarray) -> np.ndarray:
    e = volume_db(x, 160)
    return (e - e.mean()) / (e.std() + 1e-9)


def main() -> None:
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    p = Projeto(sys.argv[1])
    a = envelope(carregar_audio(p.arquivo_bruto(sys.argv[2])))
    b = envelope(carregar_audio(p.arquivo_bruto(sys.argv[3])))
    n = 1 << int(np.ceil(np.log2(len(a) + len(b))))
    c = np.fft.irfft(np.fft.rfft(b, n) * np.conj(np.fft.rfft(a, n)), n)
    lag = int(np.argmax(c))
    lag = lag if lag < n // 2 else lag - n
    print(f"{sys.argv[2]} -> {sys.argv[3]}: tempo_voz = tempo_cam + {lag / 100:.2f}s (pico {c.max() / len(a):.2f})")


if __name__ == "__main__":
    main()
