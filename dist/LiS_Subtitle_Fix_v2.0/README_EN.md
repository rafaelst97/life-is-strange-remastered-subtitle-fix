# Life is Strange Remastered — Subtitle Fix Mod v2.0

Fixes the subtitle failure bug in *Life is Strange Remastered* on PC, where
subtitles stop working after a scene or episode transition and the raw audio-cue
identifier (the "file name", e.g. `Cue_E5_7Z_..._C_2147222737`) is shown instead
of the dialogue text.

**Works in every language the game offers — you never need to switch the
language in the menu to fix subtitles again.**

---

## What's inside

| File              | Purpose                                            |
|-------------------|----------------------------------------------------|
| `XINPUT1_3.dll`   | The mod itself (native engine hooks, all compiled) |
| `install.bat`     | One-click installer                                |
| `uninstall.bat`   | Removes the mod                                    |
| `README_EN.md`    | This guide (English)                               |
| `README_PT-BR.md` | Guia de instalação (Português)                     |
| `LICENSE`         | MIT license                                        |

**No compilation is needed.** The DLL is already built.

---

## Installation

### Option A — Automatic (recommended)

1. Extract this folder anywhere.
2. Run `install.bat`.
3. If your game is not at `C:\Games\Life is Strange Remastered`, type its
   folder when asked.
4. Launch the game normally (Steam, Epic or `LiS.exe`).

### Option B — Manual

1. Find your game folder (e.g. `C:\Games\Life is Strange Remastered`).
2. Copy `XINPUT1_3.dll` into:
   ```
   <GameFolder>\LIS\Binaries\Win64\XINPUT1_3.dll
   ```
   (overwrite if asked.)
3. If a `XINPUT1_3.dll` already exists at the game root
   (`<GameFolder>\XINPUT1_3.dll`), replace it with the same file.

## Uninstallation

Run `uninstall.bat` (or manually delete the `XINPUT1_3.dll` copies you added).
The game returns to its original behavior. No other files are touched.

---

## What is NOT required

- No `.cue` files need to be replaced under `LIS\Content\AltData`.
- No `.ini` edits.
- The game executable is never modified.

The entire fix is self-contained in the single `XINPUT1_3.dll`.

## Verifying it works

Launch the game, then open the log created next to the DLL:

```
<GameFolder>\LIS\Binaries\Win64\LiS_SubtitleFix.log
```

It should contain lines like:
```
[LiS_SubMod] DllMain ATTACH
[DEBUG] GetSubtitleText hook created and enabled at ...
[DEBUG] FindAltDataSetByLayerName hook created and enabled at ...
[INIT] SubtitleMap loaded: ... entries
```

Any cue that still fails is logged as `[HOOK] NO MATCH ...`.

## How it works (brief)

1. **`GetSubtitleText` interceptor** — every subtitle cue is resolved against an
   embedded database of 10,475 lines (~64,000 aliases) covering all 5 episodes.
   The cue name is normalized (UE4 `_C_<number>` suffix stripped, `Play_`/
   `Cue_`/`Act_` prefixes handled) and the correct text is returned directly.
2. **`FindAltDataSetByLayerName` fallback** — when a scene dataset is not loaded,
   the engine receives the first loaded dataset instead of `NULL`, so the native
   lookup also succeeds.

## Support

If subtitles still break after installing, share the `LiS_SubtitleFix.log`
contents with the mod author.

## License

MIT. Created for the Life is Strange Remastered modding community.
