@echo off
setlocal
cd /d "%~dp0"
python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 exit /b 1
python -m PyInstaller --noconfirm --onefile --windowed --name chemDb-table-demo --collect-all openpyxl --hidden-import xlrd --hidden-import defusedxml.ElementTree main.py
if errorlevel 1 exit /b 1
echo EXE: %~dp0dist\chemDb-table-demo.exe
pause
