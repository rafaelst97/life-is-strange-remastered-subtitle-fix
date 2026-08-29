@echo off
setlocal
title Life is Strange Remastered - Subtitle Fix Uninstaller
color 0E

set "DEFAULT_GAME_PATH=C:\Games\Life is Strange Remastered"
if exist "%DEFAULT_GAME_PATH%\LIS\Binaries\Win64\LiS-Win64-Shipping.exe" (
    set "GAME_DIR=%DEFAULT_GAME_PATH%"
    goto :FoundGame
)
set /p "GAME_DIR=Enter your Life is Strange Remastered game folder: "

:FoundGame
if exist "%GAME_DIR%\LIS\Binaries\Win64\XINPUT1_3.dll" (
    del /f /q "%GAME_DIR%\LIS\Binaries\Win64\XINPUT1_3.dll"
    echo [OK] Removed LIS\Binaries\Win64\XINPUT1_3.dll
)
if exist "%GAME_DIR%\XINPUT1_3.dll" (
    del /f /q "%GAME_DIR%\XINPUT1_3.dll"
    echo [OK] Removed launcher-side XINPUT1_3.dll
)
if exist "%GAME_DIR%\LIS\Binaries\Win64\LiS_SubtitleFix.log" (
    del /f /q "%GAME_DIR%\LIS\Binaries\Win64\LiS_SubtitleFix.log"
    echo [OK] Removed LiS_SubtitleFix.log
)

echo.
echo [DONE] Subtitle Fix removed. The game is back to its original behavior.
echo.
pause
