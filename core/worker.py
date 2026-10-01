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
            if options.get('tool') == 'upscale':
                from core.upscale import upscale as job
            elif options.get('tool') == 'compress':
                from core.compress import compress as job
            elif options.get('tool') == 'split':
                from core.pdf_tools import split_pdf as job
            elif options.get('tool') == 'remove':
                from core.remove import remove as job
            elif options.get('tool') == 'enhance':
                from core.enhance import enhance as job
            else:
                from core.pdf_tools import make_pdf as job
            events.put(('done', job(paths, options, progress, cancel)))
        except Cancelled:
            events.put(('cancelled', None))
        except Exception as error:
            logging.exception('Job failed')
            events.put(('failed', error_code(error)))


def thumbnail_loop(commands, events):
    from core.thumbnails import thumbnail
    while True:
        command = commands.get()
        if command is None:
            return
        events.put((command[0], thumbnail(*command)))
