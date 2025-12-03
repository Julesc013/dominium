# Dominium — DIRECTORY CONTEXT AND CONTRACT

This document defines the **purpose, allowed contents, requirements, and prohibitions** for every major directory in the Dominium repository — current and planned.

This file is a contract for humans and code-generators. If code or data violates these rules, it is wrong.

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
- `SPEC-core.md`
- `DATA_FORMATS.md`
- `MILESTONES.md`
- Future versioned specs (`SPEC-v3.0.*.md`).

**Requirements**
- Must be stable, referenced by CI and tools.
- Changes require review; code must not contradict these docs.

**Prohibitions**
- No ad-hoc notes.
- No outdated drafts kept here; archive them under `/docs/archive`.

#### 1.2 `/docs/design`

**Purpose**  
High-level design, volumes, and explanatory documents.

**Contents**
- `DominiumDesignBook-v3.0.md`
- Volumes (if split): `Volume1-Vision.md`, etc.
- Any extra conceptual analysis.

**Requirements**
- Must reflect current design decisions.
- Forward-looking plans must be clearly labelled as such.

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

---

## 2. `/engine` — Core Engine Code (Deterministic)

### Purpose
All *engine* code that is independent of a specific game campaign or content. This is where C89/C++98 core lives.

### Prohibitions
- No game-specific content logic (e.g. “Dominium: Wargames” specific scenario scripts).
- No platform-specific OS calls; those live in platform layers only.
- No large assets.

### Subdirectories

#### 2.1 `/engine/core`

**Purpose**  
Fundamental, platform-agnostic utilities and primitives.

**Contents**
- `dom_core_types.[ch]`
- `dom_core_log.[ch]`
- `dom_core_rng.[ch]`
- `dom_core_mem.[ch]`
- `dom_core_fp.[ch]`
- Any other basic utilities used everywhere.

**Requirements**
- C89 only.
- No dynamic allocation in tight loops where avoidable.
- No platform headers.

#### 2.2 `/engine/sim`

**Purpose**  
Deterministic simulation code.

**Contents**
- `dom_sim_tick.[ch]`
- `dom_sim_world.[ch]`
- `dom_sim_workers.[ch]`
- `dom_sim_network_*.[ch]` (power, data, fluids)
- `dom_sim_economy.[ch]`
- `dom_sim_climate.[ch]`

**Requirements**
- C89 only.
- Deterministic. No wall clock, no OS randomness.
- Strict compliance with `SPEC-core.md` and Design Book volumes.

**Prohibitions**
- No rendering calls.
- No direct input handling.
- No platform I/O.

#### 2.3 `/engine/render`

**Purpose**  
Abstract rendering backends, independent of specific OS windowing.

**Contents**
- `dom_render_api.[ch]` (abstract interfaces)
- Backend implementations:
  - `/engine/render/dx9`
  - `/engine/render/gl1`
  - `/engine/render/gl2`
  - `/engine/render/vector2d`
  - `/engine/render/software` (future)

Each backend dir contains only the code for that backend.

**Requirements**
- The public API must be stable and backend-agnostic.
- No game-specific assumptions (no hard-coded UI layouts).

**Prohibitions**
- No simulation logic.
- No OS window creation here; that is platform layer.

#### 2.4 `/engine/audio`

**Purpose**  
Abstract audio backend.

**Contents**
- `dom_audio_api.[ch]`
- Implementations (SDL_mixer, OpenAL, etc.) under subdirs.

**Requirements**
- Deterministic sample scheduling from sim’s POV, even if actual playback jitter exists.
- No decoding logic in simulation thread.

#### 2.5 `/engine/platform`

**Purpose**  
OS-specific platform implementations behind a stable interface.

**Subdirs**
- `/engine/platform/win32`
- `/engine/platform/linux`
- `/engine/platform/macos`
- Future: `/engine/platform/dos`, `/engine/platform/win9x`, `/engine/platform/macos_classic`, `/engine/platform/webasm`.

**Contents**
- Filesystem wrappers, time sources, window creation, input, threads (if used).

**Requirements**
- The only place allowed to include `<windows.h>`, `<unistd.h>`, etc.
- Must present unified `dom_platform_*` APIs to the rest of the engine.

**Prohibitions**
- No simulation logic or game rules here.
- No direct use from mods or Lua; only engine internal.

#### 2.6 `/engine/net`

**Purpose**  
Deterministic network protocol implementation.

**Contents**
- `dom_net_proto.[ch]` (lockstep / client-server protocols)
- `dom_net_serialisation.[ch]`

**Requirements**
- Simulation-visible network must be deterministic and versioned.
- All variable-length packets must have explicit version tags.

#### 2.7 `/engine/ui`

**Purpose**  
Core UI widgets and layout logic that are game-agnostic.

**Requirements**
- No direct sim logic. Only drives commands/events.

---

## 3. `/game` — Game Glue, Dominium-Specific Logic

### Purpose
Dominium-specific gameplay code that *uses* the engine.

### Subdirectories

#### 3.1 `/game/client`

**Purpose**  
Client application logic (menus, HUD, views) that binds engine to user experience.

