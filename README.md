# Life is Strange Remastered - Subtitle Fix Mod

Mod para corrigir o bug crônico das legendas no **Life is Strange Remastered** (Unreal Engine 4), onde ao trocar de cenário, sala ou personagem, o jogo exibe os nomes técnicos dos arquivos de áudio (ex: `Act_E2_1A_...`, `Cue_E2_1B_...`) no lugar do texto traduzido.

---

## 🔍 Como o Bug Ocorre e Como o Mod Corrige

### Causa Raiz
No motor Unreal Engine 4 do Remastered, o jogo organiza as legendas em conjuntos de dados em memória (`AltDataSet`) indexados por *Layers de Contexto* (ex: `E2_1A`, `E2_1B`, etc.). Durante as transições de cenário por streaming dinâmico (*Level Streaming*), o jogo falha em instanciar o `AltDataSet` do novo contexto. Ao não encontrar a referência, o motor recorre ao comportamento padrão de fallback e imprime o identificador cru da fala na tela.

### Nossa Solução
Utilizamos o **UE4SS (Unreal Engine 4 Scripting System)** com injeção segura via proxy `dwmapi.dll` e desenvolvemos um mod em Lua (`SubtitleFixMod`) que:
1. Carrega todas as **10.475 falas do jogo** traduzidas em tabelas nativas de alta performance.
2. Intercepta em tempo de execução os hooks das funções visuais de legenda (`SetSubtitleCue`, `UpdateSubtitle`, `UpdateSubtitlesImplementable`).
3. Quando detecta uma chave técnica (`Act_...`, `Cue_...`), substitui instantaneamente pelo texto correto da fala antes de ser desenhado na tela.

---

## 🚀 Instalação Rápida

### Opção 1: Automática (Windows)
1. Baixe ou clone este repositório.
2. Execute o arquivo `install.bat`.
3. Abra o jogo normalmente.

### Opção 2: Manual
Copie o conteúdo da pasta `mod_package/Binaries/Win64/` diretamente para a pasta de binários do seu jogo:
```text
C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\
```
(ou o diretório correspondente da sua instalação Steam / Epic Games).

---

## 📁 Estrutura do Repositório

```text
├── mod_package/                     # Arquivos do mod prontos para distribuição
│   └── Binaries/Win64/
│       ├── dwmapi.dll               # Proxy DLL do UE4SS
│       ├── UE4SS.dll                # Engine do UE4SS
│       ├── UE4SS-settings.ini       # Configurações do UE4SS
│       └── Mods/
│           ├── mods.txt             # Lista de mods ativos
│           └── SubtitleFixMod/
│               └── Scripts/
│                   ├── main.lua     # Hook de interceptação e substituição
│                   └── subtitles_*.lua  # Dicionários de todas as 10.475 falas por idioma
├── tools/                           # Scripts Python auxiliares de engenharia reversa
│   ├── generate_lua_dicts.py        # Gera as tabelas Lua a partir dos arquivos .cue
│   ├── apply_subtitle_mod.py        # Consolidador de arquivos .cue
│   ├── build_pak_mod.py             # Gerador de patch .pak
│   └── restore_original_subtitles.py# Script de restauração
├── install.bat                      # Instalador automático
└── README.md
```

---

## 🌐 Idiomas Suportados
- 🇧🇷 Português do Brasil (`PTB`) - Ativo por padrão
- 🇺🇸 Inglês (`INT`)
- 🇫🇷 Francês (`FRA`)
- 🇩🇪 Alemão (`DEU`)
- 🇪🇸 Espanhol (`ESM` / `ESN`)
- 🇮🇹 Italiano (`ITA`)
- 🇯🇵 Japonês (`JPN`)

---

## 🛡️ Desinstalação
Basta apagar os seguintes arquivos de `LIS\Binaries\Win64\`:
- `dwmapi.dll`
- `UE4SS.dll`
- `UE4SS-settings.ini`
- `Mods/`
