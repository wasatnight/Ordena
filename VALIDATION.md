# Validation / Verificación

Date: 2026-10-23. Windows development environment, Python 3.12.14 x64, PySide6 6.10.2, PyInstaller 6.19.0.

## Automated tests

`python -m unittest discover -s tests -v`: **35 tests run, 33 passed, 2 skipped, no failures** in the local sandbox. All input files were synthetic files in temporary directories; personal folders were never organized.

Coverage includes all six default categories; mixed-case extensions; spaces, accents, CJK and emoji names; preview without filesystem changes; existing categories; collision names; new conflicts after preview; atomic no-overwrite behavior; unknown files; temporary/incomplete files and shortcuts; hidden/system attributes; blocked/disappeared/modified files; same-size and restored-mtime content changes; exclusions; protected paths; unsafe destination paths; directory locking; cancellation of scan, organization and undo; persistent preferences; undo conflicts and retry; modified/replaced destinations; content preservation; and interrupted move/undo recovery.

Crash recovery includes a real child process that writes its intent, performs a Windows handle rename and exits immediately with `os._exit(17)` before recording completion. The parent reopens the journal and restores the file. No fault was injected into personal data.

Eight Qt interface tests exercise English default, persistent Spanish selection, translated headings, preserved physical destinations and exclusions, category selection, rule editing, invalidation on folder change, background work, confirmation flow, organization, summary, undo, refresh and scan cancellation.

The two locally skipped tests require actual hard-link and junction creation. Both passed on the independent Windows GitHub Actions runner: **35 tests passed, no skips, no failures**, using Python 3.12.10.

## Build and visual checks

- Source startup smoke test succeeded with a separate data directory.
- English and Spanish Qt window captures inspected for layout/readability. Assets use synthetic sample files.
- PyInstaller successfully generated `dist/Ordena/Ordena.exe` and its shared-library directory on Windows.
- A standalone executable startup attempt in this sandbox timed out without producing its expected local journal. A successful executable startup is **not yet confirmed** here. No security settings were changed or bypassed.
- Independent Windows CI succeeded: all 35 tests passed, packaging succeeded, and the executable initialized its UI/journal and exited successfully with Python removed from PATH. The delivered portable ZIP is the artifact built and verified by that runner. Run: https://github.com/wasatnight/Ordena/actions/runs/39929305957 (commit 78bd360e7aeff43e846ca26522226c34d37be977).

## Remaining checks

Interactive testing on a separate personal Windows installation; actual symbolic links; very large folders and files; external/network filesystems; accessibility; installer; Authenticode signing. The portable build is unsigned. Cancellation waits for the current file's checksum/move before stopping future files.

The source code and dependencies run locally without network access. Downloading dependencies and using GitHub/CI require network access during development.


Portable provenance: the delivered archive repackages the verified CI artifact with updated README/validation documents; executable and DLL bytes are unchanged. Original CI artifact SHA-256: a8bd5efaaada4d42e02c61e306505db0ead9f57b0368c936ef44fc37d3dfac8c.
