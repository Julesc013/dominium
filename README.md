<<<<<<< HEAD
# DOMINIUM & DOMINO

## A Deterministic, Multi-Scale, Multi-Platform Simulation Game and Engine

Dominium on Domino is a fully deterministic, integer-math, platform-agnostic, modular engine and game designed to run **bit-identically** across:
=======
# DOMINIUM & DOMINO  
## A Deterministic, Multi-Scale, Multi-Platform Simulation Game and Engine

Dominium on Domino is a **fully deterministic**, **integer-math**, **platform-agnostic**, **modular** engine and game designed to run identically across:
>>>>>>> d4e03c4a9334974ad4a2a0cb4887638243533427

- Modern systems (Windows NT family, Linux, macOS X)
- Legacy systems (Win9x, Win3.x, Win16, DOS, macOS 7-9, OS/2 strata via shims)
- Future systems (WASM/Web, consoles, embedded)
- Headless/server nodes (single or clustered)

<<<<<<< HEAD
**Domino** is the deterministic simulation engine core.  
**Dominium** is the official game and tooling layer running on top of Domino.

The official game is *one* compatible implementation atop Domino. Determinism permeates:

- Physics and environmental simulation
- AI and job systems
- Networks (power, fluids, logic)
- World updates and chunk streaming
- Mod execution and scripting
- Replay and desync detection

This repository includes:

- **Domino Engine** - deterministic C89 simulation core and IO
- **Dominium Game Runtime(s)** - content-agnostic gameplay logic on top of Domino
- **Content Packs** - first-party data packs (materials, recipes, worldgen, assets)
- **Tools & Editors** - world tools, asset pipelines, debug/inspection tools
- **Ports** - DOS, Win3.x, Win9x, macOS Classic, WASM, etc.
- **Specifications** - binding behaviour contracts (determinism, formats, APIs)
- **Modding API & SDK** - deterministic, forward-compatible, sandboxed extension layer
=======
Dominium is a game running on the Domino engine.  
The official game is one compatible implementation atop it.  
Determinism permeates physics, AI, networks, world updates, rendering order, mod execution, and replay.

This repository includes:

- **Domino Engine** — deterministic C89/C++98 core  
- **Dominium Game** — content-agnostic gameplay layer  
- **Data Packs** — first-party assets and base definitions  
- **Tools & Editors** — world tools, asset pipelines, modding interfaces  
- **Ports** — DOS, Win3.x, Win9x, macOS Classic, WASM, etc.  
- **Specifications** — binding behaviour contracts  
- **Modding API** — deterministic, forward-compatible, sandboxed  
>>>>>>> d4e03c4a9334974ad4a2a0cb4887638243533427

All behaviour derives from written specifications. No code exists without a contract.

---

## 1. Project Vision

Dominium aims to:

1. **Produce universally reproducible simulation**  
   Any two machines, of any era or ISA, must yield identical state per tick, given the same executable, content set, inputs, and timeline.
2. **Handle extreme spatial scales with a single coherent hierarchy**  
   From sub-meter structural detail to full planetary surfaces:  
   - Fixed technical scale (see Section 2.3) from 1/65,536 m ("Plank") up to 16,777,216 m ("Surface").  
   - Planet surfaces are 2^24 m toroidal squares with +/-2048 m vertical range.
3. **Execute on decades of hardware (286-class upward)**  
   The full Domino engine targets 286-class-and-newer systems. Limited tooling and experimental frontends may exist for earlier 8-bit platforms (for example, CP/M-80), but they do not host the complete world simulation.  
   - Core simulation stays within strict C89, fixed-point integer math.  
   - Older targets may reduce *fidelity* of rendering and UX, but never alter simulation results.
4. **Be maximally modifiable without weakening determinism**  
   - Content packs and mods extend registries and scripts.  
   - Mods cannot change core rules, floating-point behaviour, or ordering guarantees.
5. **Support interchangeable 2D/3D vector and raster renderers at runtime**  
   - Rendering is treated as a pure projection of deterministic world state.  
   - Multiple backends: modern (GL/VK/DX/Metal), retro (VGA/EGA/MDA), vector, software.
