import pefile
import capstone
import struct
import shutil
import os

exe_path = r"C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe"
backup_path = r"D:\Projetos\LiS_Remastered_Subtitle_Mod\backup_Binaries_Win64\LiS-Win64-Shipping.exe"

# Make sure we read from clean original backup
pe = pefile.PE(backup_path)

with open(backup_path, "rb") as f:
    exe_data = bytearray(f.read())

cs = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)

print("=== APPLYING MASTER SUBTITLE ENGINE FIX ===")

# --- PATCH 1: In GetSubtitleText (0x14071023d), force always proceeding to AltDataSet lookup ---
# Original at 0x14071023d: 0F 84 75 01 00 00 (je 0x1407103b8)
# We change to: E9 76 01 00 00 90 (jmp 0x1407103b8; nop)
va_p1 = 0x14071023d
fo_p1 = pe.get_offset_from_rva(va_p1 - pe.OPTIONAL_HEADER.ImageBase)
target_lookup_va = 0x1407103b8
disp_p1 = target_lookup_va - (va_p1 + 5)
patch1_bytes = bytes([0xE9]) + struct.pack('<i', disp_p1) + bytes([0x90])

print(f"\n[Patch 1] At VA={hex(va_p1)}, FileOffset={hex(fo_p1)}")
print(f"Original: {exe_data[fo_p1 : fo_p1 + len(patch1_bytes)].hex()}")
print("New instructions:")
for ins in cs.disasm(patch1_bytes, va_p1):
    print(f"  0x{ins.address:x}: {ins.bytes.hex():16} {ins.mnemonic:8} {ins.op_str}")

exe_data[fo_p1 : fo_p1 + len(patch1_bytes)] = patch1_bytes


# --- PATCH 2: In FindAltDataSetByLayerName (0x140718a31), fallback to AltDataSet[0] ---
# If requested LayerName is not in memory, return Data[0] (which contains all consolidated subtitles)
va_p2 = 0x140718a31
fo_p2 = pe.get_offset_from_rva(va_p2 - pe.OPTIONAL_HEADER.ImageBase)
target_ret_va = 0x140719cd4
disp2_1 = target_ret_va - (va_p2 + 14 + 5)
disp2_2 = target_ret_va - (va_p2 + 21 + 5)

patch2_bytes = (
    bytes([0x48, 0x8B, 0x44, 0x24, 0x48]) +       # mov rax, [rsp + 0x48] (TArray ptr)
    bytes([0x83, 0x78, 0x08, 0x00]) +             # cmp dword ptr [rax + 8], 0 (count > 0)
    bytes([0x7E, 0x0A]) +                         # jle +10 (to va_p2 + 21)
    bytes([0x48, 0x8B, 0x00]) +                   # mov rax, [rax] (first element Data[0])
    bytes([0xE9]) + struct.pack('<i', disp2_1) +  # jmp target_ret_va
    bytes([0x31, 0xC0]) +                         # xor eax, eax
    bytes([0xE9]) + struct.pack('<i', disp2_2)    # jmp target_ret_va
)

print(f"\n[Patch 2] At VA={hex(va_p2)}, FileOffset={hex(fo_p2)}")
print(f"Original: {exe_data[fo_p2 : fo_p2 + len(patch2_bytes)].hex()}")
print("New instructions:")
for ins in cs.disasm(patch2_bytes, va_p2):
    print(f"  0x{ins.address:x}: {ins.bytes.hex():16} {ins.mnemonic:8} {ins.op_str}")

exe_data[fo_p2 : fo_p2 + len(patch2_bytes)] = patch2_bytes

# Write patched executable
with open(exe_path, "wb") as f:
    f.write(exe_data)

print(f"\n[SUCCESS] Wrote fully patched binary to {exe_path} ({len(exe_data)} bytes)")
