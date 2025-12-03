# Dominium — BUILDING & PLATFORM COMPILATION SPECIFICATION (v4)

This document defines the **authoritative rules** for:

- Build system structure  
- Toolchains and compilers  
- Deterministic build modes  
- Platform and renderer backends  
- Threading and scheduling constraints  
- UPS/FPS policies  
- Packaging outputs  
- Prohibitions and required invariants  

This file binds all modules under:

- `/engine`
- `/game`
- `/tools`
- `/tests`
- `/ports`

This version incorporates and supersedes earlier texts by enforcing the **Platform/Renderer/Engine Split** defined in:

docs/dev/dominium_new_addendum.txt

markdown
Copy code

---

# 1. BUILD SYSTEMS (CANONICAL)

Dominium uses a **single, authoritative build system**:

## 1.1 Primary Build System — CMake

- **Minimum CMake version: 3.15**
- CMake is the only official build system for:
  - `/engine`
  - `/game`
  - `/tools`
  - `/tests`
  - `/packaging`

### CMake Requirements

All CMake modules must follow:

- **Explicit file lists (no globbing)**
- **Identical compiler flags across platforms for deterministic builds**
- **All configuration options registered in root `CMakeLists.txt`**

Supported CMake variables:

DOM_PLATFORM=<win32|win32_sdl2|posix_sdl2|macos_cocoa|retro>
DOM_RENDER_BACKEND=<dx9|dx11|gl1|gl2|vk1|dx12|software>
DOM_AUDIO_BACKEND=<sdl|openal|null>
DOM_BUILD_MODE=<Debug|Release|DeterministicRelease>
DOM_HEADLESS=<ON|OFF>
DOM_CANONICAL_UPS=1..1000
DOM_LTO=<ON|OFF>
DOM_SFN_MODE=<ON|OFF>

yaml
Copy code

### Hard Separation Rules (Addendum Integration)

- No `/engine/sim` or `/engine/core` file may reference:
  - Win32, SDL, X11, Cocoa, Android, Vulkan, OpenGL, DirectX, etc.
- Only `/engine/platform/*` may include OS headers.
- Only `/engine/render/*` may include graphics headers (DX, GL, VK, etc.).
- All build definitions must strictly reflect this.

---

## 1.2 Secondary Build Systems (Retro)

Retro platforms do **not** use CMake:

### Retrobuild Layer (for `/ports`)
- Used for:
  - DOS (Watcom)
  - Windows 3.x (OpenWatcom)
  - Windows 9x (OpenWatcom + DX8/GL1)
  - macOS Classic (MPW/CodeWarrior)
- Must respect:
  - 8.3 SFN filenames
  - No dynamic linking
  - Reduced feature surface
  - Stubs for unsupported modules

Retro builds may not add new directories or modify `/engine`.

---

# 2. COMPILERS & TOOLCHAINS

## 2.1 Supported Compilers (MVP First)

| Platform             | Compilers                                    |
|----------------------|-----------------------------------------------|
| Windows NT 2000–11   | MSVC 2010+, MinGW-w64, clang-cl               |
| Windows NT 2000-only | MSVC 2010 (with legacy SDK)                   |
| Linux (glibc ≥ 2.5)  | GCC 4.8+, Clang 3.2+                           |
| macOS 10.6–10.14     | Apple Clang / GCC-Apple                       |
| macOS 10.15+         | Modern Clang (later phases)                   |
| DOS / Win3.x / 9x    | OpenWatcom 1.9+ (retro build system)          |

### Deterministic Core Requirements

- `/engine/core` and `/engine/sim` must compile under **strict C89**.  
- All other engine modules may use **strict C++98**, no later.  
- No C99/C11/C++11 features allowed.

---

# 3. BUILD MODES

Dominium defines three build modes:

## 3.1 Debug
- No optimisation
- Full assertions
- Full logging
- Development-only

## 3.2 Release
- O2/O3 optimisations
- Reduced logging
- Fast-math allowed *only in renderer code*
- Not used for authoritative simulation

## 3.3 DeterministicRelease (DR)
**This is the canonical mode for actual gameplay simulation.**

Mandatory constraints:

- Simulation uses **fixed-point**, not FP
- No FMA or fused operations
- No unsafe math optimisations
- No CPU-specific vectorisation except **SSE2 baseline**
- Identical compiler flags across platforms
- No link-time reordering of functions used by sim

DR builds across Win2000, Win11, Linux, macOS must produce **bit-identical simulation behaviour**.

---

# 4. PLATFORM TARGETS & BACKENDS

This section replaces earlier platform descriptions with the new backend model.

## 4.1 Phase 1 (MVP Required)
Only the following configuration is officially supported during MVP:

- **Platform backend:** `dom_platform_win32`  
- **OS target:** Windows NT 2000 SP4 → Windows 11  
- **Renderer backend:** `dom_render_dx9`  
- **Audio backend:** `null` (optional SDL later)

No other platforms/renderers may be compiled or used during MVP until the MVP core is complete.

## 4.2 Phase 2 (Post-MVP Early)
- Platform: `dom_platform_win32_sdl2`
- Renderer: DX11, GL1, GL2 (via SDL2), Software

## 4.3 Phase 3 (Linux/macOS)
- Platform: `dom_platform_posix_sdl2`, `dom_platform_macos_cocoa`
- Renderer: GL2, Vulkan, Software

