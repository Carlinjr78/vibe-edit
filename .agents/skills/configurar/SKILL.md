---
name: configurar
description: Configuração inicial do vibe-edit num computador novo. Confere e instala as dependências (Node, Python, ffmpeg), cria a .venv, configura o canal (nome, Twitch, avatar), a pasta de mídia e o idioma, e testa se tudo funciona. Use quando o usuário acabou de clonar o repositório, pedir para configurar, instalar ou "deixar pronto pra usar", ou quando src/canal.json ainda tiver "Seu Canal". Setup, install, first run.
---

# Configuração inicial do vibe-edit

Objetivo: deixar o kit pronto para o primeiro vídeo, perguntando ao usuário só o que for dele (nome do canal, avatar, pasta) e resolvendo o resto sozinho.

Rode tudo na raiz do repositório. Fale em português, curto, e diga o que cada passo faz antes de fazer.

## Regras

- **Nunca instale programa no sistema sem perguntar** (winget, brew, apt, instalador). Mostre o comando e espere o "sim". `npm install` e `pip install` dentro do projeto podem ir direto.
- **Nada pessoal no Git.** O avatar fica em `assets/canal/` (fora do Git). O `src/canal.json` está no Git: avise que ele não deve ir num commit ou PR para o repositório original.
- **Não mexa no registro do Windows nem em variável de ambiente permanente sem perguntar.** Mostre o comando e o efeito.
- Se um passo falhar, pare, explique o erro em uma frase e proponha a correção. Não pule para o próximo fingindo que deu certo.

## Passo 1: ver o que já existe

```bash
python scripts/configurar.py checar
```

(Se `python` não existir, tente `python3` ou `py`.) O JSON diz o que está pronto. Mostre ao usuário um resumo em lista: ✅ pronto, ❌ falta. Pule os passos do que já estiver pronto.

## Passo 2: ferramentas do sistema

Precisa de: Node 18+, Python 3.12, ffmpeg e git.

| Sistema | Comando para o que faltar |
|---|---|
| Windows | `winget install OpenJS.NodeJS.LTS`, `winget install Python.Python.3.12`, `winget install --id Gyan.FFmpeg -e`, `winget install Git.Git` |
| macOS | `brew install node python@3.12 ffmpeg git` |
| Ubuntu/Debian | `sudo apt install nodejs npm python3.12 python3.12-venv ffmpeg git` |

Pergunte antes de instalar. No Windows, depois de instalar pelo winget, o terminal precisa ser reaberto para achar o comando novo: avise o usuário.

GPU: se `gpu_nvidia` aparecer, a transcrição usa a placa sozinha. Se não, tudo roda na CPU, só mais devagar. Não precisa fazer nada.

## Passo 3: dependências do projeto

```bash
npm install
python -m venv .venv
```

Depois instale os pacotes Python com o Python da `.venv` (`.venv/Scripts/python.exe` no Windows, `.venv/bin/python` no macOS e no Linux):

```bash
<python da venv> -m pip install -r requirements-dev.txt
```

Isso leva alguns minutos (no Windows baixa as bibliotecas da GPU, perto de 1 GB).

## Passo 4: o canal

Pergunte, numa mensagem só:

1. Nome do canal, como deve aparecer no modal de inscrição.
2. Usuário da Twitch, se tiver (sem Twitch, o modal da Twitch fica desligado).
3. Caminho de uma foto ou logo para o avatar (opcional; sem ele, o modal mostra a primeira letra do nome).

Depois grave:

```bash
<python da venv> scripts/configurar.py canal --nome "Nome" [--twitch usuario] [--avatar caminho/da/foto.jpg]
```

O avatar é recortado no centro e salvo em 400×400 em `assets/canal/avatar.jpg`. Se a pessoa tem mais de um canal, explique que dá para criar outro perfil em `src/canal.json` e escolher em cada vídeo com `"perfil"` no `projeto.json`.

## Passo 5: pasta de mídia

Brutos e renders ficam fora do repositório. Padrão: `C:\video-midia` no Windows e `~/video-midia` no macOS e no Linux.

Pergunte se o padrão serve. Recomende um disco com espaço (um vídeo de 1 min gera alguns GB de arquivos de trabalho) e **fora** de pasta sincronizada (OneDrive, Dropbox, Google Drive).

- Se o padrão servir, só crie a pasta.
- Se quiser outra, mostre o comando para gravar `VIDEO_MIDIA` de forma permanente e rode com o "sim":
  - Windows: `setx VIDEO_MIDIA "D:\video-midia"`
  - macOS/Linux: `echo 'export VIDEO_MIDIA="$HOME/Videos/vibe-edit"' >> ~/.zshrc` (ou `~/.bashrc`)
  Avise que vale para terminais abertos depois disso.

## Passo 6: idioma

A transcrição usa português (`pt`). Se o usuário grava em outra língua, configure `WHISPER_LANGUAGE` (ex.: `en`, `es`) do mesmo jeito que o `VIDEO_MIDIA`.

## Passo 7: Windows, caminhos longos

Se `caminhos_longos_windows` for `false`, explique: "o Remotion falha quando o caminho da pasta é muito longo; isso significa que o render pode quebrar com erro ENOENT se o repositório estiver numa pasta funda". Duas saídas:

- deixar o repositório numa pasta curta (ex.: `C:\vibe-edit`); ou
- ligar os caminhos longos: abrir o PowerShell **como administrador** e rodar o comando abaixo, depois reiniciar. É o usuário quem roda.

```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name LongPathsEnabled -Value 1 -PropertyType DWORD -Force
```

## Passo 8: conferir

```bash
<python da venv> -m pytest -q
npm run typecheck
```

Os dois precisam passar. Se falhar, mostre o erro e resolva antes de encerrar.

Opcional: o modelo do Whisper (~1,6 GB) baixa sozinho na primeira transcrição. Pergunte se o usuário quer baixar agora:

```bash
<python da venv> -c "import sys; sys.path.insert(0, 'scripts'); import fala; fala.Whisper()"
```

## Passo 9: encerrar

Rode `checar` de novo e mostre o resumo final. Termine com o próximo passo, em uma frase:

> Pronto. Para o primeiro vídeo, peça: "cria um vídeo novo chamado AAAA-MM-nome, estilo video-curto". O exemplo completo está em `videos/_exemplo/`.
