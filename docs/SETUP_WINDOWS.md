# Windows Installers

Windows installers are MSI-centric and wrap Setup Core via the canonical
`dsu_invocation` payload. MSI defines the canonical UX; EXE is a parity clone.
GUI/TUI/CLI frontends are first-class and must follow the same UX contract.

- **MSI** built with WiX (`Dominium.wxs`) and the reference UX flow.
- **Bootstrapper EXE** (WiX Burn, optional) that mirrors MSI UX and produces
  byte-equivalent invocation payloads.
- **Native Win32 GUI** (`dominium_setup_win32_gui`) that follows the same
  contract and emits `dsu_invocation`.

## Prerequisites
- Windows with the WiX Toolset (v3+): `candle.exe`, `light.exe` on `PATH`.
- Staged payload under `DOMINIUM_DIST_DIR` (defaults to `<build>/dist/`),
  containing at minimum:
  - `dominium-setup.exe`
  - `dominium_setup_win32_gui.exe` (optional GUI frontend)
  - Game/launcher binaries
  - `data/` payload
- Optional: Custom license file
  (`DOMINIUM_LICENSE_FILE`, defaults to `scripts/packaging/windows/license.rtf`).
  - Optional bootstrapper icon/logo (`DOMINIUM_BUNDLE_ICON`, `DOMINIUM_BUNDLE_LOGO`).

## CMake options
Enable packaging targets when configuring:

```bash
cmake -G "Ninja" -DDOMINIUM_ENABLE_PACKAGING=ON ^
      -DDOMINIUM_BUILD_MSI=ON ^
      -DDOMINIUM_BUILD_BUNDLE=ON ^
      -DDOMINIUM_GAME_VERSION=0.1.0 ^
      -DDOMINIUM_DIST_DIR="C:/path/to/dist" ^
      -B build/debug
```

Key variables (all cached):
- `DOMINIUM_ENABLE_PACKAGING` — include packaging targets (default OFF).
- `DOMINIUM_BUILD_MSI` — build `dominium_msi` target (default ON).
- `DOMINIUM_BUILD_BUNDLE` — build `dominium_bundle` target (default ON).
- `DOMINIUM_GAME_VERSION` — installer version string (defaults to `0.1.0`).
- `DOMINIUM_DIST_DIR` — staging root with binaries/data (defaults to
  `<build>/dist`).
- `DOMINIUM_INSTALLER_DIR` — outputs go to `<build>/dist/installers/windows`
  by default.
- `DOMINIUM_LICENSE_FILE` — RTF shown by MSI/Burn UI.
- `DOMINIUM_BUNDLE_ICON` — optional .ico embedded into the Burn EXE.
- `DOMINIUM_BUNDLE_LOGO` — optional UI banner image for the Burn wizard.

Add `DOMINIUM_MANUFACTURER` to override the `Manufacturer` string.

## Building
After configuring with packaging enabled:

```bash
cmake --build build/debug --target dominium_msi
cmake --build build/debug --target dominium_bundle  # if enabled
```

Outputs land under `dist/installers/windows/`:
- `Dominium-<version>.msi`
- `Dominium-<version>-Setup.exe` (bootstrapper)

## MSI contents (Dominium.wxs)
- Installs to `ProgramFilesFolder\Dominium\` by default.
- Per-user fallback (`LocalAppData\Programs\Dominium`) when lacking privilege
  or when `ALLUSERS=2`/`MSIINSTALLPERUSER=1`.
- Components:
  - `dominium-setup.exe` and (optional) `dominium_setup_win32_gui.exe`
  - Launcher + game payload
  - `data\` structure including packs/mods folders (extend the manifest as your staged payload grows)
- Shortcuts and registrations are produced by Setup Core platform intents
  during apply; the MSI does not own install logic.
- Uses `WixUI_InstallDir` for a standard InstallDir wizard with license dialog.
- UpgradeCode/Component GUIDs are stable for servicing.

## Bootstrapper (bootstrapper.wxs)
- Burn bundle that chains the MSI with the standard RTF-license UI.
- Variables passed via CMake: `MsiPath`, `LicenseFile`, `ProductVersion`,
  optional `BundleLogo`/`BundleIcon`.
- Runs MSI maintenance UI for repair/uninstall.

## Win32 wrapper (`dominium_setup_win32_gui`)
- Built on Windows automatically when the setup product is built.
- Wizard-style window with Back/Next navigation that mirrors MSI step order.
- Emits a `dsu_invocation` payload and calls `dominium-setup` to resolve/plan/apply.
- No install logic lives in the wrapper; it only collects choices.

## Notes
- MSI/EXE do not recreate install logic; they only stage files and emit
  invocation payloads for Setup Core.
- Use `dominium-setup` for repair/verify flows; frontends should call it with
  an invocation payload derived from the same UX contract.
- Ensure staged payload and optional icon/license assets exist before running
  WiX to avoid `candle`/`light` failures.
- Update `scripts/packaging/windows/Dominium.wxs` if your staged executable
  names or layout diverge (WiX will fail if referenced files are missing).
