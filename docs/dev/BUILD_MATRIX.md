Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Build Matrix (DEV-OPS-0)

Scope: canonical build presets for daily development, verification, and releases.

Key
- dev: fast, debug, local iteration
- verify: strict C89/C++98 + full TestX/RepoX
- release: release configuration
- legacy: compatibility toolchains

Windows (x64)
- dev-win-vs2026
  - Toolchain: Visual Studio 2026 (MSVC)
  - Purpose: daily debug
- verify-win-vs2026
  - Toolchain: Visual Studio 2026 (MSVC)
  - Purpose: strict validation (C89/C++98 enforced)
- release-win-vs2026
  - Toolchain: Visual Studio 2026 (MSVC)
  - Purpose: release build
- legacy-win-vs2015
  - Toolchain: Visual Studio 2015
  - Purpose: compatibility checks

macOS (x64/arm64)
- dev-macos-xcode
  - Toolchain: Xcode (latest)
  - Purpose: daily debug
- verify-macos-xcode
  - Toolchain: Xcode (latest)
  - Purpose: strict validation (C89/C++98 enforced)
- release-macos-xcode
  - Toolchain: Xcode (latest)
  - Purpose: release build

Linux (x64)
- dev-linux-gcc
  - Toolchain: GCC
  - Purpose: daily debug
- dev-linux-clang
  - Toolchain: Clang
  - Purpose: daily debug
- verify-linux-gcc
  - Toolchain: GCC
  - Purpose: strict validation (C89/C++98 enforced)
- release-linux-gcc
  - Toolchain: GCC
  - Purpose: release build

Notes
- C89/C++98 is enforced in verify presets via explicit CMake flags.
- Tests are enabled in verify presets.
- Use docs/architecture/IDE_AND_TOOLCHAIN_POLICY.md for policy details.
