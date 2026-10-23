# Validation — Ordena 1.1.1

Date: 2026-10-23. Windows, Python 3.12, PySide6 6.10.2, PyInstaller 6.19.0.

## Scope

Visual correction only: pale pink backgrounds throughout the app, blue text, matching menu/control/help colors and a shorter localized subtitle. Layout, original application ICO, selection behavior, rules, execution, journal and undo are preserved.

The suite remains 44 tests: 27 filesystem safety checks and 17 Qt interface checks. The existing language tests additionally assert the exact new subtitles. All 17 interface tests passed locally; English/Spanish main windows and help were rendered and visually checked.

The Windows pipeline checks all 44 tests, the original nine executable ICO frames, startup without Python on PATH, version 1.1.1 and actual loading of packaged icon resources. Version 1.1.0 baseline: https://github.com/wasatnight/Ordena/actions/runs/39935344875.

## Independent Windows result: passed

All 44 tests passed with no skips or failures in 21.087 seconds. Packaging, all nine embedded original icon images, startup without Python on PATH, version 1.1.1 and loading of packaged icon resources passed.

- Run: https://github.com/wasatnight/Ordena/actions/runs/39937427950
- Tested application source commit: `60eaa418b4a8731eea3fd71829257811ce200e70`.
- Verified artifact ID: 12493209908.
- Original artifact SHA-256: `e4f0c5d8d38989772baedc29307ac4539c13bef1c82cf16610d0b59fa38aaaf5`.

The portable delivery repackages that verified artifact under an Ordena folder and refreshes documentation only. Original executable, libraries and resources remain byte-identical. Report-only commits after the tested source do not change the application.

## Remaining distribution work

Installer and Authenticode signing; manual testing on another personal Windows installation; actual symbolic links and more filesystem variants; very large-folder/accessibility evaluation. All development inputs are synthetic temporary files. User files and preferences/history remain untouched during testing.
