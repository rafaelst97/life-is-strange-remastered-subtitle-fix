<!-- ==================== English ==================== -->

# Life is Strange Remastered - Universal Subtitle Fix

This repository contains the source code for the definitive, universal subtitle fix for *Life is Strange Remastered*.

## The Problem
In the remastered version by Deck Nine, subtitles frequently break during scene transitions or episode changes, causing the game to display raw internal keys (e.g., Act_E2_1A_...) instead of the actual localized text, or simply displaying nothing.

Our deep dive into the game's binary revealed that during map transitions, the modified Unreal Engine localization subsystem calls FindOrLoadAltDataSet asking for .lipsync data but completely skips loading the .cue subtitle data for the new area.

## The Solution
This mod utilizes a custom XINPUT1_3.dll proxy to inject code directly into the game's memory at runtime using MinHook. It bypasses the flawed UE4 streaming localization cache entirely:
1. **Universal Parsing**: At startup, it parses the raw UTF-8 .cue files from LIS/Content/AltData/ for all available languages into a fast C++ memory dictionary.
2. **Dynamic Culture Detection**: It monitors the game's Game.ini config in real-time to know which language the user is playing in.
3. **Memory Hijack Injection**: When the engine's GetLocalizedText fails to resolve a subtitle, the DLL intercepts it, pulls the correct translation from our dictionary, allocates a valid engine buffer (by hijacking a known massive string like the Epilepsy Warning), and injects the text perfectly.

## Building from Source
1. Install Visual Studio (with Desktop development with C++).
2. Open a Visual Studio Developer Command Prompt.
3. Run uild_dll.bat inside the src folder.

