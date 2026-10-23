"""Filesystem guards and Windows handle-based no-replace renames."""
import ctypes
import hashlib
import os
from pathlib import Path
import stat

UNSAFE_ATTRIBUTES = 0x2 | 0x4 | 0x400
TEMP_EXTENSIONS = {'.part', '.partial', '.crdownload', '.tmp', '.download', '.temp'}
LINK_EXTENSIONS = {'.lnk', '.url', '.website', '.library-ms', '.search-ms', '.pif'}

def unsafe(path):
    info = path.lstat()
    return bool(getattr(info, 'st_file_attributes', 0) & UNSAFE_ATTRIBUTES or stat.S_ISLNK(info.st_mode))

def safe_directory(path):
    path = Path(os.path.abspath(path))
    for ancestor in [path, *path.parents]:
        if (ancestor.lstat().st_file_attributes & 0x400 or ancestor.is_symlink() or not ancestor.is_dir()
                or (ancestor == path and ancestor != Path(ancestor.anchor) and unsafe(ancestor))):
            raise ValueError('unsafe_folder')
    return path

def validate_root(path):
    path = safe_directory(path)
    if path == Path(path.anchor):
        raise ValueError('unsafe_folder')
    for item in filter(None, [os.environ.get(k) for k in ('WINDIR', 'ProgramFiles', 'ProgramFiles(x86)', 'ProgramData')]):
        protected = Path(os.path.abspath(item))
        if path == protected or protected in path.parents:
            raise ValueError('unsafe_folder')
    if path.parts[1:2] and path.parts[1].casefold() in {
        'windows', 'program files', 'program files (x86)', 'programdata',
        '$recycle.bin', 'system volume information', 'recovery'}:
        raise ValueError('unsafe_folder')
    return path

def fingerprint(path, digest=False):
    info = path.lstat()
    if unsafe(path) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ValueError('unsafe_file')
    result = [info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns]
    if digest:
        with path.open('rb') as stream:
            result.append(hashlib.file_digest(stream, 'sha256').hexdigest())
        if result[:4] != fingerprint(path):
            raise ValueError('changed')
    return result

def destination(root, path):
    root = validate_root(root)
    path = Path(os.path.abspath(path))
    if path.parent.parent != root or path.name in {'', '.', '..'}:
        raise ValueError('unsafe_folder')
    if path.parent.exists() or path.parent.is_symlink():
        safe_directory(path.parent)
    return path

def rename_checked(source, target, expected):
    """Lock against writers/deleters; verify identity and hash; rename by handle.

    FileRenameInfo.ReplaceIfExists=False prevents overwrites atomically.
    DirectoryLock prevents directory replacements during moves.
    """
    if os.name != 'nt':
        raise OSError('Windows is required for safe file moves')
    import msvcrt
    from ctypes import wintypes
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
        ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.SetFileInformationByHandle.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    kernel.SetFileInformationByHandle.restype = wintypes.BOOL
    handle = kernel.CreateFileW(str(source), 0x80000000 | 0x10000, 1, None, 3, 0x00200000, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    fd = None
    try:
        fd = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
        info = os.fstat(fd)
        if [info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns] != expected[:4]:
            raise ValueError('changed')
        with os.fdopen(os.dup(fd), 'rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        if digest != expected[4] or fingerprint(source) != expected[:4]:
            raise ValueError('changed')
        class RenameInfo(ctypes.Structure):
            _fields_ = [('ReplaceIfExists', wintypes.BOOLEAN), ('RootDirectory', wintypes.HANDLE),
                ('FileNameLength', wintypes.DWORD), ('FileName', wintypes.WCHAR * 1)]
        data = RenameInfo()
        data.ReplaceIfExists = False
        encoded = str(target).encode('utf-16-le')
        data.FileNameLength = len(encoded)
        buffer = ctypes.create_string_buffer(max(ctypes.sizeof(data), RenameInfo.FileName.offset + len(encoded) + 2))
        ctypes.memmove(buffer, ctypes.byref(data), RenameInfo.FileName.offset)
        ctypes.memmove(ctypes.addressof(buffer) + RenameInfo.FileName.offset, encoded, len(encoded))
        if not kernel.SetFileInformationByHandle(handle, 3, buffer, len(buffer)):
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        if fd is not None:
            os.close(fd)
        else:
            kernel.CloseHandle(handle)

class DirectoryLock:
    """Open directories without FILE_SHARE_DELETE for the operation lifetime."""
    def __init__(self, paths):
        self.paths, self.handles = paths, []
    def __enter__(self):
        if os.name != 'nt':
            raise OSError('Windows is required')
        from ctypes import wintypes
        self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        self.kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
            ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        self.kernel.CreateFileW.restype = wintypes.HANDLE
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        try:
            for path in self.paths:
                for part in reversed([Path(path), *Path(path).parents]):
                    handle = self.kernel.CreateFileW(str(part), 1, 3, None, 3, 0x02000000 | 0x00200000, None)
                    if handle == ctypes.c_void_p(-1).value:
                        raise ctypes.WinError(ctypes.get_last_error())
                    self.handles.append(handle)
                safe_directory(path)
        except BaseException:
            self.__exit__(None, None, None)
            raise
        return self
    def __exit__(self, *args):
        for handle in reversed(self.handles):
            self.kernel.CloseHandle(handle)
        self.handles.clear()


