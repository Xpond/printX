"""Launch an executable from outside its checkout and verify its smoke report."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

executable = Path(sys.argv[1]).resolve()
destination = Path(sys.argv[2]).resolve()
destination.mkdir(parents=True, exist_ok=True)
environment = dict(os.environ, QT_QPA_PLATFORM='offscreen', QT_QPA_PLATFORMTHEME='generic')
started = time.monotonic()
process = subprocess.Popen([str(executable), '--smoke-test', str(destination)],
                           cwd=tempfile.gettempdir(), env=environment)
first_frame = None
while process.poll() is None and time.monotonic() - started < 90:
    if first_frame is None and (destination / '01-home-light.png').exists():
        first_frame = time.monotonic() - started
    time.sleep(.02)
if process.poll() is None:
    process.kill()
    process.wait()
    raise SystemExit('Packaged smoke test timed out')
if process.returncode != 0:
    raise SystemExit(f'Packaged app exited {process.returncode}')
report = json.loads((destination / 'smoke.json').read_text())
assert report['passed']
report['external_startup_seconds'] = first_frame
(destination / 'smoke.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