6. **Model surface + orbital domains with discrete, graph-based mechanics**  
   - Planetary surfaces use continuous fields + discrete constructions.  
   - Orbital/space simulation uses rails-based orbital graphs, transfer arcs, docking graphs.
7. **Provide a unified construction system**  
   - Block components, slabs, vectors (rails/roads/pipes/tunnels), cut/fill, multi-layer buildings.  
   - All grounded in the same world coordinate and segmentation scheme.
8. **Maintain strict separation between physical surfaces and logical orbital/space graphs**  
   - Surfaces are continuous 3D fields (phi, materials, media).  
   - Orbits are discrete graph nodes/edges with integer dynamics.
9. **Allow deterministic clustered multiplayer**  
   - Lockstep or rollback-based synchronization at tick level.  
   - Servers and clients operate under the same simulation contract.
10. **Provide engineering clarity for multi-decade viability**  
    - Formats and APIs are versioned and documented.  
    - Migration paths are explicit; no silent breakage.

Dominium is engineered to outlive its original hardware.

---

## 2. Core Philosophy

### 2.1 Determinism

Hard constraints for the **engine core** (`/engine`):

- **No floating point is allowed in any code that mutates canonical simulation state or engine-controlled serialized formats.**
  - No `float` or `double` in `/engine` or in any engine-controlled on-disk formats.
  - All continuous quantities are fixed-point integers:  
    - Runtime: **Q16.16** (`fix32`) for general simulation.  
    - Save-local positional: **Q4.12** (`fix16`) for coordinates inside 16 m chunks.  
    - Accumulators and reductions use 64-bit ints where needed.
- Tools, renderers, and non-authoritative analysis may use floating point freely, as long as float-derived values never flow back into engine state or engine-controlled file formats.
- **World addressing:**  
  - Surfaces: 2^24 m x 2^24 m toroidal square.  
  - Vertical range: single Page of 4096 m (Z in [-2048, +2048)).  
  - Horizontal space segmented into 256x256 segments (2^8 per axis), each 2^16 m wide.  
  - Runtime positions: `SimPos = {segment_x, segment_y, Q16.16 local x, Q16.16 local y, Q16.16 z}`.
- **Deterministic ordering across phases:**  
  - Input, pre-state, ECS systems, networks, fluids, merge, postprocess, finalize.  
  - Entity processing order is stable (ascending EntityId).  
  - Network nodes/edges processed in stable ID order.
- **RNG discipline:**  
  - Procedural content uses stateless coordinate hashing (function of seeds + coordinates).  
  - Time-evolving solvers (weather, hydrology, AI) use named RNG streams (`RNGId` to `RNGState`).  
  - RNG states are fully serialized in metadata and are independent of chunk load order.  
  - RNG streams are only advanced during deterministic tick phases; debug, UI, and rendering layers must not advance engine RNG streams.
- **Replay and hashing:**  
  - Replay streams record input events and timing.  
  - Engine can recompute state hashes per tick for validation.  
  - Cross-platform builds must agree on hashes for the same content/universe.

The **runtime/renderer/launcher** layers may use floats internally, but they never feed float-derived values back into engine state or save files.

### 2.2 Tick Phasing and Ordering

The global simulation tick has **immutable phases** in the engine:

1. **Input**  
   - External commands sampled/applied as canonical events.  
   - Network inbound events reconciled to tick boundary.
2. **Pre-State**  
   - Resolve queued structural changes (spawns/despawns, worldgen openings).  
   - Apply configuration changes scheduled from previous ticks.
3. **Simulation Lanes (ECS systems)**  
   - Movement and kinematics  
   - AI and job systems  
   - Machines and production graphs  
   - Local scripts (deterministic subset)  
   - All run in defined, static order over entity IDs.
4. **Networks**  
   - Electrical networks solved (voltage/current).  
   - Hydraulic networks solved (pressure/flow).  
   - Logic/signal networks updated (combinational and sequential).  
   - Network order is fixed and independent of spatial streaming.
