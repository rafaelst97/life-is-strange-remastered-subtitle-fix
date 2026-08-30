"""Trace where SetSubtitleCue gets its FString from, and who calls GetLocalizedText"""
import sys, re, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'D:\Projetos\LiS_Remastered_Subtitle_Mod\tools')
from re_kit import Image

img = Image(r'C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe')
BASE = img.base

print("="*80)
print("Analyzing Caller 2 of GetLocalizedText (0x8c0a70)")
print("="*80)
s, e = img.func_range(BASE + 0x8c0a70)
off = img.va2off(s)
code = img.data[off:off + (e - s)]
for ins in img.md.disasm(code, s, 0):
    extra = ''
    if ins.mnemonic == 'call' and ins.op_str.startswith('0x'):
        tgt = int(ins.op_str, 16)
        if tgt - BASE == 0x767d40:
            extra = '*** CALLS GetLocalizedText ***'
    if extra:
        print('0x%x  %-10s %-40s %s' % (ins.address, ins.mnemonic, ins.op_str, extra))

print("\n" + "="*80)
print("Analyzing Caller 3 of GetLocalizedText (0x8ff870)")
print("="*80)
s, e = img.func_range(BASE + 0x8ff870)
off = img.va2off(s)
code = img.data[off:off + (e - s)]
for ins in img.md.disasm(code, s, 0):
    extra = ''
    if ins.mnemonic == 'call' and ins.op_str.startswith('0x'):
        tgt = int(ins.op_str, 16)
        if tgt - BASE == 0x767d40:
            extra = '*** CALLS GetLocalizedText ***'
    if extra:
        print('0x%x  %-10s %-40s %s' % (ins.address, ins.mnemonic, ins.op_str, extra))

print("\n" + "="*80)
print("Checking what happens if GetLocalizedText fails in Caller 3")
print("="*80)
# We want to see if Caller 3 falls back to the key name!
img.print_disasm(BASE + 0x900063, count=20)
img.print_disasm(BASE + 0x90013d, count=20)

print("\n" + "="*80)
print("Where does the raw Cue_ name come from?")
print("Checking main subtitle function 0x965310 for string fallback")
print("="*80)
# Look at what is passed into FString copy at 0x965696
img.print_disasm(BASE + 0x965680, count=20)

print("\n" + "="*80)
print("Looking up references to AltData loader (0x7188a0)")
print("="*80)
alt_callers = img.xrefs_call(BASE + 0x7188a0)
for addr, kind in alt_callers:
    fs = img.func_start_pdata(addr)
    rva = fs - BASE if fs else 0
    print(f"  {kind} at 0x{addr:x} in func RVA 0x{rva:x}")
