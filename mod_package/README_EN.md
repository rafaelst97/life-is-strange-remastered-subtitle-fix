# Life is Strange Remastered - Universal Subtitle Fix

This mod resolves the critical issue where subtitles disappear or display internal file names (e.g., `Act_E2...`) during scene transitions or episode changes in *Life is Strange Remastered*.

## 🌍 Universal Support
This fix works for **all languages** available in the game (English, French, German, Spanish, Italian, Portuguese, and Japanese). The mod automatically detects the active language from your game settings in real-time.

## 🛠️ How to Install (Simple Installation)

1. Download and extract this `.zip` file.
2. You will see a folder named `Binaries`.
3. Copy this `Binaries` folder and paste it into your game's root directory, where the main `LIS` folder is located.
   - The exact path where you should paste is: `\Life is Strange Remastered\LIS\`
   - Example: `C:\Program Files (x86)\Steam\steamapps\common\Life is Strange Remastered\LIS\`
4. Windows will ask if you want to merge the folder. Only the `XINPUT1_3.dll` file will be placed in the `Win64` folder. NO original game files will be overwritten or deleted.

## 🚀 How it Works
The error occurs due to a bug in the modified Unreal Engine by Deck Nine during new scene loads: the engine "forgets" to load the subtitle file (`.cue`) and only loads the lip-sync data (`.lipsync`). 
This mod (XINPUT1_3.dll) is silently injected when you launch the game. It loads the original subtitle files directly from your HDD into memory. When the game fails to fetch the official text, our DLL instantly injects the correct phrase onto the screen, solving the bug at its root without relying on the game's flawed streaming engine.

## ⚠️ Uninstallation
If you wish to remove the mod, simply delete the `XINPUT1_3.dll` file located at:
`Life is Strange Remastered\LIS\Binaries\Win64\XINPUT1_3.dll`

---
**Created by rafaelst97 and Antigravity.**
