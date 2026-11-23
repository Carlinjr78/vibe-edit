"""O exemplo de videos/_exemplo precisa continuar montando: roda o edicao.py dele com fala e midia falsas."""
import json
from types import SimpleNamespace

import edicao_lib
from edicao_lib import Roteiro
from kit_comum import KIT, carregar_modulo

EXEMPLO = KIT / "videos" / "_exemplo"

FALAS = {
    "gancho": "Três atalhos do VS Code que eu uso todo dia e quase ninguém conhece.",
    "atalho1": "O primeiro: Alt e clique cria vários cursores.",
    "atalho2": "O segundo: Ctrl P abre qualquer arquivo pelo nome.",
    "atalho2b": "Sem ficar caçando na árvore de pastas.",
    "atalho3": "E o terceiro: F2 renomeia a variável no projeto inteiro.",
    "atalho3b": "Esquece o buscar e substituir.",
    "final": "Qual você não conhecia? O segundo ou o terceiro?",
}


def _timeline(build):
    """cuts.json e narration_raw.json como o cortar.py gravaria, a partir dos TAKES do exemplo."""
    takes = carregar_modulo(EXEMPLO / "cortes.py", "cortes_exemplo").TAKES
    pecas, segmentos, at = [], [], 0.0
    for secao, _voz, ini, fim, cam, desloc in takes:
        dur = fim - ini
        peca = {"section": secao, "at": round(at, 3), "from": ini, "to": fim}
        if cam:
            peca.update({"cam": cam, "camFrom": round(ini + desloc, 3)})
        pecas.append(peca)
        palavras = FALAS[secao].split()
        passo = dur / len(palavras)
        words = [{"w": p, "s": round(at + i * passo + 0.02, 3), "e": round(at + (i + 0.8) * passo, 3)}
                 for i, p in enumerate(palavras)]
        segmentos.append({"start": words[0]["s"], "end": words[-1]["e"], "text": FALAS[secao], "words": words})
        at += dur + 0.1
    duracao = round(at - 0.1, 3)
    (build / "cuts.json").write_text(json.dumps({"duration": duracao, "pieces": pecas}), encoding="utf-8")
    (build / "narration_raw.json").write_text(json.dumps({"segments": segmentos}), encoding="utf-8")


def test_exemplo_monta_um_edl_valido(tmp_path, monkeypatch):
    _timeline(tmp_path)
    midia = {"width": 2560, "height": 1440, "duration": 120.0}
    monkeypatch.setattr(edicao_lib, "sondar", lambda _arquivo: midia)
    roteiro = Roteiro(SimpleNamespace(build=tmp_path, public=tmp_path, config={}))

    carregar_modulo(EXEMPLO / "edicao.py", "edicao_exemplo").montar(roteiro)
    roteiro._validar()

    assert [s["name"] for s in roteiro.shots] == ["A1", "B1", "B2", "C1", "C2"]
    assert len(roteiro.cams) == 2
    assert [m["tipo"] for m in roteiro.modais] == ["inscrever"]
    assert {o["type"] for o in roteiro.overlays} == {"terminal", "vote"}
    assert any(c["w"] == "Ctrl+P" and c["hl"] for c in roteiro.captions)
