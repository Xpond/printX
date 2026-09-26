"""Install, exercise and uninstall the actual release package on Windows."""
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parent.parent
installer = root / 'dist/installer/PrintShop-Tools-Setup.exe'
report = Path(sys.argv[1]).resolve()
report.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='PrintShop install é ') as temporary:
    target = Path(temporary) / 'PrintShop Tools'
    subprocess.run([str(installer), '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART',
                    '/SP-', f'/DIR={target}', f'/LOG={report / "install.log"}'],
                   check=True, timeout=180)
    try:
        assert (target / 'samples/04 three pages.pdf').is_file()
        subprocess.run([sys.executable, str(root / 'scripts/check_frozen.py'),
                        str(target / 'PrintShop Tools.exe'), str(report)],
                       check=True, timeout=120)
    finally:
        subprocess.run([str(target / 'unins000.exe'), '/VERYSILENT',
                        '/SUPPRESSMSGBOXES', '/NORESTART', f'/LOG={report / "uninstall.log"}'],
                       check=True, timeout=90)
    assert not (target / 'PrintShop Tools.exe').exists(), 'Uninstall left the executable behind'
print('Installer, installed app, and uninstall passed.')
