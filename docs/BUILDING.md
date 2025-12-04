# Dominium — BUILDING & PLATFORM COMPILATION SPECIFICATION (v5)

This file is the **binding build contract** for all code under `/engine`, `/game`, `/tools`, `/tests`, and `/ports`. It reconciles the spec layer with the dev addenda (`docs/dev/dominium_new_build.txt`, `docs/dev/dominium_new_addendum.txt`, renderer/platform specs, and the `/ports` rules).

---

## 0. SCOPE
- Canonical build system layout and responsibilities.
- Supported toolchains and language levels.
- Deterministic build modes and flags.
- Platform, renderer, and audio backend policies.
- Determinism validation, UPS/FPS policies, and outputs.
- Prohibitions that protect the tick-deterministic core.

---

## 1. BUILD SYSTEM ARCHITECTURE

### 1.1 Primary build system — CMake
- **Minimum CMake version: 3.15.**
- Sole authority for `/engine`, `/game`, `/tools`, `/tests`, `/packaging`.
- **No globbing**; all sources are explicitly listed.
- All options live in the root `CMakeLists.txt` and are mirrored under `/build/cmake/modules/`.
- **CMake cache must never download dependencies**; all third-party code comes from `/external` (or `/third_party` if present) with pinned hashes.

#### /build layout (canonical)
```
/build/
  README.md
  cmake/
    toolchains/   # win32_msvc, win32_mingw, linux_gcc, macos_clang, dos_watcom, win9x_mingw32
    modules/      # DominiumPlatform, DominiumDeterminism, DominiumThirdParty, DominiumTesting, LegacySupport
    presets/      # debug, release, retro_lowmem, headless
  scripts/        # build_all, package_release, generate_version_header, lint_sources
  output/         # ignored; ephemeral per-platform artifacts and logs
```
- **Retro targets** (DOS, Win3.x, Win9x, macOS Classic) may use dedicated makefiles under `/ports/*/config`, but must not add new directory structure.

#### Required CMake cache variables
- `DOM_PLATFORM` = `win32` | `macosx` | `posix_headless` | `posix_x11` | `posix_wayland` | `sdl1` | `sdl2`
- `DOM_RENDER_BACKEND` = `software` | `dx9` | `dx11` | `dx12` | `gl1` | `gl2` | `vk1`
- `DOM_AUDIO_BACKEND` = `null` | `sdl` | `openal`
- `DOM_BUILD_MODE` = `Debug` | `Release` | `DeterministicRelease`
- `DOM_HEADLESS` = `ON` | `OFF`
- `DOM_CANONICAL_UPS` = {1, 2, 5, 10, 20, 30, 45, 60, 90, 120, 180, 240, 500, 1000}
- `DOM_LTO` = `ON` | `OFF` (see §8)
- `DOM_SFN_MODE` = `ON` | `OFF` (retro 8.3 enforcement)

### 1.2 Hard layering (renderer / platform / engine split)
- `/engine/core`, `/engine/sim`, `/engine/spatial`, `/engine/path`, `/engine/physics`, `/engine/ecs`, `/engine/net` **must not include** OS, windowing, graphics, or audio headers.
- Only `/engine/platform/**` may include OS headers.
- Only `/engine/render/**` may include graphics API headers.
- Audio backends live under `/engine/audio/**` and follow the same isolation.

### 1.3 Retro build layer
- Applies only to `/ports/*`.
- Enforces: 8.3 filenames, no dynamic linking, reduced feature surface, deterministic fixed-point math, and stubs for unsupported modules.

---

## 2. COMPILERS, LANGUAGE LEVELS, AND TOOLCHAINS

| Target                      | Compilers (minimum)                         |
|-----------------------------|---------------------------------------------|
| Win NT 2000–11              | MSVC 2010+, MinGW-w64, clang-cl             |
| Win NT 2000-only            | MSVC 2010 + legacy SDK                      |
| Linux (glibc ≥ 2.5)         | GCC 4.8+, Clang 3.2+                        |
| macOS 10.6–10.14            | Apple Clang / GCC-Apple                     |
| macOS 10.15+                | Modern Clang (when enabled)                 |
| DOS / Win3.x / Win9x        | OpenWatcom 1.9+ (retro makefiles)           |

