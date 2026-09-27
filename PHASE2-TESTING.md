# Phase 2 — Windows VM test

[Download PrintShop-Tools-Setup.exe](https://github.com/Xpond/printX/releases/latest/download/PrintShop-Tools-Setup.exe) in Windows and run it; it updates the installed copy. Open **PrintShop Tools**. The samples are under **Start → PrintShop Tools → Sample files**. Also use two or three of your own phone photos.

1. The home screen shows **Upscale image** as active. Open it and drop `01 landscape.jpg`, `02 transparent logo.png`, `08 qr-style code.png` and your photos. Each tile shows the pixel size, the print size it is sharp at, and a coloured badge.
2. Choose **Fit print size**, **A4**, **300 DPI**. Expect the landscape at **2.2× · slightly soft** (amber), the logo at **8.3× · soft** (red), the QR sample at **16.8× · soft** (red), and a line under the grid about images needing more than 4×. A 12-megapixel phone photo shows **Already big enough** (green).
3. Choose **A6** and **150 DPI**: the landscape becomes **Already big enough**. Choose **Custom size**, type 50 × 70 cm, and watch the badges change. Choose **2×**: the paper box greys out and every badge reads **2× · sharp**.
4. Go back to Fit print size, A4, 300 DPI and press **Upscale 5 images** (or however many). Results are saved next to the originals as `name_upscaled.jpg` or `.png`. Images that are already big enough are skipped with a message. Run it again: the new files end in `(2)` and the first ones stay unchanged.
5. In File Explorer, check a result's **Properties → Details**: the landscape is 3508 × 2192 pixels at 300 dpi. The logo keeps its transparent background.
6. Upscale one of your photos at 3× three times, with Sharpening **Off**, **Light** and **Strong**, then compare them at 100% zoom. Light should look natural, with no bright or dark outlines around edges. Strong is crisper.
7. Remove everything except the QR sample, tick **Hard edges** and choose **4×**. Sharpening greys out and the result has crisp square blocks.
8. If you have HEIC (iPhone) or WEBP images, they are saved as JPG, or PNG when transparent, so every print app can open them.
9. Choose 3× on your largest photo and press Upscale. While it runs, move the window and press **Cancel**: it stops within a second and leaves no partial file. The next job works.
10. Choose **Custom size** 200 × 200 cm at 300 DPI: pressing Upscale asks first because the result would be over 300 megapixels. **Go back** cancels.
11. In Settings, set **Default units** to Inches and save: print sizes show in inches and photo papers read 4 × 6 in. Restart the app: the Upscale options are remembered.
12. Make PDF still works as in phase 1.

The VM has 2 GB RAM. Upscale works on several images at once only while they fit in memory; bigger ones run one at a time. Very large results, such as A0 at 300 DPI, can take a few minutes there.

If something fails, send the visible message and `%LOCALAPPDATA%\PrintShop Tools\logs\app.log` and `worker.log`.
