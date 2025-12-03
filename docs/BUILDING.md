# Dominium — BUILDING & PLATFORM COMPILATION SPECIFICATION (v3)

This document defines the complete and authoritative rules governing:
- Build system hierarchy
- Toolchains and compilers
- Deterministic build modes
- Platform targets (current + future + retro)
- Rendering and audio backend selection
- Threading and scheduling constraints
- UPS/FPS behaviour during compilation targets
- Packaging outputs
- Restrictions, prohibitions, and allowed optimisations

This file is binding for every module in `/engine`, `/game`, `/tools`, `/ports`.

---

# 1. BUILD SYSTEMS (CANONICAL)

Dominium uses a *multi-layered build architecture*:

## 1.1 Primary Build System — CMake
- Minimum CMake version: **3.15**
- CMake is authoritative; other build systems are secondary wrappers.
- Must generate:
  - MSVC solutions
  - Makefiles
  - Ninja files
  - Xcode bundles (for macOS 10.6–10.14 via legacy toolchains)

### CMake Requirements
- Each module must declare **include paths, sources, and dependencies explicitly**.
- No globbing; file lists must be explicit for determinism.
- All options must be configurable from root `CMakeLists.txt`:
  - `DOM_PLATFORM=<win32|linux|macos|retro>`
  - `DOM_RENDER_BACKENDS=<dx9;gl1;gl2;sdl1;sdl2;software>`
  - `DOM_AUDIO_BACKENDS=<sdl;openal;null>`
  - `DOM_BUILD_MODE=<Debug|Release|DeterministicRelease>`
  - `DOM_CANONICAL_UPS=1..240`
  - `DOM_HEADLESS=<ON|OFF>`
  - `DOM_LTO=<ON|OFF>`

---

## 1.2 Secondary Build Systems
Provided for legacy or retro targets:

### 1.2.1 MSVC Project Files (Windows 2000 → Windows 11)
- Visual Studio 6.0 supported for C89 engine core
- Visual Studio 2010 supported for C++98 modules
- All build settings must match CMake output options

### 1.2.2 GNU Make (Linux / POSIX)
- For minimal environments (headless servers, CI sanity tests)
- Must mirror CMake’s determinism flags

### 1.2.3 Retrobuild (DOS / Win3.x / Win9x)
- Uses Watcom/OpenWatcom for DOS/Win3.x/Win9x
- Uses custom `retro_make.bat` or `retro_build.sh`
- SFN filenames enforced (8.3)
- Unsupported modules must be stubbed deterministically

---

# 2. COMPILERS AND TOOLCHAINS

## 2.1 Mandatory Supported Compilers
| Platform | Compilers |
|----------|-----------|
| Windows 2000+ | MSVC 6.0, 2008, 2010, mingw32 |
| Linux (glibc ≥ 2.5) | GCC 3.4+, GCC 4.8+, Clang 3.2+ |
| macOS 10.6–10.14 | GCC-Apple, Clang-Legacy |
| macOS 10.15+ | Clang modern (via later port) |
| DOS / Win3.x | OpenWatcom 1.9+ |
| WebAssembly | Emscripten (future) |

---

# 3. BUILD MODES

Dominium has **three canonical build modes**:

## 3.1 Debug Mode
- No optimisations
- Assertions enabled
- Verbose logging
- Slow but safe

## 3.2 Release Mode
- Standard O2/O3 optimisations
- Logging minimal
- Floating point fast-math allowed where deterministic

## 3.3 DeterministicRelease (DR)
**This is the authoritative runtime build for simulation correctness.**

### Requirements
- Strict IEEE FP behaviour
- No fused-multiply-add unless identical across platforms
- No CPU-specific vectorisation unless identical semantics (SSE2 baseline)
- All math flags must be fixed, no per-file variability
- No link-time code reordering that changes instruction sequences affecting FP

### This mode must produce bit-identical outcomes across:
- Windows 2000, XP, 7, 10, 11
- macOS 10.6–10.14
- Linux distros
- Headless server builds
- Retro builds (where features are present)

---

# 4. PLATFORM TARGETS

## 4.1 Stage 1 (Guaranteed)
- Windows 2000+
- macOS 10.6+
- Linux desktop/server

## 4.2 Stage 2 (Retro Support)
- Windows 98 SE
- Windows ME / 2000 / XP
- Windows NT 3.51 / NT 4 (future)
- macOS 7–9 (Classic)
- DOS (DPMI)
- Linux 2.x with GCC 2.95/3.x

## 4.3 Stage 3 (Extended/Future)
- Android (via SDL)
- iOS (Metal renderer abstraction layer needed)
- WebAssembly
- Consoles (Switch/PS2+ via custom ports)

---

# 5. GRAPHICS BACKEND BUILD RULES

