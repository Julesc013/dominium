# Aggregator Packet — Dominium/Domino Engine Refactor Prompts

## 1. Packet Metadata

- Chat label: Dominium/Domino Engine Refactor Prompts
- Date anchor: 2026-05-27 Australia/Melbourne
- Source scope: THIS CHAT ONLY
- Coverage: full visible-chat coverage with caveats
- Confidence: 4/5
- Staleness risk: medium
- Merge priority: high
- Main limitations: repository state unverified; some decisions inferred from continuation; exact prompt text summarized; plugin/Q-format decisions unresolved.

## 2. Ultra-Condensed Carry-Forward Capsule

This chat was a focused architecture and implementation-planning session for the Dominium/Domino deterministic engine. The user established the assistant role as a senior simulation systems architect and supplied hard constraints that governed the entire discussion: the Domino engine core must remain ISO C89, deterministic, fixed-point where determinism matters, free of OS/platform/UI/rendering APIs, free of hardcoded gameplay semantics, and driven by TLV-versioned content. The Dominium layer is limited to portable C++98 UI/tools/visualization and must emit deterministic commands rather than mutate engine state. Strict layering across BUILD, TRANS, STRUCT, DECOR, SIM, RES, ENV, JOB, and AGENT remained a central invariant.

The chat began with a requested architecture for advanced simulation systems: heat, electrical power, fluids/hydrology, atmospheres, vehicle physics, structural loads/destruction, and a unified mod-extensible physics framework. The resulting architecture established deterministic fixed-point solvers, graph and field substrates, ports/events/deltas for cross-system interactions, stable tick ordering, replay hashes, and TLV-driven prototypes. This physics stack remains a major future workstream, but this chat primarily moved toward engine-wide primitives rather than detailed heat/power/fluid implementation prompts.

The user then shifted focus to agents and actors: wildlife, pets, companions, workers, robots, players/NPCs, plants, crops, pests, swarms, herds, flocks, and predator-prey systems. The architectural answer treated agents as composition, not inheritance. “Intelligence” became a function of components, sensors, minds/controllers, capabilities, and command/job bindings rather than a hardcoded entity type. Behavior was generalized as sensors producing observations, minds/controllers producing intents, actions validating and producing deltas, and a sorted commit phase applying all mutations. Plants and dumb wildlife were explicitly optimized through vegetation fields, population aggregates, promotion/demotion, cadence decimation, and group controllers.

The discussion then generalized these methods across the entire engine. The core pattern became: typed packet IO, fields/events/messages, deterministic scheduler, sorted delta commit, budgeted work, deterministic carryover queues, representation ladder R0/R1/R2/R3, canonical graph toolkit, hot/cold data separation, dirty-set incremental rebuilds, replay/hashing, and source-of-truth separation between authoring state and derived caches. The user asked whether custom buildings and heavy systems could benefit; the plan answered with building representation ladders, edit buffers, compiled artifacts, stable ports, surface/enclosure/support graphs, and incremental compilation.

Future Interstellar and Wargames DLC requirements were introduced, including space beyond the original Earth surface, combat, fog of war, and information dissemination. Rather than hardcoding “space” or “war,” the plan generalized them into domains, frame graphs, propagators, observer contexts, belief/knowledge stores, visibility/occlusion, communications graphs, and generic interactions/actions. A later sister-chat prompt added mandatory arbitrary placement and infrastructure requirements: no grid lock, arbitrary 3D pose, parametric anchors, TRANS corridors with cross-section slots and grade-separated junctions, STRUCT arbitrary footprints/enclosures/carriers/surfaces, and DECOR host-agnostic signage/markings/rulepacks/overrides. These requirements were merged into the existing plan rather than forked.

The major output of the chat was a sequential Codex implementation roadmap: fourteen detailed prompts plus a documentation validation prompt. The prompts cover engine invariants/spec scaffolding, typed packets/TLV registries, scheduler/budgets/delta commit, fields/events/messages, representation ladder, pose/anchors, TRANS, STRUCT, DECOR, agents/actions/groups, graph toolkit, domains/frames/propagators, observer/knowledge/visibility/comms, determinism hardening/replay/regression, and documentation validation. No code was actually generated or repository files verified in this chat; all file paths and modules are proposed implementation artifacts unless later confirmed. The most important unresolved issues are the native-plugin versus deterministic VM policy, exact fixed-point Q-format tables, actual repository layout/build system, and existing TLV/scheduler/graph/BUILD/TRANS/STRUCT/DECOR state. Future assistants must not lose the hard constraints, the no-baked-geometry rule, the no-grid-lock rule, sorted delta commit, representation ladder, generic core primitives, and the 14-prompt roadmap.

## 3. Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
|---|---|---|---|---|---|---|
| 1 | Domino Engine C89/fixed-point/no OS/UI/rendering/no hardcoded semantics. | constraint |  | Foundation of all design. | FACT | high |
| 2 | Dominium is C++98 UI/tools only and emits deterministic commands. | constraint |  | Maintains layer boundary. | FACT | high |
| 3 | All mutation through sorted delta commit. | decision |  | Deterministic order and replay safety. | INFERENCE | medium-high |
| 4 | Representation ladder R0/R1/R2/R3 engine-wide. | decision |  | Performance at scale. | INFERENCE | medium-high |
| 5 | Budgets/carryover/accumulators must change latency, not final outcomes. | constraint |  | Deterministic performance control. | INFERENCE | medium-high |
| 6 | Agents are composition and behavior pipeline is sensors→observations→minds→intents→actions→deltas. | decision |  | Arbitrary actor behavior. | INFERENCE | medium-high |
| 7 | Plants/wildlife can be fields/populations and promoted deterministically. | decision |  | Scale large ecosystems. | INFERENCE | medium-high |
| 8 | Pose+anchors are authoritative placement; grids UI-only. | decision/constraint |  | Arbitrary placement and deterministic replay. | FACT | high |
| 9 | No baked geometry as authoritative state. | constraint |  | Rebuildable caches and replay stability. | FACT | high |
| 10 | TRANS corridors use slots for co-location. | decision |  | Shared infrastructure without conflict. | FACT | high |
| 11 | STRUCT authoring/compile split: footprints, volumes, enclosures, carriers, surfaces, supports. | decision |  | Scalable infrastructure. | FACT | high |
| 12 | DECOR is host-agnostic rulepacks+overrides, render tiles by default. | decision |  | Scalable signage/markings/details. | FACT | high |
| 13 | Space/war generalized to domains/frames/propagators/knowledge/visibility/comms. | decision |  | DLC extensibility without core semantics. | FACT/INFERENCE | medium-high |
| 14 | Knowledge/fog is simulation state and query filtering. | decision |  | Replayable information model. | INFERENCE | medium-high |
| 15 | The 14 Codex prompts plus docs prompt are current roadmap artifacts. | artifact |  | Immediate implementation plan. | FACT | high |

## 4. Workstream Summaries


