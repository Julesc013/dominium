# Aggregator Packet — Dominium World Architecture

## 1. Packet Metadata

* Chat label: Dominium World Architecture
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: THIS CHAT ONLY, including previous Context Transfer Packet visible in this chat.
* Coverage: Full visible-chat coverage, no repo files inspected.
* Confidence: 4/5.
* Staleness risk: Low for internal design; medium for toolchain/software assumptions.
* Merge priority: High.
* Main limitations: Previous Codex prompt is defective; exact repo/build/toolchain unknown; solver formulas unresolved.

## 2. Ultra-Condensed Carry-Forward Capsule

This chat was a sustained architecture-design session for the **Dominium World Architecture** workstream. It defined how a future Dominium-style game world should represent space, terrain, saves, runtime memory, deterministic simulation, environmental systems, tools, mods, and a Codex implementation plan. The most important output is not a single feature spec but a coherent design philosophy: all authoritative simulation state should live in deterministic, fixed-point, content-agnostic core structures, while chunks/segments are storage and cache boundaries only.

The final spatial model is a power-of-two hierarchy with named scales from Plank through Surface. The horizontal surface is a toroidal 2^24 metre grid in X/Y, with X east and Y north. Z is not toroidal; the user confirmed one Page of vertical space, 4096 m total, centered at sea level, meaning roughly 2 km down and 2 km up. Chunk size is 16×16×16 m, giving 256 vertical chunk layers. Runtime positions use an 8-bit Segment index plus local Q16.16 precision; save positions use Q4.12 local-to-chunk. The packet identifies a critical correction to the prior Codex prompt: signed Q16.16 cannot represent the full local segment range [0,65536), and signed Q4.12 cannot represent the full chunk-local range [0,16). Future work should use unsigned local fixed types or an explicitly centered signed coordinate scheme.

The user imposed hard implementation constraints: no floats in the core or save files; C89 for the core; C++98 and floats allowed only in platform/renderer/runtime layers, with no feedback into core state. This creates another unresolved engineering issue: strict ISO C89 lacks standard fixed-width and 64-bit integer types, while the architecture needs 64-bit IDs, RNG state, and fixed-point accumulators. A portability layer or a documented “C89-style plus compiler 64-bit extension” policy is required before coding.

The terrain model converged on continuous signed geometry `φ`, not block matter. Chunks sample `φ` for meshing/collision but never own truth. Ground and air are abstract media, not blocks. Materials, phases, pressure, density, hardness, temperature, and composition are represented through registries, fields, SpatialVolumes, FluidSpaces, and solver modules. Full per-material 3D density fields were rejected as storage-expensive and conceptually wrong.

Environmental systems were unified under reusable patterns. FluidSpaces and Connectors model air, vapour, liquids, tanks, rooms, atmosphere, hydrology, reservoirs, rivers, and flooding. SpatialVolumes model caves, ore pockets, gas pockets, voids, basins, magma chambers, oil reservoirs, and local field effects. Networks model pipes, hydraulic flow, electrical power, heat, and logic, while full global CFD, EM simulation, FEA, and broad chemistry were explicitly scoped out. Oil fields, gas pressure, tank ruptures, and mineshaft flooding were mapped onto the same FluidSpace/Connector/HydraulicNet/SpatialVolume design.

The save model is sparse and deterministic. Procedural defaults are regenerated from content, recipes, and seeds; saves store only deltas and dynamic state. The cosmic hierarchy is 2^8 galaxies per universe, 2^24 systems per galaxy, and 2^16 planets per system. Internally arbitrary surface instances may exist later, but saves currently store one canonical surface per planet. Save files use directory names for high address bits and TLV chunk sections for extensibility. `content.lock` fixes content packs, versions, hashes, and deterministic registry order. Unknown TLV sections can be skipped; migrations should be explicit.

A major artifact was a Codex 5.1 implementation prompt, but it must not be used unchanged. It is useful structurally, but contains known bugs around signed fixed-point, Region bit widths, C89 syntax, and saved rotation ambiguity. The best next action is to revise that prompt and inspect the actual repository before code generation.

The most important aggregator warning is that several items are assistant design conclusions rather than direct user statements. They should be preserved as INFERENCE unless a future chat contains explicit confirmation. Direct user decisions include the 2^24 toroidal surface, one Page Z, runtime Q16.16, save Q4.12, 8-bit Segment addressing, no floats in core/saves, C89 core, C++98 platform/renderer, final cosmic ID counts, and one canonical saved surface per planet. The critical repair items are also central: unsigned local fixed-point types and corrected Region bit widths.

## 3. Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
|---|---|---|---|---|---|---|
| 1 | No floats in core/saves | constraint | CONSTRAINT-01/02 | Hard user requirement and determinism foundation | FACT | 5 |
| 2 | Torus 2^24m X/Y and one Page Z | decision | DECISION-01/02 | Defines world size and address math | FACT | 5 |
| 3 | Runtime Q16.16 and save Q4.12 with unsigned correction | decision/correction | DECISION-04/05, VERIFY-01/02 | Prevents overflow/corruption | FACT | 5 |
| 4 | Chunks are caches, not authorities | architecture | DECISION-15 | Preserves determinism across streaming | FACT | 5 |
| 5 | φ terrain and abstract media, not block matter | architecture | DECISION-19/20 | Defines world representation | FACT | 5 |
| 6 | FluidSpaces/Connectors/Networks/SpatialVolumes pattern | architecture | DECISION-22/23/29 | Unifies environment systems | INFERENCE | 4 |
| 7 | content.lock and deterministic registries | architecture | DECISION-33/35 | Required for modded determinism | FACT | 5 |
| 8 | Previous Codex prompt must be repaired before use | artifact warning | ARTIFACT-01/TASK-01 | Avoids known implementation bugs | FACT | 5 |

## 4. Workstream Summaries

### WORKSTREAM-01 — Spatial coordinate model and scale hierarchy
- Objective: Define the world’s spatial scale, axes, wrap behavior, chunk hierarchy, and origin convention.
- Current state: User-confirmed toroidal horizontal SurfaceGrid of 2^24 m per axis, one vertical Page of 4096 m, 16 m cubic chunks, and final scale names from Plank to Surface.
- Desired end state: A deterministic coordinate implementation with safe fixed-point conversion across Segment, Region, Chunk, Block, and local coordinates.
- Priority: critical
- Decisions: DECISION-01, DECISION-02, DECISION-03, DECISION-08, DECISION-17
- Tasks: TASK-01, TASK-02, TASK-03
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-04, CONSTRAINT-05, CONSTRAINT-06
- Artifacts: ARTIFACT-01, ARTIFACT-02
- Risks: RISK-01, RISK-02, RISK-03
- Open questions: QUESTION-01, QUESTION-02, QUESTION-03
- Next action: Correct fixed-point types and write addressing conversion tests.

### WORKSTREAM-02 — Deterministic fixed-point C89 core
- Objective: Build the core simulation library using deterministic fixed-point arithmetic with no floats in core or saves.
- Current state: Design established; implementation prompt produced but needs correction for C89 and fixed-point signedness.
- Desired end state: A C89-style core library with fixed-point math, RNG, ECS, world services, save/load, and no float/double usage.
- Priority: critical
- Decisions: DECISION-04, DECISION-05, DECISION-06, DECISION-07
- Tasks: TASK-01, TASK-04, TASK-05, TASK-10
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-03, CONSTRAINT-07
- Artifacts: ARTIFACT-01, ARTIFACT-06
- Risks: RISK-02, RISK-04, RISK-05
- Open questions: QUESTION-01, QUESTION-04
- Next action: Define portability header and fixed-point API before other modules.

