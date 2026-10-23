# Validation — Ordena 1.1.0

Date: 2026-10-23. Windows, Python 3.12, PySide6 6.10.2, PyInstaller 6.19.0.

## Scope and local verification

44 tests: 27 filesystem safety tests and 17 Qt interface tests. The original 35-test Windows baseline passed at https://github.com/wasatnight/Ordena/actions/runs/39929305957.

The 1.1.0 interface tests passed locally, including nine new checks: real mouse clicks on a file name and checkbox; Space-key toggling; preserved scroll and table item identity; partial category selection followed by all/none clicks; centered brand/subtitle with matching font; opening bilingual help through the ? button; multi-size window icon; and actual selection through the styled language popup.

The local full suite has two environment-specific skips: hard-link and junction creation are denied in the sandbox. Those cases are included in independent Windows CI. Tests only use synthetic files in temporary directories; personal folders are never organized.

## Packaging checks

The Windows build embeds the original nine ICO images (16, 20, 24, 32, 40, 48, 64, 128, 256 px). `tools/verify_build.py` compares the executable RT_ICON bytes with the source ICO frames. Runtime resources are bundled under `ordena/assets`. Startup without Python on PATH also confirms version 1.1.0 and actual rendering of every packaged icon resource through `smoke.json`.

English and Spanish source-window captures and the help dialog were inspected. The original mint accent and whole-row selection highlight are absent from the new preview; instructional copy is in the offline help dialog. File selection does not recreate table items or category controls.

Independent Windows results: see the final build linked from GitHub Actions: https://github.com/wasatnight/Ordena/actions. This report will be updated with its run and artifact provenance when complete.

## Remaining distribution work

Installer and Authenticode signing; manual testing on another personal Windows computer; actual symbolic links and more filesystem variants; large-folder/accessibility evaluation. Cancellation still waits for the current checksum/move. The app continues to run offline and remembers the same user settings/history location as 1.0.
