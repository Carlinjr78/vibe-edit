import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { titleFont } from "../fonts";
import { CalloutT } from "../types";
import { Stage } from "./Stage";

const clampOpts = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** Titulo grande (pode ter partes coloridas, via `parts`) ou etiqueta colorida. */
export const Callout: React.FC<{ c: CalloutT }> = ({ c }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps; // relativo ao inicio do callout
  const dur = c.t1 - c.t0;
  const s = spring({ frame, fps, config: { damping: 11, stiffness: 190, mass: 0.9 } });
  const out = interpolate(t, [dur - 0.18, dur], [1, 0], clampOpts);
  const wobble = Math.sin(frame / 7) * 1.2;

  if (c.kind === "title") {
    return (
      <Stage>
        <div
          style={{
            position: "absolute",
            top: c.y,
            width: "100%",
            textAlign: "center",
            fontFamily: titleFont,
            fontSize: 168,
            letterSpacing: 4,
            color: "#FFFFFF",
            WebkitTextStroke: "16px #1a1205",
            paintOrder: "stroke fill",
            textShadow: "10px 10px 0 #000, 0 0 60px rgba(255,190,60,0.65)",
            transform: `scale(${interpolate(s, [0, 1], [0.2, 1]) * interpolate(out, [0, 1], [1.25, 1])}) rotate(${interpolate(s, [0, 1], [-14, 0]) + wobble * 0.4}deg)`,
            opacity: Math.min(1, s * 2) * out,
          }}
        >
          {c.parts
            ? c.parts.map((p, i) => (
                <span key={i} style={{ color: p.color ?? "#FFFFFF" }}>
                  {p.t}
                </span>
              ))
            : c.text}
        </div>
      </Stage>
    );
  }
  return (
    <Stage>
      <div style={{ position: "absolute", top: c.y, width: "100%", display: "flex", justifyContent: "center" }}>
        <div
          style={{
            background: c.color ?? "#FFD400",
            color: "#0d0d0d",
            fontFamily: titleFont,
            fontSize: 72,
            padding: "10px 34px 14px",
            borderRadius: 18,
            border: "6px solid #0d0d0d",
            boxShadow: "10px 10px 0 rgba(0,0,0,0.75)",
            transform: `translateY(${interpolate(s, [0, 1], [60, 0])}px) scale(${interpolate(s, [0, 1], [0.5, 1])}) rotate(${-3 + wobble}deg)`,
            opacity: Math.min(1, s * 2) * out,
            whiteSpace: "nowrap",
          }}
        >
          {c.text}
        </div>
      </div>
    </Stage>
  );
};
