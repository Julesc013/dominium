# Build Matrix (Prompt 3)

This document enumerates the canonical build configurations used for local development and CI validation. The intent is to keep the baseline toolchain (C89/C++98) always buildable and to provide explicit opt-in for “modern” acceleration layers.

## DONE (Windows baseline)

The product is considered **complete** for Prompt 8 when the Windows baseline
verification script passes:

- `scripts\build_codex_verify.bat`
- Smoke contract: `docs/SPEC_SMOKE_TESTS.md`

## Matrix Entries

### Baseline (Windows)

**baseline win32 + soft**
- Configure: `cmake --preset baseline-debug -DDOM_DISALLOW_DOWNLOADS=ON`
- Build: `cmake --build --preset baseline-debug`
- Verify:
  - `build/baseline-debug/domino_sys_smoke.exe --smoke`
  - `build/baseline-debug/dgfx_demo.exe --gfx=soft --frames=120`
  - `build/baseline-debug/source/dominium/launcher/dominium-launcher.exe --smoke-gui --gfx=soft --profile=baseline`
  - `build/baseline-debug/source/dominium/game/dominium_game.exe --smoke-gui --gfx=soft --profile=baseline`
- Notes: Default baseline selection; uses `DOM_PLATFORM=win32` and `gfx=soft`.

**baseline win32 + dx9 (optional)**
- Configure: `cmake -S . -B build/codex_verify/baseline_win32_dx9 -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=C:/msys64/ucrt64/bin/cc.exe -DCMAKE_CXX_COMPILER=C:/msys64/ucrt64/bin/c++.exe -DDOM_DISALLOW_DOWNLOADS=ON -DFETCHCONTENT_FULLY_DISCONNECTED=ON -DFETCHCONTENT_UPDATES_DISCONNECTED=ON -DDOM_PLATFORM=win32 -DDOM_BACKEND_SOFT=OFF -DDOM_BACKEND_DX9=ON -DDOM_BACKEND_NULL=OFF`
- Build: `cmake --build build/codex_verify/baseline_win32_dx9 --target dgfx_demo dominium-launcher dominium_game`
- Verify:
  - `build/codex_verify/baseline_win32_dx9/dgfx_demo.exe --gfx=dx9 --frames=120`
  - `build/codex_verify/baseline_win32_dx9/source/dominium/launcher/dominium-launcher.exe --smoke-gui --gfx=dx9 --profile=baseline`
  - `build/codex_verify/baseline_win32_dx9/source/dominium/game/dominium_game.exe --smoke-gui --gfx=dx9 --profile=baseline`
- Notes: Presentation backend (D2); `--lockstep-strict=1` smoke paths force `gfx=soft`.

**baseline win32_headless + soft**
- Configure: `cmake -S . -B build/codex_verify/baseline_win32_headless_soft -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=C:/msys64/ucrt64/bin/cc.exe -DCMAKE_CXX_COMPILER=C:/msys64/ucrt64/bin/c++.exe -DDOM_DISALLOW_DOWNLOADS=ON -DDOM_PLATFORM=win32_headless -DDOM_BACKEND_SOFT=ON -DDOM_BACKEND_NULL=OFF`
- Build: `cmake --build build/codex_verify/baseline_win32_headless_soft --target domino_sys_smoke`
- Smoke: `build/codex_verify/baseline_win32_headless_soft/domino_sys_smoke.exe --smoke`
- Notes: Headless validation configuration; uses `DOM_PLATFORM=win32_headless` (no window/input facets).

**baseline null + null**
- Configure: `cmake -S . -B build/codex_verify/baseline_null_null -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=C:/msys64/ucrt64/bin/cc.exe -DCMAKE_CXX_COMPILER=C:/msys64/ucrt64/bin/c++.exe -DDOM_DISALLOW_DOWNLOADS=ON -DDOM_PLATFORM=null -DDOM_BACKEND_NULL=ON -DDOM_BACKEND_SOFT=OFF`
- Build: `cmake --build build/codex_verify/baseline_null_null --target dominium-launcher dominium_game`
- Notes: CI/headless baseline; use `dominium-launcher.exe --print-selection --gfx=null` to validate D0 selection.

