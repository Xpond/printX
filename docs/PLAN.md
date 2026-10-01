# PrintShop Tools — build plan

## Testing environment
- Development happens on Linux, not Windows.
- The user has a Windows VM for testing.
- Provide Windows executables from the start so the user can download them into the VM and test each phase.
- Confirmed target: Windows 11 Pro, x64, 2 GB RAM.
- Remote: git@github.com:Xpond/printX.git. Windows CI produces a portable one-folder ZIP from phase 1; the installer remains in phase 5.

## Goal
A Windows desktop app for a small print shop, written in Python. It does three jobs:
1. Upscale images for printing (classic resampling, no AI, fully offline).
2. Everyday PDF tasks like ilovepdf.com.
3. AI image edits through OpenRouter: remove backgrounds or objects, and enhance photos (online, see tool 7).
The staff using it are not technical. Every task should be: pick a tool, drop files, press one big button. Speed matters, and the UI must never freeze.

## How to work
- First save this spec as PLAN.md in the project root and refer back to it.
- Before writing code, reply with your implementation plan and any questions.
- Build in the phases listed at the end. After each phase: run the tests, launch the app, tell me exactly what to try, commit to git, and wait for my OK.
- Check library APIs against the installed versions instead of assuming.
- Test with the real files in samples/ if present; otherwise generate your own (photos, a small logo, multi-page PDFs, a Word file).

## Stack
- Python 3.12+ (newest version all dependencies have Windows wheels for), a venv, pinned requirements.txt
- UI: PySide6
- Images: Pillow + pillow-heif (iPhone HEIC photos)
- PDF engine: PyMuPDF (fast, C-based) for merge, split, rotate, reorder, render and SVG → PDF
- Images → PDF: img2pdf (lossless; embeds JPEGs without re-encoding)
- Compression: Ghostscript (bundle the Windows binaries if feasible, otherwise detect an installed copy); fallback: PyMuPDF image downsampling + cleanup
- Office → PDF: Microsoft Office via COM (pywin32); fallback: LibreOffice headless
- AI tools: OpenRouter's image API over HTTPS with the standard library (no SDK)
- Packaging: PyInstaller one-folder build + Inno Setup installer

## UX rules (most important section)
- Home screen: one tile per tool with an icon, a short name and a one-line description.
- Dropping files anywhere on the home screen opens a small popup offering only the tools that fit those files. Files passed on the command line do the same, so dragging files onto the app's icon works.
- Every tool screen uses the same layout: big drop zone (or click to browse) → file list with thumbnails (drag to reorder where order matters, remove button) → a few options with smart defaults → one big button.
- Defaults should be right most of the time; anything advanced goes under "More options".
- Output saves automatically next to the original with a clear suffix (photo_upscaled.jpg, flyer_compressed.pdf). Never overwrite: add (2), (3). Settings can switch to one fixed output folder.
- When a job finishes: clear success message with Open file, Show in folder, and Do another.
- Remember the last-used options per tool.
- Copy: sentence case and plain verbs. Buttons say exactly what happens ("Upscale 6 images") and the result uses the same verb ("Upscaled 6 images"). Errors say what happened and how to fix it ("This PDF is password protected. Enter the password to continue."), never tracebacks; details go to the log. Empty drop zones invite action ("Drop photos here or click to choose").
- Default units (cm/inches) and paper size (A4/Letter) follow the Windows region; changeable in Settings.
- Keyboard: Ctrl+O adds files, Enter runs, Esc goes back.
- All UI text in one file so it's easy to reword or translate.

## Look and feel
- Grounded in the print shop: paper-white background, ink-black text, and process-ink accents that carry meaning, cyan for image tools and magenta for PDF tools. Spend the boldness in one place: crop marks at the corners of the drop zone. Keep the rest quiet; avoid the generic look of identical rounded cards with soft shadows, gradients and all-caps labels.
- A highly legible bundled font (e.g. Atkinson Hyperlegible, open license) at generous sizes; big click targets.
- Proper dark mode following Windows, crisp on high-DPI screens.
- Save screenshots of each screen with QWidget.grab() and review them yourself before showing me.

## Tools

