"""Cria um video novo: a pasta de texto no repositorio e a pasta de midia (VIDEO_MIDIA).

Uso: python scripts/novo_video.py 2026-12-nome-do-video video-curto/games

O segundo argumento e o estilo: uma pasta dentro de estilos/ (video-curto, video-curto/games, video-longo).
"""
import json
import shutil
import sys

from kit_comum import KIT, MIDIA_BASE


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    nome, estilo = sys.argv[1], sys.argv[2].strip("/\\").replace("\\", "/")
    if not (KIT / "estilos" / estilo / "regras.md").exists():
        sys.exit(f"Estilo nao encontrado: estilos/{estilo}/regras.md")
    destino = KIT / "videos" / nome
    if destino.exists():
        sys.exit(f"Ja existe: {destino}")
    shutil.copytree(KIT / "videos" / "_modelo", destino)

    config_path = destino / "projeto.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["estilo"] = estilo
    config["formato"] = "youtube-horizontal" if estilo.startswith("video-longo") else "reels-vertical"
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    brutos = MIDIA_BASE / nome / "brutos"
    brutos.mkdir(parents=True, exist_ok=True)
    print(f"Projeto: {destino}")
    print(f"Coloque os brutos em: {brutos}")


if __name__ == "__main__":
    main()
