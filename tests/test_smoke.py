from pathlib import Path


def test_kit_comum_importa_e_acha_a_raiz_do_kit():
    import kit_comum

    assert kit_comum.KIT == Path(__file__).resolve().parent.parent
