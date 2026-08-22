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
text_fo = text_sec.PointerToRawData

cs = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)

# Disassemble from 0x14070ff00 to 0x140710700
start_va = 0x14070ff00
end_va = 0x140710700
start_offset = start_va - text_va

chunk = text_data[start_offset : end_va - text_va]
print(f"Disassembly of Subtitle Lookup Function ({hex(start_va)} - {hex(end_va)}):")

for ins in cs.disasm(chunk, start_va):
    print(f"0x{ins.address:x}: {ins.bytes.hex():24} {ins.mnemonic:8} {ins.op_str}")

