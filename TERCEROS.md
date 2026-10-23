# Terceros / Third-party components

Runtime dependencies: Python 3.12 (PSF license); PySide6, Shiboken6 and Qt 6.10.2 (LGPL/GPL/commercial options; see the upstream distribution's license files and component notices).

Build tools: PyInstaller 6.19.0 (GPL with its bootloader exception), pyinstaller-hooks-contrib, altgraph, packaging, pefile, pywin32-ctypes and setuptools. These are development dependencies, not application features.

The `third-party-licenses` directory contains the available installed wheel license metadata for the runtime dependencies, together with the Python license. The portable build keeps Qt as shared libraries in `_internal` rather than statically linking it. Preserve these notices when redistributing. Additional Qt component licensing details are maintained upstream:

- https://doc.qt.io/qtforpython-6/licenses.html
- https://doc.qt.io/qt-6/licenses-used-in-qt.html
- https://www.python.org/psf/license/
- https://pyinstaller.org/en/stable/license.html

Ordena's own source license remains for the author to select, independently of dependency licenses.
