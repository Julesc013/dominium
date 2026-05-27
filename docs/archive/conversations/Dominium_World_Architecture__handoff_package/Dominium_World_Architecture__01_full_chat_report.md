# Full Chat Report — Dominium World Architecture

## 0. Report Metadata

| Field | Value |
|---|---|
| Chat label | Dominium World Architecture |
| Generated date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | THIS CHAT ONLY, including the previously generated Context Transfer Packet visible in this chat. |
| Apparent coverage | Full visible-chat coverage, with caveats because no repository files were inspected. |
| Extraction confidence | 4/5 |
| Staleness risk | Low for internal design decisions; medium for any future software/toolchain/API assumptions. |
| Future plans present | Yes |
| Pending tasks present | Yes |
| Artifacts/files present | Yes: prior prompt artifact and this generated package. No repo files were modified in the visible chat. |
| Safe for aggregation | Yes, with caveats. |
| Main limitations | Actual git repo unknown; previous Codex prompt contains known defects; many solver formulas remain unresolved; some assistant recommendations are not explicit user decisions. |

## 1. Executive Summary

This chat was a sustained architecture-design session for the **Dominium World Architecture** workstream. It defined how a future Dominium-style game world should represent space, terrain, saves, runtime memory, deterministic simulation, environmental systems, tools, mods, and a Codex implementation plan. The most important output is not a single feature spec but a coherent design philosophy: all authoritative simulation state should live in deterministic, fixed-point, content-agnostic core structures, while chunks/segments are storage and cache boundaries only.

The final spatial model is a power-of-two hierarchy with named scales from Plank through Surface. The horizontal surface is a toroidal 2^24 metre grid in X/Y, with X east and Y north. Z is not toroidal; the user confirmed one Page of vertical space, 4096 m total, centered at sea level, meaning roughly 2 km down and 2 km up. Chunk size is 16×16×16 m, giving 256 vertical chunk layers. Runtime positions use an 8-bit Segment index plus local Q16.16 precision; save positions use Q4.12 local-to-chunk. The packet identifies a critical correction to the prior Codex prompt: signed Q16.16 cannot represent the full local segment range [0,65536), and signed Q4.12 cannot represent the full chunk-local range [0,16). Future work should use unsigned local fixed types or an explicitly centered signed coordinate scheme.

The user imposed hard implementation constraints: no floats in the core or save files; C89 for the core; C++98 and floats allowed only in platform/renderer/runtime layers, with no feedback into core state. This creates another unresolved engineering issue: strict ISO C89 lacks standard fixed-width and 64-bit integer types, while the architecture needs 64-bit IDs, RNG state, and fixed-point accumulators. A portability layer or a documented “C89-style plus compiler 64-bit extension” policy is required before coding.

The terrain model converged on continuous signed geometry `φ`, not block matter. Chunks sample `φ` for meshing/collision but never own truth. Ground and air are abstract media, not blocks. Materials, phases, pressure, density, hardness, temperature, and composition are represented through registries, fields, SpatialVolumes, FluidSpaces, and solver modules. Full per-material 3D density fields were rejected as storage-expensive and conceptually wrong.

Environmental systems were unified under reusable patterns. FluidSpaces and Connectors model air, vapour, liquids, tanks, rooms, atmosphere, hydrology, reservoirs, rivers, and flooding. SpatialVolumes model caves, ore pockets, gas pockets, voids, basins, magma chambers, oil reservoirs, and local field effects. Networks model pipes, hydraulic flow, electrical power, heat, and logic, while full global CFD, EM simulation, FEA, and broad chemistry were explicitly scoped out. Oil fields, gas pressure, tank ruptures, and mineshaft flooding were mapped onto the same FluidSpace/Connector/HydraulicNet/SpatialVolume design.

The save model is sparse and deterministic. Procedural defaults are regenerated from content, recipes, and seeds; saves store only deltas and dynamic state. The cosmic hierarchy is 2^8 galaxies per universe, 2^24 systems per galaxy, and 2^16 planets per system. Internally arbitrary surface instances may exist later, but saves currently store one canonical surface per planet. Save files use directory names for high address bits and TLV chunk sections for extensibility. `content.lock` fixes content packs, versions, hashes, and deterministic registry order. Unknown TLV sections can be skipped; migrations should be explicit.

A major artifact was a Codex 5.1 implementation prompt, but it must not be used unchanged. It is useful structurally, but contains known bugs around signed fixed-point, Region bit widths, C89 syntax, and saved rotation ambiguity. The best next action is to revise that prompt and inspect the actual repository before code generation.

## 2. How to Use This Report

This report covers only this old chat. It should not be treated as a complete Project Spec Book. Items labelled **FACT** were explicitly stated in the chat or directly requested by the user. Items labelled **INFERENCE** are reasonably inferred from the chat, often because the assistant proposed a design and the user continued building on it. Items labelled **UNCERTAIN / UNVERIFIED** are unresolved, unsupported, stale, or require repo/toolchain verification. Items labelled **PROJECT-CONTEXT** would come from project-level context outside the visible transcript; this package uses minimal project-context only for the project name where noted.

Direct user statements outrank assistant suggestions. Later user statements outrank earlier suggestions. Tentative designs remain tentative. Stale external facts, software APIs, compiler capabilities, or platform assumptions require verification before implementation. This report is intended to feed a later master-spec aggregation process; do not merge it with other chat reports until contradictions and duplicates are explicitly reviewed.

## 3. User Preferences Visible in This Chat

### 3.1 Explicit Preferences

| ID | Preference | Source type | Source basis | Strength | Implication | Risk if misunderstood | Label |
|---|---|---|---|---|---|---|---|
| PREFERENCE-01 | Direct, dense, technical answers | explicit | User profile/instructions | strong | Avoid filler and soft asks | Loss of trust/efficiency | FACT |
| PREFERENCE-02 | Rigor, second/third-order thinking, unbiased facts | explicit | User profile | strong | Preserve tradeoffs, risks, rejected options | Overconfident simplification | FACT |
| PREFERENCE-03 | Start messages with model version and build date | explicit | User instruction | strong | Include version line when responding | Style mismatch | FACT |
| PREFERENCE-04 | Preserve uncertainty and source labels | explicit | Current request | strong | Use FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT | False certainty in future spec | FACT |
| PREFERENCE-05 | Do not make user re-explain decisions | explicit | Context packet/final package requests | strong | Carry detailed handoff forward | Repeated work | FACT |
| PREFERENCE-06 | Architecture should be future-proof/modular/extensible | explicit | Repeated user requests | strong | Design stable interfaces and versioning | Short-term hacks | FACT |
| PREFERENCE-07 | Codex should do implementation best, not necessarily in user-specified order | explicit | User: does not care order, wants it done by Codex best | medium | Allow staged plan and expert sequencing | Overfitting to chronological order | FACT |
| PREFERENCE-08 | Implementation should be optimized and detailed with forward planning | explicit | User asked for maximum optimized detail | strong | Provide exact modules and constraints | Under-specified code prompt | FACT |
| PREFERENCE-09 | Avoid treating brainstorms as final decisions | explicit | Current request | strong | Separate assistant suggestions from user acceptance | Spec pollution | FACT |