- ID: WORKSTREAM-01
- Name: Dominium/Domino deterministic engine architecture
- Objective: Preserve and extend a deterministic simulation/game engine architecture with a C89 Domino core and C++98 Dominium UI/tools layer.
- Current state: Architecture and Codex prompt roadmap were produced in this chat. No repository implementation was verified in this chat.
- Desired end state: Engine core supports deterministic simulation, lockstep multiplayer, replay, modular data-driven systems, bounded work, stable IDs, and strict layer boundaries.
- Priority: highest
- Decisions: DECISION-01, DECISION-02, DECISION-03, DECISION-04, DECISION-05, DECISION-06, DECISION-07
- Tasks: TASK-01, TASK-02, TASK-03, TASK-04, TASK-14, TASK-15
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-03, CONSTRAINT-04, CONSTRAINT-05, CONSTRAINT-06, CONSTRAINT-07, CONSTRAINT-08, CONSTRAINT-09, CONSTRAINT-10
- Artifacts: ARTIFACT-01, ARTIFACT-14, ARTIFACT-31
- Risks: RISK-01, RISK-02, RISK-03, RISK-04
- Open questions: QUESTION-01, QUESTION-02, QUESTION-03
- Next action: Run or adapt CODEX PROMPT 1 after repository inspection.


- ID: WORKSTREAM-02
- Name: Advanced physics and simulation stack
- Objective: Support heat, power, fluids, atmosphere, vehicles, structural loads/destruction, and mod-extensible physics through deterministic engine primitives.
- Current state: Top-level architecture was produced. No subsystem-specific Codex prompt beyond generic graph/field/scheduler/action foundations was generated.
- Desired end state: Domain solvers use fixed-point math, fixed iteration schedules, graph/field substrates, TLV prototypes, ports/events/deltas, and replay hashes.
- Priority: high
- Decisions: DECISION-08, DECISION-09, DECISION-10, DECISION-11
- Tasks: TASK-16
- Constraints: CONSTRAINT-01, CONSTRAINT-04, CONSTRAINT-05, CONSTRAINT-06, CONSTRAINT-10, CONSTRAINT-14
- Artifacts: ARTIFACT-02
- Risks: RISK-04, RISK-05, RISK-07, RISK-10
- Open questions: QUESTION-02, QUESTION-04, QUESTION-05
- Next action: After spine prompts are implemented, generate dedicated Codex prompts for heat, power, fluids, atmosphere, vehicles, and structural load solvers.


- ID: WORKSTREAM-03
- Name: Agents, actors, life, ecology, and behavior
- Objective: Support arbitrary actors including wildlife, pets, companions, workers, robots, players/NPCs, plants, crops, pests, swarms, herds, flocks, and predator-prey behavior.
- Current state: Conceptual architecture and CODEX PROMPT 10 were produced.
- Desired end state: Behavior is implemented through composition and a semantic-free sensors → observations → minds/controllers → intents → actions → deltas pipeline, with scalable R0/R1/R2/R3 representations.
- Priority: high
- Decisions: DECISION-12, DECISION-13, DECISION-14, DECISION-15, DECISION-16
- Tasks: TASK-10
- Constraints: CONSTRAINT-07, CONSTRAINT-11, CONSTRAINT-12, CONSTRAINT-13
- Artifacts: ARTIFACT-03, ARTIFACT-04, ARTIFACT-05, ARTIFACT-23
- Risks: RISK-06, RISK-08, RISK-11
- Open questions: QUESTION-01, QUESTION-06
- Next action: Use CODEX PROMPT 10 after foundational prompts 1–9 are implemented or scaffolded.


- ID: WORKSTREAM-04
- Name: Engine-wide extensibility, modularity, and performance methodology
- Objective: Apply common optimization and extensibility techniques across all engine systems, not only agents or physics.
- Current state: Accepted as the general pattern behind the master prompt plan.
- Desired end state: Every heavy subsystem uses representation ladders, typed IO, budgets, dirty rebuilds, canonical ordering, hot/cold separation, and replay hashing.
- Priority: highest
- Decisions: DECISION-17, DECISION-18, DECISION-19, DECISION-20
- Tasks: TASK-03, TASK-04, TASK-05, TASK-11, TASK-14
- Constraints: CONSTRAINT-09, CONSTRAINT-10, CONSTRAINT-11, CONSTRAINT-12, CONSTRAINT-13, CONSTRAINT-14
- Artifacts: ARTIFACT-06, ARTIFACT-07, ARTIFACT-08, ARTIFACT-24, ARTIFACT-25
- Risks: RISK-02, RISK-03, RISK-04, RISK-05
- Open questions: QUESTION-07
- Next action: Keep future prompts aligned with this methodology; avoid subsystem-specific shortcuts.


- ID: WORKSTREAM-05
- Name: Custom buildings and infrastructure at scale
- Objective: Optimize and modularize custom buildings and infrastructure so complex real-world facilities can be built and simulated at scale.
- Current state: Concept plan integrated into TRANS/STRUCT/DECOR prompts, especially Prompts 7–9 and Prompt 11.
- Desired end state: Buildings and infrastructure are authored parametrically, compiled incrementally into derived artifacts, and simulated with representation ladders and stable ports/anchors.
- Priority: high
- Decisions: DECISION-21, DECISION-22, DECISION-23, DECISION-24
- Tasks: TASK-07, TASK-08, TASK-09, TASK-11
- Constraints: CONSTRAINT-15, CONSTRAINT-16, CONSTRAINT-17, CONSTRAINT-18
- Artifacts: ARTIFACT-09, ARTIFACT-20, ARTIFACT-21, ARTIFACT-22
- Risks: RISK-09, RISK-10, RISK-12
- Open questions: QUESTION-08
- Next action: Implement or adapt CODEX PROMPTS 6–9 and 11 in sequence.


- ID: WORKSTREAM-06
- Name: Generalized Interstellar/Wargames core primitives
- Objective: Prepare for Interstellar DLC (`data/space/`) and Wargames DLC (`data/war/`) by adding generic engine primitives rather than space/war-specific code.
- Current state: Architecture generalized into Domains/Frames/Propagators and Observer/Knowledge/Visibility/Comms, then codified as Prompts 12–13.
- Desired end state: DLCs instantiate domains, frames, propagators, sensors, knowledge, visibility, comms, and actions via data/plugins; engine core remains semantic-free.
- Priority: medium-high
- Decisions: DECISION-25, DECISION-26, DECISION-27, DECISION-28
- Tasks: TASK-12, TASK-13
- Constraints: CONSTRAINT-07, CONSTRAINT-20, CONSTRAINT-21, CONSTRAINT-22
- Artifacts: ARTIFACT-11, ARTIFACT-12, ARTIFACT-26, ARTIFACT-27
- Risks: RISK-13, RISK-14, RISK-15
- Open questions: QUESTION-09, QUESTION-10
- Next action: Use CODEX PROMPTS 12–13 after foundational prompt implementation.


- ID: WORKSTREAM-07
- Name: Arbitrary placement and TRANS/STRUCT/DECOR spatial primitives
- Objective: Support arbitrary 3D placement, curved geometry, corridor co-location, buildings, signage, markings, and surface detail without grid lock.
- Current state: Additional mandatory requirements from sister GPT-5.1 prompt were integrated into the plan and became Prompts 6–9.
- Desired end state: All placement uses fixed-point pose + parametric anchors; TRANS, STRUCT, and DECOR have clear authoring/compiled boundaries; grids are UI-only.
- Priority: highest
- Decisions: DECISION-29, DECISION-30, DECISION-31, DECISION-32
- Tasks: TASK-06, TASK-07, TASK-08, TASK-09
- Constraints: CONSTRAINT-15, CONSTRAINT-16, CONSTRAINT-17, CONSTRAINT-18, CONSTRAINT-19
- Artifacts: ARTIFACT-13, ARTIFACT-14, ARTIFACT-19, ARTIFACT-20, ARTIFACT-21, ARTIFACT-22
- Risks: RISK-09, RISK-12, RISK-16
- Open questions: QUESTION-11
- Next action: Prioritize Prompt 6 before TRANS/STRUCT/DECOR implementation.


