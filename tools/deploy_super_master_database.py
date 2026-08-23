import json
import os

json_path = r"D:\Projetos\LiS_Remastered_Subtitle_Mod\mod_package\Binaries\Win64\Mods\SubtitleFixMod\Scripts\subtitles_PTB.json"
with open(json_path, "r", encoding="utf-8") as f:
    subs = json.load(f)

print(f"Loading {len(subs)} base cues...")

expanded = {}
for k, v in subs.items():
    if not k or not v: continue
    expanded[k] = v
    expanded[f"Play_{k}"] = v
    
    if k.startswith("Cue_") or k.startswith("Act_"):
        stripped = k[4:]
        expanded[stripped] = v
        expanded[f"Play_{stripped}"] = v
        
    parts = k.split("_")
    if len(parts) >= 4:
        for i in range(len(parts)):
            for j in range(i+2, len(parts)+1):
                sub_token = "_".join(parts[i:j])
                if len(sub_token) >= 6 and not sub_token.startswith("E") and not sub_token.isdigit():
                    if sub_token not in expanded:
                        expanded[sub_token] = v

print(f"Total expanded entries: {len(expanded)}")

# Build binary buffer
buf = bytearray()
for k, v in expanded.items():
    buf.extend(k.encode("utf-16le") + b"\x00\x00")
    buf.extend(v.encode("utf-16le") + b"\x00\x00")
buf.extend(b"\x00\x00")

binary_data = bytes(buf)
print(f"Master binary database size: {len(binary_data)} bytes ({len(binary_data)/(1024*1024):.2f} MB)")

alt_dir = r"C:\Games\Life is Strange Remastered\LIS\Content\AltData"
count = 0
for f in os.listdir(alt_dir):
    if f.endswith(".cue"):
        p = os.path.join(alt_dir, f)
        with open(p, "wb") as fp:
            fp.write(binary_data)
        count += 1

print(f"SUCCESS: Synchronized {count} .cue files with the expanded {len(expanded)}-entry database!")

