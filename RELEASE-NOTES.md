**New in 0.2.0: Upscale image.** Make photos bigger for printing, fully offline and without AI. Choose a print size (A6–A0, photo sizes, Letter, Legal, Tabloid or your own) at 300 or 150 DPI, or a fixed 2×, 3× or 4×. Each image shows the size it prints sharp at and a green, amber or red badge for how the enlargement will look. Hard edges keeps QR codes and pixel art crisp. Results keep transparency, CMYK and colour profiles, and never overwrite existing files.

Phase 1: Make PDF from images and existing PDFs, with ordering, paper sizes, password prompts, background processing, and cancellation.

Download **PrintShop-Tools-Setup.exe**, run it, then open **PrintShop Tools** from the Start menu. Windows 10/11 x64; no Python installation or ZIP extraction needed. Installation is for your Windows account and includes an uninstaller.

Find the test files under **Start → PrintShop Tools → Sample files**. Follow [the phase 2 checklist](https://github.com/Xpond/printX/blob/main/PHASE2-TESTING.md). The other tool tiles are scheduled for later phases.

Windows CI runs the tests, launches the packaged app, installs this setup file, checks the installed app, and uninstalls it before publishing. SHA256SUMS.txt contains the download checksum.
