# COMPLETE CHAT PRESERVATION REPORT — Dominium Deterministic Solar-System Architecture

## 0. Coverage and Reliability Assessment

| Field | Assessment |
| --- | --- |
| Chat label | Dominium Deterministic Solar-System Architecture |
| Date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | This chat only unless labelled PROJECT-CONTEXT |
| Apparent access | Partial: visible transcript and uploaded preservation prompt are accessible; hidden/older unavailable context is not. |
| Previously generated files available? | No prior generated files observed before this response; this response creates files. |
| Uploaded files or artifacts present? | Yes: Pasted text.txt preservation prompt. |
| Contains future plans? | Yes |
| Contains decisions? | Yes, but many are design directions or assistant recommendations rather than confirmed final decisions. |
| Contains pending tasks? | Yes |
| Contains unresolved questions? | Yes |
| Staleness risk | Medium: engine/API/external-source claims and current Unreal/NASA/JPL references require verification before formal spec use. |
| Extraction confidence | 4 |
| Safe for later aggregation? | With caveats |
| Main limitations | Only the visible conversation and uploaded prompt were used; no claim is made that this captures unavailable prior project history. |


This preservation is based on the visible chat plus the uploaded preservation prompt. The prompt explicitly requested a human-readable report first, then structured registers, a spec sheet, an aggregator packet, a self-audit, downloadable files, and a ZIP package. It also required uncertainty labels and warned not to treat brainstorms or assistant suggestions as final user decisions. The uploaded prompt is therefore treated as the controlling artifact for this preservation task.

Plain-language limitations: I can see the visible transcript of this chat and the uploaded `Pasted text.txt` preservation instruction. I cannot verify whether there were older hidden turns, prior files, or separate project documents outside this chat unless they are present in the visible transcript or uploaded file. I also cannot treat the previous assistant’s technical claims about Unreal, NASA/JPL data, MMO scale, or engine capabilities as permanently current; those belong in the verification queue.

## 1. One-Page Orientation

This chat was mainly about turning **Dominium**, built on or around the **Domino engine**, into a deterministic, procedural, large-scale civilisation-building game that can handle planetary and possibly solar-system scale without collapsing under simulation cost. The opening question asked whether it is possible to build a deterministic game with a full-scale real solar system, fully recreated planets, custom systems, procedural data-driven terrain, player terraforming, cut/fill construction, megaprojects, player-designed machines, factories, fog of war, sparse simulation, client-shared compute, single-player multiverse play, and MMO-style persistent universe play. The user also asked whether Unreal Engine could do this with low latency, high FPS, and millions of players across shards or private servers.

The first assistant response framed the problem as an architecture problem rather than merely an engine-choice problem. The central recommendation was that **Domino should be the deterministic simulation and database layer**, while Unreal, Raylib, or another renderer should be treated as a client. It argued that the world should be represented as seeds, physical data, sparse deltas, event logs, field layers, and simulation LODs—not as a giant dense scene graph. It also warned that millions of players can share a logical universe if distributed across regions/shards, but not all occupy one fully simulated real-time bubble at high fidelity.

The user then refined the project substantially. The conversation moved from general engine feasibility to a concrete game premise: a robotic seed-civilisation game. The user described science-bounded procedural star systems and planets, where designers set physically meaningful parameters and can nudge or override results without manually painting every detail. The same underlying data/delta technology should support world generation, save files, planet packs, painted fields, and in-game terraforming. The lore premise is that humans launched a robotic mothership to a new solar system; the mothership lands on the most habitable planet and manufactures robot bodies intended to restart civilisation, possibly before later human biological payloads arrive.

Gameplay, as discussed, centres on players spawning as robots from physical fabrication machines. They can choose body shapes such as biped, quadruped, spider, or tank-like forms. New spawn points are created by building remote laboratories/fabricators that can manufacture robot bodies from local materials. The mothership explains why players have a HUD, recipes, blueprints, quest-like guidance, and advanced technical knowledge from the start, while its finite resources, low throughput, heat, wear, and scale limits explain why players still need to build mines, refineries, factories, cities, and supply chains.

A major design shift was away from simulating human-like worker NPCs. The user explicitly identified labour/pathfinding as expensive and unnecessary if the civilisation is robotic. The preferred direction is automation from the beginning: nanobots, machine controllers, AI agents, process diagrams, and factories that can be represented as input/output graphs rather than thousands of pathfinding workers and moving parts. This became one of the most important chat contributions: **the game should simulate materials, energy, machines, logistics, sensors, and permissions—not pretend that invisible humans are doing the work.**

The future relevance of this chat is high. It contains the conceptual seed for Dominium’s engine architecture, world generation philosophy, lore premise, spawn economy, construction interface, anti-NPC automation stance, machine abstraction model, and first vertical slice. A future reader should understand that not everything here is a final decision. Many items are user brainstorms or assistant recommendations. However, the strongest carry-forward ideas are: deterministic sparse simulation, procedural science-bounded worlds, robot avatars, mothership-constrained progression, nanobot blueprint construction, no worker NPC labour, process-graph factories, sensed-only fog-of-war simulation, and a first playable slice proving the mothership-to-remote-spawn-lab loop.

## 2. The Story of the Conversation

### 2.1 Opening: a maximum-scale technical feasibility question

The chat began with a broad but coherent question: how can Domino engine and Dominium support a deterministic universe-scale construction/civilisation game? The user wanted a real or custom solar system, procedurally recreated planets, terrain editing, terraforming, megaprojects, machine and factory design, fog of war, sparse simulation, MMO persistence, client-shared compute, and both single-player and multiplayer operation. The user also asked whether Unreal could handle this without lag at high FPS and low latency.

This established the key tension: the desired game is extremely ambitious, but the user already understood some necessary constraints—fog of war, sparse simulation, collapsed unseen state, and distributed compute.

### 2.2 First response: architecture before engine

