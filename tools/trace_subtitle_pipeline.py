import pefile
import capstone
import struct
import re

exe_path = r"C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe"
pe = pefile.PE(exe_path)

with open(exe_path, "rb") as f:
    data = f.read()

image_base = pe.OPTIONAL_HEADER.ImageBase
text_sec = [s for s in pe.sections if s.Name.decode().strip('\x00') == '.text'][0]
text_data = text_sec.get_data()
text_va = image_base + text_sec.VirtualAddress

cs = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)

# 1. Search for all occurrences of property names
props = [
    b'CurrentTextSubtitle',
    b'CurrentSubtitleCue',
    b'SetSubtitleCue',
    b'UpdateSubtitle',
    b'UpdateSubtitles',
    b'WidgetSubtitles',
    b'ClearSubtitles',
    b'SetText',
    b'D9TextBlock'
]

print("=== SEARCHING PROPERTY / FUNCTION NAMES IN BINARY ===")
for p in props:
    pos = 0
    matches = []
    while True:
        idx = data.find(p, pos)
        if idx == -1: break
        matches.append(idx)
        pos = idx + len(p)
    print(f"Prop '{p.decode()}': found {len(matches)} occurrences at {[hex(m) for m in matches[:5]]}")

