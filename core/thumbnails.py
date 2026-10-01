from io import BytesIO
from pathlib import Path

SIZE = 256  # Sharp in 128 px tiles up to 200% display scaling.


def thumbnail(path, side=SIZE):
    """Run inside the thumbnail process, never in a Qt thread."""
    try:
        if Path(path).suffix.lower() == '.pdf':
            import pymupdf
            with pymupdf.open(path) as doc:
                if doc.needs_pass:
                    return b'', 'locked', 0
                page = doc[0]
                scale = side / max(page.rect.width, page.rect.height)
                pixmap = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False)
                return pixmap.tobytes('png'), 'pages', doc.page_count
        from PIL import ImageOps
        from core.images import pillow_open
        with pillow_open(path) as image:
            size = image.size
            if image.getexif().get(0x0112) in (5, 6, 7, 8):  # Report the upright size of rotated photos.
                size = size[::-1]
            image.draft('RGB', (side, side))
            image.thumbnail((side, side))
            image = ImageOps.exif_transpose(image).convert('RGBA')
            data = BytesIO()
            image.save(data, 'PNG')
            return data.getvalue(), 'pixels', size
    except Exception:
        return b'', 'unreadable', 0
