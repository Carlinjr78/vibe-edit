"""Apoio da configuracao inicial (skill "configurar"). So usa a biblioteca padrao: roda antes da .venv existir.

Uso:
  python scripts/configurar.py checar
      Mostra o que ja esta pronto e o que falta, em JSON (ferramentas, dependencias, canal, pasta de midia).
  python scripts/configurar.py canal --nome "Meu Canal" [--twitch usuario] [--avatar foto.jpg]
      Grava o perfil padrao em src/canal.json e, com --avatar, salva assets/canal/avatar.jpg em 400x400.
"""
import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
CANAL = KIT / "src" / "canal.json"
ASSETS_CANAL = KIT / "assets" / "canal"
NOME_PADRAO = "Seu Canal"


def _versao(comando: list[str]) -> str | None:
    caminho = shutil.which(comando[0])  # no Windows, npm e um .cmd: precisa do caminho completo
    if not caminho:
        return None
    try:
        saida = subprocess.run([caminho, *comando[1:]], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    texto = (saida.stdout or saida.stderr).strip().splitlines()
    return texto[0] if texto else ""


def python_da_venv() -> Path:
    pasta = "Scripts" if os.name == "nt" else "bin"
    nome = "python.exe" if os.name == "nt" else "python"
    return KIT / ".venv" / pasta / nome


def pasta_de_midia() -> Path:
    padrao = r"C:\video-midia" if os.name == "nt" else str(Path.home() / "video-midia")
    return Path(os.environ.get("VIDEO_MIDIA", padrao))


def caminhos_longos_windows() -> bool | None:
    """True/False no Windows (o Remotion falha em caminho longo sem isso); None nos outros sistemas."""
    if os.name != "nt":
        return None
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\FileSystem") as chave:
            return winreg.QueryValueEx(chave, "LongPathsEnabled")[0] == 1
    except OSError:
        return False


def ler_canal(arquivo: Path = CANAL) -> dict:
    return json.loads(arquivo.read_text(encoding="utf-8"))


def canal_configurado(arquivo: Path = CANAL) -> bool:
    canal = ler_canal(arquivo)
    perfil = canal["perfis"][canal["perfil_padrao"]]
    return bool(perfil.get("nome")) and perfil["nome"] != NOME_PADRAO


def checar() -> dict:
    venv = python_da_venv()
    canal = ler_canal()
    perfil = canal["perfis"][canal["perfil_padrao"]]
    avatar = ASSETS_CANAL / perfil.get("avatar", "")
    return {
        "sistema": f"{platform.system()} {platform.release()}",
        "ferramentas": {
            "node": _versao(["node", "--version"]),
            "npm": _versao(["npm", "--version"]),
            "python": sys.version.split()[0],
            "ffmpeg": _versao(["ffmpeg", "-version"]),
            "git": _versao(["git", "--version"]),
            "gpu_nvidia": _versao(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"]),
        },
        "dependencias": {
            "node_modules": (KIT / "node_modules" / "remotion").is_dir(),
            "venv": venv.is_file(),
        },
        "canal": {
            "configurado": canal_configurado(),
            "nome": perfil.get("nome", ""),
            "twitch": perfil.get("twitch", ""),
            "avatar": avatar.is_file() if perfil.get("avatar") else False,
        },
        "midia": {"pasta": str(pasta_de_midia()), "existe": pasta_de_midia().is_dir(),
                  "variavel_VIDEO_MIDIA": "VIDEO_MIDIA" in os.environ},
        "idioma_whisper": os.environ.get("WHISPER_LANGUAGE", "pt"),
        "caminhos_longos_windows": caminhos_longos_windows(),
    }


def limpar_twitch(texto: str) -> str:
    """Aceita "usuario", "@usuario" ou o link do canal e devolve so o usuario."""
    texto = texto.strip().rstrip("/")
    texto = re.sub(r"^(https?://)?(www\.)?twitch\.tv/", "", texto, flags=re.IGNORECASE)
    return texto.lstrip("@")


def gravar_canal(nome: str, twitch: str = "", arquivo: Path = CANAL) -> dict:
    """Preenche o perfil padrao, mantendo os outros perfis que ja existirem."""
    nome = nome.strip()
    if not nome:
        raise ValueError("o nome do canal nao pode ser vazio")
    canal = ler_canal(arquivo)
    perfil = canal["perfis"].setdefault(canal["perfil_padrao"], {})
    perfil["nome"] = nome
    perfil["twitch"] = limpar_twitch(twitch)
    perfil.setdefault("avatar", "avatar.jpg")
    arquivo.write_text(json.dumps(canal, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return perfil


def gravar_avatar(origem: Path, destino: Path) -> None:
    """Recorta o centro em quadrado e reduz para 400x400 (o modal corta em circulo)."""
    if not origem.is_file():
        raise FileNotFoundError(f"imagem nao encontrada: {origem}")
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg nao encontrado: instale antes de configurar o avatar")
    destino.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(origem), "-vf",
                    "crop='min(iw,ih)':'min(iw,ih)',scale=400:400", "-frames:v", "1", "-q:v", "2", str(destino)],
                   check=True)


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Configuracao inicial do vibe-edit.")
    sub = parser.add_subparsers(dest="comando", required=True)
    sub.add_parser("checar", help="mostra o que esta pronto e o que falta")
    canal = sub.add_parser("canal", help="grava o nome, a Twitch e o avatar do canal")
    canal.add_argument("--nome", required=True)
    canal.add_argument("--twitch", default="")
    canal.add_argument("--avatar", type=Path)
    args = parser.parse_args(argv)

    if args.comando == "checar":
        print(json.dumps(checar(), ensure_ascii=False, indent=2))
        return 0
    perfil = gravar_canal(args.nome, args.twitch)
    if args.avatar:
        gravar_avatar(args.avatar, ASSETS_CANAL / perfil["avatar"])
    print(json.dumps({"canal": perfil, "avatar": str(ASSETS_CANAL / perfil["avatar"]) if args.avatar else None},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
