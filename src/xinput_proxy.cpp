#include <windows.h>
#include <cstdint>
#include <cstdarg>
#include <string>
#include <unordered_map>
#include "minhook/include/MinHook.h"
#include "subtitles_data.h"

#pragma comment(lib, "user32.lib")

// --- Real XInput function pointers ---
typedef DWORD (WINAPI *t_XInputGetState)(DWORD dwUserIndex, void* pState);
typedef DWORD (WINAPI *t_XInputSetState)(DWORD dwUserIndex, void* pVibration);
typedef DWORD (WINAPI *t_XInputGetCapabilities)(DWORD dwUserIndex, DWORD dwFlags, void* pCapabilities);
typedef void (WINAPI *t_XInputEnable)(BOOL enable);
typedef DWORD (WINAPI *t_XInputGetDSoundAudioDeviceGuids)(DWORD dwUserIndex, GUID* pDSoundRenderGuid, GUID* pDSoundCaptureGuid);
typedef DWORD (WINAPI *t_XInputGetBatteryInformation)(DWORD dwUserIndex, BYTE devType, void* pBatteryInformation);
typedef DWORD (WINAPI *t_XInputGetKeystroke)(DWORD dwUserIndex, DWORD dwReserved, void* pKeystroke);
typedef DWORD (WINAPI *t_XInputGetStateEx)(DWORD dwUserIndex, void* pState);
typedef DWORD (WINAPI *t_XInputWaitForGuideButton)(DWORD dwUserIndex, DWORD dwFlag, void* pUnk);
typedef DWORD (WINAPI *t_XInputCancelGuideButtonWait)(DWORD dwUserIndex);
typedef DWORD (WINAPI *t_XInputPowerOffController)(DWORD dwUserIndex);

static t_XInputGetState orig_XInputGetState = NULL;
static t_XInputSetState orig_XInputSetState = NULL;
static t_XInputGetCapabilities orig_XInputGetCapabilities = NULL;
static t_XInputEnable orig_XInputEnable = NULL;
static t_XInputGetDSoundAudioDeviceGuids orig_XInputGetDSoundAudioDeviceGuids = NULL;
static t_XInputGetBatteryInformation orig_XInputGetBatteryInformation = NULL;
static t_XInputGetKeystroke orig_XInputGetKeystroke = NULL;
static t_XInputGetStateEx orig_XInputGetStateEx = NULL;
static t_XInputWaitForGuideButton orig_XInputWaitForGuideButton = NULL;
static t_XInputCancelGuideButtonWait orig_XInputCancelGuideButtonWait = NULL;
static t_XInputPowerOffController orig_XInputPowerOffController = NULL;

static HMODULE hRealXInput = NULL;

void LoadRealXInput() {
    if (!hRealXInput) {
        char sysPath[MAX_PATH];
        GetSystemDirectoryA(sysPath, MAX_PATH);
        strcat_s(sysPath, "\\xinput1_3.dll");
        hRealXInput = LoadLibraryA(sysPath);
        if (!hRealXInput) {
            GetSystemDirectoryA(sysPath, MAX_PATH);
            strcat_s(sysPath, "\\xinput1_4.dll");
            hRealXInput = LoadLibraryA(sysPath);
        }
        if (hRealXInput) {
            orig_XInputGetState = (t_XInputGetState)GetProcAddress(hRealXInput, (LPCSTR)2);
            orig_XInputSetState = (t_XInputSetState)GetProcAddress(hRealXInput, (LPCSTR)3);
            orig_XInputGetCapabilities = (t_XInputGetCapabilities)GetProcAddress(hRealXInput, (LPCSTR)4);
            orig_XInputEnable = (t_XInputEnable)GetProcAddress(hRealXInput, (LPCSTR)5);
            orig_XInputGetDSoundAudioDeviceGuids = (t_XInputGetDSoundAudioDeviceGuids)GetProcAddress(hRealXInput, (LPCSTR)6);
            orig_XInputGetBatteryInformation = (t_XInputGetBatteryInformation)GetProcAddress(hRealXInput, (LPCSTR)7);
            orig_XInputGetKeystroke = (t_XInputGetKeystroke)GetProcAddress(hRealXInput, (LPCSTR)8);
            orig_XInputGetStateEx = (t_XInputGetStateEx)GetProcAddress(hRealXInput, (LPCSTR)100);
            orig_XInputWaitForGuideButton = (t_XInputWaitForGuideButton)GetProcAddress(hRealXInput, (LPCSTR)101);
            orig_XInputCancelGuideButtonWait = (t_XInputCancelGuideButtonWait)GetProcAddress(hRealXInput, (LPCSTR)102);
            orig_XInputPowerOffController = (t_XInputPowerOffController)GetProcAddress(hRealXInput, (LPCSTR)103);
        }
    }
}

