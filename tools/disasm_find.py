import pefile
import capstone

exe_path = r"C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe"
pe = pefile.PE(exe_path)
with open(exe_path, 'rb') as f:
    data = f.read()

image_base = pe.OPTIONAL_HEADER.ImageBase
text_sec = [s for s in pe.sections if s.Name.decode().strip('\x00') == '.text'][0]
text_data = text_sec.get_data()
text_va = image_base + text_sec.VirtualAddress

cs = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)

target_va = 0x1407188a0
offset = target_va - text_va
chunk = text_data[offset : offset + 200]

print(f"Disassembly of FindAltDataSetByLayerName (0x1407188a0):")
for ins in cs.disasm(chunk, target_va):
    print(f"0x{ins.address:x}: {ins.bytes.hex():24} {ins.mnemonic:8} {ins.op_str}")

