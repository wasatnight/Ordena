# Validation / Verificación

Date: 2026-10-23. Windows development environment, Python 3.12.14 x64, PySide6 6.10.2, PyInstaller 6.19.0.

## Automated tests

`python -m unittest discover -s tests -v`: **35 tests run, 33 passed, 2 skipped, no failures** in the local sandbox. All input files were synthetic files in temporary directories; personal folders were never organized.

Coverage includes all six default categories; mixed-case extensions; spaces, accents, CJK and emoji names; preview without filesystem changes; existing categories; collision names; new conflicts after preview; atomic no-overwrite behavior; unknown files; temporary/incomplete files and shortcuts; hidden/system attributes; blocked/disappeared/modified files; same-size and restored-mtime content changes; exclusions; protected paths; unsafe destination paths; directory locking; cancellation of scan, organization and undo; persistent preferences; undo conflicts and retry; modified/replaced destinations; content preservation; and interrupted move/undo recovery.

Crash recovery includes a real child process that writes its intent, performs a Windows handle rename and exits immediately with `os._exit(17)` before recording completion. The parent reopens the journal and restores the file. No fault was injected into personal data.

Eight Qt interface tests exercise English default, persistent Spanish selection, translated headings, preserved physical destinations and exclusions, category selection, rule editing, invalidation on folder change, background work, confirmation flow, organization, summary, undo, refresh and scan cancellation.

The two skipped tests require actual hard-link and junction creation. The sandbox returned access denied or disallowed creation. Attribute checks and other link-related exclusions are implemented, but those two end-to-end cases require another Windows environment.

## Build and visual checks

- Source startup smoke test succeeded with a separate data directory.
- English and Spanish Qt window captures inspected for layout/readability. Assets use synthetic sample files.
- PyInstaller successfully generated `dist/Ordena/Ordena.exe` and its shared-library directory on Windows.
- A standalone executable startup attempt in this sandbox timed out without producing its expected local journal. A successful executable startup is **not yet confirmed** here. No security settings were changed or bypassed.
- The Windows CI workflow builds and checks startup in an independent Windows runner. Its results should be consulted before calling the portable build verified.

## Remaining checks

Clean Windows installation; actual hard links/junctions where creation is allowed; very large folders and files; external/network filesystems; accessibility; installer; Authenticode signing. The portable build is unsigned. Cancellation waits for the current file's checksum/move before stopping future files.

The source code and dependencies run locally without network access. Downloading dependencies and using GitHub/CI require network access during development.
