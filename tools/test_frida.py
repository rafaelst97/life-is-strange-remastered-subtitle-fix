import frida
import sys

print("Frida version:", frida.__version__)
devices = frida.enumerate_devices()
for d in devices:
    print("Device:", d)
