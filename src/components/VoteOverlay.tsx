import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { titleFont } from "../fonts";
import { Stage } from "./Stage";

type Props = { a: number; b: number; labelA: string; labelB: string; cta?: string };

/** Pergunta final com duas opcoes lado a lado, no topo, acima da cabeca de quem fala. */
export const VoteOverlay: React.FC<Props> = ({ a, b, labelA, labelB, cta }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const btn = (label: string, color: string, at: number, x: number, y: number, rot: number) => {
    const s = spring({ frame: (t - at) * fps, fps, config: { damping: 10, stiffness: 200 } });
    const bob = Math.sin((frame - at * fps) / 8) * 5;
    return (
      <div
        style={{
          position: "absolute",
          left: x,
          top: y + bob,
          transform: `translate(-50%, 0) scale(${s}) rotate(${rot}deg)`,
          background: color,
          color: "#0d0d0d",
          fontFamily: titleFont,
          fontSize: 52,
          padding: "8px 24px 12px",
          borderRadius: 16,
          border: "6px solid #0d0d0d",
          boxShadow: "8px 8px 0 rgba(0,0,0,0.75)",
          whiteSpace: "nowrap",
        }}
      >
        {label}
      </div>
    );
  };
  const vs = spring({ frame: (t - b + 0.1) * fps, fps, config: { damping: 12 } });
  return (
    <Stage>
      {btn(labelA, "#3DDC84", a - 0.06, 245, 175, -4)}
      {btn(labelB, "#FF5C5C", b - 0.1, 715, 175, 3)}
      {cta ? (
        <div
          style={{
            position: "absolute",
            top: 285,
            width: "100%",
            textAlign: "center",
            fontFamily: titleFont,
            fontSize: 42,
            color: "#fff",
            WebkitTextStroke: "10px #000",
            paintOrder: "stroke fill",
            opacity: vs,
            transform: `scale(${vs})`,
          }}
        >
          {cta}
        </div>
      ) : null}
    </Stage>
  );
};
