"""Quais trechos de cada audio entram no video.

Cada linha: (secao, voz, inicio, fim, camera, deslocamento voz-camera).
- secao: nome livre; o edicao.py usa para saber onde cada parte comeca.
- camera: nome do bruto de camera falando esse trecho, ou None se a imagem for de tela.
- deslocamento: resultado de scripts/sincronizar.py (0 se a voz vier do proprio video).

Em cortes de jogo, descomente a linha abaixo: cada take entra inteiro e o som do jogo fica.
"""

# REMOVER_PAUSAS = False

TAKES = [
    ("gancho", "voz1", 0.00, 5.00, "cam1", 0),
    ("corpo", "voz1", 5.00, 20.00, None, 0),
    ("final", "voz1", 20.00, 25.00, "cam1", 0),
]
