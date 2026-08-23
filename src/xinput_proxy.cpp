#include <windows.h>
#include <cstdint>
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
}

const wchar_t* FindTranslation(const std::wstring& cue) {
    if (g_SubtitleMap.empty()) return nullptr;
    
    // Direct lookup
    auto it = g_SubtitleMap.find(cue);
    if (it != g_SubtitleMap.end()) return it->second.c_str();

    // Strip Play_
    if (cue.rfind(L"Play_", 0) == 0) {
        std::wstring stripped = cue.substr(5);
        it = g_SubtitleMap.find(stripped);
        if (it != g_SubtitleMap.end()) return it->second.c_str();
    }
    
    // Strip Cue_ or Act_
    if (cue.rfind(L"Cue_", 0) == 0 || cue.rfind(L"Act_", 0) == 0) {
        std::wstring stripped = cue.substr(4);
        it = g_SubtitleMap.find(stripped);
        if (it != g_SubtitleMap.end()) return it->second.c_str();
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
                return 3; // Return success code
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

    // Hook UDNEAltData::GetSubtitleText at function entry RVA 0x70fb40
    if (MH_Initialize() == MH_OK) {
        uintptr_t targetFn = base + 0x70fb40;
        MH_CreateHook((LPVOID)targetFn, (LPVOID)&hook_GetSubtitleText, (LPVOID*)&orig_GetSubtitleText);
        MH_EnableHook((LPVOID)targetFn);
    }

    return 0;
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
    case DLL_PROCESS_ATTACH:
        DisableThreadLibraryCalls(hModule);
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
