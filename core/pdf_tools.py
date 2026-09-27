import logging
import re
import shutil
from pathlib import Path

from core.files import (INPUT_EXTENSIONS, Cancelled, JobError, check_cancel, each_file, error_code,
                        output_directory, pdf_name, publish, publish_folder, stage_directory, staging)


def open_pdf(path, progress, cancel):
    """Open a PDF, asking for its password until it opens; returns the document and the password used."""
    import pymupdf
    with open(path, 'rb'):
        pass  # Preserve ordinary filesystem errors before MuPDF wraps them.
    document = pymupdf.open(path)
    password = ''
    try:
        while document.needs_pass:
            check_cancel(cancel)
            password = progress('password', {'path': str(path)})
            if password is None:
                raise JobError('password_skipped')
            if document.authenticate(password):
                break
        if not document.page_count:
            raise JobError('empty_pdf')
        return document, password
    except BaseException:
        document.close()
        raise


def make_pdf(paths, options, progress, cancel):
    """Make PDFs in input order. Progress accepts (event, payload); password returns text/None."""
    import pymupdf
    from core.images import image_pdf

    token = options['token']
    combined = options.get('combined', True)
    outputs, stages = [], set()
    result = pymupdf.open()

    def save(document, source, name):
        directory = output_directory(source, options)
        stage = stage_directory(directory, token)
        stage.mkdir(parents=True, exist_ok=True)
        stages.add(stage)
        temp = stage / 'output.pdf'
        check_cancel(cancel)
        document.save(temp, garbage=3, deflate=True)
        check_cancel(cancel)
        output = publish(temp, directory / f'{name}.pdf')
        outputs.append(output)
        progress('output', {'path': output})

    try:
        for index, value in enumerate(paths):
            check_cancel(cancel)
            path = Path(value)
            progress('progress', {'index': index, 'total': len(paths), 'path': str(path)})
            try:
                if path.suffix.lower() not in INPUT_EXTENSIONS:
                    raise JobError('unsupported')
                if path.suffix.lower() == '.pdf':
                    source, _ = open_pdf(path, progress, cancel)
                else:
                    source = pymupdf.open(stream=image_pdf(path, options, cancel), filetype='pdf')
                with source:
                    check_cancel(cancel)
                    if combined:
                        result.insert_pdf(source)
                    else:
                        with pymupdf.open() as single:
                            single.insert_pdf(source)
                            save(single, path, f'{path.stem}_made')
            except Cancelled:
                raise
            except Exception as error:
                logging.exception('Could not process %s', path)
                progress('skipped', {'path': str(path), 'code': error_code(error)})
            progress('progress', {'index': index + 1, 'total': len(paths), 'path': str(path)})
        if combined and result.page_count:
            save(result, paths[0], pdf_name(paths, options.get('name', '')))
        if not outputs:
            raise JobError('no_outputs')
        return outputs
    finally:
        result.close()
        for stage in stages:
            shutil.rmtree(stage, ignore_errors=True)


def page_ranges(text):
    """'1-3, 5, 8-10' as [(1, 3), (5, 5), (8, 10)], or None when the text is not a list of page ranges."""
    ranges = []
    for item in filter(str.strip, text.split(',')):
        match = re.fullmatch(r'\s*(\d+)\s*(?:[-–]\s*(\d+)\s*)?', item)
        first, last = map(int, match.groups(match[1])) if match else (0, 0)  # A single page ends where it starts.
        if not 1 <= first <= last:
            return None
        ranges.append((first, last))
    return ranges or None


def split_parts(count, options):
    """The first and last page of each part, counted from 1."""
    if options['mode'] == 'ranges':
        return page_ranges(options['ranges'])
    size = options['every'] if options['mode'] == 'every' else 1
    return [(first, min(first + size - 1, count)) for first in range(1, count + 1, size)]


def split_pdf(paths, options, progress, cancel):
    """Split each PDF into a new folder named after it: every page, page ranges, or every N pages."""
    import pymupdf

    def one(index, path):
        if path.suffix.lower() != '.pdf':
            raise JobError('not_pdf')
        source, _ = open_pdf(path, progress, cancel)
        with source:
            count = source.page_count
            parts = split_parts(count, options)
            if max(last for _, last in parts) > count:
                raise JobError('missing_pages')
            folder = staging(path, options) / str(index)
            folder.mkdir()
            digits = len(str(count))  # Zero-padded, so every app sorts the parts in page order.
            for number, (first, last) in enumerate(parts):
                check_cancel(cancel)
                pages = f'page_{first:0{digits}}' if first == last else f'pages_{first:0{digits}}-{last:0{digits}}'
                with pymupdf.open() as part:
                    part.insert_pdf(source, from_page=first - 1, to_page=last - 1)
                    part.save(folder / f'{path.stem}_{pages}.pdf', garbage=3, deflate=True)
                progress('progress', {'index': index + (number + 1) / len(parts), 'total': len(paths),
                                      'path': str(path)})
        output = publish_folder(folder, output_directory(path, options) / f'{path.stem}_split')
        progress('output', {'path': output, 'parts': len(parts)})
        return output

    return each_file(paths, options, progress, cancel, one)
