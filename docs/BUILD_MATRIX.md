# Build Matrix (Prompt 3)

This document enumerates the canonical build configurations used for local development and CI validation. The intent is to keep the baseline toolchain (C89/C++98) always buildable and to provide explicit opt-in for “modern” acceleration layers.

## Matrix Entries

### Baseline (Windows)

**baseline win32 + soft**
- Configure: `cmake --preset baseline-debug`
- Build: `cmake --build --preset baseline-debug`
- Smoke: `build/baseline-debug/domino_sys_smoke.exe --smoke --print-selection`
- Notes: Default baseline selection; uses `DOM_PLATFORM=win32` and `gfx=soft`.

**baseline win32_headless + soft**
- Configure: `cmake -S . -B build/codex_verify/baseline_win32_headless_soft -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=C:/msys64/ucrt64/bin/cc.exe -DCMAKE_CXX_COMPILER=C:/msys64/ucrt64/bin/c++.exe -DDOM_DISALLOW_DOWNLOADS=ON -DDOM_PLATFORM=win32_headless -DDOM_BACKEND_SOFT=ON -DDOM_BACKEND_NULL=OFF`
- Build: `cmake --build build/codex_verify/baseline_win32_headless_soft --target dominium-launcher domino_sys_smoke`
- Smoke: `build/codex_verify/baseline_win32_headless_soft/domino_sys_smoke.exe --smoke --print-selection`
- Notes: Headless validation configuration; uses `DOM_PLATFORM=win32_headless` (no window/input facets).

**baseline null + null**
- Configure: `cmake -S . -B build/codex_verify/baseline_null_null -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=C:/msys64/ucrt64/bin/cc.exe -DCMAKE_CXX_COMPILER=C:/msys64/ucrt64/bin/c++.exe -DDOM_DISALLOW_DOWNLOADS=ON -DDOM_PLATFORM=null -DDOM_BACKEND_NULL=ON -DDOM_BACKEND_SOFT=OFF`
- Build: `cmake --build build/codex_verify/baseline_null_null --target dominium-launcher`
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

### Placeholders (to fill later)

- baseline win32 + dx11
- baseline win32 + gl2
- modern win32 + dx9/dx11/gl2
