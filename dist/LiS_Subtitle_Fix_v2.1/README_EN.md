# Life is Strange Remastered — Subtitle Fix Mod v2.1

Fixes the subtitle failure bug in *Life is Strange Remastered* on PC, where
subtitles stop working — most noticeably right at the start of **Episode 2** —
and the raw audio-cue identifier (the "file name", e.g.
`Cue_E5_7Z_..._C_2147222737`) is shown instead of the dialogue text. Switching
the language in the menu and back used to be the only way to force the
subtitles to reload correctly; this mod removes the need for that workaround.

**Works in every language the game offers — you never need to switch the
language in the menu to fix subtitles again.**

---

## What's new in v2.1

Episode 2's opening scenes could still show the raw cue name even with v2.0
installed, because the runtime cue `FName` sometimes carries a Blueprint
instance suffix (`_C_<number>`) that never matches any dataset key, and in a
few cases the subtitle *display* code itself falls back to printing the raw
name before the mod's lookup ever runs. v2.1 adds two more hooks that close
both gaps — see "How it works" below.

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

If you have an older v2.0 install, just overwrite it the same way — no
uninstall step is required between versions.

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
[DEBUG] SearchSubtitle hook created and enabled at ...
[DEBUG] FNameToString hook created and enabled at ...
[INIT] SubtitleMap loaded: ... entries
```

## How it works (brief)

Subtitles go through several native engine steps before reaching the screen;
the fix hooks each step so the raw cue name can never make it through:

1. **`GetSubtitleText` interceptor** — every subtitle cue is resolved against an
   embedded database of 10,475 lines (~64,000 aliases) covering all 5 episodes.
2. **`FindAltDataSetByLayerName` fallback** — when a scene's dataset is not
   loaded yet, the engine receives the first loaded dataset instead of `NULL`,
   so the native lookup also succeeds.
3. **`SearchSubtitle` FName normalization** *(new in v2.1)* — the runtime cue
   name sometimes carries a Blueprint instance suffix (`_C_<number>`) that
   never matches a dataset key. This hook strips that suffix before the
   engine's own hash-table lookup runs, so the native lookup succeeds on the
   first try instead of falling through to the buggy path.
4. **Display-time text substitution** *(new in v2.1)* — as a last line of
   defense, the exact call the subtitle widget uses to turn the cue name into
   on-screen text is hooked too. If a cue ever reaches that point unresolved,
   the mod substitutes the correct translated line before it is drawn, so the
   player never sees a raw cue key even in the worst case.

## Support

If subtitles still break after installing, share the `LiS_SubtitleFix.log`
contents with the mod author.

## License

MIT. Created for the Life is Strange Remastered modding community.
