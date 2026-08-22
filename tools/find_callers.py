import pefile
import capstone
import struct

exe_path = r"C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe"
pe = pefile.PE(exe_path)

with open(exe_path, "rb") as f:
    data = f.read()

image_base = pe.OPTIONAL_HEADER.ImageBase
text_sec = [s for s in pe.sections if s.Name.decode().strip('\x00') == '.text'][0]
text_data = text_sec.get_data()
text_va = image_base + text_sec.VirtualAddress
text_fo = text_sec.PointerToRawData

target_va = 0x140710100
target_rva = target_va - image_base

cs = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)

print(f"Finding all CALL instructions to 0x{target_va:x} (RVA 0x{target_rva:x})...")

# In x64: E8 [disp32] where ins_va + 5 + disp32 == target_va
# disp32 = target_va - ins_va - 5
# ins_offset = ins_va - text_va
# disp32 = target_va - (text_va + i) - 5

for i in range(len(text_data) - 5):
    if text_data[i] == 0xE8:
        disp = struct.unpack('<i', text_data[i+1:i+5])[0]
        ins_va = text_va + i
        if ins_va + 5 + disp == target_va:
            print(f"\n>>> Found CALL at VA=0x{ins_va:x} (FileOffset=0x{text_fo + i:x})")
            # Disassemble 50 bytes before and 30 bytes after
            start_i = max(0, i - 50)
            chunk = text_data[start_i : i + 30]
            for ins in cs.disasm(chunk, text_va + start_i):
                mark = " >>> " if ins.address == ins_va else "     "
                print(f"{mark}0x{ins.address:x}: {ins.bytes.hex():20} {ins.mnemonic:8} {ins.op_str}")