extern "C" {
    DWORD WINAPI XInputGetState(DWORD dwUserIndex, void* pState) {
        if (!orig_XInputGetState) LoadRealXInput();
        return orig_XInputGetState ? orig_XInputGetState(dwUserIndex, pState) : 1167;
    }
    DWORD WINAPI XInputSetState(DWORD dwUserIndex, void* pVibration) {
        if (!orig_XInputSetState) LoadRealXInput();
        return orig_XInputSetState ? orig_XInputSetState(dwUserIndex, pVibration) : 1167;
    }
    DWORD WINAPI XInputGetCapabilities(DWORD dwUserIndex, DWORD dwFlags, void* pCapabilities) {
        if (!orig_XInputGetCapabilities) LoadRealXInput();
        return orig_XInputGetCapabilities ? orig_XInputGetCapabilities(dwUserIndex, dwFlags, pCapabilities) : 1167;
    }
    void WINAPI XInputEnable(BOOL enable) {
        if (!orig_XInputEnable) LoadRealXInput();
        if (orig_XInputEnable) orig_XInputEnable(enable);
    }
    DWORD WINAPI XInputGetDSoundAudioDeviceGuids(DWORD dwUserIndex, GUID* pDSoundRenderGuid, GUID* pDSoundCaptureGuid) {
        if (!orig_XInputGetDSoundAudioDeviceGuids) LoadRealXInput();
        return orig_XInputGetDSoundAudioDeviceGuids ? orig_XInputGetDSoundAudioDeviceGuids(dwUserIndex, pDSoundRenderGuid, pDSoundCaptureGuid) : 1167;
    }
    DWORD WINAPI XInputGetBatteryInformation(DWORD dwUserIndex, BYTE devType, void* pBatteryInformation) {
        if (!orig_XInputGetBatteryInformation) LoadRealXInput();
        return orig_XInputGetBatteryInformation ? orig_XInputGetBatteryInformation(dwUserIndex, devType, pBatteryInformation) : 1167;
    }
    DWORD WINAPI XInputGetKeystroke(DWORD dwUserIndex, DWORD dwReserved, void* pKeystroke) {
        if (!orig_XInputGetKeystroke) LoadRealXInput();
        return orig_XInputGetKeystroke ? orig_XInputGetKeystroke(dwUserIndex, dwReserved, pKeystroke) : 1167;
    }
    DWORD WINAPI XInputGetStateEx(DWORD dwUserIndex, void* pState) {
        if (!orig_XInputGetStateEx) LoadRealXInput();
        return orig_XInputGetStateEx ? orig_XInputGetStateEx(dwUserIndex, pState) : 1167;
    }
    DWORD WINAPI XInputWaitForGuideButton(DWORD dwUserIndex, DWORD dwFlag, void* pUnk) {
        if (!orig_XInputWaitForGuideButton) LoadRealXInput();
        return orig_XInputWaitForGuideButton ? orig_XInputWaitForGuideButton(dwUserIndex, dwFlag, pUnk) : 1167;
    }
    DWORD WINAPI XInputCancelGuideButtonWait(DWORD dwUserIndex) {
        if (!orig_XInputCancelGuideButtonWait) LoadRealXInput();
        return orig_XInputCancelGuideButtonWait ? orig_XInputCancelGuideButtonWait(dwUserIndex) : 1167;
    }
    DWORD WINAPI XInputPowerOffController(DWORD dwUserIndex) {
        if (!orig_XInputPowerOffController) LoadRealXInput();
        return orig_XInputPowerOffController ? orig_XInputPowerOffController(dwUserIndex) : 1167;
    }
}