5. **Fluids & Fields / Merge**  
   - FluidSpaces (rooms, tanks, pipes) compartments updated.  
   - Atmo/hydro macroscopic grids stepped.  
   - ThermalSpaces updated.  
   - Merges consistent with network outputs and ECS.
6. **Post-Process**  
   - Rebuild spatial acceleration structures.  
   - Mark chunks dirty for meshing.  
   - Schedule IO and mesh jobs (purely cache effects).
7. **Finalize**  
   - Prepare state for next tick (RNG states stored, logs emitted).  
   - Replay/event logs flushed.

No system may reorder or bypass phases. Parallelism is allowed only within phases, and only for tasks that do not mutate shared state (for example, meshing, IO) or that commit in a fixed, serialized order.

Any operation that schedules work for a future tick (timers, delayed spawns, transport completions) must do so via the Pre-State phase's queueing mechanism; no system may directly mutate future-tick state.

Parallel execution within a phase may only operate on disjoint subsets of state and must commit results in a globally deterministic order (for example, by sort-by-ID before commit).

### 2.3 Spatial Hierarchy (Technical Scale)

The engine uses a **single, unified, metric scale hierarchy** for space and time references, tuned for the simulation needs. All units are metres and conceptually cubic (3D), even if stored sparsely.

- **2^-16 m - Plank**  
  Minimal unit for internal precision (not directly exposed to gameplay). Useful for fine SDF and field resolution.
- **2^-12 m - Point**  
  Sub-millimetre resolution for exact geometry and collision math where needed.
- **2^-8 m - Step**  
  1/256 m; base save precision for static positions (`Q?.8`/`Q4.12`), about 3.9 mm granularity.
- **2^-4 m - Sixteenth**  
  1/16 m; used for fine local grids, ramps, detailed building layout.
- **2^0 m - Block**  
  1 m; primary gameplay block/tile unit (for building placement, grids).
- **2^4 m - Chunk**  
  16 m; core cubic chunk unit for streaming and meshing.  
  - Chunks are 16x16x16 m.  
  - Terrain caches: 32^3 samples (0.5 m spacing). Terrain caches are derived, non-canonical acceleration structures; they are never the primary definition of terrain on disk.
- **2^8 m - Region**  
  256 m; groups 16x16 chunks in X/Y. Basic hydrology and environment cell size.
- **2^12 m - Page**  
  4096 m; vertical domain per surface. For Dominium, Z in [-Page/2, +Page/2).  
  Each Surface owns exactly one vertical Page in Dominium 1.x. Additional shells, deep volumes, or orbital shells are represented as separate Surfaces or logical spaces, not by extending Z beyond this range.
- **2^16 m - Segment**  
  65,536 m; horizontal segments. Each of the 256x256 segments maps directly to Q16.16 integer part.
- **2^20 m - Sector**  
  1,048,576 m; used to define atmo/hydro grids and logical LOD partitions.
- **2^24 m - Surface**  
  16,777,216 m; full horizontal extent of a surface, toroidally wrapped.

Surfaces are **sparse collections** of chunks and fields:

- No monolithic global 3D array exists.
- Geometry is defined by procedural functions plus local overrides and volumes.
- Underground structures and multi-level constructs are represented via SDF/fields and object/volume graphs, not by fixed layered tiles.

### 2.4 Universal Modularity

All subsystems are **hot-swappable** at the configuration/content level, behind stable contracts:

- **Rendering backends** (see Section 9 for the full matrix)  
  - Software rasterizers  
  - Vector renderers  
  - OpenGL 1.x/2.x, DirectX 9/11/12, Vulkan 1.x  
  - VGA/EGA/CGA/MDA/Hercules, VESA modes  
  - QuickDraw, Carbon/Quartz, Metal, WinG (where appropriate)  
  - Headless (no rendering)
- **Audio backends**  
  - Configurable abstraction per platform.
- **Platform backends** (see Section 9 for the full platform/render matrix)
- **Tools and data packs**  
  - Share common IO and registry libraries from `/engine`.
