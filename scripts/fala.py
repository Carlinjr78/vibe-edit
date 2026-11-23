"""Deteccao de voz (Silero VAD) e transcricao (faster-whisper) usadas pelo kit."""
import os
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path


def _registrar_dlls_da_gpu() -> None:
    """Deixa o Whisper achar o cuBLAS e o cuDNN instalados pelo pip (pacotes nvidia-*-cu12) no Windows."""
    raiz = Path(sys.prefix) / "Lib" / "site-packages" / "nvidia"
    pastas = [str(p) for p in raiz.glob("*/bin") if p.is_dir()]
    for pasta in pastas:
        if hasattr(os, "add_dll_directory"):
            os.add_dll_directory(pasta)
    if pastas:
        os.environ["PATH"] = os.pathsep.join(pastas + [os.environ.get("PATH", "")])


_registrar_dlls_da_gpu()

from faster_whisper import WhisperModel  # noqa: E402  (depois das DLLs da GPU)
from faster_whisper.vad import VadOptions, get_speech_timestamps

MODELO = os.environ.get("WHISPER_MODEL", "large-v3-turbo")
IDIOMA = os.environ.get("WHISPER_LANGUAGE", "pt")  # idioma da fala (pt, en, es...)
SR = 16000


def blocos_de_voz(audio) -> list[list[float]]:
    """Trechos com voz separados por silencios de 180 ms ou mais (ignora som de fundo, ao contrario do volume)."""
    ts = get_speech_timestamps(audio, VadOptions(threshold=0.5, min_silence_duration_ms=180, speech_pad_ms=0,
                                                 min_speech_duration_ms=120))
    return [[t["start"] / SR, t["end"] / SR] for t in ts]


class Whisper:
    """Tenta a GPU; se faltar biblioteca CUDA (o erro so aparece ao transcrever), cai para a CPU.

    Com cpu_threads, vai direto para a CPU com esse limite: e o caminho de quem roda durante a live.
    """

    def __init__(self, cpu_threads: int = 0):
        self.cpu_threads = cpu_threads
        if cpu_threads:
            self._usar_cpu()
            return
        self.device = "cuda"
        try:
            self.model = WhisperModel(MODELO, device="cuda", compute_type="float16")
        except Exception:  # noqa: BLE001
            self._usar_cpu()

    def _usar_cpu(self):
        self.device = "cpu"
        self.model = WhisperModel(MODELO, device="cpu", compute_type="int8", cpu_threads=self.cpu_threads)

    def transcrever(self, audio, **opcoes):
        opcoes.setdefault("language", IDIOMA)
        opcoes.setdefault("beam_size", 5)
        opcoes.setdefault("word_timestamps", True)
        try:
            segs, info = self.model.transcribe(audio, **opcoes)
            return list(segs), info
        except Exception:  # noqa: BLE001
            if self.device != "cuda":
                raise
            self._usar_cpu()
            segs, info = self.model.transcribe(audio, **opcoes)
            return list(segs), info

    def detectar_idioma(self, audio) -> str:
        idioma, _, _ = self.model.detect_language(audio)
        return idioma


def _palavras(seg, deslocamento=0.0):
    return [{"w": w.word.strip(), "s": round(w.start + deslocamento, 3), "e": round(w.end + deslocamento, 3),
             "p": round(w.probability, 3)} for w in (seg.words or [])]


def transcrever_blocos(whisper: Whisper, audio, prompt: str) -> list[dict]:
    """Transcreve cada bloco de voz separado.

    Num arquivo inteiro o Whisper junta takes repetidos e estica palavras por cima das pausas.
    Bloco a bloco, as regravacoes aparecem como blocos separados com texto parecido.
    """
    saida = []
    for ini, fim in blocos_de_voz(audio):
        a, b = max(0, int((ini - 0.15) * SR)), int((fim + 0.15) * SR)
        segs, _ = whisper.transcrever(audio[a:b], vad_filter=False, condition_on_previous_text=False,
                                      initial_prompt=prompt or None)
        palavras = [p for s in segs for p in _palavras(s, a / SR)]
        saida.append({"start": round(ini, 3), "end": round(fim, 3), "text": " ".join(s.text.strip() for s in segs).strip(),
                      "words": palavras})
    return saida


def transcrever_narracao(whisper: Whisper, audio, prompt: str) -> dict:
    """Transcreve a narracao ja cortada, de onde saem as legendas e as ancoras do roteiro."""
    segs, info = whisper.transcrever(audio, vad_filter=True, vad_parameters={"min_silence_duration_ms": 300},
                                     initial_prompt=prompt or None)
    return {"duration": info.duration, "segments": [
        {"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip(), "words": _palavras(s)} for s in segs
    ]}


def _normaliza(texto: str) -> list[str]:
    return re.findall(r"[\wÀ-ÿ]+", texto.lower())


def achar_regravacoes(blocos: list[dict], janela: int = 4, minimo: int = 3) -> list[str]:
    """Avisos de frases repetidas (regravacao) e de frases que terminam cortadas."""
    avisos = []
    palavras = [_normaliza(b["text"]) for b in blocos]
    for i, a in enumerate(palavras):
        vistos = {}
        for k in range(len(a) - minimo + 1):
            trio = tuple(a[k:k + minimo])
            if trio in vistos and k - vistos[trio] >= minimo:
                avisos.append(f"[{blocos[i]['start']:.2f}s] repetido dentro do bloco: \"{' '.join(trio)}\"")
                break
            vistos.setdefault(trio, k)
        for j in range(i + 1, min(i + 1 + janela, len(palavras))):
            b = palavras[j]
            m = SequenceMatcher(None, a, b, autojunk=False).find_longest_match(0, len(a), 0, len(b))
            if m.size >= minimo:
                trecho = " ".join(a[m.a:m.a + m.size])
                avisos.append(f"[{blocos[i]['start']:.2f}s] e [{blocos[j]['start']:.2f}s] repetem: \"{trecho}\"")
        if blocos[i]["text"].rstrip().endswith("..."):
            avisos.append(f"[{blocos[i]['start']:.2f}s] termina cortado: \"{blocos[i]['text'][-40:]}\"")
    return avisos
