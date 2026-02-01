Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# UI Handoff Notes

This repo now includes stub GUI/TUI entrypoints for launcher and setup so UI
design work can begin without touching backend logic.

## Expectations for UI Designers
- Use Visual Studio designers (Win32/WPF/WinUI) or platform-native tooling.
- Keep backend calls confined to launcher/setup public APIs.
- Avoid direct includes of engine internal headers.
- Treat current GUI/TUI entrypoints as stable integration points.

## Next Steps (Planned)
- Replace `launcher/gui/launcher_gui_stub.c` and `setup/gui/dsu_gui_stub.c`
  with platform-specific GUI frontends.
- Bind UI events to launcher/setup core interfaces, not engine internals.
- Keep CLI and backend stubs intact to preserve headless build/test paths.