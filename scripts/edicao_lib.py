"""Ferramentas para escrever o edicao.py de cada video.

A edicao e ancorada nas palavras da narracao final: se a narracao mudar, cortes, zooms e efeitos acompanham.
Coordenadas de camera, destaques e lupas sao em pixels do arquivo de origem.
Camera: x, y = ponto de foco; z = zoom (1 = um pixel da gravacao vira um pixel do video).
Tempos t0/t1/at sao em segundos na timeline final; o `t` de K() e relativo ao inicio da cena.
"""
import json
import re
import shutil
from pathlib import Path

from kit_comum import KIT, sondar

Y, R, G, B, ORANGE, PINK = "#FFD400", "#FF4D4D", "#3DDC84", "#5AB0FF", "#F4A15D", "#FF5C8A"
TIPOS_MODAL = {"inscrever", "curtir", "twitch"}
CLIQUE_MODAL = 1.3  # segundos depois do modal aparecer em que o cursor clica


def sons_do_modal(m: dict) -> list[dict]:
    """Efeitos padronizados de cada modal (assets/livre/sfx): um pop quando aparece e outro no clique."""
    return [{"src": "pop.wav", "at": m["t0"], "volume": 0.5}, {"src": "pop.wav", "at": m["clique"], "volume": 0.7}]


def K(t, x, y, z, ease="inout"):
    return {"t": round(t, 3), "x": x, "y": y, "z": z, "ease": ease}


def HL(t0, t1, x, y, w, h, color=Y):
    return {"t0": round(t0, 3), "t1": round(t1, 3), "x": x, "y": y, "w": w, "h": h, "color": color}


def MAG(t0, t1, rect, ox, oy, scale, label=None, color=Y):
    sx, sy, sw, sh = rect
    return {"t0": round(t0, 3), "t1": round(t1, 3), "sx": sx, "sy": sy, "sw": sw, "sh": sh, "ox": ox, "oy": oy,
            "scale": scale, "label": label, "color": color}


