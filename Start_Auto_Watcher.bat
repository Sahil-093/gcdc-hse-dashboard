@echo off
title GCDC HSE Dashboard - Real-Time Excel Auto-Watcher
color 0B
cd /d "%~dp0"
echo ================================================================
echo     GCDC HSE DASHBOARD - REAL-TIME EXCEL AUTO-WATCHER
echo ================================================================
echo.
echo Whenever you save (Ctrl + S) in your Excel file,
echo the dashboard will automatically sync and update live!
echo.
python excel_watcher.py
pause