## 4.4 Phase 4 (Retro)
- Platforms under `/ports` (DOS, Win3.x, Win9x, macOS Classic)
- Renderers: GL1, Software
- Must comply with 8.3 naming + component stubs

---

# 5. RENDERING BACKENDS (UPDATED)

This section replaces earlier listings.

### 5.1 Renderer API (Canonical)

All renderer backends must implement the API defined in:

/engine/render/dom_render_api.h
docs/dev/dominium_new_addendum.txt

yaml
Copy code

### 5.2 MVP Renderer Set

Only one backend is required for MVP:

- **Direct3D 9.0c (dom_render_dx9)**  
  - No fixed-function; shader path only  
  - Compatible with Windows 2000 → 11  
  - Must support:
    - 2D vector primitives
    - 3D wireframe primitives

### 5.3 Future Renderer Backends

May be added after MVP:

- DX11
- DX12
- OpenGL 1.1
- OpenGL 2.0
- Vulkan 1.x
- Software (CPU)

All must follow the standard backend vtable defined in `dom_render_api.h`.  
All capability probing is runtime, not compile-time.

---

# 6. AUDIO BACKENDS

### MVP:
- `null` (no sound)

### Post-MVP:
- SDL2_mixer
- OpenAL Soft

Audio backends must follow the platform/renderer separation.  
No audio code may appear in `/engine/sim`.

---

# 7. THREADING & MULTICORE RULES

Simulation thread is **single and deterministic**.

Allowed background threads:

- Asset loading  
- Shader compilation  
- Editor-only tasks  
- Async file IO  

Prohibitions:

- No engine/sim mutation from background threads  
- No job stealing  
- No OS thread priorities or dynamic scheduling in sim  

All inter-thread messages must be ordered deterministically.

---

# 8. UPS & FPS RULES

UPS and FPS are runtime-configurable but reflected in build metadata.

### UPS Options:
1, 2, 5, 10, 20, 30, 45, 60, 90, 120, 180, 240, 500, 1000, unlimited

shell
Copy code

### FPS Options:
18, 24, 25, 30, 48, 50, 60, 75, 90, 120, 150, 180, 240, 500, 1000,
unlimited, vsync, match_UPS

yaml
Copy code

Simulation slows gracefully if CPU cannot maintain UPS.  
Rendering does **not** affect simulation tick rate.

---

# 9. PACKAGE OUTPUTS

CMake must generate:

### 9.1 Executables
- `dom_client`
- `dom_server`
- `dom_hclient`
- `dom_tools_editor`
- `dom_tools_converter`

### 9.2 Data Packs
- Base game
- DLC packs
- Graphics/sound/music packs

### 9.3 Retro Images (Phase 4)
- DOS floppy (1.44MB)
- Win9x ISO
- Win3.x ZIP package

All using 8.3 filenames from mapping tables.

---

# 10. BUILD RESTRICTIONS (UPDATED)

- NO rendering API calls outside `/engine/render/**`.
- NO OS API calls outside `/engine/platform/**`.
- NO dynamic symbol lookup in sim code.
- NO dependence on filesystem case sensitivity.
- NO C99/C11/C++11 features anywhere in engine.
- NO AVX/AVX2/AVX512 in deterministic builds.
- NO backends may create more than one rendering thread.

Renderer and platform backends must not interfere with simulation determinism.

---

# 11. OPTIONAL EXTENSIONS

### 11.1 LTO
Allowed only when build reproducibility is verified across:
- MSVC
- Clang
- GCC

Forbidden in DeterministicRelease builds unless cross-platform bit-identical.

### 11.2 SIMD
- Allowed: SSE2
- Forbidden: SSE3+, AVX, NEON, AVX512 in DR mode

---

# 12. ENVIRONMENT VARIABLES

DOM_FORCE_DETERMINISTIC=1
DOM_BUILD_PLATFORM=<backend>
DOM_BUILD_RENDERER=<backend>
DOM_ASSET_PATH_OVERRIDE=<path>
DOM_DISABLE_BACKENDS=<list>
DOM_SFN_MODE=<1|0>

yaml
Copy code

---

# 13. BUILD VERIFICATION

Every build outputs:

### 13.1 Determinism Hash
Generated from:
- Engine binary
- Serialization schema
- Component layouts
- Tick pipeline configuration
- Constants, merge rules

### 13.2 Cross-Platform Replay Test
Same replay must produce same hash across:
- Windows
- Linux
- macOS

### 13.3 API Boundary Validation
- No forbidden OS headers in simulation modules
- No graphics headers outside render backends
- No data races or UB detectable via sanitizers

### 13.4 Build Metadata
Stored in:
build_info.json

yaml
Copy code

---

# 14. FUTURE-PROOFING

The build system must:

- Accept new renderers (DX11, Vulkan, Metal) without rewriting engine code.
- Accept new platform targets by adding new `/engine/platform/*` directories only.
- Preserve determinism across all expansions.
- Handle multi-surface, multi-planet, multi-galaxy worlds with no new build flags.
- Allow headless server clusters.

---

# 15. SUMMARY (FOR CODEGEN)

- Engine deterministic core = C89.
- Non-core modules = C++98.
- CMake is canonical.
- Platform and renderer layers strictly separated.
- MVP build = Win32 + DX9 only.
- All rendering is vector-only in MVP.
- DeterministicRelease mode is required for real gameplay.
- No directory additions beyond DIRECTORY_CONTEXT.md.
- All backends are modular and pluggable through vtables.
- Retro builds isolated under `/ports`.

End of BUILDING.md.