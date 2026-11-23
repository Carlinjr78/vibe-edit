import React from "react";
import { Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import canalJson from "../canal.json";
import { captionFont } from "../fonts";
import { CanalT, PosModal, TipoModal } from "../types";

const clampOpts = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const CARD_W = 770;
const CARD_H = 150;
const MARGEM = 44;

// EDL antigo, sem o campo canal: usa o perfil padrao do canal.json.
const PADRAO: CanalT = canalJson.perfis[canalJson.perfil_padrao as keyof typeof canalJson.perfis];

const COR: Record<TipoModal, string> = { inscrever: "#FF3B30", curtir: "#3EA6FF", twitch: "#9146FF" };

function textos(tipo: TipoModal, canal: CanalT, texto?: string): [string, string] {
  if (tipo === "inscrever") return [canal.nome || "Seu canal", texto ?? "Inscreva-se no canal"];
  if (tipo === "curtir") return ["Curtiu até aqui?", texto ?? "Deixa o like"];
  return ["Me segue na Twitch", texto ?? `twitch.tv/${canal.twitch || "seucanal"}`];
}

function posicionar(pos: PosModal, width: number, height: number) {
  const centroX = (width - CARD_W) / 2;
  const direita = width - CARD_W - MARGEM;
  const baixo = height - CARD_H - MARGEM;
  // no vertical o topo comeca abaixo da interface do Reels (area segura: 250 px de cima)
  const topo = height > width ? 260 : MARGEM;
  const mapa = {
    "top-center": { left: centroX, top: topo, dx: 0, dy: -70 },
    "top-left": { left: MARGEM, top: topo, dx: -90, dy: 0 },
    "top-right": { left: direita, top: topo, dx: 90, dy: 0 },
    "bottom-left": { left: MARGEM, top: baixo, dx: -90, dy: 0 },
    "bottom-right": { left: direita, top: baixo, dx: 90, dy: 0 },
  };
  return mapa[pos];
}

const Polegar: React.FC<{ cheio: boolean; cor: string }> = ({ cheio, cor }) => (
  <svg width="58" height="58" viewBox="0 0 24 24">
    <path
      d="M7 10v11H3V10h4zm2 11h8.5a2 2 0 0 0 2-1.6l1.4-7A2 2 0 0 0 19 10h-5l.8-4.2A1.8 1.8 0 0 0 13 3.6L9 9.5V21z"
      fill={cheio ? cor : "none"}
      stroke={cheio ? cor : "#fff"}
      strokeWidth="1.6"
      strokeLinejoin="round"
    />
  </svg>
);

const Coracao: React.FC<{ cheio: boolean }> = ({ cheio }) => (
  <svg width="34" height="34" viewBox="0 0 24 24">
    <path
      d="M12 21s-8-5.2-8-11.2A4.8 4.8 0 0 1 12 6.6a4.8 4.8 0 0 1 8 3.2C20 15.800 12 21 12 21z"
      fill={cheio ? "#fff" : "none"}
      stroke="#fff"
      strokeWidth="2"
      strokeLinejoin="round"
    />
  </svg>
);

const Cursor: React.FC = () => (
  <svg width="54" height="54" viewBox="0 0 24 24" style={{ filter: "drop-shadow(0 4px 8px rgba(0,0,0,.6))" }}>
    <path d="M5 2l14 12-6.500 1 3.500 7-3 1.500-3.500-7L5 21z" fill="#fff" stroke="#111" strokeWidth="1.3" strokeLinejoin="round" />
  </svg>
);

type Props = { dur: number; clickAt: number; tipo: TipoModal; pos?: PosModal; texto?: string; canal?: CanalT };

/** Modal do canal: aparece no canto, o cursor clica no botao e ele muda de estado. */
export const CtaModal: React.FC<Props> = ({ dur, clickAt, tipo, pos, texto, canal = PADRAO }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const t = frame / fps;
  const lugar = posicionar(pos ?? (height > width ? "top-center" : "top-right"), width, height);
  const entra = spring({ frame, fps, config: { damping: 14, stiffness: 170 } });
  const sai = interpolate(t, [dur - 0.28, dur], [1, 0], clampOpts);
  const clicou = t >= clickAt;
  const pop = spring({ frame: frame - clickAt * fps, fps, config: { damping: 8, stiffness: 260 } });
  const cor = COR[tipo];
  const [titulo, subtitulo] = textos(tipo, canal, texto);

  const botaoW = tipo === "curtir" ? 100 : 216;
  const botaoH = tipo === "curtir" ? 100 : 72;
  const botaoX = CARD_W - botaoW - 26;
  const botaoY = (CARD_H - botaoH) / 2;
  const alvoX = botaoX + botaoW / 2;
  const alvoY = botaoY + botaoH / 2;
  const chegada = interpolate(t, [0.3, clickAt - 0.06], [0, 1], { ...clampOpts, easing: (x) => 1 - (1 - x) ** 3 });
  const cursorX = interpolate(chegada, [0, 1], [CARD_W + 80, alvoX]);
  const cursorY = interpolate(chegada, [0, 1], [CARD_H + 110, alvoY]);
  const cursorOpacidade = interpolate(t, [0.25, 0.4, clickAt + 0.3, clickAt + 0.55], [0, 1, 1, 0], clampOpts);
  const aperto = t >= clickAt - 0.05 && t < clickAt + 0.1 ? 0.9 : 1;

  const rotulo = tipo === "inscrever" ? (clicou ? "INSCRITO" : "INSCREVER-SE") : clicou ? "SEGUINDO" : "SEGUIR";

  return (
    <div
      style={{
        position: "absolute",
        left: lugar.left,
        top: lugar.top,
        width: CARD_W,
        height: CARD_H,
        transform: `translate(${lugar.dx * (1 - entra * sai)}px, ${lugar.dy * (1 - entra * sai)}px)`,
        opacity: Math.min(1, entra * 1.5) * sai,
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "rgba(16,16,20,0.96)",
          border: `4px solid ${cor}`,
          borderRadius: 26,
          boxShadow: `0 18px 50px rgba(0,0,0,0.65), 0 0 34px ${cor}66`,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 26,
          top: (CARD_H - 96) / 2,
          width: 96,
          height: 96,
          borderRadius: 48,
          background: cor,
          overflow: "hidden",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "#fff",
          fontFamily: captionFont,
          fontWeight: 900,
          fontSize: 50,
        }}
      >
        {canal.avatar ? (
          <Img src={staticFile(canal.avatar)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        ) : (
          (canal.nome || "C").charAt(0).toUpperCase()
        )}
      </div>
      <div
        style={{
          position: "absolute",
          left: 142,
          right: botaoW + 40,
          top: 0,
          bottom: 0,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          fontFamily: captionFont,
          color: "#fff",
          whiteSpace: "nowrap",
          overflow: "hidden",
        }}
      >
        <div style={{ fontSize: 31, fontWeight: 900, lineHeight: 1.2, overflow: "hidden", textOverflow: "ellipsis" }}>{titulo}</div>
        <div style={{ fontSize: 25, fontWeight: 800, color: "#c9c9d2", lineHeight: 1.3, overflow: "hidden", textOverflow: "ellipsis" }}>{subtitulo}</div>
      </div>
      <div
        style={{
          position: "absolute",
          left: botaoX,
          top: botaoY,
          width: botaoW,
          height: botaoH,
          borderRadius: botaoH / 2,
          background: tipo === "curtir" ? "rgba(255,255,255,0.1)" : clicou && tipo === "inscrever" ? "#4a4a52" : cor,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 10,
          color: "#fff",
          fontFamily: captionFont,
          fontWeight: 900,
          fontSize: tipo === "inscrever" && !clicou ? 23 : 27,
          transform: `scale(${aperto * (clicou ? interpolate(pop, [0, 1], [1.16, 1]) : 1)})`,
        }}
      >
        {tipo === "curtir" ? (
          <Polegar cheio={clicou} cor={cor} />
        ) : (
          <>
            {tipo === "twitch" ? <Coracao cheio={clicou} /> : null}
            {rotulo}
          </>
        )}
      </div>
      <div style={{ position: "absolute", left: cursorX, top: cursorY, opacity: cursorOpacidade, transform: `scale(${aperto})` }}>
        <Cursor />
      </div>
    </div>
  );
};
