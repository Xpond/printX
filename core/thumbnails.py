from io import BytesIO
from pathlib import Path


def thumbnail(path):
    """Run inside the thumbnail process, never in a Qt thread."""
    try:
        if Path(path).suffix.lower() == '.pdf':
            import pymupdf
            with pymupdf.open(path) as doc:
                if doc.needs_pass:
                    return b'', 'locked', 0
                page = doc[0]
                scale = 112 / max(page.rect.width, page.rect.height)
                pixmap = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False)
                return pixmap.tobytes('png'), 'pages', doc.page_count
        from PIL import ImageOps
        from core.images import pillow_open
        with pillow_open(path) as image:
            size = image.size
            image.draft('RGB', (112, 112))
            image.thumbnail((112, 112))
            image = ImageOps.exif_transpose(image).convert('RGBA')
            data = BytesIO()
            image.save(data, 'PNG')
            return data.getvalue(), 'pixels', size
    except Exception:
        return b'', 'unreadable', 0
