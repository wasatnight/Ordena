"""Qt Widgets desktop interface. All filesystem work runs outside the GUI thread."""
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QFileDialog, QMessageBox, QProgressBar,
    QDialog, QDialogButtonBox, QScrollArea, QTextEdit, QTextBrowser)
from .i18n import tr
from .rules import Rule, validate
from .settings import Settings
from .journal import Journal
from .workers import Task
from .theme import STYLE, ASSETS, ACCENT, MUTED, configure_app
from .controls import FileDelegate, CategoryCheckBox


def size_text(size):
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if size < 1024 or unit == 'TB':
            return f'{size:,.1f} {unit}' if unit != 'B' else f'{size} B'
        size /= 1024

class RuleDialog(QDialog):
    def __init__(self, rules, language, parent=None):
        super().__init__(parent)
        self.language = language
        self.setWindowTitle(tr('rules', language))
        self.resize(720, 440)
        layout = QVBoxLayout(self)
        hint = QLabel(tr('rule_hint', language)); hint.setWordWrap(True); layout.addWidget(hint)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels([tr('name', language), tr('extensions', language)])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 180)
        for rule in rules:
            self.add(rule.name, ' '.join(rule.extensions))
        layout.addWidget(self.table)
        actions = QHBoxLayout()
        add = QPushButton(tr('add', language)); add.clicked.connect(lambda: self.add('', ''))
        remove = QPushButton(tr('remove', language)); remove.clicked.connect(lambda: self.table.removeRow(self.table.currentRow()))
        actions.addWidget(add); actions.addWidget(remove); layout.addLayout(actions)
        buttons = QDialogButtonBox()
        save = buttons.addButton(tr('save', language), QDialogButtonBox.AcceptRole)
        buttons.addButton(tr('cancel', language), QDialogButtonBox.RejectRole)
        save.clicked.connect(self.save); buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    def add(self, name, extensions):
        row = self.table.rowCount(); self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))
        self.table.setItem(row, 1, QTableWidgetItem(extensions))
    def save(self):
        try:
            self.rules = validate([Rule(self.table.item(r, 0).text(),
                self.table.item(r, 1).text().replace(',', ' ').split()) for r in range(self.table.rowCount())])
            self.accept()
        except ValueError as exc:
            QMessageBox.warning(self, tr('rules', self.language), tr(str(exc), self.language))

class HelpDialog(QDialog):
    def __init__(self, language, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('help_title', language))
        self.resize(740, 660)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)
        self.browser.document().setDefaultStyleSheet(
            'body {color:#243b63; font-family:Segoe UI; font-size:11pt;}'
            'h2,h3 {color:#243b63;} p {line-height:1.5;}'
            'code {color:#243b63;} td {padding:7px;}')
        self.browser.setHtml(tr('help_body', language))
        layout.addWidget(self.browser)
        buttons = QDialogButtonBox()
        close = buttons.addButton(tr('close', language), QDialogButtonBox.RejectRole)
        close.clicked.connect(self.accept)
        layout.addWidget(buttons)


