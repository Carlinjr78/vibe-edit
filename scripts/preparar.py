"""Gera em public/ as versoes dos brutos que o Remotion usa, e copia os efeitos sonoros.

Uso: python scripts/preparar.py videos/<projeto> [--refazer]

tipo "tela": H.264 sem audio no fps do formato (tamanho original, para os zooms ficarem nitidos)
tipo "cam":  H.264 no tamanho e fps do formato, ja respeitando a rotacao do celular
tipo "voz":  WAV 48 kHz (pode apontar para um video; so o audio e usado)
"""
import shutil
import sys

from kit_comum import KIT, Projeto, rodar_ffmpeg, sondar


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    refazer = "--refazer" in sys.argv
    if len(args) != 1:
        sys.exit(__doc__)
    p = Projeto(args[0])
    w, h, fps = p.preset["width"], p.preset["height"], p.preset["fps"]

    for nome, bruto in p.brutos.items():
        origem, tipo = p.arquivo_bruto(nome), bruto["tipo"]
        if not origem.exists():
            sys.exit(f"{nome}: arquivo nao encontrado: {origem}")
        destino = p.public / (nome + (".wav" if tipo == "voz" else ".mp4"))
        if destino.exists() and not refazer:
            print(f"ja existe: {destino.name}")
            continue
        if tipo == "tela":
            rodar_ffmpeg("-i", origem, "-vf", f"fps={fps}", "-c:v", "libx264", "-preset", "veryfast", "-crf", 16,
                         "-g", fps, "-pix_fmt", "yuv420p", "-an", destino)
        elif tipo == "cam":
            filtro = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={fps}"
            rodar_ffmpeg("-i", origem, "-vf", filtro, "-c:v", "libx264", "-preset", "veryfast", "-crf", 17,
                         "-g", fps, "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", destino)
        elif tipo == "voz":
            rodar_ffmpeg("-i", origem, "-vn", "-c:a", "pcm_s16le", "-ar", 48000, destino)
        else:
            sys.exit(f"{nome}: tipo desconhecido '{tipo}' (use tela, cam ou voz)")
        info = sondar(destino)
        tamanho = f", {info['width']}x{info['height']}" if info["width"] else ""
        print(f"ok: {destino.name} ({info['duration']:.1f}s{tamanho})")

    for pasta in ("livre/sfx", "canal"):
        for arquivo in (KIT / "assets" / pasta).glob("*.*"):
            if arquivo.name != "README.md":
                shutil.copy2(arquivo, p.public / arquivo.name)
    print("efeitos sonoros e imagens do canal copiados")


if __name__ == "__main__":
    main()
