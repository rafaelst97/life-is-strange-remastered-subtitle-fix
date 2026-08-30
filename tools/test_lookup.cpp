// Standalone regression test for the cue-name normalization the mod ships.
// Runs without the game.
//
// It compiles the exact src/subtitle_lookup.h used by XINPUT1_3.dll and checks
// it against two fixtures taken from the real game:
//
//   fixtures/subtitle_keys.txt - every localization key shipped in
//       LIS/Content/Packages/Localization/en/*.ini (extracted from pakchunk0)
//   fixtures/real_cues.txt     - cue names captured on screen while the bug
//       was reproducing, i.e. the strings the game failed to resolve
//
// Two properties must hold for the fix to be both effective and safe:
//   1. every captured on-screen name with a "_C_<digits>" suffix resolves to a
//      real key once the suffix is stripped;
//   2. no real key is altered by the strip.
//
// Build: tools\build_test.bat      Run: tools\test_lookup.exe
#include <cstdio>
#include <fstream>
#include <string>
#include <unordered_set>
#include <vector>

#include "../src/subtitle_lookup.h"

static std::vector<std::wstring> LoadLines(const char* path) {
    std::vector<std::wstring> lines;
    std::ifstream in(path, std::ios::binary);
    if (!in) {
        printf("[FAIL] cannot open %s\n", path);
        return lines;
    }
    std::string line;
    while (std::getline(in, line)) {
        while (!line.empty() && (line.back() == '\r' || line.back() == '\n')) line.pop_back();
        if (line.empty() || line[0] == '#') continue;
        // Keys and cue names are ASCII; widen directly.
        lines.emplace_back(line.begin(), line.end());
    }
    return lines;
}

int main(int argc, char** argv) {
    const char* keysPath = argc > 1 ? argv[1] : "fixtures/subtitle_keys.txt";
    const char* cuesPath = argc > 2 ? argv[2] : "fixtures/real_cues.txt";

    std::vector<std::wstring> keyList = LoadLines(keysPath);
    std::vector<std::wstring> cueList = LoadLines(cuesPath);
    if (keyList.empty() || cueList.empty()) return 1;

    std::unordered_set<std::wstring> keys(keyList.begin(), keyList.end());
    printf("loaded %zu localization keys, %zu captured cue names\n",
           keys.size(), cueList.size());

    int decorated = 0, resolved = 0, unresolved = 0;
    for (const std::wstring& cue : cueList) {
        if (!HasObjectSuffix(cue)) continue;
        ++decorated;
        std::wstring stripped = StripObjectSuffix(cue);
        if (keys.count(stripped)) {
            ++resolved;
        } else if (++unresolved <= 5) {
            printf("  unresolved: %ls -> %ls\n", cue.c_str(), stripped.c_str());
        }
    }
    printf("captured names with a _C_<digits> suffix: %d, resolved after strip: %d\n",
           decorated, resolved);

    int damaged = 0;
    for (const std::wstring& key : keys) {
        if (StripObjectSuffix(key) != key && ++damaged <= 5) {
            printf("  key altered by strip: %ls\n", key.c_str());
        }
    }
    printf("real keys altered by the strip: %d\n", damaged);

    bool ok = decorated > 0 && unresolved == 0 && damaged == 0;
    printf("%s\n", ok ? "[PASS]" : "[FAIL]");
    return ok ? 0 : 1;
}
