// Life is Strange Remastered - subtitle fix.
//
// The game resolves every subtitle through
//   ULiSLocalizationManager::GetLocalizedText(const TCHAR* Key, FString& Out)
// (RVA 0x767d40 in LiS-Win64-Shipping.exe), which looks Key up in the tables
// loaded from LIS/Content/Packages/Localization/<culture>/*.ini and returns
// false with Out set to "?Key?" when the key is missing.
//
// A cue actor streamed in with a sub-level keeps its cooked name, but one
// spawned at runtime gets UE4's unique object name <CueName>_C_<Number>. That
// decorated name reaches the lookup verbatim, matches no key, and the widget
// draws the "?...?" placeholder - the raw cue name players see after a scene
// or episode change.
//
// This hook does nothing until the game's own lookup has already failed; then
// it strips the "_C_<digits>" suffix and asks the game again. The text still
// comes from the game's own tables, so the fix is correct in every language
// and carries no subtitle data of its own.

#include <windows.h>
#include <cstdint>
#include <cstdio>
#include <cstdarg>
#include <string>
#include "minhook/include/MinHook.h"
#include "subtitle_lookup.h"
#include "miniz.h"

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
    if (hRealXInput) return;
    char sysPath[MAX_PATH];
    GetSystemDirectoryA(sysPath, MAX_PATH);
    strcat_s(sysPath, "\\xinput1_3.dll");
    hRealXInput = LoadLibraryA(sysPath);
    if (!hRealXInput) {
        GetSystemDirectoryA(sysPath, MAX_PATH);
        strcat_s(sysPath, "\\xinput1_4.dll");
        hRealXInput = LoadLibraryA(sysPath);
    }
    if (!hRealXInput) return;
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

// ---------------------------------------------------------------------------
// Diagnostics. Written next to this DLL, UTF-8, capped so a long session can
// never grow the file without bound.
// ---------------------------------------------------------------------------
static char g_LogPath[MAX_PATH] = { 0 };
static LONG g_LogLines = 0;

static void InitLogPath(HMODULE hModule) {
    wchar_t modulePath[MAX_PATH] = { 0 };
    if (GetModuleFileNameW(hModule, modulePath, MAX_PATH) == 0) return;
    wchar_t* dot = wcsrchr(modulePath, L'.');
    if (dot) wcscpy_s(dot, MAX_PATH - (size_t)(dot - modulePath), L".log");
    WideCharToMultiByte(CP_UTF8, 0, modulePath, -1, g_LogPath, MAX_PATH, NULL, NULL);
}

static void LogLine(const char* fmt, ...) {
    if (g_LogPath[0] == '\0') return;
    if (InterlockedIncrement(&g_LogLines) > 3000) return;
    FILE* f = NULL;
    if (fopen_s(&f, g_LogPath, "a") != 0 || !f) return;
    va_list args;
    va_start(args, fmt);
    vfprintf(f, fmt, args);
    va_end(args);
    fputc('\n', f);
    fclose(f);
}

// UTF-8 rendering of a wide string, for the log only.
static std::string Utf8(const wchar_t* s) {
    if (!s) return std::string();
    int n = WideCharToMultiByte(CP_UTF8, 0, s, -1, NULL, 0, NULL, NULL);
    if (n <= 1) return std::string();
    std::string out((size_t)n - 1, '\0');
    WideCharToMultiByte(CP_UTF8, 0, s, -1, &out[0], n, NULL, NULL);
    return out;
}

typedef int (__fastcall *t_wcsicmp)(const wchar_t* s1, const wchar_t* s2);
static t_wcsicmp orig_wcsicmp = NULL;

static const uintptr_t kWcsicmpRVA = 0xa3d330;
static const unsigned char kWcsicmpPrologue[] = {
    0x4C, 0x8B, 0xD1,                          // mov r10, rcx
    0x4C, 0x8D, 0x1D, 0xA6, 0xA1, 0x0E, 0x02,  // lea r11, [rip + 0x20ea1a6]
    0x4C, 0x2B, 0xD2                           // sub r10, rdx
};

