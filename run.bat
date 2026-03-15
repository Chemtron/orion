@echo off
title ORION — Signal Intelligence
cd /d C:\Projects\orion

if not exist "data" mkdir data
if not exist "data\logs" mkdir data\logs

echo ==============================
echo  ORION Signal Intelligence
echo  Starting server...
echo ==============================
echo.
echo Open browser: http://127.0.0.1:5000
echo Press Ctrl+C to stop
echo.

python orion.py
pause
