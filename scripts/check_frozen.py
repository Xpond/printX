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
environment = dict(os.environ, QT_QPA_PLATFORM='windows' if os.name == 'nt' else 'offscreen',
                   LOCALAPPDATA=str(destination / 'state'), XDG_STATE_HOME=str(destination / 'state'))
if os.name == 'nt':
    environment.pop('QT_QPA_PLATFORMTHEME', None)
else:
    environment['QT_QPA_PLATFORMTHEME'] = 'generic'
started = time.monotonic()
command = ([sys.executable] if executable.suffix == '.py' else []) + [str(executable)]
process = subprocess.Popen(command + ['--smoke-test', str(destination)],
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
    for log in destination.rglob('*.log'):
        print(log.read_text(encoding='utf-8', errors='replace')[-10000:])
    raise SystemExit(f'Packaged app exited {process.returncode}')
report = json.loads((destination / 'smoke.json').read_text())
assert report['passed']
report['external_startup_seconds'] = first_frame
(destination / 'smoke.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
