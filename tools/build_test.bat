@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
cd /d "%~dp0"
cl.exe /nologo /O2 /EHsc /std:c++17 /utf-8 test_lookup.cpp /Fe:test_lookup.exe /link /SUBSYSTEM:CONSOLE
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
echo [OK] test_lookup.exe built