- **Scripting**  
  - Deterministic subset of Lua or a custom "Dominium Script".  
  - No direct access to system clock, threads, real RNG, or floating point.

Backends adapt to core contracts, never the reverse.

### 2.5 Platform Breadth

Engine core compiles under:

- **Strict C89** (no compiler extensions, no non-portable assumptions).
- **No libc extensions** in the core (only a well-defined subset of `stdlib`/`string` etc.).

Higher layers:

- Runtime, launcher, tools: **C++98** only, with a constrained subset of STL where allowed.
- Platform-specific behaviour is contained in:  
  - `/runtime/` (frontends)  
  - `/launcher/`  
  - `/tools/`  
  - Platform shims in `/ports/`

All platforms must adhere to the same engine ABI and file formats.

---

## 3. Repository Overview

This section is a high-level overview only. The authoritative and machine-checkable directory layout and semantics are defined in `/docs/spec/DIRECTORY_CONTRACT.md`. In any conflict, the spec file is the source of truth.

Top-level structure (conceptual):

- `/docs` - specifications, formats, policies, style, building
- `/engine` - deterministic engine core (C89, fixed-point, no floats)
- `/runtime` - high-level game runtimes (C++98 frontends; e.g., CLI, SDL, editor)
- `/content` - official content packs (materials, recipes, worldgen, assets)
- `/mods` - third-party deterministic mods and content packs
- `/tools` - editors, converters, inspection tools, pipelines
- `/tests` - unit tests, replay determinism tests, integration and performance tests
- `/external` - vendored dependencies (Lua subset, platform libs, zlib, etc.)
- `/build` - build trees, generated headers, CI artefacts
- `/package` - installer scripts, retro media images and packaging
- `/scripts` - automation, CI helpers, migration tools
- `/ports` - per-platform configuration and shims (DOS, Win3.x, Win9x, macOS Classic, WASM, consoles)

Within `/docs/spec/` the authoritative directory contract lives in:

- `/docs/spec/DIRECTORY_CONTRACT.md`

This README is descriptive; the spec files are normative.

---

## 4. Building

### 4.1 Modern Platforms

Primary workflow: **CMake** targeting modern compilers.

```bash
mkdir build
cd build
cmake ..
cmake --build .
```

Core expectations:

- `/engine` builds as a C89 static library (for example, `libdom_engine.a`).
- `/runtime/dom_cli` and `/runtime/dom_sdl` (or equivalent) link against `libdom_engine`.
- `/tools` link against engine IO libraries for format access.

On every successful build:

- Global build number incremented in `.dominium_build_number`.
- Generated header written at `build/generated/dom_build_version.h` with:  
  - Major/minor/patch  
  - Build number  
  - Git commit hash (if available)  
  - Timestamp (for diagnostics; not used in simulation)

Build numbers and timestamps are diagnostic only and never appear in engine-controlled formats or influence simulation behaviour. Different builds of the same commit must still produce bit-identical simulation results for the same inputs and content.

### 4.2 Retro Platforms

Retro build flows live under `/ports/<target>/`:

Each target includes:

- Toolchain config
- Build scripts
- Notes about supported feature subsets

Examples:

- DOS: OpenWatcom plus wmake or similar; 16-bit/32-bit builds as appropriate.
- Win3.x: MASM plus MSVC 1.52; targeting Win16 APIs and limited memory.
- Win9x: MSVC6 plus DX7 SDK or SDL1 backend.
- macOS Classic (7-9): CodeWarrior plus MPW projects.
- WASM/Web: Emscripten; runtime frontends in C++98 compiled to WASM; engine compiled as C library.

Retro builds:

- Must use the same engine core sources, file formats, and content.
- May alter:  
  - Renderer choice  
  - UI complexity  
  - Build flags (size vs speed), but not simulation logic.
- Simulation behaviour remains bit-identical across all targets.

---

## 5. Running

### 5.1 Headless Server

Typical headless binary (example naming):

```bash
./dom_cli --universe path/to/universe --surface 0 --ticks 0 --listen 0.0.0.0:PORT
```

