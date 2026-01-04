# Dominium Setup (Windows EXE) - Visual Studio Workflow

This solution is a convenience layer for native UI editing. CMake remains canonical.

## Open + Edit
- Open `source/dominium/setup/frontends/adapters/windows_exe/vs/DominiumSetupWin.sln`.
- Edit UI resources in `source/dominium/setup/frontends/adapters/windows_exe/dominium_setup_win_exe.rc`.
- Stable IDs live in `source/dominium/setup/frontends/adapters/windows_exe/dominium_setup_win_exe_resources.h`.
- Common macros/settings live in `source/dominium/setup/frontends/adapters/windows_exe/vs/DominiumSetupWinCommon.props`
  (see `DSK_UI_ERA=2026` for era gating).

## Debug Profiles (GUI/TUI/CLI)
Profiles live in `source/dominium/setup/frontends/adapters/windows_exe/vs/launch.vs.json`.
They run against a deterministic sandbox under `tmp/setup2_sandbox` at the repo root.

If you need to override paths:
- Use `--manifest <path>` to point at a test manifest.
- Use `--use-fake-services <dir>` to set the sandbox root.

## Guardrails
- The UI project must not embed install logic. It emits `install_request.tlv` and calls `dominium-setup`.
- Any VS-only settings must be mirrored in CMake or documented as local-only.
