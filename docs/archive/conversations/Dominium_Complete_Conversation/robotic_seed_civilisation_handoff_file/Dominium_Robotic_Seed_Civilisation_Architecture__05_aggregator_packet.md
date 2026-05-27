# Aggregator Packet — Dominium Robotic Seed-Civilisation Architecture

## Packet Metadata

* Chat label: Dominium Robotic Seed-Civilisation Architecture
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: This chat only unless labelled PROJECT-CONTEXT
* Coverage: Partial / unclear; visible chat and uploaded preservation prompt available
* Confidence: 4/5 for visible chat
* Staleness risk: Medium
* Merge priority: High for Dominium concept/spec book
* Main limitations: Assistant suggestions must not be merged as user decisions unless ratified; external facts need verification.

## Ultra-Condensed Carry-Forward Capsule

This chat should be merged as the core concept-development record for Dominium’s robotic seed-civilisation direction. It began with a broad feasibility question about creating a deterministic game with full-scale real solar-system scope, procedurally recreated planets, customizable systems, terraforming, cut/fill, megaprojects, machines, factories, fog of war, sparse simulation, MMO persistence, single-player multi-universe support, client-shared compute, and Unreal integration. The assistant recommended a deterministic simulation/database architecture: Domino should own authoritative world state, fixed-tick deterministic logic, sparse procedural data, event logs, snapshots, fog-of-war truth, server authority, and simulation LOD. Unreal, if used, should be a renderer/client/tool layer, not the source of universe truth. This is an assistant recommendation, not yet a user-ratified decision.

The user then provided the most important creative direction. The world should initially be a procedural star/solar system rather than a galaxy. Designers should set realistic parameters and use science-bounded sliders rather than arbitrary ones. Planet generation should produce terrain and planetary conditions procedurally, while allowing targeted overrides and painted fields. The user also proposed reverse generation: design the planet outcome, then make the orbital/planetary parameters fit plausibly. A common field-layer technology should support worldgen, data overrides, save files, mod packs, painted fields, terraforming, and construction/destruction deltas.

The central premise is a robotic seedship civilisation. Humans in the past launched a robotic mothership that finds a suitable solar system, lands on the most habitable planet, and manufactures robot bodies using nanotechnology to restart civilisation. Players spawn as robots from physical fabrication machines and can choose chassis such as biped, quadruped, spider, or tank-like bodies. Expansion is tied to building remote spawn labs using local raw materials. The mothership contains human knowledge, explaining why players can access recipe/blueprint knowledge for CPUs, railways, calendars, and advanced technologies. It must not be an unlimited factory: its reserves, throughput, heat dissipation, scale, and mission reserves should be constrained, forcing players into mining, refining, factories, cities, and replenishment.

A major design decision is automation-first civilisation. The user considered worker NPCs but rejected/deprioritised them because labour simulation means pathfinding, physics, scheduling, and expensive compute. Instead, computers, AI agents, nanobots, and machines should do the work. The user wants machines/factories/vehicles/rockets to be player-creatable but compiled into functional objects or process graphs: inputs, ticks, outputs, power, heat, throughput, and constraints. High-detail visuals can appear locally, but the authoritative simulation should be sparse, collapsed, and deterministic.

This chat contributes requirements candidates for the master spec: science-bounded procedural generation; layered field data; robot player bodies; physical spawn labs; resource-limited mothership; nanobot/HUD blueprint construction; no worker NPC core economy; machine process graph compiler; fog-of-war by sensors; and first playable slice from mothership spawn to remote spawn lab. Open questions include generator science bounds, reverse generation, field schema, mothership balance, chassis stats, nanobot limits, machine compiler rules, city liveliness without NPCs, Unreal integration, and MMO mode architecture. The recommended next action is to create the Dominium First Playable Slice Spec.

## Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
|---|---|---|---|---|---|---|
| P0 | Robotic seed-civilisation premise | Creative pillar | DECISION-05 | Unifies lore, respawn, HUD, automation, and progression. | FACT | 5 |
| P0 | Science-bounded procedural planets | System requirement | DECISION-02 | Defines the worldgen/editor identity. | FACT | 5 |
| P0 | Field layers for generation/saves/packs/terraforming | Data architecture | DECISION-04 | Unifies creation, persistence, and terrain change. | FACT + INFERENCE | 4 |
| P0 | Mothership as knowledge source but limited fabricator | Progression requirement | DECISION-06 | Explains recipes without erasing industry. | FACT | 5 |
| P0 | Automation-first/no worker NPC economy | Simulation constraint | DECISION-08 | Controls compute and reinforces robot premise. | FACT | 5 |
| P0 | Machine compiler/process graphs | Simulation requirement | DECISION-09 | Enables player machines without per-part simulation. | FACT | 5 |
| P0 | First playable slice to remote spawn lab | Prototype plan | DECISION-12 | Best next step to test the whole concept. | INFERENCE | 4 |

## Workstream Summaries

### WORKSTREAM-01 — Deterministic Domino simulation architecture
* Objective: Define Domino as the deterministic authoritative simulation core, with renderer clients downstream.
* Current state: Discussed conceptually; assistant recommended fixed-tick/event-sourced/sparse architecture.
* Desired end state: A clear engine architecture spec separating simulation, persistence, networking, and rendering.
* Priority: P0
* Decisions: DECISION-11
* Tasks: None directly
* Constraints: see Constraint Register.
* Artifacts: ARTIFACT-04 and ARTIFACT-05 are most relevant unless otherwise stated.
* Risks: RISK-01
* Open questions: None directly
* Next action: Convert to spec requirements and acceptance criteria.

### WORKSTREAM-02 — Science-bounded procedural star-system and planet generation
* Objective: Generate plausible solar systems/planets from physical parameters, with bounded design controls and optional reverse generation.
* Current state: User explicitly described procedural generation with realistic sliders, designer tweaks, and reverse fitting.
* Desired end state: A generator/editor spec with hard validity, soft plausibility, gameplay overrides, and reproducible seeds.
* Priority: P0
* Decisions: DECISION-01, DECISION-02, DECISION-03
* Tasks: TASK-02
* Constraints: see Constraint Register.
* Artifacts: ARTIFACT-04 and ARTIFACT-05 are most relevant unless otherwise stated.
* Risks: RISK-01
* Open questions: QUESTION-01, QUESTION-02
* Next action: Convert to spec requirements and acceptance criteria.

### WORKSTREAM-03 — Field-layer planet data, saves, packs, and terraforming
* Objective: Use common layered fields for procedural terrain, painted overrides, saves, mod packs, and gameplay terraforming.
* Current state: User proposed overlaying procedural fields with painted fields and using similar tech for saves/packs/terraforming; assistant formalized layer stack.
* Desired end state: A versioned field stack with conservation rules for gameplay layers and non-conservation for editor layers.
* Priority: P0
* Decisions: DECISION-04
* Tasks: TASK-03
* Constraints: see Constraint Register.
* Artifacts: ARTIFACT-04 and ARTIFACT-05 are most relevant unless otherwise stated.
* Risks: RISK-01, RISK-09
* Open questions: QUESTION-03
* Next action: Convert to spec requirements and acceptance criteria.

### WORKSTREAM-04 — Robotic seedship lore, recipe book, and spawn economy
* Objective: Make players robot bodies fabricated by a mothership/spawn labs, with the ship providing knowledge but limited resources/throughput.
* Current state: User developed mothership, robot spawn, body selection, recipe book, finite ship reserves, and remote spawn labs.
* Desired end state: A concrete lore/gameplay loop connecting respawn, exploration, industrialization, and progression.
* Priority: P0
* Decisions: DECISION-05, DECISION-06, DECISION-10
* Tasks: TASK-04, TASK-05
* Constraints: see Constraint Register.
* Artifacts: ARTIFACT-04 and ARTIFACT-05 are most relevant unless otherwise stated.
* Risks: RISK-01, RISK-04
* Open questions: QUESTION-04, QUESTION-05
* Next action: Convert to spec requirements and acceptance criteria.

