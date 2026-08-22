@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"

cd /d "D:\Projetos\LiS_Remastered_Subtitle_Mod\src"

echo Compiling XINPUT1_3.dll with MinHook and Master Subtitles...
cl.exe /O2 /MD /W3 /I. /Iminhook /LD ^
    xinput_proxy.cpp ^
    minhook/buffer.c ^
    minhook/hook.c ^
    minhook/trampoline.c ^
    minhook/hde64.c ^
    /link /OUT:"XINPUT1_3.dll" /DEF:"xinput.def" user32.lib

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Build failed!
    exit /b %ERRORLEVEL%
)

echo [SUCCESS] XINPUT1_3.dll built successfully!
copy /Y "XINPUT1_3.dll" "C:\Games\Life is Strange Remastered\LIS\Binaries\Win64\XINPUT1_3.dll"
copy /Y "XINPUT1_3.dll" "D:\Projetos\LiS_Remastered_Subtitle_Mod\mod_package\Binaries\Win64\XINPUT1_3.dll"

