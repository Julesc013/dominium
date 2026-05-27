# Full Chat Report — Dominium Architecture II

## 0. Report Metadata

| Field | Assessment |
| --- | --- |
| Chat label | Dominium Architecture II |
| Generated date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | Visible content of this chat only; no Project files or external verification used. |
| Apparent coverage | Partial: visible long transcript plus previous OC-1 and Context Transfer Packet; several early messages were skipped. |
| Extraction confidence | 4/5 |
| Staleness risk | Medium |
| Contains future plans | Yes |
| Contains pending tasks | Yes |
| Contains artifacts/files | Yes |
| Safe for aggregation | Yes, with caveats. |
| Main limitations | Actual repo files not inspected; uploaded ZIP not inspected; external platform/toolchain/legal facts need verification; some generated docs may not be applied on disk. |

## 1. Executive Summary

This chat, **Dominium Architecture II**, is a high-density architecture, specification, and Codex-preparation session for the Dominium engine/game project. It develops a deterministic, modular, multi-scale simulation engine intended to support both retro and modern platforms, with an immediate MVP target and a long-term extensible platform/renderer/data/modding architecture. The most important state to preserve is that Dominium is not merely a game idea; in this chat it was shaped into a tightly constrained deterministic engine architecture with explicit repository contracts and Codex implementation prompts.

The most important user-defined MVP is: a fully complete core; one full-size Earth surface; all systems interactable through minimal data prototypes; Lua for all data; Windows/DX9/Win32/SDL2 path; 2D vector top-down and 3D vector first-person rendering. Textures, sounds, music, multiplayer, the Sol system/space expansion, additional renderers, and additional platforms are post-MVP.

Major architectural choices were fixed. The world uses meters with Q16.16 fixed substeps, not a millimeter base. The spatial ladder is base-16 from subnano to surface, with sparse chunk/microgrid storage rather than a dense planetary grid. The simulation is deterministic, integer/fixed-point, tick-based, C89-compatible in core, and strictly separated from platform and renderer code. The renderer is a pure observer. Platform backends handle OS/window/input/time; renderer backends handle graphics APIs; the sim never includes OS, DirectX, OpenGL, Vulkan, SDL, or other external platform/graphics headers.

The building and infrastructure model was heavily refined. Buildings use blocks/modules/cells/faces/edges as simulation truth, with walls/floors/roofs on grid faces/edges including diagonals. Doors and devices are explicit fixtures on anchors; they must not appear automatically or be hardcoded into every tunnel type. Terrain uses immutable base terrain plus earthworks deltas/cavities and structural microgrids. Vector splines exist as authoring/generation/visual inputs for roads, rails, tunnels, bridges, platforms, and utilities; runtime sim uses deterministic baked chainpoints, linear microgrids, cells, and graphs.

Space was separated from surfaces: surfaces are high-fidelity physical domains, while space is a logical/on-rails domain using orbital rails, transfer nodes, local bubbles for docking/approach, and explicit state-machine transitions for takeoff/landing/docking. Orbital ships/stations/yards, rockets, drop pods, and cargo tugs were designed as future extensions using the same ECS/jobs/inventory/graph primitives.

The chat also generated or updated many project artifacts: root docs, directory contracts, per-directory dev specs, Codex prompts, and V4 replacements for BUILDING.md, SPEC_CORE.md, DATA_FORMATS.md, and DIRECTORY_CONTEXT.md. The user later provided the actual current file tree and explicitly wants Codex 5.1 Max to work only from those files. A key addendum should live at `docs/dev/dominium_new_addendum.txt`.

Open issues remain: actual repo state is unverified; Lua-for-all-data must be reconciled with JSON-oriented data docs; final render command/camera APIs need settling; DX9/Windows 2000 and SDL2 compatibility must be verified; Lua 5.4.4 portability to old compilers must be tested; and the restrictive licence needs legal review.

## 2. How to Use This Report

- FACT: This report covers only the visible content of the old chat labelled **Dominium Architecture II** and the already-produced Context Transfer Packet in that chat.
- FACT: It should not be treated as a whole-Project summary.
- FACT: Uncertain items must not be promoted to facts during future aggregation.
- FACT: Direct user statements outrank assistant suggestions.
- FACT: Assistant suggestions are only final when accepted by the user or clearly continued from by the user.
- FACT: External-world/toolchain/API/legal facts require verification before future use.
- FACT: This report is intended to be combined later with similar reports from other retired chats.

## 3. User Preferences Visible in This Chat

### 3.1 Explicit Preferences

| ID | Preference | Area | Explicit or inferred | Strength | Implication for future assistant | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PREFERENCE-01 | Maximum-fidelity, structured handoff rather than normal summary. | handoff | explicit | strong | Produce exhaustive self-contained reports with labels and IDs. | FACT | high |
| PREFERENCE-02 | No invented facts or silent inference. | reasoning | explicit | strong | Label uncertainties and avoid unsupported claims. | FACT | high |
| PREFERENCE-03 | Preserve rejected/superseded/deprioritised options. | handoff | explicit | strong | Do not erase design history. | FACT | high |
| PREFERENCE-04 | Prioritise direct user statements over assistant suggestions. | reasoning | explicit | strong | Treat suggestions as tentative unless accepted. | FACT | high |
| PREFERENCE-05 | Use Codex with strict scoped prompts. | coding/process | explicit | strong | Prompts must list source files and constraints. | FACT | high |
| PREFERENCE-06 | Detailed architecture/spec outputs, often as long as possible. | length/detail | inferred | strong | Provide comprehensive specs when asked. | INFERENCE | high |
| PREFERENCE-07 | Vector graphics first; textures/sounds/music later. | MVP scope | explicit | strong | Avoid asset work in early implementation. | FACT | high |
| PREFERENCE-08 | Lua for all MVP data. | data/modding | explicit | strong | Implement script/data bridge early. | FACT | high |
| PREFERENCE-09 | Determinism and integer math as non-negotiable. | engineering | explicit | strong | Challenge any float/nondeterministic design. | FACT | high |
| PREFERENCE-10 | Retro and future extensibility kept in architecture even if deferred. | architecture | explicit/inferred | strong | Do not hardcode MVP-only assumptions. | INFERENCE | high |
| PREFERENCE-11 | Restrictive licensing. | legal | explicit | strong | Docs/licence should enforce source-view/personal-use only. | FACT | medium |
| PREFERENCE-12 | Do not make doors auto-appear; arbitrary explicit placement. | building UX | explicit | strong | Use fixture/anchor system. | FACT | high |
| PREFERENCE-13 | Use real file tree and avoid phantom files. | repo/process | explicit | strong | References must match listed paths. | FACT | high |

### 3.2 Inferred Preferences

INFERENCE: The user prefers durable, exhaustive, highly structured architecture documents and strict Codex prompts. This is inferred from repeated requests for maximum-length specs, per-directory dev specs, and anti-invention handoff packets.

### 3.3 Preferences Not Established by This Chat

- UNCERTAIN / UNVERIFIED: Preferred final legal jurisdiction for the restrictive licence.
- UNCERTAIN / UNVERIFIED: Whether the user wants long-term data to remain Lua-only or merely MVP Lua-first.
- UNCERTAIN / UNVERIFIED: Whether SDL2 must be implemented in the first Windows MVP pass or can wait until after native Win32+DX9.