**Requirements**
- May be in C or C++98.
- May use higher-level helpers.

#### 3.2 `/game/server`

**Purpose**  
Dedicated server logic for multiplayer/universes.

**Requirements**
- Headless, uses engine/sim/net only.
- No rendering.

#### 3.3 `/game/launcher`

**Purpose**  
Launcher executable that selects platform+renderer+mode, detects hardware, launches correct binary.

**Requirements**
- Handles mod/DLC selection.
- Handles demo/restricted modes.

---

## 4. `/data` — Canonical Game Data Packs

### Purpose
First-party data for the base game and official DLCs.

### Prohibitions
- No third-party mod content.
- No temp data.

### Subdirectories

#### 4.1 `/data/base`

**Purpose**  
Built-in base content (Dominium without DLC).

**Contents**
- Entities, machines, buildings
- Base graphics and sounds
- Tech tree core

**Requirements**
- Loaded as “base mod” in-game.
- Must always exist.

#### 4.2 `/data/dlc`

**Purpose**  
Official DLC content (Interstellar, Extras, Wargames).

**Subdirs**
- `/data/dlc/interstellar`
- `/data/dlc/extras`
- `/data/dlc/wargames`
- Future DLC subdirs.

**Requirements**
- Each DLC pack must be self-describing and versioned.
- No engine code; only data and scripts.

#### 4.3 `/data/packs`

**Purpose**  
First-party graphics, sound, and music packs, loaded like OpenTTD newgrfs/new music.

**Requirements**
- Each pack must be independent and overrideable.
- Must not embed executable code.

#### 4.4 `/data/templates`

**Purpose**  
Sample universes, example saves, marketing/demo saves.

---

## 5. `/mods` — Third-Party and Local Mods

### Purpose
User/modder extensions. Not official content.

### Subdirectories

- `/mods/local` — Locally-installed mods.
- `/mods/workshop` — Mods downloaded from Steam Workshop or other portals.
- `/mods/disabled` — Mods installed but not active.

**Requirements**
- Each mod lives in its own directory with a manifest.
- No engine binaries allowed here.

**Prohibitions**
- No writing engine source code here.
- No unreviewed scripts auto-loaded from outside `/mods`.

---

## 6. `/tools` — Editors, Devkits, Pipelines

### Purpose
All non-runtime tools.

### Subdirectories

#### 6.1 `/tools/editor`

**Purpose**  
World editor, map editor, blueprint editor.

#### 6.2 `/tools/devkit`

**Purpose**  
Modding SDK, schema generators, script stubs.

**Requirements**
- Clearly versioned to modding API.

#### 6.3 `/tools/pipeline`

**Purpose**  
Asset import/export and conversion (images, soundbanks, mesh builders).

**Prohibitions**
- No game runtime logic.
- No modifications to `/engine` except via build scripts.

---

## 7. `/tests` — Tests Only

### Purpose
Unit tests, integration tests, replays, perf tests.

### Subdirectories

#### 7.1 `/tests/unit`

**Purpose**  
Per-module unit tests.

**Requirements**
- C89 if testing C89 modules.
- No OS interaction beyond what the engine exposes.

#### 7.2 `/tests/integration`

**Purpose**  
Whole-system tests: run the engine in headless mode and validate state.

#### 7.3 `/tests/replay`

**Purpose**  
Deterministic replay tests. Long-running scenarios.

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
- No mixingDominium source with third-party in same directory.

---

## 9. `/build` — Build Artifacts and Aux Files

### Purpose
Build scripts, CMake configs, and local build outputs (if not ignored).

### Subdirectories

- `/build/cmake` — shared CMake modules.
- `/build/scripts` — build helper scripts (Python, shell, batch).
- `/build/output` — local build outputs (ignored by VCS).

**Requirements**
- Only build-related, no source of truth stored here.

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
- 8.3 SFN constraints must be respected for retro images.
- Filenames for retro must be mapped from canonical modern paths via a mapping table.

**Prohibitions**
- No engine source here.
- No game logic changes here.

---

## 11. `/scripts` — Meta Automation (Non-Build)

### Purpose
Meta-level helper scripts for repo maintenance, analysis, or CI that are not strictly part of the build.

**Examples**
- Log analyzers
- Code generators
- Repo maintenance tools (e.g. license scanners)

**Prohibitions**
- No runtime engine dependencies from production binaries.

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
- Each port must document its constraints (file systems, SFN, memory).
- Ports should try to reuse `/engine/platform` abstractions wherever possible.

**Prohibitions**
- No design-by-copy duplication of engine code. Port-specific hacks must be wrapped or isolated.

---

## 13. GENERAL RULES ACROSS ALL DIRECTORIES

1. No directory may contain both **engine C code** and **user mod content**.  
2. No directory may redefine a module that already exists elsewhere; one authority per module.  
3. All determinism-sensitive code must live in `/engine/core` or `/engine/sim`.  
4. All platform-specific code must live under `/engine/platform` or `/ports`.  
5. All game-specific content lives under `/game` and `/data`, not `/engine`.  
6. All third-party materials must live under `/third_party` with licences.

This directory contract is binding. Any future directory additions must be slotted into this structure or documented here before being used.
