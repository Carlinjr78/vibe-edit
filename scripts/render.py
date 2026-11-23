"""Renderiza um video do kit.

Uso:
  python scripts/render.py videos/<projeto> --previa 60,205,320   imagens de conferencia em build/previa/
  python scripts/render.py videos/<projeto>                       video completo em out/<projeto>_vN.mp4
  python scripts/render.py videos/<projeto> --so-audio            refaz so o audio sobre o ultimo render

--so-audio serve quando so a musica, a voz ou os efeitos mudaram: a imagem nao e renderizada de novo.
Em todo caso final passa um limitador, para musica e efeitos nao estourarem.
"""
import re
import shutil
import subprocess
import sys

from kit_comum import KIT, Projeto, medir_loudness, rodar_ffmpeg

CLI = KIT / "node_modules" / "@remotion" / "cli" / "remotion-cli.js"
ENTRADA = "src/index.ts"
COMPOSICAO = "Video"
POR_FOLHA = 8


def remotion(*args) -> None:
    subprocess.run(["node", str(CLI), *map(str, args)], cwd=KIT, check=True)


def proxima_saida(p: Projeto):
    versoes = [int(m.group(1)) for f in p.out.glob(f"{p.nome}_v*.mp4") if (m := re.search(r"_v(\d+)\.mp4$", f.name))]
    return p.out / f"{p.nome}_v{max(versoes, default=0) + 1}.mp4"


def finalizar(video_origem, audio_origem, destino) -> None:
    rodar_ffmpeg("-i", video_origem, "-i", audio_origem, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                 "-af", "alimiter=limit=0.891:attack=3:release=60:level=false", "-c:a", "aac", "-b:a", "320k",
                 "-movflags", "+faststart", destino)
    lufs, pico = medir_loudness(destino)
    print(f"ok: {destino} ({destino.stat().st_size / 1e6:.0f} MB, {lufs:.1f} LUFS, pico {pico:.1f} dBFS)")


def previa(p: Projeto, quadros: list[int]) -> None:
    pasta = p.build / "previa"
    if pasta.exists():
        shutil.rmtree(pasta)
    pasta.mkdir()
    pacote = p.build / "_bundle"
    remotion("bundle", ENTRADA, "--out-dir", pacote, f"--public-dir={p.public}", "--log=error")
    arquivos = []
    for q in quadros:
        img = pasta / f"q{q:05d}.jpg"
        remotion("still", pacote, COMPOSICAO, img, f"--frame={q}", "--image-format=jpeg", "--scale=0.4", "--log=error")
        arquivos.append(img)
    shutil.rmtree(pacote)
    for n in range(0, len(arquivos), POR_FOLHA):
        grupo = arquivos[n:n + POR_FOLHA]
        entradas = [x for a in grupo for x in ("-i", a)]
        rotulos = "".join(
            f"[{i}]drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='{quadros[n + i]}':x=6:y=6:"
            f"fontsize=22:fontcolor=yellow:box=1:boxcolor=black[v{i}];" for i in range(len(grupo)))
        junta = "".join(f"[v{i}]" for i in range(len(grupo)))
        pilha = f"{junta}hstack=inputs={len(grupo)}" if len(grupo) > 1 else "[v0]null"
        rodar_ffmpeg(*entradas, "-filter_complex", rotulos + pilha, pasta / f"folha_{n // POR_FOLHA + 1}.jpg")
    print(f"ok: {pasta}")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    p = Projeto(args[0])
    bruto = p.out / "_ultimo_render.mp4"
    publico = f"--public-dir={p.public}"
    if "--previa" in args:
        previa(p, [int(x) for x in args[args.index("--previa") + 1].split(",")])
    elif "--so-audio" in args:
        if not bruto.exists():
            sys.exit("Ainda nao ha render completo deste video.")
        audio = p.build / "_audio.wav"
        remotion("render", ENTRADA, COMPOSICAO, audio, publico, "--codec=wav", "--log=error")
        finalizar(bruto, audio, proxima_saida(p))
        audio.unlink()
    else:
        remotion("render", ENTRADA, COMPOSICAO, bruto, publico, "--codec=h264", "--crf=18", "--audio-bitrate=320k", "--log=error")
        finalizar(bruto, bruto, proxima_saida(p))


if __name__ == "__main__":
    main()
