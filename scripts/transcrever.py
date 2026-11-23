"""Transcreve os brutos bloco a bloco e avisa sobre regravacoes.

Uso: python scripts/transcrever.py videos/<projeto> [nome_do_bruto ...]

Salva em build/transcricoes/<nome>.json e imprime cada bloco com seu tempo.
Use a lista para decidir os takes em cortes.py.
"""
import json
import sys

from fala import Whisper, achar_regravacoes, transcrever_blocos
from kit_comum import Projeto, carregar_audio


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    p = Projeto(sys.argv[1])
    nomes = sys.argv[2:] or list(p.brutos)
    saida = p.build / "transcricoes"
    saida.mkdir(exist_ok=True)
    whisper = Whisper()
    for nome in nomes:
        audio = carregar_audio(p.arquivo_bruto(nome))
        blocos = transcrever_blocos(whisper, audio, p.nomes_whisper)
        (saida / f"{nome}.json").write_text(json.dumps({"blocos": blocos}, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n### {nome} ({len(audio) / 16000:.1f}s, {whisper.device})")
        for b in blocos:
            print(f"  [{b['start']:6.2f}-{b['end']:6.2f}] {b['text']}")
        avisos = achar_regravacoes(blocos)
        if avisos:
            print("  ATENCAO, possiveis regravacoes:")
            for a in avisos:
                print(f"    - {a}")


if __name__ == "__main__":
    main()
