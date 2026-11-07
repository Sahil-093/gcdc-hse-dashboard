@echo off
title GCDC HSE Dashboard - 1-Click Excel Sync
color 0A
cd /d "%~dp0"
echo ================================================================
echo        GCDC HSE DASHBOARD - 1-CLICK EXCEL SYNC & DEPLOY
echo ================================================================
echo.
echo Reading latest Excel workbook and updating dashboard...
python sync_engine.py
echo.
echo ================================================================
echo Sync Completed!
echo Live GitHub Pages Link:
echo https://sahil-093.github.io/gcdc-hse-dashboard/
echo ================================================================
echo.
pause