int __fastcall hook_wcsicmp(const wchar_t* s1, const wchar_t* s2) {
    if (!s1 || !s2) return orig_wcsicmp(s1, s2);
    
    // Quick filter: Subtitle cue strings usually start with 'Cue_' or 'Act_'
    if ((s1[0] == L'C' && s1[1] == L'u' && s1[2] == L'e' && s1[3] == L'_') || 
        (s1[0] == L'A' && s1[1] == L'c' && s1[2] == L't' && s1[3] == L'_') ||
        (s2[0] == L'C' && s2[1] == L'u' && s2[2] == L'e' && s2[3] == L'_') || 
        (s2[0] == L'A' && s2[1] == L'c' && s2[2] == L't' && s2[3] == L'_')) {
        
        std::wstring str1 = StripObjectSuffix(s1);
        std::wstring str2 = StripObjectSuffix(s2);
        
        int result = orig_wcsicmp(str1.c_str(), str2.c_str());
        LogLine("[CMP] res=%d '%s' vs '%s' (orig: '%s', '%s')", 
            result, Utf8(str1.c_str()).c_str(), Utf8(str2.c_str()).c_str(), 
            Utf8(s1).c_str(), Utf8(s2).c_str());
        return result;
    }
    
    return orig_wcsicmp(s1, s2);
}

// ---------------------------------------------------------------------------
// ULiSLocalizationManager::GetLocalizedText(const TCHAR* Key, FString& Out)
//
// RVA and prologue are pinned to the shipping build this was reverse
// engineered against (LiS-Win64-Shipping.exe, 62,406,144 bytes,
// sha256 2697f850bffc316b7cbd692b37d2ea32411924fd9cbf104396b005ce32b19e79).
// The prologue is re-checked at runtime; on any mismatch the hook is skipped
// rather than installed at a guessed address.
// ---------------------------------------------------------------------------
static const uintptr_t kGetLocalizedTextRVA = 0x767d40;
static const unsigned char kGetLocalizedTextPrologue[] = {
    0x48, 0x89, 0x54, 0x24, 0x10,              // mov [rsp+0x10], rdx
    0x48, 0x89, 0x4C, 0x24, 0x08,              // mov [rsp+0x08], rcx
    0x56,                                      // push rsi
    0x57,                                      // push rdi
    0x48, 0x81, 0xEC, 0xD8, 0x09, 0x00, 0x00   // sub  rsp, 0x9d8
};

// UE4 FString header, for reading (never writing) text the game produced.
struct UE4String {
    wchar_t* Data;
    int32_t ArrayNum;
    int32_t ArrayMax;
};

static std::string PeekString(const void* fstring, size_t maxChars = 90) {
    const UE4String* s = (const UE4String*)fstring;
    if (!s || !s->Data || s->ArrayNum <= 1) return std::string("<empty>");
    size_t n = (size_t)(s->ArrayNum - 1);
    if (n > maxChars) n = maxChars;
    return Utf8(std::wstring(s->Data, n).c_str());
}

typedef bool (__fastcall *t_GetLocalizedText)(const wchar_t* key, void* outText);
static t_GetLocalizedText orig_GetLocalizedText = NULL;

#include <unordered_map>
#include <vector>

std::unordered_map<std::wstring, std::unordered_map<std::wstring, std::wstring>> g_AltDataDicts;
bool g_HasFanTranslation = false;
std::wstring g_FanTranslationLang = L"";

std::wstring Utf8ToWString(const std::string& str) {
    if (str.empty()) return std::wstring();
    int size_needed = MultiByteToWideChar(CP_UTF8, 0, &str[0], (int)str.size(), NULL, 0);
    std::wstring wstrTo(size_needed, 0);
    MultiByteToWideChar(CP_UTF8, 0, &str[0], (int)str.size(), &wstrTo[0], size_needed);
    return wstrTo;
}