- ID: WORKSTREAM-08
- Name: Master Codex prompt implementation roadmap
- Objective: Provide sequential Codex prompts to implement/refactor the engine safely without breaking prior architecture.
- Current state: Fourteen prompts plus a documentation validation prompt were generated in this chat.
- Desired end state: Codex can execute prompts in order, with each prompt scoped, tested, and guarded against semantic overreach.
- Priority: highest
- Decisions: DECISION-33
- Tasks: TASK-01, TASK-02, TASK-03, TASK-04, TASK-05, TASK-06, TASK-07, TASK-08, TASK-09, TASK-10, TASK-11, TASK-12, TASK-13, TASK-14, TASK-15
- Constraints: CONSTRAINT-23, CONSTRAINT-24
- Artifacts: ARTIFACT-14, ARTIFACT-15, ARTIFACT-16, ARTIFACT-17, ARTIFACT-18, ARTIFACT-19, ARTIFACT-20, ARTIFACT-21, ARTIFACT-22, ARTIFACT-23, ARTIFACT-24, ARTIFACT-25, ARTIFACT-26, ARTIFACT-27, ARTIFACT-28, ARTIFACT-29
- Risks: RISK-17, RISK-18
- Open questions: QUESTION-03
- Next action: Use the generated prompts or refine them against actual repository structure.


- ID: WORKSTREAM-09
- Name: Documentation validation and normalization
- Objective: Ensure all architecture docs are internally consistent, correct, non-contradictory, and aligned with module boundaries.
- Current state: A dedicated Codex documentation validation prompt was generated.
- Desired end state: Docs become formal, coherent specs with conflict resolutions, source-of-truth tables, forbidden sections, and a validation report.
- Priority: high
- Decisions: DECISION-34
- Tasks: TASK-15
- Constraints: CONSTRAINT-24, CONSTRAINT-25
- Artifacts: ARTIFACT-29
- Risks: RISK-18, RISK-19
- Open questions: none recorded
- Next action: Run the documentation validation prompt after specs are created or updated.


## 5. Registers for Merge