The first assistant answer reframed the problem around deterministic simulation. It recommended that the game be built as a deterministic simulation/database first, with renderers as clients. It proposed fixed ticks, deterministic commands, event logs, snapshots, state hashes, hierarchical coordinates, sparse deltas, procedural base terrain, simulation LOD, fog-of-war filtering, and server authority. It argued that Unreal can help with visualisation and local tooling but should not be expected to be the authoritative simulator for planets, factories, and millions of players.

The answer also drew a feasibility boundary: millions of accounts or players distributed across a universe may be possible with sharding and region authority, but millions in one fully simulated, low-latency visible place is not a practical design target.

### 2.3 User refinement: from engine question to game identity

The user then provided a long design monologue that changed the centre of gravity. The game became not only a technical engine challenge but a specific fiction and gameplay loop. The user described a procedurally generated star system or “galaxy” with as many planets as desired; physically meaningful parameters; a worldgen editor where sliders are bounded by realism; and perhaps reverse generation, where the designer specifies the kind of planet they want and the system solves plausible orbital/planetary parameters.

The user wanted procedural fields that can be overlaid with painted or custom fields, allowing planet packs, designer edits, and gameplay terraforming to share the same underlying technology. This is important because it suggests one unified world-state model rather than separate systems for saves, mods, and worldgen.

The user then introduced the robotic mothership premise. Humans in the past sent a robotic mothership to another solar system to land on a habitable planet, manufacture robots using advanced technology, and restart civilisation. Players spawn as robots from physical machines. They can build new spawn labs on the frontier if they can gather resources, power them, and connect them to the mothership or local industry.

### 2.4 Gameplay simplification: automation replaces labour

The user identified labour NPCs as a likely compute trap. Instead of workers with pathfinding, collision, schedules, and animation, the game should lean into the fact that the civilisation is robotic. Nanobots, ship AI, automation, blueprints, and process diagrams provide a diegetic reason for construction and manufacturing to be abstracted. The user wanted cut/fill, blueprint stages, non-destructive planning, and deterministic execution. Machines and vehicles should be constructible, but once assembled, their functions should be summarised as process equations where possible.

This was a major narrowing of the simulation model. The game can still be deep, but it does not need to simulate every person, machine part, or worker step.

### 2.5 Second response: synthesis into a robotic seed-civilisation game

The second assistant response named the direction: Dominium should be a robotic seed-civilisation game. It organised the user’s ideas into systems: science-bounded planet generation, forward/reverse generation, field layer stack, mothership resource and recipe logic, physical robot body spawning, nanobot construction as an actuator rather than magic, no worker NPCs, machines compiled into graphs, easy-to-start cities, AI planning as quest markers, fog of war as robot sensor knowledge, separate single-player/private/official MMO modes, and a first vertical slice.

This response generated many useful framework elements, but it remains mostly assistant synthesis. The user had not yet accepted every element before uploading the preservation prompt.

### 2.6 Preservation request: export this chat for future use

The final user action was uploading a detailed preservation prompt. It required this response to produce a maximum-fidelity human-readable report, structured registers, spec sheet, aggregator packet, audit, downloadable files, and final in-chat reader. That prompt also required uncertainty labels and warned against treating brainstorms as final decisions.

The final state of the chat is therefore a design handoff. The substantive design work is not complete, but this chat now has a coherent conceptual foundation ready to be turned into a formal project spec.

## 3. Main Topics Discussed

### Topic 1 — Deterministic Domino engine architecture

The topic was how to make a massive procedural universe deterministic and persistent. It came up because the user explicitly asked for deterministic gameplay across solar-system scale, sparse construction/destruction, multiplayer, and client-shared compute. The discussion concluded that the authoritative game should be represented as deterministic data and commands: seeds, rules versions, event logs, state hashes, sparse deltas, and snapshots. Rendering should not own truth. This remains a design recommendation rather than a confirmed implementation decision, but it is one of the strongest technical conclusions.

Uncertain points include exact language/runtime, math model, tick rates, coordinate scheme, physics boundaries, storage format, and how much determinism is required across platforms. Future work should define the Domino simulation core spec before building high-level content.

### Topic 2 — Science-bounded procedural star systems and planets

The user wanted procedural systems and planets generated from physically meaningful parameters. Sliders should not be arbitrary; they should be bounded to plausible values. The user also raised reverse generation: specifying a desired planet and letting the system find plausible orbital/planetary parameters. This connects directly to the official server world, private universes, planet packs, and future editor tools.

Unresolved points include how realistic the model should be, what counts as an allowable sci-fi override, what external datasets should be used, how licensing works, and whether the initial scope is one star system or many.

### Topic 3 — Field layers, painted overrides, saves, packs, and terraforming

The user wanted procedural fields overlaid with painted fields, and wanted the same technology to support save files and packs. The assistant formalised this into a field-layer stack: base procedural generation plus real data, designer overrides, mods/packs, terraforming layers, construction layers, damage layers, and temporary preview layers.

The key conclusion is that worldgen, saves, packs, and terraforming should probably share a unified sparse field/delta model. The caveat is that editor/worldgen layers may freely create matter, while gameplay terraforming/construction layers must obey conservation rules.

### Topic 4 — Robotic mothership lore and spawn economy

The user described a robotic mothership launched by humans to restart civilisation. It lands, manufactures robot bodies, and possibly prepares the world for later human biological payloads. This premise explains respawn, HUDs, recipes, quest markers, and advanced knowledge.

The mothership should be powerful but limited. It can fabricate early bodies and precision items, but finite resources, low throughput, heat, wear, and mission reserves force players to mine, refine, fabricate, and build industry. The exact limits remain unresolved and are a top design task.

### Topic 5 — Robot player bodies and physical respawn

The user proposed players spawning into robot forms such as biped, quadruped, spider, or tank-like bodies. New players enter through physical spawn machines. Frontier expansion depends on building remote labs that can make robot bodies from local materials.