## 4. Complete Topic and Workstream Inventory

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Unified documentation/source-of-truth | Consolidate architecture and Codex-facing instructions into a coherent source of truth. | V4 replacements for BUILDING.md, SPEC_CORE.md, DATA_FORMATS.md, and DIRECTORY_CONTEXT.md were generated in this chat; actual on-disk application is unverified. | The four docs plus docs/dev/dominium_new_addendum.txt consistently guide Codex without contradictions. | active | P0 | high | FACT |
| WORKSTREAM-02 | Deterministic core/kernel | Implement the deterministic C89 simulation kernel. | Detailed V3 determinism material and SPEC_CORE V4 exist as visible design outputs. | A ticking deterministic core with fixed phases, lanes, merge, fixed-point math, and no sim floats. | active | P0 | high | FACT |
| WORKSTREAM-03 | ECS architecture | Define and implement deterministic entity/component/system architecture. | V3 1B material and engine/ecs dev spec were generated. | Stable entity IDs/generations, POD components, dense arrays, sorted active lists, deterministic iteration. | active | P0 | high | FACT |
| WORKSTREAM-04 | Messaging, events, jobs | Provide deterministic event buses, command buffers, jobs, deferred ops and interrupts. | V3 1B-2a/b visible and sim dev spec generated. | Fixed-size queues, deterministic ordering, one-tick cross-lane/global latency, job assignment with stable tie-breaks. | active | P0 | high | FACT |
| WORKSTREAM-05 | Spatial hierarchy and cosmic identity | Define coordinates, scale ladder, sparse chunking, and universe/galaxy/system/planet/surface IDs. | User fixed the scale ladder and defaults; SPEC_CORE/DATA_FORMATS were updated around it. | Single Earth surface MVP with full hierarchy capability and sparse chunks/microgrids. | active | P0 | high | FACT |
| WORKSTREAM-06 | Terrain, cut/fill, and microgrids | Support terrain edits, underground/overground structures, and logical separation from base terrain. | Three-layer model established: immutable base terrain, earthworks deltas/cavities, structural microgrids. | Flat MVP surface with future-ready cut/fill/cavity hooks. | active | P1 | high | FACT |
| WORKSTREAM-07 | Building system: cells, faces, edges, fixtures | Use a unified building system for surface, underground and orbital structures. | Blocks/modules/cells/faces/edges model and explicit fixture/anchor system defined. | MVP can place functional blocks/devices and simple walls/floors; future supports collapse/destruction. | active | P0 | high | FACT |
| WORKSTREAM-08 | Vector corridor/spline infrastructure | Support arbitrary vector splines for roads, rails, tunnels, bridges, platforms and utilities. | Alignment-to-chainpoint-to-linear-microgrid pipeline defined; full implementation deferred beyond minimal MVP. | Data-driven corridor archetypes, fixtures/anchors, bridge/tunnel/cut/fill generation, node topology. | active/future | P1 | high | FACT |
| WORKSTREAM-09 | Utility networks: power, data, fluids, thermal | Graph/field utility systems for machines and infrastructure. | Power/data/fluid/thermal network specs generated; MVP requires minimal interactive prototypes. | Power gen/load works first; fluid/data minimal snapshots; thermal may be stubbed. | active | P0/P1 | high | FACT |
| WORKSTREAM-10 | Transport systems | Represent rail, road, water, air and space movement as graphs/corridors/fields. | Generalized design exists; MVP only needs one minimal transport segment/vehicle. | Unified transport graph with modes, vehicles, stations, signals, bridges/tunnels. | active/future | P1 | medium-high | FACT |
| WORKSTREAM-11 | Pathfinding and deterministic movement | Deterministic path and vehicle/worker movement primitives. | Engine/path and engine/physics dev specs generated; no code confirmed. | Integer A*/routing and simple kinematics suitable for workers/vehicles/corridors. | active | P1 | medium-high | FACT |
| WORKSTREAM-12 | Surface vs space and orbital systems | Separate high-resolution surface sim from logical on-rails space sim. | Design defined, post-MVP. | Orbit rails, SOI, Lagrange points, belts/clouds/EM fields, local bubbles, docking transitions. | future | P2 | high | FACT |
| WORKSTREAM-13 | Orbital construction/logistics | Support construction and servicing of orbital ships/stations. | Conceptual design defined, not MVP. | Orbital yards/stations/ships serviced by rockets/drop pods/cargo tugs. | future | P2 | high | FACT |
| WORKSTREAM-14 | Renderer/platform mix-and-match | Cleanly separate OS/platform and renderer backends and allow cross-product selection. | Addendum and BUILDING V4 specify platform API, renderer API, backend registry, DX9 MVP. | Win32+DX9 MVP; later SDL2/DX11/GL/VK/DX12/Linux/macOS/retro.  | active | P0 | high | FACT |
| WORKSTREAM-15 | Lua data and script binding | Enable Lua-driven data prototypes and sandboxed script interaction. | Codex clarification answered: /engine/script, Lua 5.4.4, API namespaces and sandbox. | Lua loads data/prefabs/jobs/net snapshots through safe deterministic engine APIs. | active | P0 | high | FACT |
| WORKSTREAM-16 | Serialization, save/replay, state hash | Persist and hash authoritative state deterministically. | DATA_FORMATS V4 generated; FNV-1a hash rule clarified. | Canonical serialization buffer for save/load/replay/hash, FNV-1a tick hash tests. | active | P0 | high | FACT |
| WORKSTREAM-17 | Build system and CMake | Create deterministic modular CMake build and stubs. | BUILDING V4 and root CMake draft/prompt exist; actual applied state unknown. | Root and per-dir CMake with explicit file lists, DR mode, MVP backend flags. | active | P0 | high | FACT |
| WORKSTREAM-18 | MVP client loop and UI/HUD | Produce a playable vector-only minimal loop. | Prompt generated for minimal client loop; no code confirmed. | 2D/3D camera, tick loop, vector rendering, selection/placement UI, minimal HUD. | active | P0/P1 | high | FACT |
| WORKSTREAM-19 | Testing and CI | Validate determinism and prevent regressions. | Tests dev spec generated; FNV tick+hash test planned. | Unit, integration, replay, perf tests; CI boundary checks. | active | P0/P1 | high | FACT |
| WORKSTREAM-20 | Legal/governance docs | Provide restrictive project governance, licence, contribution and security docs. | Drafts generated for README, LICENCE, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, CHANGELOG, .gitignore, etc. | Consistent, legally reviewed governance docs. | active draft | P1 | medium | FACT |
| WORKSTREAM-21 | Future multiplayer and server universe | Add deterministic multiplayer, server/shard interaction and cross-server trade/communication. | Planned after MVP; net protocol/dev specs exist conceptually. | Lockstep or server-authoritative multiplayer with async cross-surface interactions. | future | P2 | medium-high | FACT |
| WORKSTREAM-22 | Future platforms/renderers/assets | Add non-MVP renderers/platforms/textures/audio/music. | Roadmap defined; implementation deferred. | DX11/GL1/GL2/VK1/DX12, Windows 98, Linux/macOS, retro, textures/audio/music packs. | future | P2/P3 | medium-high | FACT |

## 5. Detailed Workstream State

### WORKSTREAM-01 — Unified documentation/source-of-truth
- Label: FACT
- Objective: Consolidate architecture and Codex-facing instructions into a coherent source of truth.
- Background: The chat identified spec drift from earlier generated volumes and moved toward binding docs and codegen addenda.
- Current state: V4 replacements for BUILDING.md, SPEC_CORE.md, DATA_FORMATS.md, and DIRECTORY_CONTEXT.md were generated in this chat; actual on-disk application is unverified.
- Desired end state: The four docs plus docs/dev/dominium_new_addendum.txt consistently guide Codex without contradictions.
- Importance: Blocks reliable implementation and future aggregation.
- Decisions made:
- docs/dev/dominium_new_addendum.txt is the addendum location, not a new CODEGEN_ADDENDUM.md.
- Actual user-provided file names and tree win over earlier generic names.
- Decisions pending:
- Verify whether generated V4 docs were applied to disk.
- Reconcile any lingering references to /docs/spec if the actual tree has docs root files.
- Pending tasks: TASK-01, TASK-02, TASK-03, TASK-04, TASK-05
- Constraints: CONSTRAINT-07, CONSTRAINT-11, CONSTRAINT-12
- Dependencies: ARTIFACT-19, ARTIFACT-20, ARTIFACT-21, ARTIFACT-22, ARTIFACT-23
- Timeline / sequencing: Immediate, before Codex implementation.
- Blockers:
- Actual repo state unknown.
- Risks: RISK-01, RISK-02
- Artifacts: ARTIFACT-19, ARTIFACT-20, ARTIFACT-21, ARTIFACT-22, ARTIFACT-23
- Success criteria:
- Four key docs align with actual file tree and dev addenda.
- Recommended next action: Run the Codex consistency pass or manually verify the four docs.
- Verification needed: See verification queue where applicable.
- Confidence: high
- Carry-forward priority: P0