### 3.2 Inferred Preferences

No separate inferred preferences were necessary beyond the explicit preferences above; however, several design preferences can be inferred from repeated user requests: architecture-first planning, deterministic core implementation, modular extensibility, and high-fidelity handoff preservation.

### 3.3 Preferences Not Established by This Chat

| Preference area | Status |
|---|---|
| Preferred build system | UNCERTAIN / UNVERIFIED |
| Exact compiler/platform targets | UNCERTAIN / UNVERIFIED |
| Exact visual style or renderer API | UNCERTAIN / UNVERIFIED |
| Exact Lua version or scripting dependency | UNCERTAIN / UNVERIFIED |
| Exact desired implementation order beyond “Codex best” | UNCERTAIN / UNVERIFIED |

## 4. Complete Topic and Workstream Inventory

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | Spatial coordinate model and scale hierarchy | Define the world’s spatial scale, axes, wrap behavior, chunk hierarchy, and origin convention. | User-confirmed toroidal horizontal SurfaceGrid of 2^24 m per axis, one vertical Page of 4096 m, 16 m cubic chunks, and final scale names from Plank to Surface. | A deterministic coordinate implementation with safe fixed-point conversion across Segment, Region, Chunk, Block, and local coordinates. | active | critical | 5 | FACT |
| WORKSTREAM-02 | Deterministic fixed-point C89 core | Build the core simulation library using deterministic fixed-point arithmetic with no floats in core or saves. | Design established; implementation prompt produced but needs correction for C89 and fixed-point signedness. | A C89-style core library with fixed-point math, RNG, ECS, world services, save/load, and no float/double usage. | active | critical | 5 | FACT |
| WORKSTREAM-03 | Sparse save file architecture | Persist only dynamic state and procedural deltas using a hierarchical universe save and TLV region/chunk files. | Architecture designed; exact binary details remain pending. | Versioned, sparse, deterministic save files with content.lock, metadata, Region files, Chunk TLVs, global environment/network files, and migration support. | active | critical | 4 | FACT |
| WORKSTREAM-04 | Runtime memory model, chunking, streaming, and continuity | Keep active memory sparse and deterministic while chunks/segments never alter simulation truth. | Design conclusion: chunks are caches; state lives in global/topological systems. | Sparse SurfaceRuntime/ChunkRuntime with lazy terrain caches, vertical chunk bitsets, async mesh/IO later, and deterministic streaming-independent results. | active | high | 5 | FACT |
| WORKSTREAM-05 | Continuous terrain, geometry, materials, and media | Represent smooth arbitrary terrain and abstract materials with continuous fields rather than block matter. | Core model established: geometry φ + material/media/phase fields + sampled chunk meshes. | A field-provider-based terrain/material system supporting caves, cliffs, volcanoes, floating solids, voids, and arbitrary sub-meter geometry. | active | high | 5 | FACT |
| WORKSTREAM-06 | FluidSpaces, hydrology, weather, climate, rooms, tanks | Unify liquids, gases, vapours, weather, climate, rooms, tanks, basins, rivers, and atmosphere through FluidSpaces and Connectors. | Architecture designed; solvers not nailed down. | Deterministic fixed-point fluid/environment systems with global atmosphere/hydrology and local enclosed compartment support. | active | medium | 4 | FACT |
| WORKSTREAM-07 | Oil fields, gas pockets, pressure, ruptures, flooding, rivers | Use the fluid/network/volume model to support oil reservoirs, gas pockets, pressure, ruptures, mineshaft flooding, river flow, tank rupture, and flooding. | Design mapped onto existing primitives; implementation not started. | Reservoirs and floods are deterministic state transitions and flows through FluidSpaces, Connectors, Hydrology, and HydraulicNet. | active | medium | 4 | FACT |
| WORKSTREAM-08 | Thermal, hydraulic, electrical, logic, and limited EM systems | Apply Spaces/Connectors/Networks pattern to routed systems while avoiding full multiphysics simulation. | Scope boundaries and graph abstraction established. | Separate deterministic graph/network modules for hydraulic, electrical, logic, and thermal systems, linked to world objects and saved globally. | active | medium | 4 | FACT |
| WORKSTREAM-09 | Mod/content system, registries, JSON/Lua, content.lock | Make official and modded content use deterministic registries and content packs without core hardcoding. | Design established; schemas and sandbox implementation pending. | Content packs and mods define materials/recipes/fields/solvers through JSON/Lua; core loads deterministic registries from content.lock. | active | high | 4 | FACT |
| WORKSTREAM-10 | Whole-project modular architecture: engine, runtime, launcher, tools, mods | Extend the deterministic modular philosophy to the entire repo and toolchain. | Directory/layering design proposed; actual repo not inspected. | Engine static library, C++98 runtimes, metadata-only launcher, tools reusing engine IO, content/mod SDK, versioned migrations. | active | high | 3 | FACT |
| WORKSTREAM-11 | Codex implementation prompt and code generation plan | Produce a Codex-ready prompt to implement/refactor repo according to the architecture. | A long prompt was generated but is known defective in fixed-point/C89 details and must be revised. | A corrected, repo-aware Codex prompt or set of smaller implementation prompts. | active | critical | 5 | FACT |
| WORKSTREAM-12 | Testing, verification, determinism, seam validation | Ensure world state is deterministic, seamless, and independent of chunk streaming. | Test strategy described; no tests created in chat. | Automated tests for save/load hash equivalence, streaming-order independence, seam continuity, and network continuity. | active | high | 4 | FACT |
| WORKSTREAM-13 | Documentation, reports, and future Project Spec Book | Preserve design state and create documents usable for future implementation and aggregation. | Context Transfer Packet created; this package now exports normalized report files. | Markdown/YAML report package plus repo docs that feed into a future full Project Spec Book. | active | high | 5 | FACT |

