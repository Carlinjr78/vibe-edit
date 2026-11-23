# Como contribuir

Obrigado por querer ajudar! Correções, efeitos novos, estilos e testes em outros sistemas são bem-vindos.

## Antes de abrir um PR

1. **Abra uma issue primeiro** para mudanças grandes (efeito novo, script novo, mudança no fluxo). Correção pequena pode ir direto no PR.
2. Faça um fork, crie uma branch a partir da `main` e mande o PR para a `main`.
3. Rode os testes e o typecheck. A checagem automática do GitHub roda os dois em todo PR, e o PR só entra com ela verde.

```bash
.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
.venv/Scripts/python.exe -m pytest
npm run typecheck
```

(No macOS e no Linux, troque `.venv/Scripts/python.exe` por `.venv/bin/python`.)

## Regras do repositório

**1. Nada pessoal e nada de mídia no Git.** O repositório guarda só texto e código. Nunca faça commit de:

- vídeo, áudio ou imagem dos seus projetos (brutos, renders, prints, fotos);
- `.env`, chaves de API, tokens ou senhas;
- seus projetos em `videos/` (só `videos/_modelo/` e `videos/_exemplo/` são do repositório);
- caminhos do seu computador (`C:\Users\seu-nome\...`), nomes ou dados de outras pessoas.

O `.gitignore` já barra quase tudo isso, e a checagem automática falha se algum arquivo assim entrar.

**2. Só material com direito de uso.** Efeito sonoro, música, fonte ou imagem só entra se for original (gerado por código, como `scripts/sfx_sinteticos.py` e `scripts/musica_chiptune.py`) ou tiver licença que permita redistribuir. Diga no PR de onde veio e qual é a licença. Logo, fonte ou arte de marca (jogos, empresas, plataformas) não entra, nem "inspirada".

**3. Reaproveite antes de criar.** Antes de escrever um efeito novo em `src/components/`, veja se um existente resolve com outros parâmetros. Efeito novo precisa funcionar no vertical (1080×1920) e no horizontal (1920×1080).

**4. Teste o que mudar.** Mudança em `scripts/` vem com teste em `tests/`. Os testes não podem depender de vídeo real, GPU, internet ou chave de API: use dados falsos, como em `tests/test_exemplo.py`.

**5. Regras de estilo são do usuário.** Os arquivos de `estilos/` são um ponto de partida. Mude quando for uma melhoria para todo mundo (ex.: área segura do Reels), não por gosto pessoal.

**6. Português.** Código, comentários, mensagens e documentação ficam em português, como o resto do projeto. Nos scripts Python, sem acento em comentários e mensagens (evita erro de encoding no Windows).

**7. Commits pequenos e com mensagem clara.** Formato sugerido: `tipo(area): o que mudou`, por exemplo `fix(cortar): nao corta o fim de palavra com s`.

## O que é bem-vindo

- Testes e correções no macOS e no Linux (até agora só foi testado no Windows).
- Novos efeitos genéricos e estilos para outros tipos de vídeo.
- Melhorias na documentação e no exemplo.

## O que provavelmente não entra

- Integração com serviço pago obrigatório (o kit precisa funcionar sem gastar nada além do Claude Code).
- Mudança que envie vídeo do usuário para a internet.
- Código que só funciona para um canal específico.

## Dúvidas e bugs

Use as [issues](../../issues). Para falha de segurança, veja o [SECURITY.md](SECURITY.md) e **não** abra issue pública.

Ao participar, você concorda com o [código de conduta](CODE_OF_CONDUCT.md).