### WORKSTREAM-02 — Deterministic core/kernel
- Label: FACT
- Objective: Implement the deterministic C89 simulation kernel.
- Background: The project identity is deterministic simulation across modern and retro systems.
- Current state: Detailed V3 determinism material and SPEC_CORE V4 exist as visible design outputs.
- Desired end state: A ticking deterministic core with fixed phases, lanes, merge, fixed-point math, and no sim floats.
- Importance: Foundational for everything else.
- Decisions made:
- No floats in /engine/core or /engine/sim.
- Seven-phase tick pipeline.
- Simulation slows rather than skipping ticks.
- Decisions pending:
- Exact C API function signatures during implementation.
- Pending tasks: TASK-06, TASK-07, TASK-17
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-03, CONSTRAINT-04
- Dependencies: WORKSTREAM-03, WORKSTREAM-16
- Timeline / sequencing: First implementation after docs/build skeleton.
- Blockers:
- None established in this chat.
- Risks: RISK-05, RISK-10
- Artifacts: WORKSTREAM-03, WORKSTREAM-16
- Success criteria:
- Headless world ticks deterministically and hashes reproduce.
- Recommended next action: Generate engine/core skeletons and sim tick/ECS shell.
- Verification needed: See verification queue where applicable.
- Confidence: high
- Carry-forward priority: P0

### WORKSTREAM-03 — ECS architecture
- Label: FACT
- Objective: Define and implement deterministic entity/component/system architecture.
- Background: All simulation objects, buildings, workers, vehicles, networks, fixtures and devices depend on ECS.
- Current state: V3 1B material and engine/ecs dev spec were generated.
- Desired end state: Stable entity IDs/generations, POD components, dense arrays, sorted active lists, deterministic iteration.
- Importance: Core substrate.
- Decisions made:
- Entity handle is ID plus generation.
- Components are POD with fixed layout.
- Structural changes deferred to command buffers and merge.
- Decisions pending:
- Final component set and exact field names for MVP.
- Pending tasks: TASK-07, TASK-18
- Constraints: CONSTRAINT-06, CONSTRAINT-09
- Dependencies: WORKSTREAM-02, WORKSTREAM-04
- Timeline / sequencing: Early implementation.
- Blockers:
- None established in this chat.
- Risks: RISK-10, RISK-17
- Artifacts: WORKSTREAM-02, WORKSTREAM-04
- Success criteria:
- Entity/component operations deterministic and serializable.
- Recommended next action: Implement ECS shell with deterministic tests.
- Verification needed: See verification queue where applicable.
- Confidence: high
- Carry-forward priority: P0

### WORKSTREAM-04 — Messaging, events, jobs
- Label: FACT
- Objective: Provide deterministic event buses, command buffers, jobs, deferred ops and interrupts.
- Background: Needed for construction, workers, devices, networks and Lua command orchestration.
- Current state: V3 1B-2a/b visible and sim dev spec generated.
- Desired end state: Fixed-size queues, deterministic ordering, one-tick cross-lane/global latency, job assignment with stable tie-breaks.
- Importance: Core process layer.
- Decisions made:
- Queue overflow deterministic oldest-drop plus flag.
- Jobs assigned deterministically.
- Commands mutate world only at safe phases.
- Decisions pending:
- MVP job type enum and minimal worker tasks.
- Pending tasks: TASK-07, TASK-22
- Constraints: CONSTRAINT-08, CONSTRAINT-09
- Dependencies: WORKSTREAM-03
- Timeline / sequencing: Early implementation.
- Blockers:
- None established in this chat.
- Risks: RISK-05, RISK-10
- Artifacts: WORKSTREAM-03
- Success criteria:
- Command emitted during sim applies in merge; worker can perform a fixed job.
- Recommended next action: Implement event/job skeletons and minimal worker job prototype.
- Verification needed: See verification queue where applicable.
- Confidence: high
- Carry-forward priority: P0

### WORKSTREAM-05 — Spatial hierarchy and cosmic identity
- Label: FACT
- Objective: Define coordinates, scale ladder, sparse chunking, and universe/galaxy/system/planet/surface IDs.
- Background: The engine must support full-size planetary surfaces without dense global arrays.
- Current state: User fixed the scale ladder and defaults; SPEC_CORE/DATA_FORMATS were updated around it.
- Desired end state: Single Earth surface MVP with full hierarchy capability and sparse chunks/microgrids.
- Importance: World representation foundation.
- Decisions made:
- Subnano through Surface base-16 ladder.
- Default Earth/Sol/Milky Way.
- Base game starts with one surface.
- Decisions pending:
- Exact packed CosmicKey/hash/text representation.
- Pending tasks: TASK-19
- Constraints: CONSTRAINT-15, CONSTRAINT-16
- Dependencies: WORKSTREAM-06, WORKSTREAM-16
- Timeline / sequencing: MVP needs one Earth surface; multi-surface later.
- Blockers:
- None established in this chat.
- Risks: RISK-15
- Artifacts: WORKSTREAM-06, WORKSTREAM-16
- Success criteria:
- World coords/chunks map deterministically and save metadata is stable.
- Recommended next action: Implement constants and single-surface sparse chunk roots.
- Verification needed: See verification queue where applicable.
- Confidence: high
- Carry-forward priority: P0

### WORKSTREAM-06 — Terrain, cut/fill, and microgrids
- Label: FACT
- Objective: Support terrain edits, underground/overground structures, and logical separation from base terrain.
- Background: Needed for tunnels, basements, canals, bridges and future collapse/subsidence.
- Current state: Three-layer model established: immutable base terrain, earthworks deltas/cavities, structural microgrids.
- Desired end state: Flat MVP surface with future-ready cut/fill/cavity hooks.
- Importance: Core world/building integration.
- Decisions made:
- Base terrain immutable.
- Earthworks are deltas: H_eff = H_base + ΔH.
- Structures are separate microgrids.
- Decisions pending:
- Exact minimal data fields for MVP terrain/chunk storage.
- Pending tasks: TASK-19, TASK-27
- Constraints: CONSTRAINT-17, CONSTRAINT-18
- Dependencies: WORKSTREAM-05, WORKSTREAM-07
- Timeline / sequencing: MVP can stub complex terrain with flat Earth surface.
- Blockers:
- None established in this chat.
- Risks: RISK-15, RISK-17
- Artifacts: WORKSTREAM-05, WORKSTREAM-07
- Success criteria:
- Structures and earthworks can serialize separately from base terrain.
- Recommended next action: Implement flat heightfield plus delta/cavity placeholders.
- Verification needed: See verification queue where applicable.
- Confidence: high
- Carry-forward priority: P1

### WORKSTREAM-07 — Building system: cells, faces, edges, fixtures
- Label: FACT
- Objective: Use a unified building system for surface, underground and orbital structures.
- Background: User wanted blocks for structural/functional components and walls/floors/roofs between metre-grid blocks.
- Current state: Blocks/modules/cells/faces/edges model and explicit fixture/anchor system defined.
- Desired end state: MVP can place functional blocks/devices and simple walls/floors; future supports collapse/destruction.
- Importance: Core gameplay construction.
- Decisions made:
- Blocks/modules are sim truth.
- Walls/floors/roofs on faces/edges, including diagonals.
- Doors/devices are explicit fixtures; no automatic doors.
- Decisions pending:
- Exact component structures and Lua prefab fields.
- Pending tasks: TASK-15, TASK-20, TASK-21
- Constraints: CONSTRAINT-19, CONSTRAINT-20, CONSTRAINT-21
- Dependencies: WORKSTREAM-03, WORKSTREAM-06, WORKSTREAM-15
- Timeline / sequencing: MVP functional placement first; destruction/collapse later.
- Blockers:
- Lua data schema not finalized.
- Risks: RISK-11, RISK-17
- Artifacts: WORKSTREAM-03, WORKSTREAM-06, WORKSTREAM-15
- Success criteria:
- User can place and inspect minimal structures/devices.
- Recommended next action: Define minimal prefab schema and place generator/consumer/cable/building blocks.
- Verification needed: See verification queue where applicable.
- Confidence: high
- Carry-forward priority: P0

