Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Linux Installers

Linux packaging offers native distro packages plus a portable `.run` wrapper.
All flows emit a `dsu_invocation` payload and call `dominium-setup` for
resolve/plan/apply, keeping logic shared with other platforms.
Linux TUI/CLI flows must mirror MSI semantics and the canonical UX contract.

## Prerequisites
- Built payload staged under `DOMINIUM_DIST_DIR` (default `<build>/dist/`):
  - `dominium-setup`
  - Game/launcher binaries and data
- For distro packages: `dpkg-deb` (Debian/Ubuntu) and/or `rpmbuild` (Fedora/openSUSE).
- For portable installer: `bash`, `tar`, `gzip`; optional `appimagetool` if you
  extend to a formal AppImage.

## CMake options
Configure with packaging enabled:

```bash
cmake -G "Ninja" -DDOMINIUM_ENABLE_PACKAGING=ON \
      -DDOMINIUM_BUILD_DEB=ON \
      -DDOMINIUM_BUILD_RPM=ON \
      -DDOMINIUM_BUILD_RUN=ON \
      -DDOMINIUM_GAME_VERSION=0.1.0 \
      -DDOMINIUM_DIST_DIR="$PWD/build/dist" \
      -B build/linux
```

Key cache variables:
- `DOMINIUM_BUILD_DEB` / `DOMINIUM_BUILD_RPM` / `DOMINIUM_BUILD_RUN` — enable respective targets (default ON when on Linux).
- `DOMINIUM_GAME_VERSION` — package version string.
- `DOMINIUM_DIST_DIR` — staging root with binaries/data.
- `DOMINIUM_INSTALLER_DIR` — output root (defaults to `<build>/dist/installers/linux`).
- `DOMINIUM_DEB_DEPENDS`, `DOMINIUM_DEB_MAINTAINER` — control fields for .deb.
- `DOMINIUM_RPM_REQUIRES`, `DOMINIUM_RPM_RELEASE` — spec fields for .rpm.

## Building

```bash
cmake --build build/linux --target dominium_deb   # .deb via dpkg-deb
cmake --build build/linux --target dominium_rpm   # .rpm via rpmbuild
cmake --build build/linux --target dominium_run   # portable .run
```

Outputs (by default in `dist/installers/linux/`):
- `dominium_<version>_amd64.deb`
- `dominium-<version>-<release>.x86_64.rpm`
- `Dominium-<version>.run`

## Debian skeleton
- Control file: `scripts/packaging/linux/deb/DEBIAN/control.in`
  - Package: dominium, Architecture: amd64, Depends default to libc6/libstdc++6.
- Maintainer scripts (`postinst`, `prerm`, `postrm`) generate an invocation
  payload (system scope, install root `/opt/dominium`) and call:
  - `dominium-setup plan --manifest <manifest> --invocation <file> --out <plan>`
  - `dominium-setup apply --plan <plan>`

## RPM skeleton
- Spec template: `scripts/packaging/linux/rpm/dominium.spec.in`
- `%post` / `%preun` generate invocation payloads and call `dominium-setup` plan/apply.
- Payload installs into `/opt/dominium`.

## Portable .run
- `scripts/packaging/linux/dominium-installer.sh.in` is a self-extracting stub;
  `build_run.sh` packages the staged payload into `Dominium-<version>.run`.
- Installer extracts to a temp directory, writes a `dsu_invocation` payload
  (scope, install root, component selection), then runs:
  - `dominium-setup plan --manifest <manifest> --invocation <file> --out <plan>`
  - `dominium-setup apply --plan <plan>`
  and cleans up.
- Extend with `appimagetool` if you want an AppImage: populate an `AppDir` with
  `usr/bin/dominium-launcher`, `dominium-setup-cli`, .desktop file, and icon,
  then call `appimagetool AppDir`.

## Notes
- Packaging scripts live under `scripts/packaging/linux/`; no distro-specific
  logic is added to the core engine.
- Install logic stays in Setup Core; packages primarily stage files under
  `/opt/dominium` (or the chosen target) and call the CLI with invocation
  payloads. Adjust paths or dependencies in the templates as your payload grows.