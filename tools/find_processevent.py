import pefile
import capstone
import struct

exe_path = r"C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe"
pe = pefile.PE(exe_path)

with open(exe_path, "rb") as f:
    data = f.read()

image_base = pe.OPTIONAL_HEADER.ImageBase

# In UE4 4.23, ProcessEvent string or signature
# Often references string: "ProcessEvent: %s" or "Calling %s" or "Script call stack:"
needles = [
    'Script call stack:'.encode(),
    'ProcessEvent'.encode(),
    'UObject::ProcessEvent'.encode(),
    'ProcessLocalScriptFunction'.encode()
]

print("Searching for ProcessEvent signatures...")
for n in needles:
    pos = 0
    while True:
        idx = data.find(n, pos)
        if idx == -1: break
        rva = pe.get_rva_from_offset(idx)
        print(f"Found {n.decode(errors='ignore')} at RVA 0x{rva:x} (VA 0x{image_base + rva:x})")
        pos = idx + len(n)

