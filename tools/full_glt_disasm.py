"""CRITICAL ANALYSIS: How GetLocalizedText constructs the lookup key.

Based on our analysis:
1. GetLocalizedText (0x767d40) is ~11KB, references 'CU_%s_%s' and 'Cues' section name
2. It receives a raw key and tries to find it in loaded INI tables
3. The localization loader at 0x777800 loads '%s/Packages/Localization/%s/%s.ini'

The key question: does GetLocalizedText parse the cue name to find which
layer's INI file to look in? If so, the _C_<digits> suffix would break
the layer name extraction too, not just the key lookup.

Let's trace the exact flow inside GetLocalizedText:
- It receives the cue name (e.g., 'Cue_E5_3B_..._C_2147461859')
- It needs to find which INI file has this key (e.g., CU_E5_3B.ini)
- It extracts the episode/layer from the cue name using 'CU_%s_%s' format
"""
import sys
sys.path.insert(0, r'D:\Projetos\LiS_Remastered_Subtitle_Mod\tools')
from re_kit import Image

img = Image(r'C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe')
BASE = img.base

# Disassemble the ENTIRE GetLocalizedText with annotations
print("="*80)
print("COMPLETE GetLocalizedText disassembly (11556 bytes)")
print("="*80)
va = BASE + 0x767d40
s, e = img.func_range(va)

# Do it in chunks to avoid memory issues
for chunk_start in range(s, e, 2000):
    chunk_end = min(chunk_start + 2000, e)
    off = img.va2off(chunk_start)
    code = img.data[off:off + (chunk_end - chunk_start)]
    for ins in img.md.disasm(code, chunk_start, 0):
        import re
        extra = ""
        if "rip" in ins.op_str:
            m = re.search(r"rip \+ (0x[0-9a-f]+)|rip - (0x[0-9a-f]+)", ins.op_str)
            if m:
                d = int(m.group(1), 16) if m.group(1) else -int(m.group(2), 16)
                tgt = ins.address + ins.size + d
                w = img.wstr(tgt, 60)
                if w and len(w) >= 2:
                    extra = f"  ; -> 0x{tgt:x} L'{w[:60]}'"
                else:
                    # Try ANSI
                    o = img.va2off(tgt)
                    if o:
                        b = img.data[o:o+80]
                        j = 0
                        while j < len(b) and 32 <= b[j] < 127:
                            j += 1
                        if j >= 3 and (j >= len(b) or b[j] == 0):
                            extra = f"  ; -> 0x{tgt:x} A'{b[:j].decode('latin1')}'"
        elif ins.mnemonic == "call" and ins.op_str.startswith("0x"):
            tgt = int(ins.op_str, 16)
            extra = f"  ; RVA 0x{tgt-BASE:x}"
        
        print(f"0x{ins.address:x}  {ins.mnemonic:24} {ins.op_str:40}{extra}")
