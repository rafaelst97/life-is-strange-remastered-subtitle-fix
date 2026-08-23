$procmon = "C:\Users\rafae\AppData\Local\Microsoft\WinGet\Packages\Microsoft.Sysinternals.ProcessMonitor_Microsoft.Winget.Source_8wekyb3d8bbwe\Procmon64.exe"
$pmlPath = "D:\Projetos\LiS_Remastered_Subtitle_Mod\trace.pml"
$csvPath = "D:\Projetos\LiS_Remastered_Subtitle_Mod\trace.csv"

Write-Host "Process Monitor executable: $procmon"
if (Test-Path $procmon) {
    Write-Host "ProcMon is ready for automatic background tracing!"
} else {
    Write-Host "ProcMon not found at $procmon"
}
