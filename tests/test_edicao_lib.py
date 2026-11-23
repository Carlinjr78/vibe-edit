"""Testes do tratamento de legendas do Roteiro."""
import json
from types import SimpleNamespace

from edicao_lib import Roteiro


def _roteiro(tmp_path, palavras):
    duracao = palavras[-1][2] + 1
    (tmp_path / "cuts.json").write_text(json.dumps({"duration": duracao, "pieces": [{"at": 0, "from": 0, "to": duracao}]}), encoding="utf-8")
    words = [{"w": w, "s": s, "e": e} for w, s, e in palavras]
    segmento = {"start": words[0]["s"], "end": words[-1]["e"], "text": " ".join(p[0] for p in palavras), "words": words}
    (tmp_path / "narration_raw.json").write_text(json.dumps({"segments": [segmento]}), encoding="utf-8")
    roteiro = Roteiro(SimpleNamespace(build=tmp_path))
    roteiro.preparar_legendas()
    return roteiro.captions


def test_hifen_fica_dentro_da_palavra(tmp_path):
    legendas = _roteiro(tmp_path, [("Segunda-feira,", 0.0, 0.8), ("-oi-", 0.9, 1.2)])
    assert [(c["w"], c["p"]) for c in legendas] == [("Segunda-feira", ","), ("oi", "")]


def test_exclamacao_fecha_a_frase(tmp_path):
    legendas = _roteiro(tmp_path, [("Assustou!", 0.0, 0.6), ("Agora", 0.8, 1.1), ("sim.", 1.2, 1.5)])
    assert [c["p"] for c in legendas] == [".", "", "."]


def _canal(tmp_path, perfil, modais=("inscrever",)):
    (tmp_path / "canal.json").write_text(json.dumps({
        "perfil_padrao": "principal",
        "perfis": {"principal": {"nome": "Meu Canal", "avatar": "a_principal.jpg"},
                   "games": {"nome": "Meu Canal Games", "avatar": "a_games.jpg", "twitch": "meucanal"}}}), encoding="utf-8")
    assets = tmp_path / "assets"
    assets.mkdir()
    for nome in ("a_principal.jpg", "a_games.jpg"):
        (assets / nome).write_bytes(b"jpg")
    public = tmp_path / "public"
    public.mkdir()
    config = {"perfil": perfil} if perfil else {}
    roteiro = Roteiro.__new__(Roteiro)  # sem cuts.json: so o canal importa aqui
    roteiro.p = SimpleNamespace(public=public, config=config)
    roteiro.modais = [{"tipo": t} for t in modais]
    return roteiro._canal(tmp_path / "canal.json", assets), public


def test_perfil_escolhido_usa_nome_twitch_e_avatar_dele(tmp_path):
    canal, public = _canal(tmp_path, "games")
    assert canal == {"perfil": "games", "nome": "Meu Canal Games", "twitch": "meucanal", "avatar": "a_games.jpg"}
    assert (public / "a_games.jpg").is_file() and not (public / "a_principal.jpg").exists()


def test_sem_perfil_usa_o_padrao(tmp_path):
    canal, _ = _canal(tmp_path, None)
    assert canal["nome"] == "Meu Canal" and canal["avatar"] == "a_principal.jpg" and canal["twitch"] == ""


def test_modal_twitch_em_perfil_sem_twitch_falha(tmp_path):
    import pytest
    with pytest.raises(ValueError, match="nao tem Twitch"):
        _canal(tmp_path, "principal", modais=("inscrever", "twitch"))


def test_perfil_desconhecido_falha(tmp_path):
    import pytest
    with pytest.raises(ValueError, match="perfil desconhecido"):
        _canal(tmp_path, "tech")


def _roteiro_vazio():
    roteiro = Roteiro.__new__(Roteiro)
    roteiro.p = SimpleNamespace(config={})
    roteiro.DUR, roteiro.modais = 30.0, []
    return roteiro


def test_modal_clica_1_3_s_depois_de_entrar():
    roteiro = _roteiro_vazio()
    roteiro.modal("inscrever", 2.0, pos="top-left")
    m = roteiro.modais[0]
    assert (m["t0"], m["clique"], m["t1"], m["pos"]) == (2.0, 3.3, 6.5, "top-left")


def test_tipo_de_modal_desconhecido_falha():
    import pytest
    with pytest.raises(ValueError, match="tipo de modal desconhecido"):
        _roteiro_vazio().modal("seguir", 2.0)


def test_sons_do_modal_sao_pops_que_existem():
    from edicao_lib import KIT, sons_do_modal
    sons = sons_do_modal({"tipo": "inscrever", "t0": 0, "clique": 1.3})
    assert {s["src"] for s in sons} == {"pop.wav"}
    for s in sons:
        assert (KIT / "assets" / "livre" / "sfx" / s["src"]).is_file()
