# Life is Strange Remastered — Correção das Legendas

Corrige o problema em que o jogo mostra o nome interno da fala em vez da legenda,
normalmente logo depois de uma troca de cenário ou de episódio:

```
Cue_E5_3B_ArtGallery_PhotoLook_Admirer1_050_C_2147461859
```

Funciona em todos os idiomas do jogo. Nada no jogo é alterado — o executável, os
arquivos `.pak` e a pasta `LIS/Content/AltData` continuam intactos.

## Instalação

1. Feche o jogo.
2. Execute `install.bat`, ou copie `Binaries\Win64\XINPUT1_3.dll` para:
   ```
   <PastaDoJogo>\LIS\Binaries\Win64\XINPUT1_3.dll
   ```
3. Abra o jogo normalmente (Steam, Epic, GOG ou `LiS.exe`).

## Desinstalação

Apague `<PastaDoJogo>\LIS\Binaries\Win64\XINPUT1_3.dll`.

## Como conferir se está funcionando

O mod grava o arquivo `XINPUT1_3.log` na mesma pasta, em `LIS\Binaries\Win64\`:

```
[INIT] subtitle fix active - GetLocalizedText hooked at 00007FF7...
[FIX] resolved 'Cue_E2_1A_..._010_C_2147459969' -> 'Cue_E2_1A_..._010'
```

Se o log disser que a versão do jogo não foi reconhecida, o mod não fez nada de
propósito — ele só altera exatamente a versão do jogo para a qual foi feito.

## O que ele faz

O jogo guarda as legendas em tabelas de localização dentro do `pakchunk0`,
indexadas pelo nome da fala. Quando uma fala é criada durante o carregamento de
um sub-nível, a Unreal Engine acrescenta um sufixo `_C_<número>` ao nome do
objeto. Esse nome não corresponde mais a nenhuma chave da tabela, então o jogo
escreve a chave na tela no lugar da legenda.

O mod intercepta a própria busca de legendas do jogo. Quando — e somente quando —
essa busca falha, ele remove o sufixo `_C_<número>` e pergunta de novo ao jogo. O
texto continua vindo das tabelas do próprio jogo, então fica sempre correto e no
idioma que você escolheu.

## Idioma

O jogo escolhe as legendas pelo idioma definido no menu de opções. Se quiser
definir manualmente, edite:

```
%LOCALAPPDATA%\LIS\Saved\Config\WindowsNoEditor\Game.ini
```

```ini
[Internationalization]
Culture=pt-BR
```

Os valores válidos são as pastas de idioma que acompanham o jogo: `de`, `en`,
`es`, `es-419`, `fr`, `it`, `ja`, `pt-BR`, `ru`, `zh-Hans`.

## Licença

MIT.
