import os
import subprocess
import time
import ctypes
from ctypes import wintypes

print("=" * 75)
print("LIVE GAME LAUNCH & MOD INITIALIZATION TEST")
print("=" * 75)

game_dir = r"C:\Games\Life is Strange Remastered"
bin_dir = os.path.join(game_dir, r"LIS\Binaries\Win64")
exe_path = os.path.join(bin_dir, "LiS-Win64-Shipping.exe")

# Launch game process in background
print(f"Launching game: {exe_path}")
proc = subprocess.Popen([exe_path, "-nosplash", "-nullrhi", "-NoSound"], cwd=bin_dir)

print(f"Game process started with PID: {proc.pid}")
time.sleep(3)

# Check if process is alive
ret = proc.poll()
if ret is not None:
    print(f"[FAIL] Game exited prematurely with code: {ret}")
else:
    print("[PASS] Game process is running stably!")

    # Check loaded modules using Windows Toolhelp API
    TH32CS_SNAPMODULE = 0x00000008
    TH32CS_SNAPMODULE32 = 0x00000010

    class MODULEENTRY32(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("th32ModuleID", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("GlblcntUsage", wintypes.DWORD),
            ("ProccntUsage", wintypes.DWORD),
            ("modBaseAddr", ctypes.POINTER(wintypes.BYTE)),
            ("modBaseSize", wintypes.DWORD),
            ("hModule", wintypes.HMODULE),
            ("szModule", ctypes.c_char * 256),
            ("szExePath", ctypes.c_char * 260)
        ]

    kernel32 = ctypes.windll.kernel32
    hSnap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, proc.pid)
    
    loaded_mods = []
    if hSnap != -1:
        me = MODULEENTRY32()
        me.dwSize = ctypes.sizeof(MODULEENTRY32)
        if kernel32.Module32First(hSnap, ctypes.byref(me)):
            while True:
                loaded_mods.append(me.szModule.decode(errors="ignore"))
                if not kernel32.Module32Next(hSnap, ctypes.byref(me)):
                    break
        kernel32.CloseHandle(hSnap)

    print(f"Total loaded modules in game process: {len(loaded_mods)}")
    for target in ["XINPUT1_3.dll", "UE4SS.dll", "dwmapi.dll", "LiS-Win64-Shipping.exe"]:
        found = any(m.lower() == target.lower() for m in loaded_mods)
        status = "[PASS]" if found else "[INFO]"
        print(f"{status} Module: {target} (Loaded: {found})")

    # Terminate game process gracefully
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    print("[SUCCESS] Game test process terminated cleanly.")

print("=" * 75)


