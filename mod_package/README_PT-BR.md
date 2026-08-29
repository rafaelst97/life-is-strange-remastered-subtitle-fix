# Life is Strange Remastered — Mod de Correção de Legendas (v2.1)

Este mod corrige o bug de legendas de *Life is Strange Remastered* no PC, em que
as legendas quebram após uma troca de cenário ou episódio e, no lugar do texto,
aparece o identificador interno do áudio (o "nome do arquivo", ex.:
`Cue_E5_7Z_..._C_2147222737`).

**A correção funciona independentemente do idioma selecionado nas configurações
do jogo.**

---

## Por que as legendas quebram?

Dentro do jogo, as legendas são resolvidas pelo subsistema `UDNEAltData`:

1. Quando um evento de áudio dispara, `GetSubtitleText` procura o nível/subnível
   dono do cue (`FindAltDataSetByLayerName`).
2. Quando um novo cenário é carregado, o conjunto de legendas dele muitas vezes
   **ainda não está na memória**, então a busca retorna `NULL`.
3. Quando a busca falha, o jogo cai num fallback que imprime a chave bruta do
   cue — é por isso que aparece o "nome do arquivo" em vez da legenda.
4. Trocar o idioma no menu força o jogo a recarregar todos os conjuntos de
   legendas, por isso a solução "funcionava" até a próxima transição.

## O que este mod faz

Este pacote traz uma DLL nativa de proxy (`XINPUT1_3.dll`) que instala quatro
hooks em tempo de execução no motor do jogo:

1. **Interceptador de `GetSubtitleText`** — resolve cada cue de legenda contra
   um banco de dados mestre embutido (10.475 falas / ~64.000 aliases cobrindo
   os 5 episódios). O nome do cue é normalizado (o sufixo `_C_<número>` do UE4
   é removido, prefixos como `Play_`/`Cue_`/`Act_` são tratados e formas
   abreviadas são tentadas) para que **toda** legenda encontre correspondência.
   Quando encontra, o texto correto é retornado imediatamente, contornando o
   caminho com bug do motor.
2. **Fallback de `FindAltDataSetByLayerName`** — quando o conjunto do cenário
   exato não está carregado, o motor agora recebe o primeiro conjunto carregado
   em vez de `NULL`. Como todo arquivo `.cue` traz o banco mestre consolidado,
   a busca nativa do motor também passa a funcionar como segunda linha de
   defesa.
3. **Normalização de FName em `SearchSubtitle`** *(novo na v2.1)* — era isso
   que ainda quebrava o começo do Episódio 2: o `FName` do cue em tempo de
   execução às vezes carrega um sufixo de instância do Blueprint
   (`_C_<número>`) que nunca bate com uma chave do dataset. Esse hook remove o
   sufixo antes da busca na hash table do próprio motor, então ela já funciona
   de primeira.
4. **Substituição de texto na exibição** *(novo na v2.1)* — como última linha
   de defesa, a chamada exata que o widget de legenda usa para transformar o
   nome do cue em texto na tela também é interceptada, então um cue que não
   resolveu ainda é trocado pela fala traduzida correta antes de ser
   desenhado.

Resultado: as legendas não quebram mais após trocas de cenário/episódio —
incluindo a abertura do Episódio 2 — e você nunca mais precisa trocar o
idioma no menu para consertá-las.

## O que ele NÃO faz

- Não modifica o executável do jogo.
- Não altera o áudio/dublagem.
- Fornece o banco de legendas traduzido (PT-BR) como fonte das legendas; a
  *correção em si* é independente de idioma e ativa em todos os idiomas
  disponíveis no jogo.

---

## Instalação

### Opção A — Instalador automático

1. Copie a pasta `mod_package` para qualquer lugar do PC.
2. Execute `install.bat` (Windows). Se o jogo não estiver em
   `C:\Games\Life is Strange Remastered`, digite a pasta correta quando
   perguntado.
3. Abra o jogo normalmente (Steam, Epic ou `LiS.exe`).

### Opção B — Instalação manual

1. Localize a pasta do jogo (ex.: `C:\Games\Life is Strange Remastered`).
2. Copie o arquivo `Binaries\Win64\XINPUT1_3.dll` deste pacote para:
   ```
   <PastaDoJogo>\LIS\Binaries\Win64\XINPUT1_3.dll
   ```
   (substitua se pedir).
3. Se já existir um `XINPUT1_3.dll` na raiz do jogo
   (`<PastaDoJogo>\XINPUT1_3.dll`), substitua também pelo arquivo deste pacote.
4. Abra o jogo.

## Desinstalação

Apague os arquivos `XINPUT1_3.dll` copiados nos passos acima (as duas cópias).
O jogo volta ao comportamento original.

## Como verificar se está funcionando

Depois de abrir o jogo, abra o arquivo de log criado ao lado do DLL:

```
<PastaDoJogo>\LIS\Binaries\Win64\LiS_SubtitleFix.log
```

Uma instalação bem-sucedida registra linhas como:
```
[LiS_SubMod] DllMain ATTACH
[DEBUG] GetSubtitleText hook created and enabled at ...
[DEBUG] FindAltDataSetByLayerName hook created and enabled at ...
[DEBUG] SearchSubtitle hook created and enabled at ...
[DEBUG] FNameToString hook created and enabled at ...
[INIT] SubtitleMap loaded: ... entries
```
Com esta correção, os cues de legenda são resolvidos sem precisar trocar de
idioma.

## O que NÃO é necessário

A correção é totalmente autocontida no único arquivo `XINPUT1_3.dll`. Você
**não** precisa substituir nenhum arquivo `.cue` em `LIS\Content\AltData`,
editar `.ini` nem modificar o executável do jogo.

## Compilar a partir do código-fonte

Veja o `README.md` na raiz do repositório (requer Visual Studio 2022 com a
carga de trabalho de C++; execute `src\build_dll.bat`).

## Licença

MIT. Criado para a comunidade de mods de Life is Strange Remastered.
