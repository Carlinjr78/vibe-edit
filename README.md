# vibe-edit

**Você escreve o roteiro e grava. A IA corta, legenda, coloca os efeitos e renderiza.**

vibe-edit é um kit de edição de vídeo feito para ser usado com o [Claude Code](https://claude.com/claude-code). Em vez de passar horas na linha do tempo de um editor, você conversa com o agente: ele transcreve a gravação, escolhe os melhores takes, corta as pausas sem comer palavra, sincroniza a câmera com o áudio, coloca legenda animada, zoom na tela, destaques, títulos, modais de "inscreva-se" e renderiza o vídeo final. Tudo sempre no **mesmo padrão**, porque o seu estilo fica escrito em arquivos que o agente segue.

Feito para Reels, Shorts e TikTok (vertical), e também para vídeos longos do YouTube.

> Tudo roda no seu computador. A transcrição é local (Whisper), o vídeo é montado em código (Remotion) e o corte é feito com ffmpeg. Nenhum vídeo seu sobe para lugar nenhum.

---

## O que ele faz

- **Corte sem pausa e sem palavra comida.** Detecta a voz com Silero VAD (não pelo volume, então funciona com som de fundo), remove silêncios e mede o fim real de cada palavra.
- **Acha suas regravações.** Se você repetiu uma frase porque errou, ele avisa e usa a versão completa.
- **Sincroniza câmera e microfone** gravados em aparelhos diferentes (celular + microfone, por exemplo).
- **Legenda animada palavra por palavra**, com a palavra falada em destaque e as palavras-chave em outra cor, fora da área do rosto.
- **Gravação de tela com zoom suave**, destaques coloridos sobre o que você está citando e lupas para detalhes pequenos.
- **Títulos, etiquetas, flash nas transições, barra de progresso** e efeitos sonoros (whoosh, pop, stamp) nos lugares certos.
- **Modais de inscrever, curtir e Twitch** com o nome e o avatar do seu canal, com um cursor que clica no botão.
- **Votação no final** ("qual você prefere? A ou B") para puxar comentário.
- **Trilha original** em chiptune gerada por código, sem risco de direitos autorais, ou a sua música com licença livre, sempre 20 dB abaixo da voz e abaixando quando você fala.
- **Prévias antes do render**: folhas com quadros de cada cena para conferir antes de gastar tempo renderizando.
- **Render versionado**: cada versão vira um arquivo novo (`_v1`, `_v2`...). Nada é sobrescrito.
- **Vídeo longo só com modais**: para gameplay, live ou aula, corta só o começo e o fim e cola os modais de inscrição em horários fixos, sem reeditar horas de gravação.

## Como funciona

```
 você                              o agente (Claude Code)
 ───                               ──────────────────────
 roteiro.md  ───────────────────▶  lê as regras do estilo
 brutos (câmera, tela, voz)  ───▶  transcreve e acha os takes bons
                                   corta (cortes.py)
                                   ◀── mostra o MAPA: cada frase, a imagem, o efeito
 aprova o mapa  ────────────────▶  escreve a edição (edicao.py)
                                   gera prévias em imagem e corrige
                                   renderiza out/video_v1.mp4
 aprova ou pede ajuste  ────────▶  v2, v3...
 posta e manda o link  ─────────▶  guarda o que aprendeu e atualiza o estilo
```

A ideia central: **o seu estilo é texto**. As regras de cada tipo de vídeo ficam em `estilos/` (tamanho da legenda, ritmo dos cortes, onde nunca pôr texto, volume da música). Quando você corrige algo num vídeo, a correção vira regra e vale para os próximos. Com o tempo, o agente edita do seu jeito.

---

## O que você precisa

| | |
|---|---|
| **Claude Code** | Com uma conta que dê acesso a ele (plano pago da Anthropic ou chave de API) |
| **Node.js** | 18 ou mais novo |
| **Python** | 3.12 |
| **ffmpeg** | No PATH |
| **Placa de vídeo** | Opcional. Com NVIDIA, a transcrição e o vídeo longo ficam bem mais rápidos; sem ela, tudo roda na CPU |

Feito e usado no **Windows**. Deve funcionar no macOS e no Linux, mas ainda não foi testado lá: se testar, conte como foi numa issue.

## Instalação

```bash
git clone https://github.com/<seu-usuario>/vibe-edit.git
cd vibe-edit
npm install
python -m venv .venv
```

**Windows:**

```bash
.venv/Scripts/python.exe -m pip install -r requirements.txt
winget install --id Gyan.FFmpeg -e
```

**macOS / Linux:**

```bash
.venv/bin/python -m pip install -r requirements.txt
brew install ffmpeg        # macOS
sudo apt install ffmpeg    # Ubuntu/Debian
```

Na primeira transcrição, o Whisper baixa o modelo (`large-v3-turbo`, cerca de 1,6 GB).

### Onde ficam os vídeos

O repositório guarda **só texto** (roteiros, cortes, edições). Brutos e renders ficam numa pasta de mídia fora dele:

- Windows: `C:\video-midia\`
- macOS / Linux: `~/video-midia/`

Para usar outra pasta, defina a variável de ambiente `VIDEO_MIDIA`. Evite pastas sincronizadas (OneDrive, Dropbox, Google Drive): os arquivos de trabalho são grandes e mudam o tempo todo.

### Seu canal

Edite `src/canal.json` com o nome do canal e, se tiver, o usuário da Twitch. Coloque o avatar (quadrado, 400×400) em `assets/canal/avatar.jpg`. Tem mais de um canal? Crie outro perfil no mesmo arquivo e escolha em cada vídeo.

```json
{
  "perfil_padrao": "principal",
  "perfis": {
    "principal": { "nome": "Meu Canal", "avatar": "avatar.jpg", "twitch": "meucanal" }
  }
}
```

Se você esquecer, o agente pergunta no primeiro vídeo.

---

## Seu primeiro vídeo

1. **Abra o Claude Code na pasta** e peça: *"cria um vídeo novo chamado 2026-12-meu-video, estilo video-curto"*.
2. **Grave e coloque os brutos** na pasta que ele indicar (`<pasta de mídia>/2026-12-meu-video/brutos/`). Nomes como `01-gancho-cam.mov`, `02-tela.mp4`, `03-narracao.m4a` ajudam.
3. **Mande o roteiro.** Pode colar no chat. O modelo está em [`videos/_modelo/roteiro.md`](videos/_modelo/roteiro.md):

   ```markdown
   ## Gancho
   FALA: "Três atalhos do VS Code que quase ninguém conhece."
   IMAGEM: câmera
   DIREÇÃO: título "VS CODE" quando eu falar o nome

   ## Atalho 1
   FALA: "Alt e clique cria vários cursores."
   IMAGEM: tela, eu clicando em três linhas
   DIREÇÃO: zoom nas linhas; destaque amarelo
   [MODAL-INSCREVER] logo depois dessa frase
   ```

4. **Aprove o mapa.** Antes de renderizar, ele mostra uma linha por frase: que imagem entra, que efeito, onde vão os modais.
5. **Confira o vídeo** em `out/` e peça ajustes ("a legenda tá cobrindo meu rosto no final", "música mais baixa"). Cada ajuste vira uma versão nova.
6. **Depois de postar**, mande o link e peça para encerrar. Ele anota o que funcionou, propõe mudanças no estilo e apaga os arquivos pesados (só com a sua confirmação).

Um vídeo completo, do roteiro à edição, está em [`videos/_exemplo/`](videos/_exemplo/). Os brutos dele não vêm no repositório: serve para ver como cada arquivo é escrito.

### Marcações do roteiro

| Marcação | O que faz |
|---|---|
| `[TITULO: texto]` | Título grande no topo |
| `[ETIQUETA: texto]` | Etiqueta colorida, inclinada |
| `[EFEITO: descrição]` | Descreva o efeito como faria para um editor; o agente monta com os componentes do kit |
| `[MODAL-INSCREVER]` `[MODAL-CURTIR]` `[MODAL-TWITCH]` | Modal do canal com clique animado |
| `[VOTAÇÃO] A / B` | Enquete no final para puxar comentário |
| `[MÚSICA: clima]` | Pede uma trilha com esse clima |
| `[LIVRE]` | Liberdade criativa nesse trecho |

### Vídeo longo só com modais

Para uma gameplay de 3 horas que você não quer editar, só colocar os lembretes de inscrição:

```bash
.venv/Scripts/python.exe scripts/longo_modais.py minha-live.mp4 --so-plano
```

Ele corta o silêncio do começo e do fim, mostra os horários dos modais e uma folha com um quadro de cada momento. Sem `--so-plano`, gera o vídeo pronto. A gravação original nunca é alterada. Detalhes em [`estilos/video-longo/regras.md`](estilos/video-longo/regras.md).

---

## Estrutura

| Pasta | O que tem |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | O manual que o agente segue: fluxo, regras e armadilhas conhecidas |
| [`estilos/`](estilos/) | Regras de cada tipo de vídeo (`video-curto`, `video-curto/games`, `video-longo`). Subpastas herdam da pasta acima |
| [`referencias/`](referencias/) | Vídeos de outros criadores de que você gosta, com uma nota do que copiar |
| [`videos/`](videos/) | Um projeto por vídeo, só com texto. `_modelo/` é o ponto de partida e `_exemplo/` é a referência |
| [`src/components/`](src/components/) | Os efeitos, em React com Remotion |
| [`scripts/`](scripts/) | Preparar, transcrever, sincronizar, cortar, mixar a música, renderizar e encerrar |
| [`assets/livre/`](assets/livre/) | Efeitos sonoros, músicas e packs com licença livre |
| [`assets/com-direitos/`](assets/com-direitos/) | Material com direitos autorais: fica fora do Git e fora dos vídeos |
| [`assets/canal/`](assets/canal/) | Avatar do seu canal (fora do Git) |

Seus vídeos em `videos/` ficam fora do Git por padrão (veja o `.gitignore`), para você não publicar sem querer um roteiro ou um caminho do seu computador. Quer versionar? Tire as linhas de `videos/` do `.gitignore` no seu fork privado.

### Efeitos prontos

| Componente | Efeito |
|---|---|
| `Captions` | Legenda palavra por palavra, até 3 palavras por vez |
| `ScreenShot` | Gravação de tela com zoom em quadros-chave, destaques e lupas |
| `CamShot` | Você falando para a câmera, com punch-in alternado a cada corte |
| `Callout` | Título com partes coloridas ou etiqueta |
| `CtaModal` | Modal de inscrever, curtir ou Twitch com cursor clicando |
| `VoteOverlay` | Enquete final com duas opções |
| `TerminalOverlay` | Terminal digitando que leva um X vermelho |
| `WindowsOverlay` | Várias janelas que se juntam e somem |
| `Flash` / `ProgressBar` | Flash nas transições e barra de progresso no topo |

Quer outro? Peça ao agente. Antes de escrever um efeito novo, ele tenta resolver com os que já existem.

---

## Limites (com franqueza)

- **O agente vê, mas não ouve.** Ele mede volume e cortes, mas se a música combina, só você sabe. Sempre escute antes de postar.
- **Não é um editor visual.** Você não arrasta clipes: você conversa e aprova. Para ajuste fino de um quadro, descreva o que quer.
- **Render leva tempo.** Um Reel de 60 s sai em poucos minutos; um vídeo longo editado leva uns 45 min a cada 10 min de vídeo a 30 fps, e perto do dobro a 60 fps. O comando de vídeo longo só com modais é rápido (com NVIDIA, 10 min de 1080p60 em cerca de 3,5 min).
- **Português por padrão.** A transcrição usa `pt`. Para outra língua, defina `WHISPER_LANGUAGE` (ex.: `en`). As regras e o `CLAUDE.md` estão em português.
- **Windows:** o Remotion falha em caminhos muito longos. Use uma pasta curta para o repositório ou ative os caminhos longos do Windows.

## Testes

```bash
.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
.venv/Scripts/python.exe -m pytest
npm run typecheck
```

## Licença

Código sob a [licença MIT](LICENSE). Os efeitos sonoros de `assets/livre/sfx/` e a trilha chiptune são gerados por código e podem ir em qualquer vídeo.

**Atenção ao Remotion:** o vídeo é montado com o [Remotion](https://www.remotion.dev), que tem licença própria. Ele é gratuito para pessoas físicas, organizações sem fins lucrativos e empresas com até 3 funcionários; empresas maiores precisam de uma [licença de empresa](https://www.remotion.dev/license). Confira se você se encaixa antes de usar comercialmente.

vibe-edit não é afiliado à Anthropic nem ao Remotion.
