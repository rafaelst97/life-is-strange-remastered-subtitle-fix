@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"

cd /d "%~dp0"

echo Compiling XINPUT1_3.dll (XInput proxy + GetLocalizedText hook + miniz)...
rem /MT: static CRT, so the shipped DLL has no VC++ redistributable dependency.
cl.exe /nologo /O2 /MT /W3 /EHsc /std:c++17 /utf-8 /I. /Iminhook /LD ^
    xinput_proxy.cpp ^
    miniz.c ^
    minhook/buffer.c ^
    minhook/hook.c ^
    minhook/trampoline.c ^
    minhook/hde64.c ^
    /link /OUT:"XINPUT1_3.dll" /DEF:"xinput.def" user32.lib

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Build failed!
    exit /b %ERRORLEVEL%
)

echo [SUCCESS] XINPUT1_3.dll built.
copy /Y "XINPUT1_3.dll" "..\mod_package\Binaries\Win64\XINPUT1_3.dll"
copy /Y "XINPUT1_3.dll" "C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\XINPUT1_3.dll"
