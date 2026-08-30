# Life is Strange Remastered — Subtitle Fix

Fixes the bug where the game shows a raw internal cue name instead of the spoken
line, usually right after a scene or episode change:

```
Cue_E5_3B_ArtGallery_PhotoLook_Admirer1_050_C_2147461859
```

Works in every language the game ships. Nothing in the game is modified — no
executable patching, no edits to the paks or to `LIS/Content/AltData`.

## Install

1. Close the game.
2. Run `install.bat`, or copy `Binaries\Win64\XINPUT1_3.dll` to:
   ```
   <GameFolder>\LIS\Binaries\Win64\XINPUT1_3.dll
   ```
3. Launch the game normally (Steam, Epic, GOG or `LiS.exe`).

## Uninstall

Delete `<GameFolder>\LIS\Binaries\Win64\XINPUT1_3.dll`.

## Checking that it is working

The mod writes `XINPUT1_3.log` next to itself in `LIS\Binaries\Win64\`:

```
[INIT] subtitle fix active - GetLocalizedText hooked at 00007FF7...
[FIX] resolved 'Cue_E2_1A_..._010_C_2147459969' -> 'Cue_E2_1A_..._010'
```

If the log says the game build was not recognised, the mod has deliberately done
nothing — it only patches the exact shipping build it was built against.

## What it does

The game stores its subtitles in localization tables inside `pakchunk0`, keyed by
the cue name. A cue actor that is spawned while a sub-level streams in gets an
extra `_C_<number>` suffix from Unreal Engine, so its key no longer matches the
table and the game prints the key instead of the line.

The mod hooks the game's own subtitle lookup. When — and only when — that lookup
fails, it removes the `_C_<number>` suffix and asks the game again. The text
still comes from the game's own tables, so it is always correct and always in
the language you selected.

## Language

The game picks subtitles from the culture chosen in its options menu. If you
want to set it by hand, edit:

```
%LOCALAPPDATA%\LIS\Saved\Config\WindowsNoEditor\Game.ini
```

```ini
[Internationalization]
Culture=pt-BR
```

Valid values are the culture folders the game ships: `de`, `en`, `es`, `es-419`,
`fr`, `it`, `ja`, `pt-BR`, `ru`, `zh-Hans`.

## License

MIT.
