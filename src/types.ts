import presets from "./presets.json";

export type Formato = keyof typeof presets;

export type Key = { t: number; x: number; y: number; z: number; ease: "inout" | "out" | "linear" };
export type Highlight = { t0: number; t1: number; x: number; y: number; w: number; h: number; color: string };
export type Mag = {
  t0: number; t1: number; sx: number; sy: number; sw: number; sh: number;
  ox: number; oy: number; scale: number; label: string | null; color: string;
};
export type Shot = {
  name: string; at: number; dur: number; src: string; from: number;
  srcW: number; srcH: number; keys: Key[]; highlights: Highlight[]; mags: Mag[];
};
/** efeitos: false mostra o video como veio, sem zoom, drift, filtro nem gradiente. */
export type CamShotT = { at: number; dur: number; src: string; from: number; zoom: number; efeitos?: boolean };
export type Selo = { src: string; x: number; y: number; w: number; h: number };
export type TitlePart = { t: string; color?: string };
export type CalloutT = {
  t0: number; t1: number; text: string; kind: "title" | "pill"; y: number;
  color?: string; parts?: TitlePart[];
};
export type TermLine = { txt: string; color: string };
export type TipoModal = "inscrever" | "curtir" | "twitch";
export type PosModal = "top-center" | "top-left" | "top-right" | "bottom-left" | "bottom-right";
export type Overlay =
  | { type: "cta"; t0: number; t1: number; clique: number; tipo: TipoModal; pos?: PosModal; texto?: string }
  | { type: "terminal"; t0: number; t1: number; strike: number; title?: string; lines?: TermLine[] }
  | { type: "windows"; t0: number; t1: number; collapse: number; titles?: string[] }
  | { type: "vote"; t0: number; t1: number; a: number; b: number; labelA: string; labelB: string; cta?: string };
/** Perfil do canal usado nos modais (nome, avatar e Twitch); vem de src/canal.json pelo edicao_lib. */
export type CanalT = { perfil?: string; nome: string; twitch?: string; avatar?: string };
export type Word = { w: string; s: number; e: number; p: string; hl: boolean };
export type CaptionLayout = { t0: number; t1: number; y: number; size: number };
export type Edl = {
  formato: Formato; duration: number; narration: string; music?: string;
  cams: CamShotT[]; shots: Shot[]; callouts: CalloutT[]; overlays: Overlay[];
  transitions: { at: number; big: boolean }[];
  /** dur: quanto tocar, em segundos (padrao 0,6). */
  sfx: { src: string; at: number; volume: number; dur?: number }[];
  captions: Word[];
  captionLayouts?: CaptionLayout[];
  selo?: Selo;
  barra?: boolean;
  canal?: CanalT;
};