### WORKSTREAM-08 — Vector corridor/spline infrastructure
- Label: FACT
- Objective: Support arbitrary vector splines for roads, rails, tunnels, bridges, platforms and utilities.
- Background: User asked how to handle long stations, tunnels, bridges, doors/utilities, overlapping microgrids, grades/cliffs.
- Current state: Alignment-to-chainpoint-to-linear-microgrid pipeline defined; full implementation deferred beyond minimal MVP.
- Desired end state: Data-driven corridor archetypes, fixtures/anchors, bridge/tunnel/cut/fill generation, node topology.
- Importance: Transport and infrastructure backbone.
- Decisions made:
- Splines are authoring metadata; runtime uses baked chainpoints/cells/graphs.
- Corridors use archetypes+instances.
- Doors/utilities are fixtures/patterns only when explicitly placed.
- Decisions pending:
- Exact algorithm/data schema for corridor baking and overlaps.
- Pending tasks: TASK-25
- Constraints: CONSTRAINT-22, CONSTRAINT-23
- Dependencies: WORKSTREAM-06, WORKSTREAM-07, WORKSTREAM-10
- Timeline / sequencing: Minimal straight segment for MVP; full splines later.
- Blockers:
- None established in this chat.
- Risks: RISK-12, RISK-15
- Artifacts: WORKSTREAM-06, WORKSTREAM-07, WORKSTREAM-10
- Success criteria:
- A vehicle can move deterministically along a simple segment; full corridor generator remains spec-ready.
- Recommended next action: Implement simplest straight corridor/vehicle path only in MVP.
- Verification needed: See verification queue where applicable.
- Confidence: high
- Carry-forward priority: P1

### WORKSTREAM-09 — Utility networks: power, data, fluids, thermal
- Label: FACT
- Objective: Graph/field utility systems for machines and infrastructure.
- Background: Earlier chats discussed electrical phases, voltages, data networks and utilities; SPEC_CORE includes network core.
- Current state: Power/data/fluid/thermal network specs generated; MVP requires minimal interactive prototypes.
- Desired end state: Power gen/load works first; fluid/data minimal snapshots; thermal may be stubbed.
- Importance: MVP all-systems interaction.
- Decisions made:
- Power balances generation/load per connected component.
- Data packets/signals one hop/tick.
- Fluids deterministic pressure/flow graph.
- Decisions pending:
- Exact MVP network component fields and Lua definitions.
- Pending tasks: TASK-20, TASK-21
- Constraints: CONSTRAINT-05, CONSTRAINT-24
- Dependencies: WORKSTREAM-03, WORKSTREAM-16, WORKSTREAM-15
- Timeline / sequencing: Power first in MVP, fluid/data thinner. 
- Blockers:
- Component/data schema.
- Risks: RISK-13
- Artifacts: WORKSTREAM-03, WORKSTREAM-16, WORKSTREAM-15
- Success criteria:
- Power status visibly updates and hashes deterministically.
- Recommended next action: Implement generator-consumer-cable power prototype.
- Verification needed: See verification queue where applicable.
- Confidence: high
- Carry-forward priority: P0/P1

### WORKSTREAM-10 — Transport systems
- Label: FACT
- Objective: Represent rail, road, water, air and space movement as graphs/corridors/fields.
- Background: Long early discussion covered rail gauges/traction, roads, waterways, airways, spaceways.
- Current state: Generalized design exists; MVP only needs one minimal transport segment/vehicle.
- Desired end state: Unified transport graph with modes, vehicles, stations, signals, bridges/tunnels.
- Importance: Core gameplay expansion; MVP prototype requirement.
- Decisions made:
- Topology connects at nodes; mid-edge connection creates/splits nodes.
- Rail/road etc. map to graph/corridor primitives.
- Decisions pending:
- Which transport mode first for MVP (rail or road).
- Pending tasks: TASK-25
- Constraints: CONSTRAINT-22, CONSTRAINT-28
- Dependencies: WORKSTREAM-08, WORKSTREAM-11
- Timeline / sequencing: MVP minimal; full multimodal later.
- Blockers:
- Path/physics/corridor APIs.
- Risks: RISK-11
- Artifacts: WORKSTREAM-08, WORKSTREAM-11
- Success criteria:
- Vehicle moves visibly and deterministically.
- Recommended next action: Pick rail or road and implement a straight segment with one deterministic vehicle.
- Verification needed: See verification queue where applicable.
- Confidence: medium-high
- Carry-forward priority: P1

### WORKSTREAM-11 — Pathfinding and deterministic movement
- Label: FACT
- Objective: Deterministic path and vehicle/worker movement primitives.
- Background: Needed for workers, roads/rails, grades, slopes, tunnels, bridges.
- Current state: Engine/path and engine/physics dev specs generated; no code confirmed.
- Desired end state: Integer A*/routing and simple kinematics suitable for workers/vehicles/corridors.
- Importance: MVP worker and transport prototypes.
- Decisions made:
- A* deterministic tie-breaking.
- Runtime movement uses discrete/chain constraints.
- Decisions pending:
- Exact path API and component integration.
- Pending tasks: TASK-22, TASK-25
- Constraints: CONSTRAINT-22, CONSTRAINT-02
- Dependencies: WORKSTREAM-03, WORKSTREAM-05, WORKSTREAM-08
- Timeline / sequencing: Minimal worker path and vehicle line follow in MVP.
- Blockers:
- None established in this chat.
- Risks: RISK-10, RISK-12
- Artifacts: WORKSTREAM-03, WORKSTREAM-05, WORKSTREAM-08
- Success criteria:
- Worker reaches target reproducibly.
- Recommended next action: Implement grid/straight-line path stub sufficient for one worker/job. 
- Verification needed: See verification queue where applicable.
- Confidence: medium-high
- Carry-forward priority: P1

### WORKSTREAM-12 — Surface vs space and orbital systems
- Label: FACT
- Objective: Separate high-resolution surface sim from logical on-rails space sim.
- Background: User asked about space, orbital mechanics, stations, docking, asteroid belts, gas clouds, EM.
- Current state: Design defined, post-MVP.
- Desired end state: Orbit rails, SOI, Lagrange points, belts/clouds/EM fields, local bubbles, docking transitions.
- Importance: Major future expansion.
- Decisions made:
- Use on-rails orbital mechanics.
- Local bubbles for docking/approach.
- Discrete domain transitions.
- Decisions pending:
- Exact orbital data format/API.
- Pending tasks: TASK-29
- Constraints: CONSTRAINT-26
- Dependencies: WORKSTREAM-05, WORKSTREAM-16
- Timeline / sequencing: After MVP core/multiplayer maybe.
- Blockers:
- Core surface MVP first.
- Risks: RISK-07
- Artifacts: WORKSTREAM-05, WORKSTREAM-16
- Success criteria:
- Later Sol system can be added without rewriting core.
- Recommended next action: Keep stubs only; do not implement in MVP. 
- Verification needed: See verification queue where applicable.
- Confidence: high
- Carry-forward priority: P2

### WORKSTREAM-13 — Orbital construction/logistics
- Label: FACT
- Objective: Support construction and servicing of orbital ships/stations.
- Background: User explicitly asked to support orbital ships/stations serviced from surfaces and between orbital objects.
- Current state: Conceptual design defined, not MVP.
- Desired end state: Orbital yards/stations/ships serviced by rockets/drop pods/cargo tugs.
- Importance: Space expansion gameplay.
- Decisions made:
- Stations/ships/yards are ECS entities.
- Rockets/drop pods bridge surface-orbit.
- Tugs are orbital worker/vehicle jobs.
- Decisions pending:
- Docking/inventory/module schemas.
- Pending tasks: TASK-29
- Constraints: CONSTRAINT-26
- Dependencies: WORKSTREAM-12, WORKSTREAM-04, WORKSTREAM-07
- Timeline / sequencing: Post-MVP space phase.
- Blockers:
- Orbital domain not implemented.
- Risks: RISK-07
- Artifacts: WORKSTREAM-12, WORKSTREAM-04, WORKSTREAM-07
- Success criteria:
- Orbital construction uses same building/job systems.
- Recommended next action: Preserve design, defer implementation.
- Verification needed: See verification queue where applicable.
- Confidence: high
- Carry-forward priority: P2

### WORKSTREAM-14 — Renderer/platform mix-and-match
- Label: FACT
- Objective: Cleanly separate OS/platform and renderer backends and allow cross-product selection.
- Background: User explicitly asked to mix and match renderers/platforms with staged rollout.
- Current state: Addendum and BUILDING V4 specify platform API, renderer API, backend registry, DX9 MVP.
- Desired end state: Win32+DX9 MVP; later SDL2/DX11/GL/VK/DX12/Linux/macOS/retro. 
- Importance: Immediate rendering implementation and long-term portability.
- Decisions made:
- MVP Windows NT 2000 SP4 through Windows 11+, DX9.0c.
- Native Win32 first, SDL2 optional/later.
- Renderer pure observer.
- Decisions pending:
- Exact final draw command/camera structs.
- Pending tasks: TASK-08, TASK-09, TASK-34
- Constraints: CONSTRAINT-05, CONSTRAINT-06, CONSTRAINT-25
- Dependencies: WORKSTREAM-17
- Timeline / sequencing: Phase 1 MVP, future backends later.
- Blockers:
- API finalization and external compat verification.
- Risks: RISK-04, RISK-08, RISK-09
- Artifacts: WORKSTREAM-17
- Success criteria:
- Window opens and draws vector grid/crosshair while sim remains isolated.
- Recommended next action: Finalize render API then implement Win32 + DX9 vector shell.
- Verification needed: See verification queue where applicable.
- Confidence: high
- Carry-forward priority: P0

