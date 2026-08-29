"""
Life is Strange Remastered - Frida ATTACH DIAGNOSTIC v2.

Runs indefinitely. Every 2s:
  - enumerates processes through BOTH Frida and the Windows Toolhelp API,
  - logs any game-like process (lis/life/strange/shipping) seen by either,
  - every 30s logs a status line so we can compare the two views.

When a matching process appears in BOTH views it attaches, installs the
subtitle hooks and keeps tracing. Log file: frida_attach_diag.log
"""

import ctypes
import os
import time
from ctypes import wintypes

import frida

GAME_EXE = "LiS-Win64-Shipping.exe"
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frida_attach_diag.log")

TH32CS_SNAPPROCESS = 0x2
GAME_HINTS = ('lis', 'life', 'strange', 'shipping')


class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ('dwSize', wintypes.DWORD),
        ('cntUsage', wintypes.DWORD),
        ('th32ProcessID', wintypes.DWORD),
        ('th32DefaultHeapID', ctypes.POINTER(ctypes.c_ulong)),
        ('th32ModuleID', wintypes.DWORD),
        ('cntThreads', wintypes.DWORD),
        ('th32ParentProcessID', wintypes.DWORD),
        ('pcPriClassBase', ctypes.c_long),
        ('dwFlags', wintypes.DWORD),
        ('szExeFile', ctypes.c_wchar * 260),
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


JS_CODE = r"""
const base = Module.findBaseAddress("LiS-Win64-Shipping.exe");
if (!base) { send({type:'log', message:'ERROR: module not found'}); }
else {
    send({type:'log', message:'Module base: ' + base});
    Interceptor.attach(base.add(0x70fb40), {
        onEnter(args) { this.cue = args[1].toUInt64().toString(); },
        onLeave(retval) { send({type:'log', message:'[GTXT] cue=' + this.cue + ' ret=' + retval.toInt32()}); }
    });
    Interceptor.attach(base.add(0x7188a0), {
        onEnter(args) { this.layer = args[2].toUInt64().toString(); this.flag = args[1].toUInt32() & 0xFF; },
        onLeave(retval) { send({type:'log', message:'[FIND] layer=' + this.layer + ' flag=' + this.flag + ' result=' + retval}); }
    });
    Interceptor.attach(base.add(0x712d10), {
        onEnter(args) { this.cue = args[2].toUInt64().toString(); this.ht = args[0]; },
        onLeave(retval) { send({type:'log', message:'[SRCH] fname=' + this.cue + ' result=' + retval.toInt32()}); }
    });
    send({type:'log', message:'Hooks installed.'});
}
"""


def log(line):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(line + '\n')
    print(line, flush=True)


def on_message(message, data):
    if message['type'] == 'send':
        log('MSG ' + str(message['payload'].get('message', message['payload'])))
    elif message['type'] == 'error':
        log('MSG-ERR ' + str(message.get('description')))


def main():
    try:
        os.remove(LOG)
    except OSError:
        pass
    log('=== START ' + time.ctime() + ' ===')

    device = frida.get_local_device()
    log('Local device: ' + str(device))

    last_full = 0
    iteration = 0
    while True:
        iteration += 1
        try:
            frida_procs = {p.name.lower(): p.pid for p in device.enumerate_processes()}
        except Exception as e:
            frida_procs = {}
            log('FRIDA-ENUM-ERR: %s' % (e,))
        win_list = win_procs()
        win_map = {name.lower(): pid for pid, name in win_list}

        # Log game-like matches from each view
        frida_hits = [('%d:%s' % (pid, name)) for name, pid in frida_procs.items() if any(h in name for h in GAME_HINTS)]
        win_hits = [('%d:%s' % (pid, name)) for pid, name in win_list if any(h in name.lower() for h in GAME_HINTS)]
        if frida_hits or win_hits:
            log('HITS iter=%d frida=%s win=%s' % (iteration, frida_hits, win_hits))

        # Full listing every 30s
        if time.time() - last_full > 30:
            last_full = time.time()
            log('-- FULL iter=%d frida_total=%d win_total=%d frida_hits=%s win_hits=%s'
                % (iteration, len(frida_procs), len(win_list), frida_hits, win_hits))

        # Attach if the game is visible to both
        target = None
        if GAME_EXE.lower() in frida_procs:
            target = (frida_procs[GAME_EXE.lower()], GAME_EXE)
        elif 'lis-win64-shipping' in frida_procs:
            target = (frida_procs['lis-win64-shipping'], 'lis-win64-shipping')
        if target is None and GAME_EXE.lower() in win_map:
            log('GAME visible to Windows but NOT to Frida -> elevation/session problem. frida name list: %s'
                % [n for n in frida_procs if any(h in n for h in GAME_HINTS)])

        if target is not None:
            pid, name = target
            log('Attaching to pid=%d name=%s' % (pid, name))
            try:
                session = device.attach(pid)
                log('Attached OK')
                script = session.create_script(JS_CODE)
                script.on('message', on_message)
                script.load()
                log('Hooks installed. Tracing...')
                session.on('detached', lambda reason: log('SESSION DETACHED: ' + str(reason)))
                while True:
                    time.sleep(1)
            except Exception as e:
                log('ATTACH-ERR: %s' % (e,))
        time.sleep(2)


if __name__ == '__main__':
    main()
