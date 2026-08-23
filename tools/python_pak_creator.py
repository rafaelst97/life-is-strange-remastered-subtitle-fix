import struct
import hashlib
import os

def write_fstring(stream, text):
    encoded = text.encode("utf-8") + b"\x00"
    stream.write(struct.pack("<i", len(encoded)))
    stream.write(encoded)

def create_pak(files_dict, output_pak_path, mount_point="../../../"):
    # files_dict: { "LiS/Content/AltData/CU_E5_3B_PTB.cue": byte_data, ... }
    pak = open(output_pak_path, "wb+")
    
    entries = []
    for rel_path, data in files_dict.items():
        file_offset = pak.tell()
        file_size = len(data)
        file_sha1 = hashlib.sha1(data).digest()
        
        # Write FPakEntry (Header before data: 56 bytes for V8)
        entry_header = struct.pack("<qqqi", file_offset, file_size, file_size, 0)
        entry_header += file_sha1
        entry_header += struct.pack("<ib", 0, 0) # 0 blocks, 0 flags
        
        pak.write(entry_header)
        pak.write(data)
        
        entries.append((rel_path, file_offset, file_size, file_sha1))
    
    index_offset = pak.tell()
    
    # 1. Mount point
    write_fstring(pak, mount_point)
    # 2. File count
    pak.write(struct.pack("<i", len(entries)))
    
    # 3. Entries
    for rel_path, file_offset, file_size, file_sha1 in entries:
        write_fstring(pak, rel_path)
        entry_bytes = struct.pack("<qqqi", file_offset, file_size, file_size, 0)
        entry_bytes += file_sha1
        entry_bytes += struct.pack("<ib", 0, 0)
        pak.write(entry_bytes)
        
    index_size = pak.tell() - index_offset
    
    # Calculate Index SHA1
    pak.seek(index_offset)
    index_bytes = pak.read(index_size)
    index_sha1 = hashlib.sha1(index_bytes).digest()
    
    # Write Footer (204 bytes):
    pak.seek(0, 2)
    footer = struct.pack("<IIqq", 0x5A6F12E1, 8, index_offset, index_size)
    footer += index_sha1
    footer += b"\x00" # Not encrypted
    footer += b"\x00" * 16 # Encryption GUID
    footer += b"\x00" * (204 - len(footer)) # Pad to 204 bytes
    
    pak.write(footer)
    pak.close()
    print(f"PAK created successfully: {output_pak_path} ({os.path.getsize(output_pak_path)} bytes, {len(entries)} files).")

# Prepare files
json_path = r"D:\Projetos\LiS_Remastered_Subtitle_Mod\mod_package\Binaries\Win64\Mods\SubtitleFixMod\Scripts\subtitles_PTB.json"
import json
with open(json_path, "r", encoding="utf-8") as f:
    subs = json.load(f)

buf = bytearray()
for k, v in subs.items():
    buf.extend(k.encode("utf-16le") + b"\x00\x00")
    buf.extend(v.encode("utf-16le") + b"\x00\x00")
buf.extend(b"\x00\x00")

# Collect all scene files
files_to_pack = {}
alt_dir = r"C:\Games\Life is Strange Remastered\LIS\Content\AltData"
for f in os.listdir(alt_dir):
    if f.endswith(".cue"):
        files_to_pack[f"LiS/Content/AltData/{f}"] = bytes(buf)

out_pak = r"C:\Games\Life is Strange Remastered\LIS\Content\Paks\pakchunk99-WindowsNoEditor_P.pak"
create_pak(files_to_pack, out_pak)