This is not just lore. It creates a physical economy around respawn, exploration, risk, remote bases, communications, and industrial capacity. Open questions include body templates, balance, backup/mind-state rules, death penalties, and single-player versus MMO differences.

### Topic 6 — Nanobot construction, blueprinting, cut/fill, and terraforming

The user proposed nanobots or an invisible force as a computationally cheap and diegetic construction mechanism. Robots can project HUD blueprints, preview non-destructively, then commit construction when resources and energy are available. This supports cut/fill, mining, foundations, buildings, and megaprojects.

The important caveat is that nanobots should be actuators, not magic. They should consume materials, energy, time, and heat budget, and should require capability tiers. Future work must specify exact operations and data formats.

### Topic 7 — Automation instead of worker NPCs

This was one of the clearest user preferences. The user considered worker NPC labour but rejected it as expensive to compute. Since the society is robotic, there is no need to simulate people doing work. Instead, machines, nanobots, AI agents, and factory controllers can do it directly.

This affects the entire design. City-building becomes infrastructure-building, not labour management. The main risk is that cities may feel empty, so future design must create visible machine life, drones, sensor networks, traffic abstractions, and city operating systems.

### Topic 8 — Machines, devices, factories, and process graphs

The user wanted players to design machines, devices, factories, vehicles, and rockets. However, the user also wanted the entire function of a machine assembly to be summarised into an equation or process step when possible. The assistant suggested a machine graph compiler.

The key challenge is expressiveness versus safety. Players need creative freedom, but the engine must prevent exploit machines, lag machines, impossible devices, and economy bypasses. This is one of the highest-priority technical design tasks.

### Topic 9 — Fog of war and sensed-only simulation

The user required fog of war and only loading/simulating what players can sense. The assistant framed fog of war as a data-security and simulation model, not merely a visual overlay. A player should have observed, remembered, inferred, unknown, and secret states.

This connects directly to MMO anti-cheat and client-shared compute. If a client receives hidden information, players will extract it. Future design must define sensor rules, map sharing, hidden resources, and server-side filtering.

### Topic 10 — MMO, single-player, private universes, and client-shared compute

The user wanted the same general game to support single-player multi-universe play, official MMO persistent universe play, and possibly user servers. The assistant recommended a model where single-player and private servers can relax trust assumptions, while official MMO mode uses server authority and strict fog-of-war filtering.

Unresolved issues include whether the official server is one designed star system, how many players can occupy a local area, what clients are allowed to compute, how region ownership works, and how to handle failure/recovery.

### Topic 11 — Unreal’s role

The user asked whether Unreal can do the whole thing at high FPS and low latency. The assistant answered that Unreal can help with rendering, local tools, streaming, and visuals, but should not be assumed to provide deterministic planetary MMO simulation by itself.

This is a recommendation, not a user-confirmed decision. It requires current verification and prototype tests before being formalised.

### Topic 12 — First vertical slice

The assistant proposed a first playable slice: one planet region, one mothership, robot chassis, resource deposit, power, cut/fill, blueprint tool, nanobot construction, mine, refinery, fabricator, remote spawn lab, and fog-of-war sensor system. The gameplay loop is spawn, survey, find ore, blueprint mine, flatten site, build power, refine, fabricate, transport, build remote spawn lab, and spawn/swap there.

This is the best immediate next action, but it remains a recommendation until the user approves or modifies it.

## 4. What We Were Trying to Achieve

### 4.1 Explicit Goals

The user explicitly wanted a deterministic Dominium/Domino game architecture capable of handling procedurally generated solar systems, planets, construction, terraforming, factories, fog of war, sparse simulation, and MMO/single-player modes. The user also explicitly wanted science-bounded planet generation, procedural fields with painted overrides, robotic mothership lore, robot spawning, nanobot-like construction, automation over worker NPCs, and machine functions that can collapse into process diagrams.

These goals matter because they define the game’s identity: a massive but compute-aware robotic civilisation simulator rather than a conventional survival/crafting game or ordinary Unreal open world.

### 4.2 Inferred Goals

It is reasonable to infer that the user wants a future master spec book, wants old chats preserved for aggregation, wants technically honest feasibility boundaries, and wants the design to remain ambitious without becoming impossible. It is also inferred that the user values diegetic explanations for gameplay interfaces, because the user repeatedly tied HUDs, recipes, quest markers, and construction tools to robot/mothership fiction.

### 4.3 Goals That Changed Over Time

The conversation began as a broad technical feasibility question. It changed into a richer game-design discussion once the user introduced the robotic seed-ship premise. The focus shifted from “can Unreal do a deterministic solar-system MMO?” to “how should Dominium be designed as a robotic seed-civilisation game that happens to require a deterministic sparse engine?”

Another shift was away from worker NPCs. The user initially mentioned possible NPC workers/labour, then argued against simulating labour because it is expensive and redundant in a robot civilisation. This created a clearer design direction: automation from the jump.

### 4.4 Goals Still Unresolved

The core goals remain unresolved at implementation level. The chat did not decide exact engine technology, exact data formats, exact planet generator equations, exact robot body rules, exact mothership resource numbers, exact MMO architecture, exact first milestone schedule, or whether the user accepts all assistant recommendations. The best next step is to convert this conceptual foundation into a formal requirements/spec document and then a vertical slice plan.

## 5. Decisions Made and Why