void ParseIniContent(const std::string& lang, const std::string& content) {
    std::wstring wlang = Utf8ToWString(lang);
    if (wlang == L"en") wlang = L"INT";
    else if (wlang == L"pt-BR" || wlang == L"pt" || wlang == L"POR") wlang = L"PTB";
    else if (wlang == L"fr") wlang = L"FRA";
    else if (wlang == L"it") wlang = L"ITA";
    else if (wlang == L"de") wlang = L"DEU";
    else if (wlang == L"es-M" || wlang == L"es-4") wlang = L"ESM";
    else if (wlang == L"es") wlang = L"ESN";
    else if (wlang == L"ja") wlang = L"JPN";
    else if (wlang == L"hu") wlang = L"HUN";
    else if (wlang == L"ru") wlang = L"RUS";
    else if (wlang == L"zh-Hans") wlang = L"ZHS";
    else if (wlang == L"zh-Hant") wlang = L"ZHT";

    size_t pos = 0;
    while (pos < content.size()) {
        size_t eol = content.find('\n', pos);
        if (eol == std::string::npos) eol = content.size();
        
        std::string line = content.substr(pos, eol - pos);
        pos = eol + 1;
        
        if (!line.empty() && line.back() == '\r') line.pop_back();
        
        size_t eq = line.find('=');
        if (eq != std::string::npos) {
            std::string key = line.substr(0, eq);
            std::string val = line.substr(eq + 1);
            if (val.length() >= 2 && val.front() == '"' && val.back() == '"') {
                val = val.substr(1, val.length() - 2);
            }
            
            size_t esc = 0;
            while ((esc = val.find("\\\"")) != std::string::npos) {
                val.replace(esc, 2, "\"");
                esc += 1;
            }

            g_AltDataDicts[wlang][Utf8ToWString(key)] = Utf8ToWString(val);
        }
    }
    g_HasFanTranslation = true;
    g_FanTranslationLang = wlang;
    LogLine("[FAN] Parsed fan translation for lang: %ls, total entries: %zu", wlang.c_str(), g_AltDataDicts[wlang].size());
}

#pragma pack(push, 1)
struct FPakInfo {
    uint32_t Magic;
    uint32_t Version;
    uint64_t IndexOffset;
    uint64_t IndexSize;
    uint8_t IndexHash[20];
};
#pragma pack(pop)

