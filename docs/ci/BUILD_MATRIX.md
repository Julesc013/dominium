# Build Matrix

This document enumerates the canonical build presets defined in
`CMakePresets.json`. For usage, see `docs/guides/BUILDING.md`.

## Primary Windows presets (MSVC)
- `vs2026-x64-debug` / `vs2026-x64-release`:
  full product build with tools/tests enabled, `DOM_PLATFORM=sdl2`,
  `DOM_BACKEND_GL2=ON`, `DOM_BACKEND_DX9=ON`, `DOM_FETCH_SDL2=ON`.
- `baseline-debug` / `baseline-release`:
  strict baseline (C90/C++98), `DOM_ENABLE_MODERN=OFF`, `DOM_PLATFORM=sdl2`,
  `DOM_BACKEND_SOFT=ON`, `DOM_BACKEND_NULL=ON`, `DOM_BACKEND_SDL2=ON`,
  `DOM_DISALLOW_DOWNLOADS=OFF`, `DOM_FETCH_SDL2=ON`.
- `modern-debug` / `modern-release`:
  baseline plus `DOM_ENABLE_MODERN=ON`; debug enables `GL2` + `DX9`, release
  enables `DX9` (GL2 remains OFF).

## Windows variants
- `msvc-debug` / `msvc-release`: MSVC base presets with output directory overrides.
- `windows-msvc-x64-debug` / `windows-msvc-x86-debug`: architecture-specific MSVC builds.
- `msvc-win32-dx9`: Win32 platform without SDL2 (`DOM_PLATFORM=win32`, `DOM_BACKEND_DX9=ON`).

## Linux presets
- `linux-debug`: GCC/Ninja, `DOM_PLATFORM=posix_x11`.
- `linux-dev`: build preset that targets `ui_preview_launcher_linux`
  (legacy; target lives under `legacy/` and is not in the root build graph).

## macOS presets
- `macos-xcode-debug`: Xcode, `DOM_PLATFORM=cocoa`.
- `macos-xcode`: build preset that targets `ui_preview_launcher_macos`
  (legacy; target lives under `legacy/` and is not in the root build graph).

## Legacy/hidden presets
- `msys2-debug` / `msys2-release`: MSYS2 UCRT64 presets marked legacy/hidden.
- `windows-msvc-vs2026`: build preset targeting `ui_preview_launcher_win32`
  (legacy; target lives under `legacy/` and is not in the root build graph).

## Notes
- Preset definitions in `CMakePresets.json` are authoritative.
- `DOM_PLATFORM` allowed values are defined in the root `CMakeLists.txt`;
  presets set compatible `DOM_BACKEND_*` toggles.