### Decision Register
| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | Domino Engine is ISO C89 only. | accepted hard requirement | User explicitly stated this in the opening constraints. | Portability and strict deterministic control. | All engine prompts and code must avoid C99/C++ features. | WORKSTREAM-01 | high | FACT |
| DECISION-02 | Dominium UI/tools use a portable C++98 subset only. | accepted hard requirement | User explicitly stated this. | Tooling can be higher-level but must remain portable and outside engine mutation. | UI/tools must emit deterministic commands rather than mutate state. | WORKSTREAM-01 | high | FACT |
| DECISION-03 | No OS/platform/UI/rendering APIs inside engine code. | accepted hard requirement | User explicitly stated no OS APIs inside engine code and Dominium is UI/tools only. | Strict layer purity and deterministic portability. | All platform/window/input/FS/process work belongs behind dsys; graphics behind dgfx. | WORKSTREAM-01 | high | FACT |
| DECISION-04 | No floats where determinism matters; use fixed-point Q formats. | accepted hard requirement | User explicitly stated this; examples include Q16.16/Q24.8. | Cross-platform identical simulation. | All deterministic math, geometry, solvers, placement, and hashes require fixed representation. | WORKSTREAM-01 | high | FACT |
| DECISION-05 | No hardcoded gameplay semantics; content defines semantics. | accepted hard requirement | User explicitly stated no hardcoded game semantics and data-driven content. | Modularity and DLC extensibility. | Engine primitives use type IDs, TLV schemas, registries, and generic actions. | WORKSTREAM-01 | high | FACT |
| DECISION-06 | Use TLV-versioned data and commands. | accepted hard requirement | User listed TLV-versioned content formats and later prompts formalized packet/TLV schemas. | Versioning, replay, deterministic content loading. | Prompt 2 and docs validation must enforce canonical TLV schemas. | WORKSTREAM-01 | high | FACT |
| DECISION-07 | State mutation flows through sorted delta commit. | accepted plan decision | Assistant proposed; user continued with this plan through Codex prompts. | Avoids order-dependent mutation and desync. | Minds/actions/controllers/solvers emit deltas; PH_COMMIT applies sorted deltas. | WORKSTREAM-01 | medium-high | INFERENCE |
| DECISION-08 | Advanced physics domains use graph, field, port, event, and delta primitives. | accepted plan decision | Top-level architecture response and later generalization. | Common infrastructure avoids duplicated solvers and cross-coupling. | Heat, power, fluids, atmo, vehicles, structures should not invent bespoke IO. | WORKSTREAM-02 | medium-high | INFERENCE |
| DECISION-09 | Physics solvers must use fixed iteration counts and stable ordering. | accepted plan decision | User required no tolerance-based solvers in sister prompt; assistant applied globally. | Avoid platform-dependent convergence divergence. | No epsilon-driven early termination in deterministic paths. | WORKSTREAM-02 | high | FACT |
| DECISION-10 | Mods can extend physics families via TLV parameters and stable vtables/registries. | accepted plan decision | Initial user asked for unified mod-extensible physics framework; assistant proposed vtables/ABI. | Extensibility without engine forks. | Plugin policy remains partly unresolved for native code. | WORKSTREAM-02 | medium-high | FACT |
| DECISION-11 | Cross-system interactions use ports/fields/events/messages/deltas rather than direct calls. | accepted plan decision | Repeated throughout plan and prompts. | Maintains layering and replayable causality. | Subsystem boundaries must route through generic IO. | WORKSTREAM-02 | medium-high | INFERENCE |
| DECISION-12 | Agents are component composition, not inheritance/classes. | accepted plan decision | Assistant proposed; user built on it without rejection. | Supports arbitrary actors without hardcoded human/animal/robot categories. | Agent storage/registry must be component-based and data-driven. | WORKSTREAM-03 | medium-high | INFERENCE |
| DECISION-13 | Behavior pipeline is sensors → observations → minds/controllers → intents → actions → deltas. | accepted plan decision | Directly answers user request for arbitrary stimuli and actions; included in Prompt 10. | Separates sensing, decision, validation, and mutation. | Every behavior path must obey typed IO and delta commit. | WORKSTREAM-03 | high | INFERENCE |
| DECISION-14 | Plants/grass/weeds/crops default to fields/aggregate layers unless promoted. | accepted plan decision | Assistant proposed as performance architecture; user continued. | Allows large numbers of plants. | Large/interactive plants can become entities; groundcover stays field-based. | WORKSTREAM-03 | medium-high | INFERENCE |
| DECISION-15 | Wildlife/pests can use population fields and local promotion. | accepted plan decision | Assistant proposed for dumb agent performance; user continued. | Scales large ecosystems without per-agent cost everywhere. | Interest-driven promotion must be deterministic. | WORKSTREAM-03 | medium-high | INFERENCE |
| DECISION-16 | Groups/herds/flocks use group controllers plus bounded local steering, not global intelligence. | accepted plan decision | Assistant proposed in response to swarms/herds/flocks request. | Controls O(N²) costs and preserves determinism. | Neighbor caps and group membership ordering are required. | WORKSTREAM-03 | medium-high | INFERENCE |
| DECISION-17 | Representation ladder R0/R1/R2/R3 applies engine-wide. | accepted plan decision | User asked if methods can apply entire engine; assistant answered yes and codified in Prompt 5. | Performance and scalability pattern across subsystems. | Entities, buildings, networks, domains, decor, propagators all need LOD hooks. | WORKSTREAM-04 | high | INFERENCE |
| DECISION-18 | Use deterministic budgets and carryover queues as core services. | accepted plan decision | Repeated in prompts 3, 5, 7–14. | Bounded work without desync. | Budgets change latency, not final state; accumulators required. | WORKSTREAM-04 | high | INFERENCE |
| DECISION-19 | Unify heavy networks under one deterministic graph toolkit. | accepted plan decision | Assistant recommended combining graph systems; Prompt 11 generated. | Avoids duplicated graph implementations and nondeterministic traversal. | Power/fluids/comms/enclosures/supports/routing use same graph substrate. | WORKSTREAM-04 | medium-high | INFERENCE |
| DECISION-20 | Use fields for continuous-ish signals and cheap sampling. | accepted plan decision | Assistant repeatedly proposed fields for stimuli, ecology, moisture, heat, population, risk. | O(1) sampling replaces expensive neighbor searches. | Prompt 4 establishes field substrate. | WORKSTREAM-04 | medium-high | INFERENCE |
| DECISION-21 | Buildings/infrastructure use authoring state plus compiled derived artifacts. | accepted plan decision | Building optimization answer and sister prompt integration. | Incremental compile, replay stability, no baked truth. | STRUCT Prompt 8 separates model/compile/phys. | WORKSTREAM-05 | high | INFERENCE |
| DECISION-22 | Compiled building artifacts include occupancy, enclosures, surfaces, supports, carriers, and anchors/sockets. | accepted plan decision | Prompt 8 details this artifact split. | Different subsystems consume only needed artifacts. | Requires dirty flags and chunk-aligned indices. | WORKSTREAM-05 | medium-high | INFERENCE |
| DECISION-23 | Building edits use edit buffers and incremental compilation under budget. | accepted plan decision | Assistant proposed two-phase construction and prompts enforce dirty rebuild. | Prevents stalls and preserves determinism. | BUILD/STRUCT/TRANS compilers must not rebuild whole world unnecessarily. | WORKSTREAM-05 | medium-high | INFERENCE |
| DECISION-24 | Ports/endpoints remain stable across LOD and compilation. | accepted plan decision | Assistant emphasized this for buildings/networks. | External networks must not desync when internal representation changes. | Port IDs are authoritative and preserved. | WORKSTREAM-05 | medium-high | INFERENCE |
| DECISION-25 | Space/DLC foundations are generalized as domains, frames, and propagators. | accepted plan decision | User asked to make it core not space-specific; assistant produced Prompt 12. | Avoids hardcoding Interstellar DLC concepts in engine. | Spatial models become domain types with fixed-point frames. | WORKSTREAM-06 | high | INFERENCE |
| DECISION-26 | Fog/information dissemination is generalized as observer contexts, belief store, visibility, and comms. | accepted plan decision | User asked Wargames support; assistant generalized and produced Prompt 13. | Fog becomes replayable simulation state. | UI and AI query through observer-filtered APIs. | WORKSTREAM-06 | high | INFERENCE |
| DECISION-27 | Knowledge is authoritative simulation state and participates in hash/replay. | accepted plan decision | Prompt 13 states this explicitly. | Prevents UI-only hidden information and desync. | Belief DB must serialize and hash canonically. | WORKSTREAM-06 | high | INFERENCE |
| DECISION-28 | Comms graph uses deterministic routing, integer tick latency, congestion queues, and transforms. | accepted plan decision | Prompt 13 details this. | Information dissemination and command routing are deterministic. | Equal-cost routes require tie-breaks. | WORKSTREAM-06 | medium-high | INFERENCE |
| DECISION-29 | All placement uses fixed-point pose plus parametric anchors; grids are UI-only. | accepted hard requirement/plan decision | Sister prompt explicitly required no grid lock and parametric anchoring; Prompt 6 generated. | Arbitrary placement and replay safety. | BUILD/TRANS/STRUCT/DECOR edit commands must not store unquantized world geometry as truth. | WORKSTREAM-07 | high | FACT |
| DECISION-30 | TRANS corridors use alignments, z-profiles, roll, cross-section slots, attachments, and junctions. | accepted plan decision | Sister prompt required unified spatial primitives; Prompt 7 generated. | Supports complex co-located infrastructure deterministically. | No stacked independent splines for shared corridors. | WORKSTREAM-07 | high | FACT |
| DECISION-31 | STRUCT supports arbitrary oriented footprints, volumes, enclosures, carriers, surfaces, sockets. | accepted plan decision | Sister prompt required this; Prompt 8 generated. | Allows real-world buildings/infrastructure. | STRUCT is split into model/compile/phys. | WORKSTREAM-07 | high | FACT |
| DECISION-32 | DECOR is host-agnostic rulepack-generated baseline plus manual overrides. | accepted plan decision | Sister prompt required decor/signage/marking system; Prompt 9 generated. | Scalable signage/markings/detail on terrain/corridors/structures/interiors. | DECOR tiles are derived and render-only unless promoted. | WORKSTREAM-07 | high | FACT |
| DECISION-33 | Use a sequential Codex prompt implementation roadmap. | accepted process decision | User asked for prompt plan and then requested prompts 1–14. | Transforms architecture into actionable implementation chunks. | Future work should continue or refine prompt plan rather than restart. | WORKSTREAM-08 | high | FACT |
| DECISION-34 | Run a documentation validation/normalization pass after docs/specs exist. | accepted process decision | User asked for a prompt to ensure validity, consistency, and correctness. | Prevents spec drift and contradictions. | docs/DOCS_VALIDATION_REPORT.md should be produced by Codex. | WORKSTREAM-09 | high | FACT |


