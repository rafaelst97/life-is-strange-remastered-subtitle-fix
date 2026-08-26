// Shared subtitle lookup logic used both by the proxy DLL and by the
// standalone test harness (tools/test_lookup.cpp). Kept header-only so the
// exact code under test is the exact code shipped in the mod.
#pragma once

#include <string>
#include <unordered_map>

// The runtime cue FName normally carries a UE4 object instance suffix such as
// "Cue_E5_7Z_..._010_C_2147222737". Strip the trailing "_C_<digits>" so the key
// matches the master subtitle database.
static inline std::wstring StripObjectSuffix(const std::wstring& s) {
    size_t pos = s.rfind(L"_C_");
    if (pos != std::wstring::npos && pos + 3 < s.length()) {
        bool allDigits = true;
        for (size_t i = pos + 3; i < s.length(); ++i) {
            if (s[i] < L'0' || s[i] > L'9') { allDigits = false; break; }
        }
        if (allDigits) return s.substr(0, pos);
    }
    return s;
}

static inline const wchar_t* FindTranslation(
    const std::unordered_map<std::wstring, std::wstring>& subtitleMap,
    const std::wstring& rawCue) {
    if (subtitleMap.empty()) return nullptr;

    std::wstring cue = StripObjectSuffix(rawCue);

    // 1) Direct lookup against the canonical key.
    auto it = subtitleMap.find(cue);
    if (it != subtitleMap.end()) return it->second.c_str();

    // 2) Strip leading "Play_" / "Cue_" / "Act_" prefixes and retry.
    static const wchar_t* kPrefixes[] = { L"Play_", L"Cue_", L"Act_" };
    for (const wchar_t* p : kPrefixes) {
        size_t plen = wcslen(p);
        if (cue.compare(0, plen, p) == 0) {
            it = subtitleMap.find(cue.substr(plen));
            if (it != subtitleMap.end()) return it->second.c_str();
        }
    }

    // 3) Progressive suffix matching: drop leading scene/layer tokens until a
    //    shorter alias (e.g. "VoiceOver_Max_010") is found in the database.
    size_t start = 0;
    while ((start = cue.find(L'_', start)) != std::wstring::npos) {
        size_t next = start + 1;
        if (next >= cue.length()) break;
        std::wstring candidate = cue.substr(next);
        if (candidate.length() < 4) break;
        it = subtitleMap.find(candidate);
        if (it != subtitleMap.end()) return it->second.c_str();
        start = next;
    }

    return nullptr;
}