- `--universe`: path to universe directory (root of saves).
- `--surface`: surface id/index to simulate.
- `--ticks`: number of ticks to run (0 = run indefinitely).

Network layer manages deterministic lockstep/rollback.

### 5.2 Client

Typical client binary (example):

```bash
./dom_sdl --universe path/to/universe --surface 0
```

- Client connects to a server (local or remote) or runs in local-only mode.
- Rendering backend selected via config/CLI.
- All game state is driven by engine state; no client-side simulation divergence is allowed.

The launcher is optional:

- The game must run with direct invocation of runtime binaries.
- Launcher provides orchestration, configuration UI, and multi-instance management but has no simulation semantics.
- Clients and servers operate in deterministic lockstep; divergences (desync) are detected via state hashes and can be replayed/debugged.

---

## 6. Modding

A mod is a content plus optional code bundle with strict contracts.

Typical mod layout:

- `mod.json`  
  - Mod id (UUID/namespace), version, author  
  - Dependencies (other mods/content packs)  
  - Required engine/runtime version
- `content/`  
  - Prefabs, materials, recipes, worldgen configs  
  - Deterministic data tables (JSON/binary formats)
- `scripts/`  
  - Deterministic Lua subset or Dominium Script  
  - No direct I/O, time, threads, or random; all via engine-provided APIs
- `assets/`  
  - Textures, sprites, meshes, audio, etc. (where applicable)

Loading order:

- Base content packs
- Official DLC packs
- Mods, ordered by stable UUID and dependency resolution

Mods may:

- Register new materials, recipes, volume types.
- Register new worldgen recipes and solvers (via deterministic APIs).
- Extend gameplay systems as long as they obey engine deterministic interfaces.

Mods may not:

- Patch binaries or change the engine's fixed-point formats.
- Introduce nondeterministic behaviour (no real RNG, no system time).
- Violate directory contracts or bypass engine IO.
- Binary plugins (when allowed) must use the documented C plugin ABI and are versioned separately. Binary plugins are bound by the same determinism constraints as the core: no direct use of system time, system RNG, threads that mutate engine state outside tick phases, or floating point in any path that affects simulation state.

---

## 7. Data Formats

All engine-controlled formats obey:

- Integer math only
- Fixed-point positions (Q16.16 and Q4.12)
- All physical quantities stored as scaled integers
- Explicit layout  
  - Packed C structs with explicit field sizes  
  - Alignment/padding rules documented; no implicit compiler padding relied upon  
  - No reliance on platform-specific struct packing pragmas is allowed in the canonical format definitions; disk layouts are specified in terms of explicit field sizes, and implementations must conform to those layouts.
- Little-endian canonical representation  
  - All multi-byte fields are little-endian on disk  
  - Platforms must convert as needed
- Explicit versioning  
  - File headers contain magic plus version  
  - Chunk sections are TLV (type-length-version) so new sections can be added without breaking older readers  
  - Existing on-disk versions are immutable contracts. Any behavioural or layout change requires a new on-disk version and a documented migration path; silently changing the meaning of an existing version is forbidden.
- No pointers in serialized data  
  - All references are via IDs or relative indices  
  - No raw memory addresses appear in files
- Integrity and replay metadata  
  - Optional CRCs on sections or entire files  
  - Replay hashes and tick markers embedded in metadata for validation

### 7.1 Save File Structure (Universe / Surface / Region / Chunk)

A save "universe" directory contains:

- `universe.meta` -> UniverseMeta (version, universe_seed, etc.)
- `content.lock` -> lists exact content packs and mod versions (id/version/hash); used to reconstruct registries deterministically. On loading a universe, the engine verifies that the active content set exactly matches `content.lock`; mismatches are treated as fatal until reconciled.

Per-surface directories:

- `surface_<id>.meta` -> SurfaceMeta (seed, recipe id, RNG states, etc.)
- `regions/` -> region files with chunk blobs

Region file structure:

- RegionHeader  
  - Magic `REGN`  
  - Version  
  - Chunk count  
  - Array of `ChunkEntry { ChunkKey3D, offset, length }`
