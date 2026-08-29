import frida
import ctypes
from ctypes import wintypes
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proc_list_compare.txt")

TH32CS_SNAPPROCESS = 0x2


class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ('dwSize', wintypes.DWORD), ('cntUsage', wintypes.DWORD),
        ('th32ProcessID', wintypes.DWORD), ('th32DefaultHeapID', ctypes.POINTER(ctypes.c_ulong)),
        ('th32ModuleID', wintypes.DWORD), ('cntThreads', wintypes.DWORD),
        ('th32ParentProcessID', wintypes.DWORD), ('pcPriClassBase', ctypes.c_long),
        ('dwFlags', wintypes.DWORD), ('szExeFile', ctypes.c_wchar * 260),
    ]


def win_procs():
    out = []
    h = ctypes.windll.kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if h == -1:
        return out
    pe = PROCESSENTRY32W()
    pe.dwSize = ctypes.sizeof(PROCESSENTRY32W)
    ok = ctypes.windll.kernel32.Process32FirstW(h, ctypes.byref(pe))
    while ok:
        out.append((pe.th32ProcessID, pe.szExeFile))
        ok = ctypes.windll.kernel32.Process32NextW(h, ctypes.byref(pe))
    ctypes.windll.kernel32.CloseHandle(h)
    return out


device = frida.get_local_device()
frida_procs = {}
try:
    for p in device.enumerate_processes():
        frida_procs[p.pid] = p.name
except Exception as e:
    print('frida enum error:', e)

win = {pid: name for pid, name in win_procs()}

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('Frida total: %d | Win total: %d\n\n' % (len(frida_procs), len(win)))
    f.write('=== Frida pid:name ===\n')
    for pid in sorted(frida_procs):
        f.write('%d:%s\n' % (pid, frida_procs[pid]))
    f.write('\n=== Only in Windows (not in Frida) ===\n')
    for pid in sorted(win):
        if pid not in frida_procs:
            f.write('%d:%s\n' % (pid, win[pid]))

print('Wrote', OUT)
