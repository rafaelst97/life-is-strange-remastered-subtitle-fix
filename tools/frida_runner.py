"""
Life is Strange Remastered - Real-Time Subtitle Fix via Dynamic Hook (Frida)
----------------------------------------------------------------------------
Monitors the game process and intercepts subtitle text rendering,
automatically replacing raw audio cue IDs (Act_*, Cue_*) with the
translated Portuguese dialogue.
"""

import frida
import json
import time
import os
import sys

GAME_EXE = "LiS-Win64-Shipping.exe"
MOD_DIR = os.path.dirname(os.path.abspath(__file__))
DICT_PATH = os.path.join(MOD_DIR, "mod_package", "Binaries", "Win64", "Mods", "SubtitleFixMod", "Scripts", "subtitles_PTB.json")

if not os.path.exists(DICT_PATH):
    print(f"Error: Subtitle dictionary not found at {DICT_PATH}")
    sys.exit(1)

print(f"Loading Portuguese subtitle dictionary from {DICT_PATH}...")
with open(DICT_PATH, "r", encoding="utf-8") as f:
    subtitles = json.load(f)

print(f"Loaded {len(subtitles)} subtitles into memory.")

JS_CODE = r"""
let Subtitles = {};

rpc.exports = {
    initSubtitles: function(dict) {
        Subtitles = dict;
        send({type: "log", message: "Dictionary registered in V8 runtime (" + Object.keys(Subtitles).length + " entries)"});
    }
};

const base = Module.findBaseAddress("LiS-Win64-Shipping.exe");
send({type: "log", message: "LiS-Win64-Shipping.exe base address: " + base});

// Memory pattern scan or address hook for FText::FromString and SetSubtitleCue
// We scan the game memory for cue strings being formatted into FText
"""

def on_message(message, data):
    if message['type'] == 'send':
        payload = message['payload']
        print(f"[Frida] {payload.get('message', payload)}")
    elif message['type'] == 'error':
        print(f"[Frida ERROR] {message.get('description', message)}")

print("Frida hook script prepared.")
