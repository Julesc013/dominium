# Build Output Guide

This document summarizes where build artifacts are written. Dist layout details
live in `docs/BUILD_DIST.md`.

## Default output directories
- Runtime outputs: `${CMAKE_BINARY_DIR}/bin`
- Libraries/archives: `${CMAKE_BINARY_DIR}/lib`

These defaults are set by the root `CMakeLists.txt` and may be overridden by
specific presets in `CMakePresets.json`.

## Dist outputs (opt-in)
- `dist/` is a separate layout used only for targets that call `dist_set_role`.
- The root build defines `dist_meta`, `verify_dist`, and `validate_dist`.
- The `dist_seed` target exists only if `tools/dist_seed` is added to the build.

## References
- `docs/BUILD_DIST.md` (dist layout and validation rules)
- `docs/BUILDING.md` (build system and options)
