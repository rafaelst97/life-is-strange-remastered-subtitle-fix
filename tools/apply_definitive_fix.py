import pefile
import capstone
import struct
import os

exe_path = r"C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe"
backup_path = r"D:\Projetos\LiS_Remastered_Subtitle_Mod\backup_Binaries_Win64\LiS-Win64-Shipping.exe"

# Make sure XINPUT1_3.dll is removed
xinput_dll = r"C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\XINPUT1_3.dll"
if os.path.exists(xinput_dll):
    os.remove(xinput_dll)
    print(f"Removed {xinput_dll}")

# Read clean backup
with open(backup_path, "rb") as f:
    exe_data = bytearray(f.read())

pe = pefile.PE(backup_path)
cs = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)

print("=== APPLYING THE DEFINITIVE ENGINE FIX ===")

# --- PATCH 1: In GetSubtitleText (0x14071023d) ---
# Bypass early exit on non-standard cues, always look up in dataset
va_p1 = 0x14071023d
fo_p1 = pe.get_offset_from_rva(va_p1 - pe.OPTIONAL_HEADER.ImageBase)
target_lookup_va = 0x1407103b8
disp_p1 = target_lookup_va - (va_p1 + 5)
patch1_bytes = bytes([0xE9]) + struct.pack('<i', disp_p1) + bytes([0x90])

print(f"\n[Patch 1] At VA={hex(va_p1)}, FileOffset={hex(fo_p1)}")
exe_data[fo_p1 : fo_p1 + len(patch1_bytes)] = patch1_bytes
for ins in cs.disasm(patch1_bytes, va_p1):
    print(f"  0x{ins.address:x}: {ins.bytes.hex():16} {ins.mnemonic:8} {ins.op_str}")

# --- PATCH 2: In FindAltDataSetDirect (0x1406f0ea1) ---
# If TMap index is -1 (layer not found), clamp to 0 (use primary loaded AltDataSet Data[0])
va_p2 = 0x1406f0ea1
fo_p2 = pe.get_offset_from_rva(va_p2 - pe.OPTIONAL_HEADER.ImageBase)
patch2_asm = (
    bytes([0x8B, 0x44, 0x24, 0x20]) +  # mov eax, [rsp + 0x20]
    bytes([0x85, 0xC0]) +              # test eax, eax
    bytes([0x79, 0x02]) +              # jns +2 (to mov [rsp+0x30], eax)
    bytes([0x31, 0xC0]) +              # xor eax, eax (force index 0)
    bytes([0x89, 0x44, 0x24, 0x30]) +  # mov [rsp + 0x30], eax
    bytes([0x90, 0x90])                # 2 NOPs
)

print(f"\n[Patch 2] At VA={hex(va_p2)}, FileOffset={hex(fo_p2)} (len={len(patch2_asm)})")
exe_data[fo_p2 : fo_p2 + len(patch2_asm)] = patch2_asm
for ins in cs.disasm(patch2_asm, va_p2):
    print(f"  0x{ins.address:x}: {ins.bytes.hex():16} {ins.mnemonic:8} {ins.op_str}")

# Save patched executable
with open(exe_path, "wb") as f:
    f.write(exe_data)

print(f"\n[SUCCESS] Wrote definitive patched LiS-Win64-Shipping.exe ({len(exe_data)} bytes)")
