import sys
import re
sys.path.insert(0, r'D:\Projetos\LiS_Remastered_Subtitle_Mod\tools')
from re_kit import Image

sys.stdout.reconfigure(encoding='utf-8')
img = Image(r'C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe')

def extract_strings(min_len=4):
    pat = re.compile(b'(?:[\x20-\x7e]\x00){' + str(min_len).encode() + b',}')
    seen = set()
    strings = []
    for m in pat.finditer(img.data):
        st = m.start()
        # extend left
        while st - 2 >= 0 and 32 <= img.data[st - 2] < 127 and img.data[st - 1] == 0:
            st -= 2
        va = img.off2va(st)
        if va and va not in seen:
            seen.add(va)
            strings.append((va, img.wstr(va, 1000)))
            
    # also ascii strings just in case
    pat_asc = re.compile(b'[\x20-\x7e]{' + str(min_len).encode() + b',}')
    seen_asc = set()
    strings_asc = []
    for m in pat_asc.finditer(img.data):
        st = m.start()
        va = img.off2va(st)
        if va and va not in seen_asc:
            seen_asc.add(va)
            # read ascii
            s = img.data[st:st+200].split(b'\x00')[0]
            try:
                s = s.decode('ascii')
                strings_asc.append((va, s))
            except:
                pass
    return strings, strings_asc

wstrs, astrs = extract_strings(min_len=3)

def search_strs(query, case_insensitive=True):
    print(f"\n--- Search results for '{query}' (wide) ---")
    q = query.lower() if case_insensitive else query
    for va, s in wstrs:
        if case_insensitive and q in s.lower():
            xrefs = img.xrefs_to(va, confirm=False) + img.xrefs_to(va, confirm=True)
            print(f"0x{va:x}: {s[:100]} (xrefs: {len(xrefs)})")
            for x, extra in xrefs[:3]:
                print(f"  -> xref from 0x{x:x}")
                
print("\n=== 1. Subtitle References ===")
search_strs('subtitle')

print("\n=== 2. Localization References ===")
search_strs('locali')

print("\n=== 3. Fallback Pattern References ===")
search_strs('?%s?')
search_strs('?') # This might be too noisy, we will just look for '?%s?' and '?' with xrefs maybe
for va, s in wstrs:
    if s == '?' or s == '?%s?':
        print(f"Exact match 0x{va:x}: {s}")
        xrefs = img.xrefs_to(va)
        for x, _ in xrefs:
            print(f"  -> xref from 0x{x:x}")

print("\n=== 4. Disassemble Lipsync Getter 0x70fb40 ===")
img.print_disasm(img.base + 0x70fb40, 40)

print("\n=== 5. Disassemble FindOrLoadAltDataSet 0x7188a0 ===")
img.print_disasm(img.base + 0x7188a0, 100)

print("\n=== 6. INT and JPN References ===")
search_strs('INT', False)
search_strs('JPN', False)

print("\n=== 7. Cues References ===")
search_strs('Cues', False)

print("\n=== 8. FName::ToString / Name conversion logic ===")
# FName::ToString usually takes an FString out parameter.
# We might see strings like 'None' or xrefs to standard names.
# We can search for 'FName' in ascii or wide strings
print("\n--- Ascii FName references ---")
for va, s in astrs:
    if 'FName' in s or 'ToString' in s:
        # Just print few
        pass

print("\n=== 9. .ini References ===")
search_strs('.ini')

print("\n=== 10. Culture References ===")
search_strs('culture')
