"""Static analysis helpers for LiS-Win64-Shipping.exe.

Loads the PE once, exposes VA<->file-offset mapping, RIP-relative xref scanning
and a capstone disassembler bound to the image, so the individual analysis
scripts stay short.
"""
import re
import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

EXE = r"C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\LiS-Win64-Shipping.exe"


class Image:
    def __init__(self, path=EXE):
        self.path = path
        self.data = open(path, "rb").read()
        self.pe = pefile.PE(path, fast_load=True)
        self.base = self.pe.OPTIONAL_HEADER.ImageBase
        self.sections = [
            (s.Name.decode().rstrip("\x00"), s.VirtualAddress, s.Misc_VirtualSize,
             s.PointerToRawData, s.SizeOfRawData)
            for s in self.pe.sections
        ]
        for name, va, vsz, ptr, rsz in self.sections:
            if name == ".text":
                self.text_va, self.text_ptr, self.text_size = va, ptr, rsz
        self.md = Cs(CS_ARCH_X86, CS_MODE_64)
        self.md.detail = True

    # --- address conversion -------------------------------------------------
    def off2va(self, off):
        for name, va, vsz, ptr, rsz in self.sections:
            if ptr <= off < ptr + rsz:
                return self.base + va + (off - ptr)
        return None

    def va2off(self, va):
        rva = va - self.base
        for name, sva, vsz, ptr, rsz in self.sections:
            if sva <= rva < sva + max(vsz, rsz):
                off = ptr + (rva - sva)
                if off < len(self.data):
                    return off
        return None

    def read(self, va, n):
        off = self.va2off(va)
        return self.data[off:off + n] if off is not None else b""

    def qword(self, va):
        return int.from_bytes(self.read(va, 8), "little")

    def dword(self, va):
        return int.from_bytes(self.read(va, 4), "little")

    # --- strings -----------------------------------------------------------
    def wstr(self, va, maxlen=400):
        out = []
        off = self.va2off(va)
        if off is None:
            return ""
        for i in range(maxlen):
            c = int.from_bytes(self.data[off + 2 * i:off + 2 * i + 2], "little")
            if c == 0:
                break
            out.append(chr(c))
        return "".join(out)

    def find_wide(self, needle):
        """Yield VAs of wide strings containing `needle` (returns full string)."""
        pat = needle.encode("utf-16-le")
        res = []
        for m in re.finditer(re.escape(pat), self.data):
            st = m.start()
            while st - 2 >= 0 and 32 <= self.data[st - 2] < 127 and self.data[st - 1] == 0:
                st -= 2
            va = self.off2va(st)
            if va is not None:
                res.append((va, self.wstr(va)))
        # dedupe by va
        seen, out = set(), []
        for va, s in res:
            if va not in seen:
                seen.add(va)
                out.append((va, s))
        return out

    # --- xrefs -------------------------------------------------------------
    def _text_i32(self):
        import numpy as np
        if getattr(self, "_i32cache", None) is None:
            text = self.data[self.text_ptr:self.text_ptr + self.text_size]
            buf = np.frombuffer(text, dtype=np.uint8)
            # int32 read at every byte offset
            n = len(buf) - 3
            self._i32cache = (
                buf[0:n].astype(np.int64)
                | (buf[1:n + 1].astype(np.int64) << 8)
                | (buf[2:n + 2].astype(np.int64) << 16)
                | (buf[3:n + 3].astype(np.int64) << 24)
            )
            # sign-extend
            self._i32cache = np.where(self._i32cache >= 0x80000000,
                                      self._i32cache - 0x100000000, self._i32cache)
            self._idx = np.arange(n, dtype=np.int64)
        return self._i32cache, self._idx

    def xrefs_to(self, target_va, confirm=True):
        """Find RIP-relative instructions in .text whose target equals target_va."""
        import numpy as np
        i32, idx = self._text_i32()
        text_base = self.base + self.text_va
        want = target_va - text_base - 4
        cand = np.nonzero((i32 + idx) == want)[0]
        text = self.data[self.text_ptr:self.text_ptr + self.text_size]
        hits = []
        for i in cand.tolist():
            if not confirm:
                hits.append((text_base + i, "?"))
                continue
            for back in range(2, 11):
                start = i - back
                if start < 0:
                    continue
                try:
                    ins = next(self.md.disasm(text[start:start + 16], text_base + start, 1))
                except StopIteration:
                    continue
                if ins.size == back + 4 and "rip" in ins.op_str:
                    hits.append((text_base + start, "%s %s" % (ins.mnemonic, ins.op_str)))
                    break
        return hits

    def xrefs_call(self, target_va):
        """Find direct `call rel32` / `jmp rel32` sites targeting target_va."""
        import numpy as np
        i32, idx = self._text_i32()
        text_base = self.base + self.text_va
        want = target_va - text_base - 4
        cand = np.nonzero((i32 + idx) == want)[0]
        text = self.data[self.text_ptr:self.text_ptr + self.text_size]
        hits = []
        for i in cand.tolist():
            if i >= 1 and text[i - 1] in (0xE8, 0xE9):
                kind = "call" if text[i - 1] == 0xE8 else "jmp"
                hits.append((text_base + i - 1, kind))
        return hits

    def disasm(self, va, count=60):
        off = self.va2off(va)
        code = self.data[off:off + count * 15]
        return list(self.md.disasm(code, va, count))

    def print_disasm(self, va, count=60, annotate=True):
        for ins in self.disasm(va, count):
            extra = ""
            if annotate and "rip" in ins.op_str:
                m = re.search(r"rip \+ (0x[0-9a-f]+)|rip - (0x[0-9a-f]+)", ins.op_str)
                if m:
                    d = int(m.group(1), 16) if m.group(1) else -int(m.group(2), 16)
                    tgt = ins.address + ins.size + d
                    extra = "  ; -> 0x%x" % tgt
                    s = self.wstr(tgt, 60)
                    if s and all(32 <= ord(c) < 127 for c in s[:20]) and len(s) > 3:
                        extra += " L%r" % s
            print("0x%x  %-24s %-40s%s" % (ins.address, ins.mnemonic, ins.op_str, extra))

    # --- function table (.pdata / RUNTIME_FUNCTION) -------------------------
    def _pdata(self):
        import numpy as np
        if getattr(self, "_pd", None) is None:
            for name, va, vsz, ptr, rsz in self.sections:
                if name == ".pdata":
                    raw = self.data[ptr:ptr + vsz]
                    break
            arr = np.frombuffer(raw[:len(raw) // 12 * 12], dtype=np.uint32).reshape(-1, 3)
            self._pd = arr  # columns: BeginRVA, EndRVA, UnwindRVA
        return self._pd

    def func_range(self, va):
        """Return (start_va, end_va) of the function containing va, from .pdata."""
        import numpy as np
        arr = self._pdata()
        rva = va - self.base
        i = int(np.searchsorted(arr[:, 0], rva, side="right")) - 1
        while i >= 0:
            b, e = int(arr[i, 0]), int(arr[i, 1])
            if b <= rva < e:
                return self.base + b, self.base + e
            i -= 1
        return None, None

    def func_start_pdata(self, va):
        return self.func_range(va)[0]

    def func_start(self, va, limit=0x4000):
        """Walk backwards to a plausible function start (int3 padding / cc alignment)."""
        off = self.va2off(va)
        i = off
        while i > off - limit:
            # look for a run of int3 (0xCC) or a nop-pad boundary
            if self.data[i - 1] == 0xCC and self.data[i - 2] == 0xCC:
                return self.off2va(i)
            i -= 1
        return None


if __name__ == "__main__":
    img = Image()
    print("base 0x%x, .text 0x%x size 0x%x" % (img.base, img.base + img.text_va, img.text_size))
