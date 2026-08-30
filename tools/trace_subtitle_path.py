"""Analyze the main SetSubtitleCue caller path"""
import sys, re, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'D:\Projetos\LiS_Remastered_Subtitle_Mod\tools')
from re_kit import Image

img = Image(r'C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe')
BASE = img.base

# Caller 1 of SetSubtitleCue - at 0x7a1905 (in DisplayFakeSubtitle caller 0x7a0f90)
print("SetSubtitleCue callers:")
callers = img.xrefs_call(BASE + 0x95c670)
for addr, kind in callers:
    fs = img.func_start_pdata(addr)
    rva = fs - BASE if fs else 0
    print(f"  {kind} at 0x{addr:x} in func RVA 0x{rva:x}")

# The second caller at 0x965310 - what does this function do?
print("\n" + "="*80)
print("Main subtitle dispatch function (RVA 0x965310)")
print("="*80)
va = BASE + 0x965310
s, e = img.func_range(va)
print(f"Function 0x{s:x} - 0x{e:x}, size {e-s}")

off = img.va2off(s)
code = img.data[off:off + (e - s)]
for ins in img.md.disasm(code, s, 0):
    extra = ''
    if 'rip' in ins.op_str:
        m = re.search(r'rip \+ (0x[0-9a-f]+)|rip - (0x[0-9a-f]+)', ins.op_str)
        if m:
            d = int(m.group(1), 16) if m.group(1) else -int(m.group(2), 16)
            tgt = ins.address + ins.size + d
            w = img.wstr(tgt, 60)
            if w and len(w) >= 2:
                extra = 'STR L"' + w[:60] + '"'
    elif ins.mnemonic == 'call' and ins.op_str.startswith('0x'):
        tgt = int(ins.op_str, 16)
        extra = 'CALL RVA 0x%x' % (tgt - BASE)
    if extra:
        print('0x%x  %-10s %-40s %s' % (ins.address, ins.mnemonic, ins.op_str, extra))

# Now trace callers of this function too
print("\n\nCallers of 0x965310:")
callers2 = img.xrefs_call(BASE + 0x965310)
for addr, kind in callers2:
    fs = img.func_start_pdata(addr)
    rva = fs - BASE if fs else 0
    print(f"  {kind} at 0x{addr:x} in func RVA 0x{rva:x}")

# Also check function at 0x9fe410 callers
print("\nCallers of 0x9fe410 (other SetSubtitleCue caller):")
callers3 = img.xrefs_call(BASE + 0x9fe410)
for addr, kind in callers3:
    fs = img.func_start_pdata(addr)
    rva = fs - BASE if fs else 0
    print(f"  {kind} at 0x{addr:x} in func RVA 0x{rva:x}")
