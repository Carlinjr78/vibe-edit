"""Testes do plano de modais do video longo."""
import pytest

from longo_modais import ler_modais, plano_padrao, validar

COM_TWITCH = {"perfil": "principal", "twitch": "seucanal"}
SEM_TWITCH = {"perfil": "principal", "twitch": ""}


def test_plano_de_meia_hora():
    assert plano_padrao(30 * 60, True) == [("inscrever", 90.0), ("curtir", 900.0), ("inscrever", 1200.0), ("twitch", 1620.0)]


def test_sem_twitch_no_perfil():
    assert all(tipo != "twitch" for tipo, _ in plano_padrao(30 * 60, False))


def test_video_longo_ganha_inscrever_a_cada_10_min_sem_encavalar():
    plano = plano_padrao(60 * 60, True)
    tempos = [t for _, t in plano]
    assert tempos == sorted(tempos)
    assert all(b - a >= 180 for a, b in zip(tempos, tempos[1:]))
    assert sum(1 for tipo, _ in plano if tipo == "inscrever") >= 4
    validar(plano, 60 * 60, COM_TWITCH)


def test_video_curto():
    assert plano_padrao(5 * 60, True) == [("inscrever", 75.0), ("curtir", 180.0)]


def test_horarios_a_mao():
    assert ler_modais("curtir@15:00, inscrever@1:30") == [("inscrever", 90.0), ("curtir", 900.0)]
    assert ler_modais("twitch@1:02:03") == [("twitch", 3723.0)]
    with pytest.raises(ValueError, match="modal invalido"):
        ler_modais("seguir@1:00")


def test_validar_barra_twitch_sem_perfil_e_modais_encavalados():
    with pytest.raises(ValueError, match="nao tem Twitch"):
        validar([("twitch", 60.0)], 600, SEM_TWITCH)
    with pytest.raises(ValueError, match="encavalados"):
        validar([("inscrever", 60.0), ("curtir", 62.0)], 600, COM_TWITCH)
    with pytest.raises(ValueError, match="passa do fim"):
        validar([("curtir", 598.0)], 600, COM_TWITCH)


def test_corte_das_pontas():
    from longo_modais import escolher_corte
    # comecou a falar em 0:40 e parou em 29:10 num video de 30 min
    assert escolher_corte([[40.0, 42.0], [50.0, 51.0]], [[1700.0, 1720.0], [1748.0, 1750.0]], 1800.0) == (39.0, 1751.5)


def test_corte_ignora_ruido_curto_e_pontas_pequenas():
    from longo_modais import escolher_corte
    # um estalo de 0,2 s em 0:05 nao conta; fala em 0:02 daria corte de 1 s, abaixo do minimo
    assert escolher_corte([[5.0, 5.2], [2.0, 4.0]], [], 1800.0) == (0.0, 1800.0)


def test_sem_fala_nas_pontas_nao_corta():
    from longo_modais import escolher_corte
    assert escolher_corte([], [], 1800.0) == (0.0, 1800.0)


def test_video_de_10_min_nao_cola_inscrever_no_twitch():
    assert plano_padrao(10 * 60, True) == [("inscrever", 90.0), ("curtir", 300.0), ("twitch", 420.0)]
