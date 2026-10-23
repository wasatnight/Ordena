"""Read-only first-level scanning and collision planning."""
from dataclasses import dataclass
from pathlib import Path
from .rules import validate
from .safety import validate_root, unsafe, fingerprint, TEMP_EXTENSIONS, LINK_EXTENSIONS, destination

@dataclass
class Entry:
    source: Path
    target: Path | None
    category: str
    size: int
    identity: list | None
    status: str
    selected: bool = False

@dataclass
class Plan:
    root: Path
    rules: list
    entries: list[Entry]
    cancelled: bool = False

def scan(folder, rules, cancelled=lambda: False):
    root = validate_root(folder)
    rules = validate(rules)
    lookup = {'.' + ext: rule.name for rule in rules for ext in rule.extensions}
    result = Plan(root, rules, [])
    reserved = set()
    for source in sorted(root.iterdir(), key=lambda p: p.name.casefold()):
        if cancelled():
            result.cancelled = True
            break
        try:
            if source.is_dir() and not unsafe(source):
                continue
            info = source.lstat()
            entry = Entry(source, None, '', info.st_size, None, 'ready')
            result.entries.append(entry)
            if unsafe(source) or source.suffix.lower() in LINK_EXTENSIONS or info.st_nlink != 1:
                entry.status = 'unsafe_file'
                continue
            if (source.suffix.lower() in TEMP_EXTENSIONS or source.name.startswith(('~$', '.'))
                or any(suffix.lower() in TEMP_EXTENSIONS for suffix in source.suffixes)):
                entry.status = 'temporary'
                continue
            category = lookup.get(source.suffix.lower())
            if not category:
                entry.status = 'unclassified'
                continue
            entry.category = category
            parent = root / category
            if parent.exists() and (unsafe(parent) or not parent.is_dir()):
                entry.status = 'unsafe_folder'
                continue
            target = destination(root, parent / source.name)
            count = 1
            while target.exists() or str(target).casefold() in reserved:
                target = parent / f'{source.stem} ({count}){source.suffix}'
                count += 1
            reserved.add(str(target).casefold())
            entry.target = target
            entry.identity = fingerprint(source, digest=True)
            entry.status = 'renamed' if count > 1 else 'ready'
            entry.selected = True
        except (OSError, ValueError) as exc:
            if result.entries and result.entries[-1].source == source:
                result.entries[-1].status = str(exc) if isinstance(exc, ValueError) else 'unreadable'
                result.entries[-1].selected = False
            else:
                result.entries.append(Entry(source, None, '', 0, None, 'unreadable'))
    return result