### WORKSTREAM-05 — Nanobot construction, blueprinting, cut/fill, and inventory
* Objective: Provide diegetic robot HUD, blueprint previews, nanobot-assisted cut/fill/building, and physical but generous robot logistics.
* Current state: User proposed nanobots as cheap-to-compute invisible force, blueprint stages, cut/fill, and robot carrying capacity.
* Desired end state: A validated staged construction workflow: preview, plan, reserve, stage, execute, commit, operate.
* Priority: P0
* Decisions: DECISION-07
* Tasks: TASK-06
* Constraints: see Constraint Register.
* Artifacts: ARTIFACT-04 and ARTIFACT-05 are most relevant unless otherwise stated.
* Risks: RISK-01, RISK-03
* Open questions: QUESTION-06
* Next action: Convert to spec requirements and acceptance criteria.

### WORKSTREAM-06 — Automation, machines, factories, and process graphs
* Objective: Avoid expensive worker NPCs and per-part machine simulation by making machines compile into functional graphs/equations.
* Current state: User explicitly deprioritised labour NPCs/pathfinding and wanted process diagrams: input, tick, output.
* Desired end state: A machine compiler and factory simulation model with active visual mode and collapsed aggregate mode.
* Priority: P0
* Decisions: DECISION-08, DECISION-09, DECISION-10
* Tasks: TASK-07
* Constraints: see Constraint Register.
* Artifacts: ARTIFACT-04 and ARTIFACT-05 are most relevant unless otherwise stated.
* Risks: RISK-01, RISK-05, RISK-06
* Open questions: QUESTION-07, QUESTION-08
* Next action: Convert to spec requirements and acceptance criteria.

### WORKSTREAM-07 — Fog of war, sensors, and information security
* Objective: Ensure players/clients only know what sensors, communications, and faction maps reveal.
* Current state: Initial user asked for fog of war and sensing-limited simulation; assistant expanded server-side truth filtering.
* Desired end state: A formal observed/last-known/unknown/secret information model.
* Priority: P1
* Decisions: None directly
* Tasks: TASK-09
* Constraints: see Constraint Register.
* Artifacts: ARTIFACT-04 and ARTIFACT-05 are most relevant unless otherwise stated.
* Risks: RISK-01, RISK-07
* Open questions: None directly
* Next action: Convert to spec requirements and acceptance criteria.

### WORKSTREAM-08 — Single-player, private servers, official MMO, and distributed authority
* Objective: Support single-player multi-universe play plus an official persistent MMO star system if feasible.
* Current state: User explicitly wanted single-player across instantiated universes or MMO canonical server; initial query asked about millions/shards/client compute.
* Desired end state: Mode-specific architecture and balance rules, including authority, sharding, persistence, and anti-cheat.
* Priority: P1
* Decisions: None directly
* Tasks: TASK-11
* Constraints: see Constraint Register.
* Artifacts: ARTIFACT-04 and ARTIFACT-05 are most relevant unless otherwise stated.
* Risks: RISK-01, RISK-07, RISK-10
* Open questions: QUESTION-09
* Next action: Convert to spec requirements and acceptance criteria.

### WORKSTREAM-09 — Unreal and renderer/client role
* Objective: Evaluate Unreal as renderer/client/tooling rather than authoritative deterministic universe engine.
* Current state: Assistant repeatedly recommended Unreal as client/renderer while Domino owns deterministic truth; user has not formally accepted.
* Desired end state: A documented Unreal integration boundary and verification-backed capability matrix.
* Priority: P1
* Decisions: DECISION-11
* Tasks: TASK-10
* Constraints: see Constraint Register.
* Artifacts: ARTIFACT-04 and ARTIFACT-05 are most relevant unless otherwise stated.
* Risks: RISK-01, RISK-08
* Open questions: QUESTION-10
* Next action: Convert to spec requirements and acceptance criteria.

