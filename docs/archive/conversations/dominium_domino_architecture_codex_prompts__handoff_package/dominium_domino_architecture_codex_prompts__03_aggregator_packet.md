# Aggregator Packet — Dominium/Domino Architecture and Codex Prompts

## 1. Packet Metadata

- Chat label: Dominium/Domino Architecture and Codex Prompts
- Date anchor: 2026-05-27 Australia/Melbourne
- Source scope: FACT: This visible chat only; no repository files inspected.
- Coverage: Full for visible chat, with implementation caveats.
- Confidence: 4 / 5.
- Staleness risk: Medium.
- Merge priority: High, because this chat contains the prompt roadmap and advanced simulation handoff.
- Main limitations: Generated prompts are artifacts, not implementation proof; exact repo state is UNCERTAIN / UNVERIFIED.

## 2. Ultra-Condensed Carry-Forward Capsule

This chat is a high-value architecture and implementation-roadmap chat for Dominium/Domino. The user began with a master starter prompt defining Domino as a deterministic, fixed-point, ISO C89 engine and Dominium as a portable C++98 product suite. Hard constraints include strict layering, dsys for platform abstraction, dgfx for rendering, no OS-native drawing, no platform variance in simulation, stable ABI, versioned TLV formats, replay/network determinism, and full backward/forward compatibility for saves/packs/mods/tools.

The chat expanded from resources/entities/items/recipes into the complete engine and product architecture. A major accepted pattern is Core + Model + Proto + Instance + Registry + TLV. Each subsystem should have generic core APIs, pluggable model vtables, data-only prototypes loaded from packs/mods, runtime instances, registries, and subsystem-scoped save/load. Content must be data-driven: engine/core must not know actual game definitions. The user explicitly corrected the assistant before Prompt 8: actual data definitions belong in base/mods/packs. This is one of the most important carry-forward rules.

The dres resource system was introduced from another chat and became the baseline: resource core stores generic channels and values/deltas; resource models implement strata/reservoir/vegetation/soil/etc.; content prototypes define deposits/materials/items/processes; interaction systems call APIs like sample/apply_delta. This pattern was generalized to environment, buildings, transport, vehicles, jobs, net/replay, and content.

The chat produced a detailed Codex prompt sequence. Prompts 1-7 cover core infrastructure, content/protos, world/res/env/build/trans/struct/vehicle/job, sim/net/replay/view/ui, Dominium common, game, and launcher/setup/tools. After the user requested GUI-first testing and emphasized content separation, Prompts 8-12 added minimal GUI soft-rendering, base pack schemas, a data-driven demo slice, GUI gameplay loop, and determinism/validation. Prompts 13-18 cover world-scale physical systems, logistics/construction/packaging, production/jobs/AI/economy, research/orgs/policies, multiplayer/netcode, and tools/editors.

The user later said they would branch into another conversation and focus on Path D: advanced simulation. A standalone new-chat prompt was generated for heat, power grids, fluids/hydrology/pipe networks, atmosphere/gases, vehicle physics, structural loads/destruction, and mod-extensible deterministic physics. The next chat should use this packet and begin with top-level Path D architecture unless the user asks directly for implementation prompts.

Key risks for aggregation: do not treat generated Codex prompts as completed implementation; do not erase the evolved strictness around engine domain-neutrality; preserve GUI-first preference; preserve the existing-code warning; preserve uncertainty labels.

## 3. Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Engine/core must not know actual gameplay data definitions. | Constraint | DECISION-06 | Central user correction. | FACT | high |
| 2 | Domino C89 / Dominium C++98 split. | Constraint | DECISION-01, DECISION-02 | Language/portability foundation. | FACT | high |
| 3 | Deterministic fixed-point simulation. | Constraint | DECISION-03 | Replay/multiplayer/cross-platform requirement. | FACT | high |
| 4 | GUI-first development preference. | Preference | DECISION-11 | User explicitly rejected CLI-only testing. | FACT | high |
| 5 | Prompts 1-18 are major artifacts. | Artifact | ARTIFACT-09..26 | Implementation roadmap. | FACT | high |
| 6 | Path D advanced simulation is next focus. | Next action | WORKSTREAM-17 | User stated new chat focus. | FACT | high |
| 7 | Existing code may be out of date. | Warning | DECISION-23 | Implementation prompts must reconcile existing code. | FACT | high |
| 8 | Core+Model+Proto+Instance+Registry+TLV pattern. | Architecture | DECISION-07 | Subsystem extensibility pattern. | INFERENCE | medium-high |
| 9 | Use base/base_demo packs for data-driven testing. | Plan | DECISION-12 | Avoid content in engine. | FACT | high |
| 10 | Use spline/packet/container logistics. | Design | DECISION-13, DECISION-14 | Low-CPU realistic transport. | FACT | high |