### WORKSTREAM-03 — Sparse save file architecture
- Objective: Persist only dynamic state and procedural deltas using a hierarchical universe save and TLV region/chunk files.
- Current state: Architecture designed; exact binary details remain pending.
- Desired end state: Versioned, sparse, deterministic save files with content.lock, metadata, Region files, Chunk TLVs, global environment/network files, and migration support.
- Priority: critical
- Decisions: DECISION-09, DECISION-10, DECISION-11, DECISION-12, DECISION-13, DECISION-14
- Tasks: TASK-06, TASK-07, TASK-11
- Constraints: CONSTRAINT-08, CONSTRAINT-09, CONSTRAINT-10, CONSTRAINT-12, CONSTRAINT-17
- Artifacts: ARTIFACT-03, ARTIFACT-04, ARTIFACT-07
- Risks: RISK-06, RISK-07, RISK-08
- Open questions: QUESTION-05, QUESTION-06, QUESTION-07
- Next action: Write DATA_FORMATS.md and implement TLV reader/writer.

### WORKSTREAM-04 — Runtime memory model, chunking, streaming, and continuity
- Objective: Keep active memory sparse and deterministic while chunks/segments never alter simulation truth.
- Current state: Design conclusion: chunks are caches; state lives in global/topological systems.
- Desired end state: Sparse SurfaceRuntime/ChunkRuntime with lazy terrain caches, vertical chunk bitsets, async mesh/IO later, and deterministic streaming-independent results.
- Priority: high
- Decisions: DECISION-15, DECISION-16, DECISION-18
- Tasks: TASK-08, TASK-09, TASK-15
- Constraints: CONSTRAINT-11, CONSTRAINT-13, CONSTRAINT-14
- Artifacts: ARTIFACT-02, ARTIFACT-05
- Risks: RISK-09, RISK-10
- Open questions: QUESTION-08, QUESTION-09
- Next action: Implement sparse chunk table and seam tests.

### WORKSTREAM-05 — Continuous terrain, geometry, materials, and media
- Objective: Represent smooth arbitrary terrain and abstract materials with continuous fields rather than block matter.
- Current state: Core model established: geometry φ + material/media/phase fields + sampled chunk meshes.
- Desired end state: A field-provider-based terrain/material system supporting caves, cliffs, volcanoes, floating solids, voids, and arbitrary sub-meter geometry.
- Priority: high
- Decisions: DECISION-19, DECISION-20, DECISION-21, DECISION-22
- Tasks: TASK-12, TASK-16, TASK-20
- Constraints: CONSTRAINT-15, CONSTRAINT-16
- Artifacts: ARTIFACT-08
- Risks: RISK-11, RISK-12
- Open questions: QUESTION-10, QUESTION-11
- Next action: Implement minimal fixed-point φ provider and material registry.

### WORKSTREAM-06 — FluidSpaces, hydrology, weather, climate, rooms, tanks
- Objective: Unify liquids, gases, vapours, weather, climate, rooms, tanks, basins, rivers, and atmosphere through FluidSpaces and Connectors.
- Current state: Architecture designed; solvers not nailed down.
- Desired end state: Deterministic fixed-point fluid/environment systems with global atmosphere/hydrology and local enclosed compartment support.
- Priority: medium
- Decisions: DECISION-23, DECISION-24, DECISION-25
- Tasks: TASK-17, TASK-18, TASK-21
- Constraints: CONSTRAINT-18, CONSTRAINT-19
- Artifacts: ARTIFACT-09
- Risks: RISK-13, RISK-14
- Open questions: QUESTION-12, QUESTION-13, QUESTION-14
- Next action: Specify fixed-point FluidSpace state and connector equations.

### WORKSTREAM-07 — Oil fields, gas pockets, pressure, ruptures, flooding, rivers
- Objective: Use the fluid/network/volume model to support oil reservoirs, gas pockets, pressure, ruptures, mineshaft flooding, river flow, tank rupture, and flooding.
- Current state: Design mapped onto existing primitives; implementation not started.
- Desired end state: Reservoirs and floods are deterministic state transitions and flows through FluidSpaces, Connectors, Hydrology, and HydraulicNet.
- Priority: medium
- Decisions: DECISION-26, DECISION-27, DECISION-28
- Tasks: TASK-22, TASK-23
- Constraints: CONSTRAINT-19, CONSTRAINT-20
- Artifacts: ARTIFACT-10
- Risks: RISK-15, RISK-16
- Open questions: QUESTION-15, QUESTION-16
- Next action: Define reservoir FluidSpace schema and rupture event rules.

### WORKSTREAM-08 — Thermal, hydraulic, electrical, logic, and limited EM systems
- Objective: Apply Spaces/Connectors/Networks pattern to routed systems while avoiding full multiphysics simulation.
- Current state: Scope boundaries and graph abstraction established.
- Desired end state: Separate deterministic graph/network modules for hydraulic, electrical, logic, and thermal systems, linked to world objects and saved globally.
- Priority: medium
- Decisions: DECISION-29, DECISION-30, DECISION-31, DECISION-32
- Tasks: TASK-24
- Constraints: CONSTRAINT-20, CONSTRAINT-21
- Artifacts: ARTIFACT-11
- Risks: RISK-17
- Open questions: QUESTION-17
- Next action: Stub network modules and global_networks.bin sections.

### WORKSTREAM-09 — Mod/content system, registries, JSON/Lua, content.lock
- Objective: Make official and modded content use deterministic registries and content packs without core hardcoding.
- Current state: Design established; schemas and sandbox implementation pending.
- Desired end state: Content packs and mods define materials/recipes/fields/solvers through JSON/Lua; core loads deterministic registries from content.lock.
- Priority: high
- Decisions: DECISION-33, DECISION-34, DECISION-35
- Tasks: TASK-13, TASK-14, TASK-25
- Constraints: CONSTRAINT-22, CONSTRAINT-23
- Artifacts: ARTIFACT-12
- Risks: RISK-18, RISK-19
- Open questions: QUESTION-18, QUESTION-19
- Next action: Write content manifest and registry spec.

### WORKSTREAM-10 — Whole-project modular architecture: engine, runtime, launcher, tools, mods
- Objective: Extend the deterministic modular philosophy to the entire repo and toolchain.
- Current state: Directory/layering design proposed; actual repo not inspected.
- Desired end state: Engine static library, C++98 runtimes, metadata-only launcher, tools reusing engine IO, content/mod SDK, versioned migrations.
- Priority: high
- Decisions: DECISION-36, DECISION-37, DECISION-38
- Tasks: TASK-26, TASK-27, TASK-28
- Constraints: CONSTRAINT-24, CONSTRAINT-25
- Artifacts: ARTIFACT-13
- Risks: RISK-20, RISK-21
- Open questions: QUESTION-20, QUESTION-21
- Next action: Inspect repo and adapt architecture without blind overwrites.

