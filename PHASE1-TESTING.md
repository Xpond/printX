# Phase 1 — Windows VM test

[Download PrintShop-Tools-Setup.exe](https://github.com/Xpond/printX/releases/latest/download/PrintShop-Tools-Setup.exe) directly in Windows and run it. Open **PrintShop Tools** from the Start menu. No Python installation is needed. Open **Start → PrintShop Tools → Sample files** for the included examples.

Only **Make PDF** is active in this phase. The other tools arrive in the phases listed in PLAN.md.

1. Open Make PDF. Drop `01 landscape.jpg`, `02 transparent logo.png`, `03 two-page.tiff`, and `04 three pages.pdf` from the included samples folder.
2. Drag the PDF to the top. Choose A4 and one combined PDF, then press **Make PDF from 4 files**. Expect seven pages: three original PDF pages, the landscape, the logo, then two TIFF pages. Original PDF page sizes stay unchanged.
3. Use **Open file** and **Show in folder**. Run the same job again: the second output should end in `(2)` and the first should remain unchanged.
4. Choose **One PDF per file**. Try **Same as image**, then Letter with Large margins.
5. Add `05 password-printshop.pdf`; enter a wrong password once, then `printshop`. Try cancelling the password prompt to skip that file.
6. Mix `06 broken.pdf` with a valid photo. The photo should still convert, with a clear message about the broken file. The Word sample is intentionally unsupported until phase 4.
7. In Settings, choose one output folder. Return to Make PDF and verify the next result saves there. Restart the app: the folder and tool options should persist. Try Windows light and dark modes.
8. Add a large PDF or many photos. While processing, move the window and press Cancel. The window should stay responsive, unfinished files should disappear, and the next job should work. Already completed PDFs are kept.
9. Add eight or more files. They should appear as a grid of large thumbnails with readable names. With no files, clicking the empty grid should open the file picker. Drag a thumbnail between two others and check the new order. Press **Select all** then **Remove selected** to clear the list. Also click one file, press Delete, and check that only that file is removed.
10. With **One combined PDF**, the **File name** box shows the default name. Type a new name, press **Make PDF**, and check the saved PDF uses it. Switch to **One PDF per file**: the box hides and each PDF is named after its original.
11. Try Ctrl+O to add files, Enter to run, and Esc to return home. Try a filename containing spaces, accents, or emoji.

The VM has 2 GB RAM, so this version processes one PDF job at a time. First use starts background workers; subsequent jobs reuse them.

If something fails, send the visible message and `%LOCALAPPDATA%\PrintShop Tools\logs\app.log` and `worker.log`. Include whether it happened before or after pressing Make PDF.

Home drop routing, Office conversion, and before/after previews are scheduled for phase 4. Installer delivery was brought forward so each phase can be downloaded directly on Windows.
