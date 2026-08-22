// SubtitleFix Frida Hook for Life is Strange Remastered
const fs = require('fs');

console.log("[SubtitleFix] Frida script loaded into LiS-Win64-Shipping.exe!");

// We will receive the subtitle dictionary from Python via send/recv or inline
let Subtitles = {};

rpc.exports = {
    setDictionary: function(dict) {
        Subtitles = dict;
        console.log("[SubtitleFix] Subtitle dictionary loaded with " + Object.keys(Subtitles).length + " entries.");
    }
};

// Base address of the main module
const base = Module.findBaseAddress("LiS-Win64-Shipping.exe");
console.log("[SubtitleFix] Main module base: " + base);

if (base) {
    // Function: GetSubtitleText (VA = base + 0x710100 - wait, RVA = 0x710100)
    // Let's hook 0x710100 (VA = base.add(0x710100) or find function via pattern)
    const getSubtitleTextRVA = 0x710100;
    const targetAddr = base.add(getSubtitleTextRVA);
    console.log("[SubtitleFix] Hooking GetSubtitleText at: " + targetAddr);

    Interceptor.attach(targetAddr, {
        onEnter: function(args) {
            this.rcx = args[0];
            this.rdx = args[1];
            this.r8 = args[2];
            this.r9 = args[3];
            
            try {
                // Try reading FString from rdx or rcx
                // In UE4, FString is { TArray: Data* (8 bytes), Num (4 bytes), Max (4 bytes) }
                let rdx_ptr = this.rdx;
                if (!rdx_ptr.isNull()) {
                    let str_ptr = rdx_ptr.readPointer();
                    if (!str_ptr.isNull()) {
                        let cueName = str_ptr.readUtf16String();
                        this.cueName = cueName;
                        console.log("[SubtitleFix] [CALL] Requested Cue: " + cueName);
                    }
                }
            } catch(e) {
                // Ignore
            }
        },
        onLeave: function(retval) {
            console.log("[SubtitleFix] [RETURN] GetSubtitleText returned: " + retval + " for cue: " + this.cueName);
            if (this.cueName && Subtitles[this.cueName]) {
                let fixedText = Subtitles[this.cueName];
                console.log("[SubtitleFix] [FIXED] Found translation: " + fixedText.substring(0, 40) + "...");
                // Write translation to output FString if needed or set retval = 0
            }
        }
    });
}
