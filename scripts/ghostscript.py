"""Fetch the pinned Ghostscript DLL that Compress PDF bundles on Windows; needs 7-Zip."""
import hashlib
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path

URL = 'https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10080/gs10080w64.exe'
SHA256 = '52a91b8bf09298788d7a57b9206127026c23eacd75405f0a131e26dc381dce50'
target = Path(__file__).resolve().parent.parent / 'vendor/ghostscript'

if not (target / 'gsdll64.dll').exists():
    with tempfile.TemporaryDirectory() as temporary:
        installer = Path(temporary) / 'ghostscript.exe'
        urllib.request.urlretrieve(URL, installer)
        if hashlib.sha256(installer.read_bytes()).hexdigest() != SHA256:
            raise SystemExit('The Ghostscript download does not match its pinned checksum.')
        seven = shutil.which('7z') or r'C:\Program Files\7-Zip\7z.exe'
        subprocess.run([seven, 'e', '-y', '-r', f'-o{target}', str(installer), 'gsdll64.dll', 'COPYING'],
                       check=True, stdout=subprocess.DEVNULL)  # The DLL and its AGPL licence.
print(f'Ghostscript is ready in {target}')
