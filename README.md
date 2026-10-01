# PrintShop Tools

Windows tools for a print shop, offline except for two optional AI tools. Phase 1 implements **Make PDF** for images and existing PDFs, with a shared desktop interface, background workers, cancellation, settings, and logs. Phase 2 adds **Upscale image**: classic Lanczos resampling with a light unsharp mask (no AI), print-size fitting, and sharpness badges. Phase 3 adds **Compress PDF** (Ghostscript, with Smallest, Recommended and Print quality levels) and **Split PDF** (every page, page ranges, or every N pages). The AI tools use OpenRouter with a key pasted in Settings: **Remove background** (Ming, free) cuts out the subject or removes something described, applied to the full-size original, and **Enhance image** (Muse) is a chat that saves each new version of a photo.

[Download the Windows installer (.exe)](https://github.com/Xpond/printX/releases/latest/download/PrintShop-Tools-Setup.exe). Run it, then open **PrintShop Tools** from the Start menu. Supports Windows 10/11 x64; no Python installation or ZIP extraction needed. See the checklists for [the AI tools](docs/AI-TESTING.md), [phase 3](docs/PHASE3-TESTING.md), [phase 2](docs/PHASE2-TESTING.md) and [phase 1](docs/PHASE1-TESTING.md). Downloads are public once the repository is public.

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

Processing is in `core/`, without Qt. Each tool has one warm worker process; a separate lazy process makes visible thumbnails. Compress runs Ghostscript through its C API inside the job process, so cancelling stops it too; Windows builds bundle the pinned Ghostscript DLL that `scripts/ghostscript.py` downloads (AGPL, like PyMuPDF). On Linux, install Ghostscript; Compress and its tests use the system library. Upscale runs several images at once in threads (Pillow releases the GIL; as fast as processes in benchmarks, with less memory) within a 512 MB budget, and resizes in strips so a huge result needs one full-size buffer. The AI tools call OpenRouter's image API with the standard library (`core/openrouter.py`), one image per request in the job process; on Windows the key is encrypted for the user with DPAPI. Cancelling terminates the job process and removes its private staging directories. Completed PDFs are published atomically without overwriting existing files. On Windows, this uses same-volume rename; on Linux, a hard link publishes the completed file.

The `samples/` images are generated test graphics, not real photos; the QR-style code does not scan. Regenerate them with `python scripts/samples.py`. The password sample uses `printshop`. The Word and broken PDF samples test unsupported/corrupt input handling.

All application copy is in `ui/text.py`. Atkinson Hyperlegible is bundled under the [SIL Open Font License](assets/fonts/OFL.txt), from [Google Fonts](https://github.com/google/fonts/tree/main/ofl/atkinsonhyperlegible).

The full specification and phase gates are in [docs/PLAN.md](docs/PLAN.md); current status is in [AGENTS.md](AGENTS.md). Installer delivery was brought forward for testing; packaging completion and shop documentation remain in phases 5 and 6.
