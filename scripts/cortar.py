"""Monta a narracao final a partir da tabela TAKES de <projeto>/cortes.py.

Uso: python scripts/cortar.py videos/<projeto>

Dentro de cada take, junta so os trechos com voz (Silero VAD), com um respiro curto entre eles.
Com REMOVER_PAUSAS = False em cortes.py (videos de jogo), cada take entra inteiro e o som do jogo fica.
Gera build/cuts.json, build/narration_raw.wav, public/narration.wav (limpeza e -14 LUFS) e
build/narration_raw.json (transcricao da narracao final, de onde saem legendas e ancoras).

Avisa quando um corte parece comer o comeco ou o fim de uma palavra.
"""
import json
import sys

import numpy as np

from fala import Whisper, blocos_de_voz, transcrever_narracao
from kit_comum import Projeto, carregar_audio, carregar_modulo, rodar_ffmpeg, volume_db

MERGE_GAP = 0.30     # pausas menores que isso ficam
MIN_ILHA = 0.12      # trechos menores que isso (estalos, respiros curtos) saem
PAD_IN, PAD_OUT = 0.05, 0.12
GAP_NO_TAKE = 0.06   # respiro entre trechos da mesma secao
GAP_ENTRE = 0.16     # respiro entre secoes
SR = 48000
CADEIA_VOZ = ("highpass=f=80,afftdn=nf=-30:nr=8,acompressor=threshold=-20dB:ratio=3:attack=5:release=90:makeup=2,"
              "loudnorm=I=-14:TP=-1.5:LRA=9")
CADEIA_JOGO = "loudnorm=I=-14:TP=-1.5:LRA=11"  # sem reduzir ruido nem comprimir: o som do jogo fica natural


def ilhas(vad, t0, t1):
    segs = [[max(a, t0), min(b, t1)] for a, b in vad if b > t0 and a < t1]
    juntos = []
    for s in segs:
        if juntos and s[0] - juntos[-1][1] < MERGE_GAP:
            juntos[-1][1] = s[1]
        else:
            juntos.append(s)
    juntos = [s for s in juntos if s[1] - s[0] >= MIN_ILHA]
    saida = []
    for a, b in juntos:
        a, b = max(t0, a - PAD_IN), min(t1, b + PAD_OUT)
        if saida and a < saida[-1][1]:
            saida[-1][1] = b
        else:
            saida.append([a, b])
    return saida


def verificar_cortes(pecas, db_por_voz):
    """Fala audivel logo depois do fim (ou logo antes do comeco) de um pedaco indica palavra cortada."""
    avisos = []
    for p in pecas:
        db = db_por_voz[p["voice"]]
        limite = np.percentile(db, 10) + 12
        fim, ini = int(p["to"] * 100), int(p["from"] * 100)
        if len(db[fim:fim + 4]) and db[fim:fim + 4].mean() > limite:
            avisos.append(f"{p['voice']} {p['to']:.2f}s: ainda tem fala logo depois do corte (fim de palavra comido?)")
        if len(db[max(0, ini - 4):ini]) and db[max(0, ini - 4):ini].mean() > limite and ini > 4:
            avisos.append(f"{p['voice']} {p['from']:.2f}s: ja tem fala logo antes do corte (comeco de palavra comido?)")
    return avisos