## 4. Workstream Summaries

### WORKSTREAM-01 — Domino Engine Core Infrastructure
- Objective: Define deterministic C89 engine core with subsystem/model/schema registries, TLV save/load, fixed-point foundations, and strict platform/render abstractions.
- Current state: Architecture and Codex prompts defined; implementation not verified.
- Desired end state: Working C89 core infrastructure with deterministic tick/save/model/content extension points.
- Priority: critical
- Decisions: DECISION-01, DECISION-03, DECISION-04, DECISION-07, DECISION-08, DECISION-09
- Tasks: TASK-02
- Constraints: CONSTRAINT-01, CONSTRAINT-03, CONSTRAINT-04, CONSTRAINT-05, CONSTRAINT-08, CONSTRAINT-09, CONSTRAINT-13, CONSTRAINT-25
- Artifacts: ARTIFACT-09, ARTIFACT-01, ARTIFACT-05, ARTIFACT-07
- Risks: RISK-03, RISK-10
- Open questions: QUESTION-08
- Next action: Verify repo state and use relevant prompt artifacts.

### WORKSTREAM-02 — Dominium Product Suite
- Objective: Define C++98 products on top of Domino: game, launcher, setup, and tools.
- Current state: Architecture and prompts defined; implementation not verified.
- Desired end state: Thin C++98 product layer using Domino APIs without reimplementing engine systems.
- Priority: high
- Decisions: DECISION-02, DECISION-04
- Tasks: None recorded in this chat.
- Constraints: CONSTRAINT-02, CONSTRAINT-05, CONSTRAINT-10
- Artifacts: ARTIFACT-13, ARTIFACT-14, ARTIFACT-15, ARTIFACT-01, ARTIFACT-06
- Risks: RISK-03
- Open questions: None recorded in this chat.
- Next action: Verify repo state and use relevant prompt artifacts.

### WORKSTREAM-03 — Repository, Instance, and Compatibility Model
- Objective: Maintain multi-version products, packs, mods, blueprints, and instances under DOMINIUM_HOME.
- Current state: Canonical layout and compatibility concepts defined.
- Desired end state: Non-destructive repo with multi-version builds/content and explicit compat decisions.
- Priority: high
- Decisions: DECISION-19
- Tasks: None recorded in this chat.
- Constraints: CONSTRAINT-08, CONSTRAINT-09, CONSTRAINT-15
- Artifacts: ARTIFACT-11, ARTIFACT-13, ARTIFACT-01
- Risks: None recorded in this chat.
- Open questions: None recorded in this chat.
- Next action: Verify repo state and use relevant prompt artifacts.

### WORKSTREAM-04 — Content, Packs, Mods, TLV, and Base Pack
- Objective: Keep all gameplay data in packs/mods using TLV schemas and registries.
- Current state: Content model, base pack, base_demo mod prompts defined.
- Desired end state: Validated, versioned content layer where engine sees only IDs/tags/TLV params.
- Priority: critical
- Decisions: DECISION-06, DECISION-10, DECISION-12
- Tasks: TASK-04, TASK-12, TASK-16
- Constraints: CONSTRAINT-07, CONSTRAINT-08, CONSTRAINT-15, CONSTRAINT-20
- Artifacts: ARTIFACT-10, ARTIFACT-17
- Risks: RISK-02, RISK-06
- Open questions: QUESTION-04, QUESTION-07, QUESTION-09
- Next action: Verify repo state and use relevant prompt artifacts.

### WORKSTREAM-05 — DRES Resource System
- Objective: Generic channel-based resource system with model vtables and data-defined deposits.
- Current state: Baseline architecture accepted; implementation prompts generated.
- Desired end state: Resource core independent of ore/oil/tree semantics; models handle strata/reservoir/vegetation/soil.
- Priority: high
- Decisions: None recorded in this chat.
- Tasks: None recorded in this chat.
- Constraints: CONSTRAINT-03, CONSTRAINT-04, CONSTRAINT-16
- Artifacts: ARTIFACT-11, ARTIFACT-18, ARTIFACT-02
- Risks: None recorded in this chat.
- Open questions: None recorded in this chat.
- Next action: Verify repo state and use relevant prompt artifacts.

### WORKSTREAM-06 — Environment, Hydrology, Atmosphere, and Lithology
- Objective: Zone/field-based environmental systems for enclosed spaces, water, gases, heat, light, pollution, radiation, and terrain layers.
- Current state: Architecture developed; Prompt 13 generated.
- Desired end state: Deterministic coarse field/zone/network systems coupled to RES/BUILD/STRUCT/VEH/JOB.
- Priority: high
- Decisions: DECISION-19
- Tasks: None recorded in this chat.
- Constraints: CONSTRAINT-03, CONSTRAINT-04, CONSTRAINT-16
- Artifacts: ARTIFACT-11, ARTIFACT-21
- Risks: None recorded in this chat.
- Open questions: None recorded in this chat.
- Next action: Verify repo state and use relevant prompt artifacts.