### WORKSTREAM-15 — Lua data and script binding
- Label: FACT
- Objective: Enable Lua-driven data prototypes and sandboxed script interaction.
- Background: User said “Lua for all data.” Codex needed specifics.
- Current state: Codex clarification answered: /engine/script, Lua 5.4.4, API namespaces and sandbox.
- Desired end state: Lua loads data/prefabs/jobs/net snapshots through safe deterministic engine APIs.
- Importance: MVP data and mod future.
- Decisions made:
- Create /engine/script.
- Vendor Lua 5.4.4.
- Expose dom.entity/query/prefab/data/net/jobs/random.
- Disable io/os/unrestricted debug/native modules.
- Decisions pending:
- Exact Lua data table schema.
- Lua-vs-JSON long-term docs.
- Pending tasks: TASK-12, TASK-13, TASK-14, TASK-15, TASK-16, TASK-33
- Constraints: CONSTRAINT-13, CONSTRAINT-14
- Dependencies: WORKSTREAM-03, WORKSTREAM-09, WORKSTREAM-16
- Timeline / sequencing: After minimal core loop but before data prototypes.
- Blockers:
- Directory contract update, Lua vendoring.
- Risks: RISK-05, RISK-06
- Artifacts: WORKSTREAM-03, WORKSTREAM-09, WORKSTREAM-16
- Success criteria:
- Lua data pack loads deterministically and can spawn prefabs via commands.
- Recommended next action: Amend DIRECTORY_CONTEXT and implement VM/sandbox skeleton.
- Verification needed: See verification queue where applicable.
- Confidence: high
- Carry-forward priority: P0

### WORKSTREAM-16 — Serialization, save/replay, state hash
- Label: FACT
- Objective: Persist and hash authoritative state deterministically.
- Background: Needed for determinism, saves, CI, lockstep. 
- Current state: DATA_FORMATS V4 generated; FNV-1a hash rule clarified.
- Desired end state: Canonical serialization buffer for save/load/replay/hash, FNV-1a tick hash tests.
- Importance: Critical validation and future multiplayer.
- Decisions made:
- FNV-1a 64-bit over full authoritative serialized sim state.
- Exclude debug/reconstructable caches.
- Little-endian binary formats; no pointers.
- Decisions pending:
- Exact block/struct layouts for MVP components.
- Pending tasks: TASK-17, TASK-18, TASK-26
- Constraints: CONSTRAINT-10, CONSTRAINT-29, CONSTRAINT-30, CONSTRAINT-31
- Dependencies: WORKSTREAM-02, WORKSTREAM-03, WORKSTREAM-09
- Timeline / sequencing: Implement early even if subsystems stubbed. 
- Blockers:
- State structures finalized enough to serialize.
- Risks: RISK-10, RISK-14
- Artifacts: WORKSTREAM-02, WORKSTREAM-03, WORKSTREAM-09
- Success criteria:
- Headless test emits stable tick/hash pairs.
- Recommended next action: Implement dom_core_hash and canonical serializer skeleton.
- Verification needed: See verification queue where applicable.
- Confidence: high
- Carry-forward priority: P0

### WORKSTREAM-17 — Build system and CMake
- Label: FACT
- Objective: Create deterministic modular CMake build and stubs.
- Background: Codex needs build first before code. 
- Current state: BUILDING V4 and root CMake draft/prompt exist; actual applied state unknown.
- Desired end state: Root and per-dir CMake with explicit file lists, DR mode, MVP backend flags.
- Importance: Implementation bootstrap.
- Decisions made:
- CMake canonical for modern builds.
- Retro builds isolated under /ports.
- No globbing.
- Decisions pending:
- Actual directories and target files.
- Pending tasks: TASK-06
- Constraints: CONSTRAINT-32, CONSTRAINT-33
- Dependencies: WORKSTREAM-01, WORKSTREAM-14
- Timeline / sequencing: First Codex implementation task. 
- Blockers:
- Docs consistency pass.
- Risks: RISK-02, RISK-16
- Artifacts: WORKSTREAM-01, WORKSTREAM-14
- Success criteria:
- Project configures and builds stub targets.
- Recommended next action: Run CMake skeleton prompt. 
- Verification needed: See verification queue where applicable.
- Confidence: high
- Carry-forward priority: P0

### WORKSTREAM-18 — MVP client loop and UI/HUD
- Label: FACT
- Objective: Produce a playable vector-only minimal loop.
- Background: User wants playable MVP, all systems interactable.
- Current state: Prompt generated for minimal client loop; no code confirmed.
- Desired end state: 2D/3D camera, tick loop, vector rendering, selection/placement UI, minimal HUD.
- Importance: First visible playable artifact.
- Decisions made:
- 2D top-down vector and 3D first-person vector.
- No textures/audio in MVP.
- Decisions pending:
- Exact input bindings/UI hotbar details.
- Pending tasks: TASK-09, TASK-10, TASK-24
- Constraints: CONSTRAINT-27, CONSTRAINT-35
- Dependencies: WORKSTREAM-02, WORKSTREAM-14, WORKSTREAM-15
- Timeline / sequencing: After platform/render/sim skeletons. 
- Blockers:
- Render/camera API.
- Risks: RISK-11
- Artifacts: WORKSTREAM-02, WORKSTREAM-14, WORKSTREAM-15
- Success criteria:
- Can pan/zoom/toggle 3D and see deterministic world tick.
- Recommended next action: Wire minimal client loop with flat world. 
- Verification needed: See verification queue where applicable.
- Confidence: high
- Carry-forward priority: P0/P1

### WORKSTREAM-19 — Testing and CI
- Label: FACT
- Objective: Validate determinism and prevent regressions.
- Background: Deterministic project requires early tests.
- Current state: Tests dev spec generated; FNV tick+hash test planned.
- Desired end state: Unit, integration, replay, perf tests; CI boundary checks.
- Importance: Prevents architecture rot. 
- Decisions made:
- Hash full authoritative sim state via FNV-1a.
- Headless tick+hash test first.
- Decisions pending:
- Test harness implementation.
- Pending tasks: TASK-18
- Constraints: CONSTRAINT-36
- Dependencies: WORKSTREAM-16
- Timeline / sequencing: Early, immediately after serializer. 
- Blockers:
- Serializer/hash.
- Risks: RISK-10
- Artifacts: WORKSTREAM-16
- Success criteria:
- Same seed/ticks yields identical hash.
- Recommended next action: Implement first deterministic headless test. 
- Verification needed: See verification queue where applicable.
- Confidence: high
- Carry-forward priority: P0/P1

### WORKSTREAM-20 — Legal/governance docs
- Label: FACT
- Objective: Provide restrictive project governance, licence, contribution and security docs.
- Background: User asked for restrictive licence and root docs. 
- Current state: Drafts generated for README, LICENCE, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, CHANGELOG, .gitignore, etc.
- Desired end state: Consistent, legally reviewed governance docs.
- Importance: Distribution and collaboration boundary. 
- Decisions made:
- Licence should be completely restrictive except personal use/source viewing.
- Decisions pending:
- Legal review; actual doc application.
- Pending tasks: TASK-31
- Constraints: CONSTRAINT-34
- Dependencies: None specific.
- Timeline / sequencing: Before public release. 
- Blockers:
- Legal expertise.
- Risks: RISK-18
- Artifacts: See artifact ledger.
- Success criteria:
- Docs match user intent and are legally usable.
- Recommended next action: Legal review of LICENCE.md and references. 
- Verification needed: See verification queue where applicable.
- Confidence: medium
- Carry-forward priority: P1

