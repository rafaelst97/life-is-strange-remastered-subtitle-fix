import glob
import os

bak_dir = r"D:\Projetos\LiS_Remastered_Subtitle_Mod\backup_original_AltData"
mods_dir = r"C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\Mods\SubtitleFixMod\Scripts"
os.makedirs(mods_dir, exist_ok=True)

def escape_lua(text):
    return text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '')

def expand_aliases(sub_dict):
    expanded = {}
    for k, v in sub_dict.items():
        if not k or not v: continue
        expanded[k] = v
        expanded[f"Play_{k}"] = v
        
        clean_k = k
        if k.startswith("Cue_") or k.startswith("Act_"):
            clean_k = k[4:]
            expanded[clean_k] = v
            expanded[f"Play_{clean_k}"] = v
        
        parts = clean_k.split("_")
        if len(parts) >= 3 and parts[0].startswith("E") and len(parts[0]) <= 3:
            no_ep = "_".join(parts[2:])
            if no_ep not in expanded:
                expanded[no_ep] = v
                expanded[f"Play_{no_ep}"] = v
            if len(parts) >= 4:
                action = "_".join(parts[3:])
                if action not in expanded:
                    expanded[action] = v
                    expanded[f"Play_{action}"] = v
                if parts[-1].isdigit():
                    action_no_num = "_".join(parts[3:-1])
                    if action_no_num not in expanded:
                        expanded[action_no_num] = v
                        expanded[f"Play_{action_no_num}"] = v
    return expanded

dest_dirs = [
    r"C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\Mods\SubtitleFixMod\Scripts",
    r"D:\Projetos\LiS_Remastered_Subtitle_Mod\mod_package\Binaries\Win64\Mods\SubtitleFixMod\Scripts"
]

for d in dest_dirs:
    os.makedirs(d, exist_ok=True)

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

    expanded = expand_aliases(sub_dict)
    
    for d in dest_dirs:
        lua_path = os.path.join(d, f"subtitles_{lang}.lua")
        with open(lua_path, 'w', encoding='utf-8') as out:
            out.write("return {\n")
            for k, v in expanded.items():
                out.write(f'  ["{escape_lua(k)}"] = "{escape_lua(v)}",\n')
            out.write("}\n")
    print(f"Generated subtitles_{lang}.lua: {len(expanded)} entries ({os.path.getsize(os.path.join(dest_dirs[0], f'subtitles_{lang}.lua'))/1024:.1f} KB)")

