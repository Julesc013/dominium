# Aggregator Packet — Dominium Architecture II

## 1. Packet Metadata

- Chat label: Dominium Architecture II
- Date anchor: 2026-05-27 Australia/Melbourne
- Source scope: Visible chat content only; no project files inspected.
- Coverage: Partial but high-fidelity for visible content.
- Confidence: 4/5.
- Staleness risk: Medium.
- Merge priority: High for Dominium architecture, MVP, docs/Codex implementation and renderer/platform split.
- Main limitations: Some early messages skipped; actual repo files unverified; external compatibility facts stale.

## 2. Ultra-Condensed Carry-Forward Capsule

This chat, **Dominium Architecture II**, is a high-density architecture, specification, and Codex-preparation session for the Dominium engine/game project. It develops a deterministic, modular, multi-scale simulation engine intended to support both retro and modern platforms, with an immediate MVP target and a long-term extensible platform/renderer/data/modding architecture. The most important state to preserve is that Dominium is not merely a game idea; in this chat it was shaped into a tightly constrained deterministic engine architecture with explicit repository contracts and Codex implementation prompts.

The most important user-defined MVP is: a fully complete core; one full-size Earth surface; all systems interactable through minimal data prototypes; Lua for all data; Windows/DX9/Win32/SDL2 path; 2D vector top-down and 3D vector first-person rendering. Textures, sounds, music, multiplayer, the Sol system/space expansion, additional renderers, and additional platforms are post-MVP.

Major architectural choices were fixed. The world uses meters with Q16.16 fixed substeps, not a millimeter base. The spatial ladder is base-16 from subnano to surface, with sparse chunk/microgrid storage rather than a dense planetary grid. The simulation is deterministic, integer/fixed-point, tick-based, C89-compatible in core, and strictly separated from platform and renderer code. The renderer is a pure observer. Platform backends handle OS/window/input/time; renderer backends handle graphics APIs; the sim never includes OS, DirectX, OpenGL, Vulkan, SDL, or other external platform/graphics headers.

The building and infrastructure model was heavily refined. Buildings use blocks/modules/cells/faces/edges as simulation truth, with walls/floors/roofs on grid faces/edges including diagonals. Doors and devices are explicit fixtures on anchors; they must not appear automatically or be hardcoded into every tunnel type. Terrain uses immutable base terrain plus earthworks deltas/cavities and structural microgrids. Vector splines exist as authoring/generation/visual inputs for roads, rails, tunnels, bridges, platforms, and utilities; runtime sim uses deterministic baked chainpoints, linear microgrids, cells, and graphs.

Space was separated from surfaces: surfaces are high-fidelity physical domains, while space is a logical/on-rails domain using orbital rails, transfer nodes, local bubbles for docking/approach, and explicit state-machine transitions for takeoff/landing/docking. Orbital ships/stations/yards, rockets, drop pods, and cargo tugs were designed as future extensions using the same ECS/jobs/inventory/graph primitives.

The chat also generated or updated many project artifacts: root docs, directory contracts, per-directory dev specs, Codex prompts, and V4 replacements for BUILDING.md, SPEC_CORE.md, DATA_FORMATS.md, and DIRECTORY_CONTEXT.md. The user later provided the actual current file tree and explicitly wants Codex 5.1 Max to work only from those files. A key addendum should live at `docs/dev/dominium_new_addendum.txt`.

Open issues remain: actual repo state is unverified; Lua-for-all-data must be reconciled with JSON-oriented data docs; final render command/camera APIs need settling; DX9/Windows 2000 and SDL2 compatibility must be verified; Lua 5.4.4 portability to old compilers must be tested; and the restrictive licence needs legal review.

## 3. Top Carry-Forward Items

| Priority | Item | Type | Why it matters | Risk if lost | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | MVP scope exactly as user stated | decision/scope | Prevents overbuilding or underbuilding MVP. | MVP direction lost. | FACT | high |
| 2 | Strict deterministic integer/fixed-point core | requirement | Foundational technical identity. | Desync/invalid architecture. | FACT | high |
| 3 | Renderer/platform/sim separation | requirement | Prevents OS/GPU contamination. | Layer violations. | FACT | high |
| 4 | User-provided current file tree | artifact | Defines Codex universe. | Wrong file references. | FACT | high |
| 5 | V4 BUILDING/SPEC_CORE/DATA_FORMATS/DIRECTORY_CONTEXT | artifacts | Core spec layer. | Codex follows stale docs. | FACT | high |
| 6 | docs/dev/dominium_new_addendum.txt addendum location | artifact/path | Codex renderer/platform override. | Missing binding addendum. | FACT | high |
| 7 | Spatial ladder and Earth/Sol/Milky Way defaults | decision | World model. | Coordinate/world errors. | FACT | high |
| 8 | Blocks/cells/faces/edges + explicit fixtures | decision | Building system. | Wrong building implementation. | FACT | high |
| 9 | Immutable base terrain + earthworks + microgrids | decision | Terrain integrity. | Terrain/structure conflation. | FACT | high |
| 10 | Splines baked into chainpoints/microgrids | decision | Infrastructure runtime. | Runtime curve complexity. | FACT | high |
| 11 | On-rails space and local bubbles | decision | Future space. | Premature n-body implementation. | FACT | high |
| 12 | /engine/script + Lua 5.4.4 + sandboxed API | decision | Data layer. | Lua misplaced/unsafe. | FACT | high |
| 13 | FNV-1a 64-bit full-state hash | decision | Determinism tests. | Weak/partial validation. | FACT | high |
| 14 | Codex staged implementation order | plan | Keeps implementation manageable. | Chaotic codegen. | FACT | high |
| 15 | Rejected options list | risk control | Prevents repeating dead designs. | Repeated design churn. | FACT | high |

## 4. Workstream Summaries

### WORKSTREAM-01 — Unified documentation/source-of-truth
- Objective: Consolidate architecture and Codex-facing instructions into a coherent source of truth.
- Current state: V4 replacements for BUILDING.md, SPEC_CORE.md, DATA_FORMATS.md, and DIRECTORY_CONTEXT.md were generated in this chat; actual on-disk application is unverified.
- Desired end state: The four docs plus docs/dev/dominium_new_addendum.txt consistently guide Codex without contradictions.
- Priority: P0
- Decisions: docs/dev/dominium_new_addendum.txt is the addendum location, not a new CODEGEN_ADDENDUM.md., Actual user-provided file names and tree win over earlier generic names.
- Tasks: TASK-01, TASK-02, TASK-03, TASK-04, TASK-05
- Constraints: CONSTRAINT-07, CONSTRAINT-11, CONSTRAINT-12
- Artifacts: ARTIFACT-19, ARTIFACT-20, ARTIFACT-21, ARTIFACT-22, ARTIFACT-23
- Risks: RISK-01, RISK-02
- Open questions: see Question Register.
- Next action: Run the Codex consistency pass or manually verify the four docs.

### WORKSTREAM-02 — Deterministic core/kernel
- Objective: Implement the deterministic C89 simulation kernel.
- Current state: Detailed V3 determinism material and SPEC_CORE V4 exist as visible design outputs.
- Desired end state: A ticking deterministic core with fixed phases, lanes, merge, fixed-point math, and no sim floats.
- Priority: P0
- Decisions: No floats in /engine/core or /engine/sim., Seven-phase tick pipeline., Simulation slows rather than skipping ticks.
- Tasks: TASK-06, TASK-07, TASK-17
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-03, CONSTRAINT-04
- Artifacts: WORKSTREAM-03, WORKSTREAM-16
- Risks: RISK-05, RISK-10
- Open questions: see Question Register.
- Next action: Generate engine/core skeletons and sim tick/ECS shell.