### WORKSTREAM-07 — Buildings, Construction, Placement, and Sloped Terrain
- Objective: Support Sims-style buildings, interior zones, machine placement, off-grid anchors, yaw rotation, and realistic terrain foundations.
- Current state: Design defined; prompts generated.
- Desired end state: Player-designed buildings with auto foundations, interior env zones, and generic placement APIs.
- Priority: high
- Decisions: DECISION-16
- Tasks: None recorded in this chat.
- Constraints: CONSTRAINT-03, CONSTRAINT-07
- Artifacts: ARTIFACT-11, ARTIFACT-22
- Risks: None recorded in this chat.
- Open questions: None recorded in this chat.
- Next action: Verify repo state and use relevant prompt artifacts.

### WORKSTREAM-08 — Transport and Logistics Splines
- Objective: Unified spline infrastructure for arbitrary transport modes with endpoints/midpoints, profiles, movers, ports, and low-CPU simulation.
- Current state: Design defined; Prompt 14 generated.
- Desired end state: Generic spline+mover framework for content-defined conveyors/rails/roads/pipes/chutes/etc.
- Priority: high
- Decisions: DECISION-13, DECISION-14, DECISION-15
- Tasks: None recorded in this chat.
- Constraints: CONSTRAINT-03, CONSTRAINT-07, CONSTRAINT-16
- Artifacts: ARTIFACT-11, ARTIFACT-22
- Risks: None recorded in this chat.
- Open questions: None recorded in this chat.
- Next action: Verify repo state and use relevant prompt artifacts.

### WORKSTREAM-09 — Packaging and Containers
- Objective: Aggregate items into crates/bags/pallets/containers to reduce simulation cost while respecting mass/volume/density.
- Current state: Design defined; integrated into Prompt 14.
- Desired end state: Generic container states and packing/unpacking processes, content-defined.
- Priority: medium-high
- Decisions: DECISION-14, DECISION-18
- Tasks: TASK-17
- Constraints: CONSTRAINT-07, CONSTRAINT-15
- Artifacts: ARTIFACT-22
- Risks: RISK-14
- Open questions: QUESTION-11
- Next action: Verify repo state and use relevant prompt artifacts.

### WORKSTREAM-10 — Structures, Machines, and Generic Process Runner
- Objective: Generic structures/machines run data-defined processes via ports, inventories, resources, and networks.
- Current state: Prompts 10 and 15 define minimal and expanded loops.
- Desired end state: Data-driven machine/process execution with no process-specific engine branches.
- Priority: high
- Decisions: DECISION-06, DECISION-12
- Tasks: TASK-05
- Constraints: CONSTRAINT-07, CONSTRAINT-15
- Artifacts: ARTIFACT-11, ARTIFACT-18, ARTIFACT-23
- Risks: None recorded in this chat.
- Open questions: None recorded in this chat.
- Next action: Verify repo state and use relevant prompt artifacts.

### WORKSTREAM-11 — Vehicles and Weapons as Compiled Runtime Objects
- Objective: Allow player-designed vehicles/weapons compiled from module graphs into single runtime protos.
- Current state: Design defined; prompt scaffolding generated.
- Desired end state: Runtime-cheap vehicles/weapons with aggregate physics, damage modules, mount points, and factory production.
- Priority: medium-high
- Decisions: DECISION-17
- Tasks: None recorded in this chat.
- Constraints: CONSTRAINT-03, CONSTRAINT-07
- Artifacts: ARTIFACT-11
- Risks: None recorded in this chat.
- Open questions: None recorded in this chat.
- Next action: Verify repo state and use relevant prompt artifacts.

### WORKSTREAM-12 — Jobs, Agents, AI, and Factory Orchestration
- Objective: Generic job templates, deterministic planner, agent capabilities, and production/logistics orchestration.
- Current state: Prompt 15 generated.
- Desired end state: Agents/workers/vehicles/robots execute jobs deterministically through generic capabilities.
- Priority: high
- Decisions: DECISION-15
- Tasks: None recorded in this chat.
- Constraints: CONSTRAINT-03, CONSTRAINT-15
- Artifacts: ARTIFACT-11, ARTIFACT-23
- Risks: None recorded in this chat.
- Open questions: None recorded in this chat.
- Next action: Verify repo state and use relevant prompt artifacts.

