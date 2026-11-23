"""Mostra o volume de um trecho de voz para achar o ponto exato de corte.

Uso: python scripts/pausas.py videos/<projeto> voz6 44.30 44.90

Imprime um valor de dB a cada 20 ms e o ponto mais silencioso. O fim real de uma palavra
costuma estar depois do tempo dado pelo Whisper: corte onde o volume ja caiu para perto do piso.
"""
import sys

import numpy as np

from kit_comum import Projeto, carregar_audio, volume_db


def main() -> None:
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    p = Projeto(sys.argv[1])
    ini, fim = float(sys.argv[3]), float(sys.argv[4])
    db = volume_db(carregar_audio(p.arquivo_bruto(sys.argv[2])), 160)
    trecho = db[int(ini * 100):int(fim * 100)]
    k = int(np.argmin(np.convolve(trecho, np.ones(5) / 5, mode="same")))
    print(f"piso do arquivo (p10): {np.percentile(db, 10):.1f} dB | ponto mais silencioso: {ini + k / 100:.2f}s ({trecho[k]:.1f} dB)")
    for i in range(0, len(trecho), 2):
        print(f"{ini + i / 100:.2f}s {trecho[i]:6.1f} dB  {'#' * max(0, int(trecho[i] + 60))}")


if __name__ == "__main__":
    main()