## 5.1 Supported Backends (Stage 1)
- **SDL1 (software and GL1.1)**
- **SDL2 (GL1/GL2)**
- **DirectX 9.0c (shader path only, no FFP)**
- **OpenGL 1.1 (fixed pipeline)**
- **OpenGL 2.0 (programmable pipeline)**

Rendering backends must compile under every platform where supported.

### Backend Inclusion Flags
- `DOM_BUILD_DX9=ON|OFF`
- `DOM_BUILD_GL1=ON|OFF`
- `DOM_BUILD_GL2=ON|OFF`
- `DOM_BUILD_SDL1=ON|OFF`
- `DOM_BUILD_SDL2=ON|OFF`
- `DOM_BUILD_SOFTWARE=ON|OFF`

### Requirements
- A user may build any subset.
- Launcher auto-selects valid backend.
- Engine cannot assume features: must probe at runtime.

---

# 6. AUDIO BACKENDS

Supported:
- SDL_mixer
- OpenAL Soft
- Null backend (headless)

Compiled independently of rendering.

---

# 7. THREADING & MULTICORE RULES

## Deterministic work scheduling:
- Simulation must run in a *single deterministic thread*.
- Background threads may:
  - load assets
  - compile shaders
  - prepare geometry
  - handle async file operations

But:
- No background thread may mutate simulation state.
- No work-stealing, no priority heuristics.
- All inter-thread messages must be time-stamped and delivered deterministically.

---

# 8. UPS/FPS COMPILATION RULES

During build configuration, the developer may fix:
- **Canonical UPS:** {1,2,5,10,20,30,45,60,90,120,180,240}
- **Max FPS:** {24,25,30,48,60,75,90,120,150,180,240}

Simulation slows gracefully if CPU cannot maintain UPS.

Renderer runs independently.

These values must be visible as CMake variables and embedded into build metadata.

---

# 9. PACKAGE OUTPUTS

CMake must generate:

## 9.1 Executables
- `dom_client`
- `dom_server`
- `dom_hclient` (headless client)
- `dom_tools_editor`
- `dom_tools_converter`

## 9.2 Data Packs
- Base game pack
- DLC packs
- Graphics/sound/music packs

## 9.3 Retro Images
- DOS floppy (1.44 MB)
- Win9x CD-ROM (ISO9660)
- Win3.x installation ZIP
- All respecting 8.3 filenames generated from mapping table

---

# 10. BUILD RESTRICTIONS

- No non-deterministic compiler optimisations in DR mode.
- No backend may force more than one rendering thread.
- No module may include OS headers except inside `/engine/platform`.
- No code may rely on filesystem case sensitivity.
- No dynamic symbol lookup (e.g., dlsym) in simulation code.
- No reliance on C99/C11 features.

---

# 11. OPTIONAL BUILD EXTENSIONS

## 11.1 LTO (Link-Time Optimisation)
Allowed only if:
- Identical results across toolchains
- DeterministicRelease forbids LTO unless verified safe

## 11.2 SIMD
Allowed only if:
- Instructions sets identical across target platforms
- SSE2 baseline only
- No AVX, AVX2, AVX-512 in DR builds

---

# 12. ENVIRONMENT VARIABLES FOR BUILD PIPELINES

- `DOM_FORCE_DETERMINISTIC=1`
- `DOM_BUILD_PLATFORM=win32/linux/macos/...`
- `DOM_ASSET_PATH_OVERRIDE=<path>`
- `DOM_DISABLE_BACKENDS=<list>`
- `DOM_SFN_MODE=1` for retro 8.3 output

---

# 13. BUILD VERIFICATION

Every build must include:

## 13.1 Determinism Test
- Replays must match hashes across:
  - Windows
  - macOS
  - Linux
  - Headless server

## 13.2 API Surface Test
- No unauthorised platform headers appear in compiled units.
- All files comply with directory contract.

## 13.3 Diagnostics
- Dump build configuration to `build_info.json` inside package.

---

# 14. FUTURE-PROOFING

The build system *must* be structured so future expansions require no rearchitecture:

- Additional planets → no new build flags
- Additional renderers (DX11, Vulkan, Metal) → pluggable
- Retro ports (PS2, GameCube) → added under `/ports` with isolated toolchains
- Dedicated server scaling → additional headless binaries, no simulation changes

---

# 15. SUMMARY (REQUIRED FOR CODING)

- C89 for deterministic core verified across *all* targets.
- C++98 for non-core.
- CMake is canonical.
- DeterministicRelease is mandatory for real gameplay.
- Backends are optional and interchangeable.
- UPS/FPS settings belong to build metadata but runtime-overridable.
- Retro builds require strict 8.3 names and reduced features.
- Engine, game, tools, tests, mods, and data packs must compile separately.

End of BUILDING.md.
