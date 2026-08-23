import os
import shutil
import subprocess

staging_dir = r"D:\Projetos\LiS_Remastered_Subtitle_Mod\pak_staging"
alt_src_dir = r"C:\Games\Life is Strange Remastered\LIS\Content\AltData"
output_pak = r"C:\Games\Life is Strange Remastered\LIS\Content\Paks\pakchunk99-WindowsNoEditor_P.pak"

# 1. Clean staging directory
if os.path.exists(staging_dir):
    shutil.rmtree(staging_dir)

# 2. Create LiS/Content/AltData in staging
target_alt = os.path.join(staging_dir, "LiS", "Content", "AltData")
os.makedirs(target_alt, exist_ok=True)

# 3. Copy all .cue files to staging
cue_count = 0
for f in os.listdir(alt_src_dir):
    if f.endswith(".cue"):
        shutil.copy2(os.path.join(alt_src_dir, f), os.path.join(target_alt, f))
        cue_count += 1

print(f"Staged {cue_count} master .cue files into {target_alt}")

# 4. Add Config files
config_dir = os.path.join(staging_dir, "LiS", "Config")
os.makedirs(config_dir, exist_ok=True)

ini_content = """[Internationalization]
Culture=pt-BR
Language=pt-BR
Locale=pt-BR

[Internationalization.AutoEnable]
Culture=pt-BR
Language=pt-BR

[Internationalization.AssetGroupCultures]
+Audio=pt-BR
+Text=pt-BR
"""
with open(os.path.join(config_dir, "DefaultEngine.ini"), "w", encoding="utf-8") as fp:
    fp.write(ini_content)

# 5. Pack with repak
cmd = [
    "repak", "pack",
    "--version", "V8B",
    "--mount-point", "../../../",
    staging_dir,
    output_pak
]

print("Running command:", " ".join(cmd))
res = subprocess.run(cmd, capture_output=True, text=True)
print("repak stdout:", res.stdout)
print("repak stderr:", res.stderr)
print("Return code:", res.returncode)

if os.path.exists(output_pak):
    print(f"SUCCESS: Created official patch PAK: {output_pak} ({os.path.getsize(output_pak)} bytes)!")
else:
    print("ERROR: Pak file was not created.")

