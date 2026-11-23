"""Coloca os modais do canal (inscrever, curtir, Twitch) num video longo ja gravado, sem legenda nem corte.

Cada tipo de modal e renderizado uma vez so pelo Remotion (fundo transparente) e o ffmpeg cola por cima
da gravacao nos horarios do plano, com os sons de cada modal, codificando na placa de video (NVENC).
A gravacao original nunca e alterada.

Corte das pontas: o detector de voz (Silero VAD) olha so os 2 primeiros e os 2 ultimos minutos. O video
comeca 1 s antes da primeira fala e termina 1,5 s depois da ultima. Sem fala ali, ou se o corte for de menos
de 3 s, nada e cortado. --sem-corte desliga; --inicio e --fim (m:ss) forcam.

Plano padrao (horarios fixos, sem analisar o video):
  inscrever em 1:30 · curtir no meio · inscrever em 2/3 (a partir de 20 min) · Twitch 3 min antes do fim
  (so se o perfil tiver Twitch em src/canal.json)
  acima de 35 min, mais um inscrever a cada 10 min. Abaixo de 8 min, um inscrever e um curtir.

Uso:
  longo_modais.py <gravacao.mp4> [--modais "inscrever@1:30,curtir@15:00"] [--perfil nome]
                  [--sem-corte | --inicio m:ss --fim m:ss] [--so-plano]
Os horarios dos modais contam a partir do inicio ja cortado.

Pastas (dentro da pasta de midia, VIDEO_MIDIA): as gravacoes ficam em longo/gravacoes/ e o resultado sai em
longo/prontos/<mesmo nome>.mp4 (nunca sobrescreve: _v2, _v3...).
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from edicao_lib import CLIQUE_MODAL, TIPOS_MODAL, sons_do_modal
from kit_comum import KIT, MIDIA_BASE, ferramenta, rodar_ffmpeg, sondar

PASTA = MIDIA_BASE / "longo"
GRAVACOES, PRONTOS, TRABALHO = PASTA / "gravacoes", PASTA / "prontos", PASTA / "trabalho"
CLI = KIT / "node_modules" / "@remotion" / "cli" / "remotion-cli.js"
DUR_MODAL = 4.5
SFX = KIT / "assets" / "livre" / "sfx"


# ------------------------------------------------------------ plano
def plano_padrao(duracao: float, com_twitch: bool) -> list[tuple[str, float]]:
    if duracao < 8 * 60:
        plano = [("inscrever", min(90.0, duracao * 0.25)), ("curtir", duracao * 0.6)]
    else:
        plano = [("inscrever", 90.0), ("curtir", duracao / 2)]
        if duracao >= 20 * 60:  # abaixo disso o 2/3 cai colado no modal da Twitch
            plano.append(("inscrever", duracao * 2 / 3))
        if com_twitch:
            plano.append(("twitch", duracao - 180))
        if duracao > 35 * 60:
            t = 600.0
            while t < duracao - 300:
                if all(abs(t - x) >= 180 for _, x in plano):
                    plano.append(("inscrever", t))
                t += 600
    return sorted(((tipo, round(t, 2)) for tipo, t in plano), key=lambda x: x[1])


def ler_tempo(texto: str) -> float:
    partes = [float(p) for p in texto.strip().split(":")]
    segundos = 0.0
    for p in partes:
        segundos = segundos * 60 + p
    return segundos


def ler_modais(texto: str) -> list[tuple[str, float]]:
    """ "inscrever@1:30,curtir@15:00" -> [("inscrever", 90.0), ("curtir", 900.0)]"""
    plano = []
    for item in filter(None, (x.strip() for x in texto.split(","))):
        m = re.fullmatch(r"(\w+)@([\d:.]+)", item)
        if not m or m.group(1) not in TIPOS_MODAL:
            raise ValueError(f"modal invalido: {item!r} (use tipo@m:ss, tipo = {', '.join(sorted(TIPOS_MODAL))})")
        plano.append((m.group(1), ler_tempo(m.group(2))))
    return sorted(plano, key=lambda x: x[1])


def validar(plano: list[tuple[str, float]], duracao: float, canal: dict) -> None:
    for tipo, t in plano:
        if t < 0 or t + DUR_MODAL > duracao:
            raise ValueError(f"{tipo} em {fmt(t)} passa do fim do video ({fmt(duracao)})")
        if tipo == "twitch" and not canal.get("twitch"):
            raise ValueError(f"o perfil {canal['perfil']} nao tem Twitch")
    for (a, ta), (b, tb) in zip(plano, plano[1:]):
        if tb - ta < DUR_MODAL + 1:
            raise ValueError(f"{a} em {fmt(ta)} e {b} em {fmt(tb)} ficam encavalados")


def fmt(t: float) -> str:
    t = int(round(t))
    return f"{t // 3600}:{t % 3600 // 60:02d}:{t % 60:02d}" if t >= 3600 else f"{t // 60}:{t % 60:02d}"


# ------------------------------------------------------------ corte das pontas
PONTA = 120.0
FOLGA_ANTES, FOLGA_DEPOIS, CORTE_MINIMO, FALA_MINIMA = 1.0, 1.5, 3.0, 0.5


def escolher_corte(blocos_inicio, blocos_fim, duracao: float) -> tuple[float, float]:
    """blocos com voz (em segundos do video) nos 2 primeiros e nos 2 ultimos minutos -> (inicio, fim)."""
    falas_ini = [a for a, b in blocos_inicio if b - a >= FALA_MINIMA]
    falas_fim = [b for a, b in blocos_fim if b - a >= FALA_MINIMA]
    inicio = max(0.0, falas_ini[0] - FOLGA_ANTES) if falas_ini else 0.0
    fim = min(duracao, falas_fim[-1] + FOLGA_DEPOIS) if falas_fim else duracao
    if inicio < CORTE_MINIMO:
        inicio = 0.0
    if duracao - fim < CORTE_MINIMO:
        fim = duracao
    if fim - inicio < duracao / 2:  # algo estranho: melhor nao cortar
        return 0.0, duracao
    return round(inicio, 2), round(fim, 2)


def _voz(gravacao: Path, inicio: float, dur: float) -> list[list[float]]:
    import numpy as np
    from fala import SR, blocos_de_voz  # so aqui: carrega o faster-whisper
    bruto = subprocess.run([ferramenta("ffmpeg"), "-v", "error", "-ss", str(inicio), "-t", str(dur), "-i", str(gravacao),
                            "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], check=True, capture_output=True).stdout
    return [[a + inicio, b + inicio] for a, b in blocos_de_voz(np.frombuffer(bruto, dtype=np.float32))]


def corte_automatico(gravacao: Path, duracao: float) -> tuple[float, float]:
    if duracao < 3 * PONTA:
        return 0.0, duracao
    return escolher_corte(_voz(gravacao, 0, PONTA), _voz(gravacao, duracao - PONTA, PONTA), duracao)


# ------------------------------------------------------------ canal
def perfil_do_canal(nome: str | None, arquivo: Path = KIT / "src" / "canal.json") -> dict:
    canal = json.loads(arquivo.read_text(encoding="utf-8"))
    nome = nome or canal["perfil_padrao"]
    if nome not in canal["perfis"]:
        raise ValueError(f"perfil desconhecido: {nome} (use {', '.join(canal['perfis'])})")
    p = canal["perfis"][nome]
    return {"perfil": nome, "nome": p.get("nome", ""), "twitch": p.get("twitch", ""), "avatar": p.get("avatar")}


# ------------------------------------------------------------ video
def taxa_de_quadros(arquivo: Path) -> float:
    saida = subprocess.run([ferramenta("ffprobe"), "-v", "error", "-select_streams", "v:0", "-show_entries",
                            "stream=r_frame_rate", "-of", "csv=p=0", str(arquivo)],
                           capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()
    num, den = saida.split(",")[0].split("/")
    return int(num) / int(den)


def tem_audio(arquivo: Path) -> bool:
    saida = subprocess.run([ferramenta("ffprobe"), "-v", "error", "-select_streams", "a", "-show_entries",
                            "stream=index", "-of", "csv=p=0", str(arquivo)],
                           capture_output=True, text=True, encoding="utf-8", check=True).stdout
    return bool(saida.strip())


def proxima_saida(gravacao: Path) -> Path:
    destino = PRONTOS / f"{gravacao.stem}.mp4"
    n = 2
    while destino.exists():
        destino = PRONTOS / f"{gravacao.stem}_v{n}.mp4"
        n += 1
    return destino


# sem fonte explicita, o drawtext do ffmpeg trava no Windows
FONTE = r"C\:/Windows/Fonts/arial.ttf" if sys.platform == "win32" else ""


def folha_do_plano(gravacao: Path, plano, destino: Path, pasta: Path, inicio: float = 0.0) -> None:
    """Um quadro de cada momento (1 s depois de o modal entrar), em grade de 2 colunas, para conferir antes."""
    fonte = f"fontfile='{FONTE}':" if FONTE else ""
    for i, (tipo, t) in enumerate(plano):
        rotulo = f"{tipo} {fmt(t)}".replace(":", r"\:")
        rodar_ffmpeg("-ss", inicio + t + 1, "-i", gravacao, "-frames:v", 1, "-vf",
                     f"scale=480:-2,drawtext={fonte}text='{rotulo}':x=10:y=10:fontsize=28:"
                     "fontcolor=white:box=1:boxcolor=black@0.6", pasta / f"q{i}.jpg")
    linhas = (len(plano) + 1) // 2
    rodar_ffmpeg("-framerate", 1, "-i", pasta / "q%d.jpg", "-vf", f"tile=2x{linhas}:padding=4", "-frames:v", 1, destino)


def renderizar_modais(tipos: set[str], canal: dict, largura: int, altura: int, fps: float,
                      pasta: Path) -> dict[str, Path]:
    """Cada tipo uma vez, em ProRes 4444 com transparencia."""
    publico = pasta / "public"
    publico.mkdir(parents=True, exist_ok=True)
    if canal.get("avatar"):
        shutil.copy2(KIT / "assets" / "canal" / canal["avatar"], publico / canal["avatar"])
    pacote = pasta / "pacote"
    subprocess.run(["node", str(CLI), "bundle", "src/index.ts", "--out-dir", str(pacote), f"--public-dir={publico}",
                    "--log=error"], cwd=KIT, check=True)
    saidas = {}
    for tipo in sorted(tipos):
        props = {"tipo": tipo, "dur": DUR_MODAL, "clique": CLIQUE_MODAL, "largura": largura, "altura": altura,
                 "fps": fps, "canal": canal}
        arquivo_props = pasta / f"props_{tipo}.json"
        arquivo_props.write_text(json.dumps(props, ensure_ascii=False), encoding="utf-8")
        saidas[tipo] = pasta / f"modal_{tipo}.mov"
        subprocess.run(["node", str(CLI), "render", str(pacote), "Modal", str(saidas[tipo]), f"--props={arquivo_props}",
                        "--codec=prores", "--prores-profile=4444", "--pixel-format=yuva444p10le", "--image-format=png",
                        "--log=error"],
                       cwd=KIT, check=True)
    return saidas


def filtros(plano, n_sfx_por_modal: list[list[dict]], largura: int, altura: int, com_audio: bool) -> tuple[str, int]:
    """Monta o filter_complex: entrada 0 = gravacao, 1..N = modais, depois os sons. Devolve (filtro, n de sons)."""
    partes, atual = [], "0:v"
    n = len(plano)
    for i in range(n):
        partes.append(f"[{i + 1}:v]scale={largura}:{altura}[m{i}]")
        partes.append(f"[{atual}][m{i}]overlay=eof_action=pass:format=auto[v{i}]")
        atual = f"v{i}"
    partes.append(f"[{atual}]format=yuv420p[v]")
    sons = [s for lista in n_sfx_por_modal for s in lista]
    if com_audio:
        rotulos = ["[0:a:0]"]
        for j, s in enumerate(sons):
            atraso = int(round(s["at"] * 1000))
            partes.append(f"[{n + 1 + j}:a]atrim=0:{s.get('dur', 0.6)},volume={s['volume']},"
                          f"adelay={atraso}|{atraso},aformat=sample_rates=48000:channel_layouts=stereo[s{j}]")
            rotulos.append(f"[s{j}]")
        partes.append("".join(rotulos) + f"amix=inputs={len(rotulos)}:normalize=0:duration=first[a]")
    return ";".join(partes), len(sons)


def montar(gravacao: Path, plano, modais: dict[str, Path], largura: int, altura: int,
           fps: float, saida: Path, inicio: float = 0.0, fim: float | None = None) -> None:
    itens = [{"tipo": tipo, "t0": t, "clique": round(t + CLIQUE_MODAL, 3)} for tipo, t in plano]
    sons = [sons_do_modal(m) for m in itens]
    com_audio = tem_audio(gravacao)
    filtro, _ = filtros(plano, sons, largura, altura, com_audio)
    entradas = ["-ss", inicio, *(["-to", fim] if fim else []), "-i", gravacao]
    for tipo, t in plano:
        entradas += ["-itsoffset", t, "-i", modais[tipo]]
    if com_audio:
        for s in (s for lista in sons for s in lista):
            entradas += ["-i", SFX / s["src"]]
    mapas = ["-map", "[v]"] + (["-map", "[a]"] if com_audio else [])
    comum = [*entradas, "-filter_complex", filtro, *mapas, "-g", round(fps * 2), "-c:a", "aac", "-b:a", "320k",
             "-ar", 48000, "-movflags", "+faststart"]
    try:
        rodar_ffmpeg(*comum, "-c:v", "h264_nvenc", "-preset", "p5", "-cq", 19, "-b:v", 0, saida)
    except subprocess.CalledProcessError:
        print("[longo] NVENC indisponivel; usando libx264 (mais lento).", file=sys.stderr)
        rodar_ffmpeg(*comum, "-c:v", "libx264", "-preset", "veryfast", "-crf", 19, saida)
    gerado = sondar(saida)["duration"] if saida.exists() and saida.stat().st_size > 1024 else 0
    esperado = (fim if fim else sondar(gravacao)["duration"]) - inicio
    if abs(gerado - esperado) > 2:
        raise RuntimeError(f"o video pronto tem {gerado:.1f} s, mas devia ter {esperado:.1f} s: confira {saida}")


# ------------------------------------------------------------ main
def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Coloca os modais do canal num video longo.")
    parser.add_argument("gravacao", help="o video gravado (caminho, ou so o nome se estiver em longo/gravacoes)")
    parser.add_argument("--modais", help='horarios a mao, ex.: "inscrever@1:30,curtir@15:00,twitch@27:00"')
    parser.add_argument("--perfil", help="perfil de src/canal.json (padrao: perfil_padrao)")
    parser.add_argument("--sem-corte", action="store_true", help="nao corta o comeco nem o fim")
    parser.add_argument("--inicio", help="corta o comeco ate aqui (m:ss), sem detectar")
    parser.add_argument("--fim", help="corta o fim a partir daqui (m:ss), sem detectar")
    parser.add_argument("--so-plano", action="store_true", help="so mostra o plano e a folha, sem renderizar")
    args = parser.parse_args(argv)

    for pasta in (GRAVACOES, PRONTOS, TRABALHO):
        pasta.mkdir(parents=True, exist_ok=True)
    gravacao = Path(args.gravacao)
    if not gravacao.is_absolute() and not gravacao.exists():
        gravacao = GRAVACOES / gravacao
    if not gravacao.is_file():
        sys.exit(f"gravacao nao encontrada: {gravacao}")

    info = sondar(gravacao)
    total, fps = info["duration"], taxa_de_quadros(gravacao)
    print(f"[longo] {gravacao.name}: {fmt(total)}, {info['width']}x{info['height']} a {fps:g} fps")
    if args.sem_corte:
        inicio, fim = 0.0, total
    else:
        inicio, fim = corte_automatico(gravacao, total) if not (args.inicio or args.fim) else (0.0, total)
        inicio = ler_tempo(args.inicio) if args.inicio else inicio
        fim = ler_tempo(args.fim) if args.fim else fim
    print(f"[longo] corte: começa em {fmt(inicio)} e termina em {fmt(fim)} "
          f"(tira {inicio:.1f} s do começo e {total - fim:.1f} s do fim)")
    duracao = fim - inicio
    canal = perfil_do_canal(args.perfil)
    plano = ler_modais(args.modais) if args.modais else plano_padrao(duracao, bool(canal.get("twitch")))
    validar(plano, duracao, canal)

    print(f"[longo] perfil {canal['perfil']} ({canal['nome']}), {len(plano)} modais:")
    for tipo, t in plano:
        print(f"  {fmt(t):>7}  {tipo}")
    trabalho = TRABALHO / gravacao.stem
    if trabalho.exists():
        shutil.rmtree(trabalho)
    trabalho.mkdir(parents=True)
    folha = trabalho / "plano.jpg"
    folha_do_plano(gravacao, plano, folha, trabalho, inicio)
    print(f"[longo] folha do plano: {folha}")
    if args.so_plano:
        print('[longo] para trocar algum horario: --modais "inscrever@1:30,curtir@15:00,..."')
        return 0

    vertical = info["height"] > info["width"]
    largura, altura = (1080, 1920) if vertical else (1920, 1080)
    relogio = time.time()
    modais = renderizar_modais({tipo for tipo, _ in plano}, canal, largura, altura, fps, trabalho)
    print(f"[longo] modais renderizados em {time.time() - relogio:.0f} s; colando no video...")
    saida = proxima_saida(gravacao)
    montar(gravacao, plano, modais, info["width"], info["height"], fps, saida, inicio,
           fim if fim < total else None)
    print(f"[longo] pronto em {time.time() - relogio:.0f} s: {saida}")
    shutil.rmtree(trabalho / "pacote", ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
