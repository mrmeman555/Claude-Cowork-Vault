@echo off
REM setup-transcript-sync-windows.bat — Device 1 (Windows) transcript sync setup
REM Run this ONCE as Administrator on the Windows machine.
REM Creates a scheduled task that copies Claude Code transcripts to shared drive every 1 minute.

set SRC=%USERPROFILE%\.claude\projects
set DST=Z:\Projects\ML_OS\transcripts\device-1

echo Creating target directory...
if not exist "%DST%" mkdir "%DST%"

echo Creating scheduled task MLOS-TranscriptSync...
schtasks /create /tn "MLOS-TranscriptSync" /tr "robocopy \"%SRC%\" \"%DST%\" *.jsonl /E /XO /R:1 /W:1 /NFL /NDL /NJH /NJS" /sc minute /mo 1 /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS: Scheduled task created.
    echo Transcripts will sync from %SRC% to %DST% every 1 minute.
    echo.
    echo To verify: schtasks /query /tn "MLOS-TranscriptSync"
    echo To remove:  schtasks /delete /tn "MLOS-TranscriptSync" /f
) else (
    echo.
    echo ERROR: Failed to create scheduled task. Run as Administrator.
)
pause
