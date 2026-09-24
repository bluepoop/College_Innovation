@echo off
cd /d %~dp0
python -m pip install -r requirements.txt pyinstaller
python -m PyInstaller --noconfirm --onefile --windowed --name chemDb-client main.py
echo.
echo dist\chemDb-client.exe
pause
