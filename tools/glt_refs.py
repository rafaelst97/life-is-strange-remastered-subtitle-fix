"""Extract all string references and calls from GetLocalizedText."""
import sys, re, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'D:\Projetos\LiS_Remastered_Subtitle_Mod\tools')
from re_kit import Image

img = Image(r'C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe')
BASE = img.base
va = BASE + 0x767d40
s, e = img.func_range(va)

off = img.va2off(s)
code = img.data[off:off + (e - s)]
for ins in img.md.disasm(code, s, 0):
    extra = ''
    if 'rip' in ins.op_str:
        m = re.search(r'rip \+ (0x[0-9a-f]+)|rip - (0x[0-9a-f]+)', ins.op_str)
        if m:
            d = int(m.group(1), 16) if m.group(1) else -int(m.group(2), 16)
            tgt = ins.address + ins.size + d
            w = img.wstr(tgt, 80)
            if w and len(w) >= 2:
                extra = 'STR L"' + w[:80] + '"'
            else:
                o = img.va2off(tgt)
                if o:
                    b = img.data[o:o+80]
                    j = 0
                    while j < len(b) and 32 <= b[j] < 127:
                        j += 1
                    if j >= 3 and (j >= len(b) or b[j] == 0):
                        extra = 'ASTR "' + b[:j].decode('latin1') + '"'
    elif ins.mnemonic == 'call' and ins.op_str.startswith('0x'):
        tgt = int(ins.op_str, 16)
        extra = 'CALL RVA 0x%x' % (tgt - BASE)
    if extra:
        print('0x%x  %-10s %-40s %s' % (ins.address, ins.mnemonic, ins.op_str, extra))
