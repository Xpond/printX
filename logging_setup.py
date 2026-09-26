import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging(worker=False):
    root = Path(os.environ.get('LOCALAPPDATA') or os.environ.get('XDG_STATE_HOME')
                or Path.home() / '.local/state')
    directory = root / 'PrintShop Tools' / 'logs'
    directory.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(directory / ('worker.log' if worker else 'app.log'),
                                  maxBytes=2_000_000, backupCount=3, encoding='utf-8')
    logging.basicConfig(level=logging.INFO, handlers=[handler],
                        format='%(asctime)s %(levelname)s %(message)s', force=True)
