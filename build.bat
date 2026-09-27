@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  py -3.14 -m venv .venv
  if errorlevel 1 goto fail
)
.venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements-dev.txt
if errorlevel 1 goto fail
.venv\Scripts\python.exe scripts\ghostscript.py
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pytest -q
if errorlevel 1 goto fail
.venv\Scripts\python.exe scripts\build.py
if errorlevel 1 goto fail
.venv\Scripts\python.exe scripts\build_installer.py
if errorlevel 1 goto fail
.venv\Scripts\python.exe scripts\check_installer.py artifacts\installer-smoke
if errorlevel 1 goto fail
echo Build ready: dist\installer\PrintShop-Tools-Setup.exe
pause
exit /b 0
:fail
echo Build failed. See the message above.
pause
exit /b 1
