@echo off
title Sync HSE Dashboard with Excel
cd /d "%~dp0"
echo ========================================================
echo   Syncing HSE Dashboard with Latest Excel Workbook...
echo ========================================================
python sync_excel.py
pause
