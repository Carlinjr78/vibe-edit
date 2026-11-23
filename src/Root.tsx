import React from "react";
import { CalculateMetadataFunction, Composition, staticFile } from "remotion";
import presets from "./presets.json";
import { Edl } from "./types";
import { ModalSolo, ModalSoloProps } from "./ModalSolo";
import { Video, VideoProps } from "./Video";

// O video a renderizar e o da pasta passada em --public-dir: cada projeto tem o seu edl.json.
const calculateMetadata: CalculateMetadataFunction<VideoProps> = async ({ props }) => {
  const res = await fetch(staticFile("edl.json"));
  if (!res.ok) {
    throw new Error("edl.json nao encontrado. Rode scripts/montar_edl.py e use --public-dir=videos/<projeto>/public");
  }
  const edl = (await res.json()) as Edl;
  const preset = presets[edl.formato];
  return {
    durationInFrames: Math.round(edl.duration * preset.fps),
    fps: preset.fps,
    width: preset.width,
    height: preset.height,
    props: { ...props, edl },
  };
};

// Modal sozinho (scripts/longo_modais.py): tamanho, fps e duracao vem das props.
const metadadosDoModal: CalculateMetadataFunction<ModalSoloProps> = async ({ props }) => ({
  width: props.largura,
  height: props.altura,
  fps: props.fps,
  durationInFrames: Math.round(props.dur * props.fps),
});

export const RemotionRoot: React.FC = () => (
  <>
  <Composition
    id="Video"
    component={Video}
    calculateMetadata={calculateMetadata}
    defaultProps={{ edl: null } as VideoProps}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={30}
  />
  <Composition
    id="Modal"
    component={ModalSolo}
    calculateMetadata={metadadosDoModal}
    defaultProps={{ tipo: "inscrever", dur: 4.5, clique: 1.3, largura: 1920, altura: 1080, fps: 60 } as ModalSoloProps}
    width={1920}
    height={1080}
    fps={60}
    durationInFrames={270}
  />
  </>
);
