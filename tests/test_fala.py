"""Testes do Whisper e da transcricao. O Whisper real nunca roda aqui: o modelo e sempre falso."""
from types import SimpleNamespace

import numpy as np
import pytest

import fala


def _palavra(texto, inicio, fim, prob=0.9):
    return SimpleNamespace(word=texto, start=inicio, end=fim, probability=prob)


SEGMENTOS = [
    SimpleNamespace(start=0.5, end=1.5, text=" Olha isso ", words=[_palavra(" Olha", 0.5, 0.9), _palavra(" isso", 0.95, 1.5)]),
    SimpleNamespace(start=2.0, end=2.8, text=" caramba ", words=[_palavra(" caramba", 2.0, 2.8, 0.75)]),
]


class ModeloFalso:
    def __init__(self, nome, **opcoes):
        self.opcoes = opcoes
        ModeloFalso.criados.append(opcoes)

    def transcribe(self, audio, **opcoes):
        ModeloFalso.transcricoes.append(opcoes)
        return iter(SEGMENTOS), SimpleNamespace(duration=30.0)


@pytest.fixture(autouse=True)
def modelo_falso(monkeypatch):
    ModeloFalso.criados = []
    ModeloFalso.transcricoes = []
    monkeypatch.setattr(fala, "WhisperModel", ModeloFalso)
    # O VAD real fica de fora: so importa quais opcoes chegam ao modelo.
    monkeypatch.setattr(fala, "blocos_de_voz", lambda audio: [[0.0, 1.0]])


AUDIO = np.zeros(16000 * 2, dtype=np.float32)


def test_whisper_do_fluxo_atual_continua_tentando_a_gpu_sem_limite_de_threads():
    fala.Whisper()

    assert ModeloFalso.criados == [{"device": "cuda", "compute_type": "float16"}]


def test_whisper_do_fluxo_atual_cai_para_a_cpu_com_o_padrao_de_threads(monkeypatch):
    class GpuAusente(ModeloFalso):
        def __init__(self, nome, **opcoes):
            if opcoes["device"] == "cuda":
                raise RuntimeError("sem cuda")
            super().__init__(nome, **opcoes)

    monkeypatch.setattr(fala, "WhisperModel", GpuAusente)

    fala.Whisper()

    # cpu_threads=0 e o padrao do faster-whisper: o fluxo atual nao ganha limite.
    assert ModeloFalso.criados == [{"device": "cpu", "compute_type": "int8", "cpu_threads": 0}]


def test_transcrever_blocos_mantem_as_opcoes_do_fluxo_atual():
    fala.transcrever_blocos(fala.Whisper(), AUDIO, "nomes")

    assert ModeloFalso.transcricoes == [{
        "language": "pt",
        "beam_size": 5,
        "word_timestamps": True,
        "vad_filter": False,
        "condition_on_previous_text": False,
        "initial_prompt": "nomes",
    }]


def test_transcrever_narracao_mantem_as_opcoes_do_fluxo_atual():
    fala.transcrever_narracao(fala.Whisper(), AUDIO, "nomes")

    assert ModeloFalso.transcricoes == [{
        "language": "pt",
        "beam_size": 5,
        "word_timestamps": True,
        "vad_filter": True,
        "vad_parameters": {"min_silence_duration_ms": 300},
        "initial_prompt": "nomes",
    }]