| ID | Decision | Status | Why it mattered | Confidence | Label |
| --- | --- | --- | --- | --- | --- |
| DECISION-01 | Treat Domino as the authoritative deterministic simulation/data core and rendering as a client layer. | Recommended / not explicitly user-accepted | Keeps deterministic state separate from frame-rate, rendering, physics effects, and engine limitations. | 4 | INFERENCE |
| DECISION-02 | Use science-bounded procedural generation rather than purely arbitrary sliders or manual painting. | User-stated design direction | Supports surprising worlds while preserving plausibility and design control. | 5 | FACT |
| DECISION-03 | Support procedural fields overlaid with painted/designer/player layers. | User-stated direction, technical details open | Unifies worldgen, packs, saves, and terraforming under one model. | 4 | FACT + INFERENCE |
| DECISION-04 | Use a robotic seed-ship/mothership premise to explain spawning, recipes, HUD, and automation. | User-stated design premise | Provides diegetic explanation for robot avatars, HUD, knowledge database, spawn machines, and fabrication. | 5 | FACT |
| DECISION-05 | Make player characters robots with selectable manufactured chassis rather than ordinary humans. | User-stated design direction | Makes HUD, strength, inventory, respawn, hostile environments, and automation coherent. | 5 | FACT |
| DECISION-06 | Use nanobot/automation construction as the main interaction layer, bounded by material, energy, time, and capability. | User-stated direction with assistant constraints | Avoids expensive labour simulation and makes construction convenient while preserving economy. | 4 | FACT + INFERENCE |
| DECISION-07 | Deprioritise human-like worker NPC labour and use automation/process graphs instead. | Strong user-stated preference / tentative design direction | Avoids pathfinding/AI costs and aligns with robot civilisation premise. | 5 | FACT |
| DECISION-08 | Use the mothership as the recipe book and early precision fabricator, but constrain it with finite resources and throughput. | User-stated direction | Preserves progression while explaining why players know advanced designs. | 5 | FACT |
| DECISION-09 | Represent distant machines/factories as processes/equations rather than simulating all physical parts. | User-stated direction with assistant formalisation | Enables scale and preserves performance. | 5 | FACT |
| DECISION-10 | Use sparse construction/destruction and collapsed simulation for unseen/unneeded areas. | Core user requirement and assistant recommendation | Makes planet-scale and MMO-scale persistence possible. | 5 | FACT |
| DECISION-11 | Do not trust clients with hidden information or authoritative MMO results. | Assistant recommendation / not explicitly user-accepted | Protects fog-of-war secrets and anti-cheat. | 3 | INFERENCE |
| DECISION-12 | Treat Unreal as useful for presentation/tooling but not as the whole authoritative deterministic MMO engine. | Assistant recommendation / not explicitly user-accepted | Prevents architecture from depending on ordinary engine scene graphs for planetary/MMO authority. | 3 | INFERENCE |
| DECISION-13 | Make the first serious milestone a small vertical slice, not a full solar-system MMO. | Assistant recommendation / not explicitly user-accepted | Tests whether the core loop is fun and technically viable. | 4 | INFERENCE |


### DECISION-01 — Domino as deterministic simulation core

This was recommended by the assistant, not explicitly accepted by the user. It follows from the user’s deterministic, persistent, sparse, MMO-scale requirements. The alternative would be to make Unreal or a normal scene graph the source of truth, but that conflicts with replayability, sparse planetary scale, and authority boundaries. This decision affects almost everything: save files, networking, terrain, factory simulation, and debugging. It should be revisited only if a much smaller game scope is chosen.

### DECISION-02 — Science-bounded procedural generation

This is a clear user-stated direction. The user does not want planets manually painted from scratch or shaped by arbitrary sliders. The alternative, fully arbitrary world creation, was deprioritised because it would undermine the “real science” premise. This affects the planet editor and official server world design.

### DECISION-03 — Procedural fields plus overlays

The user explicitly wanted procedural fields overlaid with painted fields and wanted save-file technology to support packs. The decision is conceptually clear, but the technical implementation remains open. The key assumption is that the same sparse field system can serve worldgen, saves, mods, and gameplay deltas if conservation rules are separated by layer type.

### DECISION-04 — Robotic mothership premise

The user made this a central lore/gameplay idea. It explains robot players, HUDs, recipes, spawning, and early constraints. It also creates faction and mystery possibilities. This decision could be revisited if the game changes away from robot civilisation, but in the current chat it is the strongest creative anchor.

### DECISION-05 — Robot player chassis

The user explicitly described players choosing robot forms. This affects movement, inventory, environment access, progression, respawn, and player roles. Exact chassis are not final.

### DECISION-06 — Nanobot construction bounded by costs

The user proposed nanobots/invisible force because it is computationally cheap and diegetic. The assistant added the constraint that nanobots should consume materials, energy, time, and capability. This matters because otherwise construction becomes magic and invalidates factories.

### DECISION-07 — Avoid worker NPC labour

The user strongly favoured skipping expensive NPC labour and using automation. The main alternative was simulating worker-like agents, but that was deprioritised because of pathfinding and compute costs. This should be preserved carefully: future assistants should not reintroduce labour management as a default.

### DECISION-08 — Mothership as recipe book but not infinite factory

The user explicitly wanted the mothership to contain knowledge and some fabrication capacity, but with finite resources and low throughput so players still need to build industry. This affects early-game pacing and prevents a contradiction: if the ship can make everything, why play?

### DECISION-09 — Machines/factories compile to equations

The user explicitly wanted machine functions summarised into simple process steps where possible. This is a major performance strategy. The unresolved risk is how to keep player-designed machines expressive without creating exploits.

### DECISION-10 — Sparse construction/destruction and collapsed simulation

This was both user-stated and assistant-supported. The world must store player changes sparsely and simulate unobserved systems at lower fidelity. This is foundational and should become a formal requirement.

### DECISION-11 — Client compute must be limited in public MMO mode

This is an assistant recommendation. The user wanted clients to share compute; the assistant separated safe client compute from unsafe hidden/authoritative compute. It should be treated as a security recommendation pending final MMO design.

### DECISION-12 — Unreal as client/tooling, not authoritative universe

This is an assistant recommendation, not a user decision. It needs verification against current Unreal capabilities and the final scope. It matters because betting on Unreal as the whole simulation engine could lead to architectural failure.