## 5. Detailed Workstream State


### WORKSTREAM-01 — Spatial coordinate model and scale hierarchy

- Label: FACT
- Objective: Define the world’s spatial scale, axes, wrap behavior, chunk hierarchy, and origin convention.
- Background: The conversation began with 1 m cubes, subchunks/chunks/regions, then converged on a power-of-two scale hierarchy.
- Current state: User-confirmed toroidal horizontal SurfaceGrid of 2^24 m per axis, one vertical Page of 4096 m, 16 m cubic chunks, and final scale names from Plank to Surface.
- Desired end state: A deterministic coordinate implementation with safe fixed-point conversion across Segment, Region, Chunk, Block, and local coordinates.
- Importance: critical
- Decisions made: DECISION-01, DECISION-02, DECISION-03, DECISION-08, DECISION-17
- Decisions pending: QUESTION-01, QUESTION-02, QUESTION-03
- Pending tasks: TASK-01, TASK-02, TASK-03
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-04, CONSTRAINT-05, CONSTRAINT-06
- Dependencies: Fixed-point type definitions, C89 portability layer, Save directory bit layout
- Timeline / sequencing: Early/core substrate before geometry, save, or systems.
- Blockers: Signedness and C89 portability contradictions from earlier prompt need repair.
- Risks: RISK-01, RISK-02, RISK-03
- Artifacts: ARTIFACT-01, ARTIFACT-02
- Success criteria: Exact wrap at 2^24 m with no seam bugs, Z bounded to [-2048,+2048), Block/chunk/region conversion round-trips exactly
- Recommended next action: Correct fixed-point types and write addressing conversion tests.
- Verification needed: VERIFY-01, VERIFY-02, VERIFY-03
- Confidence: 5/5
- Carry-forward priority: critical


### WORKSTREAM-02 — Deterministic fixed-point C89 core

- Label: FACT
- Objective: Build the core simulation library using deterministic fixed-point arithmetic with no floats in core or saves.
- Background: User explicitly required runtime Q16.16, save Q4.12, no floats in core/saves, C89 core, C++98 platform/renderer.
- Current state: Design established; implementation prompt produced but needs correction for C89 and fixed-point signedness.
- Desired end state: A C89-style core library with fixed-point math, RNG, ECS, world services, save/load, and no float/double usage.
- Importance: critical
- Decisions made: DECISION-04, DECISION-05, DECISION-06, DECISION-07
- Decisions pending: QUESTION-01, QUESTION-04
- Pending tasks: TASK-01, TASK-04, TASK-05, TASK-10
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-03, CONSTRAINT-07
- Dependencies: Compiler support for 64-bit ints, Portable typedef policy, Unit scaling per physical quantity
- Timeline / sequencing: First implementation layer.
- Blockers: Strict ISO C89 lacks standard fixed-width integers and inline functions.
- Risks: RISK-02, RISK-04, RISK-05
- Artifacts: ARTIFACT-01, ARTIFACT-06
- Success criteria: Core builds as a library, No float/double symbols in engine source, Determinism tests pass
- Recommended next action: Define portability header and fixed-point API before other modules.
- Verification needed: VERIFY-02, VERIFY-04
- Confidence: 5/5
- Carry-forward priority: critical


### WORKSTREAM-03 — Sparse save file architecture

- Label: FACT
- Objective: Persist only dynamic state and procedural deltas using a hierarchical universe save and TLV region/chunk files.
- Background: User wanted directory names to encode address bits efficiently and saves to handle sparse/dense worlds.
- Current state: Architecture designed; exact binary details remain pending.
- Desired end state: Versioned, sparse, deterministic save files with content.lock, metadata, Region files, Chunk TLVs, global environment/network files, and migration support.
- Importance: critical
- Decisions made: DECISION-09, DECISION-10, DECISION-11, DECISION-12, DECISION-13, DECISION-14
- Decisions pending: QUESTION-05, QUESTION-06, QUESTION-07
- Pending tasks: TASK-06, TASK-07, TASK-11
- Constraints: CONSTRAINT-08, CONSTRAINT-09, CONSTRAINT-10, CONSTRAINT-12, CONSTRAINT-17
- Dependencies: World address mapping, Content registry IDs, Endian/alignment policy
- Timeline / sequencing: Core v0; before durable saves.
- Blockers: No exact file format structs verified against repo/build system.
- Risks: RISK-06, RISK-07, RISK-08
- Artifacts: ARTIFACT-03, ARTIFACT-04, ARTIFACT-07
- Success criteria: Save/load round-trip exact, Unknown TLV sections skipped safely, Procedural-only chunks not saved
- Recommended next action: Write DATA_FORMATS.md and implement TLV reader/writer.
- Verification needed: VERIFY-05, VERIFY-06
- Confidence: 4/5
- Carry-forward priority: critical


### WORKSTREAM-04 — Runtime memory model, chunking, streaming, and continuity

- Label: FACT
- Objective: Keep active memory sparse and deterministic while chunks/segments never alter simulation truth.
- Background: User asked how to avoid loading/saving untouched vertical chunks and whether chunk/page/segment crossings cost performance.
- Current state: Design conclusion: chunks are caches; state lives in global/topological systems.
- Desired end state: Sparse SurfaceRuntime/ChunkRuntime with lazy terrain caches, vertical chunk bitsets, async mesh/IO later, and deterministic streaming-independent results.
- Importance: high
- Decisions made: DECISION-15, DECISION-16, DECISION-18
- Decisions pending: QUESTION-08, QUESTION-09
- Pending tasks: TASK-08, TASK-09, TASK-15
- Constraints: CONSTRAINT-11, CONSTRAINT-13, CONSTRAINT-14
- Dependencies: Address conversions, SurfaceRuntime data structure, Chunk state machine
- Timeline / sequencing: Core v0 with more optimization over time.
- Blockers: Exact hash table/allocator/job system not defined.
- Risks: RISK-09, RISK-10
- Artifacts: ARTIFACT-02, ARTIFACT-05
- Success criteria: Streaming path does not alter world hash, Untouched chunks not saved, Procedural chunks evict cleanly
- Recommended next action: Implement sparse chunk table and seam tests.
- Verification needed: VERIFY-07, VERIFY-08
- Confidence: 5/5
- Carry-forward priority: high


### WORKSTREAM-05 — Continuous terrain, geometry, materials, and media

