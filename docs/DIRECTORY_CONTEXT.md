# Dominium — DIRECTORY CONTEXT AND CONTRACT (V4)

This document defines the **purpose, allowed contents, requirements, and prohibitions** for every major directory in the Dominium repository — current and planned.

This file is a contract for humans and code-generators. If code or data violates these rules, it is wrong.

All rules below are binding for Codex and all generators.

---

## 0. TOP-LEVEL LAYOUT (CANONICAL)

Top-level directories:

- `/docs`
- `/engine`
- `/game`
- `/data`
- `/mods`
- `/tools`
- `/tests`
- `/third_party`
- `/build`
- `/packaging`
- `/scripts`
- `/ports`

Each top-level dir has hard responsibilities described below.

---

## 1. `/docs` — Documentation Only

### Purpose
All human-readable documentation: specs, design books, legal text, and meta docs.

### Allowed contents
- Markdown, plaintext, diagrams (sources, not generated binaries).
- Subdirectories (see below).

### Prohibitions
- No compiled binaries.
- No game data assets (textures, sounds, maps).
- No source code that is compiled into the game.

### Subdirectories

#### 1.1 `/docs/spec`

**Purpose**  
Formal specifications that drive implementation. This is the authority for behaviour.

**Contents**
- `LANGUAGE_POLICY.md`
- `STYLE.md`
- `BUILDING.md`
- `SPEC_CORE.md`
- `DATA_FORMATS.md`
- `DIRECTORY_CONTEXT.md`
- `MILESTONES.md`
- Future versioned specs (`SPEC-v*.md`).

**Requirements**
- Must be stable, referenced by CI and tools.
- Code must not contradict these docs.

**Prohibitions**
- No ad-hoc notes.
- No outdated drafts kept here; archive them under `/docs/archive`.

#### 1.2 `/docs/design`

**Purpose**  
High-level design, volumes, and explanatory documents.

**Contents**
- `DominiumDesignBook-*.md`
- Volumes (if split): `Volume1-Vision.md`, etc.
- Conceptual analysis, design narratives.

**Requirements**
- Must reflect current design decisions.
- Forward-looking plans must be clearly labelled.

#### 1.3 `/docs/legal`

**Purpose**  
Legal and policy text.

**Contents**
- `LICENCE.md`
- `EULA.md`
- `TOS.md`
- Disclaimers, attribution lists.

**Prohibitions**
- No build instructions or technical design here.

#### 1.4 `/docs/archive`

**Purpose**  
Old or superseded documents retained for reference.

**Requirements**
- Files must be clearly marked as obsolete or historical.

#### 1.5 `/docs/context` (optional)

**Purpose**  
Context packs for LLMs, Codex addenda, internal design notes.

**Prohibitions**
- No authoritative specs. Anything authoritative must be promoted to `/docs/spec`.

#### 1.6 `/docs/dev` (optional)

**Purpose**  
Developer-oriented notes and internal design writeups tied to dirs/modules.

**Requirements**
- May describe expectations for per-dir behaviour (`dominium_new_*.txt`).
- Not authoritative over `/docs/spec`; conflicts must be resolved in favour of `/docs/spec`.

---

## 2. `/engine` — Core Engine Code (Deterministic)

### Purpose
All *engine* code independent of specific game campaigns or content. This is where C89/C++98 core lives.

### Prohibitions
- No Dominium-specific content rules (scenario scripts, campaign logic).
- No platform-specific OS calls outside `/engine/platform`.
- No large assets or Lua scripts.
- No direct rendering of game-specific UIs (only generic widgets and draw commands).

### Subdirectories

#### 2.1 `/engine/core`

**Purpose**  
Fundamental, platform-agnostic utilities and primitives.

**Contents**
- `dom_core_types.[ch]` — canonical types (ints, fixed-point, IDs).
- `dom_core_log.[ch]` — logging abstraction (no OS headers).
- `dom_core_rng.[ch]` — deterministic RNG.
- `dom_core_mem.[ch]` — allocators, arenas, pools.
- `dom_core_fp.[ch]` — fixed-point helpers, deterministic math.
- Other basic utilities used everywhere.

**Requirements**
- C89 only.
- No dynamic allocation in tight loops where avoidable.
- No platform headers.
- No floats exposed in public interfaces to sim/net.

#### 2.2 `/engine/sim`

**Purpose**  
Deterministic simulation code.

