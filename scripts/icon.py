from pathlib import Path
from PIL import Image, ImageDraw

image = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)
draw.rectangle((46, 30, 210, 226), fill='#f7f6f1', outline='#202226', width=8)
draw.rectangle((74, 68, 156, 148), fill='#009bb4')
draw.rectangle((112, 102, 184, 178), fill='#b51b60')
for x, dx in [(20, 1), (236, -1)]:
    for y, dy in [(16, 1), (240, -1)]:
        draw.line([(x, y + dy * 20), (x, y), (x + dx * 20, y)], fill='#202226', width=6)
path = Path(__file__).resolve().parent.parent / 'assets/icon.ico'
image.save(path, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
