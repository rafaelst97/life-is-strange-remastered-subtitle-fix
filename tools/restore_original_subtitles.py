"""
Life is Strange Remastered - Subtitle Mod Uninstaller / Restorer
----------------------------------------------------------------
Restores original AltData and Binaries/Win64 files from backup.
"""

import os
import shutil

GAME_DIR = r"C:\Games\Life is Strange Remastered"
ALT_DATA_DIR = os.path.join(GAME_DIR, "LIS", "Content", "AltData")
BIN_DIR = os.path.join(GAME_DIR, "LIS", "Binaries", "Win64")
BACKUP_ALT = os.path.join(os.path.dirname(__file__), "backup_original_AltData")
BACKUP_BIN = os.path.join(os.path.dirname(__file__), "backup_Binaries_Win64")

def restore():
    print(f"Restoring AltData from: {BACKUP_ALT}")
    if os.path.exists(BACKUP_ALT):
        count = 0
        for filename in os.listdir(BACKUP_ALT):
            src = os.path.join(BACKUP_ALT, filename)
            dst = os.path.join(ALT_DATA_DIR, filename)
            shutil.copy2(src, dst)
            count += 1
        print(f"Restored {count} AltData files.")

    # Remove UE4SS files added to Binaries/Win64
    ue4ss_items = ["Mods", "dwmapi.dll", "UE4SS.dll", "UE4SS-settings.ini", "Changelog.md", "README.md", "UE4SS.log"]
    for item in ue4ss_items:
        p = os.path.join(BIN_DIR, item)
        if os.path.exists(p):
            if os.path.isdir(p):
                shutil.rmtree(p, ignore_errors=True)
            else:
                os.remove(p)
            print(f"Removed {item} from Binaries/Win64.")

    print("\nMod uninstalled and original state restored successfully.")

if __name__ == "__main__":
    restore()
