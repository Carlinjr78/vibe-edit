import React from "react";
import { useVideoConfig } from "remotion";

const STAGE_W = 1080;
const STAGE_H = 1920;

/**
 * Palco virtual de 1080x1920: titulos e efeitos sao posicionados nessas coordenadas.
 * No vertical a escala e 1; em outros formatos o palco encolhe e fica centralizado.
 */
export const Stage: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { width, height } = useVideoConfig();
  const k = Math.min(width / STAGE_W, height / STAGE_H);
  return (
    <div
      style={{
        position: "absolute",
        left: (width - STAGE_W * k) / 2,
        top: (height - STAGE_H * k) / 2,
        width: STAGE_W,
        height: STAGE_H,
        transform: `scale(${k})`,
        transformOrigin: "0 0",
        pointerEvents: "none",
      }}
    >
      {children}
    </div>
  );
};
