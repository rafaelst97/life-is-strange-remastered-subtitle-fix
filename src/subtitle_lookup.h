// Cue-name normalization shared by the proxy DLL and the standalone test
// harness (tools/test_lookup.cpp), so the code under test is the code shipped.
//
// Life is Strange Remastered stores every subtitle line in
//   LIS/Content/Packages/Localization/<culture>/[Episode0N__]CU_<Layer>.ini
// under a [Cues] section keyed by the plain cue name, e.g.
//   Cue_E5_3B_ArtGallery_PhotoLook_Admirer1_050="..."
//
// When a cue actor is spawned at runtime instead of being loaded with its
// cooked sub-level - which is what happens as a sub-level streams in on a
// scene or episode change - UE4 gives it a unique object name of the form
// <CueName>_C_<Number> (MakeUniqueObjectName, counting down from MAX_int32).
// That decorated name is what reaches the localization lookup, it matches no
// key, and the manager hands back "?<key>?" which the subtitle widget draws.
//
// Stripping the "_C_<digits>" suffix turns the decorated name back into the
// asset name the .ini is keyed by. Verified against the shipped data: all 707
// decorated names captured on screen resolve, and no real key is altered
// (the only shipped keys containing "_C_" are of the form
// "E4_Page03_C_DontKillChloe", whose tail is not digits).
#pragma once

#include <string>

static inline bool HasObjectSuffix(const std::wstring& s) {
    size_t pos = s.rfind(L"_C_");
    if (pos == std::wstring::npos || pos + 3 >= s.length()) return false;
    for (size_t i = pos + 3; i < s.length(); ++i) {
        if (s[i] < L'0' || s[i] > L'9') return false;
    }
    return true;
}

// Returns the cue name without the UE4 "_C_<number>" instance suffix, or the
// input unchanged when there is no such suffix.
static inline std::wstring StripObjectSuffix(const std::wstring& s) {
    if (!HasObjectSuffix(s)) return s;
    return s.substr(0, s.rfind(L"_C_"));
}
