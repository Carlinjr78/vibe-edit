# Vídeo longo (YouTube)

Ponto de partida: ajuste com o que os seus primeiros vídeos ensinarem.

Há dois caminhos:

- **Vídeo longo editado** (tutorial, review): mesmo fluxo do vídeo curto, com o formato `youtube-horizontal`.
- **Gravação longa só com modais** (gameplay, live, aula): `scripts/longo_modais.py`, sem legenda nem corte. Veja a seção no fim deste arquivo.

| Item | Padrão |
|---|---|
| Formato | `youtube-horizontal`: 1920×1080, 60 fps |
| Ritmo | sem silêncios longos; corte visual a cada 4 a 10 s |
| Música | em torno de 20 dB abaixo da voz (-35 LUFS), só nos trechos que pedirem |
| Efeitos | só nos pontos-chave; não precisa de efeito em toda frase |
| Render | medido a 30 fps: 10 minutos de vídeo levavam uns 45 minutos; a 60 fps espere perto do dobro |

**Layout:** títulos e efeitos foram desenhados para o vertical e encolhem no centro da tela. Revise nas prévias e ajuste no primeiro vídeo.

## Modais de inscrição e like

Regra geral para todo vídeo longo. Marcações no roteiro têm prioridade. Sem marcação, Claude escolhe os momentos por estas regras e os mostra no mapa antes de renderizar.

| Modal | Quando | Quantas vezes |
|---|---|---|
| `r.modal("inscrever", inicio)` | depois da primeira entrega de valor, entre 20% e 35% do vídeo, nunca antes de 1:00 | 1 vez; 2 em vídeos acima de 20 min (a segunda perto de 75%) |
| `r.modal("curtir", inicio)` | logo depois de um momento forte, entre 55% e 70% do vídeo | 1 vez |

- Duração de 4 a 5 s, no canto superior direito (padrão do formato).
- Só em momento oportuno: fim de ideia, transição ou resultado que acabou de aparecer.
- Nunca durante uma demonstração, em cima do rosto ou de legenda, ou nos últimos 20 s do vídeo, onde entram os elementos finais do YouTube.
- Nunca dois modais com menos de 2 minutos de diferença.

## Gravação longa só com modais (`longo_modais.py`)

Para gravações de 10 min a várias horas que não precisam de edição, só dos lembretes de inscrição.

- Corta só as pontas: o detector de voz olha os 2 primeiros e os 2 últimos minutos. Começa 1 s antes da primeira fala e termina 1,5 s depois da última.
- Plano padrão, com horários fixos: inscrever em 1:30, curtir no meio, inscrever em 2/3 (a partir de 20 min), Twitch 3 min antes do fim (só se o perfil tiver Twitch) e mais um inscrever a cada 10 min acima de 35 min.
- `--so-plano` mostra os horários e uma folha com um quadro de cada momento, sem renderizar. Confira antes.
- `--modais "inscrever@1:30,curtir@15:00"` troca os horários; `--sem-corte`, `--inicio` e `--fim` controlam as pontas.
- Cada tipo de modal é renderizado uma vez (fundo transparente) e o ffmpeg cola por cima. Com placa NVIDIA usa NVENC (10 min de 1080p60 em cerca de 3,5 min); sem ela, cai para o x264, mais lento.
- A gravação original nunca é alterada.
