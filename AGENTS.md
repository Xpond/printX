# PrintShop Tools handoff

- Spec: `PLAN.md`. Keep changes simple, files around 200 lines or less, and UI copy in `ui/text.py`. Use `rb` before rediscovering code.
- Develop on Linux; target Windows 10/11 x64. The Windows 11 VM has 2 GB RAM. Never require copying ZIPs or using a shared VM folder: deliver an installer `.exe` through GitHub Releases. The owner will make the repository public.
- Phase 1 complete: PySide6 home/tool screens, settings, logs, background jobs with cancellation, lazy thumbnails, and Make PDF for images/PDFs. Supports ordering, lossless JPEG embedding, multi-page TIFF, passwords, corrupt-file skipping, and safe output names.
- Post-phase-1 UI, from owner feedback (overrides PLAN.md's big drop zone and big buttons): compact, uncluttered layouts with no filler space. Tool titles sit in the window header. Make PDF has no drop zone: its grid of 128 px thumbnails (two-line names, drag to reorder) takes drops and opens the file picker when clicked empty. Options are two aligned rows with an editable File name for the combined PDF.
- Phase 2 built, awaiting the owner's OK: Upscale image. Fit print size (A6–A0, photo sizes, Letter/Legal/Tabloid, custom) at 300/150 DPI, or 2×/3×/4×. Tiles show pixel size, the print size the original is sharp at, and a badge: up to 2× green, up to 4× amber, beyond red. Lanczos in 256-row strips (one full-size buffer) plus an unsharp mask with a small radius (min(0.6 + 0.1 × scale, 1.2)); Light 70% and Strong 140% were tuned on real crops for no halos. Premultiplied alpha, Hard edges = nearest neighbour at a whole-number scale, CMYK/ICC/transparency kept, DPI written, JPEG q95 4:4:4, TIFF LZW, HEIC/WEBP saved as JPG (PNG when transparent). Benchmark: threads matched processes, so files run in worker threads within a 512 MB budget.
- Shared job flow lives in `ui/tool_screen.py`; each tool passes its copy dict (`T.MAKE`, `T.UPSCALE`) and options. Known: at the 680 px minimum width tool pages scroll sideways (Make PDF's rows already need about 740 px).
- Verified: 28 tests pass on Linux; the source smoke test runs Make PDF and Upscale. Reviewed light/dark screenshots. Last measured packaged first frame: 1.41 seconds. Samples and manual checks are in `samples/`, `PHASE1-TESTING.md` and `PHASE2-TESTING.md`.
- Packaging started early: pinned Python 3.14 dependencies, PyInstaller one-folder build, Windows CI. Installer/release delivery is being added before phase 2; keep the app one-folder inside the installer. Never force `QT_QPA_PLATFORMTHEME=generic` on native Windows.
- After each phase: test, launch, review `QWidget.grab()` screenshots, give exact manual checks, commit, and wait for the owner's OK.

## Next phases

3. Compress/split PDFs, organize pages, export pages as images.
4. Office conversion, logo tracing, previews, home drop routing, Send To integration.
5. Finish packaging and installed-app validation; bundle external tools where appropriate.
6. Shop installation guide and one-page how-to.

Do not build page numbers, watermarks, unlocking, booklets, or N-up yet.
