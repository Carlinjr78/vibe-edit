"""Testes do apoio da configuracao inicial (scripts/configurar.py)."""
import json

import pytest

import configurar


def _canal(tmp_path, perfis=None):
    arquivo = tmp_path / "canal.json"
    arquivo.write_text(json.dumps({"perfil_padrao": "principal", "perfis": perfis or {
        "principal": {"nome": "Seu Canal", "avatar": "avatar.jpg", "twitch": ""}}}), encoding="utf-8")
    return arquivo


def test_canal_do_repositorio_vem_sem_configurar():
    assert not configurar.canal_configurado()


def test_grava_nome_e_twitch_no_perfil_padrao(tmp_path):
    arquivo = _canal(tmp_path)
    configurar.gravar_canal("Meu Canal", "https://www.twitch.tv/MeuCanal/", arquivo)
    perfil = json.loads(arquivo.read_text(encoding="utf-8"))["perfis"]["principal"]
    assert perfil == {"nome": "Meu Canal", "avatar": "avatar.jpg", "twitch": "MeuCanal"}
    assert configurar.canal_configurado(arquivo)


def test_mantem_os_outros_perfis(tmp_path):
    arquivo = _canal(tmp_path, {"principal": {"nome": "Seu Canal"}, "games": {"nome": "Games", "twitch": "x"}})
    configurar.gravar_canal("Meu Canal", "@meucanal", arquivo)
    perfis = json.loads(arquivo.read_text(encoding="utf-8"))["perfis"]
    assert perfis["games"] == {"nome": "Games", "twitch": "x"}
    assert perfis["principal"]["twitch"] == "meucanal"


def test_nome_vazio_falha(tmp_path):
    with pytest.raises(ValueError):
        configurar.gravar_canal("  ", "", _canal(tmp_path))


def test_checar_responde_tudo_que_a_skill_usa():
    estado = configurar.checar()
    assert set(estado) >= {"ferramentas", "dependencias", "canal", "midia", "idioma_whisper", "caminhos_longos_windows"}
    assert estado["ferramentas"]["python"]
