import sys
import re
sys.path.insert(0, r'D:\Projetos\LiS_Remastered_Subtitle_Mod\tools')
from re_kit import Image
import traceback

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
            
    pat_asc = re.compile(b'[\x20-\x7e]{' + str(min_len).encode() + b',}')
    seen_asc = set()
    strings_asc = []
    for m in pat_asc.finditer(img.data):
        st = m.start()
        va = img.off2va(st)
        if va and va not in seen_asc:
            seen_asc.add(va)
            s = img.data[st:st+200].split(b'\x00')[0]
            try:
                s = s.decode('ascii')
                strings_asc.append((va, s))
            except:
                pass
    return strings, strings_asc

with open('report.txt', 'w', encoding='utf-8') as f:
    def write(s):
        f.write(s + '\n')
    
    try:
        wstrs, astrs = extract_strings(min_len=3)
        
        def search_strs(query, case_insensitive=True):
            write(f"\n--- Search results for '{query}' (wide) ---")
            q = query.lower() if case_insensitive else query
            for va, s in wstrs:
                if case_insensitive and q in s.lower():
                    xrefs = img.xrefs_to(va, confirm=False) + img.xrefs_to(va, confirm=True)
                    write(f"0x{va:x}: {s[:100]} (xrefs: {len(xrefs)})")
                    for x, extra in xrefs[:3]:
                        write(f"  -> xref from 0x{x:x}")
                        
        write("\n=== 1. Subtitle References ===")
        search_strs('subtitle')
        
        write("\n=== 2. Localization References ===")
        search_strs('locali')
        
        write("\n=== 3. Fallback Pattern References ===")
        search_strs('?%s?')
        for va, s in wstrs:
            if s == '?' or s == '?%s?':
                write(f"Exact match 0x{va:x}: {s}")
                xrefs = img.xrefs_to(va)
                for x, _ in xrefs:
                    write(f"  -> xref from 0x{x:x}")
        
        write("\n=== 4. Disassemble Lipsync Getter 0x70fb40 ===")
        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        img.print_disasm(img.base + 0x70fb40, 60)
        write(sys.stdout.getvalue())
        sys.stdout = old_stdout
        
        write("\n=== 5. Disassemble FindOrLoadAltDataSet 0x7188a0 ===")
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        img.print_disasm(img.base + 0x7188a0, 100)
        write(sys.stdout.getvalue())
        sys.stdout = old_stdout
        
        write("\n=== 6. INT and JPN References ===")
        search_strs('INT', False)
        search_strs('JPN', False)
        
        write("\n=== 7. Cues References ===")
        search_strs('Cues', False)
        
        write("\n=== 9. .ini References ===")
        search_strs('.ini')
        
        write("\n=== 10. Culture References ===")
        search_strs('culture')

        write("\nDone.")
    except Exception as e:
        write("Error: " + traceback.format_exc())
