import pefile
import capstone
import struct
import shutil
import os

exe_path = r"C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe"
backup_path = r"D:\Projetos\LiS_Remastered_Subtitle_Mod\backup_Binaries_Win64\LiS-Win64-Shipping.exe"

# Make sure backup exists
if not os.path.exists(backup_path):
    shutil.copy2(exe_path, backup_path)
    print(f"Created backup at {backup_path}")
else:
    print(f"Backup already exists at {backup_path}")

pe = pefile.PE(backup_path)
fo = pe.get_offset_from_rva(0x718a31)
patch_va = 0x140718a31
target_ret_va = 0x140719cd4

print(f"Patch location: VA={hex(patch_va)}, FileOffset={hex(fo)}")

# Compute jump displacement:
# At 0x140718a3f: jmp 0x140719cd4 (ins_len = 5) -> disp = 0x140719cd4 - (0x140718a3f + 5) = 0x1290
# At 0x140718a46: jmp 0x140719cd4 (ins_len = 5) -> disp = 0x140719cd4 - (0x140718a46 + 5) = 0x1289

disp1 = target_ret_va - (patch_va + 14 + 5)
disp2 = target_ret_va - (patch_va + 21 + 5)

patch_bytes = (
    bytes([0x48, 0x8B, 0x44, 0x24, 0x48]) +       # 140718a31: mov rax, [rsp + 0x48] (TArray ptr)
    bytes([0x83, 0x78, 0x08, 0x00]) +             # 140718a36: cmp dword ptr [rax + 8], 0 (count > 0)
    bytes([0x7E, 0x0A]) +                         # 140718a3a: jle +10 (to 140718a46)
    bytes([0x48, 0x8B, 0x00]) +                   # 140718a3c: mov rax, [rax] (first element Data[0])
    bytes([0xE9]) + struct.pack('<i', disp1) +    # 140718a3f: jmp 0x140719cd4
    bytes([0x31, 0xC0]) +                         # 140718a44: xor eax, eax
    bytes([0xE9]) + struct.pack('<i', disp2)      # 140718a46: jmp 0x140719cd4
)

print(f"Patch size: {len(patch_bytes)} bytes")

cs = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
print("\nDisassembly of patch:")
for ins in cs.disasm(patch_bytes, patch_va):
    print(f"0x{ins.address:x}: {ins.bytes.hex():18} {ins.mnemonic:8} {ins.op_str}")

# Read original binary from backup
with open(backup_path, "rb") as f:
    exe_data = bytearray(f.read())

# Verify original bytes at target location
orig_at_target = exe_data[fo : fo + len(patch_bytes)]
print(f"\nOriginal bytes at target: {orig_at_target.hex()}")

# Apply patch
exe_data[fo : fo + len(patch_bytes)] = patch_bytes

# Write patched binary
with open(exe_path, "wb") as f:
    f.write(exe_data)

print(f"\nSuccessfully patched {exe_path}!")