### WORKSTREAM-11 — Codex implementation prompt and code generation plan
- Objective: Produce a Codex-ready prompt to implement/refactor repo according to the architecture.
- Current state: A long prompt was generated but is known defective in fixed-point/C89 details and must be revised.
- Desired end state: A corrected, repo-aware Codex prompt or set of smaller implementation prompts.
- Priority: critical
- Decisions: DECISION-39
- Tasks: TASK-01, TASK-29
- Constraints: CONSTRAINT-01, CONSTRAINT-03, CONSTRAINT-05
- Artifacts: ARTIFACT-01
- Risks: RISK-01, RISK-02, RISK-22
- Open questions: QUESTION-22
- Next action: Audit/rewrite the Codex prompt using this report.

### WORKSTREAM-12 — Testing, verification, determinism, seam validation
- Objective: Ensure world state is deterministic, seamless, and independent of chunk streaming.
- Current state: Test strategy described; no tests created in chat.
- Desired end state: Automated tests for save/load hash equivalence, streaming-order independence, seam continuity, and network continuity.
- Priority: high
- Decisions: DECISION-40, DECISION-41
- Tasks: TASK-10, TASK-30
- Constraints: CONSTRAINT-26, CONSTRAINT-27
- Artifacts: ARTIFACT-14
- Risks: RISK-23, RISK-24
- Open questions: QUESTION-23
- Next action: Define canonical world-state hash and seam probe tests.

### WORKSTREAM-13 — Documentation, reports, and future Project Spec Book
- Objective: Preserve design state and create documents usable for future implementation and aggregation.
- Current state: Context Transfer Packet created; this package now exports normalized report files.
- Desired end state: Markdown/YAML report package plus repo docs that feed into a future full Project Spec Book.
- Priority: high
- Decisions: DECISION-42
- Tasks: TASK-31, TASK-32
- Constraints: CONSTRAINT-28, CONSTRAINT-29
- Artifacts: ARTIFACT-15, ARTIFACT-16, ARTIFACT-17, ARTIFACT-18, ARTIFACT-19, ARTIFACT-20, ARTIFACT-21
- Risks: RISK-25, RISK-26
- Open questions: none recorded
- Next action: Save ZIP package and use it in a new chat or aggregator later.

## 5. Registers for Merge

### Decision Register
| ID | Decision | Status | Evidence | Rationale | Workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|
| DECISION-01 | Use a toroidal 2^24m horizontal SurfaceGrid per axis | final | User explicitly confirmed toroidal 2^24m surface. | Large seamless wrapped world; modulo X/Y. | WORKSTREAM-01 | 5 | FACT |
| DECISION-02 | Use one vertical Page of 4096m for Z, 2km up and 2km down | final | User explicitly confirmed 1 Page for Z. | Simplifies vertical storage; 256 vertical chunk layers. | WORKSTREAM-01 | 5 | FACT |
| DECISION-03 | Use cubic chunks of 16×16×16m | final | Repeated user framing and assistant confirmation. | Uniform meshing/streaming unit. | WORKSTREAM-01 | 5 | FACT |
| DECISION-04 | Use Q16.16 for runtime/transient working memory | final with type correction needed | User stated runtime q16.16. | High precision moving objects; local math. | WORKSTREAM-02 | 5 | FACT |
| DECISION-05 | Use Q4.12 save-local positions inside chunks | final with unsigned correction needed | User stated save q4.12 in chunks. | 16-bit local coordinate with 1/4096m precision. | WORKSTREAM-02 | 5 | FACT |
| DECISION-06 | Use 8-bit Segment addressing | final | User stated 8bit integer for segment addressing. | 8 bits × 2^16m = 2^24m. | WORKSTREAM-01 | 5 | FACT |
| DECISION-07 | Core and saves must not use floats | final | User stated floats cannot be allowed in core or saves. | Determinism; fixed-point all core quantities. | WORKSTREAM-02 | 5 | FACT |
| DECISION-08 | Platform and renderer may use C++98 and floats | final | User explicitly allowed C++98/floats for platform/renderer. | Renderer can convert core ints to floats one-way. | WORKSTREAM-02 | 5 | FACT |
| DECISION-09 | Universe cosmic limits are 2^8 galaxies, 2^24 systems/galaxy, 2^16 planets/system | final | User explicitly revised these limits. | Directory IDs: galaxy 8-bit, system 24-bit, planet 16-bit. | WORKSTREAM-03 | 5 | FACT |
| DECISION-10 | Save one canonical surface per planet for now | final | User explicitly stated only one canonical surface in save files. | No surface instance directory needed initially; internal arbitrary surfaces later. | WORKSTREAM-03 | 5 | FACT |
| DECISION-11 | Use directory names to encode high addresses | final intent | User asked to take advantage of directory names for addresses. | Reduces per-object storage; improves sparse addressing. | WORKSTREAM-03 | 4 | FACT |
| DECISION-12 | Use sparse Region files containing chunk blobs | accepted design | Assistant recommended; user continued from it. | Avoid file-per-chunk explosion while supporting sparse/dense worlds. | WORKSTREAM-03 | 4 | INFERENCE |
| DECISION-13 | Use TLV chunk sections for future-proof save data | accepted design | Assistant proposed and used throughout later design. | Unknown sections can be skipped; mod/core extension. | WORKSTREAM-03 | 4 | INFERENCE |
| DECISION-14 | Save procedural defaults as seeds/recipes, not full state | accepted design | Repeated in assistant design; user built on it. | Saves only deltas/dynamic state. | WORKSTREAM-03 | 4 | INFERENCE |
| DECISION-15 | Chunks/segments are caches/storage partitions, not authorities | accepted design | Central principle in implementation/determinism answer. | Prevents streaming from changing simulation results. | WORKSTREAM-04 | 5 | FACT |
| DECISION-16 | Use sparse vertical chunk loading and avoid untouched chunk saves | accepted design | User asked; assistant proposed sparse vertical chunks and states. | Memory/storage optimization. | WORKSTREAM-04 | 4 | INFERENCE |
| DECISION-17 | Origin (0,0,0) is block vertex/corner, not block center | accepted recommendation | Assistant recommended; no objection and later summaries used it. | Simplifies floor/bit/chunk mapping. | WORKSTREAM-01 | 4 | INFERENCE |
| DECISION-18 | Spawn offset is not required for performance | accepted recommendation | Assistant concluded boundary crossing cheap; no objection. | Spawn can be gameplay-driven. | WORKSTREAM-04 | 4 | INFERENCE |
| DECISION-19 | World geometry is a continuous signed field φ | accepted design | Repeated after user asked about smooth world; user built on it. | Supports smooth terrain, cuts, fills, caves, arbitrary geometry. | WORKSTREAM-05 | 5 | FACT |
| DECISION-20 | Ground and air are abstract media, not blocks | final | User explicitly stated ground/air will not be made of blocks. | No block-based matter; fields/materials determine composition. | WORKSTREAM-05 | 5 | FACT |
| DECISION-21 | Do not store separate full density fields per material | accepted design | Assistant rejected as storage explosion; user did not object. | Use material/phase/composition maps and sparse volumes. | WORKSTREAM-05 | 4 | INFERENCE |
| DECISION-22 | Use SpatialVolumes as unified pockets/basins/voids/gas/magma/etc. | accepted design | Assistant proposed; later questions built on it. | Extensible local field effects. | WORKSTREAM-05 | 4 | INFERENCE |
| DECISION-23 | Use FluidSpaces + Connectors for liquids, gases, weather, rooms, tanks | accepted design | Assistant proposed in response to user; user built onward. | Unified fluid/climate/interior model. | WORKSTREAM-06 | 4 | INFERENCE |
| DECISION-24 | Weather/climate can operate in rooms/buildings/tanks as local FluidSpaces | accepted design | Direct answer to user question; no objection. | Room air/HVAC and tanks share fluid abstraction. | WORKSTREAM-06 | 4 | INFERENCE |
| DECISION-25 | Hydrology uses basins/heightfields/graphs, not water blocks | accepted design | Repeated assistant response; user continued. | Efficient rivers, oceans, lakes, canals. | WORKSTREAM-06 | 4 | INFERENCE |
| DECISION-26 | Oil/gas reservoirs are SpatialVolumes linked to FluidSpaces | accepted design | Final oil/flooding answer. | Reservoirs are not voxel fluids. | WORKSTREAM-07 | 4 | INFERENCE |
| DECISION-27 | Ruptures are deterministic structural failures that create connectors | accepted design | Final oil/flooding answer. | Tank/pipe/rock failures change graph topology. | WORKSTREAM-07 | 4 | INFERENCE |
| DECISION-28 | Flooding is flow through FluidSpaces/connectors/hydrology, not chunk fluid simulation | accepted design | Final oil/flooding answer. | Mineshaft flooding independent of chunk loading. | WORKSTREAM-07 | 4 | INFERENCE |
| DECISION-29 | Use graph-based hydraulic networks for pipes | accepted design | Pipes/cables/heat answer. | Avoids full fluid PDE in pipes. | WORKSTREAM-08 | 4 | INFERENCE |
| DECISION-30 | Use graph/circuit networks for electrical power and logic | accepted design | Pipes/cables/heat answer. | Avoids full EM simulation. | WORKSTREAM-08 | 4 | INFERENCE |
| DECISION-31 | Use ThermalSpaces/thermal connectors for heat | accepted design | Pipes/cables/heat answer. | Lumped deterministic heat model. | WORKSTREAM-08 | 4 | INFERENCE |
| DECISION-32 | Do not simulate full EM/CFD/FEA globally | accepted scope limit | Assistant stated; no objection. | Keeps core tractable. | WORKSTREAM-08 | 4 | INFERENCE |
| DECISION-33 | Use content.lock for exact content set and deterministic registries | accepted design | User asked deterministic JSON/Lua; assistant proposed. | Official/modded content become data feeding core. | WORKSTREAM-09 | 5 | FACT |
| DECISION-34 | Lua, if used, must be deterministic sandboxed | accepted design | Assistant proposed; no objection. | No OS/time/random/nondeterministic table iteration. | WORKSTREAM-09 | 4 | INFERENCE |
| DECISION-35 | Core must be agnostic to official vs modded content | final intent | User explicitly asked for this. | Registries/interfaces instead of hardcoded content. | WORKSTREAM-09 | 5 | FACT |
| DECISION-36 | Whole project should use strict layering: engine/runtime/launcher/tools/content/modsdk | accepted design | Assistant proposed; user requested broad philosophy. | Future-proof modular repo. | WORKSTREAM-10 | 4 | INFERENCE |
| DECISION-37 | Launcher should orchestrate runtimes and read metadata, not simulate | accepted design | Whole-project architecture answer. | Separates UI/install from core. | WORKSTREAM-10 | 4 | INFERENCE |
| DECISION-38 | Tools should reuse engine IO and not hand-roll formats | accepted design | Whole-project architecture answer. | Avoids drift between tools and game. | WORKSTREAM-10 | 4 | INFERENCE |
| DECISION-39 | Codex prompt should implement/refactor relevant code/docs | requested artifact | User explicitly requested Codex 5.1 optimized prompt. | Prompt produced but must be corrected. | WORKSTREAM-11 | 5 | FACT |
| DECISION-40 | Use fixed deterministic simulation order | accepted design | Implementation/determinism answer. | Avoids order-dependent divergences. | WORKSTREAM-12 | 4 | INFERENCE |
| DECISION-41 | Use tests for save/load, seam, streaming-order determinism | accepted design | Assistant recommended; no objection. | Detects core failure modes early. | WORKSTREAM-12 | 4 | INFERENCE |
| DECISION-42 | Create final report package with Markdown/YAML/ZIP | final current task | User requested this package. | Creates reusable handoff for aggregation/spec book. | WORKSTREAM-13 | 5 | FACT |