### Task Register
| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Recommended next step | Related workstream | Label | Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Run/adapt CODEX PROMPT 1: engine invariants, specs, scaffolding. | highest | first implementation step | Codex/user | Repository access; current build system | Existing repo; prompt text | Specs, scaffolding, det_invariants header, no behavior | Inspect repository then apply Prompt 1 | WORKSTREAM-08 | FACT | high |
| TASK-02 | Run/adapt CODEX PROMPT 2: typed packet ABI and TLV registries. | high | after Prompt 1 | Codex | Prompt 1; TLV/res layer state | Existing RES/TLV code | Packet ABI, registries, canonical TLV/hash tests | Apply Prompt 2 after scaffolding | WORKSTREAM-08 | FACT | high |
| TASK-03 | Run/adapt CODEX PROMPT 3: scheduler, budgets, queues, delta commit. | high | after Prompt 2 | Codex | Packet ABI | Existing scheduler/build architecture | Deterministic tick spine and delta commit tests | Apply Prompt 3 | WORKSTREAM-08 | FACT | high |
| TASK-04 | Run/adapt CODEX PROMPT 4: fields, events, messages. | high | after Prompt 3 | Codex | Scheduler, packets, budgets | Stimulus substrate requirements | Event/message buses and field layers | Apply Prompt 4 | WORKSTREAM-08 | FACT | high |
| TASK-05 | Run/adapt CODEX PROMPT 5: representation ladder and interest volumes. | high | after Prompt 3/4 | Codex | Scheduler, budgets, chunk/object indices | LOD thresholds defaults | R0/R1/R2/R3 framework and accumulator tests | Apply Prompt 5 | WORKSTREAM-08 | FACT | high |
| TASK-06 | Run/adapt CODEX PROMPT 6: pose, anchors, arbitrary placement. | highest | before TRANS/STRUCT/DECOR | Codex | Fixed-point core; frame scaffolding | Placement command schemas | Pose/anchor/quantization infrastructure | Apply Prompt 6 | WORKSTREAM-07 | FACT | high |
| TASK-07 | Run/adapt CODEX PROMPT 7: TRANS corridors, slots, junctions. | high | after Prompt 6 | Codex | Pose/anchors, budgets, dirty rebuild | Existing TRANS code | TRANS authoring/compiler with slot co-location | Apply Prompt 7 | WORKSTREAM-07 | FACT | high |
| TASK-08 | Run/adapt CODEX PROMPT 8: STRUCT model/compile/phys artifacts. | high | after Prompt 6; can follow Prompt 7 | Codex | Pose/anchors, budgets, graph toolkit helpful | Existing STRUCT/BUILD code | Structure authoring and compiled artifacts | Apply Prompt 8 | WORKSTREAM-05 | FACT | high |
| TASK-09 | Run/adapt CODEX PROMPT 9: DECOR system. | medium-high | after Prompts 6–8 | Codex | Host catalogs from TRANS/STRUCT; LOD | Decor/signage content schemas | Host-agnostic decor model and compiler | Apply Prompt 9 | WORKSTREAM-07 | FACT | high |
| TASK-10 | Run/adapt CODEX PROMPT 10: agents/sensors/minds/actions/groups. | high | after foundational IO/LOD/action prompts | Codex | Prompts 2–5; action/delta pipeline | Existing AGENT/JOB code | Generic behavior substrate | Apply Prompt 10 | WORKSTREAM-03 | FACT | high |
| TASK-11 | Run/adapt CODEX PROMPT 11: graph toolkit and rebuild harness. | high | before heavy graph solvers/comms | Codex | Scheduler/budgets | Existing graph needs | Canonical graph core, dirty sets, rebuild harness | Apply Prompt 11 | WORKSTREAM-04 | FACT | high |
| TASK-12 | Run/adapt CODEX PROMPT 12: domains, frames, propagators. | medium-high | after LOD/graph foundations | Codex | Prompts 5 and 11 | World model state | Generic domain/frame/propagator primitives | Apply Prompt 12 | WORKSTREAM-06 | FACT | high |
| TASK-13 | Run/adapt CODEX PROMPT 13: observer/knowledge/visibility/comms. | medium-high | after agents/graphs/domains | Codex | Prompts 10–12; compiled surface stubs | Visibility and comms requirements | Generic information model | Apply Prompt 13 | WORKSTREAM-06 | FACT | high |
| TASK-14 | Run/adapt CODEX PROMPT 14: determinism hardening, replay, regression. | highest | after core prompts exist | Codex | Prompts 1–13 | Test harness state | Hash/replay validation and regression suite | Apply Prompt 14 | WORKSTREAM-08 | FACT | high |
| TASK-15 | Run documentation validation prompt. | high | after specs are created/updated | Codex | Docs from Prompt 1 and subsequent prompts | Repository docs | Normalized docs and docs/DOCS_VALIDATION_REPORT.md | Run docs prompt | WORKSTREAM-09 | FACT | high |
| TASK-16 | Generate subsystem-specific physics prompts. | medium | after core spine | Assistant/Codex | Prompt 1–14 foundations | Physics subsystem priorities | Codex prompts for heat/power/fluids/atmo/vehicles/structures | Ask user which physics domain to prompt next | WORKSTREAM-02 | INFERENCE | medium |
| TASK-17 | Decide VM-only versus native-code plugin policy. | high | before plugin ABI implementation | User/architect | Security/performance/modding requirements | User decision | Final mod execution policy | Ask only when implementation requires it | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED | high |


