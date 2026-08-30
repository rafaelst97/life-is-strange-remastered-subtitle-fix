"""Deep analysis of the subtitle pipeline in LiS Remastered.

Goal: understand the COMPLETE path from cue name → subtitle display,
including all intermediate functions, to find why subtitles show the
raw cue name instead of the translated text.
"""
import sys
sys.path.insert(0, r'D:\Projetos\LiS_Remastered_Subtitle_Mod\tools')
from re_kit import Image

img = Image(r'C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe')
BASE = img.base

print("="*80)
print("1. GetLocalizedText (RVA 0x767d40) - Full Disassembly")
print("="*80)
glt_va = BASE + 0x767d40
glt_start, glt_end = img.func_range(glt_va)
print(f"Function range: 0x{glt_start:x} - 0x{glt_end:x} ({glt_end - glt_start} bytes)")
img.print_disasm(glt_start, count=200)

print("\n" + "="*80)
print("2. ALL callers of GetLocalizedText")
print("="*80)
callers = img.xrefs_call(glt_va)
print(f"Found {len(callers)} direct callers:")
for addr, kind in callers:
    func_start = img.func_start_pdata(addr)
    print(f"  {kind} at 0x{addr:x} (in function starting at 0x{func_start:x}, RVA 0x{func_start - BASE:x})")

print("\n" + "="*80)
print("3. SetSubtitleCue (RVA 0x95c670) - Full Disassembly + calls")
print("="*80)
ssc_va = BASE + 0x95c670
ssc_start, ssc_end = img.func_range(ssc_va)
print(f"Function range: 0x{ssc_start:x} - 0x{ssc_end:x} ({ssc_end - ssc_start} bytes)")
img.print_disasm(ssc_start, count=150)

print("\n" + "="*80)
print("4. Callers of SetSubtitleCue")
print("="*80)
ssc_callers = img.xrefs_call(ssc_va)
print(f"Found {len(ssc_callers)} direct callers:")
for addr, kind in ssc_callers:
    func_start = img.func_start_pdata(addr)
    print(f"  {kind} at 0x{addr:x} (in function starting at 0x{func_start:x}, RVA 0x{func_start - BASE:x})")

# Disassemble each caller of SetSubtitleCue
for addr, kind in ssc_callers:
    func_start = img.func_start_pdata(addr)
    if func_start:
        func_s, func_e = img.func_range(func_start)
        print(f"\n  --- Caller function at 0x{func_s:x} (RVA 0x{func_s-BASE:x}) ---")
        img.print_disasm(func_s, count=min(200, (func_e - func_s)//4))

print("\n" + "="*80)
print("5. Searching for key strings in the subtitle path")
print("="*80)

search_strings = [
    "?%s?", "GetLocalizedText", "Cues", "SubtitleText",
    "SetSubtitle", "ShowSubtitle", "DisplaySubtitle",
    "CueName", "GetName", "FName", "ToString",
    "LocalizationManager", "LiSLocalization",
]
for s in search_strings:
    hits = img.find_wide(s)
    if hits:
        print(f"\n  Wide string '{s}' found at:")
        for va, text in hits[:5]:
            print(f"    0x{va:x}: {text[:80]}")
            # Find xrefs to this string
            xrefs = img.xrefs_to(va)
            for xva, xins in xrefs[:3]:
                xfunc = img.func_start_pdata(xva)
                print(f"      <- ref at 0x{xva:x} ({xins}) in func 0x{xfunc:x} (RVA 0x{xfunc-BASE:x})")

print("\n" + "="*80)
print("6. Searching for the '?' fallback pattern in GetLocalizedText")
print("="*80)
# The game returns "?Key?" when lookup fails. Find the format string.
for s in ["?", "?%s?"]:
    hits = img.find_wide(s)
    if hits:
        for va, text in hits:
            if len(text) < 10:  # short strings only
                print(f"  Wide string '{text}' at 0x{va:x}")
                xrefs = img.xrefs_to(va)
                for xva, xins in xrefs[:5]:
                    xfunc = img.func_start_pdata(xva)
                    print(f"    <- ref at 0x{xva:x} in func RVA 0x{xfunc-BASE:x}")

print("\n" + "="*80)
print("7. Disassemble each GetLocalizedText caller in full")
print("="*80)
for addr, kind in callers:
    func_start = img.func_start_pdata(addr)
    if func_start:
        func_s, func_e = img.func_range(func_start)
        sz = func_e - func_s
        print(f"\n--- Caller at RVA 0x{func_s-BASE:x}, size {sz} bytes ---")
        img.print_disasm(func_s, count=min(300, sz//3))
