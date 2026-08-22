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

with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write("=== Life is Strange Remastered - Robust Live Telemetry Monitor ===\n")

log("Active process scanner started. Waiting for LiS-Win64-Shipping.exe...")

d = frida.get_local_device()
session = None
target_pid = None

while session is None:
    try:
        for p in d.enumerate_processes():
            if "lis-win64-shipping" in p.name.lower() or "lis.exe" in p.name.lower():
                log(f"Detected game process: PID {p.pid} ({p.name})")
                if "shipping" in p.name.lower():
                    target_pid = p.pid
                    break
        if target_pid:
            log(f"Attaching to target PID {target_pid}...")
            session = d.attach(target_pid)
            log(f"SUCCESS: Attached to PID {target_pid}!")
            break
    except Exception as e:
        log(f"Waiting / Retrying: {e}")
    time.sleep(0.3)

JS_MONITOR = r"""
const base = Module.findBaseAddress("LiS-Win64-Shipping.exe");
send({type: "info", message: "LiS-Win64-Shipping.exe Base Address: " + base});

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

// 1. Hook FindAltDataSetByLayerName (RVA 0x715a00)
const fnFindAltDataSet = base.add(0x715a00);
Interceptor.attach(fnFindAltDataSet, {
    onEnter: function(args) {
        let layerName = readFString(args[2]);
        send({type: "layer_req", message: "FindAltDataSetByLayerName for Layer: '" + layerName + "'"});
    },
    onLeave: function(retval) {
        send({type: "layer_res", message: "FindAltDataSetByLayerName returned: " + retval});
    }
});

// 2. Hook GetSubtitleText (RVA 0x710100)
const fnGetSubtitleText = base.add(0x710100);
Interceptor.attach(fnGetSubtitleText, {
    onEnter: function(args) {
        this.cueStr = readFString(args[1]);
        send({type: "cue_req", message: ">> [SUBTITLE REQUEST] Cue: '" + this.cueStr + "'"});
    },
    onLeave: function(retval) {
        send({type: "cue_res", message: "<< [SUBTITLE RESULT] Ret=" + retval + " for Cue: '" + this.cueStr + "'"});
    }
});

send({type: "ready", message: "Real-time telemetry instrumentation active in game process!"});
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

log("Instrumentation active! Monitoring live subtitle execution...")

while True:
    time.sleep(1)
    if session.is_detached:
        log("Game process closed.")
        break
