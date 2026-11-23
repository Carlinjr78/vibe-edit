"""Coloca a musica sob a narracao: nivel baixo e abaixando sozinha quando ha voz.

Uso:
  python scripts/mixar_musica.py videos/<projeto>                 trilha chiptune original
  python scripts/mixar_musica.py videos/<projeto> musica.mp3      faixa propria (com licenca livre)
  python scripts/mixar_musica.py videos/<projeto> --nivel -31     mais baixa (padrao: -28; cada 6 = metade)

Gera public/music_ducked.wav. Rode depois de cortar.py e antes de montar_edl.py.
"""
import json
import sys

from kit_comum import Projeto, medir_loudness, rodar_ffmpeg
from musica_chiptune import compor

NIVEL_PADRAO = -28  # resulta em cerca de -35 LUFS sob a voz, uns 20 dB abaixo dela


def encaixar(faixa, destino, dur: float) -> None:
    """Repete ou corta a faixa na duracao do video, com entrada curta e saida de 2,5 s."""
    rodar_ffmpeg("-stream_loop", -1, "-i", faixa, "-t", dur,
                 "-af", f"afade=t=in:d=0.4,afade=t=out:st={max(0, dur - 2.5):.2f}:d=2.5", "-ar", 48000, "-ac", 2, destino)


def abaixar_sob_a_voz(trilha, voz, destino, nivel: float = NIVEL_PADRAO) -> tuple[float, float]:
    """Musica baixa e abaixando sozinha quando ha voz. Devolve (LUFS da musica, LUFS da voz)."""
    filtro = (f"[0]loudnorm=I={nivel}:TP=-9:LRA=11[m];[1]aformat=channel_layouts=stereo[sc];"
              "[m][sc]sidechaincompress=threshold=0.06:ratio=3:attack=25:release=400[d]")
    rodar_ffmpeg("-i", trilha, "-i", voz, "-filter_complex", filtro, "-map", "[d]", "-ar", 48000, destino)
    return medir_loudness(destino)[0], medir_loudness(voz)[0]


def main() -> None:
    args = sys.argv[1:]
    nivel = NIVEL_PADRAO
    if "--nivel" in args:
        i = args.index("--nivel")
        nivel = float(args[i + 1])
        del args[i:i + 2]
    if not 1 <= len(args) <= 2:
        sys.exit(__doc__)
    p = Projeto(args[0])
    dur = json.loads((p.build / "cuts.json").read_text(encoding="utf-8"))["duration"]
    trilha = p.build / "music_raw.wav"
    if len(args) == 2:
        encaixar(args[1], trilha, dur)
    elif not trilha.exists():
        compor(trilha, dur)

    musica, voz = abaixar_sob_a_voz(trilha, p.public / "narration.wav", p.public / "music_ducked.wav", nivel)
    print(f"musica: {musica:.1f} LUFS | voz: {voz:.1f} LUFS | diferenca: {voz - musica:.1f} dB")


if __name__ == "__main__":
    main()