def verificar_frases_abandonadas(pecas, p):
    """Avisa se um pedaco escolhido inclui o fim de um bloco que termina em "..." (comeco de frase abandonado)."""
    avisos = []
    for q in pecas:
        arquivo = p.build / "transcricoes" / f"{q['voice']}.json"
        if not arquivo.exists():
            continue
        for b in json.loads(arquivo.read_text(encoding="utf-8"))["blocos"]:
            if q["from"] <= b["end"] - 0.1 and q["to"] >= b["end"] - 0.05 and b["text"].rstrip().endswith("..."):
                avisos.append(f"{q['voice']} {b['start']:.2f}s: frase abandonada entrou no corte: \"{b['text'][-40:]}\"")
    return avisos


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    p = Projeto(sys.argv[1])
    cortes = carregar_modulo(p.dir / "cortes.py", "cortes")
    takes = cortes.TAKES
    remover_pausas = getattr(cortes, "REMOVER_PAUSAS", True)

    arquivo = {v: p.public / f"{v}.wav" for v in {t[1] for t in takes}}
    audio = {v: carregar_audio(a) for v, a in arquivo.items()}
    vad = {v: blocos_de_voz(a) for v, a in audio.items()} if remover_pausas else {}
    db_por_voz = {v: volume_db(a, 160) for v, a in audio.items()}

    pecas, t = [], 0.0
    for i, (secao, voz, a, b, cam, deslocamento) in enumerate(takes):
        if i:
            t += GAP_NO_TAKE if takes[i - 1][0] == secao else GAP_ENTRE
        for k, (x0, x1) in enumerate(ilhas(vad[voz], a, b) if remover_pausas else [[a, b]]):
            if k:
                t += GAP_NO_TAKE
            peca = {"section": secao, "voice": voz, "from": round(x0, 3), "to": round(x1, 3), "at": round(t, 3)}
            if cam:
                peca["cam"] = cam
                peca["camFrom"] = round(x0 - deslocamento, 3)
            pecas.append(peca)
            t += x1 - x0
    total = round(t + 0.6, 3)

    entradas, filtros = [], []
    for i, q in enumerate(pecas):
        entradas += ["-i", arquivo[q["voice"]]]
        d = q["to"] - q["from"]
        filtros.append(
            f"[{i}:a]atrim={q['from']}:{q['to']},asetpts=PTS-STARTPTS,"
            f"afade=t=in:d=0.012,afade=t=out:st={max(0, d - 0.015):.3f}:d=0.015,"
            f"adelay={int(q['at'] * 1000)}:all=1[a{i}]"
        )
    mix = "".join(f"[a{i}]" for i in range(len(pecas)))
    filtros.append(f"{mix}amix=inputs={len(pecas)}:normalize=0,apad=whole_dur={total}[out]")
    script = p.build / "narration_filter.txt"
    script.write_text(";\n".join(filtros), encoding="utf-8")
    bruta = p.build / "narration_raw.wav"
    canais = 1 if remover_pausas else 2  # som de jogo continua estereo
    rodar_ffmpeg(*entradas, "-/filter_complex", script, "-map", "[out]", "-ar", SR, "-ac", canais, bruta)
    rodar_ffmpeg("-i", bruta, "-af", CADEIA_VOZ if remover_pausas else CADEIA_JOGO, "-ar", SR, "-ac", 2, p.public / "narration.wav")

    (p.build / "cuts.json").write_text(json.dumps({"duration": total, "pieces": pecas}, ensure_ascii=False, indent=1), encoding="utf-8")
    for secao in dict.fromkeys(q["section"] for q in pecas):
        ps = [q for q in pecas if q["section"] == secao]
        print(f"{secao:8s} {ps[0]['at']:6.2f}s -> {ps[-1]['at'] + ps[-1]['to'] - ps[-1]['from']:6.2f}s  ({len(ps)} pedacos)")
    print(f"total: {total:.2f}s")

    avisos = verificar_frases_abandonadas(pecas, p) + verificar_cortes(pecas, db_por_voz) if remover_pausas else []
    if avisos:
        print("ATENCAO, cortes suspeitos (confira com scripts/pausas.py):")
        for a in avisos:
            print(f"  - {a}")

    dados = transcrever_narracao(Whisper(), carregar_audio(bruta), p.nomes_whisper)
    (p.build / "narration_raw.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nnarracao final:")
    for s in dados["segments"]:
        print(f"  [{s['start']:6.2f}-{s['end']:6.2f}] {s['text']}")


if __name__ == "__main__":
    main()
