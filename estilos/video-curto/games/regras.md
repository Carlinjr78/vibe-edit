# Vídeo curto de games (cortes de jogo)

Herda `estilos/video-curto/regras.md`, com estas diferenças.

| Item | Padrão |
|---|---|
| Duração | jogada isolada: 15 a 60 s; corte de live: até 3 min |
| Início | direto no momento forte; contexto só depois, se precisar |
| Pausas | **não remover**: `REMOVER_PAUSAS = False` em `cortes.py`, para manter o som do jogo |
| Som | áudio do jogo e da voz como protagonistas, em -14 LUFS |
| Música | só se o roteiro pedir; o jogo normalmente já preenche |
| Whoosh | pouco: só em trocas de cena reais |

**Momentos:** Claude não ouve o jogo e não sabe o que foi uma boa jogada. O roteiro precisa dizer o momento, com tempo aproximado ("a jogada dos 3:20"). Confira com `quadros.py` antes de cortar.

**Enquadramento:** gameplay preenchendo a altura (z=1,33 numa gravação 2560×1440), centralizado na ação. Se houver facecam, defina no roteiro onde ela entra.

**Legendas:** só nas falas. Não cubra minimapa, mira, placar ou killfeed quando eles forem o assunto.

**Selo do canal (opcional):** uma imagem fixa (ex.: o nome da sua live) pode ficar parada o vídeo todo com `r.selo` no `edicao.py` (a imagem vai em `public/`). Sem animação de entrada ou saída, e fora da área do rosto e das legendas.

## Corte de live

- **Layout:** câmera em cima (1080×662) e jogo embaixo (1080×1258). Recorte a facecam sem os avisos do overlay (metas, inscritos, chat). Quando a cena da live muda, o recorte muda junto.
- **Estrutura:** gancho com a frase que desperta a curiosidade (até 3 s) e depois o clipe em ordem.
- **Cortes:** o clipe fica quase inteiro. Corte só esperas sem fala, com rampa de 30 ms no áudio de cada corte.
