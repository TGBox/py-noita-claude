@echo off
rem Startet den unbeaufsichtigten Kartenlauf (tools\kartenlauf.py). Argumente werden durchgereicht,
rem z. B.  kartenlauf.bat --max 3   oder   kartenlauf.bat --bis 17:00
cd /d "%~dp0.."
uv run python tools\kartenlauf.py %*
pause
