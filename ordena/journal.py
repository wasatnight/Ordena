"""Durable SQLite write-ahead intents for completed and interrupted moves."""
import json
from pathlib import Path
import sqlite3
import time

class Journal:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS operations(id INTEGER PRIMARY KEY, root TEXT, created REAL);
            CREATE TABLE IF NOT EXISTS moves(id INTEGER PRIMARY KEY, operation INTEGER,
                source TEXT, target TEXT, identity TEXT, state TEXT);
            CREATE TABLE IF NOT EXISTS folders(operation INTEGER, path TEXT, dev TEXT, inode TEXT);
        ''')
    def close(self):
        self.db.close()
    def start(self, root):
        with self.db:
            return self.db.execute('INSERT INTO operations(root,created) VALUES (?,?)',
                (str(root), time.time())).lastrowid
    def intent(self, operation, entry):
        with self.db:
            return self.db.execute('INSERT INTO moves(operation,source,target,identity,state) VALUES (?,?,?,?,?)',
                (operation, str(entry.source), str(entry.target), json.dumps(entry.identity), 'pending')).lastrowid
    def state(self, move, state):
        with self.db:
            self.db.execute('UPDATE moves SET state=? WHERE id=?', (state, move))
    def folder(self, operation, path):
        info = path.stat()
        with self.db:
            self.db.execute('INSERT INTO folders VALUES (?,?,?,?)', (operation, str(path), str(info.st_dev), str(info.st_ino)))
    def latest(self):
        return self.db.execute("SELECT MAX(operation) FROM moves WHERE state IN ('pending','moved','undo_pending')").fetchone()[0]
    def rows(self, operation):
        return self.db.execute('SELECT id,source,target,identity,state FROM moves WHERE operation=? ORDER BY id DESC', (operation,)).fetchall()
    def root(self, operation):
        return Path(self.db.execute('SELECT root FROM operations WHERE id=?', (operation,)).fetchone()[0])

