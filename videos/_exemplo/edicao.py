"""Edicao do Reel dos atalhos do VS Code: cada frase ligada ao trecho certo da gravacao de tela.

Exemplo completo de como usar camera, cenas de tela com zoom, destaques, lupas, titulos, efeitos,
modal, votacao, transicoes e efeitos sonoros. Coordenadas e tempos sao ilustrativos.
Gravacao de tela: 2560x1440, z=0.42 mostra a tela inteira na largura, z=1.33 preenche a altura.
"""
from edicao_lib import B, G, HL, K, MAG, Y  # cores: Y amarelo, B azul, G verde, R vermelho

# regioes da gravacao de tela (x, y, largura, altura), medidas com scripts/quadros.py grade/recorte
LINHAS_EDITOR = (700, 420, 1300, 260)    # as tres linhas que ganham cursor
BUSCA = (900, 40, 760, 90)               # caixa do Ctrl P
VARIAVEL = (820, 610, 420, 60)           # nome da variavel sendo renomeada


def montar(r):
    r.preparar_legendas(
        correcoes={"vs": "VS", "code": "Code", "ctrl": "Ctrl", "f2": "F2"},
        juntar={("ctrl", "p"): "Ctrl+P"},
        destaque={"VS", "Code", "cursores", "Ctrl+P", "arquivo", "F2", "renomeia", "projeto"},
    )
    w, cut = r.w, r.cut_before

    # ------------------------------------------------------------ pontos de corte (ancorados na fala)
    t_1 = cut("atalho1")
    t_2 = cut("atalho2")
    t_2b = cut("atalho2b")
    t_3 = cut("atalho3")
    t_3b = cut("atalho3b")
    t_fim = cut("final")

    r.camera_da_secao("gancho", 0.0, t_1)
    r.camera_da_secao("final", t_fim, r.DUR)

    S = r.SHOT
    r.shots = [
        # "O primeiro: Alt e clique cria varios cursores."
        S("A1", t_1, t_2, 3.0, [K(0, 1280, 720, 0.42), K(1.0, 1350, 550, 1.4), K(t_2 - t_1, 1350, 550, 1.5)],
          hl=[HL(w("cursores") - 0.1, t_2, *LINHAS_EDITOR, Y)]),
        # "O segundo: Ctrl P abre qualquer arquivo pelo nome."
        S("B1", t_2, t_2b, 14.0, [K(0, 1280, 300, 1.2), K(t_2b - t_2, 1280, 320, 1.4)],
          mags=[MAG(w("Ctrl+P") - 0.1, t_2b, BUSCA, 540, 900, 1.3, "Ctrl + P", B)]),
        # "Sem ficar cacando na arvore de pastas."
        S("B2", t_2b, t_3, 19.0, [K(0, 300, 700, 1.5), K(t_3 - t_2b, 300, 760, 1.6)]),
        # "E o terceiro: F2 renomeia a variavel no projeto inteiro."
        S("C1", t_3, t_3b, 27.0, [K(0, 1030, 640, 1.8), K(1.2, 1280, 720, 0.8), K(t_3b - t_3, 1280, 720, 0.75)],
          hl=[HL(w("F2") - 0.1, w("projeto") - 0.1, *VARIAVEL, G)]),
        # "Esquece o buscar e substituir."
        S("C2", t_3b, t_fim, 33.0, [K(0, 1280, 720, 0.6), K(t_fim - t_3b, 1280, 720, 0.42, "out")]),
    ]

    # ------------------------------------------------------------ titulos, etiquetas e efeitos
    r.callouts = [
        {"t0": round(w("VS") - 0.1, 3), "t1": round(t_1, 3), "text": "VS CODE", "kind": "title", "y": 290,
         "parts": [{"t": "VS "}, {"t": "CODE", "color": "#3EA6FF"}]},
        {"t0": round(w("Alt") - 0.05, 3), "t1": round(t_2, 3), "text": "ALT + CLIQUE", "kind": "pill", "y": 330, "color": Y},
        {"t0": round(w("F2") - 0.05, 3), "t1": round(t_3b, 3), "text": "F2", "kind": "pill", "y": 330, "color": G},
    ]

    risca = w("substituir") - 0.05
    segundo, terceiro = w("segundo", t_fim), w("terceiro", t_fim)
    r.overlays = [
        {"type": "terminal", "t0": round(t_3b + 0.03, 3), "t1": t_fim, "strike": round(risca, 3),
         "title": "buscar e substituir", "lines": [{"txt": "buscar: totalAntigo", "color": "#e6e6e6"},
                                                    {"txt": "substituir: total", "color": "#e6e6e6"}]},
        {"type": "vote", "t0": round(segundo - 0.1, 3), "t1": r.DUR, "a": segundo, "b": terceiro,
         "labelA": "SEGUNDO", "labelB": "TERCEIRO", "cta": "comenta aí ↓"},
    ]

    # modal de inscricao logo depois de "pastas" ([MODAL-INSCREVER] no roteiro)
    r.modal("inscrever", w("pastas") + 0.4, dur=4.0, pos="top-center")

    r.definir_transicoes(
        cortes=[s["at"] for s in r.shots] + [t_fim],
        trocas_de_assunto=[t_1, t_2, t_3, t_fim],
    )
    r.sfx_extra = [
        {"src": "stamp.wav", "at": round(risca, 2), "volume": 0.6},
        {"src": "pop.wav", "at": segundo, "volume": 0.7},
        {"src": "pop.wav", "at": terceiro, "volume": 0.7},
    ]

    # no final o rosto fica perto da camera: a legenda desce e diminui para nao cobri-lo
    r.layouts = [{"t0": t_fim, "t1": r.DUR + 1, "y": 1455, "size": 80}]