**Contents**
- `dom_sim_tick.[ch]` — tick loop, canonical UPS model.
- `dom_sim_world.[ch]` — world-step orchestration.
- `dom_sim_workers.[ch]` — worker update rules.
- `dom_sim_network_*.[ch]` — power/data/fluids sim logic.
- `dom_sim_economy.[ch]` — economic tick logic.
- `dom_sim_climate.[ch]` — climate and weather ticks.
- `dom_sim_save.[ch]` / `dom_sim_load.[ch]` — state serialization per `DATA_FORMATS.md`.
- `dom_sim_blueprint.[ch]` — blueprint state machine and construction progression.

**Requirements**
- C89 only.
- Deterministic. No wall clock, no OS randomness, no threads.
- Strict compliance with `SPEC_CORE.md`, `DATA_FORMATS.md`, `BUILDING.md`.
- No direct rendering, no platform I/O.

**Prohibitions**
- No direct input handling.
- No OS headers.
- No floats used for authoritative state.

#### 2.3 `/engine/spatial`

**Purpose**  
Spatial partitioning and world hierarchy (surfaces, regions, chunks, microgrids).

**Contents**
- `dom_spatial_grid.[ch]` — chunk/subchunk/tile mapping.
- `dom_spatial_query.[ch]` — spatial queries (range, overlap).
- `dom_spatial_surface.[ch]` — surface-level partitioning and paging.

**Requirements**
- Deterministic integer/fixed-point coordinates.
- No rendering logic.
- No platform calls.

#### 2.4 `/engine/path`

**Purpose**  
Pathfinding primitives.

**Contents**
- `dom_path_grid.[ch]` — grid/graph abstraction.
- `dom_path_nav.[ch]` — A* and other deterministic path algorithms.
- `dom_path_network.[ch]` — multi-layer networks (road, rail, air, sea).

**Requirements**
- Deterministic results for same inputs.
- No threads, no OS calls.
- Interface used by sim and workers only.

#### 2.5 `/engine/physics`

**Purpose**  
Simple deterministic physics primitives (movement, collisions, constraints where needed).

**Contents**
- `dom_phys_body.[ch]` — kinematic bodies.
- `dom_phys_step.[ch]` — integration per tick.
- `dom_phys_collision.[ch]` — discrete collision checks.

**Requirements**
- Deterministic fixed-step integration.
- No high-fidelity physics; all approximations must be stable and reproducible.

#### 2.6 `/engine/ecs`

**Purpose**  
Entity-component system implementation.

**Contents**
- `dom_ecs_world.[ch]` — ECS world, entity lifecycle.
- `dom_ecs_component.[ch]` — component registration, storage, iteration.
- `dom_ecs_serialise.[ch]` — ECS state to/from `DATA_FORMATS.md`.

**Requirements**
- Stable entity IDs across save/load.
- Deterministic iteration order (sorted or explicitly ordered).
- No floats in serialized component formats.

#### 2.7 `/engine/net`

**Purpose**  
Deterministic network protocol implementation.

**Contents**
- `dom_net_proto.[ch]` — lockstep and client-server protocols.
- `dom_net_serialisation.[ch]` — packet encoding/decoding.
- `dom_net_replay.[ch]` — input/replay stream handling for deterministic tests.

**Requirements**
- All on-the-wire formats follow `DATA_FORMATS.md`.
- All variable-length packets must have explicit version tags.
- Deterministic ordering and delivery semantics.

#### 2.8 `/engine/render`

**Purpose**  
Abstract rendering backends, independent of OS windowing.

**Contents**
- `dom_render_api.[ch]` — abstract renderer interface (takes draw-command streams).
- Backend implementations:
  - `/engine/render/dx9`
  - `/engine/render/gl1`
  - `/engine/render/gl2`
  - `/engine/render/vector2d`
  - `/engine/render/software` (future)
- Backend-specific entrypoints and state, isolated per directory.

**Requirements**
- Public API is backend-agnostic; only draw commands and resource handles.
- No simulation logic.
- No window creation or OS calls (platform layer only).

**Prohibitions**
- No game-specific assumptions (no hard-coded HUD layouts, modes).
- No direct access to ECS or simulation state.

#### 2.9 `/engine/audio`

**Purpose**  
Abstract audio backend.

**Contents**
- `dom_audio_api.[ch]` — renderer-neutral audio interface.
- Implementations (SDL_mixer, OpenAL, etc.) under subdirs.

**Requirements**
- Deterministic sample scheduling from simulation perspective.
- Decoding and playback jitter must not affect sim determinism.

#### 2.10 `/engine/ui`

**Purpose**  
Core UI widgets and layout logic that are game-agnostic.

**Contents**
- `dom_ui_core.[ch]` — basic widgets and layout.
- `dom_ui_skin.[ch]` — styling abstraction.
- `dom_ui_draw.[ch]` — UI to draw-command translation.

**Requirements**
- No direct sim logic. Emits commands/events into game layer.
- No platform calls; uses render and input abstractions only.

