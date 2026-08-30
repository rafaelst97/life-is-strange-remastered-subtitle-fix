"""DEFINITIVE BUG ANALYSIS AND SIMULATION

Based on deep disassembly of GetLocalizedText (RVA 0x767d40, 11556 bytes):

The function does the following:
1. Receives a cue name key like "Cue_E5_3B_ArtGallery_PhotoLook_Max_060"
2. Checks if it starts with "Cue" or "Act" (prefix stripping)
3. After stripping the prefix, extracts episode+layer pattern:
   - Parses "E5_3B" from "_E5_3B_ArtGallery_..."
   - Constructs INI filename: "CU_E5_3B"
   - Constructs full path: "Episode05__CU_E5_3B"
4. Loads that INI file and looks up the key in the [Cues] section
5. If not found, returns false with Out = "?key?"

THE BUG: When UE4 spawns cue actors at runtime, it appends "_C_<digits>" 
making the name e.g. "Cue_E5_3B_ArtGallery_PhotoLook_Max_060_C_2147461877"

The _C_<digits> suffix breaks TWO things:
A) The key lookup in [Cues] section (key doesn't match)
B) Potentially the episode/layer EXTRACTION - the parser may not correctly
   extract "E5_3B" from the modified name

The current mod only hooks GetLocalizedText and strips _C_<digits> from the
key parameter before retrying. But the question is: does this actually work?

Let's simulate EXACTLY what the game does by:
1. Parsing the localization INI files from the pak
2. Running the same lookup logic the game uses
3. Testing with real failing cue names
"""

import os
import sys
import re
from collections import defaultdict

# =========================================================================
# 1. Parse AltData .cue files (these have the same keys as the INI files)
# =========================================================================
ALTDATA_DIR = r'C:\Games\Life is Strange Remastered\LIS\Content\AltData'

def parse_cue_file(path):
    """Parse a .cue file (null-separated key/value pairs)"""
    data = open(path, 'rb').read()
    text = data.decode('utf-8-sig')
    parts = text.split('\x00')
    result = {}
    for i in range(0, len(parts) - 1, 2):
        key = parts[i].strip()
        val = parts[i+1].strip() if i+1 < len(parts) else ''
        if key:
            result[key] = val
    return result

# Load all INT cue files (English - base language)
int_tables = {}  # layer_name -> {key: value}
ptb_tables = {}  # Portuguese
all_int_keys = set()

for fname in os.listdir(ALTDATA_DIR):
    if fname.endswith('.cue'):
        parts_name = fname[:-4]  # e.g., CU_E2_1A_INT
        # Extract language code (last part after last _)
        segments = parts_name.split('_')
        lang = segments[-1]
        layer = '_'.join(segments[:-1])  # e.g., CU_E2_1A
        
        path = os.path.join(ALTDATA_DIR, fname)
        entries = parse_cue_file(path)
        
        if lang == 'INT':
            int_tables[layer] = entries
            all_int_keys.update(entries.keys())
        elif lang == 'PTB':
            ptb_tables[layer] = entries

print(f"Loaded {len(int_tables)} INT layers, {len(ptb_tables)} PTB layers")
print(f"Total INT keys: {len(all_int_keys)}")

