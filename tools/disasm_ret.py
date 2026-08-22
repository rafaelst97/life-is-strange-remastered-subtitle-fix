import pefile, capstone

pe = pefile.PE("LIS/Binaries/Win64/LiS-Win64-Shipping.exe")
fo = pe.get_offset_from_rva(0x718a00)
with open("LIS/Binaries/Win64/LiS-Win64-Shipping.exe", "rb") as f:
    f.seek(fo)
    chunk = f.read(150)

cs = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
for ins in cs.disasm(chunk, 0x140718a00):
    print(f"0x{ins.address:x}: {ins.bytes.hex():24} {ins.mnemonic:8} {ins.op_str}")