### WORKSTREAM-13 — Research, Organizations, Economy, and Policies
- Objective: Generic research/tech, org ownership, accounts, macro metrics, and policy constraints.
- Current state: Prompt 16 generated.
- Desired end state: Data-defined progression and rules influencing processes, builds, jobs, and org economics.
- Priority: medium-high
- Decisions: None recorded in this chat.
- Tasks: None recorded in this chat.
- Constraints: CONSTRAINT-03, CONSTRAINT-15
- Artifacts: ARTIFACT-24
- Risks: None recorded in this chat.
- Open questions: None recorded in this chat.
- Next action: Verify repo state and use relevant prompt artifacts.

### WORKSTREAM-14 — Multiplayer, Netcode, Replay, and Determinism
- Objective: Deterministic input/command lockstep, TLV net protocol, replay capture, hash-based desync detection.
- Current state: Prompts 12 and 17 generated.
- Desired end state: Host/client deterministic sessions using save snapshots plus command streams.
- Priority: high
- Decisions: DECISION-03, DECISION-20
- Tasks: TASK-07
- Constraints: CONSTRAINT-03, CONSTRAINT-17
- Artifacts: ARTIFACT-12, ARTIFACT-20, ARTIFACT-25
- Risks: RISK-07, RISK-13
- Open questions: None recorded in this chat.
- Next action: Verify repo state and use relevant prompt artifacts.

### WORKSTREAM-15 — GUI, Renderer, View, and UI Framework
- Objective: GUI-first minimal smoke path through dsys -> dgfx soft renderer -> dview -> dui -> Dominium game/launcher.
- Current state: Prompts 8 and 11 generated after user rejected CLI-only testing.
- Desired end state: Minimal graphical window, UI labels, menu, HUD, camera, and debug panels via engine render pipeline.
- Priority: critical
- Decisions: DECISION-05, DECISION-11
- Tasks: TASK-03, TASK-06, TASK-18
- Constraints: CONSTRAINT-06, CONSTRAINT-10, CONSTRAINT-11
- Artifacts: ARTIFACT-12, ARTIFACT-14, ARTIFACT-16, ARTIFACT-19
- Risks: RISK-08
- Open questions: QUESTION-02, QUESTION-10
- Next action: Verify repo state and use relevant prompt artifacts.

### WORKSTREAM-16 — Toolchain, Editors, and Authoring Pipeline
- Objective: World/editor/blueprint/tech/policy/process/transport/structure/item/pack/save/replay/net tools.
- Current state: Prompt 18 generated.
- Desired end state: Full C++98 Dominium editor suite generating deterministic TLV content and validating via engine.
- Priority: medium
- Decisions: DECISION-21
- Tasks: TASK-16
- Constraints: CONSTRAINT-18, CONSTRAINT-15
- Artifacts: ARTIFACT-15, ARTIFACT-26
- Risks: RISK-15
- Open questions: None recorded in this chat.
- Next action: Verify repo state and use relevant prompt artifacts.

### WORKSTREAM-17 — Advanced Simulation Path D
- Objective: Dedicated future focus on heat, power grids, fluids, atmosphere, vehicles, structural loads/destruction, and mod-extensible physics.
- Current state: New-chat starter prompt generated at user request.
- Desired end state: A standalone advanced simulation architecture and/or implementation roadmap.
- Priority: critical
- Decisions: DECISION-03, DECISION-22
- Tasks: TASK-08, TASK-09, TASK-10, TASK-11
- Constraints: CONSTRAINT-03, CONSTRAINT-04, CONSTRAINT-12, CONSTRAINT-13, CONSTRAINT-16
- Artifacts: ARTIFACT-21, ARTIFACT-27
- Risks: RISK-05, RISK-12, RISK-16
- Open questions: QUESTION-03, QUESTION-05, QUESTION-06
- Next action: Start advanced simulation architecture.

### WORKSTREAM-18 — Codex Prompt Roadmap and Chat Handoff
- Objective: Sequence implementation prompts and produce reusable context/report packages for future chats.
- Current state: Prompts 1-18 and previous transfer packet generated; current request creates final package.
- Desired end state: Clean per-chat package usable for continuation and later project spec aggregation.
- Priority: critical
- Decisions: DECISION-23
- Tasks: TASK-01, TASK-13, TASK-14, TASK-15
- Constraints: CONSTRAINT-19, CONSTRAINT-20, CONSTRAINT-21, CONSTRAINT-22, CONSTRAINT-23
- Artifacts: ARTIFACT-28, ARTIFACT-29, ARTIFACT-03, ARTIFACT-04, ARTIFACT-08
- Risks: RISK-01, RISK-04, RISK-09, RISK-11
- Open questions: QUESTION-01, QUESTION-12
- Next action: Verify repo state and use relevant prompt artifacts.


