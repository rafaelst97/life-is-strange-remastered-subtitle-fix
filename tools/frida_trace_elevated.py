"""
Life is Strange Remastered - Frida ToString-substitution test (elevated).

Targeted test: hook FName::ToString; when the CALLER is base+0x64e02a (the
subtitle fallback-text conversion in the caller of GetSubtitleText) and the
name ends with "_C_<digits>", replace the output FString with the base name
(stripped suffix). If the caller looks the text up by that string, subtitles
should start working.
"""

import os
import time

import frida

GAME_EXE = "LiS-Win64-Shipping.exe"
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frida_trace.log")

JS_CODE = r"""
'use strict';
function log(msg) { send({ type: 'log', message: msg }); }

let base = null;
try {
    const exe = "LiS-Win64-Shipping.exe";
    for (const m of Process.enumerateModules()) {
        const n = m.name.toLowerCase();
        if (n === exe.toLowerCase() || n === 'lis-win64-shipping' || m.path.toLowerCase().endsWith(exe.toLowerCase())) {
            base = m.base;
            break;
        }
    }
    if (!base) base = Module.findBaseAddress(exe);
} catch (e) { log('findBase ERROR: ' + e); }

if (!base) {
    log('ERROR: module not found');
} else {
    log('Module base: ' + base);

    const fnToString = new NativeFunction(base.add(0xb30120), 'void', ['pointer', 'pointer']);
    const fnFree = new NativeFunction(base.add(0xa666d0), 'void', ['pointer']);
    const fnRealloc = new NativeFunction(base.add(0xa75240), 'pointer', ['pointer', 'uint64', 'uint']);

    function writeU64Any(buf, v) {
        if (v === undefined || v === null) return false;
        if (v instanceof NativePointer) {
            try { buf.writeU32(v.and(ptr('0xffffffff')).toUInt32()); buf.add(4).writeU32(v.shr(32).toUInt32()); return true; } catch (e) { return false; }
        }
        if (v instanceof UInt64) { try { buf.writeU32(v.lo >>> 0); buf.add(4).writeU32(v.hi >>> 0); return true; } catch (e) { return false; } }
        return false;
    }

    function readFNameStr(v) {
        try {
            const nameBuf = Memory.alloc(8);
            if (!writeU64Any(nameBuf, v)) return null;
            const out = Memory.alloc(16);
            out.writePointer(ptr(0)); out.add(8).writeU32(0); out.add(12).writeU32(0);
            fnToString(nameBuf, out);
            const data = out.readPointer();
            if (data.isNull()) return null;
            const s = data.readUtf16String();
            fnFree(data);
            return s;
        } catch (e) { return null; }
    }

    // The caller's ToString call is at base+0x64e02a (return address = base+0x64e02f)
    const CALLER_RET = base.add(0x64e02f);

    let substCount = 0;

    try {
        Interceptor.attach(base.add(0xb30120), {
            onEnter(args) { this.retAddr = this.returnAddress; this.fnamePtr = args[0]; },
            onLeave(retval) {
                if (substCount > 60) return;
                if (!this.retAddr.equals(CALLER_RET)) return;
                const fn = this.fnamePtr.readU64();
                const s = readFNameStr(fn);
                if (!s) return;
                const m = s.match(/^(.*)_C_\d+$/);
                if (!m) return;
                const baseName = m[1];
                substCount++;
                // Replace the output FString (args[1]) with the base name
                try {
                    const out = args[1];
                    const oldData = out.readPointer();
                    const n = (baseName.length + 1) * 2;
                    const nb = fnRealloc(ptr(0), n, 0);
                    if (!nb.isNull()) {
                        nb.writeUtf16String(baseName);
                        if (!oldData.isNull()) fnFree(oldData);
                        out.writePointer(nb);
                        out.add(8).writeS32(baseName.length + 1);
                        out.add(12).writeS32(baseName.length + 1);
                    }
                } catch (e) {}
                log('[SUBST] "' + s + '" -> "' + baseName + '"');
            }
        });
        log('hook ToString ok');
    } catch (e) { log('hook ToString ERROR: ' + e); }

    log('Hooks installed.');
}
"""


def log(line):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(line + '\n')
    print(line, flush=True)


def on_message(message, data):
    if message['type'] == 'send':
        line = str(message['payload'].get('message', message['payload']))
    elif message['type'] == 'error':
        line = '[MSG-ERR] ' + str(message.get('description'))
    else:
        return
    print(line, flush=True)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def main():
    try:
        os.remove(LOG)
    except OSError:
        pass
    log('=== START ' + time.ctime() + ' ===')

    device = frida.get_local_device()
    log('Local device: ' + str(device))

    print('Waiting for process...', flush=True)
    while True:
        try:
            procs = device.enumerate_processes()
            target = None
            for p in procs:
                if p.name.lower() == GAME_EXE.lower() or p.name.lower() == GAME_EXE.lower().replace('.exe', ''):
                    target = p
                    break
            if target is not None:
                log('Found process pid=%d name=%s' % (target.pid, target.name))
                session = device.attach(target.pid)
                log('Attached OK')
                script = session.create_script(JS_CODE)
                script.on('message', on_message)
                script.load()
                log('Hooks active. Play Episode 2 now.')
                session.on('detached', lambda reason: log('SESSION DETACHED: ' + str(reason)))
                while True:
                    time.sleep(1)
        except Exception as e:
            log('LOOP-ERR: %s' % (e,))
            time.sleep(2)


if __name__ == '__main__':
    main()
