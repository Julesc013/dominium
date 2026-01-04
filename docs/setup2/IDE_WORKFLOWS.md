# Setup2 IDE Workflows

## Visual Studio 2026 (Windows EXE frontend)
- Open the solution: `source/dominium/setup/frontends/adapters/windows_exe/vs/DominiumSetupWin.sln`.
- Edit dialogs/resources in `source/dominium/setup/frontends/adapters/windows_exe/dominium_setup_win_exe.rc`.
- Control IDs are defined in `source/dominium/setup/frontends/adapters/windows_exe/dominium_setup_win_exe_resources.h`.
- Debug profiles are defined in `source/dominium/setup/frontends/adapters/windows_exe/vs/launch.vs.json`.
  - Profiles write outputs under `tmp/setup2_sandbox/...` at the repo root.
- CMake remains canonical:
  - `cmake --preset windows-msvc-x64-debug`
  - `cmake --build --preset windows-msvc-x64-debug --target dominium-setup-win-exe`
- WiX authoring (MSI):
  - Project: `source/dominium/setup/frontends/adapters/windows_msi/vs/DominiumSetupMsi.wixproj`
  - Requires the WiX Toolset VS extension (v3 or compatible).

## Xcode (macOS GUI frontend)
- Open the project: `source/dominium/setup/frontends/adapters/macos_pkg/xcode/DominiumSetupMac.xcodeproj`.
- Edit UI in `source/dominium/setup/frontends/adapters/macos_pkg/xcode/DominiumSetupMacApp/Resources/Base.lproj/Main.storyboard`.
- Debug sandbox (scheme env vars):
  - `DOMINIUM_SETUP_SANDBOX_ROOT=/tmp/dominium_setup_gui`
  - `DOMINIUM_SETUP_USE_FAKE_SERVICES=1`
  - `DOMINIUM_SETUP_MANIFEST=<repo>/source/dominium/setup/tests/fixtures/manifests/minimal.dsumanifest`
- Headless request export:
  - `dominium-setup-macos-gui --export-request --manifest <path> --op install --scope user --platform macos-x64 --out-request /tmp/install_request.tlv`
- CMake remains canonical:
  - `cmake --preset macos-xcode-debug`
  - `cmake --build --preset macos-xcode-debug --target dominium-setup-macos-gui`

## Linux (CMake-native IDEs)
- Supported IDEs: VS Code, CLion, Qt Creator, KDevelop (CMake integration).
- Configure + build:
  - `cmake --preset linux-debug`
  - `cmake --build --preset linux-debug --target dominium-setup dominium-setup-tui`
- Packaging convenience targets:
  - `cmake --build --preset linux-debug --target package-linux-deb`
  - `cmake --build --preset linux-debug --target package-linux-rpm`
  - `cmake --build --preset linux-debug --target package-linux-tar`
