import os, shutil

src_dir = r"D:\Projetos\LiS_Remastered_Subtitle_Mod\src"
mh_dir = os.path.join(src_dir, "minhook")
os.makedirs(os.path.join(mh_dir, "include"), exist_ok=True)
os.makedirs(os.path.join(mh_dir, "hde"), exist_ok=True)

# Move MinHook.h to include/MinHook.h
if os.path.exists(os.path.join(mh_dir, "MinHook.h")):
    shutil.copy(os.path.join(mh_dir, "MinHook.h"), os.path.join(mh_dir, "include", "MinHook.h"))

# Move hde files to hde/
for h in ["hde64.h", "table64.h", "pstdint.h"]:
    src = os.path.join(mh_dir, h)
    if os.path.exists(src):
        shutil.copy(src, os.path.join(mh_dir, "hde", h))

print("Organized MinHook directory.")

# Create xinput.def
def_content = """LIBRARY XINPUT1_3.dll
EXPORTS
    XInputGetState @100
    XInputSetState @101
    XInputGetCapabilities @102
    XInputEnable @103
    XInputGetDSoundAudioDeviceGuids @104
    XInputGetBatteryInformation @108
    XInputGetKeystroke @109
"""
with open(os.path.join(src_dir, "xinput.def"), "w") as f:
    f.write(def_content)

print("Created xinput.def.")
