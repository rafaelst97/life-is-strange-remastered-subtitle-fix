import os
import shutil

alt_dir = r"C:\Games\Life is Strange Remastered\LIS\Content\AltData"

# 1. Read our master 10,475 subtitle database (UTF-16LE null-separated)
# We can read it from any consolidated PTB file
sample_ptb = os.path.join(alt_dir, "CU_E1_1A_PTB.cue")
with open(sample_ptb, "rb") as f:
    master_data = f.read()

entries = master_data.count(b'\x00\x00') // 2
print(f"Master Portuguese dataset size: {len(master_data)} bytes ({entries} subtitle pairs)")

# 2. Overwrite EVERY .cue file in AltData with the master Portuguese database
count = 0
for fname in os.listdir(alt_dir):
    if fname.endswith(".cue"):
        fpath = os.path.join(alt_dir, fname)
        with open(fpath, "wb") as f:
            f.write(master_data)
        count += 1

print(f"Overwrote all {count} .cue files in AltData with the master Portuguese database.")

# 3. Also generate pt-BR, POR, BRA, and default variants for every level prefix
# Level prefixes: CU_E1_1A, CU_E1_2A, etc.
prefixes = set()
for fname in os.listdir(alt_dir):
    if fname.startswith("CU_") and fname.endswith(".cue"):
        parts = fname.rsplit("_", 1)
        if len(parts) == 2:
            prefixes.add(parts[0])

extra_count = 0
for prefix in prefixes:
    for suffix in ["pt-BR", "pt_BR", "POR", "BRA", "PT", "default"]:
        target_name = f"{prefix}_{suffix}.cue"
        target_path = os.path.join(alt_dir, target_name)
        if not os.path.exists(target_path):
            with open(target_path, "wb") as f:
                f.write(master_data)
            extra_count += 1

print(f"Created {extra_count} additional language alias .cue files.")
total_now = len([f for f in os.listdir(alt_dir) if f.endswith('.cue')])
print(f"Total .cue files in AltData now: {total_now}")