### WORKSTREAM-21 — Future multiplayer and server universe
- Label: FACT
- Objective: Add deterministic multiplayer, server/shard interaction and cross-server trade/communication.
- Background: User wants multiplayer next; servers/surfaces discussed. 
- Current state: Planned after MVP; net protocol/dev specs exist conceptually.
- Desired end state: Lockstep or server-authoritative multiplayer with async cross-surface interactions.
- Importance: Major future gameplay/social layer. 
- Decisions made:
- Multiplayer after MVP.
- Cross-surface interactions async only.
- Decisions pending:
- Security/signing, server trust, protocol specifics.
- Pending tasks: TASK-28
- Constraints: CONSTRAINT-26
- Dependencies: WORKSTREAM-16, WORKSTREAM-02
- Timeline / sequencing: Post-MVP. 
- Blockers:
- Core/save/hash first.
- Risks: RISK-07, RISK-19
- Artifacts: WORKSTREAM-16, WORKSTREAM-02
- Success criteria:
- Later network implementation does not alter sim determinism.
- Recommended next action: Keep net stubs and replay tests; defer live multiplayer. 
- Verification needed: See verification queue where applicable.
- Confidence: medium-high
- Carry-forward priority: P2

### WORKSTREAM-22 — Future platforms/renderers/assets
- Label: FACT
- Objective: Add non-MVP renderers/platforms/textures/audio/music.
- Background: User explicitly listed staged platform/renderer plan and assets later. 
- Current state: Roadmap defined; implementation deferred.
- Desired end state: DX11/GL1/GL2/VK1/DX12, Windows 98, Linux/macOS, retro, textures/audio/music packs.
- Importance: Long-term portability and presentation. 
- Decisions made:
- DX9 first; other backends later.
- Textures/sounds/music later.
- Decisions pending:
- Verification of platform/API support.
- Pending tasks: TASK-29, TASK-30
- Constraints: CONSTRAINT-25, CONSTRAINT-33
- Dependencies: WORKSTREAM-14
- Timeline / sequencing: After MVP. 
- Blockers:
- Stable platform/render API.
- Risks: RISK-08, RISK-09
- Artifacts: WORKSTREAM-14
- Success criteria:
- Backends can be added without changing sim.
- Recommended next action: Do not implement prematurely; keep stubs/fallbacks only. 
- Verification needed: See verification queue where applicable.
- Confidence: medium-high
- Carry-forward priority: P2/P3


## 6. Chronological Timeline

| ID | Event / topic | What changed or was decided | Current relevance | Confidence |
| --- | --- | --- | --- | --- |
| TIMELINE-01 | Rail gauge/rail system discussion. | Gauge classes, weights, traction and multigauge groundwork. | Historical; feeds transport specs. | medium |
| TIMELINE-02 | Road, water, air, space transport broadening. | Project expanded beyond rail. | Historical/active architecture. | medium |
| TIMELINE-03 | Building/vector/voxel deterministic discussion. | Led toward grid/vector hybrid. | Active architecture. | high |
| TIMELINE-04 | V3 volumes transcribed. | Detailed determinism/ECS/persistence specs available. | Historical source. | high |
| TIMELINE-05 | Assistant reviewed existing docs/files. | Identified need for source-of-truth docs. | Active rationale. | high |
| TIMELINE-06 | UES outline and massive summary. | Created unified architecture frame. | Active context. | high |
| TIMELINE-07 | User fixed world unit and render contract. | Meter+fixed substeps and strict separation. | Current decision. | high |
| TIMELINE-08 | User fixed spatial ladder and defaults. | Subnano→surface, Earth/Sol/Milky Way. | Current decision. | high |
| TIMELINE-09 | Sharding/surface discussion. | Multiple surface instances, async cross-surface. | Current/future. | high |
| TIMELINE-10 | Surface/space and orbital mechanics discussion. | On-rails space and local bubbles. | Future architecture. | high |
| TIMELINE-11 | Orbital construction/logistics. | Ships/stations/rockets/drop pods/tugs. | Future architecture. | high |
| TIMELINE-12 | Building/cut-fill/splines generalized. | Blocks/faces/edges; terrain layers; corridor archetypes. | Current architecture. | high |
| TIMELINE-13 | Five primitives and full game summary. | Frames, archetypes, graphs, blueprints, ticks/jobs. | Current architecture. | high |
| TIMELINE-14 | Directory tree and dev specs generated. | Repo/implementation guide created. | Artifacts. | high |
| TIMELINE-15 | Root docs generated. | README, licence, contributing, security, etc. | Artifacts. | medium-high |
| TIMELINE-16 | User supplied actual current tree and Codex constraint. | Only listed files to be used. | Current. | high |
| TIMELINE-17 | BUILDING/SPEC_CORE/DATA_FORMATS/DIRECTORY_CONTEXT V4 generated. | Key docs updated. | Current, verify on disk. | high |
| TIMELINE-18 | Codex prompts generated. | Consistency pass and staged implementation prompts. | Next actions. | high |
| TIMELINE-19 | Lua/Codex clarification answered. | /engine/script, Lua 5.4.4, API, FNV hash. | Current implementation decisions. | high |
| TIMELINE-20 | OC-1 discovery and final context transfer. | Handoff preparation. | Current packet. | high |

## 7. Decisions

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

### 7.1 Highest-impact decisions

- FACT: The MVP scope is user-defined and should not be expanded without explicit user instruction.
- FACT: The deterministic core and renderer/platform split are binding constraints for code generation.
- FACT: The building/terrain/corridor choices prevent repeated debate over vectors versus blocks.
- FACT: `/engine/script`, Lua 5.4.4, sandboxed Lua APIs, and FNV-1a state hashing are concrete Codex implementation decisions produced in response to Codex clarification questions.

## 8. Pending Tasks and Next Actions

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

### 8.1 Recommended Task Order

1. Apply/verify V4 docs.
2. Verify `docs/dev/dominium_new_addendum.txt`.
3. Run Codex consistency pass.
4. Generate CMake/build skeleton.
5. Generate `engine/core` skeleton.
6. Generate sim/ECS/events/jobs/world shell.
7. Generate Win32/DX9 vector render shell.
8. Wire minimal client loop.
9. Add `/engine/script`, vendor Lua, implement sandbox/bindings.
10. Implement FNV hash, serializer, and headless determinism test.
11. Add minimal Lua data prototypes and interactive systems.

### 8.2 Blocked Tasks

- TASK-12 and TASK-13 depend on vendoring Lua and updating DIRECTORY_CONTEXT.
- TASK-18 depends on a canonical serializer and state model.
- TASK-34 must be resolved before robust renderer implementation.

### 8.3 Quick Wins

- Verify file names and references (`LICENCE.md`, `SPEC_CORE.md`).
- Patch docs with V4 replacements.
- Add `/engine/script` to DIRECTORY_CONTEXT.
- Add a clear note that MVP data is Lua-first.

### 8.4 Tasks Requiring Verification

- TASK-31, TASK-32, TASK-33, TASK-34.

## 9. Constraints and Requirements

### 9.1 Hard Requirements

