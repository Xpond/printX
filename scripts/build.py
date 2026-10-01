"""Portable build; run with the project environment's Python."""
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
command = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--onedir',
           '--windowed', '--noupx', '--name', 'PrintShop Tools', '--icon', 'assets/icon.ico',
           '--add-data', 'assets:assets', '--collect-all', 'pillow_heif',
           '--exclude-module', 'PySide6.QtWebEngineCore', '--exclude-module', 'PySide6.QtWebEngineWidgets',
           '--exclude-module', 'PySide6.QtQml', '--exclude-module', 'PySide6.QtQuick',
           '--exclude-module', 'PySide6.QtMultimedia', '--exclude-module', 'tkinter',
           '--exclude-module', 'pytest', '--exclude-module', 'docx']
if sys.platform == 'win32':
    command += ['--manifest', 'assets/windows.manifest', '--add-binary', 'vendor/ghostscript/gsdll64.dll:.',
                '--add-data', 'vendor/ghostscript/COPYING:ghostscript']
subprocess.run(command + ['app.py'], cwd=root, check=True)
