"""Render our original SVG as PNG and a Windows ICO with nine sizes."""
from pathlib import Path
import struct
from PySide6.QtCore import QByteArray, QBuffer, QIODevice, Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer


def main():
    app = QGuiApplication.instance() or QGuiApplication([])
    assets = Path(__file__).resolve().parents[1] / 'ordena/assets'
    renderer = QSvgRenderer(str(assets / 'app.svg'))
    if not renderer.isValid():
        raise ValueError('Invalid app SVG')
    sizes = [16, 20, 24, 32, 40, 48, 64, 128, 256]
    frames = []
    for size in sizes:
        image = QImage(size, size, QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        renderer.render(painter)
        painter.end()
        data = QByteArray()
        buffer = QBuffer(data)
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, 'PNG')
        frames.append(bytes(data))
        if size == 256:
            image.save(str(assets / 'app-icon.png'))
    offset = 6 + 16 * len(sizes)
    directory = bytearray(struct.pack('<HHH', 0, 1, len(sizes)))
    for size, data in zip(sizes, frames):
        directory += struct.pack('<BBBBHHII', size % 256, size % 256, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    (assets / 'app.ico').write_bytes(directory + b''.join(frames))
    print('Generated icon sizes:', sizes)


if __name__ == '__main__':
    main()
