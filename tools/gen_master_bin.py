import json
import os
import struct

mod_dir = r"D:\Projetos\LiS_Remastered_Subtitle_Mod"
json_path = os.path.join(mod_dir, "mod_package", "Binaries", "Win64", "Mods", "SubtitleFixMod", "Scripts", "subtitles_PTB.json")

with open(json_path, "r", encoding="utf-8") as f:
    subtitles = json.load(f)

print(f"Loaded {len(subtitles)} subtitle entries from JSON.")

# Build continuous UTF-16LE binary buffer: Key\0Value\0Key\0Value\0...
out_bytes = bytearray()
total_chars = 0

for key, val in subtitles.items():
    # Key as UTF-16LE with null terminator
    k_bytes = (key + "\x00").encode("utf-16-le")
    # Value as UTF-16LE with null terminator
    v_bytes = (val + "\x00").encode("utf-16-le")
    out_bytes.extend(k_bytes)
    out_bytes.extend(v_bytes)
    total_chars += len(key) + 1 + len(val) + 1

# Add double null terminator
out_bytes.extend("\x00\x00".encode("utf-16-le"))
total_chars += 2

bin_path = os.path.join(mod_dir, "src", "master_subtitles_utf16.bin")
with open(bin_path, "wb") as f:
    f.write(out_bytes)

print(f"Generated {bin_path}: {len(out_bytes)} bytes ({total_chars} wchar_t characters).")

# Also generate a C++ header with the binary data embedded directly!
h_path = os.path.join(mod_dir, "src", "subtitles_data.h")
with open(h_path, "w", encoding="utf-8") as f:
    f.write("// Auto-generated embedded subtitle database (UTF-16LE)\n")
    f.write(f"// Total entries: {len(subtitles)}, Total wchar_t: {total_chars}\n\n")
    f.write("#pragma once\n#include <cstdint>\n\n")
    f.write(f"const size_t g_MasterSubtitleCharCount = {total_chars};\n")
    f.write(f"const size_t g_MasterSubtitleByteSize = {len(out_bytes)};\n\n")
    f.write("alignas(2) const unsigned char g_MasterSubtitleData[] = {\n")
    for i in range(0, len(out_bytes), 32):
        chunk = out_bytes[i:i+32]
        hex_str = ", ".join(f"0x{b:02x}" for b in chunk)
        f.write(f"    {hex_str},\n")
    f.write("};\n")

print(f"Generated embedded C++ header {h_path} ({os.path.getsize(h_path)} bytes).")

