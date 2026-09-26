**New in 0.1.1:** the Make PDF file list keeps at least three rows visible on laptop screens, and the drop area shrinks once files are added. Remove several files at once with **Select all** and **Remove selected**, or select files and press Delete.

Phase 1: Make PDF from images and existing PDFs, with ordering, paper sizes, password prompts, background processing, and cancellation.

Download **PrintShop-Tools-Setup.exe**, run it, then open **PrintShop Tools** from the Start menu. Windows 10/11 x64; no Python installation or ZIP extraction needed. Installation is for your Windows account and includes an uninstaller.

Find the test files under **Start → PrintShop Tools → Sample files**. Follow [the phase 1 checklist](https://github.com/Xpond/printX/blob/main/PHASE1-TESTING.md). Upscaling and the other tool tiles are scheduled for later phases.

Windows CI runs the tests, launches the packaged app, installs this setup file, checks the installed app, and uninstalls it before publishing. SHA256SUMS.txt contains the download checksum.
