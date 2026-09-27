# Phase 3 — Windows VM test

[Download PrintShop-Tools-Setup.exe](https://github.com/Xpond/printX/releases/latest/download/PrintShop-Tools-Setup.exe) in Windows and run it; it updates the installed copy. Open **PrintShop Tools**. The samples are under **Start → PrintShop Tools → Sample files**. Also use a few big PDFs of your own: a scan, a print-ready flyer, anything you would email.

## Compress PDF

1. First make a big PDF: in **Make PDF**, combine three or four phone photos. Then open **Compress PDF** from the home screen and drop that PDF, your own PDFs, and `04 three pages.pdf`, `05 password-printshop.pdf` and `06 broken.pdf` from the samples. Each tile shows the file size.
2. Leave **Recommended** selected and press **Compress 6 PDFs** (or however many). Enter `printshop` when asked. Results are saved next to the originals as `name_compressed.pdf`. Each tile shows the old and new size and a green **% smaller** badge. The small samples show **Already optimized** and get no new file, and the broken one gets a clear message. The line under the options adds up the savings.
3. Open a few results: every page is there and nothing is rotated. Text, links and bookmarks still work, and photos look normal on screen.
4. Choose **Smallest (email)** and compress a scanned document again. The file is smaller than with Recommended, and the text is still easy to read at 100% zoom.
5. Choose **Print quality** and compress a print-ready CMYK flyer. The colours stay CMYK: check in Acrobat's Output Preview if you have it, or print it. Images stay sharp at about 300 DPI.
6. Run the same job again: the new files end in `(2)`, and the first ones stay unchanged.
7. Compress your biggest PDF. While it runs, move the window and press **Cancel**: it stops within a second and leaves no partial file. The next job works.
8. Restart the app: the Compression choice is remembered.
9. Make PDF and Upscale image still work.

Fillable form fields are flattened: their values stay visible but can no longer be edited. The compressed copy does not keep the password.

## Split PDF

1. Open **Split PDF** and drop `04 three pages.pdf` and `05 password-printshop.pdf`. Each tile shows its page count.
2. Leave **Every page** selected and press **Split 2 PDFs**. Enter `printshop` when asked. Each PDF gets a new folder next to it, such as `04 three pages_split`, holding one PDF per page, from `04 three pages_page_1.pdf` to `_page_3.pdf`. The status reads **Split 2 PDFs into 6 PDFs**, and **Open folder** opens the first folder.
3. Choose **Page ranges** and clear the box: the Split button greys out and a hint shows the format. Type `1-2, 3` and split again: the new folders end in `(2)` and hold `_pages_1-2.pdf` and `_page_3.pdf`. Type `2-5` and split: both samples are skipped with a message that they do not have those pages.
4. Split one of your own long PDFs with **Every N pages** set to 10. The numbers have leading zeros, as in `_pages_01-10.pdf`, so the files sort in page order in every app.
5. Start splitting a long PDF with **Every page** and press **Cancel**: no folder is left behind.
6. Restart the app: the Split choice and your page ranges are remembered.

If something fails, send the visible message and `%LOCALAPPDATA%\PrintShop Tools\logs\app.log` and `worker.log`.
