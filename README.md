# Life is Strange Remastered - Universal Subtitle Fix

This repository contains the source code for the definitive, universal subtitle fix for *Life is Strange Remastered*.

## The Problem
In the remastered version by Deck Nine, subtitles frequently break during scene transitions or episode changes, causing the game to display raw internal keys (e.g., Act_E2_1A_...) instead of the actual localized text, or simply displaying nothing.

Our deep dive into the game's binary revealed that during map transitions, the modified Unreal Engine localization subsystem calls FindOrLoadAltDataSet asking for .lipsync data but completely skips loading the .cue subtitle data for the new area.

## The Solution
This mod utilizes a custom XINPUT1_3.dll proxy to inject code directly into the game's memory at runtime using MinHook.
It bypasses the flawed UE4 streaming localization cache entirely:
1. **Universal Parsing**: At startup, it parses the raw UTF-8 .cue files from LIS/Content/AltData/ for all available languages into a fast C++ memory dictionary.
2. **Dynamic Culture Detection**: It monitors the game's Game.ini config in real-time to know which language the user is playing in.
3. **Memory Hijack Injection**: When the engine's GetLocalizedText fails to resolve a subtitle, the DLL intercepts it, pulls the correct translation from our dictionary, allocates a valid engine buffer (by hijacking a known massive string like the Epilepsy Warning), and injects the text perfectly.

## Building from Source
1. Install Visual Studio (with Desktop development with C++).
2. Open a Visual Studio Developer Command Prompt.
3. Run uild_dll.bat inside the src folder.

## Installation for Players
See the releases page for the compiled .zip file, which requires a simple copy-paste of the Binaries folder into your game's installation directory. No game files are modified or overwritten.
