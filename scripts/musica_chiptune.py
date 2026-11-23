"""Compoe uma trilha chiptune original (8-bit), sem risco de direitos autorais.

Progressao Am - F - C - G a 112 BPM: baixo pulsado, arpejo, pad suave, bateria leve
e uma melodia simples na segunda metade de cada frase.
"""
import wave

import numpy as np

SR = 48000
BPM = 112
BEAT = 60 / BPM
BAR = 4 * BEAT

# acordes (notas MIDI): Am, F, C, G
CHORDS = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
# melodia (MIDI, duracao em tempos) para 4 compassos; None = pausa
MELODY = [
    [(72, 1), (71, 0.5), (69, 0.5), (67, 1), (69, 1)],
    [(69, 1.5), (72, 0.5), (74, 1), (72, 1)],
    [(76, 1), (74, 0.5), (72, 0.5), (71, 1), (72, 1)],
    [(71, 2), (None, 1), (67, 1)],
]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def pulse(f, n, duty=0.5):
    ph = (np.arange(n) * f / SR) % 1.0
    return np.where(ph < duty, 1.0, -1.0)


def tri(f, n):
    ph = (np.arange(n) * f / SR) % 1.0
    return 4 * np.abs(ph - 0.5) - 1


def env(n, a=0.005, d=0.08, s=0.6, r=0.05):
    t = np.arange(n) / SR
    e = np.ones(n) * s
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, max(1, na))[: len(e[:na])]
    e[na:na + nd] = np.linspace(1, s, max(1, nd))[: len(e[na:na + nd])]
    if nr and n > nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e * (t >= 0)


def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def add(buf, start, sig):
    i = int(start * SR)
    j = min(len(buf), i + len(sig))
    if j > i:
        buf[i:j] += sig[: j - i]


def kick():
    n = int(0.16 * SR)
    t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 35)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18)


def snare(rng):
    n = int(0.14 * SR)
    t = np.arange(n) / SR
    noise = rng.uniform(-1, 1, n)
    noise = noise - onepole_lp(noise, 1800)  # passa-alta
    return (0.7 * noise + 0.3 * np.sin(2 * np.pi * 185 * t)) * np.exp(-t * 26)


def hat(rng):
    n = int(0.035 * SR)
    t = np.arange(n) / SR
    noise = rng.uniform(-1, 1, n)
    noise = noise - onepole_lp(noise, 6000)
    return noise * np.exp(-t * 90)


def compor(saida, dur: float) -> None:
    rng = np.random.default_rng(7)
    n_bars = int(np.ceil(dur / BAR)) + 1
    total = n_bars * BAR
    bass, arp, pad, lead, drums = (np.zeros(int(total * SR) + SR) for _ in range(5))
    K, S, H = kick(), snare(rng), hat(rng)

    for b in range(n_bars):
        t0 = b * BAR
        ch = CHORDS[b % 4]
        # baixo: oitavas alternadas em colcheias
        for k in range(8):
            m = ch[0] - 12 + (12 if k % 2 else 0)
            n = int(BEAT / 2 * SR)
            add(bass, t0 + k * BEAT / 2, pulse(hz(m), n, 0.5) * env(n, d=0.06, s=0.55, r=0.02))
        # arpejo em semicolcheias
        notes = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 12]
        for k in range(16):
            n = int(BEAT / 4 * SR)
            add(arp, t0 + k * BEAT / 4, pulse(hz(notes[k % 4]), n, 0.25) * env(n, d=0.05, s=0.25, r=0.01))
        # pad (triangulo, entra e sai devagar)
        n = int(BAR * SR)
        for m in ch:
            add(pad, t0, tri(hz(m), n) * env(n, a=0.25, d=0.3, s=0.8, r=0.3))
        # melodia na segunda frase de cada 8 compassos
        if (b // 4) % 2 == 1:
            tt = t0
            for m, d in MELODY[b % 4]:
                n = int(d * BEAT * SR)
                if m is not None:
                    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * np.arange(n) / SR)
                    ph = np.cumsum(hz(m) * vib / SR) % 1.0
                    add(lead, tt, np.where(ph < 0.5, 1.0, -1.0) * env(n, a=0.01, d=0.1, s=0.5, r=0.06))
                tt += d * BEAT
        # bateria (sem bateria no primeiro compasso)
        if b:
            for k in range(4):
                add(drums, t0 + k * BEAT, K * 0.9 if k in (0, 2) else S * 0.45)
            if b % 4 == 3:
                add(drums, t0 + 3.5 * BEAT, K * 0.7)
            for k in range(8):
                add(drums, t0 + k * BEAT / 2, H * (0.25 if k % 2 else 0.18))

    mix = (0.20 * onepole_lp(bass, 1400) + 0.07 * onepole_lp(arp, 3500) + 0.06 * pad
           + 0.075 * onepole_lp(lead, 4000) + 0.35 * drums)
    mix = mix[: int(dur * SR)]
    fi, fo = int(0.4 * SR), int(2.5 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)
    mix[-fo:] *= np.linspace(1, 0, fo) ** 1.5
    mix /= np.max(np.abs(mix)) + 1e-9
    mix *= 0.8
    pcm = (np.stack([mix, mix], axis=1) * 32767).astype("<i2")
    with wave.open(str(saida), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
