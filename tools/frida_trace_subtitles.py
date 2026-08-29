"""
Life is Strange Remastered - Frida diagnostic tracer for the subtitle pipeline.

Attaches to the running game and hooks the three subtitle functions:
  - GetSubtitleText            (base + 0x70fb40)
  - FindAltDataSetByLayerName  (base + 0x7188a0)
  - SearchSubtitle (hash table)(base + 0x712d10)

Logs the cue/layer FNames (via the game's own FName::ToString), the dataset
type byte and the lookup results, so we can see exactly where the subtitle
text resolution fails.

Usage:
  1. Remove/rename the mod XINPUT1_3.dll (so the game runs vanilla).
  2. Launch the game.
  3. Run:  python tools\\frida_trace_subtitles.py
  4. Play Episode 2 and let Max's first lines play.
"""

import frida
import os
import sys
import time

GAME_EXE = "LiS-Win64-Shipping.exe"
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frida_trace.log")

JS_CODE = r"""
const base = Module.findBaseAddress("LiS-Win64-Shipping.exe");
if (!base) {
    send({type: 'log', message: 'ERROR: module not found'});
} else {
    send({type: 'log', message: 'Module base: ' + base});
}

const fnToString = new NativeFunction(ptr(base.add(0xb30120)), 'void', ['pointer', 'pointer']);
const fnFree = new NativeFunction(ptr(base.add(0xa666d0)), 'void', ['pointer']);

function fnameStr(fnameVal) {
    try {
        const namePtr = Memory.alloc(8);
        namePtr.writeU64(fnameVal);
        const outStr = Memory.alloc(16);
        outStr.writePointer(ptr(0));
        outStr.add(8).writeU32(0);
        outStr.add(12).writeU32(0);
        fnToString(namePtr, outStr);
        const data = outStr.readPointer();
        let s = '?';
        if (!data.isNull()) {
            s = data.readUtf16String();
            fnFree(data);
        }
        return s;
    } catch (e) {
        return 'ERR:' + e;
    }
}

// ---- GetSubtitleText(this, cueFName, outPhrases) ----
Interceptor.attach(base.add(0x70fb40), {
    onEnter(args) {
        this.cueVal = args[1].toUInt64().toString();
    },
    onLeave(retval) {
        send({type: 'log', message: '[GTXT] cue=' + fnameStr(this.cueVal) + ' ret=' + retval.toInt32()});
    }
});

// ---- FindAltDataSetByLayerName(this, flag, layerName) ----
Interceptor.attach(base.add(0x7188a0), {
    onEnter(args) {
        this.layerVal = args[2].toUInt64().toString();
        this.flag = args[1].toUInt32() & 0xFF;
    },
    onLeave(retval) {
        let r = retval;
        let extra = ' type=NULL';
        if (!r.isNull()) {
            let t = '?';
            try { t = r.add(0x18).readU8(); } catch (e) {}
            extra = ' type=' + t;
        }
        send({type: 'log', message: '[FIND] layer=' + fnameStr(this.layerVal) + ' flag=' + this.flag + ' result=' + r + extra});
    }
});

// ---- SearchSubtitle(hashTable, outIndex, cueFName) ----
Interceptor.attach(base.add(0x712d10), {
    onEnter(args) {
        this.cueVal = args[2].toUInt64().toString();
        this.hashTable = args[0];
    },
    onLeave(retval) {
        let t = '?';
        try { t = this.hashTable.sub(0x20).readU8(); } catch (e) {}
        send({type: 'log', message: '[SRCH] fname=' + fnameStr(this.cueVal) + ' result=' + retval.toInt32() + ' type=' + t});
    }
});

send({type: 'log', message: 'Hooks installed.'});
"""


def on_message(message, data):
    if message['type'] == 'send':
        line = str(message['payload'].get('message', message['payload']))
    elif message['type'] == 'error':
        line = '[FRIDA ERROR] ' + str(message.get('description'))
    else:
        return
    print(line, flush=True)
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def main():
    # Clear the previous trace
    try:
        os.remove(LOG_PATH)
    except OSError:
        pass

    device = frida.get_local_device()
    session = None
    print(f'Waiting for process matching "{GAME_EXE}"...', flush=True)
    while True:
        try:
            procs = device.enumerate_processes()
            match = None
            for p in procs:
                if p.name.lower() == GAME_EXE.lower() or p.name.lower() == GAME_EXE.lower().replace('.exe', ''):
                    match = p
                    break
            if match is not None:
                print(f'Found process: {match.name} (pid {match.pid})', flush=True)
                session = device.attach(match.pid)
                break
        except frida.ProcessNotFoundError:
            pass
        except Exception as e:
            print(f'[WARN] {e}', flush=True)
        time.sleep(2)
    print('Attached! Installing hooks...', flush=True)
    script = session.create_script(JS_CODE)
    script.on('message', on_message)
    script.load()
    print('Hooks active. Now play Episode 2 and let Max\'s lines appear.', flush=True)
    print('Logging to: ' + LOG_PATH, flush=True)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Stopping...', flush=True)
        session.detach()


if __name__ == '__main__':
    main()