class Window(QMainWindow):
    def __init__(self, data_dir):
        super().__init__()
        configure_app()
        self.setWindowIcon(QIcon(str(ASSETS / "app.ico")))
        self.settings = Settings(data_dir)
        self.journal_path = Path(data_dir) / 'history.sqlite3'
        self.plan, self.task, self.mode = None, None, None
        self.category_checks = []
        self.setWindowTitle('Ordena')
        self.resize(1240, 820); self.setMinimumSize(940, 650)
        self.setAcceptDrops(True)
        self.setStyleSheet(STYLE)
        content = QWidget(); self.setCentralWidget(content)
        layout = QVBoxLayout(content); layout.setContentsMargins(30, 22, 30, 22); layout.setSpacing(14)
        header = QHBoxLayout()
        left_balance = QWidget(); left_balance.setFixedWidth(186)
        header.addWidget(left_balance)
        title = QWidget(); title_layout = QVBoxLayout(title)
        title_layout.setContentsMargins(0, 0, 0, 0); title_layout.setSpacing(0)
        self.brand = QLabel('ordena.'); self.brand.setObjectName('brand'); self.brand.setAlignment(Qt.AlignCenter)
        self.tagline = QLabel(); self.tagline.setObjectName('subtitle'); self.tagline.setAlignment(Qt.AlignCenter)
        self.tagline.setWordWrap(True)
        title_layout.addWidget(self.brand); title_layout.addWidget(self.tagline)
        header.addWidget(title, 1)
        controls = QWidget(); controls.setFixedWidth(186)
        control_layout = QHBoxLayout(controls); control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(10)
        self.language = QComboBox(); self.language.addItems(['English', 'Español'])
        self.language.setFixedSize(140, 36)
        self.language.setCurrentIndex(self.settings.language == 'es')
        self.language.currentIndexChanged.connect(self.change_language)
        control_layout.addWidget(self.language)
        self.help_button = QPushButton('?'); self.help_button.setObjectName('help'); self.help_button.setFixedSize(36, 36)
        self.help_button.clicked.connect(self.show_help); control_layout.addWidget(self.help_button)
        header.addWidget(controls, 0, Qt.AlignTop)
        layout.addLayout(header)
        self.path_label = QLabel(); self.path_label.setObjectName('path'); self.path_label.setWordWrap(True); self.path_label.setTextFormat(Qt.PlainText)
        self.path_label.setTextInteractionFlags(Qt.TextSelectableByMouse); layout.addWidget(self.path_label)
        actions = QHBoxLayout()
        self.choose = QPushButton(); self.choose.clicked.connect(self.pick_folder); actions.addWidget(self.choose)
        self.refresh = QPushButton(); self.refresh.clicked.connect(self.scan); actions.addWidget(self.refresh)
        actions.addStretch()
        self.edit = QPushButton(); self.edit.clicked.connect(self.edit_rules); actions.addWidget(self.edit)
        layout.addLayout(actions)
        self.summary = QLabel(); self.summary.setObjectName('summary'); layout.addWidget(self.summary)
        middle = QHBoxLayout()
        sidebar = QWidget(); sidebar.setFixedWidth(205); self.sidebar = QVBoxLayout(sidebar); self.sidebar.setContentsMargins(0, 0, 12, 0)
        self.category_title = QLabel(); self.category_title.setObjectName('eyebrow'); self.sidebar.addWidget(self.category_title)
        self.check_container = QWidget(); self.check_layout = QVBoxLayout(self.check_container); self.check_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar.addWidget(self.check_container); self.sidebar.addStretch()
        self.offline = QLabel(); self.offline.setObjectName('eyebrow'); self.offline.setWordWrap(True); self.sidebar.addWidget(self.offline)
        middle.addWidget(sidebar)
        preview_layout = QVBoxLayout()
        self.preview_title = QLabel(); self.preview_title.setObjectName('eyebrow'); preview_layout.addWidget(self.preview_title)
        self.table = QTableWidget(0, 6); self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setItemDelegate(FileDelegate(self.table))
        self.table.setMouseTracking(True)
        self.table.cellEntered.connect(self.preview_hover)
        self.table.verticalHeader().hide(); self.table.setWordWrap(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 180); self.table.setColumnWidth(1, 55); self.table.setColumnWidth(2, 80)
        self.table.setColumnWidth(3, 150); self.table.setColumnWidth(4, 230)
        self.table.itemChanged.connect(self.item_changed)
        preview_layout.addWidget(self.table); middle.addLayout(preview_layout, 1); layout.addLayout(middle, 1)
        self.progress = QProgressBar(); self.progress.setTextVisible(False); self.progress.setValue(0); layout.addWidget(self.progress)
        self.status = QLabel(); self.status.setWordWrap(True); self.status.setTextFormat(Qt.PlainText); layout.addWidget(self.status)
        self.details = QTextEdit(); self.details.setReadOnly(True); self.details.setMaximumHeight(100); self.details.hide(); layout.addWidget(self.details)
        footer = QHBoxLayout()
        self.undo_button = QPushButton(); self.undo_button.clicked.connect(self.undo); footer.addWidget(self.undo_button); footer.addStretch()
        self.cancel = QPushButton(); self.cancel.clicked.connect(self.cancel_task); footer.addWidget(self.cancel)
        self.organize = QPushButton(); self.organize.setObjectName('primary'); self.organize.clicked.connect(self.organize_files); footer.addWidget(self.organize)
        layout.addLayout(footer)
        self.retranslate(); self.set_busy(False)
    def t(self, key, **values):
        return tr(key, self.settings.language, **values)
    def retranslate(self):
        for widget, key in [(self.tagline,'tagline'), (self.choose,'choose'), (self.refresh,'refresh'),
            (self.edit,'rules'), (self.category_title,'categories'), (self.preview_title,'preview'),
            (self.offline,'offline'), (self.cancel,'cancel'), (self.organize,'organize'), (self.undo_button,'undo')]:
            widget.setText(self.t(key))
        self.table.setHorizontalHeaderLabels([self.t(k) for k in ('file','type','size','current','target','status')])
        self.path_label.setText(self.settings.folder or self.t('drop'))
        self.status.clear()
        self.help_button.setToolTip(self.t('help_title'))
        self.help_button.setAccessibleName(self.t('help_title'))
        self.language.setAccessibleName(self.t('language'))
        self.render()
    def change_language(self, index):
        self.settings.language = 'es' if index else 'en'
        self.save_settings(); self.retranslate()
    def save_settings(self):
        try:
            self.settings.save()
        except OSError as exc:
            self.show_error(str(exc))
    def set_busy(self, busy):
        for widget in (self.choose, self.refresh, self.edit, self.language, self.table, self.check_container):
            widget.setEnabled(not busy)
        self.refresh.setEnabled(not busy and bool(self.settings.folder))
        self.organize.setEnabled(not busy and self.plan is not None and not self.plan.cancelled and any(e.selected for e in self.plan.entries))
        self.cancel.setEnabled(busy)
        available = False
        if not busy:
            try:
                journal = Journal(self.journal_path)
                available = journal.latest() is not None
                journal.close()
            except Exception as exc:
                self.show_error(str(exc))
        self.undo_button.setEnabled(not busy and available)
    def pick_folder(self):
        folder = QFileDialog.getExistingDirectory(self, self.t('choose'), self.settings.folder)
        if folder:
            self.set_folder(folder)
    def set_folder(self, folder):
        if self.task is not None:
            return
        self.settings.folder = str(Path(folder))
        self.save_settings(); self.path_label.setText(self.settings.folder); self.scan()
    def scan(self):
        if self.settings.folder and self.task is None:
            self.plan = None; self.render()
            self.start_task('scan', (self.settings.folder, self.settings.rules))
    def start_task(self, mode, payload):
        self.mode = mode
        self.task = Task(mode, payload, self.journal_path, self)
        self.task.result.connect(self.received)
        self.task.failed.connect(self.show_error)
        self.task.progress.connect(self.update_progress)
        self.task.finished.connect(self.task_finished)
        self.set_busy(True)
        self.progress.setRange(0, 0)
        self.status.setText(self.t('busy_' + mode)); self.details.clear(); self.details.hide()
        self.task.start()
    def update_progress(self, value, total):
        self.progress.setRange(0, max(total, 1)); self.progress.setValue(value)
    def received(self, result):
        if self.mode == 'scan':
            self.plan = result; self.render()
            self.status.setText(self.t('scan_cancelled') if result.cancelled else '')
        else:
            self.plan = None; self.render()
            text = self.t('done', completed=result.completed, skipped=result.skipped, errors=len(result.errors))
            if result.cancelled:
                text = self.t('partial') + text
            elif self.mode == 'undo' and result.errors:
                text = self.t('partial_undo') + text
            self.status.setText(text)
            if result.errors:
                self.details.setPlainText('\n'.join(f'{name}: {self.t(reason)}' for name, reason in result.errors))
                self.details.show()
    def task_finished(self):
        task = self.task; self.task = None
        self.progress.setRange(0, 100); self.progress.setValue(100)
        self.set_busy(False)
        task.deleteLater()
    def cancel_task(self):
        if self.task:
            self.task.cancelled.set(); self.cancel.setEnabled(False); self.status.setText(self.t('cancelling'))
    def show_error(self, message):
        self.plan = None; self.render()
        self.status.setText(self.t('error') + ': ' + self.t(message))
    def render(self):
        self.table.blockSignals(True)
        entries = self.plan.entries if self.plan else []
        self.table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            values = [entry.source.name, entry.source.suffix.upper().lstrip('.'), size_text(entry.size),
                str(entry.source.parent), str(entry.target.relative_to(self.plan.root)) if entry.target else '—',
                self.t('excluded' if entry.identity and not entry.selected else entry.status)]
            for column, text in enumerate(values):
                item = QTableWidgetItem(text); item.setToolTip(str(entry.target) if column == 4 and entry.target else text)
                if column == 0 and entry.identity:
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(Qt.Checked if entry.selected else Qt.Unchecked)
                if column == 5:
                    item.setForeground(QColor(ACCENT if entry.selected else MUTED))
                self.table.setItem(row, column, item)
        self.table.blockSignals(False)
        self.summary.setText(self.t('summary', count=len(entries), size=size_text(sum(e.size for e in entries)), selected=sum(e.selected for e in entries)))
        while self.check_layout.count():
            self.check_layout.takeAt(0).widget().deleteLater()
        self.category_checks.clear()
        for rule in self.settings.rules:
            category_entries = [e for e in entries if e.category == rule.name and e.identity]
            count = len(category_entries)
            check = CategoryCheckBox(f'{self.t(rule.name)}  {count}')
            check.setProperty('category', rule.name)
            check.setAccessibleName(self.t(rule.name))
            check.setToolTip(rule.name)
            check.setTristate(True)
            selected = sum(e.selected for e in category_entries)
            check.setCheckState(Qt.Unchecked if not selected else Qt.Checked if selected == count else Qt.PartiallyChecked)
            check.setEnabled(count > 0)
            check.stateChanged.connect(lambda state, name=rule.name: self.toggle_category(name, state))
            self.check_layout.addWidget(check); self.category_checks.append(check)
    def preview_hover(self, row, column):
        item = self.table.item(row, column)
        enabled = item is not None and bool(item.flags() & Qt.ItemIsUserCheckable)
        self.table.viewport().setCursor(Qt.PointingHandCursor if enabled else Qt.ArrowCursor)
    def update_selection(self):
        """Update states in place: keep the active item, scroll, and keyboard focus."""
        if not self.plan:
            return
        self.table.blockSignals(True)
        try:
            for row, entry in enumerate(self.plan.entries):
                if entry.identity:
                    name = self.table.item(row, 0)
                    name.setCheckState(Qt.Checked if entry.selected else Qt.Unchecked)
                    state = self.table.item(row, 5)
                    state.setText(self.t(entry.status if entry.selected else 'excluded'))
                    state.setToolTip(state.text())
                    state.setForeground(QColor(ACCENT if entry.selected else MUTED))
        finally:
            self.table.blockSignals(False)
        entries = self.plan.entries
        self.summary.setText(self.t('summary', count=len(entries), size=size_text(sum(e.size for e in entries)), selected=sum(e.selected for e in entries)))
        for check in self.category_checks:
            files = [e for e in entries if e.category == check.property('category') and e.identity]
            selected = sum(e.selected for e in files)
            check.blockSignals(True)
            check.setCheckState(Qt.Unchecked if not selected else Qt.Checked if selected == len(files) else Qt.PartiallyChecked)
            check.blockSignals(False)
        self.organize.setEnabled(self.task is None and not self.plan.cancelled and any(e.selected for e in entries))
    def item_changed(self, item):
        if self.plan and item.column() == 0 and self.plan.entries[item.row()].identity:
            self.plan.entries[item.row()].selected = item.checkState() == Qt.Checked
            self.update_selection()
    def toggle_category(self, name, state):
        if self.plan:
            for entry in self.plan.entries:
                if entry.category == name and entry.identity:
                    entry.selected = state != Qt.Unchecked.value
            self.update_selection()
    def show_help(self):
        HelpDialog(self.settings.language, self).exec()
    def edit_rules(self):
        dialog = RuleDialog(self.settings.rules, self.settings.language, self)
        if dialog.exec() == QDialog.Accepted:
            self.settings.rules = dialog.rules; self.save_settings()
            self.plan = None; self.render(); self.set_busy(False); self.scan()
    def confirm(self, text):
        box = QMessageBox(QMessageBox.Question, self.t('confirm'), text, parent=self)
        yes = box.addButton(self.t('yes'), QMessageBox.AcceptRole)
        no = box.addButton(self.t('no'), QMessageBox.RejectRole)
        box.setDefaultButton(no); box.exec()
        return box.clickedButton() == yes
    def organize_files(self):
        if self.plan and self.task is None and not self.plan.cancelled:
            count = sum(e.selected for e in self.plan.entries)
            if count and self.confirm(self.t('confirm_move', count=count, root=self.plan.root)):
                self.start_task('move', self.plan)
    def undo(self):
        journal = Journal(self.journal_path)
        operation = journal.latest()
        root = journal.root(operation) if operation else None
        journal.close()
        if root and self.task is None and self.confirm(self.t('confirm_undo', root=root)):
            self.start_task('undo', None)
    def dragEnterEvent(self, event):
        if self.task is None and event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1 and urls[0].isLocalFile() and Path(urls[0].toLocalFile()).is_dir():
                event.acceptProposedAction()
    def dropEvent(self, event):
        if self.task is None:
            urls = event.mimeData().urls()
            if len(urls) == 1 and urls[0].isLocalFile() and Path(urls[0].toLocalFile()).is_dir():
                self.set_folder(urls[0].toLocalFile()); event.acceptProposedAction()
    def closeEvent(self, event):
        if self.task is not None:
            self.status.setText(self.t('close_busy')); event.ignore()
        else:
            self.save_settings(); event.accept()
