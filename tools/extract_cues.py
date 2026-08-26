import os
import re

log_path = r"C:\Games\Life is Strange Remastered\debug.log"
out_path = os.path.join(os.path.dirname(__file__), "fixtures", "real_cues.txt")

with open(log_path, encoding="utf-8", errors="ignore") as f:
    log = f.read()

cues = re.findall(r"cue='([^']+)'", log)
cues = list(dict.fromkeys(cues))

os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    for c in cues:
        f.write(c + "\n")

print(f"wrote {len(cues)} unique cue names to {out_path}")
