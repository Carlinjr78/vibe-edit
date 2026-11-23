import React from "react";
import { AbsoluteFill, Easing, OffthreadVideo, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { CamShotT } from "../types";

/** Video falando para a camera, com punch-in alternado a cada corte e um leve "drift". */
export const CamShot: React.FC<{ shot: CamShotT; bigEnter: boolean }> = ({ shot, bigEnter }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (shot.efeitos === false) {
    return (
      <AbsoluteFill style={{ backgroundColor: "#000" }}>
        <OffthreadVideo src={staticFile(shot.src)} trimBefore={Math.round(shot.from * fps)} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </AbsoluteFill>
    );
  }

  const drift = interpolate(frame, [0, Math.max(1, shot.dur * fps)], [1, 1.025]);
  const enterP = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const enterScale = bigEnter ? interpolate(enterP, [0, 1], [1.12, 1]) : 1;
  const blur = bigEnter ? interpolate(enterP, [0, 1], [12, 0]) : 0;
  return (
    <AbsoluteFill style={{ backgroundColor: "#000", overflow: "hidden" }}>
      <AbsoluteFill
        style={{
          transform: `scale(${shot.zoom * drift * enterScale})`,
          // origem alta: o zoom empurra menos o rosto para baixo (onde ficam as legendas)
          transformOrigin: "50% 28%",
          filter: `contrast(1.06) saturate(1.12)${blur > 0.2 ? ` blur(${blur}px)` : ""}`,
        }}
      >
        <OffthreadVideo
          src={staticFile(shot.src)}
          trimBefore={Math.round(shot.from * fps)}
          muted
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </AbsoluteFill>
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,0) 55%, rgba(0,0,0,0.45) 100%)" }} />
    </AbsoluteFill>
  );
};