### Task Register
| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs | Expected output | Next step | Workstream | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Audit and correct the previous Codex implementation prompt | critical | immediate | new chat / Codex | ARTIFACT-01 | This report | Corrected Codex prompt | Fix fixed-point, C89, region bits, rotation issues | WORKSTREAM-11 | FACT |
| TASK-02 | Define canonical fixed-point typedefs | critical | immediate | Codex | DECISION-04, DECISION-05 | Compiler constraints | Fixed-point header/spec | Use unsigned local UQ16.16/UQ4.12 or explicitly choose centred scheme | WORKSTREAM-01, WORKSTREAM-02 | FACT |
| TASK-03 | Implement SimPos↔address conversion and wrap tests | critical | early | Codex | TASK-02 | Coordinate constants | world_addr module and tests | Test segment, region, chunk, block, local round-trips | WORKSTREAM-01 | INFERENCE |
| TASK-04 | Create C89 portability layer | critical | early | Codex |  | Compiler targets | core_types.h with fixed-width types | Resolve 64-bit support in C89-style code | WORKSTREAM-02 | INFERENCE |
| TASK-05 | Implement deterministic RNG and coordinate hash | high | early | Codex | TASK-04 | Seed policy | core_rng module | Use explicit RNG state plus stateless hashes | WORKSTREAM-02 | INFERENCE |
| TASK-06 | Specify and implement TLV save reader/writer | high | early | Codex | TASK-04 | Endian/alignment policy | save_tlv module | Write DATA_FORMATS.md first | WORKSTREAM-03 | INFERENCE |
| TASK-07 | Implement Region/Chunk sparse save files | high | early | Codex | TASK-03, TASK-06 | Region file layout | save_region module | Use correct Segment/Region bit widths | WORKSTREAM-03 | INFERENCE |
| TASK-08 | Implement SurfaceRuntime and sparse ChunkRuntime cache | high | early | Codex | TASK-03 | Allocator/hash policy | world_surface/world_chunk modules | Keep chunks non-authoritative | WORKSTREAM-04 | INFERENCE |
| TASK-09 | Implement untouched/procedural/overridden chunk state logic | medium | early | Codex | TASK-08 | Dirty flags/save policy | chunk lifecycle rules | Do not save procedural caches | WORKSTREAM-04 | INFERENCE |
| TASK-10 | Add deterministic state hash/save-load test harness | high | early | Codex | TASK-05, TASK-06 | Canonical hash scheme | test executable | Run N ticks, save/reload, compare | WORKSTREAM-12 | INFERENCE |
| TASK-11 | Define universe/galaxy/system/planet/surface metadata files | high | early | Codex | TASK-06 | ID widths | save_universe module/spec | Encode 8/24/16 cosmic IDs | WORKSTREAM-03 | INFERENCE |
| TASK-12 | Implement minimal fixed-point geom_sample | high | early | Codex | TASK-02, TASK-08 | Default recipe | world_geom module | Start with simple deterministic heightfield | WORKSTREAM-05 | INFERENCE |
| TASK-13 | Implement MaterialRegistry and RecipeRegistry | high | early | Codex | TASK-04 | Initial material/recipe schema | registry modules | Use deterministic registration order | WORKSTREAM-09 | INFERENCE |
| TASK-14 | Design content.lock and manifest schema | high | early | Codex/user | TASK-13 | Content pack requirements | docs/spec and parser plan | Keep initial JSON minimal | WORKSTREAM-09 | INFERENCE |
| TASK-15 | Implement seam tests for chunk/region/segment boundaries | high | early | Codex | TASK-03, TASK-12 | Probe patterns | automated seam tests | Sample both sides of boundaries | WORKSTREAM-04, WORKSTREAM-12 | INFERENCE |
| TASK-16 | Choose v0 meshing algorithm and sample scaling | medium | early | user/Codex | TASK-12 | Performance target | meshing decision/spec | Likely start with marching cubes or simple debug mesh | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| TASK-17 | Specify FluidSpace fixed-point state model | medium | v1 | Codex/user | TASK-13 | Species/material list | sys_fluidspace schema | Define mass/energy/volume units | WORKSTREAM-06 | INFERENCE |
| TASK-18 | Specify FluidConnector equations | medium | v1 | Codex/user | TASK-17 | Pressure/flow model | connector solver spec | Pick simple deterministic orifice/pipe formulas | WORKSTREAM-06, WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| TASK-19 | Define global_env.bin and local_env TLV sections | medium | v1 | Codex | TASK-06, TASK-17 | Environment state types | save sections/spec | Store weather/hydro/fluidspace state | WORKSTREAM-06 | INFERENCE |
| TASK-20 | Implement SpatialVolume registry and dynamic volume TLV | medium | v1 | Codex | TASK-06, TASK-13 | Volume types | registry_volume and save section | Use for oil/gas/void/pockets/basins | WORKSTREAM-05, WORKSTREAM-07 | INFERENCE |
| TASK-21 | Choose atmo/weather/hydrology solver resolutions | medium | v1 | user/Codex |  | Performance goals | solver resolution spec | Prototype before finalizing | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| TASK-22 | Design oil/gas reservoir schema | medium | v1/v2 | Codex/user | TASK-17, TASK-20 | Material definitions | reservoir volume + FluidSpace schema | Define pressure, saturation, composition | WORKSTREAM-07 | INFERENCE |
| TASK-23 | Design rupture/flooding event model | medium | v1/v2 | Codex/user | TASK-18, TASK-22 | Structural component schema | rupture state machine | Create connectors on deterministic failure | WORKSTREAM-07 | INFERENCE |
| TASK-24 | Stub network modules and global_networks.bin | medium | v1/v2 | Codex | TASK-06, TASK-04 | Node/edge schema | hydraulic/electric/logic modules | Use global topological state | WORKSTREAM-08 | INFERENCE |
| TASK-25 | Define deterministic Lua sandbox | medium | later | Codex/user | TASK-14 | Lua version | sandbox spec | Ban nondeterministic APIs | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| TASK-26 | Inspect actual git repo before applying file changes | critical | before coding | new chat/Codex |  | Repo contents | repo-aware plan | Do not blindly overwrite | WORKSTREAM-10, WORKSTREAM-11 | FACT |
| TASK-27 | Set up repo directories/layering | medium | after repo audit | Codex | TASK-26 | Build system | engine/runtime/launcher/tools/docs layout | Adapt to existing repo | WORKSTREAM-10 | INFERENCE |
| TASK-28 | Create launcher/tools stubs | low | later | Codex | TASK-27 | CLI/API contracts | launcher/tool skeletons | Keep launcher metadata-only | WORKSTREAM-10 | INFERENCE |
| TASK-29 | Generate corrected Codex prompt/package from this report | critical | immediate | new chat | ARTIFACT-01, ARTIFACT-15 | User intent | safe implementation prompt | Use corrected constraints | WORKSTREAM-11 | FACT |
| TASK-30 | Implement streaming-order independence tests | high | after chunk core | Codex | TASK-10, TASK-15 | Streaming simulator | test suite | Compare hashes under different chunk loads | WORKSTREAM-12 | INFERENCE |
| TASK-31 | Save this report package and ZIP | critical | now | assistant |  | Visible chat context | downloadable files | Create Markdown/YAML/ZIP | WORKSTREAM-13 | FACT |
| TASK-32 | Use reports from old chats to build future Project Spec Book | medium | later | user/future assistant | ARTIFACT-15 | Other chat packages | master spec book | Aggregate only after all packages provided | WORKSTREAM-13 | FACT |

