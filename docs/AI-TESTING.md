# AI tools — Windows VM test

[Download PrintShop-Tools-Setup.exe](https://github.com/Xpond/printX/releases/latest/download/PrintShop-Tools-Setup.exe) in Windows and run it; it updates the installed copy. Open **PrintShop Tools**. The AI tools need internet and an OpenRouter API key. Use a few photos of your own: a person or pet, a product on a table, a group photo, a photo with a watermark, date stamp or text on it, and a small photo about 500 px wide (saved from a website or a chat app) for Enhance.

## Home and Settings

1. The first row of the home screen holds **Remove background** and **Enhance image**, each with a yellow stripe, a sparkle icon and a yellow **AI** tag. **Logo to vector** is gone. The line at the bottom says images you send to an AI tool leave this computer.
2. Open **Remove background** before adding a key: the main button stays grey and the line under it says to add an OpenRouter API key in Settings.
3. Open **Settings**, paste your key into **OpenRouter API key** and press **Save settings**. The box empties and the note says a key is saved. Restart the app and open Settings: the box is still empty, and there is no way to show or copy the key. In `regedit`, `HKEY_CURRENT_USER\Software\PrintShop Tools\PrintShop Tools\ai` holds the key only as scrambled text.
4. The model boxes show `inclusionai/ming-image-0.1-design-layer` and `meta/muse-image`.

## Remove background

1. Drop your photos, leave **Remove: Background**, and press **Remove background from N images**. Each photo takes about 20 seconds while the bar keeps moving. Results are saved next to the originals as `name_no_background.png`, the same pixel size as the originals (**Properties → Details**). Put one on a coloured slide in PowerPoint or Word: only the subject shows, with clean edges.
2. For the group photo, type who to keep in **Keep**, such as `the woman on the left`, and run it again. The new file ends in `(2)` and keeps only that person.
3. Choose **Something else**: the button greys out until you describe it. Type `the watermark` (or `the date stamp`, `the text`) for the photo that has one and run it. `name_edited.jpg` has it removed; the rest of the photo is unchanged and as sharp as before.
4. Start a job and press **Cancel**: it stops at once and leaves no file.

## Enhance image

1. Open **Enhance image** and drop the small photo, or click the empty area to choose it. It appears in the conversation with its pixel size.
2. Type `Make it sharp and clear for printing` and press **Enter** (or **Send**). About 20 seconds later the new version appears underneath, around 1500 px or more on its long side and with the same shape as the original. It is saved next to the original as `name_enhanced.jpg`; **Open file** and **Show in folder** open it.
3. Send a follow-up, such as `Make the colours a little warmer`. It changes the newest version and saves `name_enhanced (2).jpg`.
4. Click the original picture in the conversation (it gets the yellow frame) and send another instruction: this one starts again from the original.
5. **New photo** clears the conversation. Choosing a PDF says to choose an image.

## Problems

1. In Settings, change the Remove background model to `inclusionai/no-such-model` and save. Running Remove background now says OpenRouter has no model with this name. Clear the box and save to go back to the default.
2. Disconnect the VM's network and run a job: it says it could not reach OpenRouter.

Remove background is free; each Enhance reply costs about $0.01 of OpenRouter credit. If something fails, send the visible message and `%LOCALAPPDATA%\PrintShop Tools\logs\app.log` and `worker.log`.
