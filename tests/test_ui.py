import os
from pathlib import Path
import tempfile
import time
import unittest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QTableWidgetItem
from PySide6.QtTest import QTest
from ordena.ui import Window, RuleDialog
from ordena.rules import defaults
from ordena.i18n import TEXT

app = QApplication.instance() or QApplication([])

class InterfaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.base = Path(self.temp.name)
        self.root = self.base / 'Preview'; self.root.mkdir()
        self.window = Window(self.base / 'settings'); self.window.show()
        app.processEvents()
    def tearDown(self):
        self.wait_task(); self.window.close(); app.processEvents(); self.temp.cleanup()
    def wait_task(self):
        limit = time.monotonic() + 15
        while self.window.task is not None and time.monotonic() < limit:
            app.processEvents(); QTest.qWait(10)
        self.assertIsNone(self.window.task, 'Background task did not finish')
        app.processEvents()
    def populate(self):
        (self.root / 'café.JPG').write_bytes(b'image bytes')
        (self.root / 'report.pdf').write_bytes(b'document bytes')
        (self.root / 'download.crdownload').write_bytes(b'partial')
        self.window.set_folder(str(self.root)); self.wait_task()
    def test_english_default_and_spanish_persists(self):
        self.assertEqual(self.window.choose.text(), 'Choose folder')
        self.window.language.setCurrentIndex(1); app.processEvents()
        self.assertEqual(self.window.choose.text(), 'Seleccionar carpeta')
        self.window.close()
        self.window = Window(self.base / 'settings')
        self.assertEqual(self.window.settings.language, 'es')
        self.assertEqual(self.window.organize.text(), 'Organizar')
    def test_preview_exclusions_categories_and_no_files_moved(self):
        self.populate()
        self.assertEqual(self.window.table.rowCount(), 3)
        self.assertTrue(self.window.organize.isEnabled())
        self.assertFalse((self.root / 'Images').exists())
        self.window.table.item(0, 0).setCheckState(Qt.Unchecked); app.processEvents()
        self.assertFalse(self.window.plan.entries[0].selected)
        check = next(c for c in self.window.category_checks if c.toolTip() == 'Documents')
        check.setCheckState(Qt.Unchecked); app.processEvents()
        self.assertFalse(self.window.organize.isEnabled())
    def test_organize_confirm_undo_and_refresh_flow(self):
        self.populate()
        self.window.confirm = lambda text: True
        self.window.organize_files(); self.assertFalse(self.window.choose.isEnabled()); self.wait_task()
        self.assertTrue((self.root / 'Images/café.JPG').exists())
        self.assertTrue((self.root / 'download.crdownload').exists())
        self.assertTrue(self.window.undo_button.isEnabled()); self.assertFalse(self.window.organize.isEnabled())
        self.assertIn('Completed: 2', self.window.status.text())
        self.window.undo(); self.wait_task()
        self.assertTrue((self.root / 'café.JPG').exists()); self.assertFalse((self.root / 'Images').exists())
        self.assertFalse(self.window.undo_button.isEnabled())
        self.window.scan(); self.wait_task(); self.assertTrue(self.window.organize.isEnabled())
    def test_language_switch_preserves_destinations_and_exclusions(self):
        self.populate()
        before = [e.target for e in self.window.plan.entries]
        self.window.table.item(0, 0).setCheckState(Qt.Unchecked)
        self.window.language.setCurrentIndex(1); app.processEvents()
        self.assertEqual(before, [e.target for e in self.window.plan.entries])
        self.assertFalse(self.window.plan.entries[0].selected)
        self.assertEqual(self.window.table.horizontalHeaderItem(0).text(), 'Nombre del archivo')
    def test_changed_folder_invalidates_plan(self):
        self.populate()
        other = self.base / 'Other'; other.mkdir()
        self.window.set_folder(str(other)); self.assertFalse(self.window.organize.isEnabled()); self.wait_task()
        self.assertEqual(self.window.table.rowCount(), 0)
    def test_rule_editor_changes_destination_and_scan(self):
        self.populate()
        dialog = RuleDialog(self.window.settings.rules, 'en', self.window)
        dialog.table.item(0, 0).setText('Pictures'); dialog.save()
        self.window.settings.rules = dialog.rules; self.window.scan(); self.wait_task()
        image = next(e for e in self.window.plan.entries if e.source.suffix == '.JPG')
        self.assertEqual(image.target.parent.name, 'Pictures')
    def test_all_translation_pairs_nonempty(self):
        self.assertTrue(all(len(pair) == 2 and all(pair) for pair in TEXT.values()))
    def test_cancelled_scan_cannot_enable_organize(self):
        for index in range(100): (self.root / f'{index}.pdf').write_bytes(b'x')
        self.window.set_folder(str(self.root)); self.window.cancel_task(); self.wait_task()
        self.assertTrue(self.window.plan.cancelled); self.assertFalse(self.window.organize.isEnabled())

if __name__ == '__main__': unittest.main()