### DECISION-13 — First vertical slice before full MMO

This is an assistant recommendation. It matters because the game is too large to build top-down. The proposed slice tests the unique loop: spawn from mothership, survey, mine, build power/refinery/fabricator, and create a remote spawn lab.

## 6. Ideas Considered but Rejected, Superseded, or Deprioritised

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Manual painting as the main planet creation method | Deprioritised | User wants procedural generation from plausible science, with painting as override rather than primary method. | Tentative but strong | Use painting for designer overrides, mods, and exact authored locations. | WORKSTREAM-02, WORKSTREAM-03 | FACT |
| REJECTED-02 | Completely arbitrary sliders detached from physical plausibility | Deprioritised | User said sliders should be bounded by what is realistic. | Tentative but strong | Allow fantasy/sci-fi override modes if explicitly labelled. | WORKSTREAM-02 | FACT |
| REJECTED-03 | Human-like worker NPC labour as the main construction/economy mechanism | Deprioritised | User said labour is expensive to compute and suggested jumping straight to automation. | Tentative but strong | Could return as local cosmetic drones/robots or abstracted AI agents, not core labour sim. | WORKSTREAM-07, WORKSTREAM-08 | FACT |
| REJECTED-04 | Simulating every machine part, belt item, worker, and device at full fidelity everywhere | Rejected as infeasible by design rationale | User asked to collapse things; assistant recommended aggregate equations. | Tentative but fundamental | Use local detailed visualization only when sensed/interactive. | WORKSTREAM-07, WORKSTREAM-10 | FACT + INFERENCE |
| REJECTED-05 | Unreal Actors as the authoritative representation for all terrain, machines, cities, and planet state | Rejected by assistant recommendation | Assistant argued Unreal should not own the authoritative universe. | Pending user acceptance | Reconsider only for small prototypes or purely visual local scenes. | WORKSTREAM-11 | INFERENCE |
| REJECTED-06 | Trusting public MMO clients with secret fog-of-war data or authority-critical results | Rejected by assistant recommendation | Would leak secrets and enable cheating. | Strong recommendation | Private servers/single-player can relax this. | WORKSTREAM-09, WORKSTREAM-10 | INFERENCE |
| REJECTED-07 | World reset as the normal permanent official-server failure response | Deprioritised by assistant recommendation | User brainstormed restarting if first players fail; assistant suggested emergency recovery instead. | Uncertain | Could be used for alpha seasons, roguelike servers, or explicit challenge modes. | WORKSTREAM-04, WORKSTREAM-10 | INFERENCE |


The rejected/deprioritised items matter because they protect the design from sliding back into conventional assumptions. The game should not become a manual planet-painting tool, a worker-management city builder, an Unreal Actor planet, or a fully simulated machine-parts sandbox at all scales. Some options may return in limited forms: painted terrain can exist as an override; NPC-like behaviour can exist as local drones or wildlife; Unreal Actors can represent local visuals; and world resets could be used in alpha seasons. But they should not be treated as the main architecture.

## 7. Important Reasoning, Rationale, and Tradeoffs

The visible reasoning in the chat revolved around scale versus fidelity. The user wanted extreme scale but already recognised that only sensed or relevant areas can be loaded and simulated. The assistant’s rationale was that every system needs a compact representation when unobserved and a high-fidelity representation only when a player can interact with it.

A second tradeoff was realism versus design control. The user wants planets generated from real science, but also wants designers to nudge outcomes and possibly reverse-solve for a desired planet. The proposed compromise is plausibility-bounded generation plus labelled overrides.

A third tradeoff was convenience versus progression. Nanobots and mothership fabrication make the game smoother, but they can destroy the industrial challenge if unconstrained. The visible rationale was to let these systems provide precision, planning, and early capability while requiring materials, energy, throughput, heat management, and factories for scale.

A fourth tradeoff was creativity versus server safety. Player-designed machines are important, but arbitrary simulations can become lag machines or exploits. The proposed solution is machine graph compilation: visually rich designs are reduced to validated inputs, outputs, capabilities, costs, and failure modes.

A fifth tradeoff was MMO scale versus secrecy. Client-shared compute could help performance, but if clients receive hidden data, fog of war fails. The recommendation was to allow clients to compute visible/verifiable work but keep hidden state and authority on trusted servers.

## 8. Plans, Future Work, and Next Steps

The future work naturally begins with specification, not full implementation. The highest-priority tasks are to define the deterministic core, planet generator schema, field/delta format, mothership economy, nanobot construction pipeline, machine graph compiler, fog-of-war model, and first vertical slice.

Recommended sequence:

1. **Write the design pillars**: robotic seed civilisation; deterministic sparse world; science-bounded planets; automation-first cities; physical spawn economy.
2. **Define the first vertical slice**: one planet region, one mothership, one ore deposit, one power source, one cut/fill tool, one mine, one refinery, one fabricator, one remote spawn lab, one fog-of-war system.
3. **Specify the data core**: event logs, snapshots, state hashes, sparse deltas, field layers, command validation.
4. **Specify gameplay systems**: mothership constraints, robot chassis, nanobot construction, machine graphs, factory abstraction, spawn labs.
5. **Prototype determinism and terrain edits**: prove that cut/fill, save/load, and replay produce the same world state.
6. **Prototype machine graphs**: prove that a player-built machine can compile into an aggregate process safely.
7. **Verify engine choices**: test Unreal/Raylib/custom renderer assumptions only after the core data model is clear.

Main blockers are scope, unverified engine assumptions, the need for a safe machine compiler, and the need to prevent nanobots/mothership fabrication from trivialising the game.

## 9. Constraints, Preferences, and Non-Negotiables

### 9.1 Explicit Constraints and Preferences

