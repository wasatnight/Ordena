"""Tests only create synthetic files under TemporaryDirectory."""
import ctypes
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from ordena.rules import defaults, validate, Rule
from ordena.planner import scan
from ordena.executor import execute, undo
from ordena.journal import Journal
from ordena.safety import fingerprint, rename_checked, validate_root, DirectoryLock
from ordena.settings import Settings

class EngineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.root = self.base / 'Mixed'; self.root.mkdir()
        self.journal = Journal(self.base / 'history.db')
    def tearDown(self):
        self.journal.close(); self.temp.cleanup()
    def file(self, name, data=b'unchanged content\x00\xff'):
        path = self.root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
        return path
    def plan(self):
        return scan(self.root, defaults())
    def test_classification_case_unicode_and_preview_read_only(self):
        for name in ['área con espacios.JPG', '東京 🎬.Mp4', 'a.PDF', 'music.FLAC', 'a.7z', 'a.MSI']:
            self.file(name)
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        plan = self.plan()
        self.assertEqual(len(plan.entries), 6)
        self.assertTrue(all(e.selected for e in plan.entries))
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})
        self.assertEqual(execute(plan, self.journal).completed, 6)
        self.assertEqual(undo(self.journal).completed, 6)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})
    def test_collision_preview_and_existing_folder(self):
        self.file('report.pdf', b'new'); existing = self.file('Documents/report.pdf', b'old')
        plan = self.plan()
        self.assertEqual(plan.entries[0].target.name, 'report (1).pdf')
        self.assertEqual(plan.entries[0].status, 'renamed')
        self.assertEqual(execute(plan, self.journal).completed, 1)
        self.assertEqual(existing.read_bytes(), b'old')
        self.assertEqual(undo(self.journal).completed, 1)
        self.assertTrue(existing.parent.exists())
    def test_unknown_temporary_shortcuts_subfolders(self):
        for name in ['unknown.zzz', 'a.pdf.part', 'a.crdownload', 'a.tmp.pdf', 'shortcut.lnk', 'site.URL', '~$report.docx', '.private.pdf']:
            self.file(name)
        self.file('Subfolder/a.pdf')
        plan = self.plan()
        self.assertEqual(len(plan.entries), 8)
        self.assertFalse(any(e.selected for e in plan.entries))
        self.assertEqual(execute(plan, self.journal).completed, 0)
        self.assertTrue((self.root / 'Subfolder/a.pdf').exists())
    def test_disappeared_and_changed_files(self):
        a = self.file('a.pdf'); b = self.file('b.pdf')
        plan = self.plan(); a.unlink(); b.write_bytes(b'different')
        result = execute(plan, self.journal)
        self.assertEqual(result.completed, 0); self.assertEqual(len(result.errors), 2)
        self.assertEqual(b.read_bytes(), b'different')
    def test_same_size_and_time_changed_detected_by_hash(self):
        p = self.file('a.pdf', b'AAAA'); plan = self.plan(); info = p.stat()
        p.write_bytes(b'BBBB'); os.utime(p, ns=(info.st_atime_ns, info.st_mtime_ns))
        result = execute(plan, self.journal)
        self.assertEqual(result.completed, 0); self.assertTrue(p.exists())
    def test_new_collision_after_preview(self):
        self.file('a.pdf', b'original'); plan = self.plan()
        target = self.file('Documents/a.pdf', b'new occupant')
        result = execute(plan, self.journal)
        self.assertEqual(result.completed, 0); self.assertEqual(target.read_bytes(), b'new occupant')
    def test_no_replace_atomic_backend(self):
        p = self.file('a.pdf', b'original'); q = self.file('b.pdf', b'other')
        with self.assertRaises(OSError):
            rename_checked(p, q, fingerprint(p, True))
        self.assertEqual(p.read_bytes(), b'original'); self.assertEqual(q.read_bytes(), b'other')
    def test_cancel_after_one_and_restart_undo(self):
        for i in range(4): self.file(f'{i}.pdf')
        stop = [False]
        result = execute(self.plan(), self.journal, lambda: stop[0], lambda a,b: stop.__setitem__(0, True))
        self.assertTrue(result.cancelled); self.assertEqual(result.completed, 1); self.assertEqual(result.skipped, 3)
        path = self.journal.path; self.journal.close(); self.journal = Journal(path)
        self.assertEqual(undo(self.journal).completed, 1)
        self.assertEqual(len(list(self.root.glob('*.pdf'))), 4)
        self.assertFalse((self.root / 'Documents').exists())
    def test_scan_cancelled_cannot_execute(self):
        self.file('a.pdf'); plan = scan(self.root, defaults(), lambda: True)
        self.assertTrue(plan.cancelled)
        with self.assertRaises(ValueError): execute(plan, self.journal)
    def test_undo_original_location_conflict_retry(self):
        p = self.file('a.pdf', b'original'); execute(self.plan(), self.journal); p.write_bytes(b'new file')
        result = undo(self.journal)
        self.assertEqual(result.completed, 0); self.assertEqual(result.skipped, 1)
        self.assertEqual(p.read_bytes(), b'new file')
        self.assertEqual((self.root / 'Documents/a.pdf').read_bytes(), b'original')
        p.unlink(); self.assertEqual(undo(self.journal).completed, 1)
    def test_modified_destination_undo_refuses(self):
        self.file('a.pdf'); execute(self.plan(), self.journal)
        moved = self.root / 'Documents/a.pdf'; moved.write_bytes(b'edited')
        result = undo(self.journal)
        self.assertEqual(result.completed, 0); self.assertEqual(moved.read_bytes(), b'edited')
    def test_same_content_replacement_undo_refuses(self):
        self.file('a.pdf', b'same'); execute(self.plan(), self.journal)
        moved = self.root / 'Documents/a.pdf'
        backup = moved.with_name('hold.pdf'); moved.rename(backup); moved.write_bytes(b'same')
        self.assertEqual(undo(self.journal).completed, 0)
    def test_excluded_file_stays(self):
        p = self.file('a.pdf'); plan = self.plan(); plan.entries[0].selected = False
        self.assertEqual(execute(plan, self.journal).completed, 0); self.assertTrue(p.exists())
    def test_corrupt_preferences_fall_back_and_persist_spanish(self):
        directory = self.base / 'settings'; directory.mkdir(); (directory / 'settings.json').write_text('{broken')
        settings = Settings(directory); self.assertEqual(settings.language, 'en')
        settings.language = 'es'; settings.rules = [Rule('Imágenes', ['JPG'])]; settings.save()
        again = Settings(directory); self.assertEqual(again.language, 'es'); self.assertEqual(again.rules[0].extensions, ['jpg'])
    def test_invalid_and_ambiguous_rules(self):
        for name in ['../escape', 'CON', 'nul.txt', 'COM1', 'trailing.', 'a/b', 'a\\b', '', 'bad:dir']:
            with self.subTest(name=name), self.assertRaises(ValueError): validate([Rule(name, ['pdf'])])
        with self.assertRaises(ValueError): validate([Rule('A', ['jpg']), Rule('B', ['JPG'])])
        with self.assertRaises(ValueError): validate([Rule('A', ['jpg']), Rule('a', ['png'])])
    def test_drive_and_system_roots_rejected(self):
        with self.assertRaises(ValueError): validate_root(Path(self.root.anchor))
        with self.assertRaises((ValueError, OSError)): validate_root(os.environ.get('WINDIR', 'C:/Windows'))
    def test_destination_file_blocks_category(self):
        self.file('Documents'); self.file('a.pdf')
        self.assertFalse(any(e.selected for e in self.plan().entries))
    def test_hidden_and_system_files_excluded(self):
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        for name, flag in [('hidden.pdf', 2), ('system.pdf', 4)]:
            p = self.file(name)
            self.assertTrue(kernel.SetFileAttributesW(str(p), flag))
        self.assertFalse(any(e.selected for e in self.plan().entries))
    def test_hard_link_excluded(self):
        p = self.file('a.pdf')
        try: os.link(p, self.root / 'b.pdf')
        except OSError: self.skipTest('Hard link creation unavailable in sandbox')
        self.assertFalse(any(e.selected for e in self.plan().entries))
    def test_locked_file_does_not_block_other_moves(self):
        from ctypes import wintypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        kernel.CreateFileW.restype = wintypes.HANDLE; kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        p = self.file('a.pdf'); self.file('b.pdf'); plan = self.plan()
        handle = kernel.CreateFileW(str(p), 0x80000000, 0, None, 3, 0, None)
        self.assertNotEqual(handle, ctypes.c_void_p(-1).value)
        try:
            result = execute(plan, self.journal)
            self.assertEqual(result.completed, 1); self.assertTrue(p.exists())
        finally: kernel.CloseHandle(handle)
    def test_directory_lock_prevents_replacement(self):
        folder = self.root / 'Documents'; folder.mkdir()
        with DirectoryLock([folder]):
            with self.assertRaises(OSError): folder.rename(self.root / 'Swap')
    def test_junction_destination_rejected(self):
        outside = self.base / 'Outside'; outside.mkdir()
        junction = self.root / 'Documents'
        proc = subprocess.run(['cmd', '/c', 'mklink', '/J', str(junction), str(outside)], capture_output=True)
        if proc.returncode: self.skipTest('Junction creation unavailable')
        try:
            self.file('a.pdf'); self.assertFalse(any(e.selected for e in self.plan().entries))
            with self.assertRaises(ValueError): validate_root(junction)
        finally: junction.rmdir()
    def test_interrupted_intent_before_move(self):
        self.file('a.pdf'); entry = self.plan().entries[0]
        op = self.journal.start(self.root); self.journal.intent(op, entry)
        path = self.journal.path; self.journal.close(); self.journal = Journal(path)
        result = undo(self.journal)
        self.assertEqual(result.skipped, 0); self.assertTrue(entry.source.exists()); self.assertIsNone(self.journal.latest())
    def test_real_process_interruption_after_move(self):
        self.file('a.pdf'); path = self.journal.path
        script = '''
import os, sys
from ordena.journal import Journal
from ordena.planner import scan
from ordena.rules import defaults
from ordena.safety import rename_checked
from pathlib import Path
j = Journal(sys.argv[1]); root = Path(sys.argv[2]); entry = scan(root, defaults()).entries[0]
op = j.start(root); entry.target.parent.mkdir(); j.folder(op, entry.target.parent); j.intent(op, entry)
rename_checked(entry.source, entry.target, entry.identity)
os._exit(17)
'''
        proc = subprocess.run([sys.executable, '-c', script, str(path), str(self.root)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 17, proc.stderr)
        self.journal.close(); self.journal = Journal(path)
        self.assertEqual(undo(self.journal).completed, 1); self.assertTrue((self.root / 'a.pdf').exists())
    def test_interrupted_undo_after_rename(self):
        self.file('a.pdf'); execute(self.plan(), self.journal)
        row = self.journal.rows(self.journal.latest())[0]
        import json
        self.journal.state(row[0], 'undo_pending')
        rename_checked(Path(row[2]), Path(row[1]), json.loads(row[3]))
        self.assertEqual(undo(self.journal).completed, 1); self.assertIsNone(self.journal.latest())
    def test_reject_plan_destination_escape(self):
        self.file('a.pdf'); plan = self.plan(); plan.entries[0].target = self.base / 'evil.pdf'
        self.assertEqual(execute(plan, self.journal).completed, 0)
        self.assertFalse((self.base / 'evil.pdf').exists())
    def test_undo_cancellation_retains_recoverability(self):
        for i in range(3): self.file(f'{i}.pdf')
        execute(self.plan(), self.journal)
        stop = [False]
        result = undo(self.journal, lambda: stop[0], lambda a,b: stop.__setitem__(0, True))
        self.assertTrue(result.cancelled); self.assertEqual(result.completed, 1)
        self.assertEqual(undo(self.journal).completed, 2)

if __name__ == '__main__': unittest.main()

