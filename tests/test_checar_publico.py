"""A checagem do repositorio publico barra o que deve e deixa passar o que pode."""
import json

from checar_publico import problemas

CANAL_MODELO = json.dumps({"perfil_padrao": "principal", "perfis": {"principal": {"nome": "Seu Canal", "twitch": ""}}})


def _checar(arquivos: dict[str, str]) -> list[str]:
    return problemas(list(arquivos), lambda caminho: arquivos[caminho])


def test_repositorio_limpo_passa():
    assert _checar({"README.md": "Rode em C:\\video-midia", "assets/livre/sfx/pop.wav": "", "videos/_exemplo/edicao.py": "",
                    "src/canal.json": CANAL_MODELO, "docs.md": "C:\\Users\\seu-nome\\vibe-edit"}) == []


def test_barra_midia_videos_do_usuario_e_segredos():
    erros = _checar({"assets/canal/avatar.jpg": "", "videos/2026-12-meu/roteiro.md": "", ".env": "",
                     "assets/livre/sfx/musica.wav": ""})
    assert len(erros) == 4


def test_barra_caminho_pessoal_e_chave():
    erros = _checar({"a.py": 'BRUTO = "C:/Users/fulano/Videos/x.mp4"', "b.md": "token ghp_" + "a" * 36,
                     "c.json": '{"p": "/home/fulano/videos"}'})
    assert [e.split(":")[0] for e in erros] == ["a.py", "b.md", "c.json"]


def test_barra_canal_preenchido():
    canal = json.dumps({"perfil_padrao": "principal", "perfis": {"principal": {"nome": "Meu Canal", "twitch": "eu"}}})
    assert _checar({"src/canal.json": canal}) and _checar({"src/canal.json": CANAL_MODELO}) == []
