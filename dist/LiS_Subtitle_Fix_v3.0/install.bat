@echo off
setlocal
title Life is Strange Remastered - Subtitle Fix Installer
color 0B

echo =======================================================================
echo     Life is Strange Remastered - Subtitle Fix
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
    echo [ERROR] LiS-Win64-Shipping.exe not found in "%GAME_DIR%\LIS\Binaries\Win64\"
    pause
    exit /b 1
)

copy /Y "%~dp0XINPUT1_3.dll" "%GAME_DIR%\LIS\Binaries\Win64\XINPUT1_3.dll" >nul
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [ERROR] Could not copy XINPUT1_3.dll. Close the game and try again.
    pause
    exit /b 1
)

echo [OK] Installed to "%GAME_DIR%\LIS\Binaries\Win64\XINPUT1_3.dll"
echo.
echo Launch the game normally. To confirm the fix is running, check
echo XINPUT1_3.log in that same folder for "subtitle fix active".
echo.
pause
