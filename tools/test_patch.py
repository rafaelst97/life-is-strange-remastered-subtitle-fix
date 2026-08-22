import pefile
import capstone
import struct

exe_path = r"C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe"
pe = pefile.PE(exe_path)

with open(exe_path, "rb") as f:
    orig_bytes = f.read()

# Address to patch: 0x140718a31
patch_va = 0x140718a31
target_ret_va = 0x140719cd4
fo = pe.get_offset_from_rva(0x718a31)

cs = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)

# Original instructions at 0x140718a31:
# 0x140718a31: 48 8d 84 24 c8 02 00 00  lea rax, [rsp + 0x2c8]
# 0x140718a39: 48 89 84 24 c0 01 00 00  mov qword ptr [rsp + 0x1c0], rax
# ...

# We want our patch:
# 140718a31: 48 8b 44 24 48              mov rax, [rsp + 0x48]
# 140718a36: 83 78 08 00                 cmp dword ptr [rax + 8], 0
# 140718a3a: 7e 0a                       jle +10 (to 140718a46)
# 140718a3c: 48 8b 00                    mov rax, [rax]
# 140718a3f: e9 90 12 00 00              jmp 140719cd4 (rel = 140719cd4 - (140718a3f + 5) = 140719cd4 - 140718a44 = 0x1290)
# 140718a44: 90 90                       nop nop (to align)
# 140718a46: (original code continues for not-found null return)

rel_disp = target_ret_va - (patch_va + 14 + 5) # 0x140719cd4 - 0x140718a44 = 0x1290
print(f"Computed relative jump displacement: {hex(rel_disp)}")

patch_code = bytes([
    0x48, 0x8B, 0x44, 0x24, 0x48,        # mov rax, [rsp + 0x48] (TArray ptr)
    0x83, 0x78, 0x08, 0x00,              # cmp dword ptr [rax + 8], 0 (count > 0)
    0x7E, 0x0A,                          # jle +10 (to patch_va + 21 = 0x140718a46)
    0x48, 0x8B, 0x00,                    # mov rax, [rax] (first element Data[0])
    0xE9,                                # jmp target_ret_va
]) + struct.pack('<i', rel_disp) + bytes([0x90, 0x90]) # nop nop

print(f"Patch bytes length: {len(patch_code)}")
print("Disassembled patch code:")
for ins in cs.disasm(patch_code, patch_va):
    print(f"0x{ins.address:x}: {ins.bytes.hex():20} {ins.mnemonic:8} {ins.op_str}")