class Roteiro:
    """O que o edicao.py preenche; salvar() valida e grava o edl.json."""

    def __init__(self, projeto):
        self.p = projeto
        self.cuts = json.loads((projeto.build / "cuts.json").read_text(encoding="utf-8"))
        self.fala = json.loads((projeto.build / "narration_raw.json").read_text(encoding="utf-8"))
        self.DUR = round(self.cuts["duration"], 2)
        self.captions = []
        self.shots, self.cams, self.callouts, self.overlays = [], [], [], []
        self.transitions, self.sfx_extra, self.layouts, self.modais = [], [], [], []
        self.fontes = {}
        self.selo = None  # imagem fixa o video todo: {"src": "selo.png", "x": 0, "y": 0, "w": 300, "h": 100}

    # ------------------------------------------------------------ legendas e ancoras
    def preparar_legendas(self, correcoes=None, juntar=None, destaque=()):
        """correcoes: {"cloud": "Claude"}; juntar: {("vibe", "edit"): "VibeEdit"}; destaque: palavras em verde."""
        correcoes, juntar = correcoes or {}, juntar or {}
        fim_fala = max(q["at"] + q["to"] - q["from"] for q in self.cuts["pieces"])
        legendas = []
        for s in self.fala["segments"]:
            if s["end"] - s["start"] < 0.3 and len(s["words"]) > 1:
                continue  # alucinacao do whisper no silencio do final
            for w in s["words"]:
                if w["s"] > fim_fala:
                    continue
                bruto = w["w"].strip()
                # o hifen fica dentro da palavra ("Segunda-feira"), so sai das pontas
                nucleo = re.sub(r"[^\wÀ-ÿ?-]", "", bruto).strip("-")
                chave = nucleo.rstrip("?").lower()
                if chave in correcoes:
                    nucleo = correcoes[chave] + ("?" if nucleo.endswith("?") else "")
                pontuacao = "," if bruto.endswith(",") else ("." if bruto.endswith((".", "!", "…")) else "")
                legendas.append({"w": nucleo, "s": round(w["s"], 3), "e": round(w["e"], 3), "p": pontuacao})
        unidas = []
        for c in legendas:
            if unidas and (unidas[-1]["w"].lower(), c["w"].lower()) in juntar:
                unidas[-1].update({"w": juntar[(unidas[-1]["w"].lower(), c["w"].lower())], "e": c["e"], "p": c["p"] or ","})
                continue
            unidas.append(c)
        for i, c in enumerate(unidas):
            prox = unidas[i + 1]["s"] if i + 1 < len(unidas) else self.DUR
            c["e"] = round(min(c["e"], prox), 3)
            c["hl"] = c["w"].rstrip("?") in set(destaque)
        self.captions = unidas

    def w(self, palavra, depois=0.0):
        """Inicio da primeira ocorrencia exata de `palavra` a partir de `depois`."""
        for c in self.captions:
            if c["s"] >= depois - 1e-6 and c["w"].lower().rstrip("?") == palavra.lower():
                return c["s"]
        raise KeyError(f"palavra nao encontrada: {palavra} (depois de {depois})")

    def secao(self, nome):
        """(inicio, fim) de uma secao na timeline final."""
        ps = [q for q in self.cuts["pieces"] if q["section"] == nome]
        if not ps:
            raise KeyError(f"secao nao encontrada: {nome}")
        return min(q["at"] for q in ps), max(q["at"] + q["to"] - q["from"] for q in ps)

    def cut_before(self, nome):
        """Ponto de corte visual: no respiro antes da secao."""
        return round(self.secao(nome)[0] - 0.08, 2)

    # ------------------------------------------------------------ cenas
    def _fonte(self, src):
        if src not in self.fontes:
            self.fontes[src] = sondar(self.p.public / src)
        return self.fontes[src]

    def SHOT(self, name, at, end, src_from, keys, hl=(), mags=(), src="tela.mp4"):
        info = self._fonte(src)
        return {"name": name, "at": round(at, 3), "dur": round(end - at, 3), "src": src, "from": src_from,
                "srcW": info["width"], "srcH": info["height"], "keys": keys, "highlights": list(hl), "mags": list(mags)}

    def camera_da_secao(self, nome, inicio, fim, zoom_alternado=1.05):
        """Cria as cenas de camera de uma secao; cada corte interno alterna o zoom para disfarcar o pulo."""
        pecas = [q for q in self.cuts["pieces"] if q["section"] == nome and q.get("cam")]
        for k, q in enumerate(pecas):
            ini = inicio if k == 0 else q["at"]
            ate = pecas[k + 1]["at"] if k + 1 < len(pecas) else fim
            self.cams.append({"at": round(ini, 3), "dur": round(ate - ini, 3), "src": q["cam"] + ".mp4",
                              "from": round(q["camFrom"] - (q["at"] - ini), 3),
                              "zoom": 1.0 if k % 2 == 0 else zoom_alternado})

    def definir_transicoes(self, cortes, trocas_de_assunto):
        """cortes: todos os cortes com flash; trocas_de_assunto: os que tambem levam whoosh e entrada forte."""
        grandes = {round(x, 2) for x in trocas_de_assunto}
        self.transitions = [{"at": round(t, 3), "big": round(t, 2) in grandes} for t in sorted({round(x, 3) for x in cortes})]

    def modal(self, tipo, inicio, dur=4.5, pos=None, texto=None):
        """Modal do canal. tipo: inscrever, curtir ou twitch. pos: top-center, top-left, top-right, bottom-left, bottom-right."""
        if tipo not in TIPOS_MODAL:
            raise ValueError(f"tipo de modal desconhecido: {tipo}")
        fim = min(inicio + dur, self.DUR)
        item = {"type": "cta", "tipo": tipo, "t0": round(inicio, 3), "t1": round(fim, 3),
                "clique": round(inicio + min(CLIQUE_MODAL, dur * 0.4), 3)}
        if pos:
            item["pos"] = pos
        if texto:
            item["texto"] = texto
        self.modais.append(item)

    # ------------------------------------------------------------ saida
    def _canal(self, arquivo=KIT / "src" / "canal.json", assets=KIT / "assets" / "canal"):
        """Nome, Twitch e avatar do perfil do video ("perfil" no projeto.json; sem ele, o perfil_padrao), para os modais."""
        canal = json.loads(Path(arquivo).read_text(encoding="utf-8"))
        nome_perfil = getattr(self.p, "config", {}).get("perfil") or canal["perfil_padrao"]
        if nome_perfil not in canal["perfis"]:
            raise ValueError(f"perfil desconhecido no projeto.json: {nome_perfil} (use {', '.join(canal['perfis'])})")
        perfil = canal["perfis"][nome_perfil]
        dados = {"perfil": nome_perfil, "nome": perfil.get("nome", ""), "twitch": perfil.get("twitch", "")}
        tipos = {m["tipo"] for m in self.modais}
        if tipos & {"inscrever", "curtir"} and not dados["nome"]:
            print(f"ATENCAO: preencha o nome do perfil {nome_perfil} em src/canal.json")
        if "twitch" in tipos and not dados["twitch"]:
            # sem Twitch no perfil, o modal mandaria para um canal que nao existe
            raise ValueError(f"o perfil {nome_perfil} nao tem Twitch em src/canal.json; preencha ou tire o modal twitch")
        # o modal le o avatar da pasta public do video: copia o do perfil (assets/canal/) para la
        avatar = Path(assets) / perfil.get("avatar", "")
        if perfil.get("avatar") and avatar.is_file():
            dados["avatar"] = perfil["avatar"]
            if tipos:
                shutil.copy2(avatar, self.p.public / perfil["avatar"])
        elif tipos:
            print(f"ATENCAO: avatar do perfil {nome_perfil} nao encontrado em assets/canal/")
        return dados

    def _validar(self):
        for s in self.shots:
            assert s["dur"] > 0.3, f"cena {s['name']} curta demais"
            total = self._fonte(s["src"])["duration"]
            assert s["from"] + s["dur"] <= total + 0.02, f"cena {s['name']} passa do fim de {s['src']}"
        faixas = sorted([(c["at"], c["at"] + c["dur"]) for c in self.cams] + [(s["at"], s["at"] + s["dur"]) for s in self.shots])
        assert faixas and faixas[0][0] < 0.02, "a primeira cena precisa comecar em 0"
        assert abs(faixas[-1][1] - self.DUR) < 0.02, "a ultima cena precisa terminar no fim do video"
        for (_, a1), (b0, _) in zip(faixas, faixas[1:]):
            assert abs(a1 - b0) < 0.02, f"buraco ou sobreposicao entre {a1:.2f}s e {b0:.2f}s"
        for c in self.cams:
            total = sondar(self.p.public / c["src"])["duration"]
            assert c["from"] >= 0 and c["from"] + c["dur"] <= total + 0.05, f"camera em {c['at']}s passa do fim de {c['src']}"

    def salvar(self):
        self._validar()
        canal = self._canal()
        sfx = [{"src": "whoosh.wav", "at": round(t["at"] - 0.18, 2), "volume": 0.55} for t in self.transitions if t["big"]]
        sfx += [{"src": "pop.wav", "at": c["t0"], "volume": 0.6} for c in self.callouts]
        sfx += [{"src": "pop.wav", "at": m["t0"], "volume": 0.45} for s in self.shots for m in s["mags"]]
        for m in self.modais:
            sfx += sons_do_modal(m)
        sfx += self.sfx_extra
        edl = {
            "formato": self.p.formato, "duration": self.DUR, "narration": "narration.wav",
            "cams": self.cams, "shots": self.shots, "callouts": self.callouts, "overlays": self.overlays + self.modais,
            "transitions": self.transitions, "sfx": sorted(sfx, key=lambda s: s["at"]), "captions": self.captions,
            "captionLayouts": self.layouts, "canal": canal,
        }
        if self.selo:
            edl["selo"] = self.selo
        if (self.p.public / "music_ducked.wav").exists():
            edl["music"] = "music_ducked.wav"
        destino = self.p.dir / "edl.json"
        destino.write_text(json.dumps(edl, ensure_ascii=False, indent=1), encoding="utf-8")
        shutil.copy2(destino, self.p.public / "edl.json")
        print(f"ok: {self.DUR}s, {len(self.shots)} cenas de tela, {len(self.cams)} de camera, {len(self.captions)} palavras")
        for s in sorted(self.cams + self.shots, key=lambda s: s["at"]):
            print(f"  {s.get('name', s['src']):10s} {s['at']:6.2f} -> {s['at'] + s['dur']:6.2f}  (fonte {s['from']:.2f})")
