import frida
import time
import sys

d = frida.get_local_device()
print("Scanning for Life is Strange processes in real-time...")
found = []
for p in d.enumerate_processes():
    if "lis" in p.name.lower():
        found.append((p.pid, p.name))
print(f"Currently found: {found}")
