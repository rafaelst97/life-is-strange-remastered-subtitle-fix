// Standalone test for the subtitle lookup logic - runs WITHOUT the game.
// Compiles the exact same subtitle_lookup.h used by the mod DLL and reads the
// exact same master_subtitles_utf16.bin dataset, so it verifies the real
// production code path (minus the in-game hooks).
//
// Build:
//   cl.exe /O2 /EHsc /std:c++17 /utf-8 tools\test_lookup.cpp /Fe:tools\test_lookup.exe
//
// Run:
//   tools\test_lookup.exe [path\to\master_subtitles_utf16.bin] [path\to\real_cues.txt]
#include <windows.h>
#include <cstdio>
#include <string>
#include <vector>
#include <unordered_map>
#include <random>

#include "../src/subtitle_lookup.h"

static bool g_ShowMisses = false;

static std::unordered_map<std::wstring, std::wstring> LoadMasterMap(const wchar_t* binPath) {
    std::unordered_map<std::wstring, std::wstring> map;
    FILE* f = _wfopen(binPath, L"rb");
    if (!f) return map;
    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);
    std::vector<unsigned char> buf((size_t)size);
    if (fread(buf.data(), 1, (size_t)size, f) != (size_t)size) {
        fclose(f);
        return map;
    }
    fclose(f);

    const wchar_t* p = (const wchar_t*)buf.data();
    const wchar_t* end = p + size / sizeof(wchar_t);
    while (p < end && *p != L'\0') {
        std::wstring key = p;
        p += key.length() + 1;
        if (p >= end || *p == L'\0') break;
        std::wstring val = p;
        p += val.length() + 1;
        map[key] = val;
    }
    return map;
}

static std::vector<std::wstring> ReadLines(const wchar_t* path) {
    std::vector<std::wstring> lines;
    FILE* f = _wfopen(path, L"r, ccs=UTF-8");
    if (!f) return lines;
    wchar_t line[4096];
    while (fgetws(line, 4096, f)) {
        std::wstring s = line;
        while (!s.empty() && (s.back() == L'\n' || s.back() == L'\r')) s.pop_back();
        if (!s.empty()) lines.push_back(s);
    }
    fclose(f);
    return lines;
}

int wmain(int argc, wchar_t** argv) {
    std::wstring binPath = argc > 1 ? argv[1] : L"..\\src\\master_subtitles_utf16.bin";
    std::wstring cuesPath = argc > 2 ? argv[2] : L"fixtures\\real_cues.txt";

    auto map = LoadMasterMap(binPath.c_str());
    if (map.empty()) {
        fwprintf(stderr, L"[FATAL] could not load dataset from %s\n", binPath.c_str());
        return 2;
    }
    fwprintf(stderr, L"Dataset loaded: %zu entries\n", map.size());

    int pass = 0, fail = 0;

    // ---- Test 1: every database key round-trips when a UE4 "_C_<digits>"
    //      object suffix is appended (exactly what the game passes at runtime).
    std::mt19937_64 rng(0xC0FFEE);
    for (auto& kv : map) {
        if (kv.first.empty()) continue;
        // append a realistic "_C_<number>" suffix
        std::wstring fname = kv.first + L"_C_" + std::to_wstring((unsigned long long)(rng() % 5000000000ULL + 1000000000ULL));
        const wchar_t* trans = FindTranslation(map, fname);
        if (trans && kv.second == trans) {
            pass++;
        } else {
            fail++;
            if (g_ShowMisses) fwprintf(stderr, L"  MISS round-trip: %s\n", fname.c_str());
        }
    }
    fwprintf(stderr, L"[T1] round-trip all keys with _C_<num> suffix: %d ok / %d fail\n", pass, fail);

    // ---- Test 2: real runtime cue names captured from the game's debug log.
    // Cues prefixed with "GEN_" are generic reaction voice-lines (e.g.
    // "Act_GEN_PositiveSurprise_Max_40") that carry no subtitle text anywhere
    // in the game data, so a miss for them is expected, not a regression.
    int p2 = 0, f2 = 0, skip2 = 0;
    for (auto& cue : ReadLines(cuesPath.c_str())) {
        if (cue.empty() || cue.find(L"_C_") == std::wstring::npos) continue;
        bool isGen = cue.find(L"_GEN_") != std::wstring::npos || cue.rfind(L"GEN_", 0) == 0;
        const wchar_t* trans = FindTranslation(map, cue);
        if (trans && *trans) p2++;
        else if (isGen) { skip2++; if (g_ShowMisses) fwprintf(stderr, L"  SKIP (no subtitle by design): %s\n", cue.c_str()); }
        else { f2++; if (g_ShowMisses) fwprintf(stderr, L"  MISS real: %s\n", cue.c_str()); }
    }
    fwprintf(stderr, L"[T2] real runtime cue names (%d): %d ok / %d fail / %d gen-skip\n", p2 + f2 + skip2, p2, f2, skip2);

    // ---- Test 3: negative cases must return NULL (never crash / never wrong).
    int p3 = 0, f3 = 0;
    const wchar_t* bad[] = {
        L"TotallyNotACue_C_123",
        L"",
        L"Cue_",
        L"_C_999",
        L"E5_7Z",
    };
    for (const wchar_t* b : bad) {
        const wchar_t* trans = FindTranslation(map, b);
        if (!trans) p3++; else { f3++; fwprintf(stderr, L"  NEG unexpected hit: %s -> %s\n", b, trans); }
    }
    fwprintf(stderr, L"[T3] negative cases: %d ok / %d fail\n", p3, f3);

    // ---- Test 4: Spot-check a handful of known subtitle texts.
    struct Spot { const wchar_t* cue; const wchar_t* expectContains; };
    const Spot spots[] = {
        { L"Cue_E5_7B_Diner_CHMaxGhost_Phase01_Max_022_C_2147224982", L"culpa" },
        { L"Cue_E5_7Z_LabyChloe_End_Chloe_090_C_2147222736", L"preocupe" },
        { L"Act_E5_3B_ArtGallery_MaxPicture_Look01_Max_010_C_2147461876", L"artista" },
    };
    int p4 = 0, f4 = 0;
    for (auto& s : spots) {
        const wchar_t* trans = FindTranslation(map, s.cue);
        if (trans && wcsstr(trans, s.expectContains) != nullptr) p4++; else { f4++; fwprintf(stderr, L"  SPOT fail: %s\n", s.cue); }
    }
    fwprintf(stderr, L"[T4] spot-check texts: %d ok / %d fail\n", p4, f4);

    int totalFail = fail + f2 + f3 + f4;
    fwprintf(stderr, L"\nRESULT: %s\n", totalFail == 0 ? L"ALL TESTS PASSED" : L"TESTS FAILED");
    return totalFail == 0 ? 0 : 1;
}