- Label: FACT
- Objective: Represent smooth arbitrary terrain and abstract materials with continuous fields rather than block matter.
- Background: User asked how smooth triangle terrain works with cubic grid and later stated ground/air are not blocks.
- Current state: Core model established: geometry φ + material/media/phase fields + sampled chunk meshes.
- Desired end state: A field-provider-based terrain/material system supporting caves, cliffs, volcanoes, floating solids, voids, and arbitrary sub-meter geometry.
- Importance: high
- Decisions made: DECISION-19, DECISION-20, DECISION-21, DECISION-22
- Decisions pending: QUESTION-10, QUESTION-11
- Pending tasks: TASK-12, TASK-16, TASK-20
- Constraints: CONSTRAINT-15, CONSTRAINT-16
- Dependencies: Material registry, Field providers, Chunk meshing
- Timeline / sequencing: Basic heightfield/φ in v0; advanced media/volumes later.
- Blockers: Exact φ scaling and meshing algorithm unresolved.
- Risks: RISK-11, RISK-12
- Artifacts: ARTIFACT-08
- Success criteria: Adjacent chunks sample identical φ at shared coordinates, Material/media queries deterministic and chunk-independent
- Recommended next action: Implement minimal fixed-point φ provider and material registry.
- Verification needed: VERIFY-09, VERIFY-10
- Confidence: 5/5
- Carry-forward priority: high


### WORKSTREAM-06 — FluidSpaces, hydrology, weather, climate, rooms, tanks

- Label: FACT
- Objective: Unify liquids, gases, vapours, weather, climate, rooms, tanks, basins, rivers, and atmosphere through FluidSpaces and Connectors.
- Background: User asked whether climate/weather can work inside rooms/buildings/tanks like water and whether all liquids/gases/climate/weather can use this model.
- Current state: Architecture designed; solvers not nailed down.
- Desired end state: Deterministic fixed-point fluid/environment systems with global atmosphere/hydrology and local enclosed compartment support.
- Importance: medium
- Decisions made: DECISION-23, DECISION-24, DECISION-25
- Decisions pending: QUESTION-12, QUESTION-13, QUESTION-14
- Pending tasks: TASK-17, TASK-18, TASK-21
- Constraints: CONSTRAINT-18, CONSTRAINT-19
- Dependencies: Medium model, Material species registry, Solver formulas, Save global_env/local_env sections
- Timeline / sequencing: Post-v0/v1 system after core substrate.
- Blockers: Equation choices and fixed-point scaling pending.
- Risks: RISK-13, RISK-14
- Artifacts: ARTIFACT-09
- Success criteria: Room/tank/outdoor medium sampling uses same API, Flooding/venting deterministic across chunk boundaries
- Recommended next action: Specify fixed-point FluidSpace state and connector equations.
- Verification needed: VERIFY-11, VERIFY-12
- Confidence: 4/5
- Carry-forward priority: medium


### WORKSTREAM-07 — Oil fields, gas pockets, pressure, ruptures, flooding, rivers

- Label: FACT
- Objective: Use the fluid/network/volume model to support oil reservoirs, gas pockets, pressure, ruptures, mineshaft flooding, river flow, tank rupture, and flooding.
- Background: Final design question asked explicitly about oil fields/pockets/pressure/ruptures/mineshaft flooding/flowing rivers/tank ruptures.
- Current state: Design mapped onto existing primitives; implementation not started.
- Desired end state: Reservoirs and floods are deterministic state transitions and flows through FluidSpaces, Connectors, Hydrology, and HydraulicNet.
- Importance: medium
- Decisions made: DECISION-26, DECISION-27, DECISION-28
- Decisions pending: QUESTION-15, QUESTION-16
- Pending tasks: TASK-22, TASK-23
- Constraints: CONSTRAINT-19, CONSTRAINT-20
- Dependencies: FluidSpaces, Hydraulic networks, Structural component model, Materials for oil/gas/water
- Timeline / sequencing: After FluidSpaces/hydraulic net exists.
- Blockers: Pressure/rupture formulas not specified.
- Risks: RISK-15, RISK-16
- Artifacts: ARTIFACT-10
- Success criteria: Rupture creates deterministic connector, Reservoir pressure changes with mass/volume, Flooding independent of chunk loading
- Recommended next action: Define reservoir FluidSpace schema and rupture event rules.
- Verification needed: VERIFY-13
- Confidence: 4/5
- Carry-forward priority: medium


### WORKSTREAM-08 — Thermal, hydraulic, electrical, logic, and limited EM systems

- Label: FACT
- Objective: Apply Spaces/Connectors/Networks pattern to routed systems while avoiding full multiphysics simulation.
- Background: User asked how to extend philosophy to pipes/cables/heat/electromagnetic systems and where to limit scope.
- Current state: Scope boundaries and graph abstraction established.
- Desired end state: Separate deterministic graph/network modules for hydraulic, electrical, logic, and thermal systems, linked to world objects and saved globally.
- Importance: medium
- Decisions made: DECISION-29, DECISION-30, DECISION-31, DECISION-32
- Decisions pending: QUESTION-17
- Pending tasks: TASK-24
- Constraints: CONSTRAINT-20, CONSTRAINT-21
- Dependencies: Global network save, Node/edge ID system, Solver formulas
- Timeline / sequencing: Post-v0, likely v1/v2 depending on gameplay needs.
- Blockers: Exact network component schema unresolved.
- Risks: RISK-17
- Artifacts: ARTIFACT-11
- Success criteria: Network solve independent of chunk streaming, No full EM/PDE in core
- Recommended next action: Stub network modules and global_networks.bin sections.
- Verification needed: VERIFY-14
- Confidence: 4/5
- Carry-forward priority: medium


### WORKSTREAM-09 — Mod/content system, registries, JSON/Lua, content.lock

- Label: FACT
- Objective: Make official and modded content use deterministic registries and content packs without core hardcoding.
- Background: User asked how to keep deterministic core with separate JSON/Lua definitions and core agnostic to official/modded content.
- Current state: Design established; schemas and sandbox implementation pending.
- Desired end state: Content packs and mods define materials/recipes/fields/solvers through JSON/Lua; core loads deterministic registries from content.lock.
- Importance: high
- Decisions made: DECISION-33, DECISION-34, DECISION-35
- Decisions pending: QUESTION-18, QUESTION-19
- Pending tasks: TASK-13, TASK-14, TASK-25
- Constraints: CONSTRAINT-22, CONSTRAINT-23
- Dependencies: Manifest schema, Registry implementation, Lua sandbox
- Timeline / sequencing: Basic registries needed v0; Lua/plugins can follow later.
- Blockers: Lua version/sandbox not chosen.
- Risks: RISK-18, RISK-19
- Artifacts: ARTIFACT-12
- Success criteria: Same content.lock produces same numeric IDs and world state on all machines
- Recommended next action: Write content manifest and registry spec.
- Verification needed: VERIFY-15
- Confidence: 4/5
- Carry-forward priority: high


