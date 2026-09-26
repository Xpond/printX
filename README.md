# PrintShop Tools

Offline Windows tools for a print shop. Phase 1 implements **Make PDF** for images and existing PDFs, with a shared desktop interface, background workers, cancellation, settings, and logs.

Download the portable Windows x64 ZIP from a successful [Windows build](https://github.com/Xpond/printX/actions/workflows/windows.yml). Extract the whole ZIP and open **PrintShop Tools.exe**. See [the VM test checklist](PHASE1-TESTING.md).

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

On Windows, `build.bat` installs pinned dependencies, runs tests, and creates a one-folder build in `dist/PrintShop Tools`. Python 3.14 must be installed on the build machine; the finished app needs no Python installation. GitHub Actions builds and tests it on Windows automatically.

Processing is in `core/`, without Qt. One warm worker process handles PDF jobs; a separate lazy process makes visible thumbnails. Cancelling terminates the job process and removes its private staging directories. Completed PDFs are published atomically without overwriting existing files. On Windows, this uses same-volume rename; on Linux, a hard link publishes the completed file.

The `samples/` images are generated test graphics, not real photos. Regenerate them with `python scripts/samples.py`. The password sample uses `printshop`. The Word and broken PDF samples test unsupported/corrupt input handling.

All application copy is in `ui/text.py`. Atkinson Hyperlegible is bundled under the [SIL Open Font License](assets/fonts/OFL.txt), from [Google Fonts](https://github.com/google/fonts/tree/main/ofl/atkinsonhyperlegible).

The full specification and phase gates are in [PLAN.md](PLAN.md). Installer work and shop documentation follow in phases 5 and 6.
