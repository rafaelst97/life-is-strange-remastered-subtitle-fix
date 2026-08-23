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
echo Installing Subtitle Fix Mod (Native Proxy + UE4 Engine Fixes)...

xcopy /E /I /Y "%~dp0mod_package\Binaries\Win64" "%GAME_DIR%\LIS\Binaries\Win64" >nul

if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [ERROR] Failed to install mod files. Make sure the game is closed.
    pause
    exit /b 1
)

echo [SUCCESS] Subtitle Fix Mod installed successfully!
echo All subtitle bug fixes across Episodes 1 to 5 are now active.
echo You can launch Life is Strange Remastered normally via Steam, Epic, or LiS.exe.
echo.
pause
