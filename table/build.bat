@echo off
setlocal
cd /d "%~dp0"
python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 exit /b 1
python -m PyInstaller --clean --noconfirm chemDb-table-demo.spec
if errorlevel 1 exit /b 1
echo EXE: %~dp0dist\chemDb-table-demo.exe
pause
