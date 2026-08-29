# Life is Strange Remastered — Mod de Correção de Legendas v2.1

Corrige o bug de legendas de *Life is Strange Remastered* no PC, em que as
legendas param de funcionar — principalmente logo no começo do **Episódio 2**
— e, no lugar do texto, aparece o identificador bruto do áudio (o "nome do
arquivo", ex.: `Cue_E5_7Z_..._C_2147222737`). Antes, trocar o idioma no menu e
voltar era a única forma de forçar a legenda a recarregar corretamente; este
mod elimina a necessidade desse contorno.

**Funciona em todos os idiomas do jogo — você nunca mais precisa trocar o
idioma no menu para as legendas voltarem a funcionar.**

---

## Novidades da v2.1

No início do Episódio 2, mesmo com a v2.0 instalada, a legenda ainda podia
mostrar o nome bruto do cue. Isso acontece porque o `FName` do cue em tempo de
execução às vezes carrega um sufixo de instância do Blueprint (`_C_<número>`)
que nunca bate com nenhuma chave do banco de dados, e em alguns casos o
próprio código de exibição da legenda cai no texto bruto antes mesmo da busca
do mod rodar. A v2.1 adiciona dois hooks a mais que fecham essas duas brechas
— veja "Como funciona" abaixo.

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

Se você já tem a v2.0 instalada, é só sobrescrever da mesma forma — não é
preciso desinstalar antes de atualizar.

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
[DEBUG] SearchSubtitle hook created and enabled at ...
[DEBUG] FNameToString hook created and enabled at ...
[INIT] SubtitleMap loaded: ... entries
```

## Como funciona (resumo)

A legenda passa por várias etapas nativas do motor antes de chegar na tela; a
correção intercepta cada etapa para que o nome bruto do cue nunca escape:

1. **Interceptador de `GetSubtitleText`** — cada cue de legenda é resolvido
   contra um banco embutido de 10.475 falas (~64.000 aliases) cobrindo os 5
   episódios.
2. **Fallback de `FindAltDataSetByLayerName`** — quando o dataset de um
   cenário ainda não está carregado, o motor recebe o primeiro dataset
   carregado em vez de `NULL`, então a busca nativa também funciona.
3. **Normalização de FName em `SearchSubtitle`** *(novo na v2.1)* — o nome do
   cue em tempo de execução às vezes carrega um sufixo de instância do
   Blueprint (`_C_<número>`) que nunca bate com uma chave do dataset. Esse
   hook remove o sufixo antes da busca na hash table do próprio motor, então a
   busca nativa já funciona de primeira em vez de cair no caminho com bug.
4. **Substituição de texto na exibição** *(novo na v2.1)* — como última linha
   de defesa, a chamada exata que o widget de legenda usa para transformar o
   nome do cue em texto na tela também é interceptada. Se algum cue ainda
   chegar ali sem resolução, o mod substitui pela fala traduzida correta antes
   dela ser desenhada, então o jogador nunca vê o nome bruto do cue, nem no
   pior caso.

## Suporte

Se as legendas ainda quebrarem após a instalação, envie o conteúdo do
`LiS_SubtitleFix.log` para o autor do mod.

## Licença

MIT. Criado para a comunidade de mods de Life is Strange Remastered.