The user explicitly wants determinism, procedural data-driven solar-system/planet generation, realistic bounded sliders, field overlays and painted overrides, single-player/private/MMO possibilities, fog of war, sparse construction/destruction, collapsed unseen simulation, robot player avatars, physical spawn machines, nanobot-style construction, finite mothership resources, and automation rather than worker NPCs.

The uploaded preservation prompt explicitly requires human-readable explanation first, uncertainty labels, no invented facts, no silent inference, no treating brainstorms as decisions, structured registers, spec sheet, aggregator packet, self-audit, and files/ZIP when tools are available.

### 9.2 Inferred Constraints and Preferences

The user appears to prefer diegetic explanations, practical feasibility boundaries, and systems that are both ambitious and computationally honest. The user also appears to prefer future-proof preservation so old chats can become a master Project Spec Book.

### 9.3 Uncertain or Unestablished Preferences

It is not established whether the user prefers Unreal, Raylib, or a fully custom renderer long-term. It is not established how realistic the science model should be, how punishing respawn should be, how many robot bodies should exist, whether official servers should ever reset, or how much PvP/conflict the MMO should support.

## 10. Files, Artifacts, Outputs, and Prompts

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Visible chat transcript | Conversation context | Primary source for preservation. | Available in current chat; not separately exported before this response. | This chat | Yes | Contains the user’s MMO/engine question, assistant architecture responses, and user’s detailed seed-civilisation concept. | FACT |
| ARTIFACT-02 | Uploaded file: Pasted text.txt | Prompt/instruction file | Defines the preservation/export requirements for this response. | Uploaded in this turn. | User upload | Yes | Requires human-readable report, registers, spec sheet, aggregator packet, audit, files, and ZIP. | FACT |
| ARTIFACT-03 | Assistant architecture response 1 | In-chat output | First structured answer about deterministic simulation, sparse deltas, fog of war, client compute, MMO scale, and Unreal limits. | Existing in visible chat. | Assistant | Yes with uncertainty labels | Treat as recommendations unless user later accepts. | INFERENCE |
| ARTIFACT-04 | Assistant design response 2 | In-chat output | Expanded design around robot seed civilisation, mothership, nanobots, automation, planet generation, and first vertical slice. | Existing in visible chat. | Assistant | Yes with uncertainty labels | Treat as recommendations and synthesis; user had not yet replied before preservation request. | INFERENCE |
| ARTIFACT-05 | External references cited in assistant responses | Links/citations | Prior assistant cited Unreal, NASA/JPL/SPICE, Guinness, EVE, etc. | Present as citations in visible chat, not reverified for this report. | Assistant/web citations in prior turns | Carry forward to verification queue | Useful for grounding engine/scale claims but may be stale. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-06 | This generated preservation package | Markdown/YAML/ZIP files | Exports the chat for future reading and aggregation. | Created by this response. | Assistant | Yes | Includes manifest, report, context transfer packet, spec sheet, registers, aggregator packet, reader brief, audit, bootstrap prompt, in-chat reader, and ZIP. | FACT |


Before this preservation task, no downloadable files were observed as having been created in the visible chat. The uploaded `Pasted text.txt` is the controlling prompt for the preservation package. This response creates the requested downloadable files and ZIP.

## 11. Open Questions and Unresolved Issues

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Is the official scale one designed star system, many generated systems, or a true galaxy-level structure? | Determines generator scope, persistence model, and travel design. | User discussed a “Galaxy” but clarified as essentially a solar system with configurable planets. | Final product scale and naming. | Choose initial official-server scope and name the editor accordingly. | P0 | WORKSTREAM-02, WORKSTREAM-10 | FACT + UNCERTAIN / UNVERIFIED |
| QUESTION-02 | How realistic should the planet generator be, and where should sci-fi overrides be allowed? | Controls content freedom and simulation complexity. | User wants sliders bounded by realism but also wants designer nudging and overrides. | Hard vs soft physics boundaries. | Define plausibility scoring and override categories. | P0 | WORKSTREAM-02 | FACT |
| QUESTION-03 | What is the exact field-layer format for terrain/material/climate/ownership/visibility data? | It is foundational for saves, mods, terraforming, and construction. | User wants procedural fields overlaid with painted fields and reused save technology. | Data schema, operations, compression, conservation rules. | Draft field/delta spec. | P0 | WORKSTREAM-03 | FACT + INFERENCE |
| QUESTION-04 | What are the mothership’s initial resources, fabrication rate, and failure/recovery rules? | This defines early progression and MMO sustainability. | User proposed finite resources, low throughput, and possible world reset/recovery if first players fail. | Exact numbers and whether official server can reset. | Design mothership economy and failure modes. | P0 | WORKSTREAM-04 | FACT |
| QUESTION-05 | How many robot chassis exist at launch and what tradeoffs do they have? | Chassis define player role expression and balance. | User listed biped/quadruped/spider/tank-like options. | Launch set, capabilities, costs, progression. | Draft first chassis table. | P1 | WORKSTREAM-05 | FACT |
| QUESTION-06 | What can nanobots do at each tech tier? | Nanobots could break progression if too strong. | User proposed nanobots as easy compute interface; assistant recommended material/energy/time limits. | Capability ladder and limits. | Define construction tool tiers. | P0 | WORKSTREAM-06 | FACT + INFERENCE |
| QUESTION-07 | How should player-created machines compile into simple equations without killing creativity? | This is central to performance and user-generated engineering. | User wants machine assemblies summarised as unit steps/process diagrams. | Compiler limits, modules, validation, exploit prevention. | Draft machine graph compiler rules. | P0 | WORKSTREAM-07 | FACT |
| QUESTION-08 | How can cities feel alive without worker NPCs? | No labour NPCs removes common visual/social signals. | User prefers no intelligent worker NPCs and automation instead. | Ambient machines, drones, UI, population abstraction, city OS. | Design city feedback loops and visual proxies. | P1 | WORKSTREAM-08 | FACT + INFERENCE |
| QUESTION-09 | What exact information does fog of war hide, remember, infer, or reveal? | Affects gameplay, security, and simulation. | User required fog of war and sensed-only loading. | Sensor types, map sharing, hidden resources, enemy bases, caves. | Draft sensor/perception rules. | P0 | WORKSTREAM-09 | FACT |
| QUESTION-10 | What client compute is allowed in public MMO mode? | Client-shared compute is a core scaling idea but dangerous. | User asked about clients sharing compute; assistant recommended only visible/verifiable jobs. | Precise trust boundaries and validation mechanisms. | Create client compute policy. | P0 | WORKSTREAM-10 | FACT + INFERENCE |
| QUESTION-11 | What should Unreal actually do in the production stack? | Engine commitment affects architecture and team skills. | Assistant recommended Unreal as renderer/client, not source of truth. | Whether user accepts this and whether current UE features suffice. | Verify and decide renderer strategy. | P1 | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| QUESTION-12 | What is the first vertical slice? | A huge design needs a concrete implementation target. | Assistant proposed mothership-to-remote-spawn-lab loop. | User acceptance and exact milestone scope. | Approve or revise vertical slice. | P0 | WORKSTREAM-12 | INFERENCE |


