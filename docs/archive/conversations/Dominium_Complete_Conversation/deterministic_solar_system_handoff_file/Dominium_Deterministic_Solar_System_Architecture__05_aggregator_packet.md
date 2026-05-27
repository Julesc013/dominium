## 31. Aggregator Packet

# Aggregator Packet — Dominium Deterministic Solar-System Architecture

## Packet Metadata

* Chat label: Dominium Deterministic Solar-System Architecture
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: This chat only unless labelled PROJECT-CONTEXT
* Coverage: Partial visible transcript plus uploaded preservation prompt
* Confidence: 4/5
* Staleness risk: Medium
* Merge priority: High
* Main limitations: Assistant recommendations are not user decisions; engine/data-source claims require verification; no hidden prior chat context is included.

## Ultra-Condensed Carry-Forward Capsule

This chat should be treated as a high-value conceptual and architectural source for the Dominium Game / Domino engine project. The user began by asking how to build a deterministic, procedural, solar-system-scale construction and civilisation game with full planets, custom systems, terraforming, cut/fill, megaprojects, machines, factories, fog of war, sensed-only simulation, sparse construction/destruction, client-shared compute, single-player multiverse support, and an MMO persistent universe. The user also asked whether Unreal can do this with low latency/high FPS and millions of players across shards or private servers.

The first architectural answer proposed that Domino must be the authoritative deterministic simulation/data core. The world should be represented as seeds, physical parameters, procedural fields, sparse deltas, event logs, snapshots, state hashes, visibility records, machine graphs, and ledgers. Unreal or another engine may render local state but should not own authoritative planetary/MMO truth. This is an assistant recommendation, not user-confirmed, but it aligns with the user’s requirements for determinism, fog of war, sparse simulation, and scale.

The user then provided the strongest creative direction: Dominium is a robotic seed-civilisation game. Humans launched a robotic mothership to another solar system. It lands on a habitable planet and manufactures robot bodies to restart civilisation, possibly before later human biological payloads arrive. Players are robot agents spawned from physical fabrication machines. They can choose body types such as biped, quadruped, spider, or tank-like forms. Expansion depends on building remote spawn labs with materials, power, and fabrication capability.

Planet and star-system generation should be science-bounded. Designers set realistic orbital/planetary parameters, then the system generates terrain, climate, resources, and planetary fields. The user also wants reverse generation: describe a desired planet and let the generator find plausible parameters. Manual painting should not be the main workflow, but procedural fields must be overlayable with painted/designer/mod/gameplay layers. The same field/delta technology should support worldgen, saves, packs, terraforming, and construction.

The chat strongly deprioritised worker NPC labour. The user explicitly said pathfinding/labour is expensive and unnecessary if robots/AI/nanobots do the work. Future specs should not default to human-like worker simulation. Instead, construction and industry should be automation-first: nanobots, AI agents, machine controllers, construction swarms, process diagrams, and factory graphs. The mothership explains HUDs, blueprints, recipes, quest markers, and advanced designs, while finite resources, low throughput, heat, scale limits, and rare material bottlenecks force players to build local industry.

The most important technical gameplay model is sparse/collapsed simulation. Terrain edits are sparse deltas on procedural fields. Machines are visually expanded near players but compile into equations/process graphs when distant. Fog of war is not just graphics: clients should only receive what their robot body, faction, sensors, satellites, or maps can know. Client-shared compute is useful for rendering, mesh generation, visible prediction, and verified non-secret jobs, but public MMO clients should not be trusted with hidden or authoritative state.

The best immediate next action is to formalise a vertical slice: one planet region, one mothership, one robot body, one ore deposit, one power source, one cut/fill/blueprint tool, one nanobot construction swarm, one mine, one refinery, one fabricator, one remote spawn lab, and one fog-of-war sensor model. This slice tests the core loop: spawn, survey, mine, build power, refine, fabricate, transport, construct a remote spawn lab, and respawn/swap there.

## Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| P0 | Domino as deterministic sparse simulation core | Architecture | DECISION-01 | Everything else depends on authoritative replayable world state. | INFERENCE | 4 |
| P0 | Science-bounded procedural planets with overlays | World generation | DECISION-02, DECISION-03 | Defines planet editor, saves, packs, and terraforming. | FACT | 5 |
| P0 | Robotic mothership seed-civilisation premise | Game identity | DECISION-04 | Explains HUD, spawn, recipes, automation, and progression. | FACT | 5 |
| P0 | Automation over worker NPC labour | Simulation model | DECISION-07 | Avoids pathfinding-heavy labour and aligns with robot civilisation. | FACT | 5 |
| P0 | Machine graph/process abstraction | Factory design | DECISION-09 | Allows player-designed machines without simulating every part everywhere. | FACT | 5 |
| P0 | Fog-of-war as data-security model | Multiplayer/simulation | QUESTION-09 | Required for sensed-only simulation and MMO secrecy. | FACT + INFERENCE | 4 |
| P0 | First vertical slice | Roadmap | TASK-13 | Converts giant vision into a testable loop. | INFERENCE | 4 |


## Workstream Summaries

* ID: WORKSTREAM-01
* Name: Deterministic Domino simulation core
* Objective: Define Domino as the authoritative deterministic world simulator, not merely a renderer or Unreal plugin.
* Current state: Brainstormed and strongly recommended; not yet implemented.
* Desired end state: Fixed-tick, replayable, event-sourced core with state hashes, sparse deltas, and validated commands.
* Priority: P0
* Decisions: See Decision Register.
* Tasks: See Task Register.
* Constraints: See Constraint Register.
* Artifacts: See Artifact Ledger.
* Risks: See Risk Register.
* Open questions: See Open Questions Register.
* Next action: Refine into formal spec or vertical-slice plan.

* ID: WORKSTREAM-02
* Name: Scientific star-system and planet generation
* Objective: Generate realistic-bounded star systems and planets from physical parameters, with designer overrides.
* Current state: User described this as a main goal; assistant formalised forward/reverse generation.
* Desired end state: A generator/editor that creates plausible worlds from data and supports carefully bounded tuning and overrides.
* Priority: P0
* Decisions: See Decision Register.
* Tasks: See Task Register.
* Constraints: See Constraint Register.
* Artifacts: See Artifact Ledger.
* Risks: See Risk Register.
* Open questions: See Open Questions Register.
* Next action: Refine into formal spec or vertical-slice plan.

* ID: WORKSTREAM-03
* Name: Field layers, sparse deltas, saves, packs, and terraforming
* Objective: Use the same layered field/delta model for procedural generation, painted overrides, save files, packs, and player terraforming.
* Current state: User proposed overlaying procedural fields with painted fields and reusing save tech for packs; assistant formalised a stack.
* Desired end state: Unified data model for terrain/material/climate/ownership/visibility fields plus gameplay-constrained deltas.
* Priority: P0
* Decisions: See Decision Register.
* Tasks: See Task Register.
* Constraints: See Constraint Register.
* Artifacts: See Artifact Ledger.
* Risks: See Risk Register.
* Open questions: See Open Questions Register.
* Next action: Refine into formal spec or vertical-slice plan.

* ID: WORKSTREAM-04
* Name: Robotic seed-civilisation premise and mothership economy
* Objective: Use a robotic mothership as spawn source, recipe book, lore anchor, and early resource bottleneck.
* Current state: User proposed extensive lore and gameplay role; assistant refined constraints.
* Desired end state: Physical spawn economy where robot bodies and remote spawn labs require power, feedstock, permissions, and fabrication capacity.
* Priority: P0
* Decisions: See Decision Register.
* Tasks: See Task Register.
* Constraints: See Constraint Register.
* Artifacts: See Artifact Ledger.
* Risks: See Risk Register.
* Open questions: See Open Questions Register.
* Next action: Refine into formal spec or vertical-slice plan.

* ID: WORKSTREAM-05
* Name: Robot avatars, bodies, inventory, and respawn
* Objective: Define player identities as robot agents instantiated into manufactured bodies.
* Current state: User proposed multiple robot forms and physical spawning; details remain open.
* Desired end state: Balanced chassis system with body manufacturing, backups, carrying capacity, hardpoints, and meaningful death/respawn rules.
* Priority: P1
* Decisions: See Decision Register.
* Tasks: See Task Register.
* Constraints: See Constraint Register.
* Artifacts: See Artifact Ledger.
* Risks: See Risk Register.
* Open questions: See Open Questions Register.
* Next action: Refine into formal spec or vertical-slice plan.