# =========================================================================
# 2. Simulate GetLocalizedText's key parsing logic
# =========================================================================
def simulate_get_localized_text(key, tables):
    """Simulate the game's GetLocalizedText logic.
    
    Based on disassembly, it:
    1. Strips "Cue_" or "Act_" prefix
    2. Extracts episode and layer (e.g., E5_3B)
    3. Constructs INI filename: CU_E5_3B
    4. Looks up the key in that table's [Cues] section
    """
    # Step 1: Determine the prefix and what comes after
    remainder = None
    if key.startswith('Cue_'):
        remainder = key[4:]  # Strip "Cue_"
    elif key.startswith('Act_'):
        remainder = key[4:]  # Strip "Act_"
    else:
        # GEN or other patterns
        remainder = key
    
    if not remainder:
        return None, "empty_remainder"
    
    # Step 2: Extract episode and layer
    # The game looks for the pattern E<digit>_<layer>_...
    # Format: E5_3B means Episode 5, Layer 3B
    m = re.match(r'(E\d+_\w+?)_', remainder)
    if not m:
        return None, "no_episode_layer_match"
    
    episode_layer = m.group(1)
    
    # The game constructs: CU_<episode_layer>
    # But episode_layer is like "E5_3B" - extracted from "E5_3B_ArtGallery_..."
    # The tricky part: how many underscore-separated tokens does the game take?
    # From the cue files, layers are like: CU_E2_1A, CU_E5_3B, CU_E1_5A
    # So it takes exactly: E<digit>_<alphanumeric>
    
    # Let's try to match exactly what the game does
    parts = remainder.split('_')
    if len(parts) < 2:
        return None, "too_few_parts"
    
    # Episode number: E<digit(s)>
    episode_part = parts[0]  # e.g., "E5"
    layer_part = parts[1]    # e.g., "3B" or "1A"
    
    # Construct the table name
    table_name = f"CU_{episode_part}_{layer_part}"
    
    # Step 3: Look up in the table
    if table_name in tables:
        if key in tables[table_name]:
            return tables[table_name][key], "found"
        else:
            return None, f"key_not_in_table_{table_name}"
    else:
        return None, f"table_not_found_{table_name}"

# =========================================================================
# 3. Test with real failing cue names (captured from game)
# =========================================================================
with open(r'D:\Projetos\LiS_Remastered_Subtitle_Mod\tools\fixtures\real_cues.txt') as f:
    real_cues = [line.strip() for line in f if line.strip()]

print(f"\n{'='*80}")
print(f"TEST 1: Direct lookup of decorated cue names (the bug scenario)")
print(f"{'='*80}")

found_direct = 0
not_found_direct = 0
reasons = defaultdict(int)

for cue in real_cues[:20]:  # Test first 20
    val, reason = simulate_get_localized_text(cue, int_tables)
    if val:
        found_direct += 1
    else:
        not_found_direct += 1
        reasons[reason] += 1
        print(f"  MISS: {cue}")
        print(f"        reason: {reason}")

for cue in real_cues[20:]:
    val, reason = simulate_get_localized_text(cue, int_tables)
    if val:
        found_direct += 1
    else:
        not_found_direct += 1
        reasons[reason] += 1

print(f"\nDirect lookup: {found_direct} found, {not_found_direct} not found")
print(f"Reasons for failure: {dict(reasons)}")

# =========================================================================
# 4. Test with stripped cue names (the mod's approach)
# =========================================================================
print(f"\n{'='*80}")
print(f"TEST 2: Lookup after stripping _C_<digits> suffix (mod approach)")
print(f"{'='*80}")

def strip_object_suffix(s):
    """Python equivalent of StripObjectSuffix from subtitle_lookup.h"""
    pos = s.rfind('_C_')
    if pos == -1 or pos + 3 >= len(s):
        return s
    suffix = s[pos+3:]
    if suffix.isdigit():
        return s[:pos]
    return s

found_stripped = 0
not_found_stripped = 0
stripped_reasons = defaultdict(int)

for cue in real_cues[:20]:
    stripped = strip_object_suffix(cue)
    val, reason = simulate_get_localized_text(stripped, int_tables)
    if val:
        found_stripped += 1
    else:
        not_found_stripped += 1
        stripped_reasons[reason] += 1
        print(f"  STILL MISS: {cue}")
        print(f"    stripped:  {stripped}")
        print(f"    reason:    {reason}")

for cue in real_cues[20:]:
    stripped = strip_object_suffix(cue)
    val, reason = simulate_get_localized_text(stripped, int_tables)
    if val:
        found_stripped += 1
    else:
        not_found_stripped += 1
        stripped_reasons[reason] += 1

print(f"\nStripped lookup: {found_stripped} found, {not_found_stripped} not found")
print(f"Reasons for failure: {dict(stripped_reasons)}")

# =========================================================================
# 5. Test Portuguese (PTB) - where the bug is more frequent
# =========================================================================
print(f"\n{'='*80}")
print(f"TEST 3: Portuguese (PTB) lookup with stripped names")
print(f"{'='*80}")

found_ptb = 0
not_found_ptb = 0
ptb_reasons = defaultdict(int)