### WORKSTREAM-10 — Vertical slice and spec-book preparation
* Objective: Convert brainstorm into a first playable loop and future master spec-book material.
* Current state: Assistant proposed a vertical slice: mothership spawn, survey, mine, cut/fill, power, refinery, remote spawn lab.
* Desired end state: A prioritized requirements document and prototype plan.
* Priority: P0
* Decisions: DECISION-12
* Tasks: TASK-01, TASK-08, TASK-12
* Constraints: see Constraint Register.
* Artifacts: ARTIFACT-04 and ARTIFACT-05 are most relevant unless otherwise stated.
* Risks: RISK-01, RISK-02, RISK-11
* Open questions: None directly
* Next action: Convert to spec requirements and acceptance criteria.

## Compact Registers for Merge

### Decisions

| ID | Decision | Status | Label |
|---|---|---|---|
| DECISION-01 | The main playable setting should start as a procedurally generated star/solar system, not a fully simulated galaxy. | Tentative user design direction | FACT |
| DECISION-02 | Planet/system generation should be science-bounded, using plausible parameters rather than arbitrary sliders. | User-stated design direction | FACT |
| DECISION-03 | The editor should allow both forward generation from orbital/planet parameters and reverse fitting from desired planet outcomes. | Tentative design direction | FACT |
| DECISION-04 | Procedural fields, painted overrides, save files, mod packs, and terraforming should share a common layered data approach. | Tentative design direction | FACT |
| DECISION-05 | Players are robots fabricated by a mothership or remote spawn labs. | Strong user-stated direction | FACT |
| DECISION-06 | The mothership contains knowledge/recipes but is constrained by finite resources, throughput, scale, heat, and replenishment needs. | Tentative user direction, assistant refined | FACT + INFERENCE |
| DECISION-07 | Use nanobots/robot HUD/blueprints as the player-facing construction interface. | Tentative user design direction | FACT |
| DECISION-08 | Avoid worker NPC labour as a core construction/economy system; use automation and AI/process abstraction instead. | Strong user-stated direction | FACT |
| DECISION-09 | Machines/factories should compile into process graphs/equations rather than simulate every physical part continuously. | Strong user-stated direction | FACT |
| DECISION-10 | Cities should be easy to start, but advanced technology should require city-scale industry. | Tentative user direction | FACT |
| DECISION-11 | Domino should own deterministic simulation truth; Unreal, if used, should be a client/renderer/tool layer. | Assistant recommendation, not formally user-ratified | INFERENCE |
| DECISION-12 | A first playable slice should prove one region loop before solar-system/MMO scale. | Assistant recommendation, not formally user-ratified | INFERENCE |

### Tasks

| ID | Task | Priority | Urgency | Related workstream | Label |
|---|---|---|---|---|---|
| TASK-01 | Write a formal one-page creative pillars document for Dominium’s robotic seed-civilisation premise. | P0 | U1 | WORKSTREAM-10 | INFERENCE |
| TASK-02 | Define the generator/editor parameter model: physical sliders, bounds, plausibility scoring, and override rules. | P0 | U1 | WORKSTREAM-02 | FACT + INFERENCE |
| TASK-03 | Design the field-layer stack for procedural base, painted overrides, mod packs, saves, terraforming, construction, and damage. | P0 | U1 | WORKSTREAM-03 | FACT + INFERENCE |
| TASK-04 | Specify mothership constraints: starter resources, throughput, heat, reserve policy, replenishment, and fabrication limits. | P0 | U1 | WORKSTREAM-04 | FACT |
| TASK-05 | Define robot identity, body/chassis types, spawn labs, body fabrication costs, and backup/respawn rules. | P0 | U1 | WORKSTREAM-04 | FACT |
| TASK-06 | Design nanobot blueprint workflow and commit rules for cut/fill/build operations. | P0 | U1 | WORKSTREAM-05 | FACT + INFERENCE |
| TASK-07 | Design the machine compiler/process graph model. | P0 | U1 | WORKSTREAM-06 | FACT |
| TASK-08 | Define the minimal city progression and industrial chain from mothership camp to remote spawn lab. | P0 | U1 | WORKSTREAM-10 | INFERENCE |
| TASK-09 | Create a fog-of-war and sensor truth model. | P1 | U2 | WORKSTREAM-07 | FACT + INFERENCE |
| TASK-10 | Verify current Unreal capabilities and limits before locking the integration plan. | P1 | U2 | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| TASK-11 | Define official MMO vs single-player/private-server differences. | P1 | U2 | WORKSTREAM-08 | FACT + INFERENCE |
| TASK-12 | Build or specify the first deterministic prototype loop: spawn, survey, mine, cut/fill, power, refinery, fabricator, remote spawn lab. | P0 | U1 | WORKSTREAM-10 | INFERENCE |