### Constraint Register
| ID | Constraint | Type | Hard/soft | Source | Implication | Risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-01 | No floats in engine/core code | technical | hard | User explicitly forbade floats in core. | All core quantities fixed-point; tests should detect float use. | high | 5 | FACT |
| CONSTRAINT-02 | No floats in save files | technical | hard | User explicitly forbade floats in saves. | All save values are integer/fixed; no JSON decimals for authoritative state. | high | 5 | FACT |
| CONSTRAINT-03 | Core target is C89 | language | hard | User explicitly stated C89. | Avoid C99 syntax; define portability layer for 64-bit types. | high | 5 | FACT |
| CONSTRAINT-04 | Platform/renderer may use C++98 and floats | language | hard | User explicitly allowed C++98/floats there. | Renderer converts one-way from core; no feedback. | medium | 5 | FACT |
| CONSTRAINT-05 | Runtime position precision Q16.16 | numeric | hard | User explicitly set runtime q16.16. | Define safe fixed types and conversions. | high | 5 | FACT |
| CONSTRAINT-06 | Save-local precision Q4.12 in chunks | numeric | hard | User explicitly set save q4.12 in chunks. | Use unsigned 16-bit local chunk coordinates. | high | 5 | FACT |
| CONSTRAINT-07 | Use 8-bit integer Segment addressing | numeric/spatial | hard | User explicitly set 8-bit Segment addressing. | Segment wrap modulo 256. | medium | 5 | FACT |
| CONSTRAINT-08 | Horizontal SurfaceGrid is toroidal 2^24m | spatial | hard | User explicitly confirmed. | X/Y modulo arithmetic; seam tests required. | high | 5 | FACT |
| CONSTRAINT-09 | Z is one Page = 4096m total | spatial | hard | User explicitly confirmed. | No vertical wrap; 256 vertical chunks. | medium | 5 | FACT |
| CONSTRAINT-10 | One canonical surface per planet in save files for now | storage | hard | User explicitly stated. | No persistent arbitrary surface instance layer initially. | medium | 5 | FACT |
| CONSTRAINT-11 | Chunks must not be canonical simulation authorities | architecture | hard | Determinism answer and accepted design. | Chunks are caches/references only. | high | 5 | FACT |
| CONSTRAINT-12 | Save procedural defaults as seeds/recipes plus deltas | storage | hard-ish | Accepted design from assistant response. | Do not save procedural-only chunks. | medium | 4 | INFERENCE |
| CONSTRAINT-13 | Network/FluidSpace state must be topological/global, not chunk-owned | architecture | hard-ish | Continuity/determinism design. | Streaming cannot alter pressure/flows. | high | 4 | INFERENCE |
| CONSTRAINT-14 | Boundary crossings must be O(1) and non-semantic | performance | soft/hard | User worried about boundary performance; assistant resolved. | No special gameplay state change at chunk/page/segment seams. | medium | 4 | INFERENCE |
| CONSTRAINT-15 | Ground and air are not blocks | world model | hard | User explicitly stated. | Use fields/media, not voxel matter. | high | 5 | FACT |
| CONSTRAINT-16 | Do not use full per-material 3D density fields | storage/performance | hard-ish | Assistant rejected; user did not object. | Use material IDs, composition, pockets, overlays. | medium | 4 | INFERENCE |
| CONSTRAINT-17 | Use directory names to encode addresses efficiently | storage | hard-ish | User requested. | High bits in path/file names, local coords in records. | medium | 5 | FACT |
| CONSTRAINT-18 | All fluids/gases/climate should fit unified model where possible | architecture | soft/hard | User asked can all liquids/gases/weather work this way; design accepted. | Use FluidSpace/Connector abstractions. | medium | 4 | INFERENCE |
| CONSTRAINT-19 | Avoid full global CFD/Navier–Stokes | scope/performance | hard-ish | Assistant scoped; no objection. | Use basins, graphs, compartments, coarse grids. | medium | 4 | INFERENCE |
| CONSTRAINT-20 | Avoid full global EM/FEA/multiphysics simulation | scope/performance | hard-ish | Assistant scoped; no objection. | Use graph circuits and approximations. | medium | 4 | INFERENCE |
| CONSTRAINT-21 | Electrical/logical systems should be separate graph systems | architecture | soft/hard | Assistant recommendation. | Keep concerns modular. | low | 4 | INFERENCE |
| CONSTRAINT-22 | Core must be agnostic to official vs modded content | modding | hard | User explicitly requested. | Registries/content.lock/interfaces. | high | 5 | FACT |
| CONSTRAINT-23 | Lua must be deterministic if used | modding/determinism | hard-ish | Assistant recommendation; user did not object. | Sandbox Lua; ban nondeterministic APIs. | high | 4 | INFERENCE |
| CONSTRAINT-24 | Launcher must not duplicate/simulate engine state | project architecture | soft/hard | Assistant design. | Launcher reads metadata and launches runtime. | medium | 4 | INFERENCE |
| CONSTRAINT-25 | Tools must reuse engine IO, not reimplement formats | project architecture | soft/hard | Assistant design. | Avoid parser drift. | medium | 4 | INFERENCE |
| CONSTRAINT-26 | Fixed simulation tick and deterministic order | determinism | hard-ish | Assistant design. | System and entity order stable. | high | 4 | INFERENCE |
| CONSTRAINT-27 | All randomness explicit and saved or stateless-coordinate | determinism | hard-ish | Assistant design. | No load-order RNG effects. | high | 4 | INFERENCE |
| CONSTRAINT-28 | Report/package must be chat-specific only | reporting | hard | Current user request. | Do not summarize whole project beyond this chat scope. | medium | 5 | FACT |
| CONSTRAINT-29 | Important items must be labelled FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT | reporting | hard | Current user request. | Use labels in final package. | medium | 5 | FACT |

