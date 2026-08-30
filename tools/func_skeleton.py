"""Print a readable skeleton of a function: calls + string/data references."""
import re
import sys
from re_kit import Image


def skeleton(img, start, end=None, show_all=False):
    if end is None:
        start, end = img.func_range(start)
    off = img.va2off(start)
    code = img.data[off:off + (end - start)]
    for ins in img.md.disasm(code, start, 0):
        line = None
        if ins.mnemonic == "call" and ins.op_str.startswith("0x"):
            tgt = int(ins.op_str, 16)
            line = "CALL 0x%x (rva 0x%x)" % (tgt, tgt - img.base)
        elif "rip" in ins.op_str:
            m = re.search(r"rip \+ (0x[0-9a-f]+)|rip - (0x[0-9a-f]+)", ins.op_str)
            if m:
                d = int(m.group(1), 16) if m.group(1) else -int(m.group(2), 16)
                tgt = ins.address + ins.size + d
                a = img.ansi(tgt) if hasattr(img, "ansi") else ""
                w = img.wstr(tgt, 90)
                desc = ""
                o = img.va2off(tgt)
                if o is not None:
                    b = img.data[o:o + 200]
                    # ansi string?
                    j = 0
                    while j < len(b) and 32 <= b[j] < 127:
                        j += 1
                    if j >= 3 and (j >= len(b) or b[j] == 0):
                        desc = "A%r" % b[:j].decode("latin1")
                    elif w and len(w) >= 3:
                        desc = "W%r" % w
                if desc:
                    line = "%-6s %-30s ; 0x%x %s" % (ins.mnemonic, ins.op_str, tgt, desc)
                elif show_all:
                    line = "%-6s %-30s ; 0x%x" % (ins.mnemonic, ins.op_str, tgt)
        if line:
            print("0x%x  %s" % (ins.address, line))


if __name__ == "__main__":
    img = Image()
    va = int(sys.argv[1], 16)
    skeleton(img, va, show_all=("-a" in sys.argv))
