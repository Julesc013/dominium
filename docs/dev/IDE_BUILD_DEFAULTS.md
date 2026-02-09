Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none

# IDE Build Defaults

## Windows (VS 2026 / VSCode CMake Tools)

Default configure preset:
- `msvc-dev-debug`

Default build target:
- `all_runtime`

Default fast verification:
- `verify_fast` (`msvc-verify`)

Full verification:
- `verify_full` (`msvc-verify-full`)

## macOS (Xcode / CMake)

Default configure preset:
- `macos-dev`

Default build target:
- `all_runtime`

Verification:
- `macos-verify` for fast checks
- `macos-verify-full` for full checks

## Linux (CMake + Ninja IDE flows)

Default configure preset:
- `linux-gcc-dev`

Default build target:
- `all_runtime`

Verification:
- `linux-verify` for fast checks
- `linux-verify-full` for full checks

## Release builds

Release packaging is explicit and not the IDE default:
- Windows: `release-winnt-x86_64`
- Linux: `release-linux-x86_64`
- macOS: `release-macos-arm64`

Release packaging target:
- `dist_all`
