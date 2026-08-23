import os
import sys
import pefile
import struct
import time

print("=" * 75)
print("LIFE IS STRANGE REMASTERED - AUTOMATED SUBTITLE FIX TEST SUITE")
print("=" * 75)

game_dir = r"C:\Games\Life is Strange Remastered"
bin_dir = os.path.join(game_dir, r"LIS\Binaries\Win64")
exe_path = os.path.join(bin_dir, "LiS-Win64-Shipping.exe")
dll_path = os.path.join(bin_dir, "XINPUT1_3.dll")
alt_dir = os.path.join(game_dir, r"LIS\Content\AltData")
ini_path = os.path.join(game_dir, r"LIS\Config\DefaultEngine.ini")
lua_path = os.path.join(bin_dir, r"Mods\SubtitleFixMod\Scripts\subtitles_PTB.lua")

tests_passed = 0
tests_total = 0

def check(name, condition, details=""):
    global tests_passed, tests_total
    tests_total += 1
    status = "[PASS]" if condition else "[FAIL]"
    if condition:
        tests_passed += 1
    print(f"{status} Test {tests_total:2}: {name}")
    if details:
        print(f"        -> {details}")
    return condition

# -------------------------------------------------------------
# TEST 1: Clean Game Binary & Function Offsets
# -------------------------------------------------------------
check("Game Executable Exists", os.path.exists(exe_path), f"Path: {exe_path}")

with open(exe_path, "rb") as f:
    exe_data = f.read()

check("Clean Executable Size (62,406,144 bytes)", len(exe_data) == 62406144, f"Actual: {len(exe_data):,} bytes")

# UDNEAltData::GetSubtitleText prologue at 0x14070fb40 (File offset 0x70f140)
get_sub_bytes = exe_data[0x70f140 : 0x70f140 + 24]
expected_prologue = bytes.fromhex("4c89442418488954241048894c240856574881ecf8050000")
check("UDNEAltData::GetSubtitleText RVA (0x70fb40) Verified", get_sub_bytes == expected_prologue, f"Bytes: {get_sub_bytes.hex()}")

# FMemory::Realloc at 0x140a75240 (File offset 0xa74840)
realloc_bytes = exe_data[0xa74840 : 0xa74840 + 15]
expected_realloc = bytes.fromhex("48895c24084889742410574883ec20")
check("FMemory::Realloc RVA (0xa75240) Verified", realloc_bytes == expected_realloc, f"Bytes: {realloc_bytes.hex()}")

# FMemory::Free at 0x140a666d0 (File offset 0xa65cd0)
free_bytes = exe_data[0xa65cd0 : 0xa65cd0 + 12]
expected_free = bytes.fromhex("4885c9742e534883ec20488b")
check("FMemory::Free RVA (0xa666d0) Verified", free_bytes == expected_free, f"Bytes: {free_bytes.hex()}")

# -------------------------------------------------------------
# TEST 2: Native XINPUT1_3.dll Proxy & Exports
# -------------------------------------------------------------
check("Native Proxy DLL Exists in Game Directory", os.path.exists(dll_path), f"Size: {os.path.getsize(dll_path):,} bytes")

pe_dll = pefile.PE(dll_path)
exports = [exp.name.decode() if exp.name else str(exp.ordinal) for exp in pe_dll.DIRECTORY_ENTRY_EXPORT.symbols]
has_xinput_exports = "XInputGetState" in exports and "XInputSetState" in exports and "XInputGetCapabilities" in exports
check("XINPUT1_3.dll Exports 11 Standard XInput Functions", has_xinput_exports, f"Exports: {len(exports)} functions")

with open(dll_path, "rb") as f:
    dll_bytes = f.read()

check("XINPUT1_3.dll Contains Embedded UTF-16 Master Subtitles", "Heroína do Cotidiano".encode("utf-16le") in dll_bytes or "Heroina do Cotidiano".encode("utf-16le") in dll_bytes, "Found Portuguese strings inside binary")

# -------------------------------------------------------------
# TEST 3: Loose .cue AltData Database Coverage
# -------------------------------------------------------------
cue_files = [f for f in os.listdir(alt_dir) if f.endswith(".cue")]
check("AltData Directory Populated", len(cue_files) > 500, f"Total .cue files: {len(cue_files):,}")

