# Life is Strange Remastered — Subtitle Fix Mod (v2)

This mod fixes the subtitle failure bug in *Life is Strange Remastered* on PC,
where subtitles stop working after a scene or episode transition and the raw
internal audio-cue identifier (the "file name", e.g. `Cue_E5_7Z_..._C_2147222737`)
is shown on screen instead of the actual dialogue text.

**The fix works regardless of the language selected in the game settings.**

---

## Why do the subtitles break?

Inside the game, subtitles are resolved by the `UDNEAltData` subsystem:

1. When an audio event plays, `GetSubtitleText` looks up the level/sub-level
   that owns the cue (`FindAltDataSetByLayerName`).
2. When a new scene is streamed in, its subtitle dataset is frequently **not
   loaded in memory yet**, so the lookup returns `NULL`.
3. When the lookup fails, the game falls back to printing the raw cue key —
   which is why you see the "file name" instead of text.
4. Changing the language in the menu forces the game to reload all subtitle
   datasets, which is why the workaround "worked" until the next transition.

## What this mod does

This package ships a native proxy DLL (`XINPUT1_3.dll`) that installs two
runtime hooks in the game engine:

1. **`GetSubtitleText` interceptor** — resolves every subtitle cue against an
   embedded master database (10,475 lines / ~64,000 aliases covering all 5
   episodes). The cue name is normalized (the UE4 `_C_<number>` object suffix
   is stripped, prefixes such as `Play_`/`Cue_`/`Act_` are handled, and shorter
   alias forms are tried) so that **every** subtitle matches. When a match is
   found the correct text is returned immediately, bypassing the buggy engine
   path.
2. **`FindAltDataSetByLayerName` fallback** — when the exact scene dataset is
   not loaded, the engine now receives the first loaded dataset instead of
   `NULL`. Because every `.cue` file ships the consolidated master database,
   the native engine lookup also succeeds as a second line of defense.

Result: subtitles no longer break after scene/episode transitions, and you
never have to switch the language in the menu to fix them again.

## What it does NOT do

- It does not modify the game executable.
- It does not change voice-over audio.
- It provides the translated (PT-BR) subtitle database as the subtitle source;
  the *fix itself* is language-agnostic and activates in every language the
  game offers.

---

## Installation

### Option A — Automatic installer

1. Copy the `mod_package` folder anywhere on your PC.
2. Run `install.bat` (Windows). If your game is not at
   `C:\Games\Life is Strange Remastered`, type the correct folder when asked.
3. Launch the game normally (Steam, Epic, or `LiS.exe`).

### Option B — Manual installation

1. Locate your game folder (example: `C:\Games\Life is Strange Remastered`).
2. Copy `Binaries\Win64\XINPUT1_3.dll` from this package into:
   ```
   <GameFolder>\LIS\Binaries\Win64\XINPUT1_3.dll
   ```
   (overwrite if asked).
3. If a `XINPUT1_3.dll` already exists at the game root
   (`<GameFolder>\XINPUT1_3.dll`), replace it with the one from this package too.
4. Launch the game.

## Uninstallation

Delete the `XINPUT1_3.dll` you copied in the steps above (both copies). The
game will return to its original behavior.

## Verifying it works

After launching the game, open the log file that is created next to the DLL:

```
<GameFolder>\LIS\Binaries\Win64\LiS_SubtitleFix.log
```

A successful install logs entries like:
```
[LiS_SubMod] DllMain ATTACH
[DEBUG] GetSubtitleText hook created and enabled at ...
[DEBUG] FindAltDataSetByLayerName hook created and enabled at ...
[INIT] SubtitleMap loaded: ... entries
```
If some cue still fails to resolve, it is logged as `[HOOK] NO MATCH ...`.
With this fix, subtitle cues resolve without needing any language change.

## What is NOT needed

The fix is fully self-contained in the single `XINPUT1_3.dll`. You do **not**
need to replace any `.cue` files in `LIS\Content\AltData`, edit any `.ini`,
or modify the game executable.

## Building from source

See the repository root `README.md` (requires Visual Studio 2022, C++ Desktop
workload; run `src\build_dll.bat`).

## License

MIT. Created for the Life is Strange Remastered modding community.
