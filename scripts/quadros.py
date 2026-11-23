"""Gera imagens dos brutos para o Claude "assistir" e achar coordenadas.

Uso:
  python scripts/quadros.py videos/<projeto> folhas tela        folhas 3x3 com um quadro por segundo
  python scripts/quadros.py videos/<projeto> grade tela 7.5 11  quadro inteiro com grade de referencia
  python scripts/quadros.py videos/<projeto> recorte tela 49.9 1460 1140 1100 300

Saida em build/quadros/. Na grade, cada celula tem 128x144 pixels da imagem original.
"""
import sys

from kit_comum import Projeto, rodar_ffmpeg, sondar

FONTE = "fontfile='C\\:/Windows/Fonts/arialbd.ttf'"


def main() -> None:
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    p = Projeto(sys.argv[1])
    modo, nome, resto = sys.argv[2], sys.argv[3], sys.argv[4:]
    origem = p.public / f"{nome}.mp4"
    saida = p.build / "quadros"
    saida.mkdir(exist_ok=True)
    info = sondar(origem)
    if modo == "folhas":
        vertical = info["height"] > info["width"]
        escala, colunas = ("360:640", "6x2") if vertical else ("640:360", "3x3")
        filtro = (f"fps=1,scale={escala},drawtext={FONTE}:text='%{{eif\\:t\\:d}}s':x=8:y=8:fontsize=28:fontcolor=yellow:"
                  f"box=1:boxcolor=black@0.7:boxborderw=6,tile={colunas}:padding=4:color=white")
        rodar_ffmpeg("-i", origem, "-vf", filtro, saida / f"{nome}_%02d.jpg")
    elif modo == "grade":
        w, h = info["width"] // 2, info["height"] // 2
        for t in resto:
            rodar_ffmpeg("-ss", t, "-i", origem, "-frames:v", 1, "-vf", f"scale={w}:{h},drawgrid=w=64:h=72:t=1:c=cyan@0.35",
                         saida / f"{nome}_t{t}.jpg")
    elif modo == "recorte":
        t, x, y, w, h = resto
        rodar_ffmpeg("-ss", t, "-i", origem, "-frames:v", 1, "-vf", f"crop={w}:{h}:{x}:{y}", saida / f"{nome}_recorte_{t}.jpg")
    else:
        sys.exit(__doc__)
    print(f"ok: {saida}")


if __name__ == "__main__":
    main()