for cue in real_cues[:20]:
    stripped = strip_object_suffix(cue)
    val, reason = simulate_get_localized_text(stripped, ptb_tables)
    if val:
        found_ptb += 1
    else:
        not_found_ptb += 1
        ptb_reasons[reason] += 1
        print(f"  PTB MISS: {stripped}")
        print(f"    reason:  {reason}")

for cue in real_cues[20:]:
    stripped = strip_object_suffix(cue)
    val, reason = simulate_get_localized_text(stripped, ptb_tables)
    if val:
        found_ptb += 1
    else:
        not_found_ptb += 1
        ptb_reasons[reason] += 1

print(f"\nPTB lookup: {found_ptb} found, {not_found_ptb} not found out of {len(real_cues)}")
print(f"PTB reasons: {dict(ptb_reasons)}")

# =========================================================================
# 6. Cross-check: are all INT keys present in PTB?
# =========================================================================
print(f"\n{'='*80}")
print(f"TEST 4: Key coverage INT vs PTB")
print(f"{'='*80}")

for layer in sorted(int_tables.keys()):
    int_keys = set(int_tables[layer].keys())
    if layer in ptb_tables:
        ptb_keys = set(ptb_tables[layer].keys())
        missing = int_keys - ptb_keys
        extra = ptb_keys - int_keys
        if missing:
            print(f"  {layer}: {len(missing)} keys in INT but not PTB (first 3: {list(missing)[:3]})")
        if extra:
            print(f"  {layer}: {len(extra)} keys in PTB but not INT (first 3: {list(extra)[:3]})")
    else:
        print(f"  {layer}: EXISTS in INT but NOT in PTB!")

# =========================================================================
# 7. CRITICAL: Test the actual hook behavior - simulate what happens
#    when the hook receives the key, strips it, and retries
# =========================================================================
print(f"\n{'='*80}")
print(f"TEST 5: Simulate hook behavior (like hook_GetLocalizedText)")
print(f"{'='*80}")

def simulate_hook(key, tables):
    """Simulate what hook_GetLocalizedText does"""
    # First try: original game lookup
    val, reason = simulate_get_localized_text(key, tables)
    if val:
        return val, "original_found"
    
    # Hook: strip suffix and retry
    stripped = strip_object_suffix(key)
    if stripped == key:
        return None, f"no_suffix_to_strip:{reason}"
    
    val2, reason2 = simulate_get_localized_text(stripped, tables)
    if val2:
        return val2, "hook_resolved"
    else:
        return None, f"hook_failed:{reason2}"

# Test with all real cues in INT
hook_results = defaultdict(int)
for cue in real_cues:
    val, result = simulate_hook(cue, int_tables)
    hook_results[result] += 1

print("INT hook simulation:")
for k, v in sorted(hook_results.items()):
    print(f"  {k}: {v}")

# Test with all real cues in PTB
hook_results_ptb = defaultdict(int)
for cue in real_cues:
    val, result = simulate_hook(cue, ptb_tables)
    hook_results_ptb[result] += 1

print("\nPTB hook simulation:")
for k, v in sorted(hook_results_ptb.items()):
    print(f"  {k}: {v}")

# =========================================================================
# 8. Generate a comprehensive list of ALL patterns in the real cues
# =========================================================================
print(f"\n{'='*80}")
print(f"TEST 6: Pattern analysis of all failing cue names")
print(f"{'='*80}")

prefixes = defaultdict(int)
layers_seen = defaultdict(int)
for cue in real_cues:
    stripped = strip_object_suffix(cue)
    # Get prefix
    if stripped.startswith('Cue_'):
        prefix = 'Cue'
    elif stripped.startswith('Act_'):
        prefix = 'Act'
    else:
        prefix = stripped.split('_')[0]
    prefixes[prefix] += 1
    
    # Get layer
    parts = stripped.split('_')
    if len(parts) >= 3:
        layer = f"CU_{parts[1]}_{parts[2]}"  # CU_E5_3B
        layers_seen[layer] += 1

print("Prefixes:", dict(prefixes))
print("\nLayers used:")
for layer in sorted(layers_seen.keys()):
    exists_int = layer in int_tables
    exists_ptb = layer in ptb_tables
    print(f"  {layer}: {layers_seen[layer]} cues (INT:{exists_int}, PTB:{exists_ptb})")