void LoadFanTranslations() {
    WIN32_FIND_DATAW ffd;
    HANDLE hFind = FindFirstFileW(L"C:\\Games\\Life is Strange Remastered\\LIS\\Content\\Paks\\*.pak", &ffd);
    if (hFind == INVALID_HANDLE_VALUE) return;
    
    do {
        std::wstring wname = ffd.cFileName;
        if (wname.find(L"pakchunk") == 0 && wname.find(L"-WindowsNoEditor.pak") != std::wstring::npos) {
            size_t start = 8;
            size_t end = wname.find(L"-WindowsNoEditor.pak");
            bool only_digits = true;
            for (size_t i = start; i < end; ++i) {
                if (wname[i] < L'0' || wname[i] > L'9') {
                    only_digits = false;
                    break;
                }
            }
            if (only_digits) continue; // Skip official game paks
        }

        std::wstring path = L"C:\\Games\\Life is Strange Remastered\\LIS\\Content\\Paks\\";
        path += wname;
        
        FILE* f = _wfopen(path.c_str(), L"rb");
        if (!f) continue;
        
        _fseeki64(f, 0, SEEK_END);
        long long size = _ftelli64(f);
        if (size < 256) { fclose(f); continue; }
        
        _fseeki64(f, size - 256, SEEK_SET);
        std::vector<uint8_t> tail(256);
        fread(tail.data(), 1, 256, f);
        
        int magic_idx = -1;
        for (int i = 0; i < 256 - 24; i++) {
            if (tail[i] == 0xE1 && tail[i+1] == 0x12 && tail[i+2] == 0x6F && tail[i+3] == 0x5A) {
                magic_idx = i;
                break;
            }
        }
        
        if (magic_idx == -1) { fclose(f); continue; }
        
        FPakInfo info;
        memcpy(&info, &tail[magic_idx], sizeof(FPakInfo));
        
        _fseeki64(f, info.IndexOffset, SEEK_SET);
        std::vector<uint8_t> idx_data(info.IndexSize);
        fread(idx_data.data(), 1, info.IndexSize, f);
        
        size_t offset = 0;
        
        auto ReadString = [&](std::string& out) {
            if (offset + 4 > idx_data.size()) return false;
            int32_t len = *(int32_t*)&idx_data[offset];
            offset += 4;
            if (len > 0) {
                if (offset + len > idx_data.size()) return false;
                out.assign((char*)&idx_data[offset], len - 1);
                offset += len;
            } else if (len < 0) {
                int32_t wlen = -len;
                if (offset + wlen * 2 > idx_data.size()) return false;
                out.clear();
                for (int i=0; i<wlen-1; i++) out += (char)idx_data[offset + i*2];
                offset += wlen * 2;
            } else {
                out = "";
            }
            return true;
        };
        
        std::string mount_point;
        ReadString(mount_point);
        
        if (offset + 4 > idx_data.size()) { fclose(f); continue; }
        int32_t num_entries = *(int32_t*)&idx_data[offset];
        offset += 4;
        
        for (int i = 0; i < num_entries; i++) {
            std::string name;
            if (!ReadString(name)) break;
            
            if (offset + 28 > idx_data.size()) break;
            uint64_t entry_offset = *(uint64_t*)&idx_data[offset];
            uint64_t entry_size = *(uint64_t*)&idx_data[offset + 8];
            uint64_t uncomp_size = *(uint64_t*)&idx_data[offset + 16];
            uint32_t comp_method = *(uint32_t*)&idx_data[offset + 24];
            offset += 28 + 20; 
            
            if (info.Version >= 3) {
                if (comp_method != 0) {
                    if (offset + 4 > idx_data.size()) break;
                    uint32_t num_blocks = *(uint32_t*)&idx_data[offset];
                    offset += 4 + num_blocks * 16;
                }
                offset += 5;
            }
            
            std::string full_name = mount_point + name;
            if (full_name.find("CU_") != std::string::npos && full_name.find(".ini") != std::string::npos) {
                std::string lang = "en";
                size_t loc_pos = full_name.find("Localization/");
                if (loc_pos != std::string::npos) {
                    size_t slash = full_name.find('/', loc_pos + 13);
                    if (slash != std::string::npos) {
                        lang = full_name.substr(loc_pos + 13, slash - (loc_pos + 13));
                    }
                }
                
                long long saved_pos = _ftelli64(f);
                
                int header_size = 48;
                if (info.Version >= 3) {
                    if (comp_method != 0) {
                        uint32_t blocks = 0;
                        _fseeki64(f, entry_offset + 48, SEEK_SET);
                        fread(&blocks, 1, 4, f);
                        header_size += 4 + (blocks * 16);
                    }
                    header_size += 5;
                }
                
                _fseeki64(f, entry_offset + header_size, SEEK_SET);
                
                if (comp_method == 0) {
                    std::string data(uncomp_size, 0);
                    fread(&data[0], 1, uncomp_size, f);
                    ParseIniContent(lang, data);
                } else if (comp_method == 1) {
                    std::vector<uint8_t> comp_data(entry_size);
                    fread(comp_data.data(), 1, entry_size, f);
                    
                    std::string uncomp_data(uncomp_size, 0);
                    mz_ulong dest_len = (mz_ulong)uncomp_size;
                    if (mz_uncompress((unsigned char*)&uncomp_data[0], &dest_len, comp_data.data(), (mz_ulong)comp_data.size()) == MZ_OK) {
                        ParseIniContent(lang, uncomp_data);
                    } else {
                        LogLine("[FAN] Failed to decompress %s (comp: %llu, uncomp: %llu)", full_name.c_str(), entry_size, uncomp_size);
                    }
                }
                _fseeki64(f, saved_pos, SEEK_SET);
            }
        }
        
        fclose(f);
    } while (FindNextFileW(hFind, &ffd) != 0);
    FindClose(hFind);
    LogLine("[FAN] Finished scanning paks. HasFanTranslation=%d, Lang=%ls", g_HasFanTranslation, g_FanTranslationLang.c_str());
}