### Constraints

| ID | Constraint | Hard/soft | Label |
|---|---|---|---|
| CONSTRAINT-01 | Do not treat the whole universe as a normal scene graph or actor list. | Hard | INFERENCE |
| CONSTRAINT-02 | Generation controls should be plausibility-bounded, not arbitrary magic sliders. | Soft-to-hard | FACT |
| CONSTRAINT-03 | Procedural generation should remain overridable with designer/worldgen/packs/terraforming layers. | Hard | FACT |
| CONSTRAINT-04 | Gameplay terraforming/construction should obey resource, energy, and time costs. | Hard recommendation | FACT + INFERENCE |
| CONSTRAINT-05 | Avoid labour NPC pathfinding as a core economic requirement. | Soft-to-hard | FACT |
| CONSTRAINT-06 | Machines must have collapsed/aggregate representations. | Hard recommendation | FACT + INFERENCE |
| CONSTRAINT-07 | Fog-of-war secrets must not be sent to clients in MMO mode. | Hard recommendation | INFERENCE |
| CONSTRAINT-08 | The mothership cannot be an infinite high-throughput fabricator. | Hard design constraint | FACT |
| CONSTRAINT-09 | Unreal should not be assumed to solve deterministic MMO simulation by itself. | Hard recommendation pending verification | INFERENCE |
| CONSTRAINT-10 | Preservation output must remain human-readable and not only machine-readable. | Hard | FACT |

### Open Questions

| ID | Question | Priority | Related workstream | Label |
|---|---|---|---|---|
| QUESTION-01 | What exact realism bounds should the star-system and planet generator enforce? | P0 | WORKSTREAM-02 | FACT + UNCERTAIN / UNVERIFIED |
| QUESTION-02 | How should reverse generation search from desired planet outcomes to plausible parameters? | P1 | WORKSTREAM-02 | FACT |
| QUESTION-03 | What is the exact field-layer schema for terrain, climate, resources, construction, and saves? | P0 | WORKSTREAM-03 | FACT |
| QUESTION-04 | What are the mothership’s finite reserves, fabrication throughput, and replenishment rules? | P0 | WORKSTREAM-04 | FACT |
| QUESTION-05 | What robot chassis exist at launch and how do they differ mechanically? | P0 | WORKSTREAM-04 | FACT |
| QUESTION-06 | How abstract or visible should nanobot construction be? | P0 | WORKSTREAM-05 | FACT |
| QUESTION-07 | What is the minimum machine graph model that lets players create vehicles/rockets/factories without simulating every part? | P0 | WORKSTREAM-06 | FACT |
| QUESTION-08 | How will cities feel alive without intelligent NPC workers? | P1 | WORKSTREAM-06 | INFERENCE |
| QUESTION-09 | How should official MMO, private server, and single-player modes diverge? | P1 | WORKSTREAM-08 | FACT |
| QUESTION-10 | What can Unreal safely own, and what must Domino own? | P1 | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |

### Artifact Ledger

| ID | Artifact | Type | Carry forward | Label |
|---|---|---|---|---|
| ARTIFACT-01 | Initial broad Domino/Dominium feasibility question | User prompt | Yes | FACT |
| ARTIFACT-02 | Assistant architecture response: deterministic simulation/database first | Assistant output | Yes | INFERENCE |
| ARTIFACT-03 | Assistant architecture response: Domino vs Unreal split and real solar-system data sources | Assistant output | Yes | INFERENCE + UNCERTAIN / UNVERIFIED |
| ARTIFACT-04 | User spoken brainstorm transcript about procedural planets, mothership, robots, nanobots, automation, and process graphs | User transcript | Yes | FACT |
| ARTIFACT-05 | Assistant response: robotic seed-civilisation design direction | Assistant output | Yes | INFERENCE |
| ARTIFACT-06 | Pasted text.txt preservation prompt | Uploaded file / prompt | Yes | FACT |
| ARTIFACT-07 | Generated preservation package files | Generated files | Yes | FACT |

