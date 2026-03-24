Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Build Matrix (DEV-OPS-0)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Scope: canonical build presets for daily development, verification, and releases.

Key
- dev: fast, debug, local iteration
- verify: strict C89/C++98 + full TestX/RepoX
- release: release configuration
- advanced: compatibility or alternate toolchains unlocked explicitly via `DOMINIUM_ADVANCED_PRESETS=1`

Windows (x64)
- local
  - Toolchain: Visual Studio 2022 (MSVC)
  - Purpose: daily debug
- verify
  - Toolchain: Visual Studio 2022 (MSVC)
  - Purpose: strict validation (C89/C++98 enforced)
- release-check
  - Toolchain: Visual Studio 2022 (MSVC)
  - Purpose: release dry-run lane without packaging
- release-winnt-x86_64
  - Toolchain: Visual Studio 2022 (MSVC)
  - Purpose: release build

macOS (x64/arm64)
- macos-dev
  - Toolchain: Xcode (latest)
  - Purpose: daily debug
- macos-verify
  - Toolchain: Xcode (latest)
  - Purpose: strict validation (C89/C++98 enforced)
- release-macos-arm64
  - Toolchain: Xcode (latest)
  - Purpose: release build

Linux (x64)
- linux-gcc-dev
  - Toolchain: GCC
  - Purpose: daily debug
- linux-verify
  - Toolchain: GCC
  - Purpose: strict validation (C89/C++98 enforced)
- release-linux-x86_64
  - Toolchain: GCC
  - Purpose: release build

Notes
- C89/C++98 is enforced in verify presets via explicit CMake flags.
- Tests are enabled in verify presets.
- Advanced presets stay out of the default IDE picker until `DOMINIUM_ADVANCED_PRESETS=1` is set in the environment.
- Use docs/architecture/IDE_AND_TOOLCHAIN_POLICY.md for policy details.
