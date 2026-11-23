# vibe-edit

Kit para editar vídeos sempre no mesmo padrão com Claude Code e Remotion. O usuário escreve o roteiro e grava; você corta, legenda, põe os efeitos e renderiza. Os efeitos ficam em `src/components/` e são reaproveitados: antes de escrever um efeito novo, veja se um existente resolve com outros parâmetros.

`videos/_exemplo/` é o exemplo completo de referência (os brutos dele não vêm no repositório). Em dúvida sobre como fazer algo, leia o `edicao.py` dele.

## Onde fica cada coisa

| Caminho | Conteúdo |
|---|---|
| `estilos/<tipo>/regras.md` | Regras de cada tipo de vídeo. Subpastas herdam da pasta acima |
| `referencias/` | Vídeos de que o usuário gosta, com um `nota.md` cada, na mesma organização de `estilos/` |
| `videos/<nome>/` | Só texto: `roteiro.md`, `projeto.json`, `cortes.py`, `edicao.py`, `edl.json`, `ficha.md` |
| `<VIDEO_MIDIA>/<nome>/` | `brutos/`, `public/`, `build/`, `out/`. Fora do Git. Padrão: `C:\video-midia` no Windows, `~/video-midia` no macOS e no Linux |
| `src/canal.json` | Perfis do canal usados nos modais: nome, avatar e Twitch (opcional). Cada vídeo escolhe o perfil em `"perfil"` no `projeto.json`; sem ele, vale o `perfil_padrao` |
| `assets/livre/` | O que pode ir para os vídeos: `sfx/`, `musicas/` e `packs/` |
| `assets/com-direitos/` | Material com direitos autorais. Fora do Git e não entra em vídeo publicado sem autorização do dono |
| `assets/canal/` | Avatar do canal. Fora do Git |

`roteiro.md` é a direção escrita pelo usuário. `edicao.py` é a edição que você escreve a partir dela.

## Primeiro uso

Se `src/canal.json` ainda tiver `"Seu Canal"`, pergunte ao usuário o nome do canal, o usuário da Twitch (se tiver) e peça o avatar para `assets/canal/`. Sem isso os modais saem genéricos.

## Como decidir

Em conflito, vale nesta ordem: `roteiro.md`, regras do tipo mais específico, regras do tipo acima, este arquivo. Trechos marcados com `[LIVRE]` e tudo o que o roteiro não definir são liberdade criativa, dentro do estilo.

O roteiro é preso às frases, e a gravação nunca sai igual ao texto. Case cada direção com o que foi realmente falado, usando a transcrição.

Marcações do roteiro: `[MODAL-INSCREVER]`, `[MODAL-CURTIR]`, `[MODAL-TWITCH]`, `[TITULO: texto]`, `[ETIQUETA: texto]`, `[EFEITO: descrição]`, `[VOTAÇÃO] A / B`, `[MÚSICA: clima]`, `[LIVRE]`.

Modais: `r.modal(tipo, inicio)` no `edicao.py`, com `tipo` = `inscrever`, `curtir` ou `twitch`. O modal usa o nome, o avatar e a Twitch do perfil do vídeo e toca um pop ao entrar e outro no clique (`sons_do_modal` no `edicao_lib.py`). `[MODAL-TWITCH]` só funciona se o perfil tiver Twitch.

## Fluxo de um vídeo novo

Rode tudo a partir da raiz do repositório, com o Python da `.venv` (`.venv/Scripts/python.exe` no Windows, `.venv/bin/python` no macOS e no Linux). Em caso de ambiente novo, siga a instalação do `README.md`.

1. `scripts/novo_video.py AAAA-MM-nome <estilo>` cria a pasta de texto e a de mídia. Os brutos vão em `<VIDEO_MIDIA>/<nome>/brutos/`.
2. Salve o roteiro do usuário em `videos/<v>/roteiro.md`. Leia as regras do estilo, as acima dele e as notas de `referencias/` citadas ou do mesmo tipo.
3. Preencha `projeto.json` com os brutos e os nomes próprios difíceis em `nomes_para_o_whisper`.
4. `scripts/preparar.py videos/<v>` gera as versões em `public/`.
5. `scripts/transcrever.py videos/<v>` lista os blocos de fala e avisa sobre regravações. Leia a lista inteira antes de escolher os takes.
6. Se a câmera e a voz foram gravadas em aparelhos diferentes: `scripts/sincronizar.py videos/<v> cam1 voz1`.
7. Escreva `cortes.py` e rode `scripts/cortar.py videos/<v>`. Resolva todo aviso de corte suspeito com `scripts/pausas.py`.
8. `scripts/quadros.py videos/<v> folhas tela` para assistir à gravação quadro a quadro; `grade` e `recorte` dão as coordenadas exatas.
9. **Mostre o mapa ao usuário antes de renderizar:** uma linha por frase, com o trecho de imagem, o efeito e os modais. Espere a aprovação, salvo se o usuário dispensar.
10. `scripts/mixar_musica.py videos/<v>`, depois escreva `edicao.py` e rode `scripts/montar_edl.py videos/<v>`.
11. `scripts/render.py videos/<v> --previa 60,205,...` com quadros de cada cena, títulos, efeitos e modais. Olhe as folhas em `build/previa/` e corrija antes de seguir.
12. `scripts/render.py videos/<v>` gera `out/<v>_vN.mp4`. Se só o áudio mudou, use `--so-audio` (não renderiza a imagem de novo).

