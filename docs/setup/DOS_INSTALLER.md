# DOS Installer

## Supported OS
- MS-DOS 5/6
- MS-DOS 7.x (Windows 9x boot DOS)

## Distribution layout
Preferred: ZIP/floppy layout (period-correct).

```
INSTALL.EXE
MANIFESTS\dominium_legacy.dsumanifest
PAYLOADS\payload.dsuarch
DOCS\
```

Optional: single-file SFX built with `make_sfx.bat` / `make_sfx.sh` using a
`DSUX` footer (see `source/dominium/setup/installers/windows_legacy/dos/packaging`).

## Usage (TUI)
- `INSTALL.EXE /E` — Easy install
- `INSTALL.EXE /C` — Custom install
- `INSTALL.EXE /U` — Uninstall
- `INSTALL.EXE /V` — Verify
- `INSTALL.EXE /R` — Repair

## Usage (CLI)
```
INSTALL.EXE --install --manifest MANIFESTS\dominium_legacy.dsumanifest --payload-root .
INSTALL.EXE --repair --install-root C:\DOMINIUM --state C:\DOMINIUM\dominium_state.dsus
INSTALL.EXE --uninstall --state C:\DOMINIUM\dominium_state.dsus
INSTALL.EXE --verify --state C:\DOMINIUM\dominium_state.dsus
```

Options:
- `/DIR=PATH` or `--install-root PATH`
- `/MANIFEST=PATH` or `--manifest PATH`
- `/PAYLOAD=PATH` or `--payload-root PATH`
- `/STATE=PATH` or `--state PATH`
- `/LOG=PATH` or `--log PATH`
- `--component <id>` (repeatable)
- `--exclude <id>` (repeatable)
- `--scope portable|user|system`
- `--platform <triple>` (default `dos-x86`)

## Default paths
- Install root: `C:\DOMINIUM`
- State: `C:\DOMINIUM\dominium_state.dsus`
- Log: `C:\DOMINIUM\dominium_install.log`

## Limitations
- Archive payloads only (`*.dsuarch`). Fileset payloads are not supported.
- 8.3 path constraints apply; use short paths where possible.
- No registry or advanced shell integration.

## Emulator testing (DOSBox)
1) Mount the installer directory as drive `C:`.
2) Run `INSTALL.EXE /E` for easy install.
3) Verify state/log creation under `C:\DOMINIUM`.
4) Run `INSTALL.EXE /V` and `INSTALL.EXE /U` for verify/uninstall.