### Tier-1 Rendering (Prompt 5)

**p5 win32 + soft (D0 reference)**
- Configure: `cmake -S . -B build/p5_soft -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=C:/msys64/ucrt64/bin/cc.exe -DCMAKE_CXX_COMPILER=C:/msys64/ucrt64/bin/c++.exe -DDOM_DISALLOW_DOWNLOADS=ON -DDOM_PLATFORM=win32 -DDOM_BACKEND_SOFT=ON -DDOM_BACKEND_DX9=OFF`
- Build: `cmake --build build/p5_soft`
- Verify: `build/p5_soft/dgfx_soft_hash_test.exe`
- Smoke: `build/p5_soft/dgfx_demo.exe --gfx=soft --frames=120 --print-selection`
- Notes: Canonical D0 pixel-hash baseline for DGFX minimal IR.

**p5 win32 + dx9 (present)**
- Configure: `cmake -S . -B build/p5_dx9 -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=C:/msys64/ucrt64/bin/cc.exe -DCMAKE_CXX_COMPILER=C:/msys64/ucrt64/bin/c++.exe -DDOM_DISALLOW_DOWNLOADS=ON -DDOM_PLATFORM=win32 -DDOM_BACKEND_SOFT=OFF -DDOM_BACKEND_DX9=ON`
- Build: `cmake --build build/p5_dx9`
- Smoke: `build/p5_dx9/dgfx_demo.exe --gfx=dx9 --frames=120 --print-selection`
- Notes: Presentation backend (D2); `--lockstep-strict=1` should refuse it during selection.

### Tier-2 Coverage (Prompt 6) — compile-gated native-host backends

Tier-2 backends are **compile-gated**: they are only built when explicitly enabled *and* the host OS + system dependencies are present. Selecting an incompatible backend fails at configure time with a clear message.

The build system performs **no downloads** (`DOM_DISALLOW_DOWNLOADS=ON` / `DOM_DISALLOW_DOWNLOADS` defaults to ON).

**Tier-2 platforms (DOM_PLATFORM)**
- `posix_x11`: UNIX host + X11 development headers/libs.
- `posix_wayland`: UNIX host + `wayland-client` headers/libs + protocol headers (`wayland-client-protocol.h`, `xdg-shell-client-protocol.h`).
- `cocoa`: Apple host (macOS) + Cocoa/AppKit/Foundation frameworks (enables Objective-C only when selected).

**Tier-2 renderers (DOM_BACKEND_*)**
- `DOM_BACKEND_DX11`: Windows-only; requires Windows SDK libs (`d3d11`, `dxgi`, `d3dcompiler_47` or `d3dcompiler`).
- `DOM_BACKEND_GL2`: Windows-only (WGL path); requires OpenGL headers + `opengl32`.
- `DOM_BACKEND_VK1`: any host with Vulkan SDK/loader discoverable via `find_package(Vulkan)` (no downloads).
- `DOM_BACKEND_METAL`: Apple-only; links Metal/MetalKit/QuartzCore (enables Objective-C++ only when selected).

**Example tier-2 Windows configs**
- `p6 win32 + dx11`:
  - Configure: `cmake -S . -B build/p6_dx11 -G Ninja -DCMAKE_BUILD_TYPE=Debug -DDOM_PLATFORM=win32 -DDOM_BACKEND_DX11=ON`
  - Build: `cmake --build build/p6_dx11`
- `p6 win32 + gl2`:
  - Configure: `cmake -S . -B build/p6_gl2 -G Ninja -DCMAKE_BUILD_TYPE=Debug -DDOM_PLATFORM=win32 -DDOM_BACKEND_GL2=ON`
  - Build: `cmake --build build/p6_gl2`

### Placeholders (to fill later)

- modern win32 + dx9/dx11/gl2
