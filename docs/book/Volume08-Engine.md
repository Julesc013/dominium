```markdown
// docs/book/Volume08-Engine.md
# Dominium Design Book v3.0
## Volume 08 — Engine

### Overview
The engine is a deterministic C89 core with optional C++98 modules, built via CMake/Make/MSVC for Windows/macOS/Linux (with retro paths). It implements the ECS, messaging/job systems, persistence, spatial indexing, and deterministic kernel rules that underpin all simulation, UI, and modding.

### Requirements (MUST)
- Core modules compile cleanly as C89 using only allowed headers; no C99 features, VLAs, designated initialisers, or non-portable extensions. Non-core C++98 uses no exceptions/RTTI/templates across APIs.
- Platform abstraction: no platform-specific code in core; platform interfaces wrap OS/graphics.
- Build systems: CMake primary; Make (Linux/minimal) and MSVC projects supported. Build modes: Debug, Release, DeterministicRelease.
- Output artifacts: `dom_client`, `dom_server`, `dom_hclient`, `dom_tools_*`.
- ECS: stable entity IDs (uint64) with generation, deterministic ascending iteration, dense component arrays, no pointer identity.
- Messaging: fixed-size POD messages; local/lane/cross-lane/global buses; deterministic ordering; no dynamic allocation; no mutation after creation.
- Job system: fixed-struct jobs with priorities and payload; deterministic routing to humans/robots/machines; no random assignment.
- Persistence: packed, endian-stable savefiles (`*.dom`) with version/mod lists, seeds, tick counter, component hashes; CRC per major block; no floats/pointers; fixed-size structs.
- Spatial indexing: integer grid (1 m), chunk/subchunk layers, acceleration (BVH/cell/wide grid); deterministic collision layers and prefab/resource ID assignment.
- Data integrity: deterministic RNG only; no allocator churn in simulation loop; no global mutable state outside spec; serialised forms endian/alignment neutral and forward/backward compatible.

### Recommendations (SHOULD)
- Use dense arrays and sorted iteration for cache efficiency and determinism.
- Preallocate memory in load/startup/entity creation phases; avoid runtime allocations.
- Use deterministic fixed iteration solvers and bounded buffers; assert in debug for illegal states.
- Provide legacy renderer support (SDL1/GL1/DX9) and modern paths (SDL2/GL2/DX11/software).

### Prohibitions (MUST NOT)
- No floating-point in simulation or persistence; no implicit RNG/time usage.
- No nondeterministic data structures or parallel scheduling; no lane migration.
- No dynamic allocation in tick; no garbage collection during simulation.
- No STL across API boundaries; no exceptions/RTTI in C++ modules.

### Detailed Sections
#### 8.1 — Language and Platform Rules
- C89 core; allowed headers `<stdio.h> <string.h> <stdlib.h> <stddef.h> <limits.h> <float.h>`.
- No `stdbool.h`/`stdint.h` in core; platform wrappers supply compatibility if needed.
- C++98 modules avoid exceptions/RTTI; STL internal use discouraged.

#### 8.2 — Build and Outputs
- Build systems: CMake, Make, MSVC; build modes Debug/Release/DeterministicRelease.
- Target platforms stage 1: Windows 2000+, macOS 10.6+, Linux (glibc ≥2.5); stage 2 adds Win98 SE+/classic macOS/DOS; future mobile/WASM/consoles.
- Render backends: SDL1, SDL2, OpenGL 1.1/2.0, DX9; later DX11/software renderer.

#### 8.3 — ECS and Memory Layout (Volume 1B-1)
- Entities: handle = (entity_id << 32) | generation; creation/destruction emit events; reuse only after reset.
- Components: dense ID-indexed arrays; no maps/trees as primary iteration.
- Iteration strictly ascending entity_id; no pointer storage in saves/network.
- No allocation during tick; zero/clear on destruction; component defaults deterministic.

#### 8.4 — Messaging and Jobs (Volumes 1B-2a/1B-2b)
- Messaging layers: local, lane, cross-lane, global; messages are POD structs with type/flags/system/sender/receiver/tick and fixed payload unions.
- Command buffers/deferred ops tick-scoped; no implicit discard.
- Job struct: job_type, priority (lower = higher), requester/assignee/target IDs, tick_created, estimated_ticks, payload[8]; jobs queued deterministically.
- Interrupts and task routing follow tick phases; no nondeterministic scheduling.

#### 8.5 — Persistence and Data Formats (Volume 1B-3a, DATA_FORMATS)
- Savefile layout: header, metadata, world snapshot, chunk/subchunk blocks, entity/component stores, network graphs, economy/climate/RNG seeds, replay log.
- Endian-stable little-endian; packed structs; CRC per major block.
- Supported data formats: savegame binary deterministic; mod package `.dmod` (zip with manifest/data/scripts/assets/tech_tree); blueprints JSON/binary (nodes/edges/placement/resources); replays input-only or snapshot+delta.

#### 8.6 — Spatial Indexing and Physics Abstraction (Volume 1B-3b)
- Grid 1 m resolution; chunk/subchunk tables; acceleration (BVH) for queries.
- Collision layers and collider classes deterministic; terrain sampling rules fixed.
- Prefab system and mod injection follow deterministic ID/linking; resource loading order fixed.

#### 8.7 — Determinism Kernel Summary (Volumes 1A-1/1A-2)
- Tick phases fixed; canonical UPS; virtual lanes with ordered merge; network propagation rules; deterministic backpressure/clamping; lockstep multiplayer; error handling and degradation rules.

### Cross-References
- Volume 01 — Vision (engine-first mandate)
- Volume 02 — Simulation (tick phases, lanes)
- Volume 03 — World (spatial indexing usage)
- Volume 04 — Networks (graph storage/solvers)
- Volume 05 — Economy (persisted financial state)
- Volume 06 — Climate (EnvCell persistence)
- Volume 07 — UIUX (EMB, logging, command stack)
- Volume 09 — Modding (pack structure, Lua sandbox)
```