#### 2.11 `/engine/platform`

**Purpose**  
OS-specific platform implementations behind a stable interface.

**Subdirs**
- `/engine/platform/win32`
- `/engine/platform/linux`
- `/engine/platform/macos`
- Future: `/engine/platform/dos`, `/engine/platform/win9x`, `/engine/platform/macos_classic`, `/engine/platform/webasm`.

**Contents**
- Filesystem wrappers, time sources.
- Window creation, input.
- Threads (if used for non-sim tasks).
- OS-level timers.

**Requirements**
- Only place allowed to include `<windows.h>`, `<unistd.h>`, etc.
- Present unified `dom_platform_*` APIs to the rest of the engine.

**Prohibitions**
- No simulation logic or game rules.
- No direct use from mods or Lua; only engine internal.

---

## 3. `/game` — Game Glue, Dominium-Specific Logic

### Purpose
Dominium-specific gameplay code that *uses* the engine.

### Subdirectories

#### 3.1 `/game/client`

**Purpose**  
Client application logic (menus, HUD, views) that binds engine to user experience.

**Contents**
- High-level views (top-down, first-person, overlays).
- Input mapping to game commands.
- Dominium-specific UI layouts on top of `engine/ui`.

**Requirements**
- May be in C or C++98.
- Uses only public engine APIs.
- No direct OS calls.

#### 3.2 `/game/server`

**Purpose**  
Dedicated server logic for multiplayer/universes.

**Contents**
- Headless server entrypoint.
- Universe/surface/session management.
- Authority over game rules for multiplayer.

**Requirements**
- Uses engine/sim/net only.
- No rendering backends.
- No dependency on `engine/render` or `engine/ui`.

#### 3.3 `/game/launcher`

**Purpose**  
Launcher executable that selects platform+renderer+mode, detects hardware, launches correct binary.

**Requirements**
- Handles mod/DLC selection.
- Handles demo/restricted modes.
- May be platform-specific, but should use platform and engine APIs where possible.

---

## 4. `/data` — Canonical Game Data Packs

### Purpose
First-party data for the base game and official DLCs.

### Prohibitions
- No third-party mod content.
- No temp data.
- No engine source code.

### Subdirectories

#### 4.1 `/data/base`

**Purpose**  
Built-in base content (Dominium without DLC).

**Contents**
- Entities, machines, buildings (JSON/Lua/packed).
- Base graphics, sounds, music references.
- Tech tree core definitions.
- Lua scripts for base rules and config.

**Requirements**
- Loaded as “base mod” in-game.
- Must always exist.
- Must obey `DATA_FORMATS.md` and not introduce new binary conventions.

#### 4.2 `/data/dlc`

**Purpose**  
Official DLC content (Interstellar, Extras, Wargames).

**Subdirs**
- `/data/dlc/interstellar`
- `/data/dlc/extras`
- `/data/dlc/wargames`
- Future DLC subdirs.

**Requirements**
- Each DLC pack self-describing and versioned.
- No engine code; only data and scripts.
- Can be loaded/unloaded as modules on top of base.

#### 4.3 `/data/packs`

**Purpose**  
First-party graphics, sound, and music packs, loaded like OpenTTD newgrfs/new music.

**Requirements**
- Each pack independent and overrideable.
- No executable code.
- Only references, resources, and metadata.

#### 4.4 `/data/templates`

**Purpose**  
Sample universes, example saves, marketing/demo saves.

**Requirements**
- Must be generated via normal gameplay or tooling, not hand-edited binary.

---

## 5. `/mods` — Third-Party and Local Mods

### Purpose
User/modder extensions. Not official content.

### Subdirectories

- `/mods/local` — Locally-installed mods.
- `/mods/workshop` — Mods downloaded from Steam Workshop or other portals.
- `/mods/disabled` — Mods installed but not active.

**Requirements**
- Each mod lives in its own directory with a manifest (`manifest.json`).
- Only `*.dmod` or other approved formats from `DATA_FORMATS.md`.
- No engine binaries allowed here.

**Prohibitions**
- No writing engine source code here.
- No arbitrary scripts auto-loaded from outside `/mods`.
- No direct OS-specific binaries shipped as part of mods.

---

## 6. `/tools` — Editors, Devkits, Pipelines

### Purpose
All non-runtime tools.

### Subdirectories

#### 6.1 `/tools/editor`

**Purpose**  
World editor, map editor, blueprint editor, asset layout editors.

#### 6.2 `/tools/devkit`

**Purpose**  
Modding SDK, schema generators, script stubs, codegen for Lua bindings.

**Requirements**
- Clearly versioned against modding API and engine version.

#### 6.3 `/tools/pipeline`

