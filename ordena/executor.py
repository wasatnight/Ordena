"""Cancellation, durable execution and conservative undo recovery."""
from dataclasses import dataclass, field
import json
from pathlib import Path
from .safety import validate_root, destination, fingerprint, rename_checked, DirectoryLock, unsafe

@dataclass
class Result:
    completed: int = 0
    skipped: int = 0
    errors: list = field(default_factory=list)
    cancelled: bool = False

def execute(plan, journal, cancelled=lambda: False, progress=lambda a, b: None):
    root = validate_root(plan.root)
    if plan.cancelled:
        raise ValueError('scan_cancelled')
    selected = [e for e in plan.entries if e.selected and e.target and e.identity]
    result = Result(skipped=len(plan.entries) - len(selected))
    operation = None
    with DirectoryLock([root]):
        for index, entry in enumerate(selected):
            if cancelled():
                result.cancelled = True
                result.skipped += len(selected) - index
                break
            try:
                if entry.source.parent != root or entry.status not in {'ready', 'renamed'}:
                    raise ValueError('changed')
                target = destination(root, entry.target)
                if fingerprint(entry.source) != entry.identity[:4]:
                    raise ValueError('changed')
                if target.exists():
                    raise ValueError('new_conflict')
                if operation is None:
                    operation = journal.start(root)
                if not target.parent.exists():
                    target.parent.mkdir()
                    journal.folder(operation, target.parent)
                with DirectoryLock([target.parent]):
                    destination(root, target)
                    move = journal.intent(operation, entry)
                    rename_checked(entry.source, target, entry.identity)
                    journal.state(move, 'moved')
                    result.completed += 1
            except (OSError, ValueError) as exc:
                result.skipped += 1
                result.errors.append((entry.source.name, str(exc)))
            progress(index + 1, len(selected))
    return result

def matches(path, identity):
    try:
        return fingerprint(path, digest=True) == identity
    except (ValueError, OSError):
        return False

def undo(journal, cancelled=lambda: False, progress=lambda a, b: None):
    result = Result()
    operation = journal.latest()
    if operation is None:
        return result
    root = validate_root(journal.root(operation))
    rows = [r for r in journal.rows(operation) if r[4] in {'pending', 'moved', 'undo_pending'}]
    with DirectoryLock([root]):
        for index, (move, source, target, identity, state) in enumerate(rows):
            if cancelled():
                result.cancelled = True
                result.skipped += len(rows) - index
                break
            source, target, identity = Path(source), Path(target), json.loads(identity)
            try:
                if source.parent != root:
                    raise ValueError('unsafe_folder')
                destination(root, target)
                if state in {'pending', 'undo_pending'} and matches(source, identity) and not target.exists():
                    journal.state(move, 'undone')
                    result.completed += int(state == 'undo_pending')
                    continue
                if state == 'pending' and matches(source, identity):
                    journal.state(move, 'not_moved')
                    continue
                if source.exists() or source.is_symlink():
                    raise ValueError('restore_conflict')
                with DirectoryLock([target.parent]):
                    destination(root, target)
                    if not matches(target, identity):
                        raise ValueError('restore_changed')
                    journal.state(move, 'undo_pending')
                    rename_checked(target, source, identity)
                    journal.state(move, 'undone')
                    result.completed += 1
            except (ValueError, OSError) as exc:
                result.skipped += 1
                result.errors.append((source.name, str(exc)))
            progress(index + 1, len(rows))
        for path, dev, inode in journal.db.execute('SELECT path,dev,inode FROM folders WHERE operation=?', (operation,)):
            path = Path(path)
            try:
                if path.parent == root and not unsafe(path):
                    info = path.stat()
                    if (str(info.st_dev), str(info.st_ino)) == (dev, inode):
                        path.rmdir()
            except OSError:
                pass
    return result

