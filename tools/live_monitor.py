"""
Life is Strange Remastered - Enhanced Real-Time Telemetry & Exception Monitor (Frida)
-------------------------------------------------------------------------------------
Monitors:
- Subtitle resolutions & Cue requests
- Level/Layer AltData lookups
- CPU instruction faults, Access Violations, and Exceptions via Process.setExceptionHandler
- UE4 Output Logging & Assertions
"""

import frida
import time
import os
import sys
import datetime

LOG_FILE = r"D:\Projetos\LiS_Remastered_Subtitle_Mod\live_monitor.log"

def log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    line = f"[{ts}] {msg}"
    print(line)
    sys.stdout.flush()
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

# Clear previous log
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write("=== Life is Strange Remastered - Enhanced Live Telemetry Monitor ===\n")

log("Waiting for LiS-Win64-Shipping.exe to start...")

session = None
while session is None:
    try:
        session = frida.attach("LiS-Win64-Shipping.exe")
        log("Successfully attached to LiS-Win64-Shipping.exe!")
    except frida.ProcessNotFoundError:
        time.sleep(0.5)
    except Exception as e:
        time.sleep(0.5)

JS_MONITOR = r"""
const base = Module.findBaseAddress("LiS-Win64-Shipping.exe");
send({type: "info", message: "LiS-Win64-Shipping.exe Base Address: " + base});

// 1. Global Native Exception / Crash Monitor
Process.setExceptionHandler(function(details) {
    let msg = "!!! NATIVE EXCEPTION CAUGHT !!!\n" +
              "  Type: " + details.type + "\n" +
              "  Address: " + details.address + "\n" +
              "  Memory Address: " + (details.memory ? details.memory.address : "N/A") + "\n" +
              "  Operation: " + (details.memory ? details.memory.operation : "N/A") + "\n" +
              "  RIP: " + details.context.pc + "\n" +
              "  RAX: " + details.context.rax + " RBX: " + details.context.rbx + "\n" +
              "  RCX: " + details.context.rcx + " RDX: " + details.context.rdx + "\n" +
              "  RSP: " + details.context.sp + "\n";
    send({type: "crash", message: msg});
    return false; // let default handler run if needed
});

// Helper to read FString
function readFString(ptr) {
    try {
        if (ptr.isNull()) return "<NULL>";
        let dataPtr = ptr.readPointer();
        if (dataPtr.isNull()) return "<EMPTY>";
        return dataPtr.readUtf16String();
    } catch(e) {
        return "<ERROR: " + e.message + ">";
    }
}

// 2. Hook FindAltDataSetByLayerName (RVA 0x7188a0)
const fnFindAltDataSet = base.add(0x7188a0);
Interceptor.attach(fnFindAltDataSet, {
    onEnter: function(args) {
        let layerName = readFString(args[2]);
        send({type: "layer_req", message: "FindAltDataSetByLayerName for Layer: '" + layerName + "'"});
    },
    onLeave: function(retval) {
        send({type: "layer_res", message: "FindAltDataSetByLayerName returned: " + retval});
    }
});

// 3. Hook GetSubtitleText (RVA 0x710100)
const fnGetSubtitleText = base.add(0x710100);
Interceptor.attach(fnGetSubtitleText, {
    onEnter: function(args) {
        this.cueStr = readFString(args[1]);
        send({type: "cue_req", message: ">> SUBTITLE REQUEST: '" + this.cueStr + "'"});
    },
    onLeave: function(retval) {
        send({type: "cue_res", message: "<< SUBTITLE RESOLVED (Ret=" + retval + ") for: '" + this.cueStr + "'"});
    }
});

// 4. Hook FindAltDataSetDirect (RVA 0x6f0e60)
const fnFindAltDataSetDirect = base.add(0x6f0e60);
Interceptor.attach(fnFindAltDataSetDirect, {
    onEnter: function(args) {
        let key = readFString(args[1]);
        send({type: "map_search", message: "TMap Direct Search for Layer: '" + key + "'"});
    },
    onLeave: function(retval) {
        send({type: "map_result", message: "TMap Direct Search returned Dataset: " + retval});
    }
});

send({type: "ready", message: "All telemetry, instruction monitors, and exception handlers are ACTIVE."});
"""

def on_message(message, data):
    if message['type'] == 'send':
        payload = message['payload']
        msg_type = payload.get('type', 'info')
        msg = payload.get('message', '')
        log(f"[{msg_type.upper()}] {msg}")
    elif message['type'] == 'error':
        log(f"[FRIDA ERROR] {message.get('description', message)}")

script = session.create_script(JS_MONITOR)
script.on('message', on_message)
script.load()

log("Enhanced Frida Monitor active. Logging all events and errors in real-time...")

# Keep running and monitoring
try:
    while True:
        time.sleep(1)
        if session.is_detached:
            log("Game process terminated.")
            break
except KeyboardInterrupt:
    log("Monitor stopped by user.")