* ID: WORKSTREAM-06
* Name: Nanobot construction, blueprinting, cut/fill, and terraforming tools
* Objective: Make construction convenient without making it free or nondeterministic.
* Current state: User proposed nanobots, diegetic HUD, blueprinting, cut/fill; assistant added staged validation.
* Desired end state: Preview-plan-reserve-stage-execute-commit pipeline with material, energy, heat, time, and permission costs.
* Priority: P0
* Decisions: See Decision Register.
* Tasks: See Task Register.
* Constraints: See Constraint Register.
* Artifacts: See Artifact Ledger.
* Risks: See Risk Register.
* Open questions: See Open Questions Register.
* Next action: Refine into formal spec or vertical-slice plan.

* ID: WORKSTREAM-07
* Name: Automation, machines, factories, and machine graph compiler
* Objective: Avoid expensive worker NPC simulation by making automation the default and compiling machines into process graphs.
* Current state: User explicitly argued against simulating labour/pathfinding and for process diagrams; assistant expanded.
* Desired end state: Machine and factory systems that operate as graphs/equations when distant and visual/interactive systems when near.
* Priority: P0
* Decisions: See Decision Register.
* Tasks: See Task Register.
* Constraints: See Constraint Register.
* Artifacts: See Artifact Ledger.
* Risks: See Risk Register.
* Open questions: See Open Questions Register.
* Next action: Refine into formal spec or vertical-slice plan.

* ID: WORKSTREAM-08
* Name: Cities, civilisation, economy, and progression
* Objective: Let players build cities easily, while advanced technology requires industrial scale and coordination.
* Current state: User stated cities need to be easy to build and advanced things should require city-scale industry; details remain open.
* Desired end state: Progression from mothership camp to outpost, settlement, industrial city, planetary infrastructure, terraforming, and megaprojects.
* Priority: P1
* Decisions: See Decision Register.
* Tasks: See Task Register.
* Constraints: See Constraint Register.
* Artifacts: See Artifact Ledger.
* Risks: See Risk Register.
* Open questions: See Open Questions Register.
* Next action: Refine into formal spec or vertical-slice plan.

* ID: WORKSTREAM-09
* Name: Fog of war, sensors, and hidden-state security
* Objective: Ensure the game only sends/simulates what players can sense, with remembered and unknown states.
* Current state: User required fog of war and sensed-only simulation; assistant added server-side truth/perception model.
* Desired end state: Visibility system for sensors, maps, last-known data, undiscovered resources, hidden construction, and MMO secrecy.
* Priority: P0
* Decisions: See Decision Register.
* Tasks: See Task Register.
* Constraints: See Constraint Register.
* Artifacts: See Artifact Ledger.
* Risks: See Risk Register.
* Open questions: See Open Questions Register.
* Next action: Refine into formal spec or vertical-slice plan.

* ID: WORKSTREAM-10
* Name: MMO, client compute, shards, and persistence
* Objective: Evaluate single persistent universe, private universes, server authority, and client-shared compute.
* Current state: User asked whether clients can share compute and whether Unreal can support millions; assistant set trust boundaries.
* Desired end state: Distributed authority model with region servers, event logs, interest management, anti-cheat, and safe limited client assistance.
* Priority: P0
* Decisions: See Decision Register.
* Tasks: See Task Register.
* Constraints: See Constraint Register.
* Artifacts: See Artifact Ledger.
* Risks: See Risk Register.
* Open questions: See Open Questions Register.
* Next action: Refine into formal spec or vertical-slice plan.

* ID: WORKSTREAM-11
* Name: Unreal/Raylib/client rendering role
* Objective: Clarify what Unreal can and cannot do for this design.
* Current state: Assistant recommended custom deterministic backend with Unreal as renderer/client; user has not explicitly accepted.
* Desired end state: Renderer bridge where Unreal visualises Domino state but does not own authoritative world truth.
* Priority: P1
* Decisions: See Decision Register.
* Tasks: See Task Register.
* Constraints: See Constraint Register.
* Artifacts: See Artifact Ledger.
* Risks: See Risk Register.
* Open questions: See Open Questions Register.
* Next action: Refine into formal spec or vertical-slice plan.

* ID: WORKSTREAM-12
* Name: Vertical slice and roadmap
* Objective: Turn the huge vision into a testable first playable slice.
* Current state: Assistant proposed a staged prototype; user has not yet responded.
* Desired end state: One planet region with mothership, robot body, survey, ore, power, cut/fill, refinery, fabricator, remote spawn lab, fog of war.
* Priority: P0
* Decisions: See Decision Register.
* Tasks: See Task Register.
* Constraints: See Constraint Register.
* Artifacts: See Artifact Ledger.
* Risks: See Risk Register.
* Open questions: See Open Questions Register.
* Next action: Refine into formal spec or vertical-slice plan.

