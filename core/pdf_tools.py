import logging
import shutil
from pathlib import Path

from core.files import (INPUT_EXTENSIONS, Cancelled, JobError, check_cancel, error_code,
                        output_directory, publish, stage_directory)


def open_pdf(path, progress, cancel):
    import pymupdf
    with open(path, 'rb'):
        pass  # Preserve ordinary filesystem errors before MuPDF wraps them.
    document = pymupdf.open(path)
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
        return document
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

    def save(document, source, suffix):
        directory = output_directory(source, options)
        stage = stage_directory(directory, token)
        stage.mkdir(parents=True, exist_ok=True)
        stages.add(stage)
        temp = stage / 'output.pdf'
        check_cancel(cancel)
        document.save(temp, garbage=3, deflate=True)
        check_cancel(cancel)
        output = publish(temp, directory / f'{Path(source).stem}_{suffix}.pdf')
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
                    source = open_pdf(path, progress, cancel)
                else:
                    source = pymupdf.open(stream=image_pdf(path, options, cancel), filetype='pdf')
                with source:
                    check_cancel(cancel)
                    if combined:
                        result.insert_pdf(source)
                    else:
                        with pymupdf.open() as single:
                            single.insert_pdf(source)
                            save(single, path, 'made')
            except Cancelled:
                raise
            except Exception as error:
                logging.exception('Could not process %s', path)
                progress('skipped', {'path': str(path), 'code': error_code(error)})
            progress('progress', {'index': index + 1, 'total': len(paths), 'path': str(path)})
        if combined and result.page_count:
            save(result, paths[0], 'combined' if len(paths) > 1 else 'made')
        if not outputs:
            raise JobError('no_outputs')
        return outputs
    finally:
        result.close()
        for stage in stages:
            shutil.rmtree(stage, ignore_errors=True)
