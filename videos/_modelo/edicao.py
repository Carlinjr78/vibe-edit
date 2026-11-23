"""Edicao do video: cada frase ligada a uma imagem. Exemplo completo em videos/_exemplo/edicao.py."""
from edicao_lib import K


def montar(r):
    r.preparar_legendas(
        correcoes={},                    # {"palavra errada": "palavra certa"}
        destaque={"palavra", "chave"},   # palavras que ficam verdes quando faladas
    )
    corpo, final = r.cut_before("corpo"), r.cut_before("final")

    r.camera_da_secao("gancho", 0.0, corpo)
    r.camera_da_secao("final", final, r.DUR)

    # r.modal("twitch", inicio) coloca um modal do canal.
    # r.w("palavra") da o tempo em que a palavra e falada; use para ancorar cortes e efeitos.
    r.shots = [
        r.SHOT("A1", corpo, final, 0.0, [K(0, 1280, 720, 0.42), K(final - corpo, 1280, 720, 0.8)]),
    ]

    r.definir_transicoes(cortes=[corpo, final], trocas_de_assunto=[corpo, final])

    # Se o rosto estiver perto da camera no final, desca a legenda para nao cobri-lo:
    # r.layouts = [{"t0": final, "t1": r.DUR + 1, "y": 1455, "size": 80}]
