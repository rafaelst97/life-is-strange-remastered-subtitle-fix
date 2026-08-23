import os
import shutil
import subprocess

staging_dir = r"D:\Projetos\LiS_Remastered_Subtitle_Mod\pak_staging"
alt_src_dir = r"C:\Games\Life is Strange Remastered\LIS\Content\AltData"
output_pak = r"C:\Games\Life is Strange Remastered\LIS\Content\Paks\pakchunk99-WindowsNoEditor_P.pak"

# 1. Clean staging directory
if os.path.exists(staging_dir):
    shutil.rmtree(staging_dir)

target_alt = os.path.join(staging_dir, "LiS", "Content", "AltData")
os.makedirs(target_alt, exist_ok=True)

# 2. Only copy PTB, INT, pt-BR, default variants (~200 files total)
copied = 0
for f in os.listdir(alt_src_dir):
    if any(f.endswith(f"_{lang}.cue") for lang in ["PTB", "INT", "pt-BR", "default", "POR", "BRA"]):
        shutil.copy2(os.path.join(alt_src_dir, f), os.path.join(target_alt, f))
        copied += 1

print(f"Staged {copied} key .cue files ({copied * 2.34:.1f} MB) into staging.")

# 3. Pack with repak
cmd = [
    "repak", "pack",
    "--version", "V8B",
    "--mount-point", "../../../",
    staging_dir,
    output_pak
]

print("Executing repak pack...")
res = subprocess.run(cmd, capture_output=True, text=True)
print("Return code:", res.returncode)
print("Stdout:", res.stdout)
print("Stderr:", res.stderr)

if os.path.exists(output_pak):
    sz = os.path.getsize(output_pak)
    print(f"SUCCESS: Created patch PAK: {output_pak} ({sz / (1024*1024):.2f} MB)!")
else:
    print("ERROR: Pak creation failed.")

