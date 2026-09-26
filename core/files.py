import os
import re
from pathlib import Path

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp', '.webp', '.heic', '.heif'}
INPUT_EXTENSIONS = IMAGE_EXTENSIONS | {'.pdf'}


class Cancelled(Exception):
    pass


class JobError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def check_cancel(cancel):
    if cancel.is_set():
        raise Cancelled()


def output_directory(path, options):
    return Path(options.get('output_folder') or Path(path).parent)


def pdf_name(paths, typed=''):
    """Name for the combined PDF: the typed name made safe for Windows, else the default."""
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', typed).strip().rstrip('. ')
    if name.lower().endswith('.pdf'):
        name = name[:-4].rstrip('. ')
    return name or f"{Path(paths[0]).stem}_{'combined' if len(paths) > 1 else 'made'}"


def stage_directory(directory, token):
    return Path(directory) / f'.printshop-{token}'


def publish(temp, destination):
    """Publish a complete file atomically without replacing an existing name."""
    destination = Path(destination)
    for number in range(1, 100000):
        target = destination if number == 1 else destination.with_stem(f'{destination.stem} ({number})')
        try:
            if os.name == 'nt':
                os.rename(temp, target)  # Windows rename refuses existing destinations.
            else:
                os.link(temp, target)
                Path(temp).unlink()
            return str(target)
        except FileExistsError:
            continue
    raise JobError('names_exhausted')


def error_code(error):
    if isinstance(error, JobError):
        return error.code
    if isinstance(error, PermissionError):
        return 'permission'
    if isinstance(error, FileNotFoundError):
        return 'missing'
    if isinstance(error, OSError) and error.errno == 28:
        return 'disk_full'
    return 'corrupt'
