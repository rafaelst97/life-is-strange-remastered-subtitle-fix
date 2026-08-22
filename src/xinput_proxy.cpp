#include <windows.h>
#include <cstdint>
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

static t_XInputGetState orig_XInputGetState = NULL;
static t_XInputSetState orig_XInputSetState = NULL;
static t_XInputGetCapabilities orig_XInputGetCapabilities = NULL;
static t_XInputEnable orig_XInputEnable = NULL;
static t_XInputGetDSoundAudioDeviceGuids orig_XInputGetDSoundAudioDeviceGuids = NULL;
static t_XInputGetBatteryInformation orig_XInputGetBatteryInformation = NULL;
static t_XInputGetKeystroke orig_XInputGetKeystroke = NULL;

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
            orig_XInputGetState = (t_XInputGetState)GetProcAddress(hRealXInput, "XInputGetState");
            orig_XInputSetState = (t_XInputSetState)GetProcAddress(hRealXInput, "XInputSetState");
            orig_XInputGetCapabilities = (t_XInputGetCapabilities)GetProcAddress(hRealXInput, "XInputGetCapabilities");
            orig_XInputEnable = (t_XInputEnable)GetProcAddress(hRealXInput, "XInputEnable");
            orig_XInputGetDSoundAudioDeviceGuids = (t_XInputGetDSoundAudioDeviceGuids)GetProcAddress(hRealXInput, "XInputGetDSoundAudioDeviceGuids");
            orig_XInputGetBatteryInformation = (t_XInputGetBatteryInformation)GetProcAddress(hRealXInput, "XInputGetBatteryInformation");
            orig_XInputGetKeystroke = (t_XInputGetKeystroke)GetProcAddress(hRealXInput, "XInputGetKeystroke");
        }
    }
}

extern "C" {
    DWORD WINAPI XInputGetState(DWORD dwUserIndex, void* pState) {
        if (!orig_XInputGetState) LoadRealXInput();
        return orig_XInputGetState ? orig_XInputGetState(dwUserIndex, pState) : 1167; // ERROR_DEVICE_NOT_CONNECTED
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
}

// --- UE4 AltDataSet Structure (0x50 bytes) ---
#pragma pack(push, 1)
struct AltDataSet {
    uint8_t dummy[0x18];       // 0x00..0x17
    uint8_t State;             // 0x18 (2 = ELS_Ready)
    uint8_t pad19[7];          // 0x19..0x1F
    const wchar_t* Data;       // 0x20 (pointer to raw wide buffer: key\0val\0...)
    int32_t DataLength;        // 0x28 (character count of Data buffer)
    uint8_t dummyRest[0x50 - 0x2C];
};
#pragma pack(pop)

static AltDataSet g_MasterDataset;

typedef void* (__fastcall *t_FindAltDataSetByLayerName)(void* thisPtr, int unk, void* LayerName);
static t_FindAltDataSetByLayerName orig_FindAltDataSet = NULL;

void* __fastcall hook_FindAltDataSetByLayerName(void* thisPtr, int unk, void* LayerName) {
    void* result = NULL;
    if (orig_FindAltDataSet) {
        result = orig_FindAltDataSet(thisPtr, unk, LayerName);
    }
    if (result != NULL) {
        AltDataSet* ds = (AltDataSet*)result;
        ds->State = 2; // ELS_Ready
        ds->Data = (const wchar_t*)g_MasterSubtitleData;
        ds->DataLength = (int32_t)g_MasterSubtitleCharCount;
        return result;
    }
    // Return static master dataset containing all 10,475 subtitles
    memset(&g_MasterDataset, 0, sizeof(g_MasterDataset));
    g_MasterDataset.State = 2; // ELS_Ready
    g_MasterDataset.Data = (const wchar_t*)g_MasterSubtitleData;
    g_MasterDataset.DataLength = (int32_t)g_MasterSubtitleCharCount;
    return &g_MasterDataset;
}

DWORD WINAPI SubtitleModThread(LPVOID lpParam) {
    HMODULE hMain = GetModuleHandleA(NULL);
    if (!hMain) return 0;

    uintptr_t baseAddr = (uintptr_t)hMain;

    // 1. In-memory patch at VA 0x14071023d (RVA 0x71023d):
    // Force always proceeding to AltDataSet lookup (bypass rigid cue layer validator early exit)
    uintptr_t patch1_va = baseAddr + 0x71023d;
    uintptr_t target_lookup_va = baseAddr + 0x7103b8;
    int32_t disp1 = (int32_t)(target_lookup_va - (patch1_va + 5));

    DWORD oldProt;
    if (VirtualProtect((LPVOID)patch1_va, 6, PAGE_EXECUTE_READWRITE, &oldProt)) {
        unsigned char* p = (unsigned char*)patch1_va;
        p[0] = 0xE9; // jmp rel32
        *(int32_t*)(p + 1) = disp1;
        p[5] = 0x90; // nop
        VirtualProtect((LPVOID)patch1_va, 6, oldProt, &oldProt);
    }

    // 2. Initialize MinHook and hook FindAltDataSetByLayerName at RVA 0x7188a0
    if (MH_Initialize() == MH_OK) {
        uintptr_t targetFn = baseAddr + 0x7188a0;
        MH_CreateHook((LPVOID)targetFn, (LPVOID)&hook_FindAltDataSetByLayerName, (LPVOID*)&orig_FindAltDataSet);
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