Language constraints:
- `/engine/core` and `/engine/sim`: **strict C89**.
- Other engine modules: **strict C++98** (no C++11/C99 features).
- Fast-math and non-standard extensions **forbidden** outside renderer/audio backends.
- SIMD: **SSE2 baseline only**; no AVX/NEON/AVX512 in deterministic builds.

Toolchain files under `/build/cmake/toolchains/` must set the above and pin all compiler versions.

---

## 3. BUILD MODES

### 3.1 Debug
- No optimisation; full assertions and logging; determinism checks may be relaxed but ordering rules still apply.

### 3.2 Release
- O2/O3 optimisations; reduced logging; fast-math permitted **only inside renderer/audio backends**; not authoritative for simulation.

### 3.3 DeterministicRelease (DR)
- Authoritative gameplay mode; must be bit-stable across platforms.
- Fixed-point math in simulation; no fused ops; identical flags across platforms; no link-time function reordering for sim entrypoints.
- Output binaries must produce identical simulation behaviour on Win2000, Win11, Linux, macOS given identical inputs and mod/data sets.

---

## 4. PLATFORM TARGETS & BACKEND ROADMAP

### 4.1 MVP (Phase 1)
- Platform backend: `dom_platform_win32`
- Renderer backend: `dom_render_dx9` (vector-only; wireframe 3D)
- Audio backend: `dom_audio_null`
- OS: Windows NT 2000 SP4 → Windows 11
- Headless server builds use the same platform layer without renderer/audio.

### 4.2 Post-MVP (Phase 2)
- Platform: `dom_platform_win32_sdl2`
- Renderers: DX11, GL1, GL2, Software
- Audio: SDL_mixer, OpenAL Soft

### 4.3 Linux/macOS (Phase 3)
- Platform: `dom_platform_posix_sdl2`, `dom_platform_macos_cocoa` (or _sdl2)
- Renderers: GL2, Vulkan, Software

### 4.4 Retro (Phase 4)
- Platforms: `/ports/dos`, `/ports/win3x`, `/ports/win9x`, `/ports/macos_classic`
- Renderers: GL1 (where possible) or Software
- Must respect 8.3 naming, memory limits, and stubbed features.

Backend selection is runtime-driven through the backend registry (see `/engine/render/dom_render_backend.h` and addendum), never by ad-hoc compile-time ifdefs.

### 4.5 Canonical binaries (names)
- Launchers (software renderer, vector UI): `dom_launcher-win32-software.exe`, `dom_launcher-posix-sdl2-software`, `dom_launcher-macosx-software`.
- Windows clients: `dom_client-win32-dx11.exe`, `dom_client-win32-dx9.exe`, `dom_client-win32-software.exe`; servers: `dom_server-win32-headless.exe`.
- Linux/Posix clients: `dom_client-posix-sdl2-gl2`, `dom_client-posix-sdl2-vk1`, `dom_client-posix-sdl2-software`; servers: `dom_server-posix-headless`.
- macOS clients: `dom_client-macosx-gl2`, `dom_client-macosx-software`; servers: `dom_server-macosx-headless` (or `dom_server-posix-headless`).
- Headless flag (`DOM_HEADLESS`) disables window/context creation; render mode (`DOM_RENDER_MODE_VECTOR_ONLY` vs `FULL`) is a runtime flag per view/renderer.

---

## 5. RENDERER AND AUDIO BACKEND POLICY
- All renderer backends expose `DomRenderBackendAPI` (`dom_render_api.h`), consume `DomDrawCommandBuffer`, and report capabilities via `dom_render_caps`.
- Backends must honour `dom_render_config.mode`: `VECTOR_ONLY` draws vector/text primitives and replaces sprites/tiles with deterministic placeholders; `FULL` enables textured paths when `supports_textures=1`.
- All platform backends expose only `dom_platform.h`; renderer creation uses platform-provided handles.
- Audio backends implement `dom_audio_backend.h` and consume deterministic audio command buffers; no audio logic in `/engine/sim`.
- Renderer/audio code **never** mutates simulation state or tick timing.

---