- Followed by `chunk_count` chunk blobs.

Each chunk blob:

- Sequence of `ChunkSectionHeader` plus payload blocks:  
  - `CHUNK_SEC_TERRAIN_OVERRIDES` (1)  
  - `CHUNK_SEC_OBJECTS` (2)  
  - `CHUNK_SEC_EDIT_OPS` (3)  
  - `CHUNK_SEC_LOCAL_VOLUMES` (4)  
  - `CHUNK_SEC_LOCAL_ENV_STATE` (5)  
  - `CHUNK_SEC_LOCAL_NET_STATE` (6)  
  - `>=1000` reserved for mod and future sections

Chunk/subchunk "microgrids" exist only as caches for meshing and local physics; the canonical world geometry is the combination of:

- Procedural phi from recipes
- Edit operations
- Volume instances
- Fluid/thermal and network state

Saves contain:

- Entity/component state
- Network state (pressures, voltages, flows)
- FluidSpaces/ThermalSpaces state (if applicable)
- Prefab references and overrides
- Messages/events queued across ticks
- Chunk overrides and EditOps
- Optional replay delta logs for time travel/debugging

---

## 8. Surface + Space Architecture

Two primary domains exist, sharing the same core engine but different solvers and representations.

### 8.1 Physical Domains (Surfaces)

- Planet surfaces (2^24 m toroidal squares)
- Underground volumes (caves, strata, basins)
- Oceans, lakes, rivers, canals
- Sparse terrain fields (signed distance fields, material fields)
- Structural microgrids (buildings, slabs, supports)
- Vector networks: rails (trains, trams), roads, conveyors, pipes/tunnels
- Cut/fill terrain layers and excavation volumes

Physical space is:

- Defined by fields (phi, materials, media) at arbitrary points.
- Sampled via deterministic functions and local overrides.
- Connected to discrete constructions (objects, volumes, networks).

### 8.2 Logical Domains (Orbital/Space)

- Discrete orbital tracks and arcs
- Transfer windows/manoeuvre graphs
- Docking graphs (stations, platforms, vehicles)
- Asteroid belts as discrete resource graphs
- Stations, ships, satellites
- Lagrange nodes and special points

Deterministic transfers:

- Orbital mechanics treated as a rails-based graph simulation (integer time steps, precomputed or integer-integrated ephemerides).
- Space simulation uses integer time, integer/fixed ephemeris and positions, no uncontrolled floating-point dynamics.
- Transitions between surface and space domains are well-defined ports and graph edges (elevators, launch pads, space elevators, etc.), always deterministic and reversible.

---

## 9. Platform + Renderer Matrix

This section is the normative matrix for platform and renderer targets. Other references to platforms or renderers in this README are descriptive; in any conflict, this matrix defines the supported set.

Dominium supports a matrix of platform backends and renderers.

Platforms: SDL1, SDL2, Win32, Win16, Win32s, Win9x, NT3-11, macOS 7-9 (Classic/Carbon), macOS X+, POSIX, X11, Wayland, DOS, CP/M-80/86 (tooling/limited frontends), Linux/BSD, Android.

Renderers: software rasterizers, vector renderers, OpenGL 1.x/2.x, DirectX 9/11/12, Vulkan 1.x, VGA/EGA/CGA/MDA/Hercules, VESA modes, QuickDraw, Carbon/Quartz, Metal, WinG (where appropriate).

Any platform can run any compatible renderer or headless mode and use the same save files. Renderers are pure consumers of engine state; they never change simulation results.

---

## 10. Installer + Launcher

Three installation modes:

- **Portable** - everything under a single directory; no system-wide registry entries or global config.
- **Per-user** - engine/runtime binaries shared; user-specific saves, configs, mods under profile directories.
- **All-users** - system-wide installation for multi-user environments; shared content; per-user saves and mods.

Setup/installer provides install, repair, uninstall. Repair audits manifest vs actual files; restores missing or corrupted core assets and binaries but does not overwrite user saves or mods.

In "per-user" and "all-users" modes, universes, saves, and per-user configs are stored outside the installation tree in user-specific locations (for example, under profile directories). In "portable" mode, all data lives under a single directory tree alongside the binaries.