### Open Questions Register
| ID | Question | Why it matters | Known | Unknown | Resolution | Priority | Workstreams | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | How exactly to implement C89-compatible fixed-width and 64-bit types? | Core needs 64-bit IDs/RNG/accumulators but strict C89 lacks standard types. | User requires C89 and 64-bit-like IDs were recommended. | Compiler targets and allowed extensions unknown. | Define portability header after repo/compiler inspection. | critical | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | Should SimPos X/Y local use unsigned UQ16.16 or signed centered Q16.16? | Determines core coordinate representation and wrap math. | Segment+Q16.16 final; signed prior prompt invalid. | User has not explicitly chosen unsigned vs centered. | Recommend unsigned local X/Y; user/Codex confirm. | critical | WORKSTREAM-01, WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | How are exact Z bounds encoded? | Z Page is [-2048,+2048), but fixed conversion/Chunk gz mapping needs exact convention. | One Page and 256 chunks known. | Inclusive/exclusive edges and out-of-range behavior. | Write/address tests. | high | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | What fixed-point scales should be used for pressure, mass, energy, temperature, density? | Fluid/network systems need deterministic integer units. | No floats in core; physical properties needed. | Units and scaling unknown. | Create numeric units spec before solvers. | medium | WORKSTREAM-02, WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | What endian, padding, and alignment policy should save files use? | Binary compatibility depends on it. | TLV format chosen. | Exact canonical byte order undefined. | Define little-endian packed writer/reader likely. | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | Should save files compress chunk blobs? | Storage/performance tradeoff. | Sparse saves planned. | Compression algorithm not chosen. | Prototype or defer to later. | medium | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | What exact directory path names should be final? | Future aggregation/tools need stable paths. | High address bits should be in names; cosmic IDs final. | Region naming and widths need correction. | Define path grammar in DATA_FORMATS.md. | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | What chunk cache sample resolution is final? | Memory/performance for terrain caches. | Assistant recommended 32³ per 16m chunk. | User did not explicitly confirm. | Prototype/profile; start 32³ tentatively. | medium | WORKSTREAM-04, WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-09 | What allocator/hash-table strategy should core use? | C89 core needs deterministic memory behavior. | Sparse chunk table planned. | Allocator design unknown. | Implement simple fixed/open-addressed structures first. | medium | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | Which meshing algorithm starts v0? | Affects smooth terrain and implementation complexity. | Marching cubes/dual contouring discussed. | No final choice. | Pick simplest debug mesher first or choose MC/DC. | medium | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-11 | How is φ represented/scaled in fixed-point? | All geometry sampling and meshing depend on field scale. | φ signed field chosen. | Scaling/saturation unknown. | Define φ fixed range and units. | high | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-12 | What weather solver and grid resolution? | Climate/weather performance and determinism. | Coarse grid approach chosen. | Exact cell size/layers/formula unknown. | Design v1 solver spec. | medium | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-13 | What hydrology model and resolution? | Rivers/flooding/lakes depend on it. | Basins/graphs/heightfields chosen. | Equations/resolution unknown. | Design hydrology spec. | medium | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-14 | How to decide FluidSpace membership for rooms/tanks/caves? | Medium sampling and flooding need point-to-space mapping. | FluidSpaces as geometric/topological domains chosen. | Exact geometry/BVH/priority rules unknown. | Define containment and tie-break rules. | medium | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-15 | What pressure/rupture equations and thresholds? | Oil/gas/tank rupture gameplay depends on it. | Rupture as connector event chosen. | Formula/units not specified. | Design structural component model. | medium | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| QUESTION-16 | How to model multi-phase oil/water/gas mixtures? | Reservoirs/flooding may mix fluids. | FluidSpaces support mass by species conceptually. | Composition rules unknown. | Define species/material registry and mixing rules. | medium | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| QUESTION-17 | What electrical/hydraulic/thermal network solver formulas? | Network correctness/performance. | Graph-based networks chosen. | Solver math unresolved. | Pick simple deterministic solvers. | medium | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| QUESTION-18 | What exact content pack manifest schema? | Mod/content loading and content.lock need it. | Registries/content.lock chosen. | Schema not written. | Write minimal JSON schema. | high | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| QUESTION-19 | Which Lua version and sandbox implementation? | Deterministic mod scripts depend on it. | Deterministic sandbox required if Lua used. | Lua dependency/API unknown. | Choose after platform goals. | medium | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| QUESTION-20 | What existing repo/build system exists? | Implementation prompt must not blindly overwrite. | No repo files inspected. | Repo state unknown. | Inspect repo first. | critical | WORKSTREAM-10, WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| QUESTION-21 | What platforms/compilers are targeted? | C89/C++98 and 64-bit portability depend on this. | C89/C++98 desired. | Exact compilers unknown. | User/repo should define targets. | high | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| QUESTION-22 | Should Codex implement all at once or staged prompts? | Large prompt may be too broad. | User wanted Codex best, no order preference. | Practical repo state unknown. | Recommend staged prompts after repo inspection. | high | WORKSTREAM-11 | INFERENCE |
| QUESTION-23 | What canonical state hash includes/excludes? | Determinism tests need exact hash inputs. | Need save/load/streaming tests. | Hash schema unknown. | Define canonical serialization/hash. | high | WORKSTREAM-12 | UNCERTAIN / UNVERIFIED |