## 5. Registers for Merge

### Decision Register

| ID | Decision | Status | Label | Related workstreams |
| --- | --- | --- | --- | --- |
| DECISION-01 | Domino engine code uses ISO C89. | decided | FACT | WORKSTREAM-01 |
| DECISION-02 | Dominium products/tools/UI use portable C++98 subset. | decided | FACT | WORKSTREAM-02 |
| DECISION-03 | Simulation must be deterministic and fixed-point. | decided | FACT | WORKSTREAM-01, WORKSTREAM-14, WORKSTREAM-17 |
| DECISION-04 | All platform services go through dsys. | decided | FACT | WORKSTREAM-01, WORKSTREAM-02 |
| DECISION-05 | All drawing goes through dgfx/DVIEW/DUI; no OS-native drawing. | decided | FACT | WORKSTREAM-15 |
| DECISION-06 | Engine/core must not know actual gameplay data definitions. | decided | FACT | WORKSTREAM-04, WORKSTREAM-10 |
| DECISION-07 | Use Core + Model + Proto + Instance + Registry + TLV pattern across subsystems. | adopted design | INFERENCE | WORKSTREAM-01 |
| DECISION-08 | Use subsystem registry for init/tick/save/load orchestration. | planned | FACT | WORKSTREAM-01 |
| DECISION-09 | Use unified model registry with model families. | planned | FACT | WORKSTREAM-01 |
| DECISION-10 | Use TLV schema registry and versioned schemas. | planned | FACT | WORKSTREAM-04 |
| DECISION-11 | Prefer GUI-first validation over CLI-only testing. | decided | FACT | WORKSTREAM-15 |
| DECISION-12 | Use a base pack and base_demo mod for data definitions/testing. | planned | FACT | WORKSTREAM-04, WORKSTREAM-10 |
| DECISION-13 | Transport infrastructure uses arbitrary splines with profiles. | adopted design | FACT | WORKSTREAM-08 |
| DECISION-14 | Belts/conveyors should use packets/containers, not per-item tick simulation. | adopted design | FACT | WORKSTREAM-08, WORKSTREAM-09 |
| DECISION-15 | Inserters become generic programmable robot manipulators. | adopted design | FACT | WORKSTREAM-08, WORKSTREAM-12 |
| DECISION-16 | Buildings use a local shell/grid initially, placed in world with arbitrary yaw and generated foundations. | adopted design | INFERENCE | WORKSTREAM-07 |
| DECISION-17 | Vehicles/weapons are designed as blueprints/modules then compiled into single runtime objects. | adopted design | FACT | WORKSTREAM-11 |
| DECISION-18 | Dropped items should be aggregated piles/containers, not thousands of entities. | adopted design | FACT | WORKSTREAM-09 |
| DECISION-19 | Worldgen providers should be modular and DAG/dependency ordered. | planned | FACT | WORKSTREAM-03, WORKSTREAM-06 |
| DECISION-20 | Multiplayer uses deterministic command/input lockstep with TLV protocol. | planned | FACT | WORKSTREAM-14 |
| DECISION-21 | Toolchain should become full editor/authoring ecosystem. | planned | FACT | WORKSTREAM-16 |
| DECISION-22 | Path D advanced simulation is the next new-chat focus. | decided | FACT | WORKSTREAM-17 |
| DECISION-23 | Existing code may be stale and must be reconciled, not duplicated. | decided guidance | FACT | WORKSTREAM-18 |

### Task Register

