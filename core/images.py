from io import BytesIO


def pillow_open(path):
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = 500_000_000
    if str(path).lower().endswith(('.heic', '.heif')):
        from pillow_heif import register_heif_opener
        register_heif_opener()
    return Image.open(path)


def flat_photo(path):
    """The picture as it looks (upright, RGB, transparency on white), and its DPI and RGB colour profile."""
    from PIL import Image, ImageOps
    with pillow_open(path) as source:
        keep = {key: source.info[key] for key in ('dpi', 'icc_profile') if source.info.get(key)}
        if source.mode not in ('RGB', 'RGBA'):
            keep.pop('icc_profile', None)  # A CMYK or grey profile does not describe RGB pixels.
        image = ImageOps.exif_transpose(source).convert('RGBA')
    photo = Image.new('RGB', image.size, 'white')
    photo.paste(image, mask=image.getchannel('A'))
    return photo, keep


def image_pdf(path, options, cancel):
    import img2pdf
    from PIL import Image, ImageOps
    from core.files import check_cancel

    layout = None
    if options.get('paper', 'A4') != 'image':
        sizes = {'A4': (595.2756, 841.8898), 'Letter': (612, 792)}
        margin = {'none': 0, 'small': 14.1732, 'large': 28.3465}[options.get('margin', 'small')]
        layout = img2pdf.get_layout_fun(pagesize=sizes[options.get('paper', 'A4')],
                                       border=(margin, margin), auto_orient=True)
    kwargs = {'rotation': img2pdf.Rotation.ifvalid}
    if layout:
        kwargs['layout_fun'] = layout
    check_cancel(cancel)
    try:
        with open(path, 'rb') as source:
            return img2pdf.convert(source, **kwargs)
    except (img2pdf.ImageOpenError, img2pdf.AlphaChannelError, img2pdf.UnsupportedColorspaceError,
            img2pdf.JpegColorspaceError, ValueError):
        # TIFF frames and HEIC are decoded only if direct, lossless embedding fails.
        frames = []
        with pillow_open(path) as source:
            for index in range(getattr(source, 'n_frames', 1)):
                check_cancel(cancel)
                source.seek(index)
                frame = ImageOps.exif_transpose(source)
                if frame.mode == 'CMYK':
                    encoded = BytesIO()
                    frame.save(encoded, 'TIFF', compression='tiff_lzw', dpi=source.info.get('dpi', (300, 300)))
                else:
                    rgba = frame.convert('RGBA')
                    white = Image.new('RGB', rgba.size, 'white')
                    white.paste(rgba, mask=rgba.getchannel('A'))
                    encoded = BytesIO()
                    white.save(encoded, 'PNG', dpi=source.info.get('dpi', (300, 300)))
                frames.append(encoded.getvalue())
        return img2pdf.convert(*frames, **kwargs)
