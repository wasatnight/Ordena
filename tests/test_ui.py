import os
from pathlib import Path
import tempfile
import time
import unittest
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtWidgets import QApplication, QTableWidgetItem
from PySide6.QtTest import QTest
from ordena.ui import Window, RuleDialog, HelpDialog
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
        limit = time.monotonic() + 45
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

    def test_mouse_click_filename_toggles_without_rebuilding_items(self):
        self.populate()
        table = self.window.table
        item = table.item(0, 0)
        position = table.visualItemRect(item).center()
        QTest.mouseClick(table.viewport(), Qt.LeftButton, pos=position)
        self.assertFalse(self.window.plan.entries[0].selected)
        self.assertIs(table.item(0, 0), item)
        self.assertFalse(table.selectionModel().selectedRows())
        QTest.mouseClick(table.viewport(), Qt.LeftButton, pos=position)
        self.assertTrue(self.window.plan.entries[0].selected)
        self.assertIs(table.item(0, 0), item)
    def test_mouse_click_checkbox_toggles_once(self):
        self.populate()
        table = self.window.table
        rect = table.visualItemRect(table.item(0, 0))
        QTest.mouseClick(table.viewport(), Qt.LeftButton, pos=QPoint(rect.left() + 16, rect.center().y()))
        self.assertFalse(self.window.plan.entries[0].selected)
        self.assertIn('Excluded', table.item(0, 5).text())
    def test_keyboard_space_toggles_without_row_highlight(self):
        self.populate()
        table = self.window.table
        table.setCurrentCell(0, 0); table.setFocus()
        QTest.keyClick(table, Qt.Key_Space)
        self.assertFalse(self.window.plan.entries[0].selected)
        QTest.keyClick(table, Qt.Key_Space)
        self.assertTrue(self.window.plan.entries[0].selected)
        self.assertFalse(table.selectionModel().selectedRows())
    def test_scroll_and_item_survive_real_mouse_toggle(self):
        for index in range(24): (self.root / f'{index:03}.pdf').write_bytes(b'test')
        self.window.set_folder(str(self.root)); self.wait_task()
        table = self.window.table
        item = table.item(23, 0); table.scrollToItem(item)
        app.processEvents()
        scroll = table.verticalScrollBar().value()
        QTest.mouseClick(table.viewport(), Qt.LeftButton, pos=table.visualItemRect(item).center())
        self.assertFalse(self.window.plan.entries[23].selected)
        self.assertEqual(table.verticalScrollBar().value(), scroll)
        self.assertIs(table.item(23, 0), item)
    def test_partial_category_click_selects_all_then_none(self):
        self.populate()
        (self.root / 'second.pdf').write_bytes(b'second')
        self.window.scan(); self.wait_task()
        row = next(i for i,e in enumerate(self.window.plan.entries) if e.source.name == 'report.pdf')
        self.window.table.item(row, 0).setCheckState(Qt.Unchecked)
        check = next(c for c in self.window.category_checks if c.toolTip() == 'Documents')
        self.assertEqual(check.checkState(), Qt.PartiallyChecked)
        QTest.mouseClick(check, Qt.LeftButton, pos=check.rect().center())
        self.assertEqual(check.checkState(), Qt.Checked)
        self.assertTrue(all(e.selected for e in self.window.plan.entries if e.category == 'Documents'))
        QTest.mouseClick(check, Qt.LeftButton, pos=check.rect().center())
        self.assertEqual(check.checkState(), Qt.Unchecked)
        self.assertFalse(any(e.selected for e in self.window.plan.entries if e.category == 'Documents'))
        self.assertIs(check, next(c for c in self.window.category_checks if c.toolTip() == 'Documents'))
    def test_header_is_centered_with_matching_subtitle_font(self):
        brand = self.window.brand; subtitle = self.window.tagline
        center = brand.mapTo(self.window, brand.rect().center()).x()
        self.assertLessEqual(abs(center - self.window.rect().center().x()), 2)
        self.assertGreaterEqual(subtitle.mapTo(self.window, QPoint(0, 0)).y(), brand.mapTo(self.window, QPoint(0, brand.height())).y())
        self.assertEqual(brand.font().family(), subtitle.font().family())
        self.assertEqual(brand.font().weight(), subtitle.font().weight())
        self.assertLess(subtitle.font().pointSizeF(), brand.font().pointSizeF())
    def test_help_button_opens_examples_in_each_language(self):
        for index, word in [(0, 'holiday.jpg'), (1, 'vacaciones.jpg')]:
            self.window.language.setCurrentIndex(index)
            observed = []
            def close_help():
                dialog = app.activeModalWidget()
                observed.append(dialog.browser.toPlainText())
                dialog.accept()
            QTimer.singleShot(100, close_help)
            QTest.mouseClick(self.window.help_button, Qt.LeftButton)
            self.assertIn(word, observed[0])
            self.assertIn('Documents/', observed[0])
            self.assertIn('crdownload', observed[0])
        self.assertFalse(hasattr(self.window, 'hint'))
    def test_window_icon_has_small_and_large_windows_sizes(self):
        sizes = {size.width() for size in self.window.windowIcon().availableSizes()}
        self.assertTrue({16, 32, 48, 256}.issubset(sizes))
        self.assertFalse(self.window.windowIcon().pixmap(32, 32).isNull())

    def test_language_popup_click_changes_language_with_blush_selection(self):
        from PySide6.QtGui import QPalette
        from ordena.theme import ACCENT
        combo = self.window.language
        combo.showPopup(); app.processEvents()
        view = combo.view()
        self.assertTrue(view.isVisible())
        self.assertEqual(view.palette().color(QPalette.Highlight).name(), ACCENT)
        QTest.mouseClick(view.viewport(), Qt.LeftButton, pos=view.visualRect(view.model().index(1, 0)).center())
        app.processEvents()
        self.assertEqual(self.window.settings.language, 'es')
        self.assertEqual(self.window.choose.text(), 'Seleccionar carpeta')

if __name__ == '__main__': unittest.main()

