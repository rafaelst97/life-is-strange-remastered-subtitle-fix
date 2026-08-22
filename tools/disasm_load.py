import pefile
import capstone

exe_path = r"C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe"
pe = pefile.PE(exe_path)
with open(exe_path, "rb") as f:
    data = f.read()

image_base = pe.OPTIONAL_HEADER.ImageBase
text_sec = [s for s in pe.sections if s.Name.decode().strip('\x00') == '.text'][0]
text_data = text_sec.get_data()
text_va = image_base + text_sec.VirtualAddress

cs = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)

# Disassemble function around 0x140719600
start_va = 0x140719600
end_va = 0x140719a50
chunk = text_data[start_va - text_va : end_va - text_va]

print(f"Disassembly of AltData Load Function ({hex(start_va)} - {hex(end_va)}):")
for ins in cs.disasm(chunk, start_va):
    print(f"0x{ins.address:x}: {ins.bytes.hex():24} {ins.mnemonic:8} {ins.op_str}")

