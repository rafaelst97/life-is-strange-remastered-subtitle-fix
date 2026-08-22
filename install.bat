@echo off
setlocal
echo =========================================================
echo Life is Strange Remastered - Subtitle Fix Mod Installer
echo =========================================================
echo.

set "DEFAULT_GAME_PATH=C:\Games\Life is Strange Remastered"

if exist "%DEFAULT_GAME_PATH%\LIS\Binaries\Win64" (
    set "TARGET_DIR=%DEFAULT_GAME_PATH%\LIS\Binaries\Win64"
) else (
    echo Jogo nao encontrado no caminho padrao: %DEFAULT_GAME_PATH%
    set /p "TARGET_DIR=Digite o caminho da pasta Binaries\Win64 do jogo: "
)

if not exist "%TARGET_DIR%" (
    echo Erro: Caminho invalido!
    pause
    exit /b 1
)

echo.
echo Instalando arquivos do mod em: %TARGET_DIR%
xcopy /E /I /Y "mod_package\Binaries\Win64\*" "%TARGET_DIR%\"

if %ERRORLEVEL% equ 0 (
    echo.
    echo =========================================================
    echo Mod instalado com sucesso!
    echo Agora voce pode abrir o jogo normalmente.
    echo =========================================================
) else (
    echo Erro ao copiar os arquivos.
)

echo.
pause