void LoadAllAltData() {
    WIN32_FIND_DATAW ffd;
    HANDLE hFind = FindFirstFileW(L"C:\\Games\\Life is Strange Remastered\\LIS\\Content\\AltData\\*.cue", &ffd);
    if (hFind == INVALID_HANDLE_VALUE) return;
    do {
        std::wstring fname = ffd.cFileName;
        size_t last_us = fname.find_last_of(L"_");
        size_t dot = fname.find_last_of(L".");
        if (last_us == std::wstring::npos || dot == std::wstring::npos || dot <= last_us) continue;
        
        std::wstring suffix = fname.substr(last_us + 1, dot - last_us - 1);
        if (suffix == L"pt-BR" || suffix == L"PT" || suffix == L"POR") continue; // Skip aliases
        
        std::wstring path = L"C:\\Games\\Life is Strange Remastered\\LIS\\Content\\AltData\\";
        path += ffd.cFileName;
        
        FILE* f = _wfopen(path.c_str(), L"rb");
        if (f) {
            fseek(f, 0, SEEK_END);
            size_t size = ftell(f);
            fseek(f, 0, SEEK_SET);
            std::vector<char> buf(size);
            fread(buf.data(), 1, size, f);
            fclose(f);
            
            char* ptr = buf.data();
            size_t len = size;
            if (len >= 3 && (unsigned char)ptr[0] == 0xEF && (unsigned char)ptr[1] == 0xBB && (unsigned char)ptr[2] == 0xBF) {
                ptr += 3; len -= 3; // skip UTF-8 BOM
            }
            
            size_t i = 0;
            while (i < len) {
                std::string key8;
                while (i < len && ptr[i] != 0) { key8 += ptr[i]; i++; }
                i++;
                
                std::string val8;
                while (i < len && ptr[i] != 0) { val8 += ptr[i]; i++; }
                i++;
                
                if (!key8.empty() && !val8.empty()) {
                    int k_len = MultiByteToWideChar(CP_UTF8, 0, key8.c_str(), -1, NULL, 0);
                    std::wstring key(k_len, 0);
                    MultiByteToWideChar(CP_UTF8, 0, key8.c_str(), -1, &key[0], k_len);
                    if (!key.empty() && key.back() == 0) key.pop_back();

                    int v_len = MultiByteToWideChar(CP_UTF8, 0, val8.c_str(), -1, NULL, 0);
                    std::wstring val(v_len, 0);
                    MultiByteToWideChar(CP_UTF8, 0, val8.c_str(), -1, &val[0], v_len);
                    if (!val.empty() && val.back() == 0) val.pop_back();

                    g_AltDataDicts[suffix][key] = val;
                }
            }
        }
    } while (FindNextFileW(hFind, &ffd) != 0);
    FindClose(hFind);
    
    int total = 0;
    for (auto& pair : g_AltDataDicts) total += pair.second.size();
    LogLine("[INIT] Loaded %d total subtitle lines across %zu languages", total, g_AltDataDicts.size());
    LoadFanTranslations();
}

