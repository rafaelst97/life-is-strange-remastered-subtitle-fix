import glob
import os

bak_dir = r"D:\Projetos\LiS_Remastered_Subtitle_Mod\backup_original_AltData"
mods_dir = r"C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\Mods\SubtitleFixMod\Scripts"
os.makedirs(mods_dir, exist_ok=True)

def escape_lua(text):
    return text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '')

for lang in ['PTB', 'INT', 'FRA', 'DEU', 'ESM', 'ESN', 'ITA', 'JPN']:
    files = glob.glob(os.path.join(bak_dir, f"*_{lang}.cue"))
    sub_dict = {}
    for f in files:
        with open(f, 'rb') as fp:
            data = fp.read()
        if data.startswith(b'\xef\xbb\xbf'):
            data = data[3:]
        parts = data.split(b'\x00')
        if parts and parts[-1] == b'':
            parts.pop()
        for i in range(0, len(parts), 2):
            k = parts[i].decode('utf-8', errors='ignore')
            v = parts[i+1].decode('utf-8', errors='ignore')
            sub_dict[k] = v

    lua_path = os.path.join(mods_dir, f"subtitles_{lang}.lua")
    with open(lua_path, 'w', encoding='utf-8') as out:
        out.write("return {\n")
        for k, v in sub_dict.items():
            out.write(f'  ["{escape_lua(k)}"] = "{escape_lua(v)}",\n')
        out.write("}\n")
    print(f"Generated {lua_path}: {len(sub_dict)} keys ({os.path.getsize(lua_path)/1024:.1f} KB)")
