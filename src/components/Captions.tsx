import React, { useMemo } from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { captionFont } from "../fonts";
import { CaptionLayout, Word } from "../types";

type Page = { words: Word[]; start: number; end: number };

function paginate(words: Word[], maxChars: number): Page[] {
  const pages: Page[] = [];
  let cur: Word[] = [];
  const flush = () => {
    if (cur.length) pages.push({ words: cur, start: cur[0].s, end: cur[cur.length - 1].e });
    cur = [];
  };
  words.forEach((w, i) => {
    const prev = words[i - 1];
    const chars = cur.reduce((n, x) => n + x.w.length + 1, 0) + w.w.length;
    if (cur.length && (cur.length >= 3 || chars > maxChars || (prev && (prev.p === "." || prev.w.endsWith("?"))) || (prev && w.s - prev.e > 0.45))) {
      flush();
    }
    cur.push(w);
    if (w.p === ",") flush();
  });
  flush();
  // cada pagina fica ate a proxima comecar (so some se a pausa for longa)
  for (let i = 0; i < pages.length; i++) {
    const next = pages[i + 1];
    if (!next) pages[i].end += 0.6;
    else pages[i].end = next.start - pages[i].end < 1.0 ? next.start : pages[i].end + 0.5;
  }
  return pages;
}

type Props = { words: Word[]; y: number; size: number; maxChars: number; layouts?: CaptionLayout[] };

/** Legendas palavra por palavra: ate 3 palavras por vez, palavra falada em destaque. */
export const Captions: React.FC<Props> = ({ words, y: defaultY, size: defaultSize, maxChars, layouts = [] }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const pages = useMemo(() => paginate(words, maxChars), [words, maxChars]);
  const page = pages.find((p) => t >= p.start && t < p.end);
  if (!page) return null;
  // a posicao e decidida pelo inicio da pagina, para a legenda nao pular no meio da frase
  const lay = layouts.find((l) => page.start >= l.t0 && page.start < l.t1);
  const y = lay ? lay.y : defaultY;
  const fontSize = lay ? lay.size : defaultSize;
  const pIn = spring({ frame: (t - page.start) * fps, fps, config: { damping: 15, stiffness: 220 } });

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          left: 60,
          right: 60,
          top: y,
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          gap: "0px 36px",
          transform: `scale(${interpolate(pIn, [0, 1], [0.82, 1])}) translateY(${interpolate(pIn, [0, 1], [24, 0])}px)`,
          opacity: Math.min(1, pIn * 1.6),
        }}
      >
        {page.words.map((w, i) => {
          const active = t >= w.s && (t < w.e + 0.05 || i === page.words.length - 1 || t < page.words[i + 1].s);
          const said = t >= w.s;
          const a = spring({ frame: (t - w.s) * fps, fps, config: { damping: 12, stiffness: 260 } });
          const color = active ? (w.hl ? "#3DDC84" : "#FFD400") : "#FFFFFF";
          return (
            <span
              key={i}
              style={{
                fontFamily: captionFont,
                fontWeight: 900,
                fontSize,
                lineHeight: 1.12,
                letterSpacing: -1,
                textTransform: "uppercase",
                color,
                opacity: said ? 1 : 0.92,
                WebkitTextStroke: "14px #000",
                paintOrder: "stroke fill",
                textShadow: "0 8px 0 rgba(0,0,0,0.85), 0 14px 30px rgba(0,0,0,0.6)",
                transform: `scale(${active ? interpolate(a, [0, 1], [1.0, 1.07]) : 1}) rotate(${active ? interpolate(a, [0, 1], [0, -2]) : 0}deg)`,
                transformOrigin: "50% 60%",
                display: "inline-block",
              }}
            >
              {w.w}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
