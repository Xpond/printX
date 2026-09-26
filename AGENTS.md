# PrintShop Tools handoff

- Spec: `PLAN.md`. Keep changes simple, files around 200 lines or less, and UI copy in `ui/text.py`. Use `rb` before rediscovering code.
- Develop on Linux; target Windows 10/11 x64. The Windows 11 VM has 2 GB RAM. Never require copying ZIPs or using a shared VM folder: deliver an installer `.exe` through GitHub Releases. The owner will make the repository public.
- Phase 1 complete: PySide6 home/tool screens, settings, logs, background jobs with cancellation, lazy thumbnails, and Make PDF for images/PDFs. Supports ordering, lossless JPEG embedding, multi-page TIFF, passwords, corrupt-file skipping, and safe output names.
- Post-phase-1 fix: the drop zone compacts once files are listed, the file list keeps at least 3 rows, and Select all, Remove selected, and Delete work on the list.
- Verified: 13 tests pass on Linux and Windows; native Windows source and packaged app smoke tests pass. Reviewed light/dark screenshots. Last measured packaged first frame: 1.41 seconds. Samples and manual checks are in `samples/` and `PHASE1-TESTING.md`.
- Packaging started early: pinned Python 3.14 dependencies, PyInstaller one-folder build, Windows CI. Installer/release delivery is being added before phase 2; keep the app one-folder inside the installer. Never force `QT_QPA_PLATFORMTHEME=generic` on native Windows.
- After each phase: test, launch, review `QWidget.grab()` screenshots, give exact manual checks, commit, and wait for the owner's OK. Phase 2 has not started.

## Next phases

2. Upscale images: print sizes/DPI, quality badges, sharpening, hard edges, preserve color/transparency.
3. Compress/split PDFs, organize pages, export pages as images.
4. Office conversion, logo tracing, previews, home drop routing, Send To integration.
5. Finish packaging and installed-app validation; bundle external tools where appropriate.
6. Shop installation guide and one-page how-to.

Do not build page numbers, watermarks, unlocking, booklets, or N-up yet.
