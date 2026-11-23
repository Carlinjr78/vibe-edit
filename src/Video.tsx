import React from "react";
import { AbsoluteFill, Audio, Img, Sequence, staticFile, useVideoConfig } from "remotion";
import { Callout } from "./components/Callout";
import { CamShot } from "./components/CamShot";
import { Captions } from "./components/Captions";
import { CtaModal } from "./components/CtaModal";
import { Flash } from "./components/Flash";
import { ProgressBar } from "./components/ProgressBar";
import { ScreenShot } from "./components/ScreenShot";
import { TerminalOverlay } from "./components/TerminalOverlay";
import { VoteOverlay } from "./components/VoteOverlay";
import { WindowsOverlay } from "./components/WindowsOverlay";
import presets from "./presets.json";
import { Edl } from "./types";

export type VideoProps = { edl: Edl | null };

export const Video: React.FC<VideoProps> = ({ edl }) => {
  const { fps } = useVideoConfig();
  if (!edl) return null;
  const f = (s: number) => Math.round(s * fps);
  const span = (a: number, b: number) => ({ from: f(a), durationInFrames: Math.max(1, f(b) - f(a)) });
  const isBig = (t: number) => edl.transitions.some((x) => x.big && Math.abs(x.at - t) < 0.02);
  const caption = presets[edl.formato].caption;

  return (
    <AbsoluteFill style={{ backgroundColor: "#0b0d12" }}>
      {edl.cams.map((c, i) => (
        <Sequence key={`cam${i}`} {...span(c.at, c.at + c.dur)} premountFor={30} name={`camera ${i + 1}`}>
          <CamShot shot={c} bigEnter={isBig(c.at)} />
        </Sequence>
      ))}
      {edl.shots.map((s) => (
        <Sequence key={s.name} {...span(s.at, s.at + s.dur)} premountFor={30} name={`tela ${s.name}`}>
          <ScreenShot shot={s} bigEnter={isBig(s.at)} />
        </Sequence>
      ))}

      {edl.overlays.map((o, i) => (
        <Sequence key={`ov${i}`} {...span(o.t0, o.t1)} name={o.type}>
          {o.type === "cta" ? (
            <CtaModal dur={o.t1 - o.t0} clickAt={o.clique - o.t0} tipo={o.tipo} pos={o.pos} texto={o.texto} canal={edl.canal} />
          ) : o.type === "terminal" ? (
            <TerminalOverlay dur={o.t1 - o.t0} strikeAt={o.strike - o.t0} title={o.title} lines={o.lines} />
          ) : o.type === "windows" ? (
            <WindowsOverlay dur={o.t1 - o.t0} collapseAt={o.collapse - o.t0} titles={o.titles} />
          ) : (
            <VoteOverlay a={o.a - o.t0} b={o.b - o.t0} labelA={o.labelA} labelB={o.labelB} cta={o.cta} />
          )}
        </Sequence>
      ))}
      {edl.callouts.map((c, i) => (
        <Sequence key={`co${i}`} {...span(c.t0, c.t1)} name={`titulo ${c.text}`}>
          <Callout c={c} />
        </Sequence>
      ))}

      {edl.selo ? (
        <Img src={staticFile(edl.selo.src)} style={{ position: "absolute", left: edl.selo.x, top: edl.selo.y, width: edl.selo.w, height: edl.selo.h }} />
      ) : null}

      <Captions words={edl.captions} y={caption.y} size={caption.size} maxChars={caption.maxChars} layouts={edl.captionLayouts} />

      {edl.transitions.map((tr, i) => (
        <Sequence key={`tr${i}`} from={Math.max(0, f(tr.at) - 1)} durationInFrames={9} name="flash">
          <Flash big={tr.big} />
        </Sequence>
      ))}
      {edl.barra === false ? null : <ProgressBar total={edl.duration} />}

      <Audio src={staticFile(edl.narration)} />
      {edl.music ? <Audio src={staticFile(edl.music)} /> : null}
      {edl.sfx.map((s, i) => (
        <Sequence key={`sfx${i}`} from={Math.max(0, f(s.at))} durationInFrames={f(s.dur ?? 0.6)} name={`sfx ${s.src}`}>
          <Audio src={staticFile(s.src)} volume={s.volume} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
