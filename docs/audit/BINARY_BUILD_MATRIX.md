Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# IRC-0 Phase 3: Binary Build Matrix

## Toolchain + Build Context

- Generator/toolchain: Visual Studio 2026 (`x64`)
- Build tree: `build/msvc-base`
- Build invocation: `cmake --build build/msvc-base --`
- Configuration observed: `Debug|x64`

## Build Outputs

| Product | Binary path | Type | Primary internal dependencies | External/system dependencies |
| --- | --- | --- | --- | --- |
| setup | `build/msvc-base/bin/setup.exe` | CLI app | `setup_core.lib`, `dominium_app_runtime.lib`, `libs::contracts` | Win32 CRT + standard Windows SDK link set |
| launcher | `build/msvc-base/bin/launcher.exe` | CLI app | `launcher_core.lib`, `dominium_app_runtime.lib`, `domino_engine.lib`, `libs::contracts` | Win32 CRT + standard Windows SDK link set |
| client | `build/msvc-base/bin/client.exe` | CLI app | `dominium_app_runtime.lib`, `domino_engine.lib`, `dominium_game.lib`, `build_identity.lib`, `libs::contracts` | `user32`, `gdi32`, `kernel32`, `winspool`, `shell32`, `ole32`, `oleaut32`, `uuid`, `comdlg32`, `advapi32` |
| server | `build/msvc-base/bin/server.exe` | CLI app | `dominium_app_runtime.lib`, `domino_engine.lib`, `dominium_game.lib`, `libs::contracts` | Win32 CRT + standard Windows SDK link set |
| tool_ui_bind | `dist/sys/winnt/x64/bin/tools/tool_ui_bind.exe` | Tool (CLI) | `domino_ui_ir.lib`, `appcore.lib` | Win32 CRT + standard Windows SDK link set |
| tool_ui_validate | `dist/sys/winnt/x64/bin/tools/tool_ui_validate.exe` | Tool (CLI) | `domino_ui_ir.lib`, `domino_core` link chain | Win32 CRT + standard Windows SDK link set |
| pack_validate | `tools/pack/pack_validate.py` | Tool (Python CLI) | `schema/pack_manifest.schema` + repo-local validation code | Python runtime |

## Build Artifacts Observed

- Executables:
  - `build/msvc-base/bin/client.exe`
  - `build/msvc-base/bin/launcher.exe`
  - `build/msvc-base/bin/server.exe`
  - `build/msvc-base/bin/setup.exe`
  - `dist/sys/winnt/x64/bin/tools/tool_ui_bind.exe`
  - `dist/sys/winnt/x64/bin/tools/tool_ui_validate.exe`
- Core static libraries:
  - `build/msvc-base/lib/domino_engine.lib`
  - `build/msvc-base/lib/dominium_game.lib`
  - `build/msvc-base/lib/dominium_app_runtime.lib`
  - `build/msvc-base/lib/appcore.lib`
  - `build/msvc-base/lib/build_identity.lib`

## Result

- PASS: target binaries are real build outputs and are materialized at stable paths.
- PASS: each target links against explicit internal dependency surfaces.
- NOTE: some dependencies are inferred from CMake target graphs where link-line tools are unavailable in this shell.