### WORKSTREAM-10 — Whole-project modular architecture: engine, runtime, launcher, tools, mods

- Label: FACT
- Objective: Extend the deterministic modular philosophy to the entire repo and toolchain.
- Background: User asked how to extend philosophy to entire project including launcher/game/tools/mods.
- Current state: Directory/layering design proposed; actual repo not inspected.
- Desired end state: Engine static library, C++98 runtimes, metadata-only launcher, tools reusing engine IO, content/mod SDK, versioned migrations.
- Importance: high
- Decisions made: DECISION-36, DECISION-37, DECISION-38
- Decisions pending: QUESTION-20, QUESTION-21
- Pending tasks: TASK-26, TASK-27, TASK-28
- Constraints: CONSTRAINT-24, CONSTRAINT-25
- Dependencies: Actual repo structure, Build system, Target platforms
- Timeline / sequencing: Repo-level planning before broad implementation.
- Blockers: No repository files inspected in chat.
- Risks: RISK-20, RISK-21
- Artifacts: ARTIFACT-13
- Success criteria: Launcher/tools/runtimes share engine APIs and file format code; no duplicate parsers
- Recommended next action: Inspect repo and adapt architecture without blind overwrites.
- Verification needed: VERIFY-16, VERIFY-17
- Confidence: 3/5
- Carry-forward priority: high


### WORKSTREAM-11 — Codex implementation prompt and code generation plan

- Label: FACT
- Objective: Produce a Codex-ready prompt to implement/refactor repo according to the architecture.
- Background: User requested a Codex 5.1 max optimized prompt; assistant generated one.
- Current state: A long prompt was generated but is known defective in fixed-point/C89 details and must be revised.
- Desired end state: A corrected, repo-aware Codex prompt or set of smaller implementation prompts.
- Importance: critical
- Decisions made: DECISION-39
- Decisions pending: QUESTION-22
- Pending tasks: TASK-01, TASK-29
- Constraints: CONSTRAINT-01, CONSTRAINT-03, CONSTRAINT-05
- Dependencies: This report, Repo inspection, Fixed-point corrections
- Timeline / sequencing: Immediate next step if continuing implementation.
- Blockers: Previous prompt contains critical technical bugs.
- Risks: RISK-01, RISK-02, RISK-22
- Artifacts: ARTIFACT-01
- Success criteria: Corrected prompt no longer conflicts with user constraints and implementation can proceed safely
- Recommended next action: Audit/rewrite the Codex prompt using this report.
- Verification needed: VERIFY-01, VERIFY-02, VERIFY-18
- Confidence: 5/5
- Carry-forward priority: critical


### WORKSTREAM-12 — Testing, verification, determinism, seam validation

- Label: FACT
- Objective: Ensure world state is deterministic, seamless, and independent of chunk streaming.
- Background: User asked how to ensure segmentation/chunking patterns do not ruin continuity and determinism.
- Current state: Test strategy described; no tests created in chat.
- Desired end state: Automated tests for save/load hash equivalence, streaming-order independence, seam continuity, and network continuity.
- Importance: high
- Decisions made: DECISION-40, DECISION-41
- Decisions pending: QUESTION-23
- Pending tasks: TASK-10, TASK-30
- Constraints: CONSTRAINT-26, CONSTRAINT-27
- Dependencies: Core implementation, Hash/canonical serialization, Streaming simulation
- Timeline / sequencing: Begin with v0 and expand as systems are added.
- Blockers: No repo/test harness inspected.
- Risks: RISK-23, RISK-24
- Artifacts: ARTIFACT-14
- Success criteria: Same seed/content/input yields identical hashes across save/load and streaming patterns
- Recommended next action: Define canonical world-state hash and seam probe tests.
- Verification needed: VERIFY-19
- Confidence: 4/5
- Carry-forward priority: high


### WORKSTREAM-13 — Documentation, reports, and future Project Spec Book

- Label: FACT
- Objective: Preserve design state and create documents usable for future implementation and aggregation.
- Background: User requested maximum-fidelity state transfer and then a final downloadable report package.
- Current state: Context Transfer Packet created; this package now exports normalized report files.
- Desired end state: Markdown/YAML report package plus repo docs that feed into a future full Project Spec Book.
- Importance: high
- Decisions made: DECISION-42
- Decisions pending: none recorded
- Pending tasks: TASK-31, TASK-32
- Constraints: CONSTRAINT-28, CONSTRAINT-29
- Dependencies: Visible chat context, Previous Context Transfer Packet
- Timeline / sequencing: Current finalization task.
- Blockers: none recorded
- Risks: RISK-25, RISK-26
- Artifacts: ARTIFACT-15, ARTIFACT-16, ARTIFACT-17, ARTIFACT-18, ARTIFACT-19, ARTIFACT-20, ARTIFACT-21
- Success criteria: Files downloadable, self-contained, safe for aggregation with caveats
- Recommended next action: Save ZIP package and use it in a new chat or aggregator later.
- Verification needed: VERIFY-20
- Confidence: 5/5
- Carry-forward priority: high


