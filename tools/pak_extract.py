"""Minimal UE4 .pak (version 8, unencrypted index) reader.

Used to inspect where Life is Strange Remastered actually stores its subtitle
text: LIS/Content/Packages/Localization/<culture>/<name>.ini inside pakchunk0.
"""
import os
import struct
import sys
import zlib

MAGIC = 0x5A6F12E1


def read_fstring(buf, pos):
    (n,) = struct.unpack_from('<i', buf, pos)
    pos += 4
    if n == 0:
        return '', pos
    if n < 0:  # UTF-16
        n = -n
        s = buf[pos:pos + n * 2].decode('utf-16-le').rstrip('\x00')
        return s, pos + n * 2
    s = buf[pos:pos + n].decode('latin1').rstrip('\x00')
    return s, pos + n


class Pak:
    def __init__(self, path):
        self.path = path
        size = os.path.getsize(path)
        with open(path, 'rb') as f:
            f.seek(size - 1024)
            tail = f.read()
        pos = tail.rfind(struct.pack('<I', MAGIC))
        hdr = tail[pos:]
        self.version, = struct.unpack_from('<I', hdr, 4)
        self.index_offset, self.index_size = struct.unpack_from('<QQ', hdr, 8)
        # compression method names follow the 20-byte index hash
        names = hdr[8 + 16 + 20:]
        self.compression_methods = ['None'] + [
            names[i:i + 32].split(b'\x00')[0].decode('latin1')
            for i in range(0, len(names) - 31, 32)
        ]
        with open(path, 'rb') as f:
            f.seek(self.index_offset)
            idx = f.read(self.index_size)
        self.mount, p = read_fstring(idx, 0)
        (count,) = struct.unpack_from('<i', idx, p)
        p += 4
        self.entries = {}
        for _ in range(count):
            name, p = read_fstring(idx, p)
            offset, size_, usize, cmethod = struct.unpack_from('<qqqi', idx, p)
            p += 28
            p += 20  # hash
            blocks = []
            if cmethod != 0:
                (nb,) = struct.unpack_from('<i', idx, p)
                p += 4
                for _b in range(nb):
                    s, e = struct.unpack_from('<qq', idx, p)
                    p += 16
                    blocks.append((s, e))
            flags, blocksize = struct.unpack_from('<Bi', idx, p)
            p += 5
            self.entries[name] = dict(offset=offset, size=size_, usize=usize,
                                      cmethod=cmethod, blocks=blocks,
                                      flags=flags, blocksize=blocksize)

    def entry_header_size(self, e):
        n = 8 + 8 + 8 + 4 + 20 + 1 + 4
        if e['cmethod'] != 0:
            n += 4 + 16 * len(e['blocks'])
        return n

    def read(self, name):
        e = self.entries[name]
        with open(self.path, 'rb') as f:
            if e['cmethod'] == 0:
                f.seek(e['offset'] + self.entry_header_size(e))
                return f.read(e['size'])
            out = b''
            for (bs, be) in e['blocks']:
                # block offsets are relative to the entry start for v5+
                start = bs if bs > e['offset'] else e['offset'] + bs
                f.seek(start)
                chunk = f.read(be - bs)
                method = self.compression_methods[e['cmethod']]
                if method.lower() == 'zlib':
                    out += zlib.decompress(chunk)
                else:
                    raise RuntimeError('unsupported compression: %r' % method)
            return out[:e['usize']]


if __name__ == '__main__':
    pak = Pak(sys.argv[1])
    print('version', pak.version, 'mount', pak.mount, 'entries', len(pak.entries),
          'methods', pak.compression_methods)
    pat = sys.argv[2] if len(sys.argv) > 2 else ''
    hits = [n for n in pak.entries if pat.lower() in n.lower()]
    print('matches:', len(hits))
    for n in hits[:20]:
        print('  ', n, pak.entries[n]['usize'], 'cm=%d' % pak.entries[n]['cmethod'])
