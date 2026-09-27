**New in 0.3.0: Compress PDF and Split PDF.** Compress makes PDFs smaller for email or keeps them print-ready: Smallest (email), Recommended or Print quality. Each file shows its size before and after, and files that are already optimized are left as they are. Colours are never changed, so CMYK flyers stay CMYK. Split saves every page, the page ranges you type (like 1-3, 5, 8-10), or every few pages as separate PDFs in a new folder next to the original.

Phase 2: Upscale image makes photos bigger for printing, fully offline and without AI, with print sizes and sharpness badges.

Phase 1: Make PDF from images and existing PDFs, with ordering, paper sizes, password prompts, background processing, and cancellation.

Download **PrintShop-Tools-Setup.exe**, run it, then open **PrintShop Tools** from the Start menu. Windows 10/11 x64; no Python installation or ZIP extraction needed. Installation is for your Windows account and includes an uninstaller.

Find the test files under **Start → PrintShop Tools → Sample files**. Follow [the phase 3 checklist](https://github.com/Xpond/printX/blob/main/docs/PHASE3-TESTING.md). The other tool tiles are scheduled for later phases.

Windows CI runs the tests, launches the packaged app, installs this setup file, checks the installed app, and uninstalls it before publishing. SHA256SUMS.txt contains the download checksum.