// --- UE4 String Structure ---
struct UE4String {
    wchar_t* Data;
    int32_t ArrayNum;
    int32_t ArrayMax;
};

// --- UE4 Allocator Functions ---
typedef void* (*t_FMemoryRealloc)(void* Original, size_t Count, uint32_t Alignment);
typedef void (*t_FMemoryFree)(void* Original);

static t_FMemoryRealloc fnFMemoryRealloc = NULL;
static t_FMemoryFree fnFMemoryFree = NULL;

static std::unordered_map<std::wstring, std::wstring> g_SubtitleMap;

// Diagnostic log lives next to the proxy DLL itself so the mod works from any
// game installation path (no hard-coded machine-specific location).
static wchar_t g_LogPath[MAX_PATH] = { 0 };

static void InitLogPath(HMODULE hModule) {
    if (g_LogPath[0] != L'\0') return;
    wchar_t modulePath[MAX_PATH] = { 0 };
    if (GetModuleFileNameW(hModule, modulePath, MAX_PATH) == 0) {
        wcscpy_s(g_LogPath, L"LiS_SubtitleFix.log");
        return;
    }
    wchar_t* dot = wcsrchr(modulePath, L'.');
    if (dot) {
        wcscpy_s(dot, MAX_PATH - (size_t)(dot - modulePath), L".log");
    } else {
        wcscat_s(modulePath, L".log");
    }
    wcscpy_s(g_LogPath, modulePath);
}

static void DebugWrite(const wchar_t* fmt, ...) {
    if (g_LogPath[0] == L'\0') return;
    FILE* fdebug = _wfopen(g_LogPath, L"a");
    if (!fdebug) return;
    va_list args;
    va_start(args, fmt);
    vfwprintf(fdebug, fmt, args);
    va_end(args);
    fclose(fdebug);
}

void InitSubtitleMap() {
    if (!g_SubtitleMap.empty()) return;
    const wchar_t* p = (const wchar_t*)g_MasterSubtitleData;
    const wchar_t* end = (const wchar_t*)(g_MasterSubtitleData + sizeof(g_MasterSubtitleData));
    while (p < end && *p != L'\0') {
        std::wstring key = p;
        p += key.length() + 1;
        if (p >= end || *p == L'\0') break;
        std::wstring val = p;
        p += val.length() + 1;
        g_SubtitleMap[key] = val;
    }

    // Log map stats and first 5 entries
    DebugWrite(L"[INIT] SubtitleMap loaded: %zu entries\n", g_SubtitleMap.size());
    int count = 0;
    for (auto& kv : g_SubtitleMap) {
        if (count++ >= 5) break;
        DebugWrite(L"[INIT]   key='%s' val='%.60s...'\n", kv.first.c_str(), kv.second.c_str());
    }
}

