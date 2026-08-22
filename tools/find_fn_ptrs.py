import pefile
import struct

exe_path = r"C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe"
pe = pefile.PE(exe_path)

image_base = pe.OPTIONAL_HEADER.ImageBase
rva_name = 0x2afcba0
va_name = image_base + rva_name

print(f"VA of SetSubtitleCue string: {hex(va_name)}")

for s in pe.sections:
    sec_data = s.get_data()
    sec_va = image_base + s.VirtualAddress
    name = s.Name.decode(errors='ignore').strip('\x00')
    for i in range(0, len(sec_data) - 8, 8):
        ptr = struct.unpack('<Q', sec_data[i:i+8])[0]
        if ptr == va_name:
            print(f"Found pointer to SetSubtitleCue in section {name} at VA={hex(sec_va + i)}")
            # Show 10 QWORDs around this struct
            for j in range(-3, 8):
                idx = i + j*8
                if 0 <= idx < len(sec_data) - 8:
                    val = struct.unpack('<Q', sec_data[idx:idx+8])[0]
                    print(f"  [{j:+2d}] VA={hex(sec_va + idx)}: {hex(val)}")
