"""Pale pink surfaces, blue text and packaged resources."""
from pathlib import Path
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

ASSETS = Path(__file__).resolve().parent / 'assets'
BACKGROUND = '#f4e1e9'
ACCENT = '#243b63'
MUTED = '#526783'
SELECTION = '#e6c5d5'


def configure_app():
    app = QApplication.instance()
    if app and not app.property('ordena_theme'):
        app.setStyle('Fusion')
        palette = app.palette()
        for role, color in [(QPalette.Window, BACKGROUND), (QPalette.WindowText, ACCENT),
                (QPalette.Base, '#fff7fa'), (QPalette.AlternateBase, '#f9ebf1'),
                (QPalette.Text, ACCENT), (QPalette.Button, '#efcfde'),
                (QPalette.ButtonText, ACCENT), (QPalette.Highlight, SELECTION),
                (QPalette.HighlightedText, ACCENT), (QPalette.ToolTipBase, '#fff7fa'),
                (QPalette.ToolTipText, ACCENT), (QPalette.PlaceholderText, MUTED),
                (QPalette.Light, '#fff7fa'), (QPalette.Midlight, '#f9ebf1'),
                (QPalette.Mid, '#c4a9ba'), (QPalette.Dark, '#a58ca0'),
                (QPalette.Shadow, '#a58ca0'), (QPalette.Link, '#315887'),
                (QPalette.LinkVisited, '#315887')]:
            palette.setColor(role, QColor(color))
        for role in (QPalette.WindowText, QPalette.Text, QPalette.ButtonText):
            palette.setColor(QPalette.Disabled, role, QColor('#69758a'))
        app.setPalette(palette)
        app.setProperty('ordena_theme', True)


STYLE = '''
QWidget { background: #f4e1e9; color: #243b63; font-family: 'Segoe UI'; font-size: 10pt; }
QLabel#brand { font-size: 32pt; font-weight: 700; color: #243b63; }
QLabel#subtitle { font-size: 10pt; font-weight: 700; color: #243b63; }
QLabel#eyebrow { color: #526783; font-size: 9pt; font-weight: 600; }
QLabel#path { background: #faedf3; border: 1px dashed #b49aaa; border-radius: 12px; padding: 20px; font-size: 11pt; }
QLabel#summary { color: #243b63; padding: 6px 0; font-size: 12pt; font-weight: 600; }
QPushButton, QComboBox { background: #efcfde; border: 1px solid #bba0b2; border-radius: 8px; padding: 9px 14px; }
QPushButton:hover, QComboBox:hover { background: #e8bed2; border-color: #526783; }
QPushButton:pressed { background: #dcaac2; border-color: #243b63; }
QPushButton:focus, QComboBox:focus { border: 1px solid #243b63; }
QPushButton:disabled, QComboBox:disabled { color: #69758a; background: #eadce5; border-color: #c9b7c4; }
QPushButton#primary { background: #e8bace; color: #243b63; font-weight: 700; padding: 11px 27px; border-color: #a8809a; }
QPushButton#primary:hover { background: #dfa8c2; }
QPushButton#primary:pressed { background: #d59ab7; }
QPushButton#primary:disabled { background: #eadce5; color: #69758a; border-color: #c9b7c4; }
QPushButton#help { font-size: 13pt; font-weight: 700; padding: 0; border-radius: 18px; color: #243b63; }
QComboBox { padding: 7px 30px 7px 12px; }
QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 26px; border: none; }
QComboBox::down-arrow { image: url(@ASSETS@/chevron.svg); width: 16px; height: 16px; }
QComboBox QAbstractItemView { background: #fff7fa; color: #243b63; border: 1px solid #bba0b2; selection-background-color: #e6c5d5; selection-color: #243b63; outline: 0; padding: 4px; }
QComboBox QAbstractItemView::item { min-height: 30px; padding: 5px 10px; }
QTableWidget { background: #fff7fa; alternate-background-color: #f9ebf1; border: 1px solid #c4a9ba; border-radius: 8px; gridline-color: #e4cdd9; }
QTableWidget::item { padding: 6px; border: 0; }
QTableWidget::item:hover { background: #edcfde; }
QTableWidget::item:selected { background: #e6c5d5; color: #243b63; }
QHeaderView::section { background: #ead0dd; color: #243b63; padding: 10px; border: none; font-weight: 600; }
QProgressBar { background: #ead0dd; border: 0; border-radius: 4px; height: 7px; text-align: center; }
QProgressBar::chunk { background: #b47f9b; border-radius: 4px; }
QTextEdit, QTextBrowser { background: #fff7fa; color: #243b63; border: 1px solid #c4a9ba; border-radius: 8px; padding: 10px; }
QScrollArea { border: 0; }
QCheckBox { spacing: 9px; padding: 8px 3px; border-radius: 6px; }
QCheckBox:hover, QCheckBox:focus { background: #edcfde; }
QCheckBox::indicator { width: 20px; height: 20px; }
QCheckBox::indicator:unchecked { image: url(@ASSETS@/check-off.svg); }
QCheckBox::indicator:checked { image: url(@ASSETS@/check-on.svg); }
QCheckBox::indicator:indeterminate { image: url(@ASSETS@/check-mixed.svg); }
QCheckBox::indicator:disabled { image: url(@ASSETS@/check-off.svg); }
QCheckBox:disabled { color: #69758a; }
QScrollBar:vertical { background: #faedf3; width: 12px; margin: 0; }
QScrollBar::handle:vertical { background: #c4a2b6; border-radius: 5px; min-height: 28px; margin: 2px; }
QScrollBar::handle:vertical:hover { background: #a87f99; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
QToolTip { background: #fff7fa; color: #243b63; border: 1px solid #bba0b2; padding: 4px; }
'''.replace('@ASSETS@', ASSETS.as_posix())