### Constraint Register
| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-01 | Domino Engine must be ISO C89 only. | language | hard | User opening constraints | No C99/C++ constructs in engine core. | High: Codex may use modern C by default. | high | FACT |
| CONSTRAINT-02 | Dominium UI/tools must use portable C++98 subset. | language/layering | hard | User opening constraints | UI/tools can be C++ but must not mutate engine directly. | Medium. | high | FACT |
| CONSTRAINT-03 | No OS/platform APIs inside engine code. | layering/portability | hard | User opening constraints | Use dsys abstraction outside engine; engine stays portable. | High if implementation adds file/thread/time APIs. | high | FACT |
| CONSTRAINT-04 | No rendering/UI APIs inside engine code. | layering | hard | User opening constraints | Simulation emits probes/render intents; Dominium/dgfx handle visualization. | Medium. | high | FACT |
| CONSTRAINT-05 | No floats where determinism matters; use fixed-point Q formats. | determinism/math | hard | User opening constraints | All deterministic math and solvers must be fixed-point. | High for geometry/physics code. | high | FACT |
| CONSTRAINT-06 | No platform-dependent behavior. | determinism | hard | User opening constraints | Explicit endian, sizes, sorted iteration, no raw memory hashing. | High. | high | FACT |
| CONSTRAINT-07 | No hardcoded gameplay semantics; everything data-driven. | architecture | hard | User opening constraints | Engine uses generic registries/type IDs/TLV/action pipeline. | High if implementations branch on game concepts. | high | FACT |
| CONSTRAINT-08 | Use TLV-versioned content formats and commands. | data/versioning | hard | User opening constraints and prompt plan | Schemas, remap, canonicalization required. | Medium. | high | FACT |
| CONSTRAINT-09 | Deterministic scheduler, replay, and lockstep multiplayer are core requirements. | simulation/multiplayer | hard | User opening constraints | Only deterministic inputs/seeds/content IDs should drive simulation. | High. | high | FACT |
| CONSTRAINT-10 | Stable IDs and canonical ordered iteration are mandatory. | determinism | hard | User and prompt plan | No unordered container iteration in deterministic paths. | High. | high | FACT |
| CONSTRAINT-11 | Bounded work per tick with deterministic carryover. | performance/determinism | hard | User/sister prompt and prompt plan | All heavy systems use budgets, queues, accumulators. | High. | high | FACT |
| CONSTRAINT-12 | No tolerance-based solvers in deterministic paths. | determinism/math | hard | Sister prompt and prompt plan | Fixed iterations or exact construction only. | High in geometry/physics. | high | FACT |
| CONSTRAINT-13 | State mutation only through sorted delta commit. | determinism/architecture | hard in plan | Prompt plan | Subsystems emit deltas, commit phase applies. | High if direct writes slip in. | medium-high | INFERENCE |
| CONSTRAINT-14 | All heavy systems must participate in replay/hash validation. | determinism/testing | hard in plan | Prompt 14 | Desync localization and reproducibility. | Medium. | medium-high | INFERENCE |
| CONSTRAINT-15 | No global grid dependency in engine logic. | placement | hard | Sister prompt | Grids are optional UI snapping aids only. | High if BUILD/TRANS assumes tiles. | high | FACT |
| CONSTRAINT-16 | All placement must use quantized fixed-point pose + parametric anchors. | placement/determinism | hard | Sister prompt and Prompt 6 | Commands store anchors/params, not unquantized geometry. | High. | high | FACT |
| CONSTRAINT-17 | Baked/world-space geometry is never authoritative state. | source-of-truth | hard | Sister prompt and plan | Compiled artifacts are rebuildable caches. | High. | high | FACT |
| CONSTRAINT-18 | TRANS corridor co-location must use cross-section slots, not stacked independent splines. | TRANS/placement | hard | Sister prompt and Prompt 7 | Shared corridors pack occupants into slots. | Medium-high. | high | FACT |
| CONSTRAINT-19 | DECOR must be host-agnostic and support rulepacks plus manual overrides. | DECOR | hard | Sister prompt and Prompt 9 | Works on terrain, corridors, structures, rooms, sockets. | Medium. | high | FACT |
| CONSTRAINT-20 | Space/war features must be generalized, not hardcoded. | architecture/DLC | hard in plan | User requested core coherence after DLC discussion | Core primitives only; DLCs via content/plugins. | Medium. | high | FACT |
| CONSTRAINT-21 | Knowledge/fog must be simulation state, not renderer trick. | information model | hard in plan | Prompt 13 | Observer-filtered queries and hashed belief DB. | Medium-high. | medium-high | INFERENCE |
| CONSTRAINT-22 | Comms latency and routing must be tick-based and deterministic. | information model | hard in plan | Prompt 13 | Integer latency, stable routes, deterministic queues. | Medium. | medium-high | INFERENCE |
| CONSTRAINT-23 | Codex prompts must not implement gameplay semantics early. | process | hard for prompt use | Each generated prompt repeats this scope guard | Infrastructure prompts only. | Medium-high. | high | FACT |
| CONSTRAINT-24 | Documentation must be internally consistent and authoritative. | documentation/process | hard for docs prompt | User requested docs validation prompt | Docs need conflict resolution and validation report. | Medium. | high | FACT |
| CONSTRAINT-25 | This report package is for this chat only. | reporting/source scope | hard | Current user request | Do not summarize whole Project except labeled project context. | Medium. | high | FACT |


### Open Questions Register
| ID | Question / issue | Why it matters | Known information | Unknown information | What would resolve it | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | Should deterministic behavior/mod intelligence be VM-only or allow native-code plugins? | Plugin policy affects security, determinism, ABI, modding power. | Plan supports deterministic VM and mentions optional native plugins. | Final user policy not provided. | Ask user before implementing native plugin ABI beyond stubs. | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | What exact fixed-point Q formats should each subsystem use? | Precision/overflow/range choices affect correctness and determinism. | Examples Q16.16/Q24.8/Q48.16 were mentioned. | No full Q-format table exists. | Create numeric spec after subsystem ranges are known. | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | What is the actual repository structure and build system? | Prompts assume paths and CMake. | Prompts propose source/domino and docs paths. | Repo was not inspected in this chat. | Inspect repository before applying prompts. | high | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | How much of RES/TLV already exists? | Prompt 2 depends on TLV schema plumbing. | User requires TLV-versioned formats. | Actual implementation unknown. | Inspect RES/TLV code. | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | How should subsystem-specific physics solvers be sequenced after core prompts? | Physics stack remains top-level only. | Core primitives cover graphs/fields/scheduler. | No heat/power/fluid-specific prompt sequence yet. | Ask user priority or generate after core implementation. | medium | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | What exact agent component schemas and archetype TLVs are required first? | Prompt 10 provides generic component registry, not full content schema. | Component categories were named. | Detailed schemas pending. | Design after core behavior substrate. | medium | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | How aggressive should representation demotion be for each subsystem? | LOD thresholds affect performance and fidelity. | R0/R1/R2/R3 framework established. | Thresholds, priorities, content overrides unknown. | Define after profiling/design requirements. | medium | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | What minimum STRUCT compiler scope is feasible in first implementation? | Full volumetric/building compilers can become large. | Prompt 8 scopes model/compile interfaces and tests. | Existing geometry code unknown. | Inspect repo; implement minimal deterministic artifacts first. | medium | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-09 | How should domain/frame transforms represent rotations exactly? | Domains/frames and pose require deterministic rotations. | Prompt 6 leaves rot representation abstract. | Euler vs fixed quaternion/matrix not decided. | Create pose/frame numeric design decision. | medium-high | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | How should route costs and visibility cache granularity be defined? | Comms and visibility determinism require precise policies. | Prompt 13 specifies stable ties and dirty caches. | Cost schemas/granularity not finalized. | Define content schema and defaults later. | medium | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-11 | What anchor host catalogs already exist or need to be invented? | DECOR and placement depend on host catalogs from TRANS/STRUCT. | Prompt 9 says create stubs if absent. | Actual host catalogs unknown. | Inspect repo and implement minimal catalog interfaces. | medium-high | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| QUESTION-12 | Should derived caches be hashed, excluded, or selectively hashed? | Replay validation balance between cost and coverage. | Prompt 14 says canonical if included; authoritative state primary. | Final policy pending. | Decide in SPEC_DETERMINISM and replay design. | medium | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |


