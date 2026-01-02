# Windows 9x Installer

## Supported OS
- Windows 95, 98, ME

## Binary
- `DominiumSetup-win9x.exe`

## UI modes
- GUI (default)
- TUI (`--tui`)
- CLI (`--cli`)

## CLI usage
```
DominiumSetup-win9x.exe --cli --install --manifest MANIFESTS\dominium_legacy.dsumanifest --payload-root .
DominiumSetup-win9x.exe --cli --repair --install-root "C:\Program Files\Dominium"
DominiumSetup-win9x.exe --cli --uninstall --state "C:\Program Files\Dominium\dominium_state.dsus"
DominiumSetup-win9x.exe --cli --verify --state "C:\Program Files\Dominium\dominium_state.dsus"
```

Options:
- `--install-root PATH`
- `--manifest PATH`
- `--payload-root PATH`
- `--state PATH`
- `--log PATH`
- `--component <id>` (repeatable)
- `--exclude <id>` (repeatable)
- `--scope portable|user|system`
- `--platform <triple>` (default `win32-9x-x86`)

## Default paths
- Install root: `C:\Program Files\Dominium`
- State: `C:\Program Files\Dominium\dominium_state.dsus`
- Log: `C:\Program Files\Dominium\dominium_install.log`

## Notes and limitations
- ANSI-only paths; avoid Unicode or long path edge cases.
- Shell integration beyond file copy is minimal.

## Emulator testing (PCem/86Box)
1) Install Windows 95/98/ME and mount the installer directory.
2) Run `DominiumSetup-win9x.exe` (GUI) or `--tui` in a DOS box.
3) Verify state/log output under the install root.
4) Run `--verify` and `--uninstall` to validate lifecycle.
