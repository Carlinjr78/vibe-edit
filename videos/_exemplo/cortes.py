"""Quais trechos de cada audio entram no Reel dos atalhos do VS Code (tempos ilustrativos).

Cada linha: (secao, voz, inicio, fim, camera, deslocamento voz-camera).
Linhas seguidas com a mesma secao ficam coladas, com respiro minimo.
Os comentarios mostram o tipo de decisao que se anota aqui: regravacao, frase abandonada, fim de palavra.
"""

TAKES = [
    # voz1 0-4 s e um take que travou no meio ("Tres atalhos do VS... pera"); o completo e 4.6-9.3 s
    # deslocamento 1.12: resultado de scripts/sincronizar.py entre o microfone e o celular
    ("gancho", "voz1", 4.60, 9.30, "cam1", 1.12),
    ("atalho1", "voz1", 11.20, 15.05, None, 0),
    # "Ctrl P" no fim tem pouco volume no "P": fim medido com scripts/pausas.py
    ("atalho2", "voz1", 16.40, 20.10, None, 0),
    ("atalho2b", "voz1", 20.30, 22.45, None, 0),
    # 23.0-25.8 s = "E o terceiro: F2 renome..." (cortado); a regravacao completa e 26.1-30.4 s
    ("atalho3", "voz1", 26.10, 30.40, None, 0),
    ("atalho3b", "voz1", 30.55, 32.20, None, 0),
    ("final", "voz1", 34.00, 37.60, "cam1", 1.12),
]