## Installation for Players
**[📥 CLICK HERE TO DOWNLOAD THE COMPILED .ZIP FILE](https://github.com/rafaelst97/life-is-strange-remastered-subtitle-fix/releases/download/v2.0/LiS_Remastered_Universal_Subtitle_Fix_v2.0.zip)** 
*(or visit the [Releases page](https://github.com/rafaelst97/life-is-strange-remastered-subtitle-fix/releases/latest))*

Installation requires a simple copy-paste of the Binaries folder inside the .zip into your game's installation directory. No game files are modified or overwritten.

<br><hr><br>

<!-- ==================== Português (Brasil) ==================== -->

# Life is Strange Remastered - Correção Universal das Legendas

Este repositório contém o código-fonte para a correção definitiva e universal das legendas de *Life is Strange Remastered*.

## O Problema
Na versão remasterizada pela Deck Nine, as legendas frequentemente quebram durante as transições de cenários ou mudanças de episódios, fazendo com que o jogo exiba identificadores internos crus (ex: Act_E2_1A_...) em vez do texto traduzido real, ou simplesmente não exiba nada.

Nossa análise profunda do binário do jogo revelou que, durante as transições de mapa, o subsistema de localização modificado da Unreal Engine pede dados de .lipsync, mas pula completamente o carregamento dos dados de legenda .cue para a nova área.

## A Solução
Este mod utiliza um proxy personalizado XINPUT1_3.dll para injetar código diretamente na memória do jogo em tempo de execução usando o MinHook. Ele contorna completamente o cache de localização quebrado:
1. **Análise Universal**: Na inicialização, ele faz o parsing dos arquivos .cue originais em UTF-8 de LIS/Content/AltData/ para todos os idiomas em um dicionário rápido em C++.
2. **Detecção Dinâmica**: Monitora as configurações do Game.ini em tempo real para saber em qual idioma o usuário está jogando.
3. **Injeção Dinâmica**: Quando a engine falha, a DLL intercepta, puxa a tradução do nosso dicionário, aloca um buffer válido da engine (sequestrando uma string gigante como o Aviso de Epilepsia) e injeta o texto na tela.

## Instalação para Jogadores
**[📥 CLIQUE AQUI PARA BAIXAR O MOD (ARQUIVO .ZIP)](https://github.com/rafaelst97/life-is-strange-remastered-subtitle-fix/releases/download/v2.0/LiS_Remastered_Universal_Subtitle_Fix_v2.0.zip)** 
*(ou visite a [página de Releases](https://github.com/rafaelst97/life-is-strange-remastered-subtitle-fix/releases/latest))*

A instalação requer apenas copiar a pasta Binaries que está dentro do .zip para o diretório do seu jogo.

<br><hr><br>

<!-- ==================== Español ==================== -->

# Life is Strange Remastered - Corrección Universal de Subtítulos

Este repositorio contiene el código fuente de la corrección definitiva de subtítulos para *Life is Strange Remastered*. El mod soluciona el error de carga de los archivos .cue que la versión remasterizada omite al cambiar de zona.

La solución utiliza XINPUT1_3.dll (vía MinHook) para leer directamente los textos desde los archivos originales y sobrescribir un espacio de memoria válido en el motor del juego en tiempo real, admitiendo todos los idiomas dinámicamente según el archivo Game.ini.

## Instalación para Jugadores
**[📥 HAGA CLIC AQUÍ PARA DESCARGAR EL ARCHIVO .ZIP](https://github.com/rafaelst97/life-is-strange-remastered-subtitle-fix/releases/download/v2.0/LiS_Remastered_Universal_Subtitle_Fix_v2.0.zip)** 
*(o visite la [página de Lanzamientos](https://github.com/rafaelst97/life-is-strange-remastered-subtitle-fix/releases/latest))*

Solo necesita copiar la carpeta Binaries que está dentro del .zip al directorio de su juego.

<br><hr><br>

<!-- ==================== Français ==================== -->

# Life is Strange Remastered - Correction Universelle des Sous-titres

Ce dépôt contient le code source de la correction définitive des sous-titres pour *Life is Strange Remastered*. Le mod corrige l'échec de chargement des fichiers .cue que la version remasterisée ignore lors des changements de zones.

La solution utilise XINPUT1_3.dll (via MinHook) pour lire directement les textes depuis les fichiers originaux et écraser un espace mémoire valide dans le moteur de jeu en temps réel, supportant dynamiquement toutes les langues via Game.ini.

## Installation pour les Joueurs
**[📥 CLIQUEZ ICI POUR TÉLÉCHARGER LE FICHIER .ZIP](https://github.com/rafaelst97/life-is-strange-remastered-subtitle-fix/releases/download/v2.0/LiS_Remastered_Universal_Subtitle_Fix_v2.0.zip)** 
*(ou visitez la [page des Versions](https://github.com/rafaelst97/life-is-strange-remastered-subtitle-fix/releases/latest))*

Il vous suffit de copier le dossier Binaries présent dans le .zip vers le répertoire de votre jeu.

<br><hr><br>

<!-- ==================== Deutsch ==================== -->

# Life is Strange Remastered - Universeller Untertitel-Fix

Dieses Repository enthält den Quellcode für die ultimative Untertitel-Korrektur für *Life is Strange Remastered*. Der Mod behebt den Ladefehler der .cue-Dateien, den die Remastered-Version bei Zonenwechseln ignoriert.

Die Lösung verwendet XINPUT1_3.dll (via MinHook), um Texte direkt aus den Originaldateien zu lesen und den Speicher der Engine in Echtzeit zu überschreiben, wobei alle Sprachen dynamisch unterstützt werden.

## Installation für Spieler
**[📥 KLICKEN SIE HIER, UM DIE .ZIP-DATEI HERUNTERZULADEN](https://github.com/rafaelst97/life-is-strange-remastered-subtitle-fix/releases/download/v2.0/LiS_Remastered_Universal_Subtitle_Fix_v2.0.zip)** 
*(oder besuchen Sie die [Releases-Seite](https://github.com/rafaelst97/life-is-strange-remastered-subtitle-fix/releases/latest))*

Sie müssen lediglich den Ordner Binaries aus der .zip-Datei in Ihr Spielverzeichnis kopieren.

<br><hr><br>

<!-- ==================== Italiano ==================== -->

# Life is Strange Remastered - Fix Universale dei Sottotitoli

Questo repository contiene il codice sorgente per la correzione definitiva dei sottotitoli. La mod risolve l'errore di caricamento dei file .cue che la versione rimasterizzata ignora durante i cambi di zona.

La soluzione utilizza XINPUT1_3.dll (tramite MinHook) per leggere direttamente i testi e sovrascrivere la memoria del motore in tempo reale, supportando tutte le lingue.

## Installazione per i Giocatori
**[📥 CLICCA QUI PER SCARICARE IL FILE .ZIP](https://github.com/rafaelst97/life-is-strange-remastered-subtitle-fix/releases/download/v2.0/LiS_Remastered_Universal_Subtitle_Fix_v2.0.zip)** 
*(o visita la [pagina delle Release](https://github.com/rafaelst97/life-is-strange-remastered-subtitle-fix/releases/latest))*

Basta copiare la cartella Binaries contenuta nel .zip nella directory del gioco.

<br><hr><br>

<!-- ==================== Русский ==================== -->

# Life is Strange Remastered - Универсальное исправление субтитров

В этом репозитории содержится исходный код для окончательного исправления субтитров. Мод исправляет ошибку загрузки файлов .cue, которую ремастер игнорирует при смене зон.

Решение использует XINPUT1_3.dll для прямого чтения текстов из файлов и перезаписи памяти движка в реальном времени, поддерживая все языки.

## Установка для игроков
**[📥 НАЖМИТЕ ЗДЕСЬ, ЧТОБЫ СКАЧАТЬ ФАЙЛ .ZIP](https://github.com/rafaelst97/life-is-strange-remastered-subtitle-fix/releases/download/v2.0/LiS_Remastered_Universal_Subtitle_Fix_v2.0.zip)** 
*(или посетите [страницу Релизов](https://github.com/rafaelst97/life-is-strange-remastered-subtitle-fix/releases/latest))*

Вам просто нужно скопировать папку Binaries из .zip в каталог вашей игры.

<br><hr><br>

<!-- ==================== 简体中文 ==================== -->

# 奇异人生：重制版 - 通用字幕修复 (Universal Subtitle Fix)

此存储库包含《奇异人生：重制版》字幕修复的源代码。该模组修复了重制版在切换区域时忽略加载 .cue 文件的错误。

该解决方案使用 XINPUT1_3.dll（通过 MinHook）直接从原始文件中读取文本，并实时覆盖引擎内存，动态支持所有语言。

## 玩家安装方法
**[📥 点击此处下载编译好的 .ZIP 文件](https://github.com/rafaelst97/life-is-strange-remastered-subtitle-fix/releases/download/v2.0/LiS_Remastered_Universal_Subtitle_Fix_v2.0.zip)** 
*(或访问 [发布页面](https://github.com/rafaelst97/life-is-strange-remastered-subtitle-fix/releases/latest))*

只需将 .zip 文件中的 Binaries 文件夹复制到您的游戏目录即可。

<br><hr><br>

<!-- ==================== 日本語 ==================== -->

# Life is Strange Remastered - ユニバーサル字幕修正 (Universal Subtitle Fix)

このリポジトリには、『Life is Strange Remastered』の字幕修正のソースコードが含まれています。このMODは、ゾーン変更時にリマスター版が無視する .cue ファイルの読み込みエラーを修正します。

このソリューションは XINPUT1_3.dll を使用して、ファイルから直接テキストを読み取り、リアルタイムでエンジンのメモリを上書きし、すべての言語を動的にサポートします。

## プレイヤー向けのインストール
**[📥 .ZIPファイルをダウンロードするにはここをクリック](https://github.com/rafaelst97/life-is-strange-remastered-subtitle-fix/releases/download/v2.0/LiS_Remastered_Universal_Subtitle_Fix_v2.0.zip)** 
*(または[リリースページ](https://github.com/rafaelst97/life-is-strange-remastered-subtitle-fix/releases/latest)にアクセス)*

.zip 内の Binaries フォルダをゲームディレクトリにコピーするだけです。

