# Life is Strange Remastered - Universal Subtitle Fix (Correção Universal das Legendas)

Este mod resolve o problema crítico onde as legendas desaparecem ou mostram o nome do arquivo interno (ex: `Act_E2...`) durante a transição de cenários ou troca de episódios no *Life is Strange Remastered*.

## 🌍 Suporte Universal
A correção funciona para **todos os idiomas** disponíveis no jogo (Português, Espanhol, Inglês, Francês, Alemão, Italiano e Japonês). O mod detecta o idioma escolhido nas configurações do jogo automaticamente em tempo real.

## 🛠️ Como Instalar (Instalação Simples)

1. Baixe e extraia este arquivo `.zip`.
2. Você verá uma pasta chamada `Binaries`.
3. Copie essa pasta `Binaries` e cole dentro da pasta raiz do seu jogo, onde fica a pasta `LIS` principal.
   - O caminho exato da pasta onde você deve colar é: `\Life is Strange Remastered\LIS\`
   - Exemplo: `C:\Program Files (x86)\Steam\steamapps\common\Life is Strange Remastered\LIS\`
4. O Windows perguntará se você deseja mesclar a pasta. Apenas o arquivo `XINPUT1_3.dll` será inserido na pasta `Win64`. NENHUM arquivo do jogo será substituído ou apagado.

## 🚀 Como Funciona?
O erro ocorre porque a Unreal Engine (modificada pela Deck Nine) tem um bug na hora de carregar cenários novos: o motor gráfico "esquece" de carregar o arquivo das legendas (`.cue`) e carrega apenas o arquivo de animação labial (`.lipsync`). 
Este mod (XINPUT1_3.dll) é injetado silenciosamente quando você abre o jogo. Ele carrega os arquivos originais de legenda direto do seu HD para a memória e, quando o jogo falha em buscar o texto oficial, a nossa DLL injeta a frase correta instantaneamente no meio da tela, resolvendo o bug pela raiz sem depender da engine do jogo.

## ⚠️ Desinstalação
Se desejar remover o mod, basta excluir o arquivo `XINPUT1_3.dll` localizado em:
`Life is Strange Remastered\LIS\Binaries\Win64\XINPUT1_3.dll`

---
**Criado por rafaelst97 e Antigravity.**
