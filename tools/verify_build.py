"""Verify the Windows executable embeds our original multi-size ICO resources."""
from pathlib import Path
import struct
import sys
import pefile


def verify(executable):
    icon = (Path(__file__).resolve().parents[1] / 'ordena/assets/app.ico').read_bytes()
    count = struct.unpack_from('<H', icon, 4)[0]
    expected = []
    for index in range(count):
        size, offset = struct.unpack_from('<II', icon, 6 + index * 16 + 8)
        expected.append(icon[offset:offset + size])
    pe = pefile.PE(str(executable))
    images = []
    for resource in pe.DIRECTORY_ENTRY_RESOURCE.entries:
        if resource.id == 3:  # RT_ICON
            for entry in resource.directory.entries:
                for language in entry.directory.entries:
                    item = language.data.struct
                    images.append(pe.get_data(item.OffsetToData, item.Size))
    if sorted(images) != sorted(expected):
        raise AssertionError('Executable icon differs from the original multi-size app ICO')
    print(f'Windows executable contains all {count} original icon images.')
    pe.close()


if __name__ == '__main__':
    verify(Path(sys.argv[1]))
