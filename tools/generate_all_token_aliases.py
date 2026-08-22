import os
import json
import re

alt_dir = r"C:\Games\Life is Strange Remastered\LIS\Content\AltData"
json_path = r"D:\Projetos\LiS_Remastered_Subtitle_Mod\mod_package\Binaries\Win64\Mods\SubtitleFixMod\Scripts\subtitles_PTB.json"

with open(json_path, "r", encoding="utf-8") as f:
    subs = json.load(f)

# Read master Portuguese .cue binary
sample_ptb = os.path.join(alt_dir, "CU_E1_1A_PTB.cue")
with open(sample_ptb, "rb") as f:
    master_data = f.read()

# Extract every possible layer token from all cue names
tokens = set()
for cue in subs.keys():
    # Split by underscore
    parts = cue.split("_")
    # Add combinations: E5_3B, ArtGallery, E5_3B_ArtGallery, etc.
    if len(parts) >= 3:
        tokens.add(f"{parts[1]}_{parts[2]}") # E5_3B
        tokens.add(parts[1])                # E5
        tokens.add(parts[2])                # 3B
    if len(parts) >= 4:
        tokens.add(parts[3])                # ArtGallery
        tokens.add(f"{parts[1]}_{parts[2]}_{parts[3]}") # E5_3B_ArtGallery
        tokens.add(f"{parts[1]}_{parts[3]}")            # E5_ArtGallery
    if len(parts) >= 5:
        tokens.add(parts[4])                # PhotoLook
        tokens.add(f"{parts[3]}_{parts[4]}")# ArtGallery_PhotoLook

print(f"Extracted {len(tokens)} unique level/scene/layer tokens from 10,475 cues.")

created = 0
for tok in tokens:
    if not tok or len(tok) < 2: continue
    for lang in ["PTB", "INT", "pt-BR", "pt_BR", "POR", "BRA", "default", "DEU", "FRA", "ESM", "ESN", "ITA"]:
        fname = f"CU_{tok}_{lang}.cue"
        fpath = os.path.join(alt_dir, fname)
        if not os.path.exists(fpath):
            try:
                with open(fpath, "wb") as f:
                    f.write(master_data)
                created += 1
            except Exception:
                pass

print(f"Created {created} comprehensive token alias .cue files in AltData.")
total_cue = len([f for f in os.listdir(alt_dir) if f.endswith('.cue')])
print(f"Total .cue files in AltData now: {total_cue}")