### Artifact Ledger
| ID | Artifact / file / prompt / output | Type | Purpose | Status | Where it came from | Carry forward? | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-01 | Initial global constraints and engine role statement | User prompt/content | Defines assistant role, tone, language constraints, global architecture constraints. | visible in chat; authoritative for this chat | User opening message | yes | Foundation for all later design. | FACT |
| ARTIFACT-02 | Advanced simulation stack architecture | Assistant-generated plan | Top-level architecture for heat, power, fluids, atmospheres, vehicles, structures, mod physics. | produced in chat; not implemented | Assistant response to first task | yes | Needs future subsystem prompts. | INFERENCE |
| ARTIFACT-03 | Agent/actor architecture | Assistant-generated plan | Composition-based agent system with body/motion/needs/health/sense/mind/etc. | produced in chat; not implemented | Assistant response after user focus shift | yes | Basis for Prompt 10. | INFERENCE |
| ARTIFACT-04 | Wildlife/pets/workers/plants/groups architecture | Assistant-generated plan | Intelligence spectrum and group/ecology support. | produced in chat; not implemented | Assistant response to user questions | yes | Accepted by continuation. | INFERENCE |
| ARTIFACT-05 | Arbitrary stimuli/behavior/action architecture | Assistant-generated plan | Typed observations, intents, capabilities, actions, deterministic VM, delta pipeline. | produced in chat; not implemented | Assistant response to arbitrary actor behavior request | yes | Core behavior substrate. | INFERENCE |
| ARTIFACT-06 | Dumb agents/plants performance plan | Assistant-generated plan | Tiered simulation, field/population aggregates, cadence decimation, deterministic promotion. | produced in chat | Assistant response to performance request | yes | Feeds LOD and agents. | INFERENCE |
| ARTIFACT-07 | Engine-wide methodology plan | Assistant-generated plan | Representation ladder, typed IO, budgets, data-driven wiring applied across engine. | produced in chat | Assistant response to whole-engine question | yes | Organizing principle. | INFERENCE |
| ARTIFACT-08 | Summary of required changes | Assistant-generated plan summary | Core engine services, actor changes, cross-subsystem architecture, mod pipeline, UI boundary, specs/tests. | produced in chat | Assistant response to summary request | yes | Useful overview. | INFERENCE |
| ARTIFACT-09 | Building/infrastructure optimization plan | Assistant-generated plan | Building R0/R1/R2/R3, edit buffer, compiled artifacts, pathing, structural promotion. | produced in chat | Assistant response to heavy subsystem question | yes | Feeds Prompts 7–9. | INFERENCE |
| ARTIFACT-10 | Deterministic multiplayer under LOD/budgets plan | Assistant-generated plan | Lockstep inputs, deterministic LOD, budgets/carryover, fixed iteration solvers, canonical containers, replay hashes. | produced in chat | Assistant response to determinism/MP question | yes | Feeds Prompt 14. | INFERENCE |
| ARTIFACT-11 | Interstellar/Wargames foundation plan | Assistant-generated plan | Space/war needs generalized into domains/frames/trajectories/combat-as-actions/knowledge/comms. | produced in chat | Assistant response to DLC introduction | yes | Superseded partly by core-generalized plan. | INFERENCE |
| ARTIFACT-12 | Core generalized domains/frames/propagators/knowledge/comms plan | Assistant-generated plan | Semantic-free primitives for space/war and other systems. | produced in chat | Assistant response to user request for core coherence | yes | Feeds Prompts 12–13. | INFERENCE |
| ARTIFACT-13 | Sister GPT-5.1 requirements prompt | User-provided prompt | Mandatory requirements for arbitrary placement, TRANS/STRUCT/DECOR, signage/markings, determinism/performance, docs outputs. | pasted in chat | User message from sister conversation | yes | High priority requirements. | FACT |
| ARTIFACT-14 | Full new 14-prompt master Codex plan | Assistant-generated prompt plan | Sequential implementation roadmap 1–14. | produced in chat | Assistant response to full new prompt plan request | yes | Current roadmap. | FACT |
| ARTIFACT-15 | CODEX PROMPT 1 — Engine invariants, specs, and scaffolding | Prompt | Create specs, det_invariants header, scaffolding, build integration. | produced in chat | User asked generate prompt 1 | yes | Use first in Codex. | FACT |
| ARTIFACT-16 | CODEX PROMPT 2 — Typed packet ABI + TLV registries | Prompt | Implement packet PODs, deterministic registries, TLV schema plumbing, hashing tests. | produced in chat | User asked Next | yes | Use after Prompt 1. | FACT |
| ARTIFACT-17 | CODEX PROMPT 3 — Scheduler, budgets, queues, delta commit | Prompt | Implement deterministic scheduler spine and commit pipeline. | produced in chat | User asked Next | yes | Use after Prompt 2. | FACT |
| ARTIFACT-18 | CODEX PROMPT 4 — Fields, events, messages | Prompt | Implement deterministic stimulus substrate. | produced in chat | User asked Next | yes | Use after Prompt 3. | FACT |
| ARTIFACT-19 | CODEX PROMPT 5 — Representation ladder/interest/accumulators | Prompt | Implement R0/R1/R2/R3, interest volumes, promotion/demotion, accumulator helpers. | produced in chat | User asked Next | yes | Use after Prompts 3–4. | FACT |
| ARTIFACT-20 | CODEX PROMPT 6 — Pose, anchors, arbitrary placement | Prompt | Implement fixed-point pose, anchors, quantization, placement command contract. | produced in chat | User asked Next | yes | Critical before spatial systems. | FACT |
| ARTIFACT-21 | CODEX PROMPT 7 — TRANS corridors/slots/junctions | Prompt | Implement TRANS authoring/compilation for corridors, slot co-location, junctions. | produced in chat | User asked Next | yes | Use after Prompt 6. | FACT |
| ARTIFACT-22 | CODEX PROMPT 8 — STRUCT buildings/enclosures/carriers/surfaces | Prompt | Implement STRUCT model/compiler artifacts. | produced in chat | User asked Next | yes | Use after Prompt 6/7. | FACT |
| ARTIFACT-23 | CODEX PROMPT 9 — DECOR signage/markings/rulepacks/overrides | Prompt | Implement host-agnostic DECOR model/compiler. | produced in chat | User asked Next | yes | Use after Prompts 6–8. | FACT |
| ARTIFACT-24 | CODEX PROMPT 10 — Agents/sensors/minds/actions/groups | Prompt | Implement generic behavior substrate. | produced in chat | User asked Next | yes | Use after IO/LOD/action foundations. | FACT |
| ARTIFACT-25 | CODEX PROMPT 11 — Unified graph toolkit + rebuild harness | Prompt | Implement canonical graph toolkit and incremental rebuild harness. | produced in chat | User asked Next | yes | Use before heavy graph domains. | FACT |
| ARTIFACT-26 | CODEX PROMPT 12 — Domains, frame graph, propagators | Prompt | Implement semantic-free domains/frames/time propagation. | produced in chat | User asked Next | yes | Use after LOD/graph foundations. | FACT |
| ARTIFACT-27 | CODEX PROMPT 13 — Observer/knowledge/visibility/comms | Prompt | Implement generic information model. | produced in chat | User asked Next | yes | Use after agents/graphs/domains. | FACT |
| ARTIFACT-28 | CODEX PROMPT 14 — Determinism hardening/replay/regression | Prompt | Implement hash/replay validation, sentinels, determinism tests, regression scan. | produced in chat | User asked Next | yes | Use after core prompts. | FACT |
| ARTIFACT-29 | Documentation validation/normalization prompt | Prompt | Validate, normalize, and correct docs; create DOCS_VALIDATION_REPORT.md. | produced in chat | User asked docs up-to-date prompt | yes | Use after specs exist/update. | FACT |
| ARTIFACT-30 | Maximum-fidelity Context Transfer Packet | Report text | High-fidelity state transfer produced before this package request. | produced in chat | User requested context transfer packet | yes | Source material for this package. | FACT |
| ARTIFACT-31 | This final handoff package | Generated files | Markdown/YAML/ZIP package for saving, sharing, aggregation, and future spec-book construction. | created now | Current user request | yes | Download and store with old-chat reports. | FACT |


