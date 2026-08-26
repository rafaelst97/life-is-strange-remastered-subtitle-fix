# Life is Strange Remastered - Subtitle Fix Mod (PC)

A high-performance native C++ mod that fixes the subtitle failure bug in
*Life is Strange Remastered* on PC, where subtitles intermittently display raw
internal audio-cue / file identifiers (such as `Cue_E5_7Z_..._C_2147222737`)
instead of translated dialogue text after scene transitions, character switches
or episode changes.

**The fix works in every language the game offers.**

---

## The Issue

In *Life is Strange Remastered*, subtitle loading is handled by the
`UDNEAltData` subsystem in Unreal Engine 4:

1. When an audio event triggers, `GetSubtitleText` resolves the level/sub-level
   that owns the cue through `FindAltDataSetByLayerName`.
2. When a scene is streamed in, its subtitle dataset is frequently not loaded
   in memory yet, so the lookup returns `NULL` and the validator aborts early.
3. When the lookup fails, the engine falls back to rendering the raw internal
   cue key on screen — the "filename instead of subtitle" symptom.
4. Switching the language in the menu forces the engine to reload every
   subtitle dataset, which is why that workaround temporarily "fixes" the
   subtitles until the next scene transition.

---

## The Solution

A dual-layer, zero-overhead, runtime-only fix (the game executable is never
modified):

### 1. Native `GetSubtitleText` interceptor (`XINPUT1_3.dll`)
- Built with **MinHook** and compiled with MSVC 2022.
- Embeds the master dictionary of **10,475 dialogue lines** (≈64,000 aliases)
  across all 5 episodes in native UTF-16 memory.
- Normalizes every incoming cue name before lookup:
  - strips the UE4 object instance suffix `_C_<number>`;
  - handles `Play_`, `Cue_` and `Act_` prefixes;
  - falls back to progressively shorter alias forms.
- Any subtitle request, in any language and any scene, is resolved against the
  complete database in real time and returned immediately, bypassing the buggy
  engine path.

### 2. `FindAltDataSetByLayerName` fallback hook
- When the exact scene dataset is not loaded, the engine receives the first
  loaded dataset instead of `NULL`.
- Because every `.cue` file ships the consolidated master database, the native
  engine lookup succeeds as a second line of defense.

---

## Installation

### Automated Install (1-Click)
1. Download or clone this repository.
2. Run `install.bat`.
3. Select your game directory if prompted.
4. Launch the game normally via `LiS.exe` or Steam/Epic.

### Manual Install
1. Copy `mod_package/Binaries/Win64/XINPUT1_3.dll` to:
   ```
   <GameRoot>\LIS\Binaries\Win64\XINPUT1_3.dll
   ```
2. If a copy exists at the game root (`<GameRoot>\XINPUT1_3.dll`), replace it
   with the same file.

### Uninstall
Delete the `XINPUT1_3.dll` files you copied. No other files are modified.

---

## Verifying the fix

After launching the game, check the log created next to the proxy DLL
(`<GameRoot>\LIS\Binaries\Win64\LiS_SubtitleFix.log`) for:
```
[LiS_SubMod] DllMain ATTACH
[DEBUG] GetSubtitleText hook created and enabled at ...
[DEBUG] FindAltDataSetByLayerName hook created and enabled at ...
[INIT] SubtitleMap loaded: ... entries
```

---

## Building from Source

### Requirements
- **Windows 10 / 11 (x64)**
- **Visual Studio 2022** (C++ Desktop Development workload)

### Build Steps
```cmd
cd src
build_dll.bat
```
The compiled `XINPUT1_3.dll` is generated in `src/` and automatically copied to
the game directory and `mod_package/`.

---

## Repository Structure

```
├── install.bat             # 1-Click Batch Installer
├── README.md               # Mod Documentation (English)
├── src/                    # C++ Source Code
│   ├── xinput_proxy.cpp    # Proxy DLL & MinHook Subtitle Interceptor
│   ├── xinput.def          # Export definitions
│   ├── subtitles_data.h    # Embedded UTF-16 subtitle dataset
│   ├── build_dll.bat       # MSVC compiler script
│   └── minhook/            # MinHook hooking library
├── tools/                  # Python Reverse Engineering & Analysis Tools
├── dist/                   # Ready-to-share community package
│   └── LiS_Subtitle_Fix_v2.0.zip  # Flat package (DLL + install/uninstall + EN/PT-BR guides)
└── mod_package/            # In-repo distribution package
    ├── Binaries/Win64/
    │   └── XINPUT1_3.dll   # Compiled mod binary
    ├── README_EN.md        # Install guide (English)
    ├── README_PT-BR.md     # Install guide (Português)
    └── install.bat         # Self-contained installer
```

---

## License
MIT License. Created for the *Life is Strange Remastered* modding community.
