Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Known Warnings

This file records non-fixable warnings encountered in canonical build/test flows.

## KW-2026-02-01-SDL2-CMAKE
- Tool: CMake 4.2.0
- Context: `cmake --preset dev-win-vs2026`
- File: `out/build/vs2026/dev-win-vs2026/_deps/dom_sdl2-src/CMakeLists.txt`
- Lines: 8, 3253
- Warning: CMake deprecation warning for `cmake_minimum_required` < 3.10
- Why safe: warning originates from bundled SDL2 CMake files; does not affect build outputs.
- Why not fixed now: third-party dependency; patching upstream is out of scope for DEV-OPS-0.
- Mitigation: update SDL2 dependency when upstream raises the minimum CMake version.
