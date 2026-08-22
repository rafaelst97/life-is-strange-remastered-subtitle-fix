import pefile
import capstone
import struct

exe_path = r"C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe"
pe = pefile.PE(exe_path)

with open(exe_path, 'rb') as f:
    data = f.read()

image_base = pe.OPTIONAL_HEADER.ImageBase

code_section = None
for s in pe.sections:
    name = s.Name.decode().strip('\x00')
    if name == '.text':
        code_section = s
        break

text_data = code_section.get_data()
text_rva = code_section.VirtualAddress
text_va = image_base + text_rva
text_file_offset = code_section.PointerToRawData

strings = [
    'DNEAltData: LayerName for Cue %s was not found',
    'DNEAltData: AltDataSet for Cue %s with LayerName %s was not found',
    'Failed to find Cue AltData file: %s',
    'AltData/%s_%s_%s.%s'
]

cs = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)

for s in strings:
    wide = s.encode('utf-16-le')
    pos = data.find(wide)
    if pos != -1:
        str_rva = pe.get_rva_from_offset(pos)
        str_va = image_base + str_rva
        print(f"\n--- Target String: '{s[:40]}' (VA={hex(str_va)}) ---")
        
        # Search .text for any 7-byte instruction (like 48 8d ?? [disp32])
        # where (ins_va + ins_len + disp32) == str_va
        for i in range(len(text_data) - 7):
            b0, b1 = text_data[i], text_data[i+1]
            # Common LEA / MOV: 48 8d (lea), 4c 8d (lea), 48 8b (mov), 4c 8b (mov)
            if b0 in (0x48, 0x4c) and b1 in (0x8d, 0x8b):
                ins_rva = text_rva + i
                ins_va = image_base + ins_rva
                ins_len = 7
                disp = struct.unpack('<i', text_data[i+3:i+7])[0]
                target = ins_va + ins_len + disp
                if target == str_va:
                    print(f"Found match at FileOffset={hex(text_file_offset + i)}, VA={hex(ins_va)}")
                    # Disassemble 100 bytes around it
                    dis_start = max(0, i - 80)
                    dis_bytes = text_data[dis_start : i + 120]
                    for ins in cs.disasm(dis_bytes, text_va + dis_start):
                        mark = " >>> " if ins.address == ins_va else "     "
                        print(f"{mark}{hex(ins.address)}: {ins.mnemonic:8} {ins.op_str}")
