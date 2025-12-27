# Windows EXE Installer (Parity Suite)

The Windows EXE installers are the single-file, self-contained setup frontends for
Windows 3.x through 11. They mirror the MSI installer flow and emit the same
`dsu_invocation` payloads for parity enforcement.

## Binaries

- `DominiumSetup-win16.exe` (Windows 3.x line; legacy core profile)
- `DominiumSetup-win32.exe` (Windows 95/98/ME + NT 4/2000/XP 32-bit)
- `DominiumSetup-win64.exe` (Windows XP x64 / Vista+ 64-bit)

Each EXE is a single self-contained file with embedded Setup Core, manifests, and payloads.

## Modes

Default: GUI wizard (native controls).

Explicit modes:

- GUI: `DominiumSetup-win64.exe --gui`
- TUI: `DominiumSetup-win64.exe --tui`
- CLI: `DominiumSetup-win64.exe --cli <command> ...`

## CLI commands (stable)

- `export-invocation`
- `install`, `upgrade`, `repair`, `uninstall`
- `detect`, `verify`
- `plan`, `apply`, `apply-invocation`

Common options:

- `--manifest <file>`
- `--scope <portable|user|system>`
- `--platform <triple>`
- `--install-root <path>`
- `--components <csv>` / `--exclude <csv>`
- `--deterministic 1`
- `--dry-run`
- `--json`
- `--shortcuts` / `--file-assoc` / `--url-handlers`

## Silent / headless examples

Export invocation:

```
DominiumSetup-win64.exe --cli export-invocation --manifest C:\artifact_root\setup\manifests\product.dsumanifest --op install --scope portable --platform win64-x64 --install-root C:\Dominium --ui-mode cli --frontend-id exe-win64 --out C:\Temp\invocation.tlv --deterministic 1
```

Dry-run plan:

```
DominiumSetup-win64.exe --cli plan --manifest C:\artifact_root\setup\manifests\product.dsumanifest --op install --scope portable --platform win64-x64 --install-root C:\Dominium --out C:\Temp\plan.dsuplan --deterministic 1 --dry-run
```

Dry-run apply:

```
DominiumSetup-win64.exe --cli apply --manifest C:\artifact_root\setup\manifests\product.dsumanifest --op install --scope portable --platform win64-x64 --install-root C:\Dominium --deterministic 1 --dry-run
```

## Invocation payload bridge

EXE frontends only collect user choices and emit a `dsu_invocation` payload.
They then call:

```
dominium-setup apply --invocation <payload>
```

The payload is written to `%TEMP%\dominium-invocation.tlv` by default.

## Self-contained extraction

The EXE contains an embedded archive. On launch it extracts to a temporary staging
directory, invokes Setup Core from that staging root, and removes the staging
directory on success (preserved on failure for forensics).

Developers can override extraction using:

- `DSU_EXE_STAGE=<artifact_root>` (use an external staging root)

## Build targets

CMake targets:

- `setup_exe_win32_nt` → `dist/windows/DominiumSetup-win32.exe`
- `setup_exe_win64` → `dist/windows/DominiumSetup-win64.exe`
- `setup_exe_win16` → placeholder target (external toolchain required)

## Parity guarantees

For the same inputs, MSI, EXE, and CLI must produce identical invocation digests
and plan digests. The EXE suite is validated via parity tests that compare
CLI vs EXE invocation and plan digests.

See also:

- `docs/setup/INVOCATION_PAYLOAD.md`
- `docs/setup/INSTALLER_UX_CONTRACT.md`
- `docs/setup/WINDOWS_INSTALLER_MATRIX.md`