* ID: WORKSTREAM-13
* Name: Preservation and spec-book handoff
* Objective: Create a report, registers, spec sheet, aggregator packet, and export package for this chat.
* Current state: Triggered by uploaded preservation prompt.
* Desired end state: Downloadable Markdown/YAML/ZIP package plus in-chat reader that can seed future aggregation.
* Priority: P0
* Decisions: See Decision Register.
* Tasks: See Task Register.
* Constraints: See Constraint Register.
* Artifacts: See Artifact Ledger.
* Risks: See Risk Register.
* Open questions: See Open Questions Register.
* Next action: Refine into formal spec or vertical-slice plan.

## Compact Registers for Merge

### Decisions

| ID | Decision | Status | Label |
| --- | --- | --- | --- |
| DECISION-01 | Treat Domino as the authoritative deterministic simulation/data core and rendering as a client layer. | Recommended / not explicitly user-accepted | INFERENCE |
| DECISION-02 | Use science-bounded procedural generation rather than purely arbitrary sliders or manual painting. | User-stated design direction | FACT |
| DECISION-03 | Support procedural fields overlaid with painted/designer/player layers. | User-stated direction, technical details open | FACT + INFERENCE |
| DECISION-04 | Use a robotic seed-ship/mothership premise to explain spawning, recipes, HUD, and automation. | User-stated design premise | FACT |
| DECISION-05 | Make player characters robots with selectable manufactured chassis rather than ordinary humans. | User-stated design direction | FACT |
| DECISION-06 | Use nanobot/automation construction as the main interaction layer, bounded by material, energy, time, and capability. | User-stated direction with assistant constraints | FACT + INFERENCE |
| DECISION-07 | Deprioritise human-like worker NPC labour and use automation/process graphs instead. | Strong user-stated preference / tentative design direction | FACT |
| DECISION-08 | Use the mothership as the recipe book and early precision fabricator, but constrain it with finite resources and throughput. | User-stated direction | FACT |
| DECISION-09 | Represent distant machines/factories as processes/equations rather than simulating all physical parts. | User-stated direction with assistant formalisation | FACT |
| DECISION-10 | Use sparse construction/destruction and collapsed simulation for unseen/unneeded areas. | Core user requirement and assistant recommendation | FACT |
| DECISION-11 | Do not trust clients with hidden information or authoritative MMO results. | Assistant recommendation / not explicitly user-accepted | INFERENCE |
| DECISION-12 | Treat Unreal as useful for presentation/tooling but not as the whole authoritative deterministic MMO engine. | Assistant recommendation / not explicitly user-accepted | INFERENCE |
| DECISION-13 | Make the first serious milestone a small vertical slice, not a full solar-system MMO. | Assistant recommendation / not explicitly user-accepted | INFERENCE |


### Tasks

| ID | Task | Priority | Urgency | Related workstream | Label |
| --- | --- | --- | --- | --- | --- |
| TASK-01 | Write a formal one-page design pillar document for Dominium’s robotic seed-civilisation premise. | P0 | U1 | WORKSTREAM-04, WORKSTREAM-08 | FACT + INFERENCE |
| TASK-02 | Define the deterministic Domino core requirements: ticks, event log, state hashes, command validation, sparse deltas. | P0 | U1 | WORKSTREAM-01 | INFERENCE |
| TASK-03 | Specify the star-system and planet generator parameter schema, including realism/plausibility bounds. | P0 | U1 | WORKSTREAM-02 | FACT + INFERENCE |
| TASK-04 | Design the field-layer and delta operation format for procedural generation, saves, packs, terraforming, and construction. | P0 | U1 | WORKSTREAM-03 | FACT + INFERENCE |
| TASK-05 | Define mothership constraints: starter resources, precision fabrication, throughput, heat, mission reserves, respawn budget. | P0 | U1 | WORKSTREAM-04 | FACT |
| TASK-06 | Define robot chassis/body templates and respawn/back-up rules. | P1 | U1 | WORKSTREAM-05 | FACT + INFERENCE |
| TASK-07 | Specify blueprint and nanobot construction pipeline: preview, plan, reserve, stage, execute, commit, operate. | P0 | U1 | WORKSTREAM-06 | INFERENCE |
| TASK-08 | Define machine graph compiler requirements and limits. | P0 | U1 | WORKSTREAM-07 | FACT + INFERENCE |
| TASK-09 | Design city progression and resource/technology tiers. | P1 | U2 | WORKSTREAM-08 | FACT + INFERENCE |
| TASK-10 | Define fog-of-war and sensor model, including what the client may know. | P0 | U1 | WORKSTREAM-09 | FACT + INFERENCE |
| TASK-11 | Design multiplayer authority and client compute boundaries. | P0 | U1 | WORKSTREAM-10 | INFERENCE |
| TASK-12 | Verify current Unreal capabilities and limits before making engine commitments. | P1 | U1 | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| TASK-13 | Build or specify the first vertical slice. | P0 | U1 | WORKSTREAM-12 | INFERENCE |
| TASK-14 | Merge this report into the future master Project Spec Book only after uncertainty labels are preserved. | P1 | U2 | WORKSTREAM-13 | FACT |


