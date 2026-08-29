// Standalone test for the FName::ToString substitution hook logic.
//
// Simulates exactly what hook_FNameToString does at runtime WITHOUT the game:
//   1. Take a runtime cue FName string (e.g. "Act_E2_..._010_C_2147459937").
//   2. Detect the "_C_<digits>" instance suffix (the hook's gate).
//   3. Resolve the translation via FindTranslation (the DB lookup).
//   4. That resolved text is what the display would show.
//
// Build:
//   cl.exe /O2 /EHsc /std:c++17 /utf-8 tools\test_hook.cpp /Fe:tools\test_hook.exe
//
// Run:
//   tools\test_hook.exe [path\to\master_subtitles_utf16.bin]
#include <windows.h>
#include <cstdio>
#include <string>
#include <vector>
#include <unordered_map>

#include "../src/subtitle_lookup.h"

static std::unordered_map<std::wstring, std::wstring> LoadMasterMap(const wchar_t* binPath) {
    std::unordered_map<std::wstring, std::wstring> map;
    FILE* f = _wfopen(binPath, L"rb");
    if (!f) return map;
    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);
    std::vector<unsigned char> buf((size_t)size);
    if (fread(buf.data(), 1, (size_t)size, f) != (size_t)size) { fclose(f); return map; }
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

// The hook's gate: does this name look like a runtime subtitle cue "..._C_<digits>"?
static bool IsRuntimeCueName(const std::wstring& name) {
    size_t pos = name.rfind(L"_C_");
    if (pos == std::wstring::npos || pos + 3 >= name.length()) return false;
    for (size_t i = pos + 3; i < name.length(); ++i) {
        if (name[i] < L'0' || name[i] > L'9') return false;
    }
    return true;
}

int wmain(int argc, wchar_t** argv) {
    std::wstring binPath = argc > 1 ? argv[1] : L"..\\src\\master_subtitles_utf16.bin";
    auto map = LoadMasterMap(binPath.c_str());
    if (map.empty()) {
        fwprintf(stderr, L"[FATAL] could not load dataset from %s\n", binPath.c_str());
        return 2;
    }
    fwprintf(stderr, L"Dataset loaded: %zu entries\n", map.size());

    int pass = 0, fail = 0;

    // ---- A: the exact failing runtime cues captured from the game sessions.
    const wchar_t* failing[] = {
        L"Act_E2_1A_Dormitory_Shower_VoiceOver01_Max_010_C_2147459937",
        L"Act_E2_1A_Dormitory_Shower_VoiceOver01_Max_010_C_2147459880",
        L"Act_E2_1A_Dormitory_Shower_VoiceOver01_Max_010_C_2147459974",
        L"Act_E2_1A_MaxRoom_VoiceOverReveal_Max_010_C_2147460136",
        L"Act_E2_1A_MaxRoom_PhotoWall_Look01_Max_010_C_2147459722",
        L"Act_E2_1A_MaxRoom_ShowelGel_Interact01_Max_020_C_2147459189",
        L"Act_E2_1A_MaxRoom_Artbooks_Look01_Max_010_C_2147459624",
        L"Act_E2_1A_MaxRoom_PhotoPanel_Look01_Max_010_C_2147459528",
        L"Act_E2_1A_MaxRoom_PhotoPanel_Look01_Max_020_C_2147459527",
        L"Act_E2_1A_MaxRoom_PhotoPanel_Look01_Max_040_C_2147459526",
        L"Act_E2_1A_MaxRoom_MaxNotes_Look01_Max_010_C_2147459391",
    };
    fwprintf(stderr, L"\n--- A) Exact failing runtime cues ---\n");
    for (const wchar_t* cue : failing) {
        std::wstring name(cue);
        bool detected = IsRuntimeCueName(name);
        const wchar_t* text = detected ? FindTranslation(map, name) : nullptr;
        if (text && *text) {
            pass++;
            fwprintf(stderr, L"  OK   %ls\n        -> %ls\n", name.c_str(), text);
        } else {
            fail++;
            fwprintf(stderr, L"  FAIL %ls (detected=%d)\n", name.c_str(), (int)detected);
        }
    }

    // ---- B: every E2 cue key in the fixtures, with a realistic runtime suffix.
    {
        FILE* f = _wfopen(L"fixtures\\e2_cues.txt", L"r, ccs=UTF-8");
        int total = 0, ok = 0, bad = 0, gen = 0;
        if (f) {
            wchar_t line[4096];
            while (fgetws(line, 4096, f)) {
                std::wstring s = line;
                while (!s.empty() && (s.back() == L'\n' || s.back() == L'\r')) s.pop_back();
                if (s.empty()) continue;
                total++;
                std::wstring runtime = s + L"_C_2147459000";
                if (!IsRuntimeCueName(runtime)) { bad++; continue; }
                bool isGen = s.find(L"_GEN_") != std::wstring::npos || s.rfind(L"GEN_", 0) == 0;
                const wchar_t* text = FindTranslation(map, runtime);
                if (text && *text) ok++;
                else if (isGen) gen++;
                else bad++;
            }
            fclose(f);
        }
        fwprintf(stderr, L"\n--- B) All E2 fixture cues (%d) with runtime suffix ---\n", total);
        fwprintf(stderr, L"  resolved=%d gen-skip=%d fail=%d\n", ok, gen, bad);
        pass += ok; fail += bad;
    }

    // ---- C: negative cases the hook must NOT substitute.
    fwprintf(stderr, L"\n--- C) Hook gate negative cases ---\n");
    const wchar_t* neg[] = {
        L"Act_E2_1A_Dormitory_Shower_VoiceOver01_Max_010",   // no suffix
        L"Cue_E2_1A_Bathroom_DialKate_Kate_040_C_",          // no digits
        L"SomeObject_C_2147",                                // not in DB
        L"None",                                             // not a cue
    };
    for (const wchar_t* n : neg) {
        std::wstring name(n);
        bool detected = IsRuntimeCueName(name);
        const wchar_t* text = detected ? FindTranslation(map, name) : nullptr;
        bool shouldNotSub = !detected || !text;
        fwprintf(stderr, L"  %s: %ls (detected=%d, text=%d)\n", shouldNotSub ? L"OK  " : L"FAIL", name.c_str(), (int)detected, text ? 1 : 0);
        if (shouldNotSub) pass++; else fail++;
    }

    fwprintf(stderr, L"\nRESULT: %d ok / %d fail -> %s\n", pass, fail, fail == 0 ? L"HOOK LOGIC CORRECT" : L"FAILURES");
    return fail == 0 ? 0 : 1;
}
