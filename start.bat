@echo off
REM Assessment Portal - Local / Windows Startup Script
cd /d "%~dp0"

echo ==========================================================
echo  Starting Assessment Portal Server (Mavrista Technologies)
echo ==========================================================

if not exist data mkdir data

python server.py
pause

