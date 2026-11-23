import React from "react";
import { AbsoluteFill, Easing, interpolate, random, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { monoFont } from "../fonts";
import { TermLine } from "../types";
import { Stage } from "./Stage";

const clampOpts = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const LINHAS_PADRAO: TermLine[] = [
  { txt: "$ claude", color: "#e6edf3" },
  { txt: "● Lendo src/components/Hero.astro", color: "#7ee787" },
  { txt: "● Editando src/cart/checkout.ts", color: "#7ee787" },
  { txt: "  ⎿ 3 arquivos alterados", color: "#8b949e" },
  { txt: "$ codex", color: "#e6edf3" },
  { txt: "● Rodando testes...", color: "#d2a8ff" },
  { txt: "  ⎿ 12 passed, 1 failed", color: "#ff7b72" },
  { txt: "? Aprovar permissão (y/n)", color: "#ffa657" },
];

type Props = { dur: number; strikeAt: number; title?: string; lines?: TermLine[] };

/** Janela de terminal que aparece digitando e leva um X vermelho no momento `strikeAt`. */
export const TerminalOverlay: React.FC<Props> = ({ dur, strikeAt, title = "terminal — 4 abas", lines = LINHAS_PADRAO }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const s = spring({ frame, fps, config: { damping: 14, stiffness: 160 } });
  const strike = spring({ frame: frame - strikeAt * fps, fps, config: { damping: 9, stiffness: 240 } });
  const shake = t > strikeAt && t < strikeAt + 0.25 ? (random(`sh${frame}`) - 0.5) * 22 : 0;
  const exitP = interpolate(t, [dur - 0.3, dur], [0, 1], { ...clampOpts, easing: Easing.in(Easing.cubic) });
  const shown = Math.floor(interpolate(t, [0.1, strikeAt - 0.05], [1, lines.length], clampOpts));
  return (
    <AbsoluteFill style={{ pointerEvents: "none", background: `rgba(5,8,12,${0.45 * s * (1 - exitP)})` }}>
      <Stage>
        <div
          style={{
            position: "absolute",
            left: 90,
            top: 520,
            width: 900,
            height: 600,
            background: "#0d1117",
            border: "3px solid #30363d",
            borderRadius: 22,
            boxShadow: "0 40px 120px rgba(0,0,0,0.8)",
            overflow: "hidden",
            transform: `translate(${shake}px, ${interpolate(s, [0, 1], [500, 0]) + exitP * 900}px) rotate(${interpolate(s, [0, 1], [8, -2]) + exitP * 18}deg) scale(${1 - exitP * 0.4})`,
            filter: t > strikeAt ? `grayscale(${Math.min(1, strike)})` : undefined,
          }}
        >
          <div style={{ height: 58, background: "#161b22", display: "flex", alignItems: "center", gap: 14, paddingLeft: 24 }}>
            {["#ff5f57", "#febc2e", "#28c840"].map((c) => (
              <div key={c} style={{ width: 22, height: 22, borderRadius: 11, background: c }} />
            ))}
            <div style={{ marginLeft: 20, color: "#8b949e", fontFamily: monoFont, fontSize: 26 }}>{title}</div>
          </div>
          <div style={{ padding: "22px 30px", fontFamily: monoFont, fontSize: 33, lineHeight: 1.5 }}>
            {lines.slice(0, shown).map((l, i) => (
              <div key={i} style={{ color: l.color, whiteSpace: "nowrap" }}>
                {l.txt}
              </div>
            ))}
          </div>
        </div>
        {t > strikeAt ? (
          <div
            style={{
              position: "absolute",
              left: 540 - 260,
              top: 820 - 260,
              width: 520,
              height: 520,
              transform: `translate(${shake}px, ${exitP * 900}px) scale(${interpolate(strike, [0, 1], [2.4, 1])})`,
              opacity: Math.min(1, strike * 2),
            }}
          >
            {[45, -45].map((r) => (
              <div
                key={r}
                style={{
                  position: "absolute",
                  left: -20,
                  top: 220,
                  width: 560,
                  height: 80,
                  background: "#ff3b3b",
                  borderRadius: 18,
                  border: "6px solid #200",
                  transform: `rotate(${r}deg)`,
                  boxShadow: "0 0 50px rgba(255,40,40,0.8)",
                }}
              />
            ))}
          </div>
        ) : null}
      </Stage>
    </AbsoluteFill>
  );
};