Launcher manages:

- Multiple installed versions and ports
- Multiple universes and surfaces
- Mods and content packs
- Tools and editors
- Accounts, stats, and playtime tracking (non-intrusive)
- Server discovery and network browsing

Standard scripts (per platform; names may vary):

- `setup` -> installer/repair/uninstaller wrapper
- `dominium` -> launcher binary

The game runtime can always be executed directly; the launcher is never mandatory.

---

## 11. Contributing

Contributions must satisfy:

- **Determinism preserved** - no floats in `/engine`; no nondeterministic APIs (system time, threads, I/O) in core or scripted interfaces.
- **C89/C++98 compliance** - `/engine` uses C89 only; `/runtime`, `/launcher`, `/tools` use C++98; limited STL as documented.
- **Specification-first changes** - behavioural or format changes require spec updates in `/docs/spec/` before or alongside code; directory contracts and data formats must be updated.
- **Tests** - new features require unit tests where reasonable, replay determinism tests (hashes/states over fixed sequences), integration tests for new systems or formats.
- **Documentation** - README and relevant docs updated for new public features; internal developer notes updated for non-public changes.
- **Strict prohibitions:**  
  - No floats in simulation or core IO.  
  - No platform API calls from `/engine`.  
  - No game logic in `/engine` - only generic engine capabilities.  
  - No hidden global state that affects determinism.

---

## 12. License

Licensing is tiered:

- **Engine core (Domino)** - target: permissive open source (exact license TBD); allows linking into proprietary runtimes while preserving open engine.
- **Game assets (Dominium content)** - proprietary or Creative Commons (for example, CC-BY-NC) per pack; exact terms per content pack documented.
- **Tools** - open source where possible (likely same as engine).
- **Mods** - owned by their authors; distribution terms per mod; determinism rules still enforced by engine.

Authoritative legal text: `/docs/legal/LICENCE.md` and related legal documents.

---

## 13. Status

- **Completed / Solidified:** deterministic kernel specification; fixed-point numeric model and world scale hierarchy; world addressing scheme (Segments/Regions/Chunks/Pages); ECS foundation and entity ID rules; canonical phasing/order of simulation tick; basic serialization design (TLV, Region/Chunk, Universe/Surface meta); preliminary chunk/subchunk world formats; content registry design (materials, recipes, volumes); mod loading and ordering model; platform and renderer abstraction frameworks (design-level).
- **In Development / Planned:** full renderer integration across multiple backends; cut/fill terrain implementation over SDF plus EditOps; hydrology and atmosphere solvers (macro fields); FluidSpaces and compartmental fluid/thermal systems; orbital logistics and space/rail graphs; worker/robot and agent AI stacks; deterministic clustered server infrastructure; editor suite (terrain, networks, buildings, systems); retro platform parity (DOS, Win3.x, Win9x, macOS Classic, etc.); unified launcher ecosystem for all ports and runtimes.

Concrete implementation status is tracked in `/docs/spec/MILESTONES.md` and the issue tracker/project boards.

---

## 14. Community

Documentation: `/docs/design/` and `/docs/spec/`  
Roadmap: `/docs/spec/MILESTONES.md`  
Issues and tasks: GitHub issue tracker and project boards

Community infrastructure: Discord, dev-blog, and mailing lists to be formalized once the core engine is sufficiently stable.

---

## 15. Acknowledgements

Dominium draws influence from deterministic simulation traditions in games and scientific computing; retro engineering practices emphasizing hardware frugality and predictable behaviour; long-term archival design philosophies and format stability; the modding communities of sandbox and factory games.

---

## 16. Final Note

Dominium is an attempt at a universal deterministic simulation engine and game ecosystem:

- Cross-era hardware
- Perfect or near-perfect reproducibility
- Planetary plus orbital scale
- Unlimited but safe mod extensibility
- Long-term archival survivability

This README will evolve as the specifications advance. The definitive rules, formats, and behaviour contracts always reside in `/docs/spec`.
