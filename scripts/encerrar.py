"""Encerra um video ja postado: guarda o texto e apaga a midia pesada.

Antes de rodar, escreva a ficha.md e atualize os estilos com o que foi aprendido.

Uso:
  python scripts/encerrar.py videos/<nome> --link URL               so mostra o que sera feito
  python scripts/encerrar.py videos/<nome> --link URL --confirmar   executa; apagar a midia nao tem volta

Gera folha.jpg (quadros do video final), grava o link na ficha, move o projeto para
videos/_arquivo/<ano>/ e apaga a pasta de midia do video (brutos, arquivos de trabalho e renders).
Brutos guardados fora dessa pasta nao sao tocados; o script so avisa quais sao.
"""
import datetime
import re
import shutil
import sys
from pathlib import Path

from kit_comum import KIT, MIDIA_BASE, Projeto, rodar_ffmpeg, sondar


def tamanho_gb(pasta: Path) -> float:
    return sum(f.stat().st_size for f in pasta.rglob("*") if f.is_file()) / 1e9


def versao_final(p: Projeto):
    versoes = [(int(m.group(1)), f) for f in p.out.glob(f"{p.nome}_v*.mp4") if (m := re.search(r"_v(\d+)\.mp4$", f.name))]
    return max(versoes)[1] if versoes else None


def gerar_folha(video: Path, destino: Path) -> None:
    info = sondar(video)
    colunas, linhas, largura = (9, 2, 240) if info["height"] > info["width"] else (4, 4, 480)
    filtro = f"fps={colunas * linhas}/{info['duration']:.3f},scale={largura}:-2,tile={colunas}x{linhas}:padding=4:color=white"
    rodar_ffmpeg("-i", video, "-vf", filtro, "-frames:v", 1, "-q:v", 6, destino)


def main() -> None:
    args = sys.argv[1:]
    if "--link" not in args or len(args) < 3:
        sys.exit(__doc__)
    link = args[args.index("--link") + 1]
    confirmar = "--confirmar" in args
    p = Projeto(args[0])

    if p.dir.parent != KIT / "videos" or p.nome == "_modelo" or p.nome == "_arquivo":
        sys.exit("Esse caminho nao e um video em andamento.")
    if p.midia.parent != MIDIA_BASE or not p.nome:
        sys.exit("Pasta de midia inesperada; nada foi feito.")
    ficha = p.dir / "ficha.md"
    if not ficha.exists() or "(preencher)" in ficha.read_text(encoding="utf-8"):
        sys.exit("Preencha a ficha.md antes de encerrar: ela guarda o que este video ensinou.")
    final = versao_final(p)
    if final is None:
        sys.exit("Nenhum render final encontrado em out/.")

    ano = p.nome[:4] if p.nome[:4].isdigit() else str(datetime.date.today().year)
    arquivo = KIT / "videos" / "_arquivo" / ano / p.nome
    if arquivo.exists():
        sys.exit(f"Ja existe no arquivo: {arquivo}")
    fora = [p.arquivo_bruto(n) for n in p.brutos if p.pasta_brutos not in p.arquivo_bruto(n).parents]

    print(f"Folha de quadros a partir de: {final.name}")
    print(f"Link do post: {link}")
    print(f"Arquiva o projeto em: {arquivo}")
    print(f"APAGA: {p.midia} ({tamanho_gb(p.midia):.2f} GB)")
    if fora:
        print("Brutos fora da pasta de midia, que continuam no disco:")
        for f in fora:
            print(f"  {f}")
    if not confirmar:
        print("\nNada foi feito. Para executar, repita com --confirmar.")
        return

    gerar_folha(final, p.dir / "folha.jpg")
    ficha.write_text(ficha.read_text(encoding="utf-8").replace("(link)", link, 1), encoding="utf-8")
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(p.dir), str(arquivo))
    shutil.rmtree(p.midia)
    print(f"Encerrado. Projeto em {arquivo}; midia apagada.")


if __name__ == "__main__":
    main()
