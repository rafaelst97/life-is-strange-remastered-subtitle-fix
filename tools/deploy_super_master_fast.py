import json
import time
import os

t0 = time.time()
json_path = r"D:\Projetos\LiS_Remastered_Subtitle_Mod\mod_package\Binaries\Win64\Mods\SubtitleFixMod\Scripts\subtitles_PTB.json"
with open(json_path, "r", encoding="utf-8") as f:
    subs = json.load(f)

expanded = {}
for k, v in subs.items():
    if not k or not v: continue
    expanded[k] = v
    expanded[f"Play_{k}"] = v
    
    clean_k = k
    if k.startswith("Cue_") or k.startswith("Act_"):
        clean_k = k[4:]
        expanded[clean_k] = v
        expanded[f"Play_{clean_k}"] = v
    
    parts = clean_k.split("_")
    if len(parts) >= 3 and parts[0].startswith("E") and len(parts[0]) <= 3:
        no_ep = "_".join(parts[2:])
        if no_ep not in expanded:
            expanded[no_ep] = v
            expanded[f"Play_{no_ep}"] = v
        if len(parts) >= 4:
            action = "_".join(parts[3:])
            if action not in expanded:
                expanded[action] = v
                expanded[f"Play_{action}"] = v
            if parts[-1].isdigit():
                action_no_num = "_".join(parts[3:-1])
                if action_no_num not in expanded:
                    expanded[action_no_num] = v
                    expanded[f"Play_{action_no_num}"] = v

print(f"Generated {len(expanded)} entries in {time.time()-t0:.3f}s.")

# Build binary UTF-16LE buffer
buf = bytearray()
for k, v in expanded.items():
    buf.extend(k.encode("utf-16le") + b"\x00\x00")
    buf.extend(v.encode("utf-16le") + b"\x00\x00")
buf.extend(b"\x00\x00")

binary_data = bytes(buf)
print(f"Master binary buffer size: {len(binary_data)} bytes ({len(binary_data)/(1024*1024):.2f} MB)")

alt_dir = r"C:\Games\Life is Strange Remastered\LIS\Content\AltData"
count = 0
for f in os.listdir(alt_dir):
    if f.endswith(".cue"):
        p = os.path.join(alt_dir, f)
        with open(p, "wb") as fp:
            fp.write(binary_data)
        count += 1

print(f"SUCCESS: Deployed to all {count} .cue files in {time.time()-t0:.2f} seconds total!")