## 6. Chronological Timeline

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
|---|---|---|---|---|---|
| 1 | Initial grid/fixed-point question | Explored 16/24/32 integer and 8/16/32 fractional bits. | Started coordinate precision design. | Still relevant as rationale. | 5 |
| 2 | Entities/objects storage | Discussed Q24.8 vs offsets/local storage for entities, nodes, splines, vehicles, buildings. | Moved toward hierarchical local storage. | Partly superseded by Q16.16/Q4.12 final. | 4 |
| 3 | Squares vs triangles | Established logic uses cubic grid; renderer uses triangles. | Separated world logic from render mesh. | Still foundational. | 5 |
| 4 | Smooth continuous terrain over cubic grid | Introduced continuous fields and chunk meshing. | Core φ-field idea emerged. | Still foundational. | 5 |
| 5 | Comparison to existing games | Compared Dominium proposal to Satisfactory, Factorio, Minecraft, KSP. | Established hybrid design rationale. | Contextual background only. | 4 |
| 6 | Procedural 3D terrain, arbitrary edits, endpoints/buildings | Introduced chunk-local density, EditOps, endpoints, splines, building surfaces, ramps/stairs. | Expanded object/terrain system. | Still relevant. | 5 |
| 7 | Save hierarchy and universe/galaxy/system/planet | Initial large-scale save/sharding design. | Set context for universe save structure. | Partly superseded by final ID limits. | 4 |
| 8 | Sparse/dense building storage optimization | Segment/Region/Chunk sparse save pattern recommended. | Storage architecture refined. | Still relevant with corrected bit widths. | 4 |
| 9 | Runtime/save precision and storage optimization | User discussed Q16.16 runtime, save precision, rotations; assistant recommended local storage. | Led to final Q16.16/Q4.12 choice. | Partly superseded. | 4 |
| 10 | Scale names finalized | User defined Plank/Point/Step/Sixteenth/Block/Chunk/Region/Page/Segment/Sector/Surface. | Terminology finalized. | Must preserve. | 5 |
| 11 | Cubic chunks and vertical Page | User asked fixed height; assistant recommended cubic chunks and Page height. | Final vertical structure formed. | User later confirmed one Page. | 5 |
| 12 | Sparse vertical chunks | Assistant proposed untouched/procedural/overridden chunk states and sparse vertical maps. | Memory/save optimization established. | Still relevant. | 5 |
| 13 | Final cosmic IDs and canonical surface | User changed to 2^8 galaxies, 2^24 systems, 2^16 planets; one saved canonical surface. | Final address model. | Must preserve. | 5 |
| 14 | Boundary cost/origin | Assistant concluded boundaries cheap, no spawn offset needed, origin is block vertex. | Coordinate conventions settled. | Origin accepted by continuity. | 4 |
| 15 | Variable density/material maps | Discussed physical density, air density, material/phase maps, rejected per-material density fields. | Media model established. | Still relevant. | 5 |
| 16 | Modularity/extensibility improvements | Introduced services, registries, field providers, solvers, TLV sections, plugins. | Architecture matured. | Still relevant. | 5 |
| 17 | Caves/cliffs/waterfalls/volcanoes/aquifers | Mapped features to φ providers, volumes, hydrology, materials. | Demonstrated capability. | Still relevant. | 5 |
| 18 | Deterministic JSON/Lua and content.lock | Content packs, deterministic registries, Lua sandbox introduced. | Modding/determinism architecture established. | Still relevant. | 5 |
| 19 | Gases/vapours/voids/floating masses | Extended media model and SpatialVolumes; dynamic floating masses as objects. | Expanded media/geometry model. | Still relevant. | 4 |
| 20 | Climate/weather inside rooms/tanks | Introduced FluidSpaces and connectors unifying fluids/weather. | Major abstraction added. | Still relevant. | 5 |
| 21 | Pipes/cables/heat/EM | Extended pattern to networks; scoped out full PDE/EM. | Network architecture and limits established. | Still relevant. | 5 |
| 22 | Save integration for systems | Added global_env.bin/global_networks.bin/local TLVs. | Save model expanded. | Still relevant conceptually. | 4 |
| 23 | Implementation/determinism plan | Chunks as caches; global functions; deterministic ticks; staged roadmap. | Implementation principles established. | Still critical. | 5 |
| 24 | Pre-coding items to nail down | Identified scope/numerics/LOD/API/solver/threading/mod/debug/test issues. | Open-question register basis. | Still relevant. | 5 |
| 25 | User final confirmations for 2.x/3.x | User confirmed torus, one Page, Q16.16/Q4.12, no floats core/saves, C89/C++98. | Critical final constraints. | Highest priority. | 5 |
| 26 | Detailed implementation plan and Codex prompt | Assistant produced module layout and Codex prompt. | Useful artifact but flawed. | Must repair. | 5 |
| 27 | Whole-project modular architecture | Applied philosophy to launcher/runtime/tools/mods. | Project-level architecture established. | Repo-specific confirmation needed. | 4 |
| 28 | Oil/pressure/ruptures/flooding | Final substantive system extension. | Reservoir/flooding model integrated. | Still relevant. | 4 |
| 29 | Context Transfer Packet | Assistant produced maximum-fidelity packet with corrections. | State transfer basis. | Used for this package. | 5 |
| 30 | Final report package request | User requested downloadable package files and ZIP. | Current task. | Creates final artifacts. | 5 |

## 7. Decisions

| ID | Decision | Status | Evidence / basis | Rationale | Related workstream | Confidence | Label |
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

### Highest-Impact Decisions

The highest-impact decisions are DECISION-01 through DECISION-08 because they constrain every later implementation choice: toroidal 2^24 m horizontal space, one vertical Page, 16 m chunks, Q16.16 runtime, Q4.12 save-local coordinates, 8-bit Segment addressing, no floats in core/saves, and C++98/floats only outside the core. DECISION-15 is equally important: chunks and segments are caches, not authorities. DECISION-33 through DECISION-35 determine modding and content determinism. DECISION-39 is operationally important because the previously generated Codex prompt must be treated as a draft requiring correction.

## 8. Pending Tasks and Next Actions

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Recommended next step | Related workstream | Label |
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

### 8.1 Recommended Task Order

1. Repair the previous Codex prompt (TASK-01/TASK-29).
2. Inspect the actual repository before overwriting files (TASK-26).
3. Define fixed-point and C89 portability headers (TASK-02/TASK-04).
4. Implement world addressing and tests (TASK-03).
5. Implement TLV save primitives and metadata (TASK-06/TASK-11).
6. Implement SurfaceRuntime/ChunkRuntime and minimal geom_sample (TASK-08/TASK-12).
7. Add deterministic ECS, WorldServices, and test harness (TASK-10/TASK-15/TASK-30).
8. Stub future systems for FluidSpaces, volumes, networks, and content registries.

### 8.2 Blocked Tasks

Solver-heavy tasks are blocked by numeric unit definitions and formula choices. Repo-level restructuring is blocked by actual repo inspection. Lua/mod tasks are blocked by scripting/runtime dependency decisions.

### 8.3 Quick Wins

- Write corrected fixed-point type spec.
- Correct Region bit decomposition in docs.
- Create minimal `DATA_FORMATS.md`.
- Add a grep/lint rule for float/double in engine.
- Turn this package into the bootstrap for the next chat.

### 8.4 Tasks Requiring Verification

TASK-02, TASK-04, TASK-16, TASK-18, TASK-21, TASK-25, TASK-26, and TASK-30 require verification or prototype feedback.

## 9. Constraints and Requirements

