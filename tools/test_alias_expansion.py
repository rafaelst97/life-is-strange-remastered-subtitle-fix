import json
import os

json_path = r"D:\Projetos\LiS_Remastered_Subtitle_Mod\mod_package\Binaries\Win64\Mods\SubtitleFixMod\Scripts\subtitles_PTB.json"
with open(json_path, "r", encoding="utf-8") as f:
    subs = json.load(f)

print(f"Original base cues: {len(subs)}")

# Create expanded dictionary with all alias variants
expanded = {}
for k, v in subs.items():
    if not k or not v: continue
    expanded[k] = v
    
    # 1. Play_ prefix
    expanded[f"Play_{k}"] = v
    
    # 2. Stripped Cue_ or Act_ prefix
    if k.startswith("Cue_"):
        stripped = k[4:]
        expanded[stripped] = v
        expanded[f"Play_{stripped}"] = v
    elif k.startswith("Act_"):
        stripped = k[4:]
        expanded[stripped] = v
        expanded[f"Play_{stripped}"] = v
        
    # 3. Short action tokens (e.g. E5_3B_ArtGallery_PhotoLook_Max_060 -> PhotoLook_Max, PhotoLook_Max_060)
    parts = k.split("_")
    if len(parts) >= 4:
        # e.g., ["Cue", "E5", "3B", "ArtGallery", "PhotoLook", "Max", "060"]
        # action name: PhotoLook_Max
        for i in range(len(parts)):
            for j in range(i+2, len(parts)+1):
                sub_token = "_".join(parts[i:j])
                if len(sub_token) >= 6 and not sub_token.startswith("E") and not sub_token.isdigit():
                    if sub_token not in expanded:
                        expanded[sub_token] = v

print(f"Total expanded aliases: {len(expanded)}")

# Check key test cases
test_keys = [
    "Cue_E5_3B_ArtGallery_PhotoLook_Max_060",
    "Play_Cue_E5_3B_ArtGallery_PhotoLook_Max_060",
    "PhotoLook_Max",
    "PhotoLook_Max_060",
    "ArtGallery_PhotoLook_Max",
    "ArtGallery_PhotoLook_Admirer1",
    "PhotoLook_Admirer1"
]

for tk in test_keys:
    print(f"  {tk} -> {expanded.get(tk, '[NOT FOUND]')}")

