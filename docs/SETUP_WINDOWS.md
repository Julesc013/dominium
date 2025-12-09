# Windows Installers

Windows installers wrap the cross-platform setup engine (`dominium-setup-cli`)
without reimplementing install logic. Two formats are provided:

- **MSI** built with WiX (`Dominium.wxs`).
- **Bootstrapper EXE** (WiX Burn, optional) chaining the MSI.
- **Native Win32 wrapper** (`dominium_setup_win32_gui`) that shells out to the
  setup CLI with a small wizard UI.

## Prerequisites
- Windows with the WiX Toolset (v3+): `candle.exe`, `light.exe` on `PATH`.
- Staged payload under `DOMINIUM_DIST_DIR` (defaults to
  `<build>/dist/`), containing at minimum:
  - `dominium-setup-cli.exe`
  - `dominium_setup_win32_gui.exe`
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
      -DDOMINIUM_VERSION=1.0.0 ^
      -DDOMINIUM_DIST_DIR="C:/path/to/dist" ^
      -B build/debug
```

Key variables (all cached):
- `DOMINIUM_ENABLE_PACKAGING` — include packaging targets (default OFF).
- `DOMINIUM_BUILD_MSI` — build `dominium_msi` target (default ON).
- `DOMINIUM_BUILD_BUNDLE` — build `dominium_bundle` target (default ON).
- `DOMINIUM_VERSION` — installer version string (defaults to `1.0.0`).
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
  - `dominium-setup-cli.exe` and `dominium_setup_win32_gui.exe`
  - Launcher + game payload (`dominium_launcher_cli.exe`, `dominium_game_cli.exe`)
  - `data\` structure including packs/mods folders (extend the manifest as your staged payload grows)
  - Start Menu shortcuts for Dominium + Dominium (Safe mode) and a desktop shortcut to the launcher
- Uses `WixUI_InstallDir` for a standard InstallDir wizard with license dialog.
- UpgradeCode/Component GUIDs are stable for servicing.

## Bootstrapper (bootstrapper.wxs)
- Burn bundle that chains the MSI with the standard RTF-license UI.
- Variables passed via CMake: `MsiPath`, `LicenseFile`, `ProductVersion`,
  optional `BundleLogo`/`BundleIcon`.
- Runs MSI maintenance UI for repair/uninstall.

## Win32 wrapper (`dominium_setup_win32_gui`)
- Built on Windows automatically when the setup product is built.
- Wizard-style window with Back/Next navigation:
  - Scope selection (portable/per-user/all-users) and install directory picker (Browse) on the first page
  - Install/Repair/Uninstall/Verify buttons with a marquee progress bar on the actions page
- Spawns `dominium-setup-cli.exe` via `CreateProcess`, so all install logic
  stays in the core setup engine.

## Notes
- The MSI does not recreate install logic; it copies staged files and registers
  shortcuts. Use `dominium-setup-cli` for repair/verify flows.
- Ensure staged payload and optional icon/license assets exist before running
  WiX to avoid `candle`/`light` failures.
- Update `scripts/packaging/windows/Dominium.wxs` if your staged executable
  names or layout diverge (WiX will fail if referenced files are missing).
