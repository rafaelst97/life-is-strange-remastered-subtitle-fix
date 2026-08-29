@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
cd /d "D:\Projetos\LiS_Remastered_Subtitle_Mod\tools"
cl.exe /O2 /EHsc /std:c++17 /utf-8 test_hook.cpp /Fe:test_hook.exe /I..\src
