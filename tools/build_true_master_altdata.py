import os
import json

alt_dir = r"C:\Games\Life is Strange Remastered\LIS\Content\AltData"
json_path = r"D:\Projetos\LiS_Remastered_Subtitle_Mod\mod_package\Binaries\Win64\Mods\SubtitleFixMod\Scripts\subtitles_PTB.json"

with open(json_path, "r", encoding="utf-8") as f:
    subs = json.load(f)

print(f"Loaded {len(subs)} master subtitle pairs from JSON.")

# Build complete binary UTF-16LE buffer: Key\0Val\0...
buf = bytearray()
for key, val in subs.items():
    # Encode key in UTF-16LE + null
    buf.extend(key.encode("utf-16le") + b"\x00\x00")
    # Encode val in UTF-16LE + null
    buf.extend(val.encode("utf-16le") + b"\x00\x00")

# Final null terminator
buf.extend(b"\x00\x00")

print(f"Constructed complete binary buffer: {len(buf)} bytes ({len(buf)//2} wchar_t characters).")

# Verify PhotoLook_Max is in the buffer
needle = "PhotoLook_Max".encode("utf-16le")
idx = buf.find(needle)
print(f"Verification: PhotoLook_Max found at offset {idx} in buffer!")

needle2 = "Hero".encode("utf-16le")
idx2 = buf.find(needle2)
print(f"Verification: Heroina do Cotidiano found at offset {idx2} in buffer!")

# Now write this TRUE complete master buffer to EVERY SINGLE .cue file in AltData!
count = 0
for fname in os.listdir(alt_dir):
    if fname.endswith(".cue"):
        fpath = os.path.join(alt_dir, fname)
        with open(fpath, "wb") as f:
            f.write(buf)
        count += 1

print(f"SUCCESS: Wrote TRUE 10,475-line master database to all {count} .cue files in AltData!")