### Artifact Ledger
| ID | Artifact | Type | Purpose | Status | Origin | Carry forward | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-01 | Previous Codex 5.1 max optimized implementation prompt | prompt | Implement/refactor repo architecture | produced but defective; must repair | Assistant response in this chat | yes | Contains useful layout but critical fixed-point/C89 errors. | FACT |
| ARTIFACT-02 | Scale hierarchy and coordinate decisions | design output | Spatial core reference | established | Visible chat discussion | yes | Final scale names from Plank to Surface. | FACT |
| ARTIFACT-03 | Save hierarchy design | design output | Persistence architecture | established conceptually | Visible chat discussion | yes | Needs exact binary format. | FACT |
| ARTIFACT-04 | TLV chunk section concept | format design | Future-proof save sections | established conceptually | Visible chat discussion | yes | Types 1–6 proposed; mod range >=1000 proposed. | INFERENCE |
| ARTIFACT-05 | Working memory model | design output | Runtime architecture | established conceptually | Visible chat discussion | yes | Chunks as caches; sparse vertical chunks. | FACT |
| ARTIFACT-06 | Fixed-point/C89 core plan | design output | Engine implementation basis | established but needs correction | Visible chat discussion | yes | C89/unsigned corrections required. | FACT |
| ARTIFACT-07 | Universe/galaxy/system/planet addressing plan | design output | Cosmic save addressing | established | Visible chat discussion | yes | 8/24/16 bit IDs. | FACT |
| ARTIFACT-08 | Continuous terrain/material/media field model | design output | Terrain/media architecture | established | Visible chat discussion | yes | φ + material/phase fields, no blocks as matter. | FACT |
| ARTIFACT-09 | FluidSpace/Connector climate/hydrology model | design output | Unified fluids/weather/interiors | established conceptually | Visible chat discussion | yes | Solver details pending. | INFERENCE |
| ARTIFACT-10 | Oil/gas/rupture/flooding design | design output | Reservoir and flooding support | established conceptually | Final assistant answer before CTP package request | yes | Use FluidSpaces, hydraulic nets, structural rupture. | INFERENCE |
| ARTIFACT-11 | Network systems scope model | design output | Pipes/cables/heat/electric/logic architecture | established conceptually | Visible chat discussion | yes | Graph systems, not full EM/CFD. | INFERENCE |
| ARTIFACT-12 | Mod/content lock and deterministic Lua design | design output | Content/modding architecture | established conceptually | Visible chat discussion | yes | Schemas pending. | INFERENCE |
| ARTIFACT-13 | Whole-project repo layering plan | design output | Project architecture | established conceptually | Visible chat discussion | yes | Actual repo unknown. | INFERENCE |
| ARTIFACT-14 | Determinism/seam testing plan | test plan | Prevent streaming/seam bugs | established conceptually | Visible chat discussion | yes | Needs implementation. | INFERENCE |
| ARTIFACT-15 | Original maximum-fidelity Context Transfer Packet | handoff text | State transfer to future chat | produced | Assistant response in visible chat | yes | Used as source for this package; included corrections. | FACT |
| ARTIFACT-16 | Dominium_World_Architecture__01_full_chat_report.md | generated file | Main human-readable report | created now | This response | yes | Downloadable file. | FACT |
| ARTIFACT-17 | Dominium_World_Architecture__02_spec_sheet.yaml | generated file | Structured YAML for aggregation/spec book | created now | This response | yes | Downloadable file. | FACT |
| ARTIFACT-18 | Dominium_World_Architecture__03_aggregator_packet.md | generated file | Compact merge packet | created now | This response | yes | Downloadable file. | FACT |
| ARTIFACT-19 | Dominium_World_Architecture__04_registers.md | generated file | Standalone normalized registers | created now | This response | yes | Downloadable file. | FACT |
| ARTIFACT-20 | Dominium_World_Architecture__05_reader_brief.md | generated file | Short human brief | created now | This response | yes | Downloadable file. | FACT |
| ARTIFACT-21 | Dominium_World_Architecture__06_verification_and_audit.md | generated file | Audit/reliability record | created now | This response | yes | Downloadable file. | FACT |
| ARTIFACT-22 | Dominium_World_Architecture__manifest.md | generated file | Package manifest | created now | This response | yes | Downloadable file. | FACT |
| ARTIFACT-23 | Dominium_World_Architecture__handoff_package.zip | generated archive | Bundle of all package files | created now | This response | yes | Downloadable archive. | FACT |