### Risk Register
| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Repository assumptions may be wrong. | Codex prompts may reference wrong paths/build system. | medium | high | Inspect repository and adapt paths before applying. | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| RISK-02 | Semantic leakage into engine core. | Engine may hardcode game/DLC concepts, reducing extensibility. | medium | high | Use type IDs, TLV, generic primitives, review prompts/tests. | WORKSTREAM-04 | INFERENCE |
| RISK-03 | Over-modularization creates indirection/debug overhead. | Engine becomes harder to reason about or optimize. | medium | medium | Keep few core primitives and data-defined specializations. | WORKSTREAM-04 | INFERENCE |
| RISK-04 | Nondeterministic iteration or raw memory hashing. | Lockstep desyncs and replay mismatch. | high | high | Canonical sorted iteration and hash canonicalized data only. | WORKSTREAM-01 | FACT |
| RISK-05 | Budget deferral changes simulation outcomes instead of latency. | LOD/performance optimization changes game state. | medium | high | Use accumulators and invariant checks. | WORKSTREAM-04 | INFERENCE |
| RISK-06 | Agent behavior becomes unbounded or too expensive. | Large wildlife/worker simulations stall or desync. | medium | high | Instruction budgets, cadence decimation, group controllers, fields. | WORKSTREAM-03 | INFERENCE |
| RISK-07 | Fixed-point overflow/precision errors. | Incorrect physics, geometry, placement, or replay divergence. | medium | high | Define Q-format table and range tests. | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| RISK-08 | PRNG draw count divergence. | Same seed may produce different outcomes across agents/platforms. | medium | high | Use per-entity streams and structured draw policies. | WORKSTREAM-03 | INFERENCE |
| RISK-09 | Grid assumptions re-enter placement/building code. | Arbitrary placement requirement breaks. | medium | high | Regression scan for grid-locked logic; anchors as authority. | WORKSTREAM-07 | FACT |
| RISK-10 | Tolerance-based geometry/physics solvers creep in. | Cross-platform divergence. | medium | high | Fixed-iteration/exact construction only; docs/tests. | WORKSTREAM-02 | FACT |
| RISK-11 | Population/field models lose important individuals incorrectly. | Named/targeted agents vanish or desync. | medium | medium-high | Promotion/demotion invariants and stable IDs. | WORKSTREAM-03 | INFERENCE |
| RISK-12 | Compiled geometry/caches treated as source of truth. | Rebuild/replay inconsistency and loss of parametric editability. | medium | high | Source-of-truth vs derived-cache docs/tests. | WORKSTREAM-05 | FACT |
| RISK-13 | UI/renderer accesses truth instead of observer-filtered state. | Fog/knowledge cheating and replay mismatch. | medium | high | Observer-context query API and probe-only UI. | WORKSTREAM-06 | INFERENCE |
| RISK-14 | Equal-cost comms/visibility routes resolve nondeterministically. | Different machines see different information. | medium | high | Tie-break by stable IDs and canonical graph order. | WORKSTREAM-06 | INFERENCE |
| RISK-15 | DLC-specific concepts contaminate core. | Future content becomes harder to generalize. | medium | medium-high | Keep prompts semantic-free and content-defined. | WORKSTREAM-06 | FACT |
| RISK-16 | TRANS slot packing becomes content-specific rather than generic. | Road/rail/utility semantics hardcode into engine. | medium | medium | Use occupant category/type IDs and TLV parameters only. | WORKSTREAM-07 | INFERENCE |
| RISK-17 | Codex over-implements beyond prompt scope. | Gameplay semantics or unstable code introduced too early. | medium | medium-high | Each prompt says what not to implement; review diffs. | WORKSTREAM-08 | INFERENCE |
| RISK-18 | Documentation drift or contradictions. | Future implementers violate invariants. | medium | high | Run documentation validation prompt and keep validation report. | WORKSTREAM-09 | FACT |
| RISK-19 | This handoff overstates assistant proposals as accepted decisions. | Future assistant may treat tentative architecture as final user mandate. | low-medium | medium | Labels distinguish FACT from INFERENCE and unresolved questions. | WORKSTREAM-09 | INFERENCE |


### Verification Queue
| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Inspect actual repository structure and paths. | Prompts assume source/domino and docs paths. | Repository/file tree inspection. | high | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Confirm build system and language standard enforcement. | Prompts reference CMake and C89/C++98 constraints. | Build files/toolchain inspection. | high | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Confirm no files from prompts have already been created elsewhere. | This chat generated prompts, not repository changes. | Repository status/diff check. | high | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | Confirm existing dsys/dgfx boundaries. | User mentioned dsys/dgfx but repo implementation unknown. | Code/docs inspection. | medium | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Create or verify fixed-point Q-format table. | Numeric correctness depends on explicit ranges/rounding. | SPEC_DETERMINISM or numeric design doc. | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | Verify existing RES/TLV support and schema canonicalization. | Prompt 2 depends on TLV layer. | RES source inspection and tests. | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | Decide deterministic VM versus native plugin policy. | Affects behavior extensibility and ABI/security. | User/architect decision. | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | Verify current AGENT/JOB architecture if present. | Prompt 10 may need adaptation. | Code/docs inspection. | medium | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | Check for existing ad-hoc graph implementations. | Prompt 11 may consolidate them. | Code search. | medium-high | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-10 | Check for nondeterministic containers or raw memory hashing in existing code. | Could violate determinism before prompts. | Static scan/code review. | high | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-11 | Inspect existing BUILD/TRANS/STRUCT/DECOR or equivalents. | Prompts 6–9 may need path/schema adaptation. | Code/docs inspection. | high | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-12 | Confirm existing space/DLC foundations. | User said foundations exist but this chat did not inspect them. | Repository/data/space inspection. | medium | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-13 | Confirm no engine code assumes grid-locked placement. | New requirements demand no global grid dependency. | Static scan/code review. | high | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| VERIFY-14 | Run documentation validation prompt after specs exist. | Docs may be incomplete/contradictory. | Codex docs pass and DOCS_VALIDATION_REPORT.md. | high | WORKSTREAM-09 | FACT |
| VERIFY-15 | Verify this package against original chat if exact prompt wording is needed. | This package summarizes prompts but does not reproduce every word of every prompt. | Manual comparison with transcript. | medium | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |


## 6. Possible Cross-Chat Duplicates

- Base Domino/Dominium language/layering constraints.
- dsys/dgfx architecture.
- TLV content/data format design.
- Physics simulation details.
- Agent/JOB architecture.
- BUILD/TRANS/STRUCT details from earlier or sister chats.

## 7. Possible Cross-Chat Conflicts

- Any chat that assumes grid-locked placement conflicts with this chat.
- Any chat treating baked geometry/meshes as authoritative conflicts with this chat.
- Any chat hardcoding space/war/combat concepts into core engine conflicts with this chat.
- Any chat allowing floats/tolerance solvers in deterministic paths conflicts with this chat.
- Plugin policy may conflict because this chat leaves VM-only vs native plugins unresolved.

## 8. Spec Book Integration Guidance

Feed this chat into chapters on engine invariants, deterministic scheduling/replay, typed IO, representation ladders, arbitrary placement, TRANS/STRUCT/DECOR, agents, graph/field infrastructure, domains/frames/propagators, knowledge/visibility/comms, and documentation governance. Promote hard FACT constraints directly. Promote INFERENCE decisions only after checking other chats or user confirmation. Keep rejected options as guardrails. Do not merge the 14 prompts as implementation truth unless repository execution confirms them.

## 9. Aggregator Warnings

Do not treat proposed file paths as verified repository facts. Do not collapse assistant-inferred decisions into user-stated facts. Do not lose the sister-chat mandatory requirements. Do not forget that no code was executed or inspected in this chat.
