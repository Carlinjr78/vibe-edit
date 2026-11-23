import React from "react";
import { AbsoluteFill } from "remotion";
import { CtaModal } from "./components/CtaModal";
import { CanalT, TipoModal } from "./types";

/** Um modal sozinho, sem fundo (transparente), para colar por cima de um video longo com o ffmpeg. */
export type ModalSoloProps = {
  tipo: TipoModal;
  canal?: CanalT;
  dur: number;
  clique: number;
  largura: number;
  altura: number;
  fps: number;
};

export const ModalSolo: React.FC<ModalSoloProps> = ({ tipo, canal, dur, clique }) => (
  <AbsoluteFill>
    <CtaModal dur={dur} clickAt={clique} tipo={tipo} canal={canal} />
  </AbsoluteFill>
);