### Risk Register
| ID | Risk | Consequence | Likelihood | Severity | Mitigation | Workstreams | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Signed Q16.16 local X/Y bug | Cannot represent [0,65536); overflow/seams/corruption | medium | critical | Use unsigned UQ16.16 or centred signed scheme | WORKSTREAM-01, WORKSTREAM-11 | FACT |
| RISK-02 | Signed Q4.12 save-local bug | Cannot represent full 16m chunk range | medium | critical | Use unsigned UQ4.12 | WORKSTREAM-02, WORKSTREAM-11 | FACT |
| RISK-03 | Region bit-width inconsistency | Wrong directory/file address decomposition | medium | high | Correct Region-in-Segment to 8 bits | WORKSTREAM-01, WORKSTREAM-03 | FACT |
| RISK-04 | C89 incompatibility in implementation prompt | Code may fail target constraints | high | high | Use C89-style portability layer; avoid C99 constructs | WORKSTREAM-02, WORKSTREAM-11 | FACT |
| RISK-05 | 64-bit IDs in strict C89 unresolved | Portability failure or undefined type choices | medium | high | Document compiler extension/typedef strategy | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| RISK-06 | Saving caches as authoritative state | Reload divergences and bloated saves | medium | high | Only save deltas/dynamic state; mark caches disposable | WORKSTREAM-03, WORKSTREAM-04 | INFERENCE |
| RISK-07 | Too many files or poor save locality | Poor IO performance | medium | medium | Use Region files containing many chunks; sparse directories | WORKSTREAM-03 | INFERENCE |
| RISK-08 | Content/mod ID mismatch | World loads with wrong materials/recipes | medium | high | Strict content.lock and migrations | WORKSTREAM-03, WORKSTREAM-09 | INFERENCE |
| RISK-09 | Chunk streaming changes simulation | Non-deterministic gameplay and seams | medium | critical | Chunks are caches only; global/topological state | WORKSTREAM-04 | FACT |
| RISK-10 | Boundary crossing special cases introduce bugs | Performance spikes or state discontinuities | medium | high | O(1) wrap and streaming-independent systems | WORKSTREAM-04 | INFERENCE |
| RISK-11 | Terrain mesh seams | Visible cracks/collision gaps at chunk/region edges | medium | high | Sample φ at global coordinates with boundary overlap | WORKSTREAM-05 | INFERENCE |
| RISK-12 | Material/media queries become overcoupled | Hard to mod/extend systems | medium | medium | Use registries and WorldServices | WORKSTREAM-05, WORKSTREAM-09 | INFERENCE |
| RISK-13 | Fluid/weather scope explosion | Core becomes unbuildable multiphysics engine | medium | high | Use compartments/graphs/coarse grids; defer full physics | WORKSTREAM-06 | INFERENCE |
| RISK-14 | Fixed-point fluid solver instability | Bad pressures/flows/flooding | medium | high | Pick simple clamped formulas and tests | WORKSTREAM-06, WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| RISK-15 | Rupture model creates nondeterministic topology changes | Different clients diverge | low/medium | high | Threshold deterministic events; stable ordering | WORKSTREAM-07 | INFERENCE |
| RISK-16 | Oil/gas mixture complexity overwhelms v1 | Implementation delay | medium | medium | Start with simple species mass vectors | WORKSTREAM-07 | INFERENCE |
| RISK-17 | Network solvers become too realistic/slow | Performance and complexity loss | medium | medium | Use graph simplifications; no full EM | WORKSTREAM-08 | INFERENCE |
| RISK-18 | Lua nondeterminism | Cross-machine divergence | medium | high | Sandbox and deterministic APIs | WORKSTREAM-09 | INFERENCE |
| RISK-19 | Mod schemas hardcoded or unstable | Mod ecosystem breaks saves | medium | medium | Versioned manifests and registries | WORKSTREAM-09 | INFERENCE |
| RISK-20 | Repo architecture assumptions wrong | Codex overwrites/misplaces files | medium | high | Inspect repo before changes | WORKSTREAM-10, WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| RISK-21 | Launcher/tools duplicate file parsers | Format drift and bugs | medium | medium | Tools link engine IO | WORKSTREAM-10 | INFERENCE |
| RISK-22 | Previous Codex prompt used without audit | Implementation bakes in known design bugs | medium | critical | Repair prompt first | WORKSTREAM-11 | FACT |
| RISK-23 | No deterministic test harness | Bugs discovered late | medium | high | Add save/load/hash/seam tests early | WORKSTREAM-12 | INFERENCE |
| RISK-24 | Threading breaks determinism | Race/order-dependent state | medium | high | Single-thread sim; async only for pure caches initially | WORKSTREAM-12 | INFERENCE |
| RISK-25 | Report over-compression loses design details | Future assistant repeats questions/mistakes | low | medium | Use full package + registers | WORKSTREAM-13 | FACT |
| RISK-26 | Assistant suggestions mistaken as user decisions | Spec book becomes overconfident | medium | medium | Use labels and source hierarchy | WORKSTREAM-13 | FACT |

### Verification Queue
| ID | Item | Why | Source/type | Priority | Workstreams | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Correct fixed-point signedness | Prior prompt used invalid signed ranges. | Code/spec audit | critical | WORKSTREAM-01, WORKSTREAM-11 | FACT |
| VERIFY-02 | C89 compatibility of code examples | Prior prompt used C99 constructs. | Compiler/build/lint review | critical | WORKSTREAM-02, WORKSTREAM-11 | FACT |
| VERIFY-03 | Region bit decomposition | Earlier output inconsistent about 4-bit vs 8-bit Region index inside Segment. | Math/spec review | critical | WORKSTREAM-01, WORKSTREAM-03 | FACT |
| VERIFY-04 | No float/double in engine/saves | User forbade floats in core/saves. | Static grep/lint/build policy | critical | WORKSTREAM-02 | FACT |
| VERIFY-05 | Endian/padding save format | Binary compatibility not specified. | Spec review | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | Save path grammar | Directory names and bit widths need exact final spec. | Spec review | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | Streaming independence | Chunks should not affect simulation truth. | Automated test | high | WORKSTREAM-04, WORKSTREAM-12 | INFERENCE |
| VERIFY-08 | Untouched chunks not saved | Storage optimization promise needs test. | Save inspection test | medium | WORKSTREAM-04 | INFERENCE |
| VERIFY-09 | φ seam continuity | Adjacent chunks must sample identical fields. | Boundary probe test | high | WORKSTREAM-05, WORKSTREAM-12 | INFERENCE |
| VERIFY-10 | Material/media query determinism | Field and material providers must be deterministic. | Hash/probe test | medium | WORKSTREAM-05 | INFERENCE |
| VERIFY-11 | FluidSpace solver determinism | Compartment/weather/hydro states must match across runs. | Sim hash test | medium | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-12 | Weather/hydrology resolution performance | Grid sizes were only recommended, not confirmed. | Prototype/profile | medium | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-13 | Pressure/rupture formulas | Oil/tank/flood systems need stable equations. | Design/prototype | medium | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| VERIFY-14 | Network global-state storage | Networks must not be chunk-authoritative. | Save/load test | medium | WORKSTREAM-08 | INFERENCE |
| VERIFY-15 | content.lock determinism | Registry IDs must match across machines/content order. | Content loader test | high | WORKSTREAM-09 | INFERENCE |
| VERIFY-16 | Actual repo structure | No repo files were inspected in chat. | Repo inspection | critical | WORKSTREAM-10, WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| VERIFY-17 | Build system/toolchain targets | C89/C++98 portability depends on target compilers. | Repo/user verification | high | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| VERIFY-18 | Saved rotations are 8-bit | Prior prompt made this optional despite user statement. | Spec audit/user confirmation if exceptions desired | high | WORKSTREAM-11 | FACT |
| VERIFY-19 | Canonical state hash definition | Tests need exact included fields. | Test design | high | WORKSTREAM-12 | UNCERTAIN / UNVERIFIED |
| VERIFY-20 | Package completeness | Current generated package should be checked by user before aggregation. | Manual review | medium | WORKSTREAM-13 | FACT |

## 6. Possible Cross-Chat Duplicates

Likely duplicate topics: Dominium engine architecture, ECS, save format, world generation, modding/content packs, launcher/tools, deterministic simulation, hydrology/weather, and Codex implementation plans.

## 7. Possible Cross-Chat Conflicts

Watch for other chats changing world size, precision, saved rotations, cosmic ID counts, use of floats, language constraints, surface-instance persistence, or treating chunks as authorities.

## 8. Spec Book Integration Guidance

This chat should feed chapters on world model, coordinates, fixed-point core, save format, runtime memory, fields/media, environmental systems, networks, modding, repo architecture, and testing. Formalize only direct user decisions and widely accepted design principles; keep solver formulas and repo structure as pending until verified.

## 9. Aggregator Warnings

Do not merge assistant suggestions as user decisions without labels. Do not use the previous Codex prompt without repair. Do not overlook the signed fixed-point and Region-bit corrections. Do not assume repo state or compiler targets.
