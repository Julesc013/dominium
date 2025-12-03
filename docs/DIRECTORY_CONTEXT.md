# Dominium — DIRECTORY CONTEXT AND CONTRACT (V5)

This document is the authoritative contract for every top-level directory in the repository. It reconciles the spec layer with the dev addenda (`docs/dev/dominium_new_root.txt` and the per-directory dev specs). Anything that violates these rules is wrong, even if it builds.

---

## 0. TOP-LEVEL LAYOUT (CANONICAL)
- `/docs`
- `/engine`
- `/game`
- `/data`
- `/mods`
- `/tools`
- `/tests`
- `/external` (vendored sources/pins)  
- `/third_party` (if present; must follow `/external` rules)
- `/build`
- `/packaging`
- `/scripts`
- `/ports`

No other top-level directories may be used without updating this file first.

---

## 1. `/docs` — Documentation Only
### Purpose
Human-readable specifications, design volumes, legal text, and context packs.

### Allowed
Markdown, plaintext, diagrams (sources only). Subdirectories:
- `/docs/spec` — authoritative technical specs (`BUILDING.md`, `SPEC_CORE.md`, `DATA_FORMATS.md`, `DIRECTORY_CONTEXT.md`, `LANGUAGE_POLICY.md`, `STYLE.md`, `MILESTONES.md`).
- `/docs/design` — non-binding design narratives and volumes.
- `/docs/legal` — licences, EULA, TOS, attribution.
- `/docs/archive` — obsolete or historical material.
- `/docs/context` — LLM context packs and addenda (not authoritative).
- `/docs/dev` — detailed developer addenda (lower-level intent; conflicts must be resolved in `/docs/spec`).

### Prohibitions
No compiled binaries, game data assets, or source code compiled into the game.

---

## 2. `/engine` — Deterministic Engine Code
### Purpose
Platform-agnostic deterministic engine. Separation from OS, rendering, and audio is enforced by build and CI.

### Global rules
- `/engine/core` and `/engine/sim` are **C89** only; other engine modules **C++98** max.
- No OS/graphics/audio headers outside `/engine/platform`, `/engine/render`, `/engine/audio`.
- No floating point in authoritative sim/core; fixed-point only.
- No game-specific content or mod logic.

### Subdirectories
- `/engine/core` — types, log, mem, fp, rng, bits; deterministic primitives.
- `/engine/sim` — tick, lanes, events, jobs, world registry, networks (power/data/fluids/thermal), orbit (on rails), economy; serialization stubs for sim state.
- `/engine/spatial` — coordinate hierarchy, grid/chunk/subchunk/region registries, voxel storage, spatial index, read-only spatial queries.
- `/engine/path` — deterministic pathfinding (grid/navmesh), costs/heuristics, A*, traffic, route/cache utilities.
- `/engine/physics` — integer kinematics, AABB/shape tests, collision queries, spline/vehicle helpers; no high-fidelity physics.
- `/engine/ecs` — entity handles/generations, component registry, dense storage, archetypes, queries, system registration and fixed ordering.
- `/engine/net` — deterministic lockstep protocol, packet/channels, serialize/replay, client/server state machines; no sockets.
- `/engine/render` — render command buffer and backends (dx9, dx11, gl1, gl2, software, vector); only graphics headers here; no sim mutation.
- `/engine/audio` — audio command buffer and backends (null, SDL_mixer, OpenAL, DirectSound/XAudio2, software); no sim mutation.
- `/engine/ui` — retained UI tree, layout, widgets, skins, UI command buffer; no game rules or sim logic.
- `/engine/platform` — OS boundary: window/input/timing/filesystem/net transport/threads/dynlib/log sinks; only place for OS headers.
- `/engine/io` — save/load/replay/pack IO that implements `DATA_FORMATS.md`; deterministic serialization only.
- `/engine/modding` — mod loader/registry/bindings; sandboxed and deterministic.
- `/engine/api` — public API surface used by `/game` and tools; no OS headers.

### Prohibitions
No Dominium-specific content, mods, or assets; no rendering or audio calls outside their subdirs; no dynamic allocation in hot sim paths.

---

## 3. `/game` — Game Glue and Dominium-Specific Logic
### Purpose
Dominium-specific gameplay code built on the engine API.

### Subdirectories
- `/game/shared` — logic shared by client/server (worldgen defaults, archetypes, blueprints, transport rules, utilities, research, companies, workers).
- `/game/client` — client app shell, cameras/views, HUD/UI binding, input mapping, render/audio pipelines; uses engine APIs only; no OS headers.
- `/game/server` — dedicated server host; authoritative sim driver, net bridge, world IO, admin commands; no rendering/audio/UI.
- `/game/launcher` — OS entrypoints and runtime selection (platform/render/audio backends, configs, CLI parsing, hardware detection); thin wrapper only.

### Prohibitions
No platform headers (use `/engine/platform`), no renderer/audio backends, no deterministic core logic duplication.

---

## 4. `/data` — First-Party Game Data Packs
### Purpose
Canonical base content and official DLC/asset packs.

### Subdirectories
- `/data/base` — required base content; manifests plus prefabs, tech, networks, worldgen, economy, locale, optional deterministic scripts.
- `/data/dlc` — official DLCs; each with manifest and the same structure as base extensions.
- `/data/packs` — first-party graphics/audio/music packs; pack manifests and assets only (no sim rules).
- `/data/templates` — example universes, starter saves, scenarios, blueprint libraries, presets.
- `/data/schema` — machine-readable schemas for validation; mirrors `DATA_FORMATS.md`.

