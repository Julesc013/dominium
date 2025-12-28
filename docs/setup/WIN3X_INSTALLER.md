# Windows 3.x (Win16) Installer

## Supported OS
- Windows 3.0, 3.1, 3.11 (Program Manager era)

## Binary
- `SETUP.EXE` (Win16 build via OpenWatcom or equivalent 16-bit toolchain)

## UI
Win16 dialog-based wizard:
- Easy/Custom install
- Install path entry
- Component list (Custom)
- Install/Repair/Verify/Uninstall actions

## CLI usage
```
SETUP.EXE --install --manifest MANIFESTS\dominium_legacy.dsumanifest --payload-root .
SETUP.EXE --repair --install-root C:\DOMINIUM --state C:\DOMINIUM\dominium_state.dsus
SETUP.EXE --uninstall --state C:\DOMINIUM\dominium_state.dsus
SETUP.EXE --verify --state C:\DOMINIUM\dominium_state.dsus
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
- `--platform <triple>` (default `win16-x86`)

## Default paths
- Install root: `C:\DOMINIUM`
- State: `C:\DOMINIUM\dominium_state.dsus`
- Log: `C:\DOMINIUM\dominium_install.log`

## Limitations
- Archive payloads only (`*.dsuarch`).
- No Unicode paths.
- Shell integration limited to file copy and state logging.

## Emulator testing (PCem/86Box)
1) Install Windows 3.x and add a virtual disk with installer files.
2) Run `SETUP.EXE` from Program Manager.
3) Verify `dominium_state.dsus` under the install root.
4) Run verify/uninstall paths via GUI or CLI.