**Purpose**  
Asset import/export and conversion (images, soundbanks, mesh builders).

**Prohibitions**
- No game runtime logic.
- No modifications to `/engine` except via build scripts in `/build`.

#### 6.4 `/tools/replay` (optional)

**Purpose**  
Replay analyzers, determinism checkers, diff tools.

---

## 7. `/tests` — Tests Only

### Purpose
Unit tests, integration tests, replays, performance tests.

### Subdirectories

#### 7.1 `/tests/unit`

**Purpose**  
Per-module unit tests.

**Requirements**
- C89 if testing C89 modules.
- No OS interaction beyond engine/platform abstractions.

#### 7.2 `/tests/integration`

**Purpose**  
Whole-system tests: run the engine in headless mode and validate state.

#### 7.3 `/tests/replay`

**Purpose**  
Deterministic replay tests. Long-running scenarios using `.dreplay` or `.drepd`.

#### 7.4 `/tests/perf`

**Purpose**  
Performance and load-shedding tests.

**Prohibitions**
- No golden data that depends on wallclock or OS-specific behaviour.

---

## 8. `/third_party` — External Code and Assets

### Purpose
Vendored dependencies and third-party libraries.

### Subdirectories

- `/third_party/src` — external source code.
- `/third_party/include` — external headers.
- `/third_party/licenses` — their licences.

**Requirements**
- Clearly separated; no modification without note.
- No mixing Dominium source with third-party in same directory.

---

## 9. `/build` — Build Artifacts and Aux Files

### Purpose
Build scripts, CMake configs, and local build outputs (if not ignored).

### Subdirectories

- `/build/cmake` — shared CMake modules.
- `/build/scripts` — build helper scripts (Python, shell, batch).
- `/build/output` — local build outputs (ignored by VCS).

**Requirements**
- Only build-related content; no authoritative specs or game data.

---

## 10. `/packaging` — Distribution and Media Layouts

### Purpose
Everything needed to make **installers** and **physical media images**.

### Subdirectories

#### 10.1 `/packaging/windows`

**Purpose**  
NSIS/Inno/other installer definitions.

#### 10.2 `/packaging/linux`

**Purpose**  
DEB/RPM/Flatpak/AppImage packaging scripts.

#### 10.3 `/packaging/macos`

**Purpose**  
DMG layouts, app bundles, notarisation scripts.

#### 10.4 `/packaging/retro`

**Purpose**  
Floppy/CD/DVD/ZIP layouts for DOS, Win3.x, Win9x, etc.

**Requirements**
- 8.3 SFN constraints respected for retro images.
- Filenames for retro mapped from canonical modern paths via a mapping table.

**Prohibitions**
- No engine source.
- No game logic changes.

---

## 11. `/scripts` — Meta Automation (Non-Build)

### Purpose
Meta-level helper scripts for repo maintenance, analysis, or CI that are not strictly part of the build.

**Examples**
- Log analyzers.
- Code generators.
- Repo maintenance tools (e.g. license scanners).
- Determinism regression drivers that call binaries.

**Prohibitions**
- No runtime engine dependencies embedded into production binaries.
- No game logic here; only orchestration.

---

## 12. `/ports` — Alternative Targets (Future-Facing)

### Purpose
Experimental or dedicated target-specific glue code that does not belong under the main platform dirs yet.

### Subdirectories (planned)

- `/ports/dos`
- `/ports/win9x`
- `/ports/win3x`
- `/ports/macos_classic`
- `/ports/wasm`
- `/ports/console_*`

**Requirements**
- Each port documents its constraints (file systems, SFN, memory, input/output limits).
- Ports should reuse `/engine/platform` abstractions wherever possible.

**Prohibitions**
- No design-by-copy duplication of engine code.
- Port-specific hacks must be wrapped or isolated.

---

## 13. GENERAL RULES ACROSS ALL DIRECTORIES

1. No directory may contain both **engine C/C++ code** and **user mod content**.  
2. No directory may redefine a module that already exists elsewhere; one authority per module.  
3. All determinism-sensitive code must live in `/engine/core`, `/engine/sim`, `/engine/spatial`, `/engine/path`, `/engine/physics`, or `/engine/ecs`.  
4. All platform-specific code must live under `/engine/platform` or `/ports`.  
5. All game-specific content lives under `/game` and `/data`, not `/engine`.  
6. All third-party materials must live under `/third_party` with licences.  
7. No binary format or network protocol may be invented outside the rules in `DATA_FORMATS.md`.  
8. No floating point state may be serialized to disk or used for authoritative simulation.  
9. Any new top-level directory must be added to this file before use.

This directory contract is binding. Any future directory additions or changes must be slotted into this structure and documented here before being used.
