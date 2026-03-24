Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# IDE Setup (DEV-OPS-0)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Scope: daily developer IDE setup and CMake preset usage.

Primary IDEs
- Visual Studio 2022 Community (Windows)
- Xcode (macOS)

Secondary / compatibility toolchains
- Visual Studio 2015 toolset (Windows)
- GCC / Clang (Linux)
- Cross-compilers (documented per target; optional)

Rules (binding for dev workflow)
- IDE version does not define the language standard.
- C89/C++98 is enforced via CMake flags and presets.
- Use CMake presets; do not hand-edit generated project files.
- Default IDE surfaces expose only the daily-use presets for the current host OS.
- Set `DOMINIUM_ADVANCED_PRESETS=1` before configure if you need alternate toolchains, legacy lanes, or IDE projection presets.

Windows (VS2022)
1) Open the repo folder in Visual Studio (CMake mode).
2) Select a preset:
   - local (fast debug)
   - verify (strict C89/C++98 + tests)
   - release-check (dry-run release lane)
   - release-winnt-x86_64 (release packaging lane)
3) Configure and build all targets.

macOS (Xcode)
1) Configure:
   - cmake --preset macos-dev
2) Open the generated Xcode project from the preset binary directory.
3) Build the desired targets.

Linux (GCC/Clang)
- Use linux-gcc-dev for the default fast debug lane.
- Use linux-verify for strict validation.
- Unlock alternate Linux toolchains by setting `DOMINIUM_ADVANCED_PRESETS=1`.

Debugging tips
- Headless smoke runs: use --headless or --ui=none where available.
- UI diagnostics: use --ui-log and --renderer null for deterministic logs.

See also
- docs/dev/BUILD_MATRIX.md
- docs/architecture/IDE_AND_TOOLCHAIN_POLICY.md
