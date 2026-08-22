import pefile
import capstone
import struct

exe_path = r"C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe"
pe = pefile.PE(exe_path)
with open(exe_path, 'rb') as f:
    data = f.read()

image_base = pe.OPTIONAL_HEADER.ImageBase
text_sec = [s for s in pe.sections if s.Name.decode().strip('\x00') == '.text'][0]
text_data = text_sec.get_data()
text_va = image_base + text_sec.VirtualAddress

cs = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)

# Find all wide occurrences of DNEAltData
needle = 'DNEAltData'.encode('utf-16-le')
pos = 0
str_vas = []
while True:
    idx = data.find(needle, pos)
    if idx == -1: break
    str_va = image_base + pe.get_rva_from_offset(idx)
    str_text = data[idx:idx+120].decode('utf-16-le', errors='ignore').split('\x00')[0]
    print(f"String at VA {hex(str_va)}: '{str_text}'")
    str_vas.append((str_va, str_text))
    pos = idx + len(needle)

# Fast vectorized search using memoryview/c_types or direct block scanning
import array
# Convert text_data to array of uint32
disp_vals = [s[0] for s in str_vas]

print("\nScanning .text section for references...")
for idx_str, (sva, stext) in enumerate(str_vas):
    # We want: text_va + i + ins_len + disp32 == sva
    # For LEA rdx, [rip+disp32] (48 8d 15 xx xx xx xx, len=7)
    # disp32 = sva - text_va - i - 7
    # i + disp32 = sva - text_va - 7 = CONSTANT C!
    # That means for any instruction at offset i, its disp32 must equal C - i!
    # Let's check each instruction starting with 48 8d / 4c 8d / 48 8b / 4c 8b
    C = sva - text_va - 7
    # Check if there is an LEA
    for reg_op in [b'\x48\x8d\x15', b'\x48\x8d\x0d', b'\x4c\x8d\x05', b'\x4c\x8d\x0d', b'\x48\x8d\x1d', b'\x48\x8b\x05', b'\x48\x8b\x0d']:
        start = 0
        while True:
            i = text_data.find(reg_op, start)
            if i == -1: break
            disp = struct.unpack('<i', text_data[i+3:i+7])[0]
            if disp == C - i or disp == C - i + 1 or disp == C - i - 1:
                ins_va = text_va + i
                print(f"\n>>> FOUND XREF to '{stext[:30]}' at VA={hex(ins_va)} (FileOffset={hex(text_sec.PointerToRawData + i)})")
                dis_start = max(0, i - 100)
                dis_bytes = text_data[dis_start : i + 150]
                for ins in cs.disasm(dis_bytes, text_va + dis_start):
                    mark = " >>> " if ins.address == ins_va else "     "
                    print(f"{mark}{hex(ins.address)}: {ins.mnemonic:8} {ins.op_str}")
            start = i + 1

