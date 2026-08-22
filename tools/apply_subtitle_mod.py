"""
Life is Strange Remastered - Subtitle Consolidation Mod
-------------------------------------------------------
This script consolidates all 10,475 subtitle cues into every single .cue file
for each supported language in LIS/Content/AltData.

This prevents the game engine's Level Streaming bug from showing raw Cue asset
names (e.g. Act_E2_1B...) instead of actual dialogue text when switching
scenes or characters.
"""

import os
import glob
import sys
from collections import defaultdict

GAME_DIR = r"C:\Games\Life is Strange Remastered"
ALT_DATA_DIR = os.path.join(GAME_DIR, "LIS", "Content", "AltData")

def consolidate_subtitles():
    print(f"Target AltData directory: {ALT_DATA_DIR}")
    if not os.path.exists(ALT_DATA_DIR):
        print(f"Error: {ALT_DATA_DIR} does not exist!")
        sys.exit(1)

    cue_files = glob.glob(os.path.join(ALT_DATA_DIR, "*.cue"))
    print(f"Found {len(cue_files)} .cue files.")

    # Group files and build master dictionaries per language
    lang_files = defaultdict(list)
    lang_master_dict = defaultdict(dict)

    for filepath in cue_files:
        filename = os.path.basename(filepath)
        # Format: CU_<MAP>_<LANG>.cue
        lang = filename[:-4].split("_")[-1]
        lang_files[lang].append(filepath)

        with open(filepath, "rb") as f:
            data = f.read()

        if not data.startswith(b"\xef\xbb\xbf"):
            print(f"Warning: File {filename} does not start with UTF-8 BOM.")
            body = data
        else:
            body = data[3:]

        items = body.split(b"\x00")
        if items and items[-1] == b"":
            items.pop()

        for i in range(0, len(items), 2):
            key = items[i]
            val = items[i + 1]
            # Store in master dictionary
            lang_master_dict[lang][key] = val

    print("\nMaster dictionary summary:")
    for lang, master in lang_master_dict.items():
        print(f" - {lang}: {len(master)} unique dialogue cues across {len(lang_files[lang])} files")

    # Generate the consolidated binary payload for each language
    for lang, master in lang_master_dict.items():
        print(f"\nApplying consolidation for language [{lang}]...")
        # Build payload: BOM + (key\x00val\x00 for all keys)
        payload_parts = [b"\xef\xbb\xbf"]
        for key in master:
            payload_parts.append(key)
            payload_parts.append(b"\x00")
            payload_parts.append(master[key])
            payload_parts.append(b"\x00")

        consolidated_payload = b"".join(payload_parts)
        payload_size_kb = len(consolidated_payload) / 1024.0
        print(f"Consolidated payload size: {payload_size_kb:.2f} KB ({len(consolidated_payload)} bytes)")

        # Overwrite each file for this language
        for target_file in lang_files[lang]:
            with open(target_file, "wb") as f:
                f.write(consolidated_payload)

        print(f"Updated {len(lang_files[lang])} files for [{lang}] successfully.")

    print("\n--- All subtitle files consolidated successfully! ---")

if __name__ == "__main__":
    consolidate_subtitles()