### 1. Upscale Image
- Input: JPG, PNG, TIFF, BMP, WEBP, HEIC. Batches.
- Size (big segmented buttons): Fit print size (default) | 2× | 3× | 4×. Fit print size has a paper dropdown (A6–A0, 10×15 cm / 4×6", 13×18 cm / 5×7", 20×25 cm / 8×10", Letter, Legal, Tabloid, Custom) and DPI (300 default, 150 for large posters), and matches the image's orientation.
- Each file row shows its pixel size and "Prints sharp up to W × H at 300 DPI" with a green/amber/red badge. In Fit print size mode it shows the scale factor, says "Already big enough" and skips files that need no upscale, and warns above 4× that the result will look soft.
- Method: Lanczos resampling, then an unsharp mask (Sharpening: Off / Light (default) / Strong). Tune the defaults on real photos by making before/after crops at 100% and inspecting them: natural, no halos.
- "Hard edges" toggle for QR codes, barcodes and pixel art: nearest neighbor at a whole-number scale.
- Correctness: apply EXIF rotation first; convert palette ("P") and 1-bit images before resizing, because Pillow silently uses nearest neighbor for those modes; keep transparency; keep CMYK as CMYK; keep the ICC color profile; write the target DPI into the file.
- Output format matches the input by default. JPEG at quality 95 with 4:4:4 chroma (no color bleeding in print); TIFF with LZW.
- Clicking a file opens a before/after preview at 100% zoom.

### 2. Make PDF (covers merge PDFs, JPG to PDF and Word to PDF)
- Accepts any mix of images (including multi-page TIFF), PDFs, and Word/Excel/PowerPoint files.
- Reorderable list with thumbnails and a Sort by name button.
- Options: One combined PDF (default) or One PDF per file. Images go on Paper (A4/Letter by region, default) or Same as image, auto orientation, margins None / Small (default) / Large. PDF pages keep their original size.
- Images are embedded losslessly with img2pdf; if it rejects an image (transparency, unusual mode), flatten it onto white with Pillow and retry.
- Office files: use a separate hidden Office instance (DispatchEx) so documents the user has open aren't touched, always quit it, and convert one file at a time on a dedicated thread with COM initialized. The LibreOffice fallback uses a temporary user profile so it works even while LibreOffice is open. If neither is installed, say what to install instead of failing.

### 3. Compress PDF
- Presets: Smallest (email), Recommended (default), Print quality (keeps images around 300 DPI and never converts CMYK to RGB).
- Shows before → after size and % saved. If the result isn't smaller, keep the original and say it's already optimized. Batches.

### 4. Split PDF
- Modes: every page as its own PDF | page ranges ("1-3, 5, 8-10") | every N pages. Shows the page count. Output goes in a folder named after the file.

### 5. Organize Pages
- Page thumbnail grid: rotate one page or all, delete, drag to reorder, then save. Rotation is lossless (page rotation flag, no re-rendering).

### 6. PDF → Images
- JPG or PNG; 150 / 300 (default) / 600 DPI; all pages or a range. Output goes in a folder named after the file.

### 7. AI tools (owner request; replaces Logo → Vector)
- First row of the home screen, marked as AI by a process-yellow accent, sparkle icons and an "AI" tag. They need internet and an OpenRouter API key; images are sent to OpenRouter, so the home screen says so.
- Settings: the API key can only be pasted in, never shown (stored encrypted for the Windows user with DPAPI), plus one editable model name per AI tool so models can change without a new release.
- Remove background (model `inclusionai/ming-image-0.1-design-layer`): Background (optional description of what to keep) saves a transparent PNG; Something else (described, e.g. a watermark) saves an edited copy in the original's format.
- Enhance image (model `meta/muse-image`): a chat about one photo. Each instruction makes a new version from the highlighted one (the latest, or any earlier one clicked) and saves it next to the original as `name_enhanced` in the original's format.

## Performance
- The window appears in under 2 seconds: import heavy libraries (PyMuPDF, pywin32, pillow-heif) only when a tool first needs them.
- All work runs off the UI thread with per-file progress, an overall progress bar and a Cancel button. Acceptance test: during the biggest job the window can still be moved and Cancel responds immediately. Cancel removes partial outputs.
- PyMuPDF doesn't support threading, and any C extension that holds the GIL will stall the UI from a thread, so run that work in worker processes. Keep a warm pool started on first use, and call multiprocessing.freeze_support() (required for PyInstaller on Windows).
- Pillow releases the GIL while resizing; benchmark threads vs processes for batch upscaling and use the faster one.
- Bound batch parallelism by CPU cores and by memory: estimate each job's RAM from its output size and run huge jobs one at a time.
- Thumbnails load lazily in the background and are cached. Use Pillow's fast JPEG draft/thumbnail path, and Qt model/view so a 500-page PDF or 200 images open instantly.
- Raise Pillow's MAX_IMAGE_PIXELS (these are trusted local files), but warn before creating outputs over ~300 megapixels.
- Write each output to a temp file and rename it when finished, so a crash or cancel never leaves a half-written file.

## Code structure
- core/: pure processing functions with no Qt imports (upscale, pdf_tools, office, remove). Each takes paths, options, a progress callback and a cancel flag, and returns output paths.
- ui/: home screen, shared tool-screen layout, one screen per tool, settings.
- app.py as the entry point; tests/ with pytest covering core/.

## Windows robustness
- Paths with spaces, accents, emoji and long paths must work everywhere; if an external tool (Ghostscript, LibreOffice) chokes on a path, work through a temp copy.
- Handle files locked by another program, password-protected PDFs (ask for the password), and corrupt files (skip with a clear message and continue the batch).
- Generated .ico app icon, settings via QSettings, rotating logs in %LOCALAPPDATA%\PrintShop Tools\logs.

## Phases
1. Skeleton: home screen, shared tool layout, background jobs with progress and cancel, settings, logging. Then Make PDF for images and PDFs.
2. Upscale Image, including Fit print size and the sharpness badges.
3. Compress, Split, Organize Pages, PDF → Images.
4. Office files in Make PDF, the before/after preview, the drop-anywhere popup, and an "Add to Send To menu" button in Settings (right-click files → Send to → PrintShop Tools).
5. Packaging: PyInstaller one-folder build (faster startup and fewer antivirus false alarms than one-file; no UPX), windowed, with icon, bundled Ghostscript if used, unused Qt modules excluded. Inno Setup installer with Start menu and desktop shortcuts. A build.bat that does everything in one double-click. Test the built app outside the dev environment.
6. README for the shop: how to install, the first-run "Windows protected your PC" → More info → Run anyway step, and a one-page how-to.

## Later (don't build yet)
Page numbers, watermark, unlock PDF, booklet and N-up print layouts.
