# Suporte a Traduções de Fãs

O mod possui suporte automático a traduções criadas pela comunidade e distribuídas no formato original da Unreal Engine (`.pak`).

## O Problema das Traduções
Traduções de fãs geralmente substituem os textos em inglês (`Localization/en/*.ini`) empacotando-os num arquivo `.pak` que a Unreal Engine carrega nativamente.
Entretanto, devido ao mesmo bug da engine de perder o mapa de strings da memória durante carregamentos, essas legendas modificadas também sofriam do glitch e voltavam a exibir o nome da variável (ex: `Cue_C_129`).

O nosso hook original corrigia isso consultando os arquivos `.cue` oficiais instalados com o mod. Mas isso forçava o texto de volta para o idioma oficial e **sobrescrevia o idioma modificado pelo fã**.

## A Solução (Engenharia Reversa de Pacotes .pak)

Para resolver esse conflito de compatibilidade sem exigir passos extras do usuário, o nosso Mod faz o seguinte ao iniciar o jogo:

1. **Varredura no Diretório de Paks:** Ele procura por arquivos `.pak` na pasta `C:\Games\Life is Strange Remastered\LIS\Content\Paks\`.
2. **Filtro Oficial:** Ignora os pacotes gigantes oficiais do jogo (ex: `pakchunk0-WindowsNoEditor.pak` até `pakchunk5-WindowsNoEditor.pak`).
3. **Parseamento Unreal V3 (Index Hash):** O mod lê a assinatura no final do arquivo (os últimos 256 bytes) para localizar a tabela de `Index`.
4. **Extração na Memória:** Ele localiza as entradas referentes à arquivos de legenda (`CU_*.ini`).
5. **Cálculo de Chunk e Zlib:** Ignora o header nativo dos blocos de compressão da Unreal Engine e usa a biblioteca `miniz` em C++ para descompactar o payload em memória (Zlib).
6. **Injeção de Texto:** Ele parseia o idioma-alvo que a tradução de fã sobrescreveu (por exemplo, `en` / `INT`) e injeta essas chaves novas forçadamente em nosso dicionário interno na RAM (`g_AltDataDicts`).

### Força do Idioma de Backup
Se o mod detectar uma tradução de fã, ele ativa a variável `g_HasFanTranslation`. 
Quando o jogo "esquecer" a string de legenda, o nosso Mod intercepta o erro, verifica que há uma tradução de fã carregada, **ignora o arquivo Game.ini** (que poderia estar forçando o uso de legendas em pt-BR) e puxa diretamente a legenda recém-extraída do .pak modificado. 

Isso garante que a tradução de fã brilhe e nunca seja substituída.
