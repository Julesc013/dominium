# Build Matrix (Prompt 3)

This document enumerates the canonical build configurations used for local development and CI validation. The intent is to keep the baseline toolchain (C89/C++98) always buildable and to provide explicit opt-in for “modern” acceleration layers.

## Matrix Entries

### Baseline (Windows)

**baseline win32 + soft**
- Configure: `cmake --preset baseline-debug`
- Build: `cmake --build --preset baseline-debug`
- Notes: Default baseline selection; uses `DOM_PLATFORM=win32` and `gfx=soft`.

**baseline win32_headless + soft**
- Configure: `cmake -S . -B build/codex_verify/baseline_win32_headless_soft -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=C:/msys64/ucrt64/bin/cc.exe -DCMAKE_CXX_COMPILER=C:/msys64/ucrt64/bin/c++.exe -DDOM_DISALLOW_DOWNLOADS=ON -DDOM_PLATFORM=null -DDOM_BACKEND_SOFT=ON -DDOM_BACKEND_NULL=OFF`
- Build: `cmake --build build/codex_verify/baseline_win32_headless_soft --target dominium-launcher`
- Notes: Headless validation configuration; currently uses `DOM_PLATFORM=null` (future: dedicated win32 headless platform backend).

**baseline null + null**
- Configure: `cmake -S . -B build/codex_verify/baseline_null_null -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=C:/msys64/ucrt64/bin/cc.exe -DCMAKE_CXX_COMPILER=C:/msys64/ucrt64/bin/c++.exe -DDOM_DISALLOW_DOWNLOADS=ON -DDOM_PLATFORM=null -DDOM_BACKEND_NULL=ON -DDOM_BACKEND_SOFT=OFF`
- Build: `cmake --build build/codex_verify/baseline_null_null --target dominium-launcher`
- Notes: CI/headless baseline; use `dominium-launcher.exe --print-selection --gfx=null` to validate D0 selection.

### Placeholders (to fill later)

- baseline win32 + dx9
- baseline win32 + dx11
- baseline win32 + gl2
- modern win32 + dx9/dx11/gl2