std::wstring GetCurrentCultureSuffix() {
    char path[MAX_PATH];
    ExpandEnvironmentStringsA("%LOCALAPPDATA%\\LIS\\Saved\\Config\\WindowsNoEditor\\Game.ini", path, MAX_PATH);
    FILE* f = fopen(path, "r");
    if (!f) return L"INT";
    char line[256];
    std::string culture = "en";
    while (fgets(line, sizeof(line), f)) {
        if (strncmp(line, "Culture=", 8) == 0) {
            culture = line + 8;
            while (!culture.empty() && (culture.back() == '\r' || culture.back() == '\n')) culture.pop_back();
            break;
        }
    }
    fclose(f);
    
    if (culture.find("pt") == 0) return L"PTB";
    if (culture.find("fr") == 0) return L"FRA";
    if (culture.find("it") == 0) return L"ITA";
    if (culture.find("de") == 0) return L"DEU";
    if (culture.find("es-M") == 0 || culture.find("es-4") == 0) return L"ESM";
    if (culture.find("es") == 0) return L"ESN";
    if (culture.find("ja") == 0) return L"JPN";
    return L"INT";
}

bool __fastcall hook_GetLocalizedText(const wchar_t* key, void* outText) {
    bool found = orig_GetLocalizedText(key, outText);

    if (found || !key || !*key) return found;

    std::wstring normalized = StripObjectSuffix(key);
    
    if (normalized.length() != wcslen(key)) {
        found = orig_GetLocalizedText(normalized.c_str(), outText);
        if (found) {
            return true;
        }
    }

    std::wstring current_lang = GetCurrentCultureSuffix();
    std::wstring original_lang = current_lang;
    if (g_HasFanTranslation) {
        current_lang = g_FanTranslationLang;
    }
    // Only log once per frame or so to avoid spamming, but for debugging just log every miss
    // LogLine("[HOOK] Fallback triggered. Original lang: %ls, Using lang: %ls", original_lang.c_str(), current_lang.c_str());
    auto& dict = g_AltDataDicts[current_lang];
    auto it = dict.find(normalized);
    if (it != dict.end()) {
        std::wstring translated = it->second;
        
        bool dummy_found = orig_GetLocalizedText(L"$GT_Menus_Splashes_WARNING", outText);
        if (dummy_found) {
            UE4String* s = (UE4String*)outText;
            if (s->ArrayMax > 0) {
                int copy_len = translated.length();
                if (copy_len > s->ArrayMax - 1) copy_len = s->ArrayMax - 1;
                
                wcsncpy(s->Data, translated.c_str(), copy_len);
                s->Data[copy_len] = 0;
                s->ArrayNum = copy_len + 1;
                return true;
            }
        }
    }

    return false;
}

// ULiSSubtitlesWidget::SetSubtitleCue(this, FSubtitleStruct* Cue) at RVA
// 0x95c670. Cue->Text (offset 0) is the string the widget is about to draw, so
// this is the ground truth for what the player sees. Read-only.
static const uintptr_t kSetSubtitleCueRVA = 0x95c670;
static const unsigned char kSetSubtitleCuePrologue[] = {
    0x48, 0x89, 0x54, 0x24, 0x10,  // mov [rsp+0x10], rdx
    0x48, 0x89, 0x4C, 0x24, 0x08,  // mov [rsp+0x08], rcx
    0x48, 0x83, 0xEC, 0x38         // sub rsp, 0x38
};

typedef void (__fastcall *t_SetSubtitleCue)(void* self, void* cue);
static t_SetSubtitleCue orig_SetSubtitleCue = NULL;

void __fastcall hook_SetSubtitleCue(void* self, void* cue) {
    LogLine("[SHOW] '%s'", PeekString(cue).c_str());
    orig_SetSubtitleCue(self, cue);
}

typedef HANDLE (WINAPI *t_CreateFileW)(LPCWSTR, DWORD, DWORD, LPSECURITY_ATTRIBUTES, DWORD, DWORD, HANDLE);
t_CreateFileW orig_CreateFileW = nullptr;

