@echo off
title GCDC HSE Executive Dashboard
cd /d "%~dp0"
echo =========================================================
echo   Starting GCDC HSE Executive Web Dashboard...
echo   Kharafi National / SBARC - GCDC Project
echo   URL: http://localhost:8550
echo =========================================================
echo.
streamlit run app.py --server.port 8550
pause
