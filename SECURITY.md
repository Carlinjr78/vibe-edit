# Segurança

## Como reportar uma falha

**Não abra issue pública.** Use o botão **Report a vulnerability** na aba [Security](../../security/advisories/new) deste repositório. Só o mantenedor vê o relato.

Diga o que acontece, como reproduzir e qual versão (commit) você usou. A resposta vem em até 7 dias.

## O que levar em conta

- O vibe-edit roda **no seu computador**: os scripts chamam `ffmpeg`, `node` e Python com os arquivos que você indicar, e o agente (Claude Code) executa comandos na sua máquina. Use só roteiros, projetos e vídeos de fontes em que você confia.
- `videos/<projeto>/cortes.py` e `edicao.py` são **código Python executado** pelos scripts. Nunca rode um projeto de vídeo que alguém te mandou sem ler esses arquivos antes.
- O kit não precisa de nenhuma chave de API. Se você colocar alguma no `.env`, ele fica fora do Git; confira com `git status` antes de cada commit.
- Nenhum vídeo é enviado para a internet pelo kit. O único download automático é o modelo do Whisper, na primeira transcrição.
