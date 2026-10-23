import os
import sys
from pathlib import Path
from PySide6.QtCore import QStandardPaths, QLockFile, QTimer
from PySide6.QtWidgets import QApplication, QMessageBox
from ordena.ui import Window

def main():
    app = QApplication(sys.argv)
    app.setApplicationName('Ordena'); app.setOrganizationName('IvanSolano')
    directory = Path(os.environ.get('ORDENA_DATA_DIR') or QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation))
    directory.mkdir(parents=True, exist_ok=True)
    lock = QLockFile(str(directory / 'ordena.lock')); lock.setStaleLockTime(0)
    if not lock.tryLock(0):
        QMessageBox.information(None, 'Ordena', 'Ordena is already open. / Ordena ya está abierto.')
        return 1
    window = Window(directory); window.show()
    if '--smoke-test' in sys.argv:
        QTimer.singleShot(900, app.quit)
    result = app.exec(); lock.unlock()
    return result

if __name__ == '__main__':
    raise SystemExit(main())