| ID | Task | Priority | Next step | Related workstreams | Label |
| --- | --- | --- | --- | --- | --- |
| TASK-01 | Inspect actual repository before applying any prompt. | critical | Run source tree and build inspection. | WORKSTREAM-18 | FACT |
| TASK-02 | If not implemented, apply Prompt 1 core infrastructure. | high | Apply/refactor with C89 compliance. | WORKSTREAM-01 | FACT |
| TASK-03 | Implement or reconcile GUI smoke path from Prompt 8. | high | Apply Prompt 8; prefer real backend over stub. | WORKSTREAM-15 | FACT |
| TASK-04 | Finalize content model and base pack autoload. | critical | Apply Prompt 9 after core/TLV infra. | WORKSTREAM-04 | FACT |
| TASK-05 | Build data-driven demo loop from packs/mods. | high | Apply Prompt 10. | WORKSTREAM-10 | FACT |
| TASK-06 | Add GUI gameplay menu/HUD/blueprint placement. | high | Apply Prompt 11. | WORKSTREAM-15 | FACT |
| TASK-07 | Add determinism validation and world hash. | high | Apply Prompt 12. | WORKSTREAM-14 | FACT |
| TASK-08 | Start Path D advanced simulation architecture in new chat. | critical | Use Section 15 bootstrap prompt. | WORKSTREAM-17 | FACT |
| TASK-09 | Design fixed-point solvers for heat/power/fluids/atmosphere. | high | Produce design before coding. | WORKSTREAM-17 | INFERENCE |
| TASK-10 | Reconcile Prompt 13 with Path D architecture. | high | Map systems to subsystems/models. | WORKSTREAM-17 | FACT |
| TASK-11 | Generate Codex prompt(s) for Path D implementation if requested. | medium-high | Ask user if wants architecture-to-Codex conversion. | WORKSTREAM-17 | INFERENCE |
| TASK-12 | Audit engine for domain leakage. | critical | Use prompt 12 style validation/audit. | WORKSTREAM-04 | FACT |
| TASK-13 | Prepare future master Project Spec Book aggregation. | medium | Use aggregator prompt from previous assistant output. | WORKSTREAM-18 | FACT |
| TASK-14 | Preserve this report package with all files and ZIP. | critical | Download and store in chat-specific folder. | WORKSTREAM-18 | FACT |
| TASK-15 | Verify stale external/tool facts before future use. | medium | Do not rely on memory for current external data. | WORKSTREAM-18 | FACT |
| TASK-16 | Define exact TLV schema field tables before coding content tools. | high | Generate/confirm with user. | WORKSTREAM-04, WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |
| TASK-17 | Decide container nesting policy. | medium | Resolve during Prompt 14 implementation. | WORKSTREAM-09 | INFERENCE |
| TASK-18 | Select or implement at least one real GUI platform backend. | high | Implement under dsys. | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |

### Constraint Register

| ID | Constraint | Type | Hard/soft | Label |
| --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Domino engine code must be ISO C89. | language | hard | FACT |
| CONSTRAINT-02 | Dominium code must use portable C++98 subset. | language | hard | FACT |
| CONSTRAINT-03 | Simulation must be deterministic across platforms. | simulation | hard | FACT |
| CONSTRAINT-04 | Use fixed-point Q formats where determinism matters. | math | hard | FACT |
| CONSTRAINT-05 | Platform-specific behavior must be abstracted through dsys. | architecture | hard | FACT |
| CONSTRAINT-06 | Rendering must go through dgfx/DVIEW/DUI. | architecture | hard | FACT |
| CONSTRAINT-07 | Engine/core must not contain actual content definitions. | content | hard | FACT |
| CONSTRAINT-08 | All content formats must be versioned and backward-compatible. | data | hard | FACT |
| CONSTRAINT-09 | Old saves/packs/mods/tools should not be broken. | compatibility | hard | FACT |
| CONSTRAINT-10 | GUI/TUI should share logic/pipelines. | ui | hard | FACT |
| CONSTRAINT-11 | GUI-first testing is preferred for this workflow. | workflow | soft-to-hard | FACT |
| CONSTRAINT-12 | World is toroidal 2^24 m surface with ±2 km vertical. | world | hard | FACT |
| CONSTRAINT-13 | Target platforms include retro and modern systems. | portability | hard | FACT |
| CONSTRAINT-14 | Use vector-only fallback; raster packs optional. | render/content | hard | FACT |
| CONSTRAINT-15 | Packs/mods must be data-driven and registry-based. | content | hard | FACT |
| CONSTRAINT-16 | Worldgen randomness must be seed/coordinate/tick derived. | determinism | hard | FACT |
| CONSTRAINT-17 | Network messages must be TLV-encoded/versioned. | net | hard | FACT |
| CONSTRAINT-18 | Tool outputs must be deterministic. | tools | hard | FACT |
| CONSTRAINT-19 | No treating assistant proposals as final if user did not accept them. | reporting | hard | FACT |
| CONSTRAINT-20 | Important items must be labeled FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT. | reporting | hard | FACT |
| CONSTRAINT-21 | Date anchor is 2026-05-27 Australia/Melbourne. | reporting | hard | FACT |
| CONSTRAINT-22 | Report scope is this chat only. | reporting | hard | FACT |
| CONSTRAINT-23 | Generated final package should include specific seven files and ZIP if possible. | artifact | hard | FACT |
| CONSTRAINT-24 | If facts could change externally, verify before future use. | evidence | hard | FACT |
| CONSTRAINT-25 | Avoid over-engineering past diminishing returns. | architecture | soft | FACT |

### Open Questions Register

