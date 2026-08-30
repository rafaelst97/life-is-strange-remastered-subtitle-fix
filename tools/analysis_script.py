import sys
sys.path.insert(0, r'D:\Projetos\LiS_Remastered_Subtitle_Mod\tools')
from re_kit import Image
import re

img = Image(r'C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe')

def disassemble_func(va, title):
    start, end = img.func_range(va)
    if not start:
        start = va
        end = va + 0x200 # arbitrary
    print(f"\n{'='*80}\n{title} at 0x{start:x} to 0x{end:x}\n{'='*80}")
    
    # print all instructions in range
    for ins in img.disasm(start, end - start):
        if ins.address >= end:
            break
        
        extra = ""
        if "rip" in ins.op_str:
            m = re.search(r"rip \+ (0x[0-9a-f]+)|rip - (0x[0-9a-f]+)", ins.op_str)
            if m:
                d = int(m.group(1), 16) if m.group(1) else -int(m.group(2), 16)
                tgt = ins.address + ins.size + d
                extra = f"  ; -> 0x{tgt:x}"
                s = img.wstr(tgt, 60)
                if s and all(32 <= ord(c) < 127 for c in s[:20]) and len(s) > 3:
                    extra += f" L{s!r}"
                else:
                    # check ASCII
                    ascii_s = img.read(tgt, 60).split(b'\x00')[0]
                    if len(ascii_s) > 3 and all(32 <= c < 127 for c in ascii_s):
                        extra += f" '{ascii_s.decode()}'"
        print(f"0x{ins.address:x}  {ins.mnemonic:24s} {ins.op_str:40s}{extra}")

with open(r'D:\Projetos\LiS_Remastered_Subtitle_Mod\tools\analysis_output.txt', 'w', encoding='utf-8') as f:
    sys.stdout = f
    
    # 1. Disassemble GetLocalizedText
    print("1. Disassembling GetLocalizedText")
    disassemble_func(img.base + 0x767d40, "GetLocalizedText")
    
    # 2. Find ALL callers of GetLocalizedText
    print("\n2. Find callers of GetLocalizedText")
    callers = img.xrefs_call(img.base + 0x767d40)
    print(f"Found {len(callers)} callers")
    
    # 3. Disassemble each calling function
    for va, kind in callers:
        disassemble_func(va, f"Caller of GetLocalizedText (Call site: 0x{va:x})")
        
    # 4. Look for nearby lookup functions
    print("\n4. Functions nearby GetLocalizedText (0x767d40)")
    start_range = img.base + 0x766d40
    end_range = img.base + 0x768d40
    curr = start_range
    funcs_nearby = []
    while curr < end_range:
        s, e = img.func_range(curr)
        if s and e:
            if not funcs_nearby or funcs_nearby[-1][0] != s:
                funcs_nearby.append((s, e))
            curr = e
        else:
            curr += 1
    for s, e in funcs_nearby:
        print(f"Nearby function: 0x{s:x} - 0x{e:x}")
        
    # 5. Search for wide strings containing Cue_ and Cues
    print("\n5. Searching for wide strings 'Cue_' and 'Cues'")
    cue1 = img.find_wide("Cue_")
    for va, s in cue1:
        print(f"String at 0x{va:x}: {s}")
    cue2 = img.find_wide("Cues")
    for va, s in cue2:
        print(f"String at 0x{va:x}: {s}")
        
    # 6. Disassemble SetSubtitleCue (0x95c670)
    print("\n6. Disassembling SetSubtitleCue")
    disassemble_func(img.base + 0x95c670, "SetSubtitleCue")

sys.stdout = sys.__stdout__
