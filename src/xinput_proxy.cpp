#include <windows.h>
#include <cstdint>
#include <cstdarg>
#include <string>
#include <unordered_map>
#include "minhook/include/MinHook.h"
#include "subtitle_lookup.h"
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

// Subtitle lookup (StripObjectSuffix / FindTranslation) lives in
// subtitle_lookup.h so the exact same code is exercised by the standalone
// test harness in tools/test_lookup.cpp.


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
static t_FNameToString orig_FNameToString = NULL;

// The remastered subtitle pipeline converts the runtime cue FName to a string
// with FName::ToString and, when the cue is missing from the loaded dataset,
// displays that string verbatim (the "filename instead of subtitle" bug). We
// hook FName::ToString at the exact call site used by the subtitle display
// (the fallback-text conversion in the caller of GetSubtitleText) and, when
// the name is a runtime subtitle cue ("..._C_<digits>") that exists in the
// embedded master database, return the translated text so the display shows
// the real subtitle instead of the raw cue key.
static uintptr_t g_ModuleBase = 0;
static uintptr_t g_DisplayToStringRet = 0;

void* __fastcall hook_FNameToString(const uint64_t* pName, UE4String* outStr) {
    void* result = NULL;
    if (orig_FNameToString) {
        result = orig_FNameToString(pName, outStr);
    }
    if (!outStr || !outStr->Data || outStr->ArrayNum <= 1 || g_SubtitleMap.empty()) {
        return result;
    }

    // Only rewrite the string at the subtitle display call site.
    if (g_DisplayToStringRet != 0 && (uintptr_t)_ReturnAddress() != g_DisplayToStringRet) {
        return result;
    }

    std::wstring name(outStr->Data, (size_t)(outStr->ArrayNum - 1));

    // Only runtime subtitle cue names carry the "_C_<digits>" instance suffix.
    size_t cpos = name.rfind(L"_C_");
    if (cpos == std::wstring::npos || cpos + 3 >= name.length()) {
        return result;
    }
    bool allDigits = true;
    for (size_t i = cpos + 3; i < name.length(); ++i) {
        if (name[i] < L'0' || name[i] > L'9') { allDigits = false; break; }
    }
    if (!allDigits) {
        return result;
    }

    const wchar_t* text = FindTranslation(g_SubtitleMap, name);
    if (!text) {
        return result;
    }

    SetUE4String(outStr, text);

    static LONG s_txtLogCount = 0;
    if (InterlockedIncrement(&s_txtLogCount) <= 60) {
        DebugWrite(L"[TXT] '%s' -> '%.80s'\n", name.c_str(), text);
    }
    return result;
}

// FName constructor from a null-terminated TCHAR* string:
//   void FName::FName(const TCHAR* Name, EFindName FindType)   (this = out FName)
typedef void (__fastcall *t_FNameCtor)(uint64_t* outFName, const wchar_t* name, int32_t findType);
static t_FNameCtor fnFNameCtor = NULL;

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

    static LONG s_findLogCount = 0;
    if (InterlockedIncrement(&s_findLogCount) <= 300) {
        wchar_t layerBuf[256] = L"?";
        if (fnFNameToString) {
            UE4String ts = { nullptr, 0, 0 };
            fnFNameToString(&layerName, &ts);
            if (ts.Data && ts.ArrayNum > 1) {
                size_t n = (size_t)(ts.ArrayNum - 1);
                if (n > 255) n = 255;
                memcpy(layerBuf, ts.Data, n * sizeof(wchar_t));
                layerBuf[n] = L'\0';
            }
            if (ts.Data && fnFMemoryFree) fnFMemoryFree(ts.Data);
        }
        DebugWrite(L"[FIND] layer='%s' flag=%u result=%p", layerBuf, flag, result);
        if (result) {
            int8_t dtype = *(int8_t*)((char*)result + 0x18);
            DebugWrite(L" type=%d\n", dtype);
        } else {
            DebugWrite(L" type=-1\n");
        }
    }

    if (result) return result;

    // Fallback: the requested level/sub-level dataset is not loaded. Hand back
    // the first loaded dataset instead of NULL. Because every .cue file ships
    // the consolidated master database, the subsequent cue lookup in
    // GetSubtitleText still resolves the correct text.
    if (thisPtr) {
        uintptr_t offsets[2] = { (uintptr_t)(flag ? 0x78 : 0x68), (uintptr_t)(flag ? 0x68 : 0x78) };
        for (int i = 0; i < 2; ++i) {
            uintptr_t* arr = (uintptr_t*)((char*)thisPtr + offsets[i]);
            if (arr && *(int32_t*)((char*)arr + 8) > 0) {
                void* fb = (void*)arr[0];
                DebugWrite(L"[FIND] FALLBACK -> %p (offset=%llx)\n", fb, (unsigned long long)offsets[i]);
                return fb;
            }
        }
    }
    return NULL;
}

// GetSubtitleText(this, cueFName, outPhrases)
int64_t __fastcall hook_GetSubtitleText(void* thisPtr, uint64_t inCueName, UE4String* outSubtitleText) {
    if (inCueName != 0 && fnFNameToString) {
        UE4String tempStr = { nullptr, 0, 0 };
        fnFNameToString(&inCueName, &tempStr);
        if (tempStr.Data && tempStr.ArrayNum > 1) {
            static LONG s_logCount = 0;
            if (InterlockedIncrement(&s_logCount) <= 300) {
                DebugWrite(L"[GTXT] cue='%s'\n", tempStr.Data);
            }
        }
        if (tempStr.Data && fnFMemoryFree) {
            fnFMemoryFree(tempStr.Data);
        }
    }
    if (orig_GetSubtitleText) {
        return orig_GetSubtitleText(thisPtr, inCueName, outSubtitleText);
    }
    return 1;
}