| ID | Question | Priority | Related workstreams | Label |
| --- | --- | --- | --- | --- |
| QUESTION-01 | Has any Codex prompt been applied to the actual repository? | critical | WORKSTREAM-18 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | Which GUI/backend dependencies are available? | high | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | Should the new chat produce architecture or Codex prompts for Path D first? | high | WORKSTREAM-17 | INFERENCE |
| QUESTION-04 | How strict is the ban on domain words in engine comments/docs? | medium | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | What fixed-point formats should each advanced simulation domain use? | high | WORKSTREAM-17 | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | How detailed should initial advanced physics solvers be? | high | WORKSTREAM-17 | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | Should deterministic scripting/DSL be implemented before plugin ABI? | medium | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | What build system should Codex modify? | high | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-09 | What exact TLV field tags should become canonical? | medium-high | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | How will retro targets handle GUI smoke tests? | medium | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| QUESTION-11 | What is acceptable nesting depth for containers? | medium | WORKSTREAM-09 | INFERENCE |
| QUESTION-12 | How should existing obsolete code be migrated? | high | WORKSTREAM-18 | UNCERTAIN / UNVERIFIED |

### Artifact Ledger

| ID | Artifact | Type | Status | Carry forward | Label |
| --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Extended Master Starter Prompt — Dominium + Domino | user prompt | active | yes | FACT |
| ARTIFACT-02 | dres modular resource proposal from another chat | user-provided design | accepted as baseline in discussion | yes | FACT |
| ARTIFACT-03 | Complete integrated system summary | assistant output | generated | yes | FACT |
| ARTIFACT-04 | Data/type hierarchy output | assistant output | generated | yes | FACT |
| ARTIFACT-05 | Engine-wide hierarchy output | assistant output | generated | yes | FACT |
| ARTIFACT-06 | Full stack engine+game+launcher+setup+tools+mods hierarchy | assistant output | generated | yes | FACT |
| ARTIFACT-07 | Extensibility refinement pass | assistant output | generated | yes | FACT |
| ARTIFACT-08 | Codex prompt split plan (7 prompts) | assistant output | generated | yes | FACT |
| ARTIFACT-09 | Prompt 1 — Core Infrastructure & Registries | Codex prompt | generated | yes | FACT |
| ARTIFACT-10 | Prompt 2 — Content & Proto Layer | Codex prompt | generated | yes | FACT |
| ARTIFACT-11 | Prompt 3 — World/Res/Env/Build/Trans/Struct/Vehicle/Job | Codex prompt | generated | yes | FACT |
| ARTIFACT-12 | Prompt 4 — DSIM/ECS, Net, Replay, View, UI | Codex prompt | generated | yes | FACT |
| ARTIFACT-13 | Prompt 5 — Dominium Common Layer | Codex prompt | generated | yes | FACT |
| ARTIFACT-14 | Prompt 6 — Game Product | Codex prompt | generated | yes | FACT |
| ARTIFACT-15 | Prompt 7 — Launcher, Setup, Tools | Codex prompt | generated | yes | FACT |
| ARTIFACT-16 | Prompt 8 — Minimal GUI Vertical Slice | Codex prompt | generated | yes | FACT |
| ARTIFACT-17 | Prompt 9 — Base Pack Structure, TLV Schemas, Autoload | Codex prompt | generated | yes | FACT |
| ARTIFACT-18 | Prompt 10 — Data-Driven Playable Minimal Slice | Codex prompt | generated | yes | FACT |
| ARTIFACT-19 | Prompt 11 — Minimal GUI Gameplay Loop | Codex prompt | generated | yes | FACT |
| ARTIFACT-20 | Prompt 12 — Determinism, Validation, Boundaries | Codex prompt | generated | yes | FACT |
| ARTIFACT-21 | Prompt 13 — World-Scale Physical Systems | Codex prompt | generated | yes | FACT |
| ARTIFACT-22 | Prompt 14 — Logistics Splines, Construction, Packaging | Codex prompt | generated | yes | FACT |
| ARTIFACT-23 | Prompt 15 — Production Chains, Jobs/AI, Economy | Codex prompt | generated | yes | FACT |
| ARTIFACT-24 | Prompt 16 — Research, Orgs, Macro-Econ, Policies | Codex prompt | generated | yes | FACT |
| ARTIFACT-25 | Prompt 17 — Multiplayer, Netcode, Sessions | Codex prompt | generated | yes | FACT |
| ARTIFACT-26 | Prompt 18 — Toolchain & Editors | Codex prompt | generated | yes | FACT |
| ARTIFACT-27 | New Chat Advanced Simulation Starter Prompt | bootstrap prompt | generated | yes | FACT |
| ARTIFACT-28 | Maximum-fidelity Context Transfer Packet | handoff document | generated | yes | FACT |
| ARTIFACT-29 | Final report package request and generated files | report package | in progress | yes | FACT |

### Risk Register

