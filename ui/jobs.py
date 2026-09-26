import multiprocessing as mp
import queue
import shutil
import uuid

from PySide6.QtCore import QObject, QTimer, Signal
from core.files import output_directory, stage_directory
from core.worker import job_loop, thumbnail_loop


class Jobs(QObject):
    event = Signal(str, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.context = mp.get_context('spawn')
        self.process = None
        self.busy = False
        self.cancelling = False
        self.stages = set()
        self.timer = QTimer(self)
        self.timer.setInterval(25)
        self.timer.timeout.connect(self.poll)

    def start(self, paths, options):
        if self.busy:
            return
        if self.process is None:
            self.commands = self.context.Queue()
            self.events = self.context.Queue()
            self.answers = self.context.Queue()
            self.cancel_flag = self.context.Event()
            self.process = self.context.Process(target=job_loop,
                args=(self.commands, self.events, self.answers, self.cancel_flag), daemon=True)
            self.process.start()
        self.cancel_flag.clear()
        options = dict(options, token=uuid.uuid4().hex)
        self.stages = {stage_directory(output_directory(p, options), options['token']) for p in paths}
        self.busy = True
        self.commands.put((paths, options))
        self.timer.start()

    def cancel(self):
        if not self.busy or self.cancelling:
            return
        self.cancelling = True
        self.cancel_flag.set()
        self.process.terminate()

    def dispose(self):
        self.process.join(timeout=0)
        self.process.close()
        self.process = None
        for channel in (self.commands, self.events, self.answers):
            channel.cancel_join_thread()
            channel.close()
        for directory in self.stages:
            shutil.rmtree(directory, ignore_errors=True)

    def poll(self):
        if self.cancelling:
            if not self.process.is_alive():
                self.dispose()
                self.busy = self.cancelling = False
                self.timer.stop()
                self.event.emit('cancelled', None)
            return
        try:
            while True:
                kind, payload = self.events.get_nowait()
                if kind in ('done', 'failed', 'cancelled'):
                    self.busy = False
                    self.timer.stop()
                self.event.emit(kind, payload)
        except queue.Empty:
            pass
        if self.busy and not self.process.is_alive():
            self.dispose()
            self.busy = False
            self.timer.stop()
            self.event.emit('failed', 'worker')

    def shutdown(self):
        self.timer.stop()
        if self.process:
            self.process.terminate()
            self.process.join(timeout=2)
            self.dispose()


class Thumbnails(QObject):
    ready = Signal(str, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = None
        self.pending = set()
        self.timer = QTimer(self)
        self.timer.setInterval(40)
        self.timer.timeout.connect(self.poll)

    def request(self, path):
        if path in self.pending:
            return
        if self.process is None:
            ctx = mp.get_context('spawn')
            self.commands, self.events = ctx.Queue(), ctx.Queue()
            self.process = ctx.Process(target=thumbnail_loop, args=(self.commands, self.events), daemon=True)
            self.process.start()
            self.timer.start()
        self.pending.add(path)
        self.commands.put(path)

    def poll(self):
        try:
            while True:
                path, result = self.events.get_nowait()
                self.pending.discard(path)
                self.ready.emit(path, result)
        except queue.Empty:
            pass

    def shutdown(self):
        self.timer.stop()
        if self.process:
            self.process.terminate()
            self.process.join(timeout=2)
            for channel in (self.commands, self.events):
                channel.cancel_join_thread()
                channel.close()
