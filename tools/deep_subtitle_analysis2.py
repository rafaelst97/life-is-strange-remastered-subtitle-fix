"""Critical analysis: trace what happens BEFORE GetLocalizedText.
Focus on: where does the cue name come from? Is it the object name or the asset name?

Key question: the hook strips _C_<digits>, but does the game have OTHER patterns 
that cause the same bug? Or is the problem that GetLocalizedText is never called
for some subtitles?
"""
import sys
sys.path.insert(0, r'D:\Projetos\LiS_Remastered_Subtitle_Mod\tools')
from re_kit import Image

img = Image(r'C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe')
BASE = img.base

print("="*80)
print("ANALYSIS 1: Second caller of GetLocalizedText (0x1408c0a70)")
print("This may be the main subtitle display path")
print("="*80)
va = BASE + 0x8c0a70
s, e = img.func_range(va)
print(f"Function: 0x{s:x} - 0x{e:x} ({e-s} bytes)")
img.print_disasm(s, count=200)

print("\n" + "="*80)
print("ANALYSIS 2: Third caller of GetLocalizedText (0x1408ff870)")
print("Three call sites: 0x140900063, 0x14090013d, 0x140900217")
print("="*80)
va = BASE + 0x8ff870
s, e = img.func_range(va)
print(f"Function: 0x{s:x} - 0x{e:x} ({e-s} bytes)")
img.print_disasm(s, count=400)

print("\n" + "="*80)
print("ANALYSIS 3: SetSubtitleCue full + its callees")
print("="*80)
va = BASE + 0x95c670
s, e = img.func_range(va)
print(f"SetSubtitleCue: 0x{s:x} - 0x{e:x} ({e-s} bytes)")
img.print_disasm(s, count=100)

# Function called inside SetSubtitleCue: 0x1409651b0
print("\n--- Callee 0x1409651b0 ---")
va2 = 0x1409651b0
s2, e2 = img.func_range(va2)
if s2:
    print(f"Range: 0x{s2:x} - 0x{e2:x}")
    img.print_disasm(s2, count=200)

print("\n" + "="*80)
print("ANALYSIS 4: Callers of SetSubtitleCue")
print("="*80)
ssc_callers = img.xrefs_call(BASE + 0x95c670)
print(f"Found {len(ssc_callers)} callers")
for addr, kind in ssc_callers:
    func_start = img.func_start_pdata(addr)
    rva = func_start - BASE if func_start else 0
    print(f"  {kind} at 0x{addr:x}, function RVA 0x{rva:x}")

print("\n" + "="*80)
print("ANALYSIS 5: What calls the DisplayFakeSubtitle caller (0x1407a0f90)?")
print("="*80)
dfs_callers = img.xrefs_call(BASE + 0x7a0f90)
print(f"Found {len(dfs_callers)} callers of DisplayFakeSubtitle caller")
for addr, kind in dfs_callers:
    func_start = img.func_start_pdata(addr)
    rva = func_start - BASE if func_start else 0
    print(f"  {kind} at 0x{addr:x}, function RVA 0x{rva:x}")

print("\n" + "="*80)
print("ANALYSIS 6: Check for FName::ToString pattern used to get cue names")
print("="*80)
# Search for GetName/ToString patterns near subtitle code
for s_str in ['GetName', 'FName::ToString', 'GetFName']:
    hits = img.find_wide(s_str)
    if hits:
        for va_hit, text in hits[:3]:
            print(f"  '{text}' at 0x{va_hit:x}")

# Look for the UE4 FName::ToString which converts FName to FString
# This is key - when UE4 spawns objects, FName::ToString gives the unique name
# We need to find where cue names are converted from FName to string

print("\n" + "="*80)
print("ANALYSIS 7: Search for critical format strings")
print("="*80)
for s_str in ['%s/Cues/%s', 'CU_%s', 'AltData/%s', 'Localization/%s',
              'LoadLocalizationFile', 'LoadLocalizedTextFile',
              'ReloadLocalization', 'SetCulture', 'ChangeCulture',
              'culture', 'INI', '.ini']:
    hits = img.find_wide(s_str)
    if hits:
        print(f"\n  '{s_str}' found:")
        for va_hit, text in hits[:3]:
            print(f"    0x{va_hit:x}: {text[:100]}")
            xrefs = img.xrefs_to(va_hit)
            for xva, xins in xrefs[:2]:
                xfunc = img.func_start_pdata(xva)
                print(f"      <- ref at 0x{xva:x} in func RVA 0x{xfunc-BASE:x}")
