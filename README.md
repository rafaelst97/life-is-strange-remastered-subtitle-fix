# Life is Strange Remastered - Subtitle & Localization Engine Fix (PC)

A high-performance, native C++ mod that resolves the subtitle failure bug in *Life is Strange Remastered* on PC, where subtitles intermittently display raw internal audio cue / file identifiers (such as `Act_E2_1A_...` or `Cue_E1_...`) instead of translated dialogue text after scene transitions or character switches.

---

## 🎯 The Issue

In *Life is Strange Remastered*, subtitle loading is handled by the `UDNEAltData` subsystem in Unreal Engine 4. When an audio event triggers:
1. **Rigid Layer Name Validation**: The engine attempts to extract level/scene prefixes from the audio cue identifier. If a cue string does not strictly match hardcoded patterns (e.g. streaming sub-levels, secondary character lines, or ambient thoughts), the validator fails and aborts early.
2. **Missing Sub-Level Datasets**: When level streaming loads sub-scenes (e.g., `E2_1B` while only `E2_1A` is initialized in memory), `FindAltDataSetByLayerName` returns `NULL`.
3. **Fallback Failure**: When lookup fails, the engine defaults to rendering the raw internal cue key on screen.

---

## 💡 The Solution

This mod provides a dual-layer, zero-overhead fix:

1. **Native Proxy Mod (`XINPUT1_3.dll`)**:
   - Built with **MinHook** and compiled using MSVC 2022.
   - Embeds the master dictionary of **10,475 dialogue lines** in native UTF-16 memory.
   - Dynamically hooks `FindAltDataSetByLayerName` (`0x1407188a0`) and hooks/patches the rigid validator early-exit (`0x14071023d`).
   - Ensures that any subtitle request across all 5 episodes, scenes, and characters is resolved against the complete master subtitle database in real time.
2. **Consolidated Loose `.cue` Dictionaries**:
   - All `.cue` files in `LIS/Content/AltData/` are populated with complete dialogue dictionaries across all supported languages (`PTB`, `INT`, `ESN`, `FRA`, `DEU`, `ITA`, `JPN`, `ESM`).

---

## 🚀 Installation

### Automated Install (1-Click)
1. Download or clone this repository.
2. Run `install.bat`.
3. Select your game directory if prompted.
4. Launch the game normally via `LiS.exe` or Steam/Epic.

### Manual Install
1. Copy `XINPUT1_3.dll` to:
   ```
   <GameRoot>\LIS\Binaries\Win64\XINPUT1_3.dll
   ```
2. (Optional) Copy the contents of `mod_package/Content/AltData/` to:
   ```
   <GameRoot>\LIS\Content\AltData\
   ```

---

## 🛠️ Building from Source

### Requirements
- **Windows 10 / 11 (x64)**
- **Visual Studio 2022** (C++ Desktop Development workload)

### Build Steps
1. Open PowerShell or Command Prompt.
2. Navigate to `src/`:
   ```cmd
   cd src
   build_dll.bat
   ```
3. The compiled `XINPUT1_3.dll` will be generated in `src/` and automatically copied to your game directory.

---

## 📁 Repository Structure

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
│   ├── apply_master_fix.py # Binary patch generator
│   └── gen_master_bin.py   # UTF-16 binary database generator
└── mod_package/            # Ready-to-use distribution package
    └── Binaries/Win64/
        └── XINPUT1_3.dll   # Compiled mod binary
```

---

## 📜 License
MIT License. Created for the *Life is Strange Remastered* modding community.