| ID | Constraint | Type | Source / basis | Practical implication | Violation risk | Label |
| --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Simulation must be deterministic for identical inputs/version. | technical | V3/SPEC_CORE | All state order fixed; no nondeterminism. | Desync, invalid replays. | FACT |
| CONSTRAINT-02 | No floating point in authoritative simulation. | technical | Repeated specs | Use integer/fixed-point only. | Cross-platform divergence. | FACT |
| CONSTRAINT-03 | /engine/core and /engine/sim must be C89. | technical | BUILDING/CONTRIBUTING | Preserve retro/old compiler compatibility. | Build incompatibility. | FACT |
| CONSTRAINT-04 | Non-core engine/game may use C++98 max, no newer features. | technical | BUILDING/CONTRIBUTING | Avoid modern language dependence. | Toolchain mismatch. | FACT |
| CONSTRAINT-05 | No OS headers outside /engine/platform or /ports. | technical/architecture | DIRECTORY_CONTEXT/Addendum | Keep platform isolation. | Layer contamination. | FACT |
| CONSTRAINT-06 | No graphics headers/calls outside /engine/render. | technical/architecture | Addendum | Keep renderer isolation. | GPU API leakage. | FACT |
| CONSTRAINT-07 | Codex must use only listed files/context. | process | User statement | Avoid hallucinated context. | Wrong docs/code. | FACT |
| CONSTRAINT-08 | World mutations go through command buffers/deferred phases. | technical | V3/Jobs/ECS | Safe deterministic mutation. | Mid-tick inconsistency. | FACT |
| CONSTRAINT-09 | No direct global writes from virtual lanes. | technical | V3 determinism | Lane-local then merge. | Race/order bugs. | FACT |
| CONSTRAINT-10 | Binary formats little-endian; no pointers; no floats. | data | DATA_FORMATS | Portable save/network. | Unreadable/incompatible saves. | FACT |
| CONSTRAINT-11 | No new top-level dirs unless DIRECTORY_CONTEXT updated. | process/directory | Directory contract | Controlled structure. | Repo sprawl. | FACT |
| CONSTRAINT-12 | Use actual file names from user tree. | process/directory | User tree | Avoid broken references. | Broken docs/Codex. | FACT |
| CONSTRAINT-13 | Lua script sandbox disables OS/time/native access. | security/technical | Lua clarification | Protect determinism/security. | Sandbox escape/desync. | FACT |
| CONSTRAINT-14 | Lua may mutate sim only through deterministic engine APIs/commands. | technical | Lua clarification | Preserve tick/order. | Undocumented state changes. | FACT |
| CONSTRAINT-15 | No dense full surface allocation. | resource/technical | Spatial discussion | Use sparse chunks/microgrids. | Memory explosion. | FACT |
| CONSTRAINT-16 | Base game MVP uses one Earth surface. | scope | User MVP | Keep scope bounded. | Multiworld scope creep. | FACT |
| CONSTRAINT-17 | Base terrain immutable. | technical | Cut/fill discussion | Earthworks overlay base. | Loss of original terrain. | FACT |
| CONSTRAINT-18 | Structural microgrids separate from terrain. | technical | Cut/fill discussion | Over/under structures remain distinct. | Terrain/structure conflation. | FACT |
| CONSTRAINT-19 | Blocks/modules are sim truth for structures. | technical | Building decision | Deterministic structure/path/pressure. | Continuous geometry complexity. | FACT |
| CONSTRAINT-20 | Doors/devices must be explicitly placed fixtures. | user preference/technical | User statement | No automatic doors. | Unwanted doors/type bloat. | FACT |
| CONSTRAINT-21 | Buildings rigid for MVP, but data future-proofs collapse. | scope/technical | User statement | Avoid collapse implementation now. | MVP creep or incompatible data. | FACT |
| CONSTRAINT-22 | Splines are baked to discrete chainpoints for runtime. | technical | Spline discussion | Runtime deterministic cells/graphs. | Runtime curve complexity. | FACT |
| CONSTRAINT-23 | Connections occur at explicit graph nodes. | technical | Way connectivity discussion | Topology stable. | Mid-edge graph ambiguity. | FACT |
| CONSTRAINT-24 | Networks deterministic, fixed capacity/latency/ordering. | technical | Network specs | No random loss/ordering. | Desync. | FACT |
| CONSTRAINT-25 | Renderer/platform mix-and-match via APIs/vtables. | architecture | User rollout/addendum | Extensible backend matrix. | Hardcoded backend coupling. | FACT |
| CONSTRAINT-26 | Cross-surface interactions async only. | architecture | Sharding discussion | Surface isolation. | Cross-shard desync. | FACT |
| CONSTRAINT-27 | MVP vector-only, textures/audio later. | scope | User MVP | No asset blockers. | Scope creep. | FACT |
| CONSTRAINT-28 | All systems interactable in MVP via minimal prototypes. | scope | User MVP | Thin systems, not full simulation. | Either too narrow or too broad. | FACT |
| CONSTRAINT-29 | Unknown binary blocks skippable. | data compatibility | DATA_FORMATS | Forward compatibility. | Future format breakage. | FACT |
| CONSTRAINT-30 | No hash tables serialized directly; sorted lists only. | data/determinism | DATA_FORMATS | Deterministic serialization. | Ordering mismatch. | FACT |
| CONSTRAINT-31 | FNV hash over authoritative state only. | testing | Hash clarification | Stable determinism testing. | False positives/negatives. | FACT |
| CONSTRAINT-32 | CMake explicit file lists; no globbing. | build | BUILDING | Deterministic sources. | Accidental files included. | FACT |
| CONSTRAINT-33 | Retro builds isolated under /ports. | build/platform | BUILDING/ports | Modern CMake not contaminated. | Toolchain sprawl. | FACT |
| CONSTRAINT-35 | No textures/sounds/music required in MVP. | scope/resource | User statement | Vector/null audio initially. | Asset bottleneck. | FACT |
| CONSTRAINT-36 | Tests must avoid OS randomness/wallclock dependencies. | testing | Tests dev spec | Cross-platform validation. | Flaky tests. | FACT |

### 9.2 Soft Preferences

| ID | Constraint | Type | Source / basis | Practical implication | Violation risk | Label |
| --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-34 | Licence restrictive except personal use/source viewing. | legal/user preference | User request | Distribution restrictions. | Licence intent violated. | FACT |

### 9.3 Technical Constraints

See CONSTRAINT-01 through CONSTRAINT-33, especially determinism, no sim floats, strict layer boundaries, data format rules, and CMake explicit files.

### 9.4 Time / Resource Constraints

FACT: The MVP intentionally avoids textures, sounds, music, multiplayer, space and extra renderers/platforms to reduce implementation risk.

### 9.5 Legal / Ethical / Safety Constraints

FACT: The user wants a restrictive licence. UNCERTAIN / UNVERIFIED: Legal enforceability must be reviewed.

### 9.6 Evidence / Citation Requirements

FACT: In this handoff request the user required explicit labels and uncertainty preservation. PROJECT-CONTEXT: User profile asks for fact-checked, rigorous evidence, but this packet uses visible chat only.

### 9.7 Formatting / Output Requirements

FACT: The user requested downloadable package files, stable IDs, tables, structured headings, and explicit final status.

### 9.8 Things to Avoid

- Do not invent missing files or systems.
- Do not treat future systems as MVP requirements.
- Do not reintroduce rejected design options.
- Do not collapse uncertainty labels.

## 10. Open Questions and Unresolved Issues

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

## 11. Rejected, Superseded, or Deprioritised Options

| ID | Option | Status | Reason rejected/superseded/deprioritised | Is rejection final? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Pure vector shapes as simulation truth. | rejected | Too complex for deterministic collision/serialization/retro. | final | Use vectors as skins/editor/generators. | WORKSTREAM-07 | FACT |
| REJECTED-02 | Pure blocks without vector authoring. | rejected as sole system | Insufficient for arbitrary curves/splines. | final-ish | Blocks remain sim truth; vectors authoring. | WORKSTREAM-08 | FACT |
| REJECTED-03 | Full n-body orbital mechanics. | rejected | Complex and hostile to determinism/debuggability. | final-ish | Optional future high-fidelity non-core only. | WORKSTREAM-12 | FACT |
| REJECTED-04 | Synchronous cross-surface simulation. | rejected | Would break surface/shard isolation. | final-ish | Async messaging/trade only. | WORKSTREAM-09 | FACT |
| REJECTED-05 | Hard one-surface-per-planet limit. | superseded | Sharding/mirroring requires multiple surface instances. | final-ish | One canonical surface remains. | WORKSTREAM-09 | FACT |
| REJECTED-06 | Arbitrary mid-edge topology without nodes. | rejected | Graph/path/signal ambiguity. | final-ish | Auto-split/create node. | WORKSTREAM-08 | FACT |
| REJECTED-07 | Coding doors into every tunnel type. | rejected | User explicitly did not want it. | final | Use fixtures/anchors. | WORKSTREAM-07 | FACT |
| REJECTED-08 | Auto-spawned doors/utilities. | rejected | User wants only explicit placement. | final | Pattern/blueprint only if invoked. | WORKSTREAM-07 | FACT |
| REJECTED-09 | Runtime arbitrary spline math in sim. | rejected | Runtime determinism/performance. | final | Bake to chainpoints. | WORKSTREAM-08 | FACT |
| REJECTED-10 | Continuous mesh collisions. | rejected | Too heavy, float-prone, retro-unfriendly. | final-ish | AABB/cell/edge collision. | WORKSTREAM-11 | FACT |
| REJECTED-11 | Collapse/destruction in MVP. | deprioritised | User said rigid for now, future support. | tentative for MVP | Later structural graph. | WORKSTREAM-07 | FACT |
| REJECTED-12 | Textures/sounds/music in MVP. | deprioritised | User wants vector now, assets later. | final for MVP | Post-MVP. | WORKSTREAM-22 | FACT |
| REJECTED-13 | Multiplayer in MVP. | deprioritised | User lists next steps after MVP. | final for MVP | Post-MVP. | WORKSTREAM-21 | FACT |
| REJECTED-14 | Sol system/space in MVP. | deprioritised | User lists next steps. | final for MVP | Post-MVP. | WORKSTREAM-12 | FACT |
| REJECTED-15 | DX11/GL/VK/DX12 in MVP. | deprioritised | DX9 first. | final for MVP | Later renderer phases. | WORKSTREAM-22 | FACT |
| REJECTED-16 | Mac Classic/MS-DOS/Android in MVP. | deprioritised | User says later. | final for MVP | Later ports. | WORKSTREAM-22 | FACT |
| REJECTED-17 | CMake as primary retro build system. | rejected | Retro uses isolated build systems. | final-ish | CMake stubs only. | WORKSTREAM-22 | FACT |
| REJECTED-18 | Top-level /render and /platform dirs. | superseded | Directory contract puts them under /engine. | final-ish | Only if contract changes. | WORKSTREAM-14 | FACT |
| REJECTED-19 | Separate CODEGEN_ADDENDUM.md file. | rejected | User wants only listed files. | final | Use docs/dev/dominium_new_addendum.txt. | WORKSTREAM-01 | FACT |
| REJECTED-20 | Unbounded queues/dynamic sim allocation. | rejected | Determinism/resource control. | final | Preallocated bounded buffers. | WORKSTREAM-02 | FACT |