HANDLE WINAPI hook_CreateFileW(
    LPCWSTR lpFileName,
    DWORD dwDesiredAccess,
    DWORD dwShareMode,
    LPSECURITY_ATTRIBUTES lpSecurityAttributes,
    DWORD dwCreationDisposition,
    DWORD dwFlagsAndAttributes,
    HANDLE hTemplateFile
) {
    HANDLE h = orig_CreateFileW(lpFileName, dwDesiredAccess, dwShareMode, lpSecurityAttributes, dwCreationDisposition, dwFlagsAndAttributes, hTemplateFile);
    if (lpFileName && wcsstr(lpFileName, L"AltData")) {
        LogLine("[FILE] CreateFileW('%s') -> %s", Utf8(lpFileName).c_str(), (h != INVALID_HANDLE_VALUE) ? "OK" : "FAILED");
    }
    return h;
}

DWORD WINAPI SubtitleModThread(LPVOID lpParam) {
    // Wait for the game to unpack itself
    Sleep(2000);

    if (MH_Initialize() != MH_OK) { return 1; }
    
    LoadAllAltData();
    
    MH_CreateHookApi(L"kernel32", "CreateFileW", (LPVOID)&hook_CreateFileW, (LPVOID*)&orig_CreateFileW);
    MH_EnableHook((LPVOID)GetProcAddress(GetModuleHandleW(L"kernel32"), "CreateFileW"));
    LogLine("[INIT] CreateFileW file trace active");

    HMODULE hMain = GetModuleHandleA(NULL);
    if (!hMain) {
        LogLine("[INIT] no main module; hook not installed");
        return 0;
    }

    uintptr_t base = (uintptr_t)hMain;

    // Only patch the game itself. The same proxy dropped next to the launcher
    // would otherwise be injected into a process where this RVA means nothing.
    char exePath[MAX_PATH] = { 0 };
    GetModuleFileNameA(hMain, exePath, MAX_PATH);
    const char* exeName = strrchr(exePath, '\\');
    exeName = exeName ? exeName + 1 : exePath;
    if (_stricmp(exeName, "LiS-Win64-Shipping.exe") != 0) {
        LogLine("[INIT] host is '%s', not the game; hook not installed", exeName);
        return 0;
    }

    uintptr_t gltAddr = base + kGetLocalizedTextRVA;
    if (memcmp((void*)gltAddr, kGetLocalizedTextPrologue, sizeof(kGetLocalizedTextPrologue)) == 0) {
        if (MH_CreateHook((void*)gltAddr, &hook_GetLocalizedText, (LPVOID*)&orig_GetLocalizedText) == MH_OK) {
            MH_EnableHook((void*)gltAddr);
                    }
    } else {
            }

    uintptr_t wcsicmpAddr = base + kWcsicmpRVA;
    if (memcmp((void*)wcsicmpAddr, kWcsicmpPrologue, sizeof(kWcsicmpPrologue)) == 0) {
        if (MH_CreateHook((void*)wcsicmpAddr, &hook_wcsicmp, (LPVOID*)&orig_wcsicmp) == MH_OK) {
            MH_EnableHook((void*)wcsicmpAddr);
            LogLine("[INIT] wcsicmp hooked at 0x%zx", wcsicmpAddr);
        }
    } else {
        LogLine("[INIT] wcsicmp prologue mismatch, aborting hook");
    }

    uintptr_t showTarget = (uintptr_t)hMain + kSetSubtitleCueRVA;
    if (memcmp((const void*)showTarget, kSetSubtitleCuePrologue,
               sizeof(kSetSubtitleCuePrologue)) == 0 &&
        MH_CreateHook((LPVOID)showTarget, (LPVOID)&hook_SetSubtitleCue,
                      (LPVOID*)&orig_SetSubtitleCue) == MH_OK &&
        MH_EnableHook((LPVOID)showTarget) == MH_OK) {
        LogLine("[INIT] SetSubtitleCue logger active at %p", (void*)showTarget);
    } else {
        LogLine("[INIT] SetSubtitleCue logger not installed");
    }
    return 0;
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID) {
    switch (ul_reason_for_call) {
    case DLL_PROCESS_ATTACH:
        DisableThreadLibraryCalls(hModule);
        InitLogPath(hModule);
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

