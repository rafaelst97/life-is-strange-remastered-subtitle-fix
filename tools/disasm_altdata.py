import pefile
import capstone
import struct

exe_path = r"C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe"
pe = pefile.PE(exe_path)

with open(exe_path, 'rb') as f:
    data = f.read()

image_base = pe.OPTIONAL_HEADER.ImageBase
print(f"ImageBase: {hex(image_base)}")

code_section = None
for s in pe.sections:
    name = s.Name.decode().strip('\x00')
    if name == '.text':
        code_section = s
        break

cs = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
cs.detail = True

strings = [
    'DNEAltData: LayerName for Cue %s was not found',
    'DNEAltData: AltDataSet for Cue %s with LayerName %s was not found',
    'Failed to find Cue AltData file: %s',
    'AltData/%s_%s_%s.%s'
]

text_data = code_section.get_data()
text_rva = code_section.VirtualAddress
text_va = image_base + text_rva

for s in strings:
    wide = s.encode('utf-16-le')
    pos = data.find(wide)
    if pos != -1:
        rva = pe.get_rva_from_offset(pos)
        va = image_base + rva
        print(f"\nString: '{s[:40]}' at Offset={hex(pos)}, VA={hex(va)}")
        
        # Search for rip-relative references in .text
        for ins in cs.disasm(text_data, text_va):
            for op in ins.operands:
                if op.type == capstone.x86.X86_OP_MEM and op.mem.base == capstone.x86.X86_REG_RIP:
                    target = ins.address + ins.size + op.mem.disp
                    if abs(target - va) < 16:
                        print(f"  -> Found XREF at {hex(ins.address)}: {ins.mnemonic} {ins.op_str}")
                        # Print 40 instructions around this
                        start_va = max(text_va, ins.address - 80)
                        sub_bytes = text_data[start_va - text_va : ins.address - text_va + 120]
                        print("  --- Disassembly Window ---")
                        for sub_ins in cs.disasm(sub_bytes, start_va):
                            mark = " >>> " if sub_ins.address == ins.address else "     "
                            print(f"{mark}{hex(sub_ins.address)}: {sub_ins.mnemonic} {sub_ins.op_str}")
                        print("  --------------------------")