Preserving these prevents repeated work because many discarded options are tempting alternatives: pure vectors, full n-body space, auto doors, runtime splines, MVP textures/audio/multiplayer/space, and top-level renderer/platform directories.

## 12. Artifact Ledger

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

## 13. Rationale and Assumptions

### 13.1 Visible rationale

- FACT: Integer/fixed-point core exists to make simulation reproducible across old and modern systems.
- FACT: Renderer/platform split exists so OS/GPU APIs cannot contaminate deterministic sim.
- FACT: Blocks/cells/faces/edges are sim truth because they support deterministic structure, pathing, pressure, collision, retro render, and serialization.
- FACT: Vector splines are authoring/generation tools because runtime arbitrary curve math is unnecessary and hard to make deterministic.
- FACT: Immutable base terrain exists so cut/fill and structures can be reasoned about without erasing original geography.
- FACT: On-rails space exists because full orbital/n-body mechanics would be excessive for deterministic gameplay needs.
- FACT: Vector-only MVP exists to avoid asset-production bottlenecks.

### 13.2 Assumptions

- INFERENCE: The V4 docs generated in this chat are intended to replace the older pasted docs.
- INFERENCE: Codex should work in staged passes, not attempt the whole engine at once.
- UNCERTAIN / UNVERIFIED: Actual repo files match the user-pasted tree.
- UNCERTAIN / UNVERIFIED: DX9/Win2000, SDL2, Lua 5.4.4, and toolchain assumptions are valid.

## 14. Risks and Failure Modes

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

## 15. Verification Queue

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

## 16. Spec Book Contribution Notes

### Likely chapters/sections

- Architecture Overview and Determinism Kernel
- Repository and Directory Contract
- Build and Platform Strategy
- Spatial Hierarchy and World Model
- Terrain, Earthworks and Microgrids
- Buildings, Fixtures and Construction
- Transport Corridors and Vector Alignments
- Utilities and Networks
- Renderer/Platform Abstraction
- Lua Data and Modding
- Serialization, Replay and Determinism Hashing
- MVP Roadmap and Implementation Plan

### Unique contributions from this chat

- Finalized meter+Q16.16 world unit decision.
- Finalized strict render/platform/sim separation for MVP.
- Detailed terrain/earthworks/microgrid model.
- Detailed block/face/edge/fixture building model.
- Vector corridor baking model for infrastructure.
- Explicit MVP definition and Codex implementation sequence.
- Lua binding decisions including /engine/script and Lua 5.4.4.
- FNV-1a full-state hash decision.

### Possible duplicates with other chats

- INFERENCE: Rail/transport/electrical/data systems may overlap with earlier Dominium chats.
- INFERENCE: Determinism/ECS/save specs may overlap with other generated V3 volumes.
- INFERENCE: Directory and Codex prompts may overlap with current repo-specific chats.

### Conflicts to watch for

- Lua-only MVP data versus JSON-oriented data specs.
- Current user tree versus earlier ideal repo tree.
- Render command API sketches using floats versus integer serialization.
- `LICENCE.md` versus `LICENSE.md`; `SPEC_CORE.md` versus `SPEC-core.md`.

### Formal requirements candidates

- No floats in authoritative sim.
- Renderer pure observer.
- Codex uses listed files only.
- MVP vector-only and DX9-first.
- Lua sandbox restrictions.
- Canonical state hash requirements.

### Background context candidates

- Earlier rail gauge exploration.
- Full future orbital/logistics ideas.
- Retro platform aspirations.

### Needs user confirmation before becoming spec

- Lua vs JSON long-term data policy.
- Final DomDrawCmd/camera API.
- Native Win32 vs SDL2 first implementation path.
- Legal licence validity.

## 17. What Future Assistants Must Preserve

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

## 18. What Future Assistants Must Not Assume

- Do not assume actual repo files contain generated V4 docs until verified.
- Do not assume `/engine`, `/game`, `/data`, `/mods`, etc. exist yet merely because docs describe them.
- Do not assume SDL2 works on Windows 2000.
- Do not assume DX9.0c target details are verified.
- Do not assume Lua 5.4.4 works unchanged on all intended compilers.
- Do not assume legal licence validity.
- Do not assume JSON remains the MVP data format; user said Lua for all data.
- Do not assume multiplayer, space, textures, audio or other renderers are MVP scope.
- Do not assume assistant-generated suggestions are user decisions unless accepted.
- Do not assume hidden project context is part of this chat report.

## 19. Recommended Next Action

If continuing this chat’s work alone: run or refine the Codex consistency pass against the four key docs and actual repo files, then proceed to CMake/build skeleton.

If aggregating with other chat reports: ingest this packet as the source for **architecture II / Codex prep / docs V4 / MVP implementation plan**, preserve IDs, and compare against other chats for conflicting decisions about data formats, directory layout, render/platform APIs, and MVP scope.

User verification needed before acting: confirm actual repo file state, confirm V4 docs were applied, clarify Lua-vs-JSON long-term policy, finalize DomDrawCmd/camera API.

## 20. Appendix: Possibly Relevant Details

### 20.1 User-provided MVP wording

> MVP:  
> A fully complete core.  
> 1 full size surface, on earth.  
> All systems interractable, but minimal data prototypes and such for testing.  
> Lua for all data.  
> Dx9.0c, sdl2, win32.  
> 2d vector top down.  
> 3d vector first person.

### 20.2 User-provided platform rollout wording

> First I will develop dx9 for windows NT 2000 SP4 through Windows 11+, using native win32 or sdl2, later adding dx11, gl1, gl2, vk1, dx12.  
> Then we will add Windows 98 SE+ using dx9 or gl1 and native win32 or sdl1.  
> Then modern Linux and macosx gets POSIX or sdl2 and gl2 or vk1.  
> Macos classic, msdos, android, etc versions come later.

### 20.3 User-provided current tree

Root files: `.gitignore`, `CHANGELOG.md`, `CMakeLists.txt`, `CONTRIBUTING.md`, `LICENCE.md`, `README.md`, `SECURITY.md`.

Docs files: `BUILDING.md`, `CODE_OF_CONDUCT.md`, `DATA_FORMATS.md`, `DIRECTORY_CONTEXT.md`, `LANGUAGE_POLICY.md`, `MILESTONES.md`, `SPEC_CORE.md`, `STYLE.md`, plus `docs/context/*` and many `docs/dev/dominium_new_*.txt` files.

### 20.4 Critical Codex clarification decisions

- `/engine/script` is the Lua bridge location.
- Lua version: 5.4.4, vendored under `/third_party`.
- Lua API: `dom.entity`, `dom.query`, `dom.prefab`, `dom.data`, `dom.net`, `dom.jobs`, `dom.random`.
- Hash: FNV-1a 64-bit over canonical serialized authoritative sim state.

### 20.5 Report package repair note

This report consumes the previous Context Transfer Packet, preserves its content, normalizes stable IDs, adds package files, and flags remaining uncertainty.
