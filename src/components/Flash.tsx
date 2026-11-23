import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const clampOpts = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** Flash branco curto nos cortes (mais forte nas trocas de assunto). */
export const Flash: React.FC<{ big: boolean }> = ({ big }) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [0, 2, big ? 7 : 4], [0, big ? 0.55 : 0.22, 0], clampOpts);
  return <AbsoluteFill style={{ backgroundColor: "#fff", opacity: o, pointerEvents: "none" }} />;
};
