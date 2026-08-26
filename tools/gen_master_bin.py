import os
import re

mod_dir = r"D:\Projetos\LiS_Remastered_Subtitle_Mod"
h_path = os.path.join(mod_dir, "src", "subtitles_data.h")

# The source of truth is the embedded C++ header (generated from the
# alias-expanded master database). Extract the raw UTF-16LE blob from it and
# write the matching .bin so both stay in sync.
with open(h_path, "r", encoding="utf-8", errors="ignore") as f:
    header = f.read()

hex_tokens = re.findall(r"0x([0-9a-fA-F]{2})", header)
out_bytes = bytes(int(x, 16) for x in hex_tokens)

bin_path = os.path.join(mod_dir, "src", "master_subtitles_utf16.bin")
with open(bin_path, "wb") as f:
    f.write(out_bytes)

print(f"Extracted {len(out_bytes)} bytes from {h_path}")
print(f"Generated {bin_path}")
