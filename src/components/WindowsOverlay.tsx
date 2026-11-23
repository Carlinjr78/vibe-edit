import React from "react";
import { Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { monoFont } from "../fonts";
import { Stage } from "./Stage";

const clampOpts = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const POSICOES = [
  { x: 70, y: 430, r: -7 },
  { x: 560, y: 380, r: 6 },
  { x: 120, y: 760, r: 4 },
  { x: 600, y: 720, r: -5 },
  { x: 330, y: 1020, r: 8 },
  { x: 640, y: 1060, r: -3 },
];

const TITULOS_PADRAO = ["claude — loja-virtual", "codex — chatbot", "claude — site", "terminal 4", "claude — HUB", "codex — testes"];

type Props = { dur: number; collapseAt: number; titles?: string[] };

/** Ate 6 janelas de terminal que aparecem e depois se juntam e somem no momento `collapseAt`. */
export const WindowsOverlay: React.FC<Props> = ({ dur, collapseAt, titles = TITULOS_PADRAO }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const col = interpolate(t, [collapseAt, collapseAt + 0.35], [0, 1], { ...clampOpts, easing: Easing.in(Easing.back(1.4)) });
  const fade = interpolate(t, [dur - 0.1, dur], [1, 0], clampOpts);
  return (
    <Stage>
      <div style={{ position: "absolute", inset: 0, opacity: fade }}>
        {POSICOES.slice(0, titles.length).map((w, i) => {
          const s = spring({ frame: frame - i * 4, fps, config: { damping: 12, stiffness: 200 } });
          const fl = Math.sin((frame + i * 13) / 9) * 6;
          const x = w.x + (540 - 185 - w.x) * col;
          const y = w.y + fl + (760 - 115 - w.y) * col;
          return (
            <div
              key={i}
              style={{
                position: "absolute",
                left: x,
                top: y,
                width: 370,
                height: 230,
                background: "#0d1117",
                border: "3px solid #3b4250",
                borderRadius: 16,
                boxShadow: "0 20px 60px rgba(0,0,0,0.7)",
                transform: `scale(${s * (1 - col)}) rotate(${w.r * (1 + col * 3)}deg)`,
                overflow: "hidden",
              }}
            >
              <div style={{ height: 40, background: "#161b22", display: "flex", alignItems: "center", gap: 9, paddingLeft: 14 }}>
                {["#ff5f57", "#febc2e", "#28c840"].map((c) => (
                  <div key={c} style={{ width: 14, height: 14, borderRadius: 7, background: c }} />
                ))}
                <div style={{ marginLeft: 10, color: "#8b949e", fontFamily: monoFont, fontSize: 19 }}>{titles[i]}</div>
              </div>
              <div style={{ padding: "12px 16px", fontFamily: monoFont, fontSize: 20, color: "#7ee787", lineHeight: 1.45 }}>
                <div>● trabalhando...</div>
                <div style={{ color: "#8b949e" }}>  ⎿ {3 + i} arquivos</div>
                <div style={{ color: i % 2 ? "#ffa657" : "#d2a8ff" }}>{i % 2 ? "? precisa de você" : "● rodando testes"}</div>
              </div>
            </div>
          );
        })}
      </div>
    </Stage>
  );
};
