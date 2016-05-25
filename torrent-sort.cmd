rem python torrent-sort.py "HVOB - Lion - 2013 (WEB - MP3 - V0 (VBR))-32268061.torrent"

rem Clean up output
@echo off

rem Change working directly to the one this batch file is in
pushd %~dp0

rem Execute our program
python torrent-sort.py %1

rem Wait so the user can see our output
pause