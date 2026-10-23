import json
import os
from pathlib import Path
from .rules import Rule, defaults, validate, serialize

class Settings:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / 'settings.json'
        self.language, self.rules, self.folder = 'en', defaults(), ''
        try:
            data = json.loads(self.path.read_text(encoding='utf-8'))
            self.language = data.get('language', 'en') if data.get('language') in ('en', 'es') else 'en'
            self.rules = validate([Rule(**r) for r in data['rules']])
            self.folder = data.get('folder', '')
        except (OSError, ValueError, TypeError, KeyError):
            pass
    def save(self):
        temporary = self.path.with_suffix('.tmp')
        with temporary.open('w', encoding='utf-8') as stream:
            json.dump({'language': self.language, 'rules': serialize(self.rules), 'folder': self.folder}, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, self.path)
