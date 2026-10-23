import os
import json
import sys
from pathlib import Path
from PySide6.QtCore import QStandardPaths, QLockFile, QTimer
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QIcon
from ordena import __version__
from ordena.theme import ASSETS
from ordena.ui import Window

def main():
    if os.name == 'nt':
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('IvanSolano.Ordena')
    app = QApplication(sys.argv)
    app.setApplicationVersion(__version__)
    app.setWindowIcon(QIcon(str(ASSETS / 'app.ico')))
    app.setApplicationName('Ordena'); app.setOrganizationName('IvanSolano')
    directory = Path(os.environ.get('ORDENA_DATA_DIR') or QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation))
    directory.mkdir(parents=True, exist_ok=True)
    lock = QLockFile(str(directory / 'ordena.lock')); lock.setStaleLockTime(0)
    if not lock.tryLock(0):
        QMessageBox.information(None, 'Ordena', 'Ordena is already open. / Ordena ya está abierto.')
        return 1
    window = Window(directory); window.show()
    if '--smoke-test' in sys.argv:
        icons = ['app.ico', 'check-on.svg', 'check-off.svg', 'check-mixed.svg', 'chevron.svg']
        loaded = all(not QIcon(str(ASSETS / name)).pixmap(32, 32).isNull() for name in icons)
        if not loaded or window.windowIcon().isNull():
            raise RuntimeError('Packaged icon resources are missing')
        (directory / 'smoke.json').write_text(json.dumps({'version': __version__, 'icons_loaded': loaded,
            'language': window.settings.language}), encoding='utf-8')
        QTimer.singleShot(900, app.quit)
    result = app.exec(); lock.unlock()
    return result

if __name__ == '__main__':
    raise SystemExit(main())
