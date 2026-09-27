"""Compress PDFs with Ghostscript, run inside the worker so cancelling the worker also stops it."""
import ctypes
import ctypes.util
import logging
import re
import sys
from pathlib import Path

from core.files import JobError, check_cancel, each_file, output_directory, publish, staging

# Tuned on phone photos, scans and a CMYK flyer: 72 DPI blurs scanned text, 100 DPI keeps 6 pt legible.
# Colours stay as they are, so CMYK and spot colours survive and grey scans stay grey (and 18× faster).
SETTINGS = ['-dNOPAUSE', '-dBATCH', '-dSAFER', '-sDEVICE=pdfwrite', '-dAutoRotatePages=/None',
            '-sColorConversionStrategy=LeaveColorUnchanged']
LEVELS = {'smallest': ['-dPDFSETTINGS=/ebook', '-dColorImageResolution=100', '-dGrayImageResolution=100'],
          'recommended': ['-dPDFSETTINGS=/ebook'],
          'print': ['-dPDFSETTINGS=/printer']}  # 300 DPI, high-quality JPEG without colour subsampling.
TEXT = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(ctypes.c_char), ctypes.c_int)


def library():
    """The bundled DLL on Windows, where it reuses the C++ runtime PyMuPDF loaded; elsewhere the system's."""
    if sys.platform != 'win32':
        return ctypes.CDLL(ctypes.util.find_library('gs'))
    folder = getattr(sys, '_MEIPASS', None) or Path(__file__).resolve().parent.parent / 'vendor/ghostscript'
    return ctypes.CDLL(str(Path(folder) / 'gsdll64.dll'))


def ghostscript(args, line):
    """Run Ghostscript with UTF-8 arguments, passing each line it prints to line(). True on success."""
    gs, instance, pending = library(), ctypes.c_void_p(), ['']

    def write(_, data, length):
        *lines, pending[0] = (pending[0] + ctypes.string_at(data, length).decode('utf-8', 'replace')).split('\n')
        for text in lines:
            line(text)
        return length

    stdio = TEXT(lambda *_: 0), TEXT(write), TEXT(write)  # Nothing to read; output and errors go to line().
    if gs.gsapi_new_instance(ctypes.byref(instance), None) < 0:
        return False
    try:
        gs.gsapi_set_arg_encoding(instance, 1)  # UTF-8, for paths with accents and emoji.
        gs.gsapi_set_stdio(instance, *stdio)
        argv = (ctypes.c_char_p * (len(args) + 1))(b'gs', *(arg.encode() for arg in args))
        code = gs.gsapi_init_with_args(instance, len(argv), argv)
        return gs.gsapi_exit(instance) == 0 and code in (0, -101)  # -101: finished and quit.
    finally:
        gs.gsapi_delete_instance(instance)


def compress(paths, options, progress, cancel):
    """Compress PDFs one at a time next to their originals; keep the original when nothing is gained."""
    import pymupdf
    from core.pdf_tools import open_pdf

    def one(index, path):
        if path.suffix.lower() != '.pdf':
            raise JobError('not_pdf')
        document, password = open_pdf(path, progress, cancel)
        with document:
            pages = document.page_count
        temp, messages = staging(path, options) / f'{index}.pdf', []

        def line(text):
            page = re.fullmatch(r'Page (\d+)', text)
            if page:
                progress('progress', {'index': index + (int(page[1]) - 1) / pages, 'total': len(paths),
                                      'path': str(path)})
            elif text.strip():
                messages.append(text)

        args = [*SETTINGS, *LEVELS[options['level']], f'-sOutputFile={temp}']
        if password:
            args.append(f'-sPDFPassword={password}')
        finished = ghostscript(args + [str(path)], line)
        if finished:
            with pymupdf.open(temp) as result:
                finished = result.page_count == pages  # Ghostscript can succeed with pages missing.
        if not finished:
            logging.warning('Ghostscript could not compress %s:\n%s', path, '\n'.join(messages))
            raise JobError('corrupt')
        before, after = path.stat().st_size, temp.stat().st_size
        if after >= before:
            raise JobError('optimized')
        check_cancel(cancel)
        output = publish(temp, output_directory(path, options) / f'{path.stem}_compressed.pdf')
        progress('output', {'path': output, 'source': str(path), 'before': before, 'after': after})
        return output

    return each_file(paths, options, progress, cancel, one)