### WORKSTREAM-03 — ECS architecture
- Objective: Define and implement deterministic entity/component/system architecture.
- Current state: V3 1B material and engine/ecs dev spec were generated.
- Desired end state: Stable entity IDs/generations, POD components, dense arrays, sorted active lists, deterministic iteration.
- Priority: P0
- Decisions: Entity handle is ID plus generation., Components are POD with fixed layout., Structural changes deferred to command buffers and merge.
- Tasks: TASK-07, TASK-18
- Constraints: CONSTRAINT-06, CONSTRAINT-09
- Artifacts: WORKSTREAM-02, WORKSTREAM-04
- Risks: RISK-10, RISK-17
- Open questions: see Question Register.
- Next action: Implement ECS shell with deterministic tests.

### WORKSTREAM-04 — Messaging, events, jobs
- Objective: Provide deterministic event buses, command buffers, jobs, deferred ops and interrupts.
- Current state: V3 1B-2a/b visible and sim dev spec generated.
- Desired end state: Fixed-size queues, deterministic ordering, one-tick cross-lane/global latency, job assignment with stable tie-breaks.
- Priority: P0
- Decisions: Queue overflow deterministic oldest-drop plus flag., Jobs assigned deterministically., Commands mutate world only at safe phases.
- Tasks: TASK-07, TASK-22
- Constraints: CONSTRAINT-08, CONSTRAINT-09
- Artifacts: WORKSTREAM-03
- Risks: RISK-05, RISK-10
- Open questions: see Question Register.
- Next action: Implement event/job skeletons and minimal worker job prototype.

### WORKSTREAM-05 — Spatial hierarchy and cosmic identity
- Objective: Define coordinates, scale ladder, sparse chunking, and universe/galaxy/system/planet/surface IDs.
- Current state: User fixed the scale ladder and defaults; SPEC_CORE/DATA_FORMATS were updated around it.
- Desired end state: Single Earth surface MVP with full hierarchy capability and sparse chunks/microgrids.
- Priority: P0
- Decisions: Subnano through Surface base-16 ladder., Default Earth/Sol/Milky Way., Base game starts with one surface.
- Tasks: TASK-19
- Constraints: CONSTRAINT-15, CONSTRAINT-16
- Artifacts: WORKSTREAM-06, WORKSTREAM-16
- Risks: RISK-15
- Open questions: see Question Register.
- Next action: Implement constants and single-surface sparse chunk roots.

### WORKSTREAM-06 — Terrain, cut/fill, and microgrids
- Objective: Support terrain edits, underground/overground structures, and logical separation from base terrain.
- Current state: Three-layer model established: immutable base terrain, earthworks deltas/cavities, structural microgrids.
- Desired end state: Flat MVP surface with future-ready cut/fill/cavity hooks.
- Priority: P1
- Decisions: Base terrain immutable., Earthworks are deltas: H_eff = H_base + ΔH., Structures are separate microgrids.
- Tasks: TASK-19, TASK-27
- Constraints: CONSTRAINT-17, CONSTRAINT-18
- Artifacts: WORKSTREAM-05, WORKSTREAM-07
- Risks: RISK-15, RISK-17
- Open questions: see Question Register.
- Next action: Implement flat heightfield plus delta/cavity placeholders.

### WORKSTREAM-07 — Building system: cells, faces, edges, fixtures
- Objective: Use a unified building system for surface, underground and orbital structures.
- Current state: Blocks/modules/cells/faces/edges model and explicit fixture/anchor system defined.
- Desired end state: MVP can place functional blocks/devices and simple walls/floors; future supports collapse/destruction.
- Priority: P0
- Decisions: Blocks/modules are sim truth., Walls/floors/roofs on faces/edges, including diagonals., Doors/devices are explicit fixtures; no automatic doors.
- Tasks: TASK-15, TASK-20, TASK-21
- Constraints: CONSTRAINT-19, CONSTRAINT-20, CONSTRAINT-21
- Artifacts: WORKSTREAM-03, WORKSTREAM-06, WORKSTREAM-15
- Risks: RISK-11, RISK-17
- Open questions: see Question Register.
- Next action: Define minimal prefab schema and place generator/consumer/cable/building blocks.

### WORKSTREAM-08 — Vector corridor/spline infrastructure
- Objective: Support arbitrary vector splines for roads, rails, tunnels, bridges, platforms and utilities.
- Current state: Alignment-to-chainpoint-to-linear-microgrid pipeline defined; full implementation deferred beyond minimal MVP.
- Desired end state: Data-driven corridor archetypes, fixtures/anchors, bridge/tunnel/cut/fill generation, node topology.
- Priority: P1
- Decisions: Splines are authoring metadata; runtime uses baked chainpoints/cells/graphs., Corridors use archetypes+instances., Doors/utilities are fixtures/patterns only when explicitly placed.
- Tasks: TASK-25
- Constraints: CONSTRAINT-22, CONSTRAINT-23
- Artifacts: WORKSTREAM-06, WORKSTREAM-07, WORKSTREAM-10
- Risks: RISK-12, RISK-15
- Open questions: see Question Register.
- Next action: Implement simplest straight corridor/vehicle path only in MVP.

### WORKSTREAM-09 — Utility networks: power, data, fluids, thermal
- Objective: Graph/field utility systems for machines and infrastructure.
- Current state: Power/data/fluid/thermal network specs generated; MVP requires minimal interactive prototypes.
- Desired end state: Power gen/load works first; fluid/data minimal snapshots; thermal may be stubbed.
- Priority: P0/P1
- Decisions: Power balances generation/load per connected component., Data packets/signals one hop/tick., Fluids deterministic pressure/flow graph.
- Tasks: TASK-20, TASK-21
- Constraints: CONSTRAINT-05, CONSTRAINT-24
- Artifacts: WORKSTREAM-03, WORKSTREAM-16, WORKSTREAM-15
- Risks: RISK-13
- Open questions: see Question Register.
- Next action: Implement generator-consumer-cable power prototype.

### WORKSTREAM-10 — Transport systems
- Objective: Represent rail, road, water, air and space movement as graphs/corridors/fields.
- Current state: Generalized design exists; MVP only needs one minimal transport segment/vehicle.
- Desired end state: Unified transport graph with modes, vehicles, stations, signals, bridges/tunnels.
- Priority: P1
- Decisions: Topology connects at nodes; mid-edge connection creates/splits nodes., Rail/road etc. map to graph/corridor primitives.
- Tasks: TASK-25
- Constraints: CONSTRAINT-22, CONSTRAINT-28
- Artifacts: WORKSTREAM-08, WORKSTREAM-11
- Risks: RISK-11
- Open questions: see Question Register.
- Next action: Pick rail or road and implement a straight segment with one deterministic vehicle.

### WORKSTREAM-11 — Pathfinding and deterministic movement
- Objective: Deterministic path and vehicle/worker movement primitives.
- Current state: Engine/path and engine/physics dev specs generated; no code confirmed.
- Desired end state: Integer A*/routing and simple kinematics suitable for workers/vehicles/corridors.
- Priority: P1
- Decisions: A* deterministic tie-breaking., Runtime movement uses discrete/chain constraints.
- Tasks: TASK-22, TASK-25
- Constraints: CONSTRAINT-22, CONSTRAINT-02
- Artifacts: WORKSTREAM-03, WORKSTREAM-05, WORKSTREAM-08
- Risks: RISK-10, RISK-12
- Open questions: see Question Register.
- Next action: Implement grid/straight-line path stub sufficient for one worker/job. 

### WORKSTREAM-12 — Surface vs space and orbital systems
- Objective: Separate high-resolution surface sim from logical on-rails space sim.
- Current state: Design defined, post-MVP.
- Desired end state: Orbit rails, SOI, Lagrange points, belts/clouds/EM fields, local bubbles, docking transitions.
- Priority: P2
- Decisions: Use on-rails orbital mechanics., Local bubbles for docking/approach., Discrete domain transitions.
- Tasks: TASK-29
- Constraints: CONSTRAINT-26
- Artifacts: WORKSTREAM-05, WORKSTREAM-16
- Risks: RISK-07
- Open questions: see Question Register.
- Next action: Keep stubs only; do not implement in MVP. 

