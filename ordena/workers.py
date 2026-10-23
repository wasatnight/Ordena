from threading import Event
from PySide6.QtCore import QThread, Signal
from .planner import scan
from .journal import Journal
from .executor import execute, undo

class Task(QThread):
    result = Signal(object)
    failed = Signal(str)
    progress = Signal(int, int)
    def __init__(self, mode, payload, journal_path, parent=None):
        super().__init__(parent)
        self.mode, self.payload, self.journal_path = mode, payload, journal_path
        self.cancelled = Event()
    def run(self):
        journal = None
        try:
            if self.mode == 'scan':
                result = scan(*self.payload, self.cancelled.is_set)
            else:
                journal = Journal(self.journal_path)
                args = (journal, self.cancelled.is_set, self.progress.emit)
                result = execute(self.payload, *args) if self.mode == 'move' else undo(*args)
            self.result.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            if journal:
                journal.close()