// The runtime cue FName normally carries a UE4 object instance suffix such as
// "Cue_E5_7Z_..._010_C_2147222737". Strip the trailing "_C_<digits>" so the key
// matches the master subtitle database.
static std::wstring StripObjectSuffix(const std::wstring& s) {
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

const wchar_t* FindTranslation(const std::wstring& rawCue) {
    if (g_SubtitleMap.empty()) return nullptr;

    std::wstring cue = StripObjectSuffix(rawCue);

    // 1) Direct lookup against the canonical key.
    auto it = g_SubtitleMap.find(cue);
    if (it != g_SubtitleMap.end()) return it->second.c_str();

    // 2) Strip leading "Play_" / "Cue_" / "Act_" prefixes and retry.
    static const wchar_t* kPrefixes[] = { L"Play_", L"Cue_", L"Act_" };
    for (const wchar_t* p : kPrefixes) {
        size_t plen = wcslen(p);
        if (cue.compare(0, plen, p) == 0) {
            it = g_SubtitleMap.find(cue.substr(plen));
            if (it != g_SubtitleMap.end()) return it->second.c_str();
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
        it = g_SubtitleMap.find(candidate);
        if (it != g_SubtitleMap.end()) return it->second.c_str();
        start = next;
    }

    return nullptr;
}

void SetUE4String(UE4String* str, const wchar_t* src) {
    if (!str || !src || !fnFMemoryRealloc) return;
    int32_t charCount = (int32_t)wcslen(src) + 1;
    size_t byteCount = (size_t)charCount * sizeof(wchar_t);
    wchar_t* newBuf = (wchar_t*)fnFMemoryRealloc(NULL, byteCount, 0);
    if (newBuf) {
        memcpy(newBuf, src, byteCount);
        if (str->Data && fnFMemoryFree) {
            fnFMemoryFree(str->Data);
        }
        str->Data = newBuf;
        str->ArrayNum = charCount;
        str->ArrayMax = charCount;
    }
}

// FName::ToString(const uint64_t* pName, UE4String* outStr)
typedef void* (__fastcall *t_FNameToString)(const uint64_t* pName, UE4String* outStr);
static t_FNameToString fnFNameToString = NULL;

// UDNEAltData::GetSubtitleText(thisPtr, inCueName, outSubtitleText)
typedef int64_t (__fastcall *t_GetSubtitleText)(void* thisPtr, uint64_t inCueName, UE4String* outSubtitleText);
static t_GetSubtitleText orig_GetSubtitleText = NULL;

// UDNEAltData::FindAltDataSetByLayerName(thisPtr, flag, layerName)
// Returns the FAltDataSet element (0x88 bytes) whose LayerName matches, or
// NULL when the requested level/sub-level dataset is not loaded in memory.
// The vanilla fallback in GetSubtitleText then renders the raw cue key on
// screen - this is the exact "filename instead of subtitle" bug. We hook it
// and, on failure, hand back the first loaded dataset: because every .cue
// file ships the consolidated master database, the subsequent cue lookup in
// GetSubtitleText always succeeds regardless of the selected language.
typedef void* (__fastcall *t_FindAltDataSetByLayerName)(void* thisPtr, uint8_t flag, uint64_t layerName);
static t_FindAltDataSetByLayerName orig_FindAltDataSetByLayerName = NULL;

void* __fastcall hook_FindAltDataSetByLayerName(void* thisPtr, uint8_t flag, uint64_t layerName) {
    void* result = NULL;
    if (orig_FindAltDataSetByLayerName) {
        result = orig_FindAltDataSetByLayerName(thisPtr, flag, layerName);
    }
    if (result) return result;

    // Fallback: return the first loaded dataset so the caller can still
    // resolve the cue against the consolidated subtitle data.
    if (thisPtr) {
        uintptr_t arrayOffset = flag ? 0x78 : 0x68;
        uintptr_t* arr = (uintptr_t*)((char*)thisPtr + arrayOffset);
        if (arr && *(int32_t*)((char*)arr + 8) > 0) {
            return (void*)arr[0];
        }
    }
    return NULL;
}

int64_t __fastcall hook_GetSubtitleText(void* thisPtr, uint64_t inCueName, UE4String* outSubtitleText) {
    if (inCueName != 0 && fnFNameToString) {
        UE4String tempStr = { nullptr, 0, 0 };
        fnFNameToString(&inCueName, &tempStr);
        if (tempStr.Data && tempStr.ArrayNum > 1) {
            std::wstring cue(tempStr.Data);

            const wchar_t* trans = FindTranslation(cue);
            if (trans) {
                SetUE4String(outSubtitleText, trans);
                if (tempStr.Data && fnFMemoryFree) {
                    fnFMemoryFree(tempStr.Data);
                }
                return 0;
            } else {
                // Only report the first few misses to avoid unbounded log growth.
                static LONG s_missLogCount = 0;
                if (InterlockedIncrement(&s_missLogCount) <= 100) {
                    DebugWrite(L"[HOOK] NO MATCH for cue='%s' mapSize=%zu\n", cue.c_str(), g_SubtitleMap.size());
                }
            }
        }
        if (tempStr.Data && fnFMemoryFree) {
            fnFMemoryFree(tempStr.Data);
        }
    } else {
        DebugWrite(L"[HOOK] called but inCueName=0 or fnFNameToString=NULL\n");
    }

    if (orig_GetSubtitleText) {
        return orig_GetSubtitleText(thisPtr, inCueName, outSubtitleText);
    }
    return 1;
}

DWORD WINAPI SubtitleModThread(LPVOID lpParam) {
    HMODULE hMain = GetModuleHandleA(NULL);
    if (!hMain) return 0;
    uintptr_t base = (uintptr_t)hMain;

    InitSubtitleMap();

    // UE4 Functions:
    // FName::ToString at RVA 0xb30120
    // FMemory::Realloc at RVA 0xa75240
    // FMemory::Free at RVA 0xa666d0
    fnFNameToString = (t_FNameToString)(base + 0xb30120);
    fnFMemoryRealloc = (t_FMemoryRealloc)(base + 0xa75240);
    fnFMemoryFree = (t_FMemoryFree)(base + 0xa666d0);


    // ---------------------------------------------------------------------------
    // Debug logging for MinHook initialization and hook creation
    // ---------------------------------------------------------------------------
    if (MH_Initialize() != MH_OK) {
        DebugWrite(L"[DEBUG] MinHook initialization failed\n");
    } else {
        DebugWrite(L"[DEBUG] MinHook initialized successfully\n");
        uintptr_t targetFn = base + 0x70fb40;
        if (MH_CreateHook((LPVOID)targetFn, (LPVOID)&hook_GetSubtitleText, (LPVOID*)&orig_GetSubtitleText) == MH_OK) {
            MH_EnableHook((LPVOID)targetFn);
            DebugWrite(L"[DEBUG] GetSubtitleText hook created and enabled at %p\n", (void*)targetFn);
        } else {
            DebugWrite(L"[DEBUG] GetSubtitleText hook creation failed at %p\n", (void*)targetFn);
        }

        uintptr_t targetFn2 = base + 0x7188a0;
        if (MH_CreateHook((LPVOID)targetFn2, (LPVOID)&hook_FindAltDataSetByLayerName, (LPVOID*)&orig_FindAltDataSetByLayerName) == MH_OK) {
            MH_EnableHook((LPVOID)targetFn2);
            DebugWrite(L"[DEBUG] FindAltDataSetByLayerName hook created and enabled at %p\n", (void*)targetFn2);
        } else {
            DebugWrite(L"[DEBUG] FindAltDataSetByLayerName hook creation failed at %p\n", (void*)targetFn2);
        }
    }
    return 0;
}



BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
    case DLL_PROCESS_ATTACH:
        DisableThreadLibraryCalls(hModule);
        InitLogPath(hModule);
        DebugWrite(L"[LiS_SubMod] DllMain ATTACH\n");
        LoadRealXInput();
        CreateThread(NULL, 0, SubtitleModThread, NULL, 0, NULL);
        break;
    case DLL_PROCESS_DETACH:
        MH_DisableHook(MH_ALL_HOOKS);
        MH_Uninitialize();
        if (hRealXInput) FreeLibrary(hRealXInput);
        break;
    }
    return TRUE;
}