### WORKSTREAM-13 — Orbital construction/logistics
- Objective: Support construction and servicing of orbital ships/stations.
- Current state: Conceptual design defined, not MVP.
- Desired end state: Orbital yards/stations/ships serviced by rockets/drop pods/cargo tugs.
- Priority: P2
- Decisions: Stations/ships/yards are ECS entities., Rockets/drop pods bridge surface-orbit., Tugs are orbital worker/vehicle jobs.
- Tasks: TASK-29
- Constraints: CONSTRAINT-26
- Artifacts: WORKSTREAM-12, WORKSTREAM-04, WORKSTREAM-07
- Risks: RISK-07
- Open questions: see Question Register.
- Next action: Preserve design, defer implementation.

### WORKSTREAM-14 — Renderer/platform mix-and-match
- Objective: Cleanly separate OS/platform and renderer backends and allow cross-product selection.
- Current state: Addendum and BUILDING V4 specify platform API, renderer API, backend registry, DX9 MVP.
- Desired end state: Win32+DX9 MVP; later SDL2/DX11/GL/VK/DX12/Linux/macOS/retro. 
- Priority: P0
- Decisions: MVP Windows NT 2000 SP4 through Windows 11+, DX9.0c., Native Win32 first, SDL2 optional/later., Renderer pure observer.
- Tasks: TASK-08, TASK-09, TASK-34
- Constraints: CONSTRAINT-05, CONSTRAINT-06, CONSTRAINT-25
- Artifacts: WORKSTREAM-17
- Risks: RISK-04, RISK-08, RISK-09
- Open questions: see Question Register.
- Next action: Finalize render API then implement Win32 + DX9 vector shell.

### WORKSTREAM-15 — Lua data and script binding
- Objective: Enable Lua-driven data prototypes and sandboxed script interaction.
- Current state: Codex clarification answered: /engine/script, Lua 5.4.4, API namespaces and sandbox.
- Desired end state: Lua loads data/prefabs/jobs/net snapshots through safe deterministic engine APIs.
- Priority: P0
- Decisions: Create /engine/script., Vendor Lua 5.4.4., Expose dom.entity/query/prefab/data/net/jobs/random., Disable io/os/unrestricted debug/native modules.
- Tasks: TASK-12, TASK-13, TASK-14, TASK-15, TASK-16, TASK-33
- Constraints: CONSTRAINT-13, CONSTRAINT-14
- Artifacts: WORKSTREAM-03, WORKSTREAM-09, WORKSTREAM-16
- Risks: RISK-05, RISK-06
- Open questions: see Question Register.
- Next action: Amend DIRECTORY_CONTEXT and implement VM/sandbox skeleton.

### WORKSTREAM-16 — Serialization, save/replay, state hash
- Objective: Persist and hash authoritative state deterministically.
- Current state: DATA_FORMATS V4 generated; FNV-1a hash rule clarified.
- Desired end state: Canonical serialization buffer for save/load/replay/hash, FNV-1a tick hash tests.
- Priority: P0
- Decisions: FNV-1a 64-bit over full authoritative serialized sim state., Exclude debug/reconstructable caches., Little-endian binary formats; no pointers.
- Tasks: TASK-17, TASK-18, TASK-26
- Constraints: CONSTRAINT-10, CONSTRAINT-29, CONSTRAINT-30, CONSTRAINT-31
- Artifacts: WORKSTREAM-02, WORKSTREAM-03, WORKSTREAM-09
- Risks: RISK-10, RISK-14
- Open questions: see Question Register.
- Next action: Implement dom_core_hash and canonical serializer skeleton.

### WORKSTREAM-17 — Build system and CMake
- Objective: Create deterministic modular CMake build and stubs.
- Current state: BUILDING V4 and root CMake draft/prompt exist; actual applied state unknown.
- Desired end state: Root and per-dir CMake with explicit file lists, DR mode, MVP backend flags.
- Priority: P0
- Decisions: CMake canonical for modern builds., Retro builds isolated under /ports., No globbing.
- Tasks: TASK-06
- Constraints: CONSTRAINT-32, CONSTRAINT-33
- Artifacts: WORKSTREAM-01, WORKSTREAM-14
- Risks: RISK-02, RISK-16
- Open questions: see Question Register.
- Next action: Run CMake skeleton prompt. 

### WORKSTREAM-18 — MVP client loop and UI/HUD
- Objective: Produce a playable vector-only minimal loop.
- Current state: Prompt generated for minimal client loop; no code confirmed.
- Desired end state: 2D/3D camera, tick loop, vector rendering, selection/placement UI, minimal HUD.
- Priority: P0/P1
- Decisions: 2D top-down vector and 3D first-person vector., No textures/audio in MVP.
- Tasks: TASK-09, TASK-10, TASK-24
- Constraints: CONSTRAINT-27, CONSTRAINT-35
- Artifacts: WORKSTREAM-02, WORKSTREAM-14, WORKSTREAM-15
- Risks: RISK-11
- Open questions: see Question Register.
- Next action: Wire minimal client loop with flat world. 

### WORKSTREAM-19 — Testing and CI
- Objective: Validate determinism and prevent regressions.
- Current state: Tests dev spec generated; FNV tick+hash test planned.
- Desired end state: Unit, integration, replay, perf tests; CI boundary checks.
- Priority: P0/P1
- Decisions: Hash full authoritative sim state via FNV-1a., Headless tick+hash test first.
- Tasks: TASK-18
- Constraints: CONSTRAINT-36
- Artifacts: WORKSTREAM-16
- Risks: RISK-10
- Open questions: see Question Register.
- Next action: Implement first deterministic headless test. 

### WORKSTREAM-20 — Legal/governance docs
- Objective: Provide restrictive project governance, licence, contribution and security docs.
- Current state: Drafts generated for README, LICENCE, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, CHANGELOG, .gitignore, etc.
- Desired end state: Consistent, legally reviewed governance docs.
- Priority: P1
- Decisions: Licence should be completely restrictive except personal use/source viewing.
- Tasks: TASK-31
- Constraints: CONSTRAINT-34
- Artifacts: See artifact ledger.
- Risks: RISK-18
- Open questions: see Question Register.
- Next action: Legal review of LICENCE.md and references. 

### WORKSTREAM-21 — Future multiplayer and server universe
- Objective: Add deterministic multiplayer, server/shard interaction and cross-server trade/communication.
- Current state: Planned after MVP; net protocol/dev specs exist conceptually.
- Desired end state: Lockstep or server-authoritative multiplayer with async cross-surface interactions.
- Priority: P2
- Decisions: Multiplayer after MVP., Cross-surface interactions async only.
- Tasks: TASK-28
- Constraints: CONSTRAINT-26
- Artifacts: WORKSTREAM-16, WORKSTREAM-02
- Risks: RISK-07, RISK-19
- Open questions: see Question Register.
- Next action: Keep net stubs and replay tests; defer live multiplayer. 

### WORKSTREAM-22 — Future platforms/renderers/assets
- Objective: Add non-MVP renderers/platforms/textures/audio/music.
- Current state: Roadmap defined; implementation deferred.
- Desired end state: DX11/GL1/GL2/VK1/DX12, Windows 98, Linux/macOS, retro, textures/audio/music packs.
- Priority: P2/P3
- Decisions: DX9 first; other backends later., Textures/sounds/music later.
- Tasks: TASK-29, TASK-30
- Constraints: CONSTRAINT-25, CONSTRAINT-33
- Artifacts: WORKSTREAM-14
- Risks: RISK-08, RISK-09
- Open questions: see Question Register.
- Next action: Do not implement prematurely; keep stubs/fallbacks only. 


