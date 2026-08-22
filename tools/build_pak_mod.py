"""
Life is Strange Remastered - Subtitle Pak Builder Mod
------------------------------------------------------
This script builds the UE4 Patch PAK file (pakchunk0-WindowsNoEditor_P.pak)
containing all consolidated .cue subtitle files, forcing Unreal Engine 4
to load the master subtitle dictionaries from the mounted PAK patch.
"""

import os
import glob
import struct
import hashlib
from collections import defaultdict

GAME_DIR = r"C:\Games\Life is Strange Remastered"
ALT_DATA_DIR = os.path.join(GAME_DIR, "LIS", "Content", "AltData")
PAKS_DIR = os.path.join(GAME_DIR, "LIS", "Content", "Paks")
OUTPUT_PAK_NAME = "pakchunk0-WindowsNoEditor_P.pak"
OUTPUT_PAK_PATH = os.path.join(PAKS_DIR, OUTPUT_PAK_NAME)

def create_pak(output_pak_path, file_mapping):
    mount_point = b'../../../\x00'
    entries_info = []
    
    with open(output_pak_path, 'wb') as pak:
        offset = 0
        for rel_path, data in file_mapping:
            size = len(data)
            sha1 = hashlib.sha1(data).digest()
            entry_offset = offset
            
            # Entry header: offset(8), size(8), uncomp_size(8), comp_method(4), hash(20), is_enc(1), block_count(4)
            # Total 53 bytes
            header = struct.pack('<qqqi20sBi', entry_offset, size, size, 0, sha1, 0, 0)
            pak.write(header)
            pak.write(data)
            
            entries_info.append((rel_path, entry_offset, size, sha1))
            offset += len(header) + size
        
        # Build Index
        index_offset = offset
        index_parts = []
        index_parts.append(struct.pack('<i', len(mount_point)))
        index_parts.append(mount_point)
        index_parts.append(struct.pack('<i', len(entries_info)))
        
        for rel_path, entry_offset, size, sha1 in entries_info:
            rel_bytes = rel_path.encode('utf-8') + b'\x00'
            index_parts.append(struct.pack('<i', len(rel_bytes)))
            index_parts.append(rel_bytes)
            index_parts.append(struct.pack('<qqqi20sBi', entry_offset, size, size, 0, sha1, 0, 0))
        
        index_bytes = b''.join(index_parts)
        index_size = len(index_bytes)
        index_sha1 = hashlib.sha1(index_bytes).digest()
        
        pak.write(index_bytes)
        
        # Footer: magic(4), ver(4), idx_off(8), idx_sz(8), idx_hash(20), padding(160)
        footer = struct.pack('<IIQQ20s160s', 0x5A6F12E1, 8, index_offset, index_size, index_sha1, b'\x00'*160)
        pak.write(footer)
        
    print(f'Created {output_pak_path} successfully ({os.path.getsize(output_pak_path) / (1024*1024):.2f} MB).')

def build_mod():
    print(f"Reading consolidated cue files from: {ALT_DATA_DIR}")
    cue_files = glob.glob(os.path.join(ALT_DATA_DIR, "*.cue"))
    print(f"Found {len(cue_files)} .cue files to pack.")
    
    file_mapping = []
    for filepath in cue_files:
        filename = os.path.basename(filepath)
        rel_path = f"LIS/Content/AltData/{filename}"
        with open(filepath, "rb") as f:
            data = f.read()
        file_mapping.append((rel_path, data))
        
    print(f"Building patch pak at: {OUTPUT_PAK_PATH}")
    create_pak(OUTPUT_PAK_PATH, file_mapping)
    
    # Also create in ~mods folder if desired
    mods_dir = os.path.join(PAKS_DIR, "~mods")
    os.makedirs(mods_dir, exist_ok=True)
    mods_pak = os.path.join(mods_dir, "SubtitleFix_P.pak")
    create_pak(mods_pak, file_mapping)
    
    print("\nMod PAK successfully created and deployed in both Paks/ and Paks/~mods/!")

if __name__ == "__main__":
    build_mod()
