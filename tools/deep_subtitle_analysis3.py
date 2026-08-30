"""CRITICAL: Deep dive into GetLocalizedText internals.

The format string 'CU_%s_%s' is referenced at 0x1407685ea INSIDE GetLocalizedText.
This means GetLocalizedText itself constructs the INI file name from the cue name.
We need to understand exactly how it constructs the lookup path and what can go wrong.

Also analyze the localization loading function at RVA 0x777800 which references
'%s/Packages/Localization/%s/%s.ini'
"""
import sys
sys.path.insert(0, r'D:\Projetos\LiS_Remastered_Subtitle_Mod\tools')
from re_kit import Image

img = Image(r'C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe')
BASE = img.base

print("="*80)
print("DEEP DIVE: GetLocalizedText internals (RVA 0x767d40)")
print("Focus on the 'CU_%s_%s' format string usage and 'Cues' section")
print("="*80)

# The function is huge - let's look at the specific area around the CU_%s_%s reference
# String at 0x1407685ea
va = BASE + 0x767d40
s, e = img.func_range(va)
print(f"Full function: 0x{s:x} to 0x{e:x} = {e-s} bytes, {(e-s)//15} approx instructions")

# Disassemble around the CU_%s_%s reference
print("\n--- Around CU_%s_%s reference (0x1407685ea) ---")
img.print_disasm(BASE + 0x7684a0, count=200)

print("\n" + "="*80) 
print("DEEP DIVE: Around 'Cues' section string reference (0x14076909a)")
print("="*80)
img.print_disasm(BASE + 0x768f00, count=200)

print("\n" + "="*80)
print("DEEP DIVE: Localization loader (RVA 0x777800)")
print("This function loads %s/Packages/Localization/%s/%s.ini files")
print("="*80)
va = BASE + 0x777800
s, e = img.func_range(va)
print(f"Function: 0x{s:x} to 0x{e:x} = {e-s} bytes")
img.print_disasm(s, count=400)

print("\n" + "="*80)
print("DEEP DIVE: DisplayFakeSubtitle parent caller (RVA 0x80d990)")
print("This is the function that calls DisplayFakeSubtitle")
print("="*80)
va = BASE + 0x80d990
s, e = img.func_range(va)
print(f"Function: 0x{s:x} to 0x{e:x} = {e-s} bytes")
img.print_disasm(s, count=300)

print("\n" + "="*80)
print("DEEP DIVE: Second caller 0x1408c0a70 - full disassembly")
print("="*80)
va = BASE + 0x8c0a70
s, e = img.func_range(va)
print(f"Function: 0x{s:x} to 0x{e:x} = {e-s} bytes")
img.print_disasm(s, count=200)
# Also trace its callers
print("\n  Callers:")
c2_callers = img.xrefs_call(BASE + 0x8c0a70)
for addr, kind in c2_callers:
    func_start = img.func_start_pdata(addr)
    rva = func_start - BASE if func_start else 0
    print(f"  {kind} at 0x{addr:x}, function RVA 0x{rva:x}")
