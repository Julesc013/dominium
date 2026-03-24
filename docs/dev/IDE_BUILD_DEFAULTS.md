Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# IDE Build Defaults

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Windows (VS 2022 / VSCode CMake Tools)

Default configure preset:
- `local`

Default build target:
- `all_runtime`

Default fast verification:
- `verify_fast` (`verify`)

Full verification:
- `verify_full` (`cmake --build --preset verify --target verify_full`)

## macOS (Xcode / CMake)

Default configure preset:
- `macos-dev`

Default build target:
- `all_runtime`

Verification:
- `macos-verify` for fast checks
- `cmake --build --preset macos-verify --target verify_full` for full checks

## Linux (CMake + Ninja IDE flows)

Default configure preset:
- `linux-gcc-dev`

Default build target:
- `all_runtime`

Verification:
- `linux-verify` for fast checks
- `cmake --build --preset linux-verify --target verify_full` for full checks

## Release builds

Release packaging is explicit and not the IDE default:
- Windows: `release-winnt-x86_64`
- Linux: `release-linux-x86_64`
- macOS: `release-macos-arm64`

Release packaging target:
- `dist_all`

Advanced preset surface:
- Set `DOMINIUM_ADVANCED_PRESETS=1` before configure if you need legacy, alternate-toolchain, or IDE projection presets.