## 5. Registers for Merge

### Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Use meter-based world coordinates with fixed substeps/Q16.16. | final | User selected world unit option B. | Fits base-16 hierarchy and avoids millimeter-wide coordinates. | Spatial representation and serialization use meter tiles plus substeps. | WORKSTREAM-05 | high | FACT |
| DECISION-02 | Use strict sim/render separation. | final | User selected rendering contract A. | Simplifies determinism proof. | Renderer is pure observer; sim has no GPU/OS dependencies. | WORKSTREAM-14 | high | FACT |
| DECISION-03 | Adopt base-16 spatial ladder from subnano to surface. | final | User explicitly provided ladder. | Matches fixed-point subdivisions and chunk hierarchy. | Constants and chunking derive from ladder. | WORKSTREAM-05 | high | FACT |
| DECISION-04 | Store surfaces as sparse microgrids/chunks, not continuous dense arrays. | final | User explicitly stated no continuous grid. | Full-size surfaces are too large dense. | Only active chunks/microgrids allocate data. | WORKSTREAM-05 | high | FACT |
| DECISION-05 | Default local world is Earth/Sol/Milky Way. | final | User stated default planet/system/galaxy. | Canonical single-player world. | MVP starts on Earth surface. | WORKSTREAM-05 | high | FACT |
| DECISION-06 | Support canonical surface plus multiple surface instances for shards/mirrors. | final-ish | User asked; assistant reconciled one surface vs sharding; no rejection. | Needed for servers and mirrors without cross-sim coupling. | SurfaceID identifies instance; one canonical default. | WORKSTREAM-09 | medium-high | FACT |
| DECISION-07 | Cross-surface interactions are asynchronous external events only. | final-ish | Assistant recommendation after sharding discussion; continuation accepted. | Avoids cross-shard desync. | No shared physics/networks across surfaces. | WORKSTREAM-09 | medium-high | FACT |
| DECISION-08 | Use on-rails orbital mechanics, not full n-body. | final-ish | Space mechanics answer. | Full n-body harms determinism/debuggability. | Orbit graph/rails and local bubbles. | WORKSTREAM-12 | high | FACT |
| DECISION-09 | Docking, landing and takeoff are state-machine/domain transitions. | final-ish | Space and orbital logistics answers. | One domain owns entity at a time. | Rockets/pods/craft transition via command events. | WORKSTREAM-12 | high | FACT |
| DECISION-10 | Use blocks/modules/cells/faces/edges as building simulation truth. | final | User and assistant building discussion. | Discrete sim supports pathing/collision/pressure/retro. | Buildings, stations, ships share representation. | WORKSTREAM-07 | high | FACT |
| DECISION-11 | Use vector shapes/splines as authoring, generation and visual layers only. | final | Building/spline discussions. | Avoid continuous geometry in sim. | Vectors bake into chainpoints/cells/meshes. | WORKSTREAM-08 | high | FACT |
| DECISION-12 | Place walls/floors/roofs on grid faces/edges including diagonals. | final | User explicitly requested. | Allows arbitrary orthogonal/diagonal layouts. | FaceWall/EdgeWall lattice needed. | WORKSTREAM-07 | high | FACT |
| DECISION-13 | Buildings rigid for now but schema supports destruction/collapse later. | final | User explicitly stated. | Avoids MVP complexity but future-proofs data. | Strength/connectivity fields may be present. | WORKSTREAM-07 | high | FACT |
| DECISION-14 | Doors/devices are explicit fixtures placed manually or by explicit blueprint/pattern. | final | User did not want auto doors; assistant socket model. | Avoids coding doors into each tunnel type. | Anchors/sockets + fixture entities. | WORKSTREAM-07 | high | FACT |
| DECISION-15 | Immutable base terrain plus earthworks deltas and cavities. | final | Cut/fill discussion. | Preserves natural terrain and tracks modifications. | H_eff=H_base+ΔH; cavities overlay terrain. | WORKSTREAM-06 | high | FACT |
| DECISION-16 | Vector alignments bake into deterministic ChainPoints and linear microgrids. | final | Spline answer. | Runtime efficiency/determinism. | Corridor generator pipeline. | WORKSTREAM-08 | high | FACT |
| DECISION-17 | Connections occur at nodes; mid-segment connections create/split nodes. | final | Earlier way-spline answer. | Simplifies topology and signalling. | Graph topologies remain explicit. | WORKSTREAM-08 | medium-high | FACT |
| DECISION-18 | Generalize architecture to five primitives. | final-ish | Generalization answer. | Avoids 100 subsystems. | Frames/lattices, archetypes/components, graphs/fields, blueprints/diffs, ticks/jobs. | WORKSTREAM-01 | high | FACT |
| DECISION-19 | MVP is one full-size Earth surface with all systems interactable via minimal prototypes. | final | User explicit MVP. | Test core breadth without full content. | Implementation scope. | WORKSTREAM-18 | high | FACT |
| DECISION-20 | MVP uses Lua for all data. | final | User explicit MVP. | Data-driven prototypes. | Lua binding must exist. | WORKSTREAM-15 | high | FACT |
| DECISION-21 | MVP uses 2D vector top-down and 3D vector first-person rendering. | final | User explicit MVP. | Avoid texture/sound asset bottleneck. | Vector render shell needed. | WORKSTREAM-18 | high | FACT |
| DECISION-22 | Initial platform/render target is Windows 2000+ to Windows 11+ with DX9.0c and Win32/SDL2. | final-ish | User explicit rollout. | Focus implementation. | Win32+DX9 first; SDL2 optional/later. | WORKSTREAM-14 | medium-high | FACT |
| DECISION-23 | Textures, sounds and music are post-MVP. | final | User stated they will make textures/sounds/music later. | Avoid assets during core work. | Null audio/vector only for now. | WORKSTREAM-22 | high | FACT |
| DECISION-24 | Multiplayer is post-MVP. | final | User next steps list. | Core first. | Net stubs/serialization now; live multiplayer later. | WORKSTREAM-21 | high | FACT |
| DECISION-25 | Space/Sol system is post-MVP. | final | User next steps list. | Core/surface first. | Orbital stubs/context only. | WORKSTREAM-12 | high | FACT |
| DECISION-26 | Add /engine/script for Lua binding and amend directory contract. | final | Codex clarification answer. | Needed for Lua without misplacing code. | New engine subdir. | WORKSTREAM-15 | high | FACT |
| DECISION-27 | Vendor Lua 5.4.4 under /third_party. | final-ish | Clarification answer. | Chosen Lua runtime. | Third-party pinned source/includes. | WORKSTREAM-15 | medium-high | FACT |
| DECISION-28 | Lua API is sandboxed and limited to data/light orchestration. | final | Clarification answer. | Protect determinism/security. | No OS/native module access; commands only. | WORKSTREAM-15 | high | FACT |
| DECISION-29 | Use FNV-1a 64-bit over canonical serialized sim state for tests. | final | Clarification answer. | Early deterministic validation. | Implement dom_core_hash and serializer. | WORKSTREAM-16 | high | FACT |
| DECISION-30 | Codex must use only listed files. | final | User explicit. | Avoid hidden-project assumptions. | Prompts scope tightly. | WORKSTREAM-22 | high | FACT |
| DECISION-31 | Regenerate BUILDING.md, SPEC_CORE.md, DATA_FORMATS.md, DIRECTORY_CONTEXT.md as next docs. | done | User explicit; assistant generated V4 replacements. | Aligns core spec layer. | Docs should be applied/verified. | WORKSTREAM-01 | high | FACT |
| DECISION-32 | Licence should be restrictive except personal use/source viewing. | draft/final intent | User explicitly requested. | Protect IP. | LICENCE.md draft generated; legal review needed. | WORKSTREAM-20 | medium | FACT |

### Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Recommended next step | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Apply/verify BUILDING.md V4 | P0 | U0 | User/Codex | Generated BUILDING V4 | Existing docs/BUILDING.md | Updated BUILDING.md | Patch or compare file | WORKSTREAM-01 | FACT |
| TASK-02 | Apply/verify SPEC_CORE.md V4 | P0 | U0 | User/Codex | Generated SPEC_CORE V4 | Existing docs/SPEC_CORE.md | Updated SPEC_CORE.md | Patch or compare file | WORKSTREAM-01 | FACT |
| TASK-03 | Apply/verify DATA_FORMATS.md V4 | P0 | U0 | User/Codex | Generated DATA_FORMATS V4 | Existing docs/DATA_FORMATS.md | Updated DATA_FORMATS.md | Patch or compare file | WORKSTREAM-01 | FACT |
| TASK-04 | Apply/verify DIRECTORY_CONTEXT.md V4 | P0 | U0 | User/Codex | Generated DIRECTORY_CONTEXT V4, User tree | Existing docs/DIRECTORY_CONTEXT.md | Updated directory contract | Patch or compare file | WORKSTREAM-01 | FACT |
| TASK-05 | Verify dominium_new_addendum.txt contains renderer/platform addendum | P0 | U0 | User/Codex | Addendum generated in chat | docs/dev/dominium_new_addendum.txt | Correct addendum file | Inspect/paste/update | WORKSTREAM-01 | FACT |
| TASK-06 | Generate CMake/build skeleton | P0 | U1 | Codex | Docs consistency | CMake prompt, BUILDING V4 | Root/per-dir CMake and minimal stubs | Run generated prompt | WORKSTREAM-17 | FACT |
| TASK-07 | Implement core/sim/ECS shell | P0 | U1 | Codex | CMake skeleton, Core docs | Core and sim prompts | dom_core and dom_sim skeleton files | Run core then sim prompts | WORKSTREAM-02 | FACT |
| TASK-08 | Implement Win32 + DX9 vector shell | P0 | U1 | Codex | Platform/render API | Render/platform prompt | Window, input, DX9 vector backend | Run prompt after build skeleton | WORKSTREAM-14 | FACT |
| TASK-09 | Wire minimal client loop | P0 | U1 | Codex | Core/sim/render/platform shells | Client loop prompt | Empty Earth surface loop with cameras | Run prompt after shells | WORKSTREAM-18 | FACT |
| TASK-10 | Implement 2D/3D vector camera/input controls | P0 | U1 | Codex | Client loop, Render API | Input/camera spec needs finalization | Pan/zoom/toggle first-person camera | Finalize API then implement | WORKSTREAM-18 | FACT |
| TASK-11 | Add /engine/script to DIRECTORY_CONTEXT/build | P0 | U1 | Codex | Lua decision | Clarification answer | Directory contract and build include script dir | Patch docs and CMake | WORKSTREAM-15 | FACT |
| TASK-12 | Vendor Lua 5.4.4 | P0 | U1 | Codex/User | Third-party policy | Lua source, Licence | Pinned Lua source/includes | Verify and add | WORKSTREAM-15 | FACT |
| TASK-13 | Implement script VM and sandbox | P0 | U1 | Codex | Lua vendored | Lua API/sandbox spec | dom_script_vm and sandbox files | Create /engine/script skeleton | WORKSTREAM-15 | FACT |
| TASK-14 | Implement Lua bindings | P0 | U1 | Codex | Script VM, ECS/prefabs/net/jobs APIs | Binding scope | dom.entity/query/prefab/data/net/jobs/random | Implement minimal safe bindings | WORKSTREAM-15 | FACT |
| TASK-15 | Create minimal Lua data prototypes | P0 | U1 | Codex/User | Lua bindings | Data schema decision | Generator/consumer/cable/worker/vehicle prototypes | Define data tables | WORKSTREAM-15 | FACT |
| TASK-16 | Reconcile Lua-for-data with DATA_FORMATS JSON sections | P0 | U1 | User/Codex | MVP data decision | DATA_FORMATS V4 | Clear data policy | Update docs if needed | WORKSTREAM-15 | INFERENCE |
| TASK-17 | Implement FNV-1a hash | P0 | U1 | Codex | Core skeleton | Hash spec | dom_core_hash.[ch] | Implement early | WORKSTREAM-16 | FACT |
| TASK-18 | Implement canonical state serializer and headless hash test | P0 | U1 | Codex | ECS/sim state, Hash | DATA_FORMATS, test spec | Serialized state hash and test | Implement after sim shell | WORKSTREAM-16 | FACT |
| TASK-19 | Implement single Earth surface spatial roots | P0 | U1 | Codex | Spatial constants | Scale ladder, SPEC_CORE | Flat/sparse Earth surface root | Implement minimal spatial module | WORKSTREAM-05 | FACT |
| TASK-20 | Implement minimal power prototype | P0 | U1 | Codex | ECS/network components, Lua data | SPEC_CORE | Generator-consumer-cable working | Implement first network | WORKSTREAM-09 | FACT |
| TASK-21 | Implement minimal fluid/data prototypes | P1 | U1 | Codex | Network shell | SPEC_CORE | Simple flow and data snapshots | Implement after power | WORKSTREAM-09 | FACT |
| TASK-22 | Implement worker/job prototype | P0 | U1 | Codex | Jobs, path, Lua data | Job specs | Worker walks/performs fixed job | Implement with simple path | WORKSTREAM-04 | FACT |
| TASK-23 | Implement minimal building/device placement | P0 | U1 | Codex | Lua prefabs, ECS, client UI | Building spec | Place generator/consumer/cable/building | Implement after data loading | WORKSTREAM-07 | FACT |
| TASK-24 | Implement minimal HUD/hotbar/selection | P1 | U1 | Codex | Client loop, render/UI | MVP UI needs | Tick/hash/status/hotbar/inspector | Implement thin UI | WORKSTREAM-18 | FACT |
| TASK-25 | Implement one transport segment and vehicle | P1 | U1 | Codex | Path/physics/render | Pick rail/road | Deterministic vehicle movement | Choose simplest mode | WORKSTREAM-10 | FACT |
| TASK-26 | Implement minimal save/load roundtrip | P1 | U2 | Codex | Serializer, world state | DATA_FORMATS | Save/load same hash | Implement after serializer | WORKSTREAM-16 | FACT |
| TASK-27 | Stub terrain cut/fill fields | P1 | U2 | Codex | Spatial/chunk | Terrain design | Base terrain + ΔH/cavity placeholders | Implement flat terrain first | WORKSTREAM-06 | FACT |
| TASK-28 | Keep multiplayer as stub/future | P2 | U2 | Codex/User | Core/net | Roadmap | No premature multiplayer complexity | Do not implement live MP yet | WORKSTREAM-21 | FACT |
| TASK-29 | Keep space/Sol/orbital as stub/future | P2 | U2 | Codex/User | Core/spatial | Roadmap | No premature space implementation | Preserve design only | WORKSTREAM-12 | FACT |
| TASK-30 | Defer textures/audio/music/extra renderers | P2 | U2 | Codex/User | MVP scope | Roadmap | No asset dependency in MVP | Use vector/null audio | WORKSTREAM-22 | FACT |
| TASK-31 | Legal-review restrictive LICENCE.md | P1 | U2 | User/legal | Licence draft | Legal expertise | Valid restrictive licence | Seek review before public release | WORKSTREAM-20 | UNCERTAIN / UNVERIFIED |
| TASK-32 | Verify DirectX9/Win2000/SDK compatibility | P1 | U1 | User/Codex | External docs | DX9/Win2000 info | Confirmed viable platform target | Research/test | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| TASK-33 | Verify Lua 5.4.4 old compiler portability | P1 | U1 | User/Codex | Lua source, toolchains | Compiler tests | Confirmed or patched Lua | Test build | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| TASK-34 | Finalize DomDrawCmd/camera API | P0 | U1 | User/Codex | Addendum, DATA_FORMATS | Render API choices | Consistent render header | Resolve before DX9 implementation | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |

### Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Simulation must be deterministic for identical inputs/version. | technical | hard | V3/SPEC_CORE | All state order fixed; no nondeterminism. | Desync, invalid replays. | FACT | high |
| CONSTRAINT-02 | No floating point in authoritative simulation. | technical | hard | Repeated specs | Use integer/fixed-point only. | Cross-platform divergence. | FACT | high |
| CONSTRAINT-03 | /engine/core and /engine/sim must be C89. | technical | hard | BUILDING/CONTRIBUTING | Preserve retro/old compiler compatibility. | Build incompatibility. | FACT | high |
| CONSTRAINT-04 | Non-core engine/game may use C++98 max, no newer features. | technical | hard | BUILDING/CONTRIBUTING | Avoid modern language dependence. | Toolchain mismatch. | FACT | high |
| CONSTRAINT-05 | No OS headers outside /engine/platform or /ports. | technical/architecture | hard | DIRECTORY_CONTEXT/Addendum | Keep platform isolation. | Layer contamination. | FACT | high |
| CONSTRAINT-06 | No graphics headers/calls outside /engine/render. | technical/architecture | hard | Addendum | Keep renderer isolation. | GPU API leakage. | FACT | high |
| CONSTRAINT-07 | Codex must use only listed files/context. | process | hard | User statement | Avoid hallucinated context. | Wrong docs/code. | FACT | high |
| CONSTRAINT-08 | World mutations go through command buffers/deferred phases. | technical | hard | V3/Jobs/ECS | Safe deterministic mutation. | Mid-tick inconsistency. | FACT | high |
| CONSTRAINT-09 | No direct global writes from virtual lanes. | technical | hard | V3 determinism | Lane-local then merge. | Race/order bugs. | FACT | high |
| CONSTRAINT-10 | Binary formats little-endian; no pointers; no floats. | data | hard | DATA_FORMATS | Portable save/network. | Unreadable/incompatible saves. | FACT | high |
| CONSTRAINT-11 | No new top-level dirs unless DIRECTORY_CONTEXT updated. | process/directory | hard | Directory contract | Controlled structure. | Repo sprawl. | FACT | high |
| CONSTRAINT-12 | Use actual file names from user tree. | process/directory | hard | User tree | Avoid broken references. | Broken docs/Codex. | FACT | high |
| CONSTRAINT-13 | Lua script sandbox disables OS/time/native access. | security/technical | hard | Lua clarification | Protect determinism/security. | Sandbox escape/desync. | FACT | high |
| CONSTRAINT-14 | Lua may mutate sim only through deterministic engine APIs/commands. | technical | hard | Lua clarification | Preserve tick/order. | Undocumented state changes. | FACT | high |
| CONSTRAINT-15 | No dense full surface allocation. | resource/technical | hard | Spatial discussion | Use sparse chunks/microgrids. | Memory explosion. | FACT | high |
| CONSTRAINT-16 | Base game MVP uses one Earth surface. | scope | hard | User MVP | Keep scope bounded. | Multiworld scope creep. | FACT | high |
| CONSTRAINT-17 | Base terrain immutable. | technical | hard | Cut/fill discussion | Earthworks overlay base. | Loss of original terrain. | FACT | high |
| CONSTRAINT-18 | Structural microgrids separate from terrain. | technical | hard | Cut/fill discussion | Over/under structures remain distinct. | Terrain/structure conflation. | FACT | high |
| CONSTRAINT-19 | Blocks/modules are sim truth for structures. | technical | hard | Building decision | Deterministic structure/path/pressure. | Continuous geometry complexity. | FACT | high |
| CONSTRAINT-20 | Doors/devices must be explicitly placed fixtures. | user preference/technical | hard | User statement | No automatic doors. | Unwanted doors/type bloat. | FACT | high |
| CONSTRAINT-21 | Buildings rigid for MVP, but data future-proofs collapse. | scope/technical | hard | User statement | Avoid collapse implementation now. | MVP creep or incompatible data. | FACT | high |
| CONSTRAINT-22 | Splines are baked to discrete chainpoints for runtime. | technical | hard | Spline discussion | Runtime deterministic cells/graphs. | Runtime curve complexity. | FACT | high |
| CONSTRAINT-23 | Connections occur at explicit graph nodes. | technical | hard | Way connectivity discussion | Topology stable. | Mid-edge graph ambiguity. | FACT | medium-high |
| CONSTRAINT-24 | Networks deterministic, fixed capacity/latency/ordering. | technical | hard | Network specs | No random loss/ordering. | Desync. | FACT | high |
| CONSTRAINT-25 | Renderer/platform mix-and-match via APIs/vtables. | architecture | hard | User rollout/addendum | Extensible backend matrix. | Hardcoded backend coupling. | FACT | high |
| CONSTRAINT-26 | Cross-surface interactions async only. | architecture | hard | Sharding discussion | Surface isolation. | Cross-shard desync. | FACT | medium-high |
| CONSTRAINT-27 | MVP vector-only, textures/audio later. | scope | hard | User MVP | No asset blockers. | Scope creep. | FACT | high |
| CONSTRAINT-28 | All systems interactable in MVP via minimal prototypes. | scope | hard | User MVP | Thin systems, not full simulation. | Either too narrow or too broad. | FACT | high |
| CONSTRAINT-29 | Unknown binary blocks skippable. | data compatibility | hard | DATA_FORMATS | Forward compatibility. | Future format breakage. | FACT | high |
| CONSTRAINT-30 | No hash tables serialized directly; sorted lists only. | data/determinism | hard | DATA_FORMATS | Deterministic serialization. | Ordering mismatch. | FACT | high |
| CONSTRAINT-31 | FNV hash over authoritative state only. | testing | hard | Hash clarification | Stable determinism testing. | False positives/negatives. | FACT | high |
| CONSTRAINT-32 | CMake explicit file lists; no globbing. | build | hard | BUILDING | Deterministic sources. | Accidental files included. | FACT | high |
| CONSTRAINT-33 | Retro builds isolated under /ports. | build/platform | hard | BUILDING/ports | Modern CMake not contaminated. | Toolchain sprawl. | FACT | high |
| CONSTRAINT-34 | Licence restrictive except personal use/source viewing. | legal/user preference | hard intent | User request | Distribution restrictions. | Licence intent violated. | FACT | medium |
| CONSTRAINT-35 | No textures/sounds/music required in MVP. | scope/resource | hard | User statement | Vector/null audio initially. | Asset bottleneck. | FACT | high |
| CONSTRAINT-36 | Tests must avoid OS randomness/wallclock dependencies. | testing | hard | Tests dev spec | Cross-platform validation. | Flaky tests. | FACT | high |

### Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | What would resolve it | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Have V4 docs been applied to the actual repository? | Codex state depends on disk contents. | Generated V4 docs exist in chat. | On-disk state unknown. | Inspect repo files. | P0 | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | Does the actual repo contain /engine, /game, /data etc. yet? | Determines whether Codex creates dirs or edits existing. | User tree showed only root/docs. | Actual filesystem unknown. | Codex/file inspection. | P0 | WORKSTREAM-17 | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | Should docs root remain flat or use /docs/spec? | Old and new docs differ. | User tree has docs root files. | Final organization unclear if future moves planned. | Follow current tree or user confirm. | P0 | WORKSTREAM-01 | FACT / UNCERTAIN |
| QUESTION-04 | How to reconcile Lua-for-all-data with JSON-oriented DATA_FORMATS sections? | Affects data loader and Codex implementation. | User wants Lua MVP; DATA_FORMATS includes JSON/mod schema. | Final long-term policy. | Update DATA_FORMATS/BUILDING or ask user. | P0 | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | What is the final DomDrawCmd/camera API? | DX9 renderer implementation needs exact API. | Addendum and DATA_FORMATS have differing sketches. | Final coordinate/types. | Finalize dom_render_api.h. | P0 | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | Native Win32 or SDL2 first? | Initial platform implementation scope. | User allowed both; assistant recommended Win32 first. | Whether SDL2 is MVP requirement. | Clarify or implement Win32 first with SDL2 optional. | P1 | WORKSTREAM-14 | FACT / INFERENCE |
| QUESTION-07 | Can DX9.0c reliably target Windows 2000 SP4 through Windows 11? | Platform feasibility. | User wants it. | SDK/runtime details. | External verification/test. | P1 | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | Can SDL2 support Windows 2000 target? | If SDL2 is used early. | SDL2 named by user. | Version support. | External verification. | P2 | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| QUESTION-09 | Can Lua 5.4.4 build with old/retro compilers? | Vendor/runtime feasibility. | Assistant recommended 5.4.4. | Portability/patched needs. | Test/verify. | P1 | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | What exact ECS component set is MVP? | Data/scripts/networks need fields. | Transform/occupancy/network/worker/building implied. | Exact fields. | Define minimal component schema. | P0 | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-11 | Which transport mode first for MVP? | Implementation priority. | Need at least one segment/vehicle. | Rail vs road choice. | User or Codex decide simplest. | P1 | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| QUESTION-12 | What does “fully complete core” mean at MVP depth? | Scope control. | All systems interactable minimal. | How thin each system can be. | MVP acceptance checklist. | P0 | WORKSTREAM-18 | UNCERTAIN / UNVERIFIED |
| QUESTION-13 | Do generated root docs like VERSION exist or matter? | Avoid referencing missing files. | VERSION generated earlier; user tree lacks it. | User intent. | Inspect repo/ask if needed. | P2 | WORKSTREAM-20 | UNCERTAIN / UNVERIFIED |
| QUESTION-14 | Is the restrictive licence legally valid? | Release risk. | Draft exists. | Legal enforceability. | Legal review. | P1 | WORKSTREAM-20 | UNCERTAIN / UNVERIFIED |
| QUESTION-15 | Are docs/dev files identical to generated dev specs? | Codex source fidelity. | Names listed. | Contents uninspected. | Inspect files. | P0 | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |

### Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Where it came from | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Referenced ZIP with 17 files | file reference | Existing files from earlier chat | Mentioned, not inspected | User mention | maybe | Visible transcript does not include zip contents. | FACT / UNCERTAIN |
| ARTIFACT-02 | V3 Volume 1A-1 Determinism Kernel Foundations | generated document | Determinism foundations | Visible | Transcribed in chat | yes | Important historical spec. | FACT |
| ARTIFACT-03 | V3 Volume 1A-2 Determinism Pipeline & Parallelism | generated document | Tick/lane/merge/network propagation | Visible | Transcribed | yes | Important historical spec. | FACT |
| ARTIFACT-04 | V3 Volume 1B-1 Core Simulation Architecture | generated document | ECS/entity/component/system model | Visible | Transcribed | yes | Important historical spec. | FACT |
| ARTIFACT-05 | V3 Volume 1B-2a Messaging Architecture | generated document | Events/commands/deferred ops | Visible | Transcribed | yes | Important. | FACT |
| ARTIFACT-06 | V3 Volume 1B-2b Jobs/Interrupts/Routing | generated document | Jobs and task routing | Visible | Transcribed | yes | Important. | FACT |
| ARTIFACT-07 | V3 Volume 1B-3a Serialization/Persistence | generated document | Save/replay/chunks | Visible | Transcribed | yes | Important. | FACT |
| ARTIFACT-08 | V3 Volume 1B-3b Spatial/Physics/Prefabs/Mods | generated document | Spatial/prefab/mod architecture | Visible | Transcribed | yes | Important. | FACT |
| ARTIFACT-09 | Unified Engine Specification outline | framework/plan | 12-section UES plan | Visible | Assistant output | yes | Not full formal spec but useful. | FACT |
| ARTIFACT-10 | Massive unified summary | generated summary | Whole-engine macro summary | Visible | Assistant output | yes | Architecture bridge. | FACT |
| ARTIFACT-11 | Updated world rundown | generated summary | Cosmic/spatial/server/worldgen model | Visible | Assistant output | yes | Use for world model. | FACT |
| ARTIFACT-12 | Surface vs space design answer | generated design | Physical/logical domains and orbits | Visible | Assistant output | yes | Use for future space. | FACT |
| ARTIFACT-13 | Orbital construction answer | generated design | Stations/ships/rockets/pods/tugs | Visible | Assistant output | yes | Future space logistics. | FACT |
| ARTIFACT-14 | Building/cut-fill/spline design answers | generated design | Blocks, fixtures, terrain, corridors | Visible | Assistant output | yes | Core architecture. | FACT |
| ARTIFACT-15 | Five primitives generalization | framework | Unifying systems | Visible | Assistant output | yes | High-value architecture. | FACT |
| ARTIFACT-16 | Full ASCII git directory tree | directory plan | Ideal repo structure | Visible | Assistant output | historical | Superseded by user actual tree. | FACT |
| ARTIFACT-17 | Per-directory dev spec messages | generated specs | Detailed file/API guidance | Visible | Assistant outputs | yes | Likely reflected in docs/dev files. | FACT |
| ARTIFACT-18 | Root docs drafts | generated documents | README, LICENCE, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, .gitignore, CMake, CHANGELOG, BUILDING, VERSION | Visible | Assistant outputs | some | Some may not exist in actual tree. | FACT / UNCERTAIN |
| ARTIFACT-19 | User-provided current directory tree | file tree | Actual current file set for Codex | Visible | User | yes | Highest-priority structure source. | FACT |
| ARTIFACT-20 | BUILDING.md V4 | generated document | Updated build/platform spec | Visible | Assistant after old doc pasted | yes | Apply/verify. | FACT |
| ARTIFACT-21 | SPEC_CORE.md V4 | generated document | Updated core spec | Visible | Assistant after old doc pasted | yes | Apply/verify. | FACT |
| ARTIFACT-22 | DATA_FORMATS.md V4 | generated document | Updated data formats spec | Visible | Assistant after old doc pasted | yes | Apply/verify. | FACT |
| ARTIFACT-23 | DIRECTORY_CONTEXT.md V4 | generated document | Updated directory contract | Visible | Assistant after old doc pasted | yes | Apply/verify. | FACT |
| ARTIFACT-24 | Codex consistency pass prompt | prompt | Ask Codex to reconcile four docs | Visible | Assistant | yes | Immediate use. | FACT |
| ARTIFACT-25 | Codex CMake/build skeleton prompt | prompt | Build system implementation step | Visible | Assistant | yes | Next implementation. | FACT |
| ARTIFACT-26 | Codex core API skeleton prompt | prompt | engine/core skeleton step | Visible | Assistant | yes | Implementation. | FACT |
| ARTIFACT-27 | Codex sim/ECS shell prompt | prompt | Tick/ECS/events/jobs skeleton | Visible | Assistant | yes | Implementation. | FACT |
| ARTIFACT-28 | Codex platform/render shell prompt | prompt | Win32/DX9 vector shell | Visible | Assistant | yes | Implementation. | FACT |
| ARTIFACT-29 | Codex minimal client loop prompt | prompt | MVP loop step | Visible | Assistant | yes | Implementation. | FACT |
| ARTIFACT-30 | Lua clarification answer | implementation decision | /engine/script, Lua 5.4.4, API, FNV hash | Visible | Assistant to Codex question | yes | Essential. | FACT |
| ARTIFACT-31 | OC-1 Discovery Inventory | handoff artifact | Discovery pass inventory | Visible | Assistant | yes | Basis for packet. | FACT |
| ARTIFACT-32 | Partial OC-2 registers | handoff artifact | Structured registers started but superseded | Partial | Assistant | historical | This packet supersedes. | FACT |
| ARTIFACT-33 | Current Context Transfer Packet | handoff report | Maximum-fidelity chat state transfer | Current output | Assistant | yes | Use for next chat. | FACT |

### Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Spec drift across docs/dev files. | Codex implements contradictory architecture. | high | high | Run consistency pass; keep V4 docs canonical. | WORKSTREAM-01 | FACT |
| RISK-02 | Codex invents directories or files outside contract. | Repo sprawl and bad implementation. | medium | high | Prompt scope and DIRECTORY_CONTEXT. | WORKSTREAM-01, WORKSTREAM-22 | FACT |
| RISK-03 | Treating brainstorming as final decisions. | Wrong architecture enters spec. | medium | high | Use labels and user-statement priority. | WORKSTREAM-01 | FACT |
| RISK-04 | Platform/render boundaries blur. | OS/GPU APIs leak into sim/game. | medium | critical | Addendum, BUILDING V4, lint checks. | WORKSTREAM-14 | FACT |
| RISK-05 | Floats enter authoritative simulation through Lua/render/helpers. | Cross-platform desync. | medium | critical | API conversion, no sim floats, tests. | WORKSTREAM-02, WORKSTREAM-15 | FACT |
| RISK-06 | Lua sandbox escape or nondeterministic script behavior. | Security/desync. | medium | critical | Disable OS/native/debug and deterministic RNG. | WORKSTREAM-15 | FACT |
| RISK-07 | Surface/space/cross-surface sync overreach. | Sharding/orbit complexity, desync. | medium | high | Defer space/multiplayer; async only. | WORKSTREAM-12, WORKSTREAM-21 | FACT |
| RISK-08 | DX9/Win2000 target not feasible as assumed. | MVP platform failure. | medium | high | Verify SDK/runtime early. | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| RISK-09 | SDL2 or Lua version incompatible with old targets. | Build/tooling failures. | medium | medium-high | Verify and patch/version-pin. | WORKSTREAM-14, WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| RISK-10 | Canonical hash/serializer includes unstable data or misses authoritative state. | False determinism results. | medium | high | Define serialization order and exclusions. | WORKSTREAM-16 | FACT |
| RISK-11 | MVP scope too broad. | Implementation stalls. | high | high | Minimal prototypes only; defer assets/multiplayer/space. | WORKSTREAM-18 | FACT |
| RISK-12 | Corridor/microgrid overlap ambiguity. | Invalid construction/pathing. | medium | medium-high | Ownership/portal rules. | WORKSTREAM-08 | FACT |
| RISK-13 | Network solver complexity creep. | MVP delay. | medium | medium | Simple power first, fluid/data thin. | WORKSTREAM-09 | INFERENCE |
| RISK-14 | Binary formats too underdefined for Codex. | Serializer guesses layouts. | medium | high | Finalize exact structs for MVP components. | WORKSTREAM-16 | FACT |
| RISK-15 | Sparse/full-size surface overdesign. | Memory/perf or slow implementation. | medium | medium | MVP flat sparse test area with full surface metadata. | WORKSTREAM-05 | INFERENCE |
| RISK-16 | .gitignore/build rules hide needed files. | Missing tracked build configs. | medium | medium | Audit git ignore. | WORKSTREAM-17 | INFERENCE |
| RISK-17 | Actual repo tree differs from generated specs. | Patches fail or create wrong files. | medium | medium | Inspect before applying. | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| RISK-18 | Restrictive licence legally weak. | Legal exposure. | unclear | high | Legal review. | WORKSTREAM-20 | UNCERTAIN / UNVERIFIED |
| RISK-19 | Future cross-server trade/security underspecified. | Cheating/rollback/desync. | medium | high | Future security/net spec. | WORKSTREAM-21 | INFERENCE |

### Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Actual repo file contents and whether V4 docs applied. | Generated docs may not be on disk. | Repo inspection/diff. | P0 | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Actual directory existence under /engine, /game, /data, etc. | User tree only showed root/docs. | Filesystem inspection. | P0 | WORKSTREAM-17 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | DX9.0c support on Windows 2000 SP4 through Windows 11+. | External API/runtime/toolchain fact. | Microsoft/SDK/runtime docs and test build. | P1 | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | SDL2 support for Windows 2000 target. | Version-dependent. | SDL2 docs/build test. | P2 | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Lua 5.4.4 portability to required compilers. | May require shims. | Build/test with target compilers. | P1 | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | Restrictive LICENCE.md legal enforceability. | Legal validity depends on jurisdiction. | Legal review. | P1 | WORKSTREAM-20 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | CMake minimum/toolchains and flags. | External toolchain compatibility. | CMake/compiler docs and build tests. | P2 | WORKSTREAM-17 | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | JSON-vs-Lua data policy. | Docs and MVP may conflict. | User confirmation and doc update. | P0 | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | Final DomDrawCmd/camera API. | Conflicting sketches. | Header design/user confirmation. | P0 | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| VERIFY-10 | Current docs use LICENCE.md and SPEC_CORE.md names consistently. | Name mismatches likely. | Search repo. | P0 | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-11 | .gitignore behaviour. | Could ignore /build/cmake. | git check-ignore tests. | P1 | WORKSTREAM-17 | UNCERTAIN / UNVERIFIED |
| VERIFY-12 | Third-party licence compliance for Lua/LZ4/etc. | Legal/build risk. | Licence audit. | P1 | WORKSTREAM-15, WORKSTREAM-20 | UNCERTAIN / UNVERIFIED |
| VERIFY-13 | OpenGL/Vulkan/future platform support matrices. | External-world/API facts stale. | Official API/platform docs. | P3 | WORKSTREAM-22 | UNCERTAIN / UNVERIFIED |
| VERIFY-14 | Win98 SE DX9/GL1 feasibility. | Historical platform support nuanced. | SDK/runtime tests. | P3 | WORKSTREAM-22 | UNCERTAIN / UNVERIFIED |
| VERIFY-15 | Exact contents of docs/dev/dominium_new_*.txt. | Listed but not inspected. | Read files. | P0 | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |

## 6. Possible Cross-Chat Duplicates

- Rail gauge and rail system design.
- Electrical/data network details.
- Deterministic kernel and ECS volumes.
- Directory and dev-spec generation.
- Building/cut-fill/vector/voxel discussions.
- Renderer/platform backend strategy.

## 7. Possible Cross-Chat Conflicts

- Lua-only MVP data versus JSON or binary data formats in other chats.
- Actual current tree versus idealized repo trees from other chats.
- Render command API floats versus integer draw command serialization.
- Scope of MVP “fully complete core.”
- Initial platform order: native Win32 first versus SDL2-first.

## 8. Spec Book Integration Guidance

- Feed deterministic core into engine kernel chapter.
- Feed spatial ladder and surfaces into world model chapter.
- Feed blocks/faces/edges/fixtures into building/construction chapter.
- Feed corridor baking into transport/infrastructure chapter.
- Feed platform/render split into rendering/platform chapter.
- Feed Codex prompts into implementation roadmap appendix.
- Do not merge future space/multiplayer as MVP requirements.
- Verify all external platform/toolchain/legal facts before final spec book.

## 9. Aggregator Warnings

- Do not erase uncertainty or treat assistant suggestions as direct user decisions.
- Do not assume all generated docs were applied to disk.
- Preserve rejected options; they prevent repeated design loops.
- Treat this chat as high priority for MVP/codegen, not as the entire project.
