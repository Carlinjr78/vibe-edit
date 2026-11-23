"""Funcoes compartilhadas pelos scripts do kit."""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

KIT = Path(__file__).resolve().parent.parent
PRESETS = json.loads((KIT / "src" / "presets.json").read_text(encoding="utf-8"))
# Brutos e renders ficam fora do repositorio (e de pastas sincronizadas como OneDrive/Dropbox);
# o repositorio guarda so texto. Troque o lugar com a variavel de ambiente VIDEO_MIDIA.
_MIDIA_PADRAO = r"C:\video-midia" if os.name == "nt" else str(Path.home() / "video-midia")
MIDIA_BASE = Path(os.environ.get("VIDEO_MIDIA", _MIDIA_PADRAO))


def ler_env(arquivo: Path = KIT / ".env") -> dict:
    """KEY=VALOR do .env do kit (fora do git). Nunca imprime os valores."""
    if not arquivo.exists():
        return {}
    valores = {}
    for linha in arquivo.read_text(encoding="utf-8-sig").splitlines():
        linha = linha.strip()
        if linha and not linha.startswith("#") and "=" in linha:
            nome, valor = linha.split("=", 1)
            valores[nome.strip()] = valor.strip().strip('"').strip("'")
    return valores


def ferramenta(nome: str) -> str:
    """Caminho do ffmpeg/ffprobe: variavel de ambiente, PATH ou instalacao do winget."""
    achado = os.environ.get(nome.upper()) or shutil.which(nome)
    if achado:
        return achado
    base = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"
    for exe in sorted(base.glob(f"Gyan.FFmpeg*/ffmpeg-*/bin/{nome}.exe"), reverse=True):
        return str(exe)
    sys.exit(f"{nome} nao encontrado. Instale com: winget install --id Gyan.FFmpeg -e")


def metade_dos_nucleos() -> int:
    """Limite de threads de quem roda junto com a live: o resto da CPU fica para o OBS."""
    return max(1, (os.cpu_count() or 2) // 2)


def rodar_ffmpeg(*args) -> None:
    subprocess.run([ferramenta("ffmpeg"), "-v", "error", "-y", *map(str, args)], check=True)


def medir_loudness(arquivo) -> tuple[float, float]:
    """Retorna (LUFS integrado, pico em dBFS)."""
    saida = subprocess.run(
        [ferramenta("ffmpeg"), "-hide_banner", "-nostats", "-i", str(arquivo), "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stderr
    resumo = saida[saida.rfind("Summary:"):]
    lufs = float(resumo.split("I:")[1].split("LUFS")[0])
    pico = float(resumo.split("Peak:")[1].split("dBFS")[0])
    return lufs, pico


def sondar(arquivo) -> dict:
    """Duracao e tamanho do primeiro stream de video (ja considerando rotacao)."""
    saida = subprocess.run(
        [ferramenta("ffprobe"), "-v", "error", "-show_entries",
         "format=duration:stream=codec_type,width,height:stream_side_data=rotation", "-of", "json", str(arquivo)],
        capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout
    dados = json.loads(saida)
    info = {"duration": float(dados["format"]["duration"]), "width": None, "height": None}
    for st in dados["streams"]:
        if st.get("codec_type") == "video" and info["width"] is None:
            w, h = st["width"], st["height"]
            rot = next((s.get("rotation", 0) for s in st.get("side_data_list", [])), 0)
            info["width"], info["height"] = (h, w) if abs(rot) == 90 else (w, h)
    return info


def carregar_audio(caminho, sr: int = 16000) -> np.ndarray:
    """Decodifica com ffmpeg para mono float32 (evita o decodificador PyAV do faster-whisper)."""
    bruto = subprocess.run(
        [ferramenta("ffmpeg"), "-v", "error", "-i", str(caminho), "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
        check=True, capture_output=True,
    ).stdout
    return np.frombuffer(bruto, dtype=np.float32).copy()


def volume_db(x: np.ndarray, hop: int) -> np.ndarray:
    n = len(x) // hop
    return 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)


def carregar_modulo(caminho: Path, nome: str):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


class Projeto:
    """Texto em videos/<nome>/; midia em <VIDEO_MIDIA>/<nome>/ (brutos/, public/, build/, out/)."""

    def __init__(self, caminho):
        self.dir = Path(caminho).resolve()
        arquivo = self.dir / "projeto.json"
        if not arquivo.exists():
            sys.exit(f"projeto.json nao encontrado em {self.dir}")
        self.config = json.loads(arquivo.read_text(encoding="utf-8"))
        self.nome = self.dir.name
        self.midia = MIDIA_BASE / self.nome
        self.pasta_brutos = self.midia / "brutos"
        self.public = self.midia / "public"
        self.build = self.midia / "build"
        self.out = self.midia / "out"
        for pasta in (self.pasta_brutos, self.public, self.build, self.out):
            pasta.mkdir(parents=True, exist_ok=True)

    def arquivo_bruto(self, nome: str) -> Path:
        """Caminho de um bruto: nome simples fica em brutos/; caminho absoluto e usado como esta."""
        arquivo = Path(self.brutos[nome]["arquivo"])
        return arquivo if arquivo.is_absolute() else self.pasta_brutos / arquivo

    @property
    def formato(self) -> str:
        return self.config.get("formato", "reels-vertical")

    @property
    def preset(self) -> dict:
        return PRESETS[self.formato]

    @property
    def brutos(self) -> dict:
        return self.config["brutos"]

    @property
    def nomes_whisper(self) -> str:
        return self.config.get("nomes_para_o_whisper", "")
