Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# CI Matrix

Dominium CI is split into two tiers: per-commit and scheduled canaries.

## Per-Commit (push/PR)

Minimal, always-on coverage:

- Windows (MSVC): `win32` + software renderer, and `null` headless.
- Linux (GCC): `posix_headless` + software renderer, and `null` headless.
- macOS (Apple Clang): `posix_headless` + software renderer.

All tests are CLI-only via `ctest` (no GUI/TUI dependencies).

## Scheduled (weekly)

Extended coverage intended to catch drift:

- Windows DX9 canary (`win32` + `DOM_BACKEND_DX9=ON`).
- Linux Clang build (`posix_headless` + software renderer).

Optional canaries exist via presets for additional toolchains:

- Windows `clang-cl` (`windows-clangcl-debug`)
- Windows `mingw-w64` (`windows-mingw-debug`)
- Linux `musl` (`linux-musl-debug`)

These optional presets are not enabled by default in CI and may require
toolchain installation on the runner.