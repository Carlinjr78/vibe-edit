import React from "react";
import { AbsoluteFill, Easing, Img, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { titleFont } from "../fonts";
import { Highlight, Key, Mag, Shot } from "../types";

const EASE = {
  inout: Easing.bezier(0.65, 0, 0.35, 1),
  out: Easing.bezier(0.16, 1, 0.3, 1),
  linear: (x: number) => x,
};

const clamp = (v: number, a: number, b: number) => Math.min(b, Math.max(a, v));

const IMAGEM = /\.(png|jpe?g|webp)$/i;

/** Gravacao de tela ou imagem parada (ex.: print da fonte de uma noticia). */
const Midia: React.FC<{ src: string; trim: number; style: React.CSSProperties }> = ({ src, trim, style }) =>
  IMAGEM.test(src) ? <Img src={staticFile(src)} style={style} /> : <OffthreadVideo src={staticFile(src)} trimBefore={trim} muted style={style} />;

type Size = { W: number; H: number; srcW: number; srcH: number };

/** Camera interpolada entre keyframes; zoom interpolado em escala log para parecer constante. */
export function camAt(keys: Key[], t: number, { W, H, srcW, srcH }: Size) {
  let k = keys[0];
  if (t > keys[0].t) {
    k = keys[keys.length - 1];
    for (let i = 0; i < keys.length - 1; i++) {
      const a = keys[i];
      const b = keys[i + 1];
      if (t >= a.t && t <= b.t) {
        const p = EASE[b.ease]((t - a.t) / Math.max(1e-6, b.t - a.t));
        k = {
          t,
          x: a.x + (b.x - a.x) * p,
          y: a.y + (b.y - a.y) * p,
          z: Math.exp(Math.log(a.z) + (Math.log(b.z) - Math.log(a.z)) * p),
          ease: b.ease,
        };
        break;
      }
    }
  }
  const vw = W / k.z;
  const vh = H / k.z;
  const x = vw >= srcW ? srcW / 2 : clamp(k.x, vw / 2, srcW - vw / 2);
  const y = vh >= srcH ? srcH / 2 : clamp(k.y, vh / 2, srcH - vh / 2);
  return { x, y, z: k.z };
}

const HighlightBox: React.FC<{ h: Highlight; t: number; z: number }> = ({ h, t, z }) => {
  const { fps } = useVideoConfig();
  if (t < h.t0 || t > h.t1) return null;
  const local = (t - h.t0) * fps;
  const inS = spring({ frame: local, fps, config: { damping: 14, stiffness: 180 } });
  const out = interpolate(t, [h.t1 - 0.15, h.t1], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const pulse = 1 + 0.25 * Math.sin(local / 4);
  const bw = (7 * pulse) / z;
  const pad = 10 / z;
  return (
    <div
      style={{
        position: "absolute",
        left: h.x - pad,
        top: h.y - pad,
        width: h.w + pad * 2,
        height: h.h + pad * 2,
        border: `${bw}px solid ${h.color}`,
        borderRadius: 18 / z,
        boxShadow: `0 0 ${28 / z}px ${h.color}, inset 0 0 ${18 / z}px ${h.color}66`,
        opacity: inS * out,
        transform: `scale(${interpolate(inS, [0, 1], [1.25, 1])})`,
        transformOrigin: "center",
      }}
    />
  );
};

/** Lupa: recorte ampliado da gravacao, para detalhes pequenos que a camera nao consegue centralizar. */
const MagCard: React.FC<{ m: Mag; t: number; shot: Shot; trim: number }> = ({ m, t, shot, trim }) => {
  const { fps } = useVideoConfig();
  if (t < m.t0 || t > m.t1) return null;
  const local = (t - m.t0) * fps;
  const s = spring({ frame: local, fps, config: { damping: 12, stiffness: 170, mass: 0.8 } });
  const out = interpolate(t, [m.t1 - 0.12, m.t1], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const w = m.sw * m.scale;
  const h = m.sh * m.scale;
  return (
    <div
      style={{
        position: "absolute",
        left: m.ox - w / 2,
        top: m.oy - h / 2,
        width: w,
        height: h,
        transform: `scale(${interpolate(s, [0, 1], [0.4, 1]) * (0.85 + 0.15 * out)}) rotate(${interpolate(s, [0, 1], [-6, 0])}deg)`,
        opacity: Math.min(1, s * 1.5) * out,
      }}
    >
      {m.label ? (
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: -74,
            transform: "translateX(-50%)",
            background: m.color,
            color: "#111",
            fontFamily: titleFont,
            fontSize: 44,
            padding: "6px 22px",
            borderRadius: 14,
            whiteSpace: "nowrap",
            boxShadow: "6px 6px 0 rgba(0,0,0,0.55)",
          }}
        >
          {m.label}
        </div>
      ) : null}
      <div
        style={{
          width: "100%",
          height: "100%",
          overflow: "hidden",
          borderRadius: 22,
          border: `5px solid ${m.color}`,
          boxShadow: `0 18px 60px rgba(0,0,0,0.6), 0 0 40px ${m.color}88`,
          background: "#111",
          position: "relative",
        }}
      >
        <div style={{ position: "absolute", left: -m.sx * m.scale, top: -m.sy * m.scale, width: shot.srcW * m.scale, height: shot.srcH * m.scale }}>
          <Midia src={shot.src} trim={trim} style={{ width: shot.srcW * m.scale, height: shot.srcH * m.scale }} />
        </div>
      </div>
    </div>
  );
};

/** Trecho de gravacao de tela (ou imagem) com camera (zoom/pan), destaques e lupas. */
export const ScreenShot: React.FC<{ shot: Shot; bigEnter: boolean }> = ({ shot, bigEnter }) => {
  const frame = useCurrentFrame();
  const { fps, width: W, height: H } = useVideoConfig();
  const t = frame / fps;
  const absT = shot.at + t;
  const { srcW, srcH } = shot;
  const cam = camAt(shot.keys, t, { W, H, srcW, srcH });
  const trim = Math.round(shot.from * fps);
  const needsBg = shot.keys.some((k) => k.z * srcH < H - 2);

  // entrada: zoom + desfoque rapido (efeito "punch")
  const enterP = interpolate(frame, [0, bigEnter ? 9 : 6], [0, 1], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const enterScale = interpolate(enterP, [0, 1], [bigEnter ? 1.14 : 1.05, 1]);
  const enterBlur = interpolate(enterP, [0, 1], [bigEnter ? 14 : 5, 0]);

  const tx = W / 2 - cam.x * cam.z;
  const ty = H / 2 - cam.y * cam.z;
  const bandH = srcH * cam.z;
  const bgH = H * 1.1;
  const bgW = (bgH / srcH) * srcW;

  return (
    <AbsoluteFill style={{ backgroundColor: "#0b0d12", overflow: "hidden" }}>
      {needsBg ? (
        <AbsoluteFill style={{ opacity: interpolate(bandH, [H * 0.7, H], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
          <Midia
            src={shot.src}
            trim={trim}
            style={{
              position: "absolute",
              height: bgH,
              width: bgW,
              left: W / 2 - bgW / 2,
              top: -H * 0.05,
              filter: "blur(38px) brightness(0.42) saturate(1.3)",
            }}
          />
          <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, rgba(0,0,0,0) 30%, rgba(0,0,0,0.55) 100%)" }} />
        </AbsoluteFill>
      ) : null}
      <AbsoluteFill style={{ transform: `scale(${enterScale})`, filter: enterBlur > 0.2 ? `blur(${enterBlur}px)` : undefined }}>
        <div
          style={{
            position: "absolute",
            left: 0,
            top: 0,
            width: srcW,
            height: srcH,
            transformOrigin: "0 0",
            transform: `translate(${tx}px, ${ty}px) scale(${cam.z})`,
            boxShadow: bandH < H - 2 ? "0 30px 120px rgba(0,0,0,0.7)" : undefined,
          }}
        >
          <Midia src={shot.src} trim={trim} style={{ width: srcW, height: srcH }} />
          {shot.highlights.map((h, i) => (
            <HighlightBox key={i} h={h} t={absT} z={cam.z} />
          ))}
        </div>
      </AbsoluteFill>
      {shot.mags.map((m, i) => (
        <MagCard key={i} m={m} t={absT} shot={shot} trim={trim} />
      ))}
    </AbsoluteFill>
  );
};
