# Life is Strange Remastered — Mod de Correção de Legendas v2.0

Corrige o bug de legendas de *Life is Strange Remastered* no PC, em que as
legendas quebram após uma troca de cenário ou episódio e, no lugar do texto,
aparece o identificador bruto do áudio (o "nome do arquivo", ex.:
`Cue_E5_7Z_..._C_2147222737`).

**Funciona em todos os idiomas do jogo — você nunca mais precisa trocar o
idioma no menu para as legendas voltarem a funcionar.**

---

## Conteúdo do pacote

| Arquivo            | Finalidade                                       |
|--------------------|--------------------------------------------------|
| `XINPUT1_3.dll`    | O mod em si (hooks nativos no motor, já compilado) |
| `install.bat`      | Instalador em um clique                          |
| `uninstall.bat`    | Remove o mod                                     |
| `README_EN.md`     | This guide (English)                             |
| `README_PT-BR.md`  | Guia de instalação (Português)                   |
| `LICENSE`          | Licença MIT                                      |

**Não é necessário compilar nada.** O DLL já está compilado.

---

## Instalação

### Opção A — Automática (recomendado)

1. Extraia esta pasta em qualquer lugar.
2. Execute `install.bat`.
3. Se o jogo não estiver em `C:\Games\Life is Strange Remastered`, digite a
   pasta dele quando perguntado.
4. Abra o jogo normalmente (Steam, Epic ou `LiS.exe`).

### Opção B — Manual

1. Localize a pasta do jogo (ex.: `C:\Games\Life is Strange Remastered`).
2. Copie o arquivo `XINPUT1_3.dll` para:
   ```
   <PastaDoJogo>\LIS\Binaries\Win64\XINPUT1_3.dll
   ```
   (substitua se pedir.)
3. Se já existir um `XINPUT1_3.dll` na raiz do jogo
   (`<PastaDoJogo>\XINPUT1_3.dll`), substitua também pelo mesmo arquivo.

## Desinstalação

Execute `uninstall.bat` (ou apague manualmente as cópias de `XINPUT1_3.dll` que
você adicionou). O jogo volta ao comportamento original. Nenhum outro arquivo é
alterado.

---

## O que NÃO é necessário

- Nenhum arquivo `.cue` precisa ser substituído em `LIS\Content\AltData`.
- Nenhuma edição de `.ini`.
- O executável do jogo nunca é modificado.

Toda a correção está contida no único arquivo `XINPUT1_3.dll`.

## Como verificar se está funcionando

Abra o jogo e depois abra o log criado ao lado do DLL:

```
<PastaDoJogo>\LIS\Binaries\Win64\LiS_SubtitleFix.log
```

Deve conter linhas como:
```
[LiS_SubMod] DllMain ATTACH
[DEBUG] GetSubtitleText hook created and enabled at ...
[DEBUG] FindAltDataSetByLayerName hook created and enabled at ...
[INIT] SubtitleMap loaded: ... entries
```

Qualquer cue que ainda falhar aparece como `[HOOK] NO MATCH ...`.

## Como funciona (resumo)

1. **Interceptador de `GetSubtitleText`** — cada cue de legenda é resolvido
   contra um banco embutido de 10.475 falas (~64.000 aliases) cobrindo os 5
   episódios. O nome do cue é normalizado (sufixo `_C_<número>` do UE4
   removido, prefixos `Play_`/`Cue_`/`Act_` tratados) e o texto correto é
   retornado diretamente.
2. **Fallback de `FindAltDataSetByLayerName`** — quando o dataset de um cenário
   não está carregado, o motor recebe o primeiro dataset carregado em vez de
   `NULL`, então a busca nativa também funciona.

## Suporte

Se as legendas ainda quebrarem após a instalação, envie o conteúdo do
`LiS_SubtitleFix.log` para o autor do mod.

## Licença

MIT. Criado para a comunidade de mods de Life is Strange Remastered.