### Prohibitions
No engine code; no third-party mod content; no floating-point authoritative values; no reliance on directory scanning (manifests are explicit).

---

## 5. `/mods` — Third-Party and Local Mods
### Purpose
User/modder extensions. Not official content.

### Layout
- `/mods/local`, `/mods/workshop`, `/mods/disabled`.
- Each mod root contains `mod.json` and optional `data/`, `scripts/`, `gfx/`, `audio/`, `locale/`, `docs/`, `tests/`.

### Prohibitions
No engine/game source code; no auto-loaded native binaries; no OS/network/wallclock access from scripts; must obey determinism flags and schemas defined in `DATA_FORMATS.md` and modding spec.

---

## 6. `/tools` — Editors, SDKs, Pipelines, Debuggers
### Purpose
Non-runtime tooling (world/blueprint editors, SDK/codegen, asset pipelines, replay/inspection tools).

### Subdirectories
- `/tools/editor` — editors (world, blueprint, asset inspector, shared editor libs, plugins).
- `/tools/devkit` — schemas, codegen, mod SDK, validators, generators.
- `/tools/pipeline` — image/audio/model/shader converters, packagers.
- `/tools/debug` — profilers, inspectors, replay tools.
- `/tools/scripts` — helper scripts for tooling.

### Prohibitions
No simulation hot-path logic; tools may be non-deterministic internally but outputs must be deterministic for fixed inputs; must not silently modify `/engine`, `/game`, or `/data/base` without CI guardrails.

---

## 7. `/tests` — Tests Only
### Purpose
Unit, integration, replay, and perf tests that enforce determinism and stability.

### Subdirectories
- `/tests/unit` — per-module tests (C89/C++98 matching the module under test).
- `/tests/integration` — headless whole-engine runs with fixtures.
- `/tests/replay` — deterministic replay scenarios, baselines, fuzz inputs, replay tools.
- `/tests/perf` — micro/macro/soak benchmarks.

### Prohibitions
No OS randomness, no wallclock, no network access; no GPU/audio dependencies; no test assets outside approved fixtures.

---

## 8. `/external` and `/third_party` — Vendored Dependencies
### Purpose
Hermetic dependency depot: upstream sources, patches, integration shims, licenses, pins/hashes.

### Layout (canonical `/external`)
- `/external/src/<lib>/` — upstream, patches, integration shims, build notes.
- `/external/include/` — public headers.
- `/external/assets/` — test/reference assets.
- `/external/licenses/` — license texts and notices.
- `/external/pin/` — versions.json and hashes for reproducibility.

### Rules
- No engine code inside; no auto-fetching; no mixing Dominium source with vendor code.
- If `/third_party` exists, it must follow the same isolation and licensing rules.
- No GPL/copyleft dependencies in runtime engine; tool-only use must be isolated and documented.

---

## 9. `/build` — Build System Glue
### Purpose
CMake toolchains/modules/presets, build scripts, CI hooks, and ephemeral outputs.

### Layout
- `/build/cmake/toolchains` — pinned toolchain files.
- `/build/cmake/modules` — shared CMake logic (platform, determinism, third-party, testing, legacy support).
- `/build/cmake/presets` — debug/release/retro_lowmem/headless presets.
- `/build/scripts` — build helpers (build_all, package_release, generate_version_header, lint_sources, CI hooks).
- `/build/output` — ignored local artifacts/logs.

### Prohibitions
No engine/game code; no authoritative specs; no network fetching; no permanent outputs.

---

## 10. `/packaging` — Distribution Layouts
### Purpose
Installer/image definitions for Windows/Linux/macOS/retro targets; schemas and branding assets used by packaging scripts.

### Prohibitions
No engine/game code; no runtime determinism changes; no build outputs stored here.

---

## 11. `/scripts` — Repository Automation
### Purpose
Meta-automation, maintenance, analysis, doc generation, CI helpers, formatters.

### Prohibitions
Not part of runtime; must not silently alter `/engine`, `/game`, `/data/base`; must be explicit when modifying tracked files.

---

## 12. `/ports` — Alternative/Retro Targets
### Purpose
Experimental or legacy targets (DOS, Win3.x, Win9x, macOS Classic, WASM, consoles). Build isolation only; no engine redesign.

### Prohibitions
No simulation logic changes; must respect determinism; 8.3 filenames and memory limits for retro; no third-party SDKs stored in repo.

---

## 13. GENERAL RULES
1. Engine determinism lives in `/engine/core`, `/engine/sim`, `/engine/spatial`, `/engine/path`, `/engine/physics`, `/engine/ecs`, `/engine/net`; no OS or renderer/audio headers there.
2. Platform/renderer/audio separation is strict; only `/engine/platform/**`, `/engine/render/**`, `/engine/audio/**` may include those APIs.
3. Game-specific logic stays under `/game`; content under `/data`; mods under `/mods`; tooling under `/tools`; vendors under `/external` (and `/third_party` if used).
4. No binary or network protocol may be invented outside `DATA_FORMATS.md` and the dev addenda; all formats are versioned and deterministic.
5. New directories or structural changes require updating this file and the specs before use.

This directory contract is binding for all contributors and generators.
