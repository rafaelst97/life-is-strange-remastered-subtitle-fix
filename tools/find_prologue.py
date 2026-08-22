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

# Disassemble backwards from 0x140710100 (e.g. 0x14070fe00 to 0x140710120)
start_va = 0x14070fd00
end_va = 0x140710120
chunk = text_data[start_va - text_va : end_va - text_va]

print("Searching for function prologue before 0x140710100:")
for ins in cs.disasm(chunk, start_va):
    if ins.mnemonic in ('sub', 'push') and 'rsp' in ins.op_str:
        print(f"--> PROLOGUE CANDIDATE: 0x{ins.address:x} (RVA 0x{ins.address - image_base:x}): {ins.mnemonic} {ins.op_str}")

