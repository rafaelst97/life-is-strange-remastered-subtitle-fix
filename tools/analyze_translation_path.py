"""Analyze the key functions in the subtitle translation path."""
import sys, re, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'D:\Projetos\LiS_Remastered_Subtitle_Mod\tools')
from re_kit import Image

img = Image(r'C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe')
BASE = img.base

# Analyze function 0x9076c0 - potential translation lookup
print("="*80)
print("Function at RVA 0x9076c0 (called from subtitle dispatch)")
print("="*80)
va = BASE + 0x9076c0
s, e = img.func_range(va)
print(f"Range: 0x{s:x} - 0x{e:x}, size {e-s}")

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
        # Check if this calls GetLocalizedText
        if tgt - BASE == 0x767d40:
            extra = '*** CALLS GetLocalizedText ***'
        else:
            extra = 'CALL RVA 0x%x' % (tgt - BASE)
    if extra:
        print('0x%x  %-10s %-40s %s' % (ins.address, ins.mnemonic, ins.op_str, extra))

# Analyze function 0x722c70 - cue name getter
print("\n" + "="*80)
print("Function at RVA 0x722c70 (first call in subtitle dispatch)")
print("="*80)
va = BASE + 0x722c70
s, e = img.func_range(va)
print(f"Range: 0x{s:x} - 0x{e:x}, size {e-s}")

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
        if tgt - BASE == 0x767d40:
            extra = '*** CALLS GetLocalizedText ***'
        else:
            extra = 'CALL RVA 0x%x' % (tgt - BASE)
    if extra:
        print('0x%x  %-10s %-40s %s' % (ins.address, ins.mnemonic, ins.op_str, extra))

# Also check function 0x919c90 and 0xa7fc10
for rva, name in [(0x919c90, "0x919c90"), (0xa7fc10, "0xa7fc10")]:
    print(f"\n--- Function at RVA {name} ---")
    va = BASE + rva
    s, e = img.func_range(va)
    if not s:
        continue
    print(f"Range: 0x{s:x} - 0x{e:x}, size {e-s}")
    off = img.va2off(s)
    code = img.data[off:off + (e - s)]
    for ins in img.md.disasm(code, s, 0):
        extra = ''
        if ins.mnemonic == 'call' and ins.op_str.startswith('0x'):
            tgt = int(ins.op_str, 16)
            if tgt - BASE == 0x767d40:
                extra = '*** CALLS GetLocalizedText ***'
            elif tgt - BASE == 0x95c670:
                extra = '*** CALLS SetSubtitleCue ***'
        if extra:
            print('0x%x  %-10s %-40s %s' % (ins.address, ins.mnemonic, ins.op_str, extra))

# Search for ANY function that calls GetLocalizedText
print("\n" + "="*80)
print("ALL callers of GetLocalizedText (comprehensive)")
print("="*80)
all_glt_callers = img.xrefs_call(BASE + 0x767d40)
print(f"Total: {len(all_glt_callers)}")
for addr, kind in all_glt_callers:
    fs = img.func_start_pdata(addr)
    rva = fs - BASE if fs else 0
    print(f"  {kind} at 0x{addr:x} in func RVA 0x{rva:x}")
