# macOS Installers

macOS distribution ships a native `.app` bundle plus optional `.pkg` and `.dmg`
wrappers. The app stays a thin shell over `dominium-setup-cli` and the core
engine; installation logic remains in the shared setup code.

## Prerequisites
- macOS with Xcode command line tools (for `pkgbuild`, `productbuild`, `hdiutil`).
- Staged payload under `DOMINIUM_DIST_DIR` (defaults to `<build>/dist/`):
  - `dominium_launcher_cli` (will be renamed to the bundle executable)
  - `dominium-setup-cli`
  - Optional data payload (copied manually into the bundle or handled by the CLI)
- Optional: custom icon at `Dominium.app/Contents/Resources/AppIcon.icns`
  (place it before packaging).

## CMake options
Enable packaging during configure:

```bash
cmake -G "Ninja" -DDOMINIUM_ENABLE_PACKAGING=ON \
      -DDOMINIUM_BUILD_MACOS_PKG=ON \
      -DDOMINIUM_GAME_VERSION=0.1.0 \
      -DDOMINIUM_DIST_DIR="$PWD/build/dist" \
      -B build/macos
```

Key cache variables:
- `DOMINIUM_BUILD_MACOS_PKG` — build `dominium_macos_pkg` / `dominium_macos_dmg` (default ON).
- `DOMINIUM_GAME_VERSION` — installer/app version string (default `0.1.0`).
- `DOMINIUM_DIST_DIR` — staging root containing built binaries/data.
- `DOMINIUM_INSTALLER_DIR` — outputs go to `<build>/dist/installers/macos` by default.
- `DOMINIUM_BUNDLE_IDENTIFIER` — CFBundleIdentifier (default `com.yourorg.dominium`).
- `DOMINIUM_BUNDLE_EXECUTABLE` — name inside `Dominium.app/Contents/MacOS` (default `dominium-launcher`).
- `DOMINIUM_MACOS_MINIMUM_VERSION` — minimum supported macOS version (default `10.13`).

## Building
After configure:

```bash
cmake --build build/macos --target dominium_macos_pkg
cmake --build build/macos --target dominium_macos_dmg  # builds .pkg then .dmg
```

Outputs (`dist/installers/macos/` by default):
- `Dominium-<version>-installer.pkg` (distribution pkg)
- `Dominium-<version>.pkg` (component pkg)
- `Dominium-<version>.dmg` (DMG with `.app`, Applications symlink, and the pkg)

## Bundle layout
- `scripts/packaging/macos/Dominium.app/Contents/Info.plist.in` supplies CFBundle
  metadata (name, identifier, version, executable, min OS).
- Bundle contains:
  - `Contents/MacOS/<bundle executable>` (copied from `dominium_launcher_cli`)
  - `Contents/MacOS/dominium-setup-cli` (used for repair/install tasks)
  - `Contents/Resources/` (place icon/assets before packaging)

## PKG packaging
- `build_pkg.sh` wraps `pkgbuild` + `productbuild`, staging the bundle to
  `/Applications/Dominium.app`.
- `postinstall` script calls `dominium-setup-cli` for a system-level install
  and seeds per-user data under `~/Library/Application Support/Dominium`.
  It is resilient if the CLI is absent or fails (non-fatal).

## DMG creation
- `build_dmg.sh` builds a drag-and-drop DMG containing the `.app`, an
  `/Applications` symlink, and the distribution pkg for advanced installs.

## Notes
- Packaging targets only run on macOS (guarded by `APPLE` in CMake).
- Ensure `DOMINIUM_DIST_DIR` holds macOS binaries named as expected; otherwise
  the staging copy step will fail.
- The macOS GUI shim lives in `source/dominium/setup/os/macos` and
  shells out to `dominium-setup-cli` for all real work.
