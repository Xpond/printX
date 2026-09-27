"""Wrap the one-folder build in a Windows installer; requires Inno Setup 6."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess

root = Path(__file__).resolve().parent.parent
compiler = shutil.which('ISCC')
if not compiler:
    compiler = Path(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)')) / 'Inno Setup 6/ISCC.exe'
if not Path(compiler).is_file():
    raise SystemExit('Install Inno Setup 6 from https://jrsoftware.org/isdl.php, then run build.bat again.')

bundle = root / 'dist/PrintShop Tools'
shutil.copytree(root / 'samples', bundle / 'samples', dirs_exist_ok=True)
shutil.copy2(root / 'docs/PHASE3-TESTING.md', bundle / 'Read me first.md')
subprocess.run([str(compiler), str(root / 'installer.iss')], cwd=root, check=True)
installer = root / 'dist/installer/PrintShop-Tools-Setup.exe'
with installer.open('rb') as source:
    digest = hashlib.file_digest(source, 'sha256').hexdigest()
(installer.parent / 'SHA256SUMS.txt').write_text(f'{digest}  {installer.name}\n', encoding='utf-8')
print(f'Installer ready: {installer}')
