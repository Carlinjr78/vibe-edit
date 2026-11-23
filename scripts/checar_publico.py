"""Barra no repositorio publico o que nao pode ir para o Git: midia, segredos, videos do usuario e dados pessoais.

Uso: python scripts/checar_publico.py   (roda na checagem automatica de todo PR; sai com codigo 1 se achar algo)
Olha so os arquivos versionados (git ls-files).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
MIDIA = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4a", ".mp3", ".wav", ".flac", ".aac", ".ogg",
         ".png", ".jpg", ".jpeg", ".gif", ".webp", ".psd"}
MIDIA_PERMITIDA = re.compile(r"^assets/livre/sfx/(pop|whoosh|stamp)\.wav$")
VIDEOS_PERMITIDOS = re.compile(r"^videos/(_modelo|_exemplo)/")
SEGREDO = re.compile(r"(^|/)\.env(\..*)?$|\.(pem|key|p12|pfx)$|(^|/)\.claude/settings\.local\.json$")
CAMINHO_PESSOAL = re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+(?!seu-nome|<)[^\\/\s\"'`]+|/(?:Users|home)/(?!seu-nome|<)[a-z][^/\s\"'`]+/",
                             re.IGNORECASE)
CHAVE_API = re.compile(r"\b(sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|AIza[0-9A-Za-z_-]{30,})")
NAO_VARRER = {"scripts/checar_publico.py", "tests/test_checar_publico.py"}  # tem exemplos de proposito
TEXTO = {".py", ".ts", ".tsx", ".js", ".json", ".md", ".txt", ".yml", ".yaml", ".toml", ".cfg", ".ini"}


def problemas(arquivos: list[str], ler=lambda caminho: (KIT / caminho).read_text(encoding="utf-8", errors="ignore")) -> list[str]:
    erros = []
    for caminho in arquivos:
        ext = Path(caminho).suffix.lower()
        if ext in MIDIA and not MIDIA_PERMITIDA.match(caminho):
            erros.append(f"{caminho}: midia nao vai para o Git")
        if caminho.startswith("videos/") and not VIDEOS_PERMITIDOS.match(caminho):
            erros.append(f"{caminho}: projetos de video do usuario ficam fora do Git")
        if SEGREDO.search(caminho):
            erros.append(f"{caminho}: arquivo de segredo ou configuracao local")
        if ext in TEXTO and caminho not in NAO_VARRER:
            conteudo = ler(caminho)
            for padrao, motivo in ((CAMINHO_PESSOAL, "caminho do computador de alguem"), (CHAVE_API, "parece uma chave de API")):
                achado = padrao.search(conteudo)
                if achado:
                    linha = conteudo[:achado.start()].count("\n") + 1
                    erros.append(f"{caminho}:{linha}: {motivo}")
    if "src/canal.json" in arquivos:
        canal = json.loads(ler("src/canal.json"))
        perfis = canal.get("perfis", {})
        if list(perfis) != ["principal"] or perfis["principal"].get("nome") != "Seu Canal" or perfis["principal"].get("twitch"):
            erros.append("src/canal.json: no repositorio ele fica com o modelo (\"Seu Canal\", sem Twitch); "
                         "o seu canal fica so no seu computador")
    return erros


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    saida = subprocess.run(["git", "ls-files"], cwd=KIT, capture_output=True, text=True, encoding="utf-8", check=True)
    erros = problemas([a for a in saida.stdout.splitlines() if a])
    if erros:
        print("Arquivos que nao podem ir para o repositorio publico:")
        for erro in erros:
            print(f"  - {erro}")
        print("Veja as regras em CONTRIBUTING.md.")
        return 1
    print("ok: nada pessoal, nenhuma midia e nenhum segredo nos arquivos versionados")
    return 0


if __name__ == "__main__":
    sys.exit(main())
