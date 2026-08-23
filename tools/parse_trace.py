import csv
import os
import sys

csv_path = r"D:\Projetos\LiS_Remastered_Subtitle_Mod\trace.csv"

if not os.path.exists(csv_path):
    print(f"File {csv_path} not found.")
    sys.exit(0)

print(f"=== PARSING PROCMON TRACE LOG ({csv_path}) ===")

found_events = []
with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
    reader = csv.reader(f)
    headers = next(reader, None)
    for row in reader:
        if len(row) < 7: continue
        proc = row[1]
        operation = row[3]
        path = row[4]
        result = row[5]
        detail = row[6]

        if "LiS" in proc or "Shipping" in proc:
            if "AltData" in path or ".cue" in path or "Localization" in path or "Config" in path:
                found_events.append((proc, operation, path, result, detail))

print(f"Found {len(found_events)} relevant I/O events from LiS-Win64-Shipping.exe:")
for ev in found_events[:50]:
    print(f"[{ev[1]}] {ev[2]} -> {ev[3]} ({ev[4]})")