## 6. THREADING, UPS/FPS, AND RUNTIME LOOPS
- Simulation runs single-threaded and deterministic. Background threads permitted only for asset loading, shader/audio preprocessing, editor tasks, or async I/O, and must not mutate sim state.
- UPS options (canonical): 1, 2, 5, 10, 20, 30, 45, 60, 90, 120, 180, 240, 500, 1000. Default set via `DOM_CANONICAL_UPS`.
- FPS options: fixed list plus `vsync` and `match_UPS`; rendering never dictates simulation tick rate.
- On insufficient CPU, simulation slows deterministically; UPS is not auto-changed.

---

## 7. DETERMINISM REQUIREMENTS
- No OS API calls in deterministic modules.
- No floating point in `/engine/core` or `/engine/sim`; fixed-point only.
- Identical compiler flags across platforms for deterministic modules; no `-ffast-math`, `-march=native`, or unordered optimisations.
- Deterministic archives/static libs: fixed file order, stripped timestamps for DR builds.
- All schema, component layouts, and serialization formats are versioned; unknown blocks must be skipped, not rejected.
- Build scripts **must not fetch** network dependencies. All hashes live under `/external/pin/` (or equivalent).
- Retro builds enforce `DOM_SFN_MODE=ON` and avoid dynamic linking.

---

## 8. OPTIONAL EXTENSIONS
- **LTO:** Allowed only after cross-toolchain reproducibility is proven; forbidden in DR until bit-identical output is demonstrated for MSVC/Clang/GCC.
- **SIMD:** SSE2 allowed; all later SIMD families are disabled in DR builds.

---

## 9. OUTPUTS
- Executables: `dom_client`, `dom_server`, `dom_hclient`, `dom_tools_editor`, `dom_tools_converter` (names may vary per target but must be declared in CMake explicitly).
- Data packs: base, DLC, graphics/sound/music packs; built deterministically.
- Retro images: DOS floppy (1.44MB), Win3.x ZIP, Win9x ISO, macOS Classic SMI; all 8.3 mapped.
- Packaging layouts live under `/packaging/**` and must follow `/package/common/layout` schema; no build products live in `/package`.

---

## 10. ENVIRONMENT VARIABLES
- `DOM_FORCE_DETERMINISTIC=1` — forces DR behaviours.
- `DOM_BUILD_PLATFORM` / `DOM_BUILD_RENDERER` — explicit backend selection.
- `DOM_ASSET_PATH_OVERRIDE` — optional asset override for tools (not used in DR runs).
- `DOM_DISABLE_BACKENDS` — comma-separated backend deny-list for debug.
- `DOM_SFN_MODE=1` — enforce 8.3 naming for retro/ports.

---

## 11. BUILD VERIFICATION & CI
- **Determinism hash** emitted per build from: binary, serialization schemas, component layouts, tick pipeline config, constants, and merge rules.
- **Replay cross-checks:** identical replays must produce identical hashes on Windows, Linux, macOS.
- **API boundary validation:** CI checks that OS headers appear only in `/engine/platform/**` and graphics headers only in `/engine/render/**`; sanitizers must not report UB in deterministic code paths.
- **Spec validation:** `/build/scripts/validate_specs.py` ensures `/docs/spec` is internally consistent and matches schema IDs used by serializers.
- **Third-party validation:** `/build/scripts/verify_hashes.py` and `/external/pin/` hashes must pass.

---

## 12. FUTURE-PROOFING
- New platforms are added by new `/engine/platform/*` backends only; engine/sim code must not change for platform bring-up.
- New renderers/audio backends plug into existing vtables with no engine API changes.
- Multi-surface/planet/system/galaxy/universe support must not require new build flags.
- Headless server clusters use the same DR binaries with `DOM_HEADLESS=ON`.

---

## 13. SUMMARY (QUICK REFERENCE)
- CMake is canonical; no auto-fetching; explicit sources.
- Core/sim = C89; rest of engine = C++98; no C99/C++11.
- DR mode is authoritative; identical flags across platforms; SSE2 max.
- MVP: Win32 + DX9 renderer + null audio.
- Platform/render/audio separation is strict and enforced by build/CI.
- Retro builds live under `/ports`; 8.3 names and no dynamic linking.
- Packaging is separate (`/packaging/**`); build outputs stay under `/build/output`.
