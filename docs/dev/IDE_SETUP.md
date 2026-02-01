Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# IDE Setup (DEV-OPS-0)

Scope: daily developer IDE setup and CMake preset usage.

Primary IDEs
- Visual Studio 2026 Community (Windows)
- Xcode (macOS)

Secondary / compatibility toolchains
- Visual Studio 2015 toolset (Windows)
- GCC / Clang (Linux)
- Cross-compilers (documented per target; optional)

Rules (binding for dev workflow)
- IDE version does not define the language standard.
- C89/C++98 is enforced via CMake flags and presets.
- Use CMake presets; do not hand-edit generated project files.

Windows (VS2026)
1) Open the repo folder in Visual Studio (CMake mode).
2) Select a preset:
   - dev-win-vs2026 (fast debug)
   - verify-win-vs2026 (strict C89/C++98 + tests)
   - release-win-vs2026 (release)
   - legacy-win-vs2015 (compatibility)
3) Configure and build all targets.

macOS (Xcode)
1) Configure:
   - cmake --preset dev-macos-xcode
2) Open the generated Xcode project from the preset binary directory.
3) Build the desired targets.

Linux (GCC/Clang)
- Use dev-linux-gcc or dev-linux-clang for fast debug.
- Use verify-linux-gcc for strict validation.

Debugging tips
- Headless smoke runs: use --headless or --ui=none where available.
- UI diagnostics: use --ui-log and --renderer null for deterministic logs.

See also
- docs/dev/BUILD_MATRIX.md
- docs/architecture/IDE_AND_TOOLCHAIN_POLICY.md