### 9.1 Hard Requirements

Core hard requirements are no floats in engine/saves, C89 core, Q16.16 runtime, Q4.12 save-local positions, 8-bit Segment addressing, toroidal 2^24m surface, one Page Z, content-agnostic core, and one canonical saved surface per planet.

### 9.2 Soft Preferences

Soft preferences include future-proof modularity, staged implementation, sparse storage, and keeping launcher/tools separate from simulation.

### 9.3 Technical Constraints

Fixed-point arithmetic, deterministic RNG, stable iteration order, sparse chunks, TLV saves, and content.lock registries are required by the design.

### 9.4 Time / Resource Constraints

No explicit calendar deadline was established. The user wants Codex to implement in the best order.

### 9.5 Legal / Ethical / Safety Constraints

No special legal/safety constraints were discussed beyond normal software correctness and deterministic modding. External facts or tools should be verified if they become relevant.

### 9.6 Evidence / Citation Requirements

The user generally prefers rigorous sourcing, but this chat focused on internal design. External-world facts, APIs, compilers, or tools require verification before future use.

### 9.7 Formatting / Output Requirements

The current package must provide Markdown/YAML files, stable IDs, labels, registers, audit, manifest, and ZIP if possible.

### 9.8 Things to Avoid

Avoid floats in core/saves, block-based matter, per-material full 3D density fields, chunk-authoritative simulation, full global CFD/EM/FEA, blind use of the previous Codex prompt, and overwriting repo files without inspection.

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
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

## 10. Open Questions and Unresolved Issues

| ID | Question / issue | Why it matters | Known information | Unknown information | What would resolve it | Priority | Related workstream | Label |
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

## 11. Rejected, Superseded, or Deprioritised Options

| ID | Option | Status | Reason rejected/superseded/deprioritised | Is rejection final? | Reconsider conditions | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| REJECTED-01 | Store full Q24.8 for all entity/object runtime positions | superseded/rejected | Runtime local Q16.16 plus segment addressing is more efficient. | Mostly final | Reconsider only for external APIs/tools. | WORKSTREAM-01 | FACT |
| REJECTED-02 | Use 32-bit fractional precision | rejected | Massive overprecision; storage/performance waste. | Final | Almost never. | WORKSTREAM-02 | INFERENCE |
| REJECTED-03 | Use 16-bit integer global world coordinates | rejected | Too small for planet-scale surface. | Final | Only for local spaces. | WORKSTREAM-01 | INFERENCE |
| REJECTED-04 | Use Q4.8 save-local positions | superseded | User later chose Q4.12. | Final unless user reverts | If storage pressure outweighs precision. | WORKSTREAM-03 | FACT |
| REJECTED-05 | Use saved/static 1/256m precision as final | superseded | Q4.12 gives 1/4096m precision inside chunks. | Final unless user reverts | If simpler saves needed. | WORKSTREAM-03 | FACT |
| REJECTED-06 | Use country/state/continent naming | superseded | User defined final scale names. | Final | No need. | WORKSTREAM-01 | FACT |
| REJECTED-07 | Save arbitrary surface instances now | deprioritized | User specified one canonical surface per planet in save files. | Tentative | Future sharding/dimensions. | WORKSTREAM-03 | FACT |
| REJECTED-08 | 2^32 systems per galaxy | superseded | User changed to 2^24 systems per galaxy. | Final for now | If requirements change. | WORKSTREAM-03 | FACT |
| REJECTED-09 | 2^8 planets per system | superseded | User changed to 2^16 planets per system. | Final for now | If address/storage tradeoff changes. | WORKSTREAM-03 | FACT |
| REJECTED-10 | Full per-material 3D density fields | rejected | Storage explosion; wrong abstraction. | Final | Tiny local special sims only. | WORKSTREAM-05 | INFERENCE |
| REJECTED-11 | Make ground/air out of blocks | rejected | User explicitly said ground and air will be abstract materials, not blocks. | Final | Logical placement blocks still exist. | WORKSTREAM-05 | FACT |
| REJECTED-12 | Full 3D voxel fluids for all water/air/oil | rejected | Too expensive; use FluidSpaces, hydrology graphs, basins. | Final | Small local CFD modules only. | WORKSTREAM-06 | INFERENCE |
| REJECTED-13 | Global full Navier–Stokes simulation | rejected | Out of scope/performance. | Final | Special localized device simulation only. | WORKSTREAM-06 | INFERENCE |
| REJECTED-14 | Global full electromagnetic simulation | rejected | Out of scope; graph circuits/path-loss enough. | Final | Special tools only. | WORKSTREAM-08 | INFERENCE |
| REJECTED-15 | Chunks own canonical simulation state | rejected | Breaks determinism/continuity under streaming. | Final | Never for core. | WORKSTREAM-04 | FACT |
| REJECTED-16 | Save partial network state per chunk as authority | rejected | Chunk loading could alter flows/pressure. | Final | Chunk references/caches only. | WORKSTREAM-08 | INFERENCE |
| REJECTED-17 | Floats in core or saves | rejected | User explicitly forbade. | Final | Unless user reverses. | WORKSTREAM-02 | FACT |
| REJECTED-18 | Blindly run previous Codex prompt unchanged | rejected | It contains fixed-point/C89/Region-bit errors. | Final | Use only after repair. | WORKSTREAM-11 | FACT |

Preserving these prevents repeated work: future assistants should not re-propose full per-material density fields, block-based matter, global CFD/EM, chunk-authoritative state, or the defective previous prompt without acknowledging why those were rejected.

## 12. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Where it came from | Carry forward? | Notes | Label |
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

## 13. Rationale and Assumptions

Major visible rationale:
- Power-of-two spatial units make address decomposition cheap and deterministic.
- Segment + local fixed-point avoids global large-coordinate math in hot loops.
- Chunks as caches prevent seams and streaming-dependent state.
- Save-local Q4.12 compresses object positions because high address bits are encoded by path/chunk.
- Continuous φ terrain supports smooth geometry, arbitrary cuts/fills, caves, cliffs, and overhangs.
- Media/material fields avoid exploding storage while supporting rock, air, water, oil, gas, magma, voids, and density/pressure/temperature.
- FluidSpaces and Connectors unify open-world weather, hydrology, rooms, tanks, pipes, reservoirs, and flooding.
- Graph networks for electrical/hydraulic/thermal/logic systems keep the core tractable.
- content.lock and deterministic registries keep official and modded content equivalent from the core’s perspective.

