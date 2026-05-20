Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none

# CANON-SPINE-BOUNDARY-01 Repair

Status: PASS_WITH_WARNINGS.

This repair closed the active boundary/import/build failures left after the canonical source-spine collapse.

## Changes

- Moved capability runtime implementation from `tools/repo/governance/**` into `runtime/capability/**`.
- Left compatibility shims in `tools/repo/governance/**` for old tool imports.
- Moved Win32 shell/UI implementation files under `runtime/platform/win32/**`.
- Rewired CMake targets to use `runtime_shell` and `runtime_platform_win32_ui`.
- Repaired engine test, server shard test, validator, modpack, and UI IR include paths.

## Proof

- Build boundary validator: PASS, 9 failures reduced to 0.
- CMake configure: PASS.
- `ALL_BUILD`: PASS.
- Smoke CTest: PASS, 57/57.
- Focused spine CTest: PASS, 6/6.

## Remaining Work

Full verify remains not green because of broader semantic/distribution/projection debt. Feature work remains blocked.
