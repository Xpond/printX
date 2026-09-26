# PrintShop Tools

Offline Windows tools for a print shop. Phase 1 implements **Make PDF** for images and existing PDFs, with a shared desktop interface, background workers, cancellation, settings, and logs.

[Download the Windows installer (.exe)](https://github.com/Xpond/printX/releases/latest/download/PrintShop-Tools-Setup.exe). Run it, then open **PrintShop Tools** from the Start menu. Supports Windows 10/11 x64; no Python installation or ZIP extraction needed. See [the test checklist](PHASE1-TESTING.md). Downloads are public once the repository is public.

## Development

Use Python 3.14 and a virtual environment:

```sh
python -m venv .venv
# Linux: source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install --only-binary=:all: -r requirements-dev.txt
python -m pytest -q
python app.py
```

On Windows, install Python 3.14 and [Inno Setup 6](https://jrsoftware.org/isdl.php), then double-click `build.bat`. It installs pinned dependencies, runs tests, creates the one-folder app and `dist/installer/PrintShop-Tools-Setup.exe`, then tests installation, launch, and uninstall.

GitHub Actions performs the same Windows checks. Push a version tag such as `v0.1.0` (matching `AppVersion` in `installer.iss`) to publish the tested installer and its SHA-256 checksum to GitHub Releases. The download link above always points to the latest release.

Processing is in `core/`, without Qt. One warm worker process handles PDF jobs; a separate lazy process makes visible thumbnails. Cancelling terminates the job process and removes its private staging directories. Completed PDFs are published atomically without overwriting existing files. On Windows, this uses same-volume rename; on Linux, a hard link publishes the completed file.

The `samples/` images are generated test graphics, not real photos. Regenerate them with `python scripts/samples.py`. The password sample uses `printshop`. The Word and broken PDF samples test unsupported/corrupt input handling.

All application copy is in `ui/text.py`. Atkinson Hyperlegible is bundled under the [SIL Open Font License](assets/fonts/OFL.txt), from [Google Fonts](https://github.com/google/fonts/tree/main/ofl/atkinsonhyperlegible).

The full specification and phase gates are in [PLAN.md](PLAN.md); current status is in [AGENTS.md](AGENTS.md). Installer delivery was brought forward for testing; packaging completion and shop documentation remain in phases 5 and 6.
