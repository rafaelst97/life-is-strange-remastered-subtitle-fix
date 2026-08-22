@echo off
setlocal enabledelayedexpansion
title Life is Strange Remastered - Subtitle Fix Installer
color 0B

echo =======================================================================
echo     Life is Strange Remastered - Subtitle & Localization Fix
echo =======================================================================
echo.

set "DEFAULT_GAME_PATH=C:\Games\Life is Strange Remastered"
if exist "%DEFAULT_GAME_PATH%\LIS\Binaries\Win64\LiS-Win64-Shipping.exe" (
    set "GAME_DIR=%DEFAULT_GAME_PATH%"
    goto :FoundGame
)

echo Game not found in default path: %DEFAULT_GAME_PATH%
set /p "GAME_DIR=Please enter your Life is Strange Remastered game folder: "

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
echo Installing Native Subtitle Fix Mod (XINPUT1_3.dll)...

copy /Y "%~dp0mod_package\Binaries\Win64\XINPUT1_3.dll" "%GAME_DIR%\LIS\Binaries\Win64\XINPUT1_3.dll" >nul

if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [ERROR] Failed to copy XINPUT1_3.dll. Make sure the game is closed.
    pause
    exit /b 1
)

echo [SUCCESS] Mod installed successfully!
echo You can now launch Life is Strange Remastered normally.
echo.
pause
