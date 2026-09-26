import logging


def job_loop(commands, events, answers, cancel):
    from logging_setup import configure_logging
    from core.files import Cancelled, error_code
    configure_logging(worker=True)

    def progress(kind, payload):
        events.put((kind, payload))
        if kind == 'password':
            return answers.get()

    while True:
        command = commands.get()
        if command is None:
            return
        paths, options = command
        try:
            from core.pdf_tools import make_pdf
            outputs = make_pdf(paths, options, progress, cancel)
            events.put(('done', outputs))
        except Cancelled:
            events.put(('cancelled', None))
        except Exception as error:
            logging.exception('PDF job failed')
            events.put(('failed', error_code(error)))


def thumbnail_loop(commands, events):
    from core.thumbnails import thumbnail
    while True:
        path = commands.get()
        if path is None:
            return
        events.put((path, thumbnail(path)))