### Constraints

| ID | Constraint | Hard/soft | Label |
| --- | --- | --- | --- |
| CONSTRAINT-01 | The simulation must be deterministic enough for replay, persistence, and debugging. | Hard | FACT |
| CONSTRAINT-02 | Planets and systems should be procedurally generated from data/science-bounded parameters, not arbitrary decorative sliders. | Hard/soft | FACT |
| CONSTRAINT-03 | Manual painting should not be the primary worldbuilding workflow, but overrides/painting must be supported. | Soft | FACT |
| CONSTRAINT-04 | Full planets/universes cannot be stored or simulated as dense maps. | Hard | INFERENCE |
| CONSTRAINT-05 | Only data players can sense should be loaded/sent/simulated at high fidelity. | Hard | FACT |
| CONSTRAINT-06 | Clients may not be trusted with hidden MMO truth or authority-critical results. | Hard for public MMO | INFERENCE |
| CONSTRAINT-07 | Labour NPCs and full pathfinding-heavy worker simulation should be avoided or heavily abstracted. | Soft but strong | FACT |
| CONSTRAINT-08 | Nanobots/construction must consume materials and energy and respect capability limits. | Hard/soft | FACT + INFERENCE |
| CONSTRAINT-09 | The mothership must be useful but not able to trivialise all manufacturing. | Hard/soft | FACT |
| CONSTRAINT-10 | Unreal should not be assumed capable of the whole design without a custom backend. | Soft pending verification | UNCERTAIN / UNVERIFIED |
| CONSTRAINT-11 | The preservation output must be human-readable first and also machine-aggregation-ready. | Hard | FACT |


### Open Questions

| ID | Question / issue | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- |
| QUESTION-01 | Is the official scale one designed star system, many generated systems, or a true galaxy-level structure? | P0 | WORKSTREAM-02, WORKSTREAM-10 | FACT + UNCERTAIN / UNVERIFIED |
| QUESTION-02 | How realistic should the planet generator be, and where should sci-fi overrides be allowed? | P0 | WORKSTREAM-02 | FACT |
| QUESTION-03 | What is the exact field-layer format for terrain/material/climate/ownership/visibility data? | P0 | WORKSTREAM-03 | FACT + INFERENCE |
| QUESTION-04 | What are the mothership’s initial resources, fabrication rate, and failure/recovery rules? | P0 | WORKSTREAM-04 | FACT |
| QUESTION-05 | How many robot chassis exist at launch and what tradeoffs do they have? | P1 | WORKSTREAM-05 | FACT |
| QUESTION-06 | What can nanobots do at each tech tier? | P0 | WORKSTREAM-06 | FACT + INFERENCE |
| QUESTION-07 | How should player-created machines compile into simple equations without killing creativity? | P0 | WORKSTREAM-07 | FACT |
| QUESTION-08 | How can cities feel alive without worker NPCs? | P1 | WORKSTREAM-08 | FACT + INFERENCE |
| QUESTION-09 | What exact information does fog of war hide, remember, infer, or reveal? | P0 | WORKSTREAM-09 | FACT |
| QUESTION-10 | What client compute is allowed in public MMO mode? | P0 | WORKSTREAM-10 | FACT + INFERENCE |
| QUESTION-11 | What should Unreal actually do in the production stack? | P1 | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| QUESTION-12 | What is the first vertical slice? | P0 | WORKSTREAM-12 | INFERENCE |


### Artifact Ledger

