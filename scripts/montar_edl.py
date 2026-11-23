"""Roda o edicao.py do projeto, valida e grava edl.json (a edicao que o Remotion renderiza).

Uso: python scripts/montar_edl.py videos/<projeto>
"""
import sys

from edicao_lib import Roteiro
from kit_comum import Projeto, carregar_modulo


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    p = Projeto(sys.argv[1])
    r = Roteiro(p)
    carregar_modulo(p.dir / "edicao.py", "edicao").montar(r)
    r.salvar()


if __name__ == "__main__":
    main()