The most blocking unresolved issues are the exact first vertical slice, field/delta data format, mothership constraints, machine graph compiler, fog-of-war sensor rules, and whether Unreal is merely a renderer/client or a larger part of production.

## 12. Risks, Failure Modes, and What Future Chats Might Get Wrong

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Scope explosion from full solar system, MMO, terraforming, machines, cities, and megaprojects at once. | Project never reaches a playable core. | High | High | Define and build the vertical slice first. | WORKSTREAM-12 | INFERENCE |
| RISK-02 | Future assistant treats brainstormed ideas as final decisions. | Spec becomes too rigid or misrepresents user intent. | Medium | High | Use FACT/INFERENCE/UNCERTAIN labels and decision statuses. | WORKSTREAM-13 | FACT |
| RISK-03 | Unreal capability assumptions become stale or overoptimistic. | Wrong engine architecture or performance promises. | Medium | High | Verify current Unreal docs and prototype critical path. | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| RISK-04 | Nanobots become magic and remove the need for industry/logistics. | Gameplay loses progression and constraints. | Medium | High | Bound construction by energy, materials, heat, time, and capability. | WORKSTREAM-06 | INFERENCE |
| RISK-05 | Client-shared compute leaks hidden information or enables cheating. | MMO security failure. | Medium | High | Do not send hidden state to clients; use server authority and validation. | WORKSTREAM-09, WORKSTREAM-10 | INFERENCE |
| RISK-06 | Machine graph compiler allows exploit/lag machines. | Players can crash servers or bypass economy. | High | High | Use complexity budgets, validation, and collapsed representations. | WORKSTREAM-07 | INFERENCE |
| RISK-07 | Cities feel empty without NPCs. | Player-built civilisation lacks emotional/visual feedback. | Medium | Medium | Use drones, traffic abstractions, city OS UI, visible infrastructure, sensors, and ambient machine activity. | WORKSTREAM-08 | INFERENCE |
| RISK-08 | Planet generation realism conflicts with fun layout. | Official world is plausible but not playable, or fun but implausible. | Medium | Medium | Use plausibility score plus gameplay score and allow labelled overrides. | WORKSTREAM-02 | INFERENCE |
| RISK-09 | Saves/mod packs/terraforming share tech but require different conservation rules. | Worldgen and gameplay data corrupt each other conceptually. | Medium | Medium | Separate editor layers from gameplay-constrained layers. | WORKSTREAM-03 | INFERENCE |
| RISK-10 | Mothership fabricator trivialises the tech tree. | Players skip factories and cities. | Medium | High | Limit feedstock, throughput, heat, scale, wear, and mission reserves. | WORKSTREAM-04 | FACT + INFERENCE |
| RISK-11 | Future aggregation merges this chat with other chats without preserving caveats. | Master spec contains contradictions or unsupported requirements. | Medium | High | Use artifact ledger, verification queue, and manual review before finalising spec. | WORKSTREAM-13 | FACT |


The main future-chat risk is over-certainty. A future assistant might treat the assistant’s architecture recommendations as user decisions, or treat the user’s brainstorms as final design. The safest approach is to preserve labels: user-stated goals are FACT; assistant synthesis is INFERENCE unless accepted; engine and external-source claims are UNCERTAIN / UNVERIFIED until checked.

## 13. What This Chat Contributes to the Larger Project or Future Spec Book

This chat contributes the conceptual foundation for Dominium as a robotic seed-civilisation game. It should inform the master spec book chapters on engine architecture, procedural star-system generation, planetary field layers, lore premise, player bodies and spawning, construction/terraforming, automation/factories, fog of war, MMO architecture, and first vertical slice.

Some items should become formal requirements: deterministic core, sparse deltas, science-bounded generation, robot avatars, mothership-constrained progression, automation-first labour model, machine graph abstraction, fog-of-war secrecy, and vertical-slice-first planning. Other items should remain context or open issues: human eggs/next ship lore mystery, exact robot chassis, world reset rules, exact Unreal role, and exact MMO scale claims.

Likely overlaps with other chats include Domino engine architecture, deterministic simulation, procedural planets, resource economy, construction systems, multiplayer/server architecture, and Unreal feasibility. The aggregator should compare those reports before finalising requirements.

## 14. What I Should Remember