### Risk Register

| ID | Risk | Severity | Mitigation | Label |
|---|---|---|---|---|
| RISK-01 | Brainstorm items are accidentally treated as final locked requirements. | High | Preserve FACT/INFERENCE/tentative labels and ask for ratification before locking. | FACT |
| RISK-02 | Scope explosion from solar system + planets + terraforming + cities + machines + MMO. | High | Start with one-region vertical slice and formalize phases. | INFERENCE |
| RISK-03 | Nanobots become magic and erase logistics/progression. | High | Require energy, matter, time, tool capability, range, heat, and permissions. | INFERENCE |
| RISK-04 | Mothership fabrication invalidates industrial gameplay. | High | Define finite reserves, low throughput, heat, scale limits, and mission reserves. | FACT |
| RISK-05 | No NPC workers makes cities feel empty. | Medium | Use drones, dashboards, animated infrastructure, wildlife, and player activity as feedback. | INFERENCE |
| RISK-06 | Player-created machines become lag/exploit machines. | High | Machine compiler, complexity budgets, validation, collapsed representations. | INFERENCE |
| RISK-07 | Fog-of-war data leaks through client compute or replication. | High | Never send hidden truth; clients compute only visible/verifiable work. | INFERENCE |
| RISK-08 | Unreal capability assumptions become stale or wrong. | High | Verify current docs and prototype integration. | UNCERTAIN / UNVERIFIED |
| RISK-09 | Field layers conflict with conservation laws. | High | Separate editor/nonconservative layers from gameplay/conservative layers. | INFERENCE |
| RISK-10 | Official MMO ambitions outpace networking/server budget. | High | Design for distributed regions, not one shared bubble; bound claims. | INFERENCE |
| RISK-11 | Future aggregator merges assistant suggestions as user decisions. | High | Use labels and decision statuses. | FACT |

### Verification Queue

| ID | Item | Priority | Related workstream | Label |
|---|---|---|---|---|
| VERIFY-01 | Current Unreal Engine 5/6 capabilities: LWC, World Partition, MassEntity, Iris, Nanite, runtime mesh/dynamic terrain, networking limits. | P1 | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | JPL Horizons/SPICE/IAU data suitability and licensing for real Solar System recreation. | P1 | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Physical plausibility models for atmosphere retention, climate, orbital stability, tidal locking, magnetospheres, and planet generation. | P1 | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | Determinism risks across CPU/GPU/platforms, floating point, multithreading, and physics. | P0 | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Sparse terrain/voxel/SDF storage and runtime meshing options. | P0 | WORKSTREAM-03 / WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | MMO scalability strategies and realistic player-count claims. | P1 | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | Security model for client-shared compute with fog-of-war and anti-cheat. | P1 | WORKSTREAM-07 / WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |

## Possible Cross-Chat Duplicates

Deterministic simulation architecture, Unreal integration, procedural planet generation, sparse terrain/editable voxels, MMO scaling, fog-of-war networking, and factory graph simulation may overlap with other Dominium chats.

## Possible Cross-Chat Conflicts

Watch for any later choice to include worker NPC labour, unlimited mothership fabrication, Unreal as authoritative universe state, non-science-bounded fantasy planet sliders, or a different player identity than fabricated robots.

## Spec Book Integration Guidance

Use this chat for chapters on creative pillars, world generation, engine architecture, planet data fields, player identity/spawning, construction/terraforming, factories/machines, progression/economy, fog of war, multiplayer modes, and prototype planning. Merge user-stated design directions as requirement candidates. Keep assistant-derived architecture recommendations labelled pending until confirmed. Verify external/engine/science claims before locking them.

## Aggregator Warnings

Do not compress this chat into “procedural solar-system MMO.” The distinctive carry-forward is robotic seed-civilisation plus automation-first simulation. Do not treat all assistant suggestions as final. Do not erase tentative status around Unreal, MMO scale, reverse generation, and exact lore.