Cada render vira uma versão nova; nunca sobrescreva a anterior. O usuário é quem aprova o resultado final.

## Gravação longa só com modais

Para gameplay, live ou aula que não precisa de edição: `scripts/longo_modais.py <gravacao>` corta só as pontas (detector de voz) e cola os modais em horários fixos. Grava em `<VIDEO_MIDIA>/longo/prontos/`. Rode primeiro com `--so-plano` e mostre a folha ao usuário. Regras e opções em `estilos/video-longo/regras.md`. A gravação original nunca é alterada.

## Encerrar um vídeo

Só depois que o usuário avisar que o vídeo foi postado e mandar o link.

1. Preencha `ficha.md` com o que funcionou e o que o usuário corrigiu.
2. Mostre ao usuário o que mudaria em `estilos/` e aplique o que ele aprovar. **Reescreva a regra, não acumule anotações:** a ficha é o histórico; o estilo é só o que vale hoje.
3. `scripts/encerrar.py videos/<v> --link URL` mostra o que será apagado e o tamanho. Mostre isso ao usuário e espere a confirmação.
4. Com a confirmação, repita com `--confirmar`. O final, os brutos e os arquivos de trabalho são apagados, sem volta. Fica o texto, o link e a `folha.jpg`.

## Regras gerais

- **Nada em cima do rosto.** Legendas, títulos, modais e efeitos ficam fora da área do rosto. Confira nas prévias, principalmente com a câmera perto.
- **Música baixa.** Em torno de 20 dB abaixo da voz (-35 LUFS contra -14 LUFS). Com 15 dB de diferença ela já fica alta.
- **A imagem precisa acompanhar a fala.** Cada frase mostra o trecho da gravação que corresponde ao que está sendo dito.
- **Nenhuma palavra cortada.** É a reclamação mais comum de quem assiste.

Áudio final em todos os tipos: voz em -14 LUFS, limitador em -1 dBFS, H.264 CRF 18, AAC 320k.

## Armadilhas conhecidas

- **Regravações.** É comum regravar frases no meio do áudio. Sem cuidado, o corte junta as duas versões. Confie nos avisos de `transcrever.py` e use sempre a versão completa. Áudio pode ter takes inteiros repetidos, palmas de sincronia e comentários ("tá gravando?").
- **Frase abandonada.** Um começo curto como "Esse é..." antes da frase certa passa despercebido. Blocos que terminam em "..." quase nunca devem entrar no corte; `cortar.py` avisa.
- **Whisper num arquivo inteiro engana.** Ele junta takes e estica palavras por cima das pausas. Para decidir cortes, use os blocos de `transcrever.py`.
- **Fim de palavra.** O tempo do Whisper termina antes do som real, e terminações em "s" têm pouco volume. Meça com `pausas.py`.
- **Volume não detecta pausa** quando há som de fundo. Por isso o kit usa Silero VAD.
- **Nomes próprios.** Coloque em `nomes_para_o_whisper` e corrija o resto com `correcoes` no `edicao.py`.
- **Alucinação no fim.** O Whisper inventa frases no silêncio final. `preparar_legendas` já descarta.
- **Âncoras** usam palavra exata: "com" não pode casar com "como".
- **Coordenadas mudam com o tempo.** Avisos e painéis mudam de lugar conforme a tela. Confira a lupa no instante exato com `quadros.py recorte`.
- **Direitos autorais.** Só música e efeitos com licença livre; a trilha de `musica_chiptune.py` e os efeitos de `sfx_sinteticos.py` são originais.

## Limites

- Você vê quadros, mas **não ouve**. Volume e cortes dá para medir; se a música soa bem, só o usuário sabe. Sempre diga isso ao entregar.
- O DaVinci Resolve gratuito bloqueia scripts desde a versão 21.1. Não dá para controlá-lo; use o Remotion.
- O Remotion falha em caminhos de pasta muito longos no Windows (erro ENOENT). Ative os caminhos longos do Windows ou use uma pasta curta.
- Rode o render completo sem outras tarefas pesadas: Whisper e ffmpeg rodando junto já derrubaram um render que passou ao repetir sozinho.
- O Whisper usa a GPU NVIDIA quando há cuBLAS e cuDNN (`requirements.txt`); `fala.py` registra as DLLs no Windows. Sem GPU, cai para a CPU sozinho. O idioma da fala é `pt`; troque com a variável `WHISPER_LANGUAGE`.
