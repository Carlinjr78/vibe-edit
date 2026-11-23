import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";

export const ProgressBar: React.FC<{ total: number }> = ({ total }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = Math.min(1, frame / fps / total);
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div style={{ position: "absolute", top: 0, left: 0, height: 10, width: `${p * 100}%`, background: "linear-gradient(90deg,#FFC93C,#3DDC84)", boxShadow: "0 0 18px rgba(255,201,60,0.8)" }} />
    </AbsoluteFill>
  );
};