| ID | Artifact | Type | Carry forward? | Label |
| --- | --- | --- | --- | --- |
| ARTIFACT-01 | Visible chat transcript | Conversation context | Yes | FACT |
| ARTIFACT-02 | Uploaded file: Pasted text.txt | Prompt/instruction file | Yes | FACT |
| ARTIFACT-03 | Assistant architecture response 1 | In-chat output | Yes with uncertainty labels | INFERENCE |
| ARTIFACT-04 | Assistant design response 2 | In-chat output | Yes with uncertainty labels | INFERENCE |
| ARTIFACT-05 | External references cited in assistant responses | Links/citations | Carry forward to verification queue | UNCERTAIN / UNVERIFIED |
| ARTIFACT-06 | This generated preservation package | Markdown/YAML/ZIP files | Yes | FACT |


### Risk Register

| ID | Risk | Likelihood | Severity | Label |
| --- | --- | --- | --- | --- |
| RISK-01 | Scope explosion from full solar system, MMO, terraforming, machines, cities, and megaprojects at once. | High | High | INFERENCE |
| RISK-02 | Future assistant treats brainstormed ideas as final decisions. | Medium | High | FACT |
| RISK-03 | Unreal capability assumptions become stale or overoptimistic. | Medium | High | UNCERTAIN / UNVERIFIED |
| RISK-04 | Nanobots become magic and remove the need for industry/logistics. | Medium | High | INFERENCE |
| RISK-05 | Client-shared compute leaks hidden information or enables cheating. | Medium | High | INFERENCE |
| RISK-06 | Machine graph compiler allows exploit/lag machines. | High | High | INFERENCE |
| RISK-07 | Cities feel empty without NPCs. | Medium | Medium | INFERENCE |
| RISK-08 | Planet generation realism conflicts with fun layout. | Medium | Medium | INFERENCE |
| RISK-09 | Saves/mod packs/terraforming share tech but require different conservation rules. | Medium | Medium | INFERENCE |
| RISK-10 | Mothership fabricator trivialises the tech tree. | Medium | High | FACT + INFERENCE |
| RISK-11 | Future aggregation merges this chat with other chats without preserving caveats. | Medium | High | FACT |


### Verification Queue

| ID | Item | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- |
| VERIFY-01 | Current Unreal Engine capabilities and limitations for Large World Coordinates, World Partition, Iris, Replication Graph, MassEntity, PCG, runtime mesh/geometry, and networked physics. | P1 | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Current JPL Horizons/SPICE/IAU data access, licensing, and suitability for real Solar System data. | P1 | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Feasibility of deterministic fixed-point/double hybrid for planet-scale coordinates. | P0 | WORKSTREAM-01 | INFERENCE |
| VERIFY-04 | Network scale assumptions for millions across shards versus in one interaction bubble. | P1 | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Sparse terrain/delta representation performance for cut/fill at intended resolution. | P0 | WORKSTREAM-03, WORKSTREAM-06 | INFERENCE |
| VERIFY-06 | Whether player-created machine graphs can be made expressive while compiling safely. | P0 | WORKSTREAM-07 | INFERENCE |


## Possible Cross-Chat Duplicates

Likely duplicates include deterministic Domino engine architecture, Unreal feasibility, planet generation, terrain deltas, construction systems, machine/factory simulation, MMO sharding, fog of war, client compute, and project preservation/spec-book workflows.

## Possible Cross-Chat Conflicts

Watch for chats that assume human worker NPCs, dense simulation, Unreal as authoritative engine, galaxy-scale launch scope, arbitrary planet sliders, free nanobot construction, or hidden-state client computation. These would conflict with the strongest direction in this chat.

## Spec Book Integration Guidance

This chat should feed chapters on vision, engine architecture, world generation, field/delta saves, lore, spawning, construction, automation, factories, fog of war, multiplayer, and vertical-slice roadmap. Requirements candidates: deterministic sparse simulation, science-bounded procedural worlds, robot avatars, mothership-constrained progression, automation-first labour, machine graph abstraction, and sensed-only data. Keep human eggs/next ship lore, official reset rules, exact chassis, and exact Unreal role as context/open issues until confirmed.

## Aggregator Warnings

Do not treat assistant suggestions as accepted decisions. Do not erase uncertainty labels. Do not merge external Unreal/NASA/JPL claims without verification. Do not compress away the anti-worker-NPC and automation-first shift. Do not describe the game as a generic survival builder; the robotic mothership premise is central.
