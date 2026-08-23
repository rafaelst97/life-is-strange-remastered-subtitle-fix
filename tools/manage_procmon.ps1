param (
    [switch]$Start,
    [switch]$Stop
)

$procmon = "C:\Users\rafae\AppData\Local\Microsoft\WinGet\Packages\Microsoft.Sysinternals.ProcessMonitor_Microsoft.Winget.Source_8wekyb3d8bbwe\Procmon64.exe"
$pml = "D:\Projetos\LiS_Remastered_Subtitle_Mod\trace.pml"
$csv = "D:\Projetos\LiS_Remastered_Subtitle_Mod\trace.csv"

if ($Start) {
    if (Test-Path $pml) { Remove-Item $pml -Force }
    if (Test-Path $csv) { Remove-Item $csv -Force }
    Write-Host "[PROCMON] Starting background trace capture to $pml..."
    Start-Process -FilePath $procmon -ArgumentList "/Quiet /Minimized /AcceptEula /BackingFile `"$pml`""
    Write-Host "[PROCMON] Trace is ACTIVE. Open the game, reproduce the subtitle, and close the game."
}

if ($Stop) {
    Write-Host "[PROCMON] Stopping trace and saving CSV..."
    Start-Process -FilePath $procmon -ArgumentList "/Terminate" -Wait
    Start-Sleep -Seconds 2
    Start-Process -FilePath $procmon -ArgumentList "/OpenLog `"$pml`" /SaveAs `"$csv`"" -Wait
    Write-Host "[PROCMON] Export complete: $csv"
}