// Subtitle dataset hash-table lookup (called from GetSubtitleText).
//   int Lookup(void* hashTable, int32* outIndex, FName cueFName)
// The cue FName arrives with the Blueprint instance suffix "_C_<Number>" (e.g.
// "..._020_C_2147459946") which never matches the dataset keys ("..._020",
// Number 0), so the lookup fails and the raw cue key is shown. We normalize it
// (strip "_C_<digits>", Number -> 0) BEFORE the lookup. The "_C_<digits>"
// pattern only occurs on runtime subtitle cue names, so other callers of this
// generic hash-table lookup are unaffected.
typedef int (__fastcall *t_SearchSubtitle)(void* hashTable, int32_t* outIndex, uint64_t cueFName);
static t_SearchSubtitle orig_SearchSubtitle = NULL;

int __fastcall hook_SearchSubtitle(void* hashTable, int32_t* outIndex, uint64_t cueFName) {
    uint64_t normFName = cueFName;

    // Skip obviously-invalid FName values before touching the name table.
    uint32_t lo = (uint32_t)(cueFName & 0xFFFFFFFF);
    uint32_t hi = (uint32_t)(cueFName >> 32);
    if (cueFName != 0 && lo != 0xFFFFFFFF && hi != 0xFFFFFFFF &&
        fnFNameToString && fnFNameCtor && fnFMemoryRealloc) {
        UE4String tempStr = { nullptr, 0, 0 };
        fnFNameToString(&cueFName, &tempStr);
        if (tempStr.Data && tempStr.ArrayNum > 1) {
            std::wstring cue(tempStr.Data);
            std::wstring norm = StripObjectSuffix(cue);
            if (norm != cue) {
                size_t byteCount = (norm.length() + 1) * sizeof(wchar_t);
                wchar_t* buf = (wchar_t*)fnFMemoryRealloc(NULL, byteCount, 0);
                if (buf) {
                    memcpy(buf, norm.c_str(), byteCount);
                    fnFNameCtor(&normFName, buf, 1);  // FNAME_Add
                    fnFMemoryFree(buf);

                    static LONG s_normLogCount = 0;
                    if (InterlockedIncrement(&s_normLogCount) <= 200) {
                        DebugWrite(L"[SRCH] NORM '%s' -> '%s'\n", cue.c_str(), norm.c_str());
                    }
                }
            }
        }
        if (tempStr.Data && fnFMemoryFree) {
            fnFMemoryFree(tempStr.Data);
        }
    }

    int result = orig_SearchSubtitle(hashTable, outIndex, normFName);

    // Only report "not found" for FNames that look like runtime cue names.
    if (result < 0 && (uint32_t)(normFName & 0xFFFFFFFF) != 0xFFFFFFFF) {
        static LONG s_missLogCount = 0;
        if (InterlockedIncrement(&s_missLogCount) <= 200) {
            wchar_t nameBuf[256] = L"?";
            if (fnFNameToString && normFName != 0) {
                UE4String ts = { nullptr, 0, 0 };
                fnFNameToString(&normFName, &ts);
                if (ts.Data && ts.ArrayNum > 1) {
                    size_t n = (size_t)(ts.ArrayNum - 1);
                    if (n > 255) n = 255;
                    memcpy(nameBuf, ts.Data, n * sizeof(wchar_t));
                    nameBuf[n] = L'\0';
                }
                if (ts.Data && fnFMemoryFree) fnFMemoryFree(ts.Data);
            }
            DebugWrite(L"[SRCH] MISS fname='%s'\n", nameBuf);
        }
    }

    return result;
}

DWORD WINAPI SubtitleModThread(LPVOID lpParam) {
    HMODULE hMain = GetModuleHandleA(NULL);
    if (!hMain) return 0;
    uintptr_t base = (uintptr_t)hMain;
    g_ModuleBase = base;
    // Return address of the display's FName::ToString call (0x14064e02a -> 0x14064e02f)
    g_DisplayToStringRet = base + 0x64e02f;

    InitSubtitleMap();

    // UE4 Functions:
    // FName::ToString at RVA 0xb30120
    // FName::FName(const TCHAR*, EFindName) at RVA 0xb25510
    // FMemory::Realloc at RVA 0xa75240
    // FMemory::Free at RVA 0xa666d0
    fnFNameToString = (t_FNameToString)(base + 0xb30120);
    fnFNameCtor = (t_FNameCtor)(base + 0xb25510);
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

        uintptr_t targetFn3 = base + 0x712d10;
        if (MH_CreateHook((LPVOID)targetFn3, (LPVOID)&hook_SearchSubtitle, (LPVOID*)&orig_SearchSubtitle) == MH_OK) {
            MH_EnableHook((LPVOID)targetFn3);
            DebugWrite(L"[DEBUG] SearchSubtitle hook created and enabled at %p\n", (void*)targetFn3);
        } else {
            DebugWrite(L"[DEBUG] SearchSubtitle hook creation failed at %p\n", (void*)targetFn3);
        }

        // FName::ToString hook: substitute the translated text for runtime subtitle
        // cue names so the display never falls back to the raw cue key.
        uintptr_t targetFn4 = base + 0xb30120;
        if (MH_CreateHook((LPVOID)targetFn4, (LPVOID)&hook_FNameToString, (LPVOID*)&orig_FNameToString) == MH_OK) {
            MH_EnableHook((LPVOID)targetFn4);
            DebugWrite(L"[DEBUG] FNameToString hook created and enabled at %p\n", (void*)targetFn4);
        } else {
            DebugWrite(L"[DEBUG] FNameToString hook creation failed at %p\n", (void*)targetFn4);
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