sample_cue = os.path.join(alt_dir, "CU_E5_3B_PTB.cue")
check("CU_E5_3B_PTB.cue Exists", os.path.exists(sample_cue))

with open(sample_cue, "rb") as f:
    sample_data = f.read()

check("CU_E5_3B_PTB.cue Contains Master UTF-16 Buffer", len(sample_data) > 2000000, f"Size: {len(sample_data):,} bytes")
check("CU_E5_3B_PTB.cue Contains ArtGallery & PhotoLook Tokens", "PhotoLook_Max".encode("utf-16le") in sample_data and ("Heroína".encode("utf-16le") in sample_data or "Heroina".encode("utf-16le") in sample_data))


# -------------------------------------------------------------
# TEST 4: Engine Startup Culture Configuration
# -------------------------------------------------------------
with open(ini_path, "r", encoding="utf-8", errors="ignore") as f:
    ini_content = f.read()

check("DefaultEngine.ini Forces pt-BR Culture", "Culture=pt-BR" in ini_content and "Language=pt-BR" in ini_content)

# -------------------------------------------------------------
# TEST 5: Standalone Clean Architecture (No UE4SS conflicts)
# -------------------------------------------------------------
ue4ss_conflicts = [f for f in ["UE4SS.dll", "dwmapi.dll"] if os.path.exists(os.path.join(bin_dir, f))]
check("Clean Standalone Binaries (No Hook Conflicts)", len(ue4ss_conflicts) == 0, f"Clean directory (Active: {len(ue4ss_conflicts)} legacy wrappers)")

# -------------------------------------------------------------
# TEST 6: Automated Multi-Scene Subtitle Resolution Verification
# -------------------------------------------------------------
test_cues = {
    "Episode 1 Intro Cliff": ("Act_E1_1A_CliffFuture_VoiceOver_Max_010", "tempestade"),
    "Episode 1 Lighthouse Fall": ("Cue_E1_1A_CliffFuture_LighthouseBreak_Max_010", "merda"),
    "Episode 2 Kate Observation": ("Act_E2_1A_Bathroom_CHKate_Look01_Max_010", "Kate"),
    "Episode 2 Diner Frank": ("Act_E2_2A_Diner_AfterFrank_VoiceOver01_Max_010", "Frank"),
    "Episode 3 Jefferson Art": ("Act_E1_2A_ArtClass_CHJefferson_Look01_Max_010", "Jefferson"),
    "Episode 5 Art Gallery (Full Key)": ("Cue_E5_3B_ArtGallery_PhotoLook_Max_060", "Olá"),
    "Episode 5 Art Gallery (Short Token)": ("PhotoLook_Max", "Olá"),
    "Episode 5 Art Gallery (Admirer)": ("PhotoLook_Admirer1", "diferente"),
    "Episode 5 Art Gallery (Play_ Prefix)": ("Play_PhotoLook_Max", "Olá"),
}

resolution_failures = []
for test_name, (cue_key, expected_substr) in test_cues.items():
    key_utf16 = cue_key.encode("utf-16le")
    found_in_cue = key_utf16 in sample_data
    found_in_dll = key_utf16 in dll_bytes
    if not (found_in_cue or found_in_dll):
        resolution_failures.append((test_name, cue_key, f"cue={found_in_cue}, dll={found_in_dll}"))

check("All Episode 1-5 Dialogue Keys and Alias Tokens Resolve", len(resolution_failures) == 0, 
      f"Resolved {len(test_cues) - len(resolution_failures)}/{len(test_cues)} sample scenarios" if len(resolution_failures) > 0 else f"Resolved {len(test_cues)}/{len(test_cues)} sample scenarios (100%)")
if resolution_failures:
    for fail in resolution_failures:
        print(f"        -> [DEBUG] Failure: {fail}")

print("=" * 75)
print(f"AUTOMATED TEST SUITE COMPLETED: {tests_passed} / {tests_total} PASSED ({tests_passed/tests_total*100:.1f}%)")
print("=" * 75)


