# Vídeo curto (Reels, Shorts, TikTok)

Valem para todo vídeo curto, salvo o que a subpasta do tipo mudar. São um ponto de partida: troque pelo seu estilo.

| Item | Padrão |
|---|---|
| Formato | `reels-vertical`: 1080×1920, 30 fps |
| Duração | até 90 s |
| Estrutura | câmera no gancho (até 5 s), tela com narração no corpo, câmera no final com pergunta |
| Ritmo | corte visual a cada 1,2 a 3,8 s, a maioria entre 2 e 3 s |
| Fala | sem silêncios de 180 ms ou mais; respiro de 0,06 s na frase e 0,16 s entre frases |
| Música | em torno de 20 dB abaixo da voz (-35 LUFS) |

**Legendas:** Montserrat 900, maiúsculas, contorno preto de 14 px. Até 3 palavras e 17 caracteres por vez. Palavra falada em amarelo `#FFD400`; palavra-chave falada em verde `#3DDC84`. Posição y=1340, tamanho 92. Com o rosto perto da câmera: y=1455, tamanho 80.

**Câmera na tela:** zoom suave, em geral de 1 a 3 s. Movimento rápido (0,5 s) só para pular até a resposta de uma frase. Numa gravação 2560×1440, z=0,42 mostra a tela inteira na largura, z=1,33 preenche a altura e o limite prático para detalhes é z=2.

**Cortes:** toda cena entra com zoom e desfoque rápidos e flash branco. Nos cortes comuns o efeito é leve. Nas trocas de assunto é forte e leva whoosh (em média, metade dos cortes).

**Destaques:** caixa com brilho sobre o elemento citado, no momento em que é citado. Amarelo neutro, azul informação, verde positivo, vermelho atenção.

**Lupas:** recorte ampliado de um detalhe pequeno, como barras e avisos, que a câmera vertical não consegue centralizar.

**Títulos e etiquetas:** só nos pontos-chave, no topo da tela (y entre 290 e 520). Etiqueta curta, inclinada, com sombra dura.

**Efeitos sonoros:** whoosh 0,18 s antes da troca de assunto (volume 0,55); pop em cada título e lupa (0,45 a 0,7); stamp só em impacto, como o X do terminal.

**Barra de progresso:** 10 px no topo, sempre.

**Área livre no vertical (Reels):** deixe de fora os 250 px de cima e, para textos importantes, tudo abaixo de y=1600, onde ficam o nome do perfil e a legenda. Na direita, a coluna de botões (curtir, comentar, compartilhar) ocupa mais ou menos x > 960 entre y=1100 e 1700: nada importante ali. Modais e cartelas começam em y=260; no vertical, não use modal nas posições de baixo.

**Tema:** fonte dos títulos (`titleFont` em `src/fonts.ts`) e tipo de música mudam por vídeo. Fonte pixel e chiptune combinam com tema retrô ou de games; em outro tema, pergunte ao usuário.