- The strongest design identity is **robotic seed civilisation**: players are robots created by a mothership to rebuild industrial capacity on a scientifically generated planet.
- The strongest technical identity is **deterministic sparse simulation**: the universe is seeds, fields, deltas, commands, graphs, ledgers, and snapshots, rendered locally when sensed.
- The strongest gameplay loop is **spawn, survey, mine, build power, refine, fabricate, expand spawn infrastructure, and scale toward cities/megaprojects**.
- The strongest user preference is **automation over worker NPCs**. Do not default back to human labour simulation.
- The mothership is both powerful and constrained: it explains knowledge and spawning but must not replace industry.
- Nanobots are an interface and actuator, not free matter or free energy.
- Factories and machines should compile into process graphs when possible.
- Fog of war is a simulation/security boundary, not just a shader.
- Unreal may be useful, but the authoritative universe should not be assumed to live inside Unreal without verification.
- The next best action is to formalise a vertical slice and data model.

## 15. Best Questions I Can Ask Next in This Chat

### 15.1 Understanding the Chat

- What are the five most important Dominium design pillars from this chat?
- Which ideas came directly from me and which were assistant recommendations?
- What changed when the design shifted from human labour to robotic automation?

### 15.2 Decisions

- Which decisions are safe to promote to formal requirements now?
- Which assistant recommendations still need explicit user approval?
- Should “Unreal as renderer/client only” become a project rule or stay a hypothesis?

### 15.3 Tasks and Next Actions

- Turn the proposed vertical slice into a milestone plan.
- Draft the deterministic core data model for fields, deltas, events, and state hashes.
- Define the mothership economy and starting resource constraints.

### 15.4 Artifacts and Files

- Show me the artifact ledger and explain what should feed into a master Project Spec Book.
- Convert the generated spec sheet into a formal design document outline.

### 15.5 Risks and Verification

- What are the biggest feasibility risks in the Dominium design?
- What current Unreal claims need verification before engine planning?
- What could make nanobot construction break the economy?

### 15.6 Future Spec Book / Aggregation

- Which chapters of the master Project Spec Book should this chat feed into?
- What cross-chat conflicts should an aggregator look for?

### 15.7 Deep-Dive Questions Specific to This Chat

- Design the first three robot chassis and their manufacturing costs.
- Design the mothership’s finite fabrication system.
- Design the first machine graph compiler format.
- Design the field-layer stack for procedural terrain, painted overrides, and gameplay deltas.
- Design the remote spawn lab milestone loop.

## 16. Compact Human Summary

This chat captured the core identity and technical direction for Dominium as a deterministic, large-scale, procedural robotic civilisation game. It began with a very broad technical question: how can Domino engine and Dominium support full-scale solar systems, procedural planets, terraforming, cut/fill construction, megaprojects, player-designed machines and factories, fog of war, sparse simulation, client-shared compute, single-player universes, and MMO persistent universes? The user also asked whether Unreal could do this at low latency and high FPS with millions of players.

The first major conclusion was architectural: the world should not be built as a giant live Unreal scene. Instead, Domino should be treated as the authoritative deterministic simulation and database layer. The universe should be stored as seeds, rules, fields, sparse deltas, event logs, snapshots, state hashes, machine graphs, resource ledgers, and visibility records. Renderers such as Unreal can visualise the currently sensed local state, but rendering should not own world truth. This is an assistant recommendation, not an explicitly accepted user decision, but it follows strongly from the user’s scale and determinism requirements.

The user then refined the game into a much more specific premise. The game should have procedurally generated star systems and planets, with parameters bounded by plausible science rather than arbitrary sliders. Designers should be able to guide results, perhaps even by reverse generation: specify the kind of planet desired, then have the system find plausible physical parameters. The same underlying field/delta technology should support procedural generation, painted overrides, planet packs, save files, terraforming, and construction.

The strongest creative idea was the robotic mothership. Humans launched a robotic seed ship to another solar system. The ship lands on a suitable planet and manufactures robot bodies to restart civilisation. Players spawn as robots from physical fabrication machines. They may choose different chassis such as biped, quadruped, spider, or tank-like bodies. New frontier spawn points are not menu abstractions: players must build labs or fabricators that have power, materials, and manufacturing capability.

This premise solves many design problems. The HUD is diegetic because players are robots. Quest markers are diegetic because the ship AI can generate plans. Recipes exist because the mothership brought human knowledge. Players do not need to invent CPUs, railways, or calendars from scratch. However, the mothership cannot simply build everything forever. The user specifically wanted finite resources, limited throughput, and a need for players to build mines, refineries, factories, and cities. The mothership is excellent at knowledge and precision, but the planet is required for scale.

Another crucial design shift was rejecting worker NPC labour as a core simulation. The user initially considered NPC workers but then pointed out that labour, pathfinding, and person-like simulation are expensive and unnecessary if the civilisation is robotic. The game should start with automation. Nanobots, machine controllers, AI agents, construction swarms, and process diagrams can do the work. This means cities do not need to simulate thousands of workers. They need power grids, logistics, fabricators, roads, rails, sensors, spawn labs, permissions, and industrial processes.

Construction should be built around blueprinting and nanobots. Players can preview a design, stage it, reserve resources, and commit it. Cut/fill terrain editing, mining, foundations, buildings, and megaprojects can use the same deterministic sparse operation model. But nanobots must not be magic. Every action should require materials, energy, time, capability, and usually produce heat or waste.

Factories and machines should be visually rich when nearby, but computationally simple when distant. The user wanted machines and vehicles to be summarised as equations or process steps. The future design likely needs a machine graph compiler: players assemble components, and Domino compiles the result into capabilities, input/output rates, power draw, heat, reliability, and constraints. This lets the game support creative engineering without simulating every bolt, belt, worker, and moving part everywhere.

The main unresolved work is converting this concept into a formal spec and vertical slice. The best proposed first slice is: one planet region, one mothership, one robot body, one ore deposit, one power source, one cut/fill tool, one blueprint system, one mine, one refinery, one fabricator, one remote spawn lab, and one fog-of-war sensor model. If that loop is fun and deterministic, the project can scale outward. If it is not, adding solar systems and MMO scale will not fix it.