| ID | Risk | Severity | Mitigation | Label |
| --- | --- | --- | --- | --- |
| RISK-01 | Generated prompts may be mistaken for implemented code. | high | Treat all implementation state as UNVERIFIED until repo inspection. | FACT |
| RISK-02 | Domain data leaks into engine code. | critical | Audit engine C for domain strings/IDs; move examples to packs/mods/docs. | FACT |
| RISK-03 | Codex uses non-C89/non-C++98 features. | high | Explicit prompt constraints and code review. | FACT |
| RISK-04 | Existing repo code conflicts with generated architecture. | high | Search/reconcile/update rather than duplicate. | FACT |
| RISK-05 | Advanced simulation becomes too detailed and unstable. | high | Use coarse bounded solvers and fixed-point stability analysis. | INFERENCE |
| RISK-06 | TLV schemas fragment into incompatible versions. | high | Central schema registry and DATA_FORMATS spec. | FACT |
| RISK-07 | World hash includes pointers/padding. | high | Hash logical sorted values only. | FACT |
| RISK-08 | GUI-first path blocked by missing platform backend. | medium-high | Implement soft renderer + at least one dsys backend; stub only temporarily. | UNCERTAIN / UNVERIFIED |
| RISK-09 | Assistant proposals treated as user-decided final specs. | medium | Preserve labels and request confirmation when needed. | FACT |
| RISK-10 | Over-abstraction slows implementation. | medium | Follow minimum stable interfaces and avoid reflection/VM-everything unless needed. | INFERENCE |
| RISK-11 | Future aggregator merges conflicting chats prematurely. | medium-high | Preserve provenance, labels, and conflict registers. | FACT |
| RISK-12 | Retro platform constraints ignored in advanced systems. | high | Keep memory/fixed-point/backends minimal and feature-scalable. | FACT |
| RISK-13 | Network protocol becomes ad-hoc binary structs. | high | Use TLV message schemas only. | FACT |
| RISK-14 | Containers allow unbounded nesting/state explosion. | medium | Set nesting limits and O(1) bulk defaults. | INFERENCE |
| RISK-15 | Tool outputs non-deterministic packages. | medium | Sort keys/files/IDs and stable serialize. | FACT |
| RISK-16 | Advanced sim cross-coupling creates circular tick dependencies. | high | Define dependency graph and fixed solver phases. | INFERENCE |

### Verification Queue

| ID | Item | Priority | Related workstreams | Label |
| --- | --- | --- | --- | --- |
| VERIFY-01 | Actual repository state and whether any prompts were applied. | critical | WORKSTREAM-18 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Available build system and target configuration. | high | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Availability of GUI backend dependency such as SDL2. | high | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | Existing content/TLV code compatibility. | high | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Exact TLV schema IDs and field tags before formal spec. | medium-high | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | Fixed-point numeric ranges for heat/power/fluid solvers. | high | WORKSTREAM-17 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | Whether engine comments/docs may use domain examples. | medium | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | World hash determinism across platforms. | high | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | Retro-target feasibility for memory-heavy systems. | medium | WORKSTREAM-17 | UNCERTAIN / UNVERIFIED |
| VERIFY-10 | Content validation can catch all references/dependencies. | medium-high | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-11 | Dominium Common path/FS wrappers obey dsys abstraction. | medium | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-12 | Networking transport callbacks cover target platforms. | medium | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| VERIFY-13 | Toolchain deterministic output guarantees. | medium | WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |
| VERIFY-14 | Whether user wants next chat to generate architecture or prompt for Path D. | medium-high | WORKSTREAM-17 | INFERENCE |

## 6. Possible Cross-Chat Duplicates

- Domino core architecture.
- DRES resource system.
- Environment/hydrology/advanced simulation.
- Content/TLV/modding.
- GUI/rendering.
- Product suite and repository layout.
- Tools/editors.

## 7. Possible Cross-Chat Conflicts

- Strictness of domain-neutrality in engine code.
- Exact TLV schema IDs/fields.
- Actual repo code vs prompt assumptions.
- Initial local-grid building model vs any future freeform/CAD building model.
- Solver fidelity for advanced simulation.

## 8. Spec Book Integration Guidance

This chat should feed chapters on architecture philosophy, engine core, product suite, content/modding, resource systems, logistics, buildings, determinism, and advanced simulation. Formalize C89/C++98, fixed-point determinism, no engine content semantics, dsys/dgfx layering, and TLV versioning as requirements. Keep example demo content and prompt sequence as background unless implementation begins. Verify repo state before converting prompt assumptions into implementation-status claims.

## 9. Aggregator Warnings

- Do not treat prompt artifacts as implemented code.
- Do not merge assistant suggestions into final spec without checking whether user accepted them.
- Preserve the GUI-first correction.
- Preserve the existing-code-may-be-stale warning.
- Preserve uncertainty labels and source provenance.
