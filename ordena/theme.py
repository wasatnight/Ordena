"""Shared blush theme and packaged resources."""
from pathlib import Path
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

ASSETS = Path(__file__).resolve().parent / 'assets'
ACCENT = '#f4e1e9'


def configure_app():
    app = QApplication.instance()
    if app and not app.property('ordena_theme'):
        app.setStyle('Fusion')
        palette = app.palette()
        for role, color in [(QPalette.Window, '#101a24'), (QPalette.WindowText, '#e8edf5'),
                (QPalette.Base, '#14222e'), (QPalette.AlternateBase, '#182a38'),
                (QPalette.Text, '#e8edf5'), (QPalette.Button, '#223444'),
                (QPalette.ButtonText, '#e8edf5'), (QPalette.Highlight, ACCENT),
                (QPalette.HighlightedText, '#302934'), (QPalette.ToolTipBase, '#243444'),
                (QPalette.ToolTipText, '#f4e1e9')]:
            palette.setColor(role, QColor(color))
        app.setPalette(palette)
        app.setProperty('ordena_theme', True)


STYLE = '''
QWidget { background: #101a24; color: #e8edf5; font-family: 'Segoe UI'; font-size: 10pt; }
QLabel#brand { font-size: 32pt; font-weight: 700; color: #f4e1e9; }
QLabel#subtitle { font-size: 10pt; font-weight: 700; color: #f4e1e9; }
QLabel#eyebrow { color: #a6b2c2; font-size: 9pt; font-weight: 600; }
QLabel#path { background: #172533; border: 1px dashed #526073; border-radius: 12px; padding: 20px; font-size: 11pt; }
QLabel#summary { color: #f4e1e9; padding: 6px 0; font-size: 12pt; font-weight: 600; }
QPushButton, QComboBox { background: #223444; border: 1px solid #435366; border-radius: 8px; padding: 9px 14px; }
QPushButton:hover, QComboBox:hover { background: #304052; border-color: #f4e1e9; }
QPushButton:pressed { background: #574751; border-color: #f4e1e9; }
QPushButton:focus, QComboBox:focus { border: 1px solid #f4e1e9; }
QPushButton:disabled, QComboBox:disabled { color: #7e93a4; background: #1a2835; border-color: #2c3d4d; }
QPushButton#primary { background: #f4e1e9; color: #302934; font-weight: 700; padding: 11px 27px; }
QPushButton#primary:hover { background: #fff3f8; }
QPushButton#primary:pressed { background: #dcc0cf; }
QPushButton#primary:disabled { background: #514851; color: #aba4af; border-color: #514851; }
QPushButton#help { font-size: 13pt; font-weight: 700; padding: 0; border-radius: 18px; color: #f4e1e9; }
QComboBox { padding: 7px 30px 7px 12px; }
QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 26px; border: none; }
QComboBox::down-arrow { image: url(@ASSETS@/chevron.svg); width: 16px; height: 16px; }
QComboBox QAbstractItemView { background: #1c2b39; color: #e8edf5; border: 1px solid #6f6170; selection-background-color: #f4e1e9; selection-color: #302934; outline: 0; padding: 4px; }
QComboBox QAbstractItemView::item { min-height: 30px; padding: 5px 10px; }
QTableWidget { background: #14222e; alternate-background-color: #182a38; border: 1px solid #354557; border-radius: 8px; gridline-color: #293c4c; }
QTableWidget::item { padding: 6px; border: 0; }
QTableWidget::item:hover { background: #30303f; }
QTableWidget::item:selected { background: #443744; color: #fff3f8; }
QHeaderView::section { background: #213442; color: #c3c9d5; padding: 10px; border: none; font-weight: 600; }
QProgressBar { background: #223444; border: 0; border-radius: 4px; height: 7px; text-align: center; }
QProgressBar::chunk { background: #f4e1e9; border-radius: 4px; }
QTextEdit, QTextBrowser { background: #14222e; border: 1px solid #354557; border-radius: 8px; padding: 10px; }
QScrollArea { border: 0; }
QCheckBox { spacing: 9px; padding: 8px 3px; border-radius: 6px; }
QCheckBox:hover { background: #30303f; }
QCheckBox:focus { background: #30303f; }
QCheckBox::indicator { width: 20px; height: 20px; }
QCheckBox::indicator:unchecked { image: url(@ASSETS@/check-off.svg); }
QCheckBox::indicator:checked { image: url(@ASSETS@/check-on.svg); }
QCheckBox::indicator:indeterminate { image: url(@ASSETS@/check-mixed.svg); }
QCheckBox::indicator:disabled { image: url(@ASSETS@/check-off.svg); }
QCheckBox:disabled { color: #7e93a4; }
QScrollBar:vertical { background: #14222e; width: 12px; margin: 0; }
QScrollBar::handle:vertical { background: #596272; border-radius: 5px; min-height: 28px; margin: 2px; }
QScrollBar::handle:vertical:hover { background: #cbb4c3; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
QToolTip { background: #253443; color: #fff3f8; border: 1px solid #cbb4c3; padding: 4px; }
'''.replace('@ASSETS@', ASSETS.as_posix())
