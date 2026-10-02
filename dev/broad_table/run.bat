@echo off
cd /d "%~dp0\..\.."
python dev\broad_table\main.py
if errorlevel 1 pause