Assumptions:
- Compiler/toolchain can support 64-bit integers while maintaining C89-style code.
- A staged implementation is acceptable even though user wants Codex to complete the work.
- Assistant-accepted designs that the user built upon are reasonable to carry forward as INFERENCE where not explicitly stated.
- Repo structure is not yet known and must be inspected before applying file changes.

## 14. Risks and Failure Modes

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
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

## 15. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
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

## 16. Spec Book Contribution Notes

Likely Project Spec Book sections:
- World coordinate and scale hierarchy
- Deterministic fixed-point core
- Save format and content.lock
- Chunking, streaming, and runtime memory
- Continuous terrain/material/media model
- Hydrology, weather, FluidSpaces, and environmental systems
- Oil/gas/flooding/rupture systems
- Thermal/electrical/hydraulic/logical networks
- Modding/content pipeline
- Repo architecture, launcher, tools, and Codex implementation plan
- Testing and determinism

Unique contributions from this chat:
- Final scale names and final horizontal/Z dimensions.
- Q16.16/Q4.12 precision decisions.
- No-float C89/C++98 boundary.
- Chunks-as-caches principle.
- Unified FluidSpace/SpatialVolume/Network pattern.
- Oil/gas/rupture/flooding integration.
- Known corrections to the generated Codex prompt.

Possible duplicated topics in other chats:
- Dominium game design, automation/logistics, tooling, save formats, modding, rendering, ECS, engine architecture.

Conflicts to watch:
- Any later chat using floats in core.
- Any later chat changing world size, vertical height, precision, or IDs.
- Any later chat treating assistant recommendations as final without user confirmation.

Formal requirements candidates:
- No floats in core/saves.
- Fixed-point types.
- 2^24 toroidal surface.
- One Page vertical.
- Sparse TLV saves.
- content.lock deterministic registries.
- Chunks are caches.

Background context candidates:
- Comparisons to Satisfactory/Factorio/Minecraft/KSP.
- Rationale for rejected full CFD/EM.
- Feature examples such as volcanoes/waterfalls.

Needs user confirmation before spec:
- Exact C89 portability strategy.
- Solver formulas.
- Build system/repo layout.
- Meshing algorithm.
- Lua version.

## 17. What Future Assistants Must Preserve

| Priority | Item | Type | Why it matters | Risk if lost | Label | Confidence |
|---|---|---|---|---|---|---|
| 1 | No floats in core or saves | constraint | Hard user requirement | Breaks determinism/design | FACT | 5 |
| 2 | C89 core and C++98 platform/renderer boundary | constraint | Implementation language split | Wrong code generation | FACT | 5 |
| 3 | Toroidal 2^24m horizontal surface and one Page Z | decision | Defines all address math | Wrong world scale | FACT | 5 |
| 4 | Runtime Q16.16 and save Q4.12, with unsigned correction | decision/correction | Core numeric design | Overflow/corruption | FACT | 5 |
| 5 | 8-bit Segment addressing | decision | Surface decomposition | Bad wrap/addressing | FACT | 5 |
| 6 | Chunks are caches, not authorities | architecture | Continuity and determinism | Streaming-dependent bugs | FACT | 5 |
| 7 | Ground/air not blocks; use φ and media fields | architecture | Core world model | Wrong terrain/material implementation | FACT | 5 |
| 8 | FluidSpaces + Connectors unify liquids/gases/weather/rooms/tanks | architecture | Environmental extensibility | Fragmented systems | INFERENCE | 4 |
| 9 | SpatialVolumes for pockets/basins/voids/etc. | architecture | Feature extensibility | Ad-hoc systems | INFERENCE | 4 |
| 10 | Networks graph systems for pipes/electric/heat/logic | architecture | Avoid full multiphysics | Scope explosion | INFERENCE | 4 |
| 11 | content.lock and deterministic registries | architecture | Mod/content determinism | Save incompatibility | FACT | 5 |
| 12 | One canonical saved surface per planet for now | decision | Save hierarchy | Wrong directory structure | FACT | 5 |
| 13 | Cosmic IDs: 2^8 galaxies, 2^24 systems, 2^16 planets | decision | Save addressing | Wrong ID widths | FACT | 5 |
| 14 | Previous Codex prompt is draft and defective | artifact warning | Avoid baking bugs into repo | Implementation failure | FACT | 5 |
| 15 | Inspect repo before overwriting | task | No repo files were inspected | Data loss/bad structure | FACT | 5 |

## 18. What Future Assistants Must Not Assume

- Do not assume the existing git repo structure matches the proposed one.
- Do not assume the previous Codex prompt is safe to run unchanged.
- Do not assume strict ISO C89 automatically provides 64-bit integers.
- Do not assume terrain sample resolution 32³ is final; it was recommended, not user-confirmed.
- Do not assume exact atmo/hydro solver formulas or grid sizes are final.
- Do not assume Lua is definitely chosen or which version.
- Do not assume saved rotations can be 16-bit; user said saved rotations are 8-bit.
- Do not assume arbitrary surface instances are saved now; only one canonical surface is saved per planet for now.
- Do not assume assistant recommendations are user decisions unless accepted or built upon.
- Do not assume external APIs, compilers, prices, schedules, laws, or tool versions are current.

## 19. Recommended Next Action

If continuing this chat’s work alone: revise the previous Codex implementation prompt using this package, correcting fixed-point signedness, Region bit widths, C89 syntax, and saved rotations, then inspect the actual git repo before generating code changes.

If aggregating with other chat reports: ingest this package as the authoritative report for the Dominium world architecture/fixed-point/save/environment systems chat, but keep its INFERENCE and UNCERTAIN labels intact.

User verification needed before acting: confirm C89 portability expectations and whether unsigned UQ16.16/UQ4.12 is the preferred correction.

## 20. Appendix: Possibly Relevant Details

- Scale hierarchy:
  - 2^-16 Plank
  - 2^-12 Point
  - 2^-8 Step
  - 2^-4 Sixteenth
  - 2^0 Block
  - 2^4 Chunk
  - 2^8 Region
  - 2^12 Page
  - 2^16 Segment
  - 2^20 Sector
  - 2^24 Surface
- Correct horizontal integer-meter decomposition:
  - Segment: bits 16..23, 8 bits
  - Region-in-Segment: bits 8..15, 8 bits
  - Chunk-in-Region: bits 4..7, 4 bits
  - Block-in-Chunk: bits 0..3, 4 bits
- Current package was generated from this chat and the previous Context Transfer Packet; no external files were read.
