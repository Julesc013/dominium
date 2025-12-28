# Windows Legacy Installer Matrix

This matrix covers the deep-legacy Windows installer suite (DOS/Win16/Win9x).
All installers emit a legacy invocation subset and write DSUS installed-state
files that are compatible with modern importer/launcher expectations (skip-unknown).

| OS family | Installer binary | UI modes | Operations | Notes |
| --- | --- | --- | --- | --- |
| MS-DOS 5/6/7 | `INSTALL.EXE` | TUI, CLI | install, repair, verify, uninstall | Portable scope only; archive payloads only (`*.dsuarch`). |
| Windows 3.0–3.11 | `SETUP.EXE` | GUI, CLI | install, repair, verify, uninstall | Win16 dialog UI; component list in GUI; archive payloads only. |
| Windows 95/98/ME | `DominiumSetup-win9x.exe` | GUI, TUI, CLI | install, upgrade, repair, verify, uninstall | ANSI-only paths; default `C:\Program Files\Dominium`. |

Installed-state path (all legacy installers):
- `<install_root>\dominium_state.dsus`

Logs (all legacy installers):
- `<install_root>\dominium_install.log`

Legacy invocation subset fields:
- operation, scope, platform_triple, install_root, component list, policy flags (deterministic + legacy_mode).
