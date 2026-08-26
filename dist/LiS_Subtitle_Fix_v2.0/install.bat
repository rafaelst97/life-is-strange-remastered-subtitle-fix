@echo off
setlocal enabledelayedexpansion
title Life is Strange Remastered - Subtitle Fix Installer
color 0B

echo =======================================================================
echo     Life is Strange Remastered - Subtitle Fix Mod v2.0
echo =======================================================================
echo.

set "DEFAULT_GAME_PATH=C:\Games\Life is Strange Remastered"
if exist "%DEFAULT_GAME_PATH%\LIS\Binaries\Win64\LiS-Win64-Shipping.exe" (
    set "GAME_DIR=%DEFAULT_GAME_PATH%"
    goto :FoundGame
)

echo Game not found in the default path: %DEFAULT_GAME_PATH%
set /p "GAME_DIR=Enter your Life is Strange Remastered game folder: "

:FoundGame
if not exist "%GAME_DIR%\LIS\Binaries\Win64\LiS-Win64-Shipping.exe" (
    color 0C
    echo [ERROR] Could not find LiS-Win64-Shipping.exe in:
    echo "%GAME_DIR%\LIS\Binaries\Win64\"
    pause
    exit /b 1
)

echo [OK] Game directory detected: "%GAME_DIR%"
echo.
echo Installing XINPUT1_3.dll ...

copy /Y "%~dp0XINPUT1_3.dll" "%GAME_DIR%\LIS\Binaries\Win64\XINPUT1_3.dll" >nul
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [ERROR] Failed to copy the file. Make sure the game is closed.
    pause
    exit /b 1
)
echo [OK] Installed to LIS\Binaries\Win64\XINPUT1_3.dll

if exist "%GAME_DIR%\XINPUT1_3.dll" (
    copy /Y "%~dp0XINPUT1_3.dll" "%GAME_DIR%\XINPUT1_3.dll" >nul
    echo [OK] Updated launcher-side copy at the game root.
)

echo.
echo [SUCCESS] Subtitle Fix installed! Subtitles will no longer break after
echo scene/episode transitions, in any language.
echo Launch the game normally via Steam, Epic or LiS.exe.
echo.
pause
