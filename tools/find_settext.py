import pefile
import capstone
import struct

exe_path = r"C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe"
pe = pefile.PE(exe_path)

with open(exe_path, "rb") as f:
    data = f.read()

image_base = pe.OPTIONAL_HEADER.ImageBase

# Search for SetText string in FName / UFunction tables
needle = b'SetText'
pos = 0
matches = []
while True:
    idx = data.find(needle, pos)
    if idx == -1: break
    matches.append(idx)
    pos = idx + len(needle)

print(f"Found {len(matches)} occurrences of SetText:")
for m in matches:
    rva = pe.get_rva_from_offset(m)
    ctx = data[max(0, m-20):m+40]
    readable = ''.join(chr(b) if 32 <= b < 127 else '.' for b in ctx)
    print(f"  RVA 0x{rva:x}: {readable}")

