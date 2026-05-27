# Accompanying Human-Readable Detailed Summary and Report

**Conversation label:** Dominium Complete Conversation Preservation  
**Primary design label:** Dominium Deterministic Solar-System / Robotic Seed-Civilisation Architecture  
**Date anchor:** 2026-05-27 Australia/Melbourne  
**Source scope:** This chat only, plus explicitly generated/exported files and the uploaded preservation prompt in this conversation.  
**Epistemic labels used:** FACT, INFERENCE, UNCERTAIN / UNVERIFIED, PROJECT-CONTEXT.

## 0. What this companion report is

This is a standalone human-readable companion report for the current Dominium conversation. It is designed to sit beside the previously generated structured preservation package. The earlier package already contains a large formal report, context transfer packet, spec sheet, registers, aggregator packet, reader brief, verification/audit file, future-chat bootstrap prompt, in-chat reader, and ZIP archive. This companion report adds a narrative explanation of what happened in the conversation and checks that the exported files and artifacts have been preserved together in one bundle.

This report should be read as a summary of the whole visible conversation, not as a final design specification. Some items were clearly stated by the user and are marked as FACT. Some were assistant-proposed architecture or design synthesis and are marked as INFERENCE unless the user clearly accepted them. Current-world claims about Unreal Engine, NASA/JPL data, network scale, or software capabilities remain UNCERTAIN / UNVERIFIED unless they are checked again with current sources before becoming formal project requirements.

## 1. Coverage and reliability

| Field | Assessment |
|---|---|
| Apparent chat access | Partial but useful: visible conversation context and generated artifacts are available; hidden older project history is not assumed. |
| Uploaded source prompt | Present: `Pasted text.txt`, the maximum-fidelity preservation instruction. |
| Previously generated files | Present: two generated file sets were found in the workspace: a `Dominium_Deterministic_Solar_System_Architecture` set and a `Dominium_Robotic_Seed_Civilisation_Architecture` set. |
| Main design content covered | Yes: deterministic simulation, procedural planets, robotic mothership, robot players, spawn labs, nanobot construction, machine/factory abstraction, fog of war, MMO/private/single-player modes, Unreal role, vertical slice. |
| Decisions present | Yes, but many are design directions or assistant recommendations rather than final project decisions. |
| Future work present | Yes: vertical slice, data schemas, field layers, mothership economy, machine graph compiler, sensor/fog-of-war model, engine verification. |
| Open questions present | Yes: first vertical slice scope, realism bounds, official server scope, data models, robot chassis, nanobot tiers, machine compiler, Unreal role. |
| Staleness risk | Medium: engine/API/software/network claims require verification before formal use. |
| Extraction confidence | 4/5 for the visible conversation and files; lower for any unavailable prior project history. |
| Safe for later aggregation | Yes, with caveats and labels preserved. |

Plain-language limitation: this package does not prove that every Dominium idea ever discussed elsewhere has been captured. It captures what is visible and what was generated in this chat. The files should be merged into a future master spec only after cross-checking other reports and preserving uncertainty labels.

## 2. One-page orientation

This conversation was about turning the Dominium/Domino project into a coherent technical and creative architecture for an extremely ambitious deterministic game: a procedurally generated, scientifically bounded, solar-system-scale civilisation/construction simulation with editable planets, terraforming, machine building, factories, megaprojects, fog of war, sparse simulation, single-player universes, private servers, and possible MMO operation.

The original technical problem was scale. The user asked how a game could contain a full-scale real solar system or custom solar systems, fully recreated planets, procedural planets and universes, civilisations, terraforming, cut/fill, megaprojects, devices, machines, factories, and fog of war, while only loading and simulating what players can sense. The user also asked whether clients could share compute and whether Unreal could run this without lag, at low latency and high FPS, across many shards or private universes.

The first main architecture conclusion was that Dominium should not be built as a normal giant Unreal level. Instead, Domino should be treated as a deterministic simulation and data engine. The universe should be stored as seeds, source data, procedural fields, sparse deltas, event logs, state hashes, snapshots, graphs, and ledgers. Rendering should be separate. Unreal, Raylib, or another engine can present local visible state, but the authoritative truth of the universe should not be ordinary engine actors or frame-rate-driven gameplay logic.

The conversation then shifted from pure engine feasibility to game identity. The user described a procedural star-system generator where planets are created from scientifically plausible parameters rather than arbitrary sliders. The designer should be able to nudge or override the result, and maybe even use reverse generation: design the desired planet, then let the system solve plausible orbital and planetary parameters that could produce it. The user also wanted procedural planet fields to be overlayable with painted/designer fields and to reuse the same underlying technology for saves, planet packs, terraforming, construction, and destruction.

The strongest creative identity that emerged was the robotic seed-civilisation premise. Humanity launched a robotic mothership to another solar system. The ship lands on the most habitable planet and manufactures robot bodies intended to restart civilisation. Players spawn as robot bodies from physical fabrication machines. They can later build remote spawn labs or fabrication facilities that allow new players or respawns to appear at frontier locations. This ties respawn, progression, exploration, construction, and settlement expansion into one physical in-world economy.

A major design pivot was rejecting worker NPC labour as the core of city and construction simulation. The user identified labour/pathfinding as computationally expensive and unnecessary if the civilisation is explicitly robotic. Instead, construction and production should be handled by automation: nanobots, AI controllers, machine graphs, process diagrams, drones, logistics systems, and computer-managed factories. This is one of the most important ideas to preserve. Dominium should not become a human-worker city sim by default; it should be a robotic infrastructure and automation civilisation game.

The mothership explains why players know advanced recipes. The ship already contains human knowledge: CPUs, rail gauges, calendars, construction methods, circuits, refineries, and industrial design. The progression problem is not “invent a CPU from scratch.” It is “build the industrial chain capable of locally making CPUs at scale.” The mothership can fabricate some things, but its resources, energy, heat rejection, throughput, wear, and mission reserves must be limited so it cannot solve the whole game alone.

The best next step is not “build the full MMO.” It is to formalise and prototype the first vertical slice: one planet region, one mothership, one robot body, one ore deposit, one power source, cut/fill, blueprinting, nanobot construction, mine, refinery, fabricator, remote spawn lab, and fog-of-war sensor model. If that loop is fun and deterministic, the project can scale outward.

## 3. Chronological story of the conversation

### 3.1 The initial maximum-scope question

The user began by asking whether Domino engine and Dominium could support a deterministic game with a full-scale real solar system, recreated planets, custom systems, procedural planets, player-built civilisations, terraforming, cut/fill, megaprojects, machines, devices, factories, fog of war, sparse simulation, client-shared compute, MMO persistence, private servers, and Unreal support. The user already framed the problem in terms of simulation load: only load and simulate what players can sense, collapse everything else, and make construction/destruction sparse.

### 3.2 First architecture response

The assistant responded with an architecture-first answer. The main point was that the game should be built as a deterministic simulation/database first, with rendering as a client. It recommended fixed ticks, deterministic commands, seeded procedural generation, hierarchical coordinates, sparse terrain deltas, field layers, simulation LOD, event logs, snapshots, state hashes, server authority, and fog-of-war filtering. The assistant also drew a scale boundary: millions of accounts or players spread across shards/regions is possible in principle, but millions in one fully simulated real-time bubble is not a practical target.

### 3.3 User refinement into a robotic civilisation game

The user then gave a long design monologue. The star-system generator should produce planets using real science. The designer should not manually paint everything and should not use arbitrary sliders. Sliders should be bounded to plausible physical ranges. There should also be a way to nudge results or possibly use reverse generation: specify the desired outcome and let the system infer plausible physical parameters.

The user also introduced the main lore and gameplay premise. Humans in the past created a robotic mothership that travels to another solar system, lands on a suitable planet, manufactures robots with advanced technology, and tries to restart civilisation. A future ship might bring human eggs or another payload, but the main gameplay does not depend on that being finalised.

The player is a robot. The player spawns from a physical machine. They may choose a chassis, such as biped, quadruped, spider, tank-like body, or other robot forms. Early spawns come from the mothership. Later, players expand by building remote labs/fabricators that can manufacture bodies from local materials. This makes frontier spawn points an earned industrial milestone.

The user then moved into construction. Robots can justify HUDs, blueprints, task markers, recipe knowledge, and remote AI guidance. Nanobots or an invisible construction force can be used because they are easy to compute and can be explained diegetically. A player can blueprint a plan in the world, inspect it, and then commit it. Cut/fill and construction should be deterministic and non-destructive in the planning phase.

The user considered NPC workers but deprioritised them. Worker NPCs imply pathfinding, labour scheduling, collisions, and simulation complexity. The user’s conclusion was that if computers and robots are doing the work, the game should admit that directly. The player should have automation from the beginning, even if advanced machines still require progression.

The user also explained why the mothership does not trivialise everything. It contains recipes and can synthesize some objects, but it has finite resources and limited throughput. It can help early players but eventually must be replenished with planet-derived materials and supported by local factories. The ship is a knowledge and precision bottleneck, not an infinite city printer.

### 3.4 Second synthesis response

The assistant then synthesised the game as a robotic seed-civilisation design. It framed the project as: players are robot avatars; the mothership contains human knowledge, starter resources, spawn fabrication, and AI planning; players explore, survey, mine, refine, build cities, create spawn labs, automate industry, and eventually terraform or build megaprojects.

The assistant proposed several major systems: science-bounded forward/reverse planet generation, field layer stacks, mothership constraints, robot chassis, physical inventory, nanobot construction pipelines, no worker NPCs, machine graph compilers, easy-to-start/hard-to-advance cities, AI-planner quest markers, fog-of-war sensors, single-player/private/MMO modes, Unreal as a visual client, and a first vertical slice.

### 3.5 Preservation/export phase

The user then uploaded a maximum-fidelity preservation prompt. That prompt requested a human-readable report first, then structured registers, a context transfer packet, a YAML-style spec sheet, an aggregator packet, a self-audit, downloadable files, a ZIP package, and a final in-chat reader. A preservation package was generated with 10 files plus a ZIP. In the workspace, two related file sets exist: one labelled `Dominium_Deterministic_Solar_System_Architecture` and one labelled `Dominium_Robotic_Seed_Civilisation_Architecture`. This companion task now bundles those existing files, the uploaded prompt, this new report, and an updated package index into a single consolidated ZIP.

## 4. Main design topics preserved

### 4.1 Deterministic Domino simulation core

FACT/INFERENCE: The user wants determinism, sparse simulation, fog of war, and large-scale persistence. The assistant recommended that Domino be the deterministic authoritative simulation core, with rendering separated. This should be treated as a strong architecture recommendation, not necessarily a final engine decision until explicitly accepted and prototyped.

The core idea is that the universe is not a giant live map. It is a deterministic state transition system. Commands, seeds, source data, field layers, sparse deltas, graphs, ledgers, snapshots, and hashes reconstruct the world. Rendering converts currently sensed state into visible terrain, machines, robots, effects, and UI.

### 4.2 Full-scale solar systems and procedural planets

FACT: The user wants star systems/solar systems and planets generated from realistic parameters. The wording briefly used “galaxy,” but the described scope was closer to custom solar systems with many planets. This remains an open scope issue: whether the project should call the launch scope a star system, solar system, galaxy, universe, or multiverse.

The design should support physical parameters such as orbit, mass, radius, atmosphere, water, rotation, moons, climate, geology, and resource distribution. Sliders should be bounded by plausible science. The user wants designer control, but not arbitrary manual painting as the primary workflow.

### 4.3 Reverse generation and designer nudging

FACT: The user suggested a reverse process where a designer creates or describes the desired planet and the generator infers plausible parameters that fit it. This is an important tool idea. It lets designers say “I want a fun planet with these features” while still preserving scientific plausibility.

UNCERTAIN: The actual algorithm remains undecided. It could be constraint solving, search over parameters, evolutionary generation, simulated annealing, or manual tuning with plausibility feedback.

### 4.4 Field layers, saves, packs, terraforming, construction, and destruction

FACT: The user wants procedural fields overlaid with painted/designed data and wants the same technology to support save files, planet packs, and in-game terraforming. The assistant formalised this as a field layer stack.

The key preservation point is that worldgen layers and gameplay layers should not be treated the same. A designer/editor layer can create a mountain or ocean as an authored override. A gameplay terraforming layer should conserve mass, energy, heat, time, permissions, and tool capability. This distinction prevents the save/packs system from turning into free in-game creation.

### 4.5 Robotic mothership lore and game loop

FACT: The user described a robotic mothership sent by humans to restart civilisation. The mothership lands on a habitable planet, manufactures robots, and contains knowledge and starter resources. Possible mystery lore around future humans/human eggs was mentioned but not finalised.

This premise is extremely useful because it explains many game systems at once: robot bodies, HUD, blueprints, recipe book, AI guidance, spawn fabrication, early tools, finite starting resources, and the need to build local industry.

### 4.6 Robot players and physical spawn economy

FACT: Players are robots, not humans. New players or respawns are manufactured by physical machines. Early bodies are fabricated at the mothership. Later bodies can be created at remote spawn labs built by players.

This changes the normal survival-game loop. Expansion is not only geographic; it is reproductive/infrastructural. Building a remote spawn lab means extending civilisation’s ability to create new agents at the frontier.

### 4.7 Nanobot construction and blueprinting

FACT: The user proposed nanobots or an invisible force to do construction because it is computationally easy and fits robots. The assistant recommended bounding this by materials, energy, time, heat, sensor coverage, permissions, and tool capability.

The key implementation idea is a staged pipeline: preview, plan, reserve, stage, execute, commit, operate. The preview can be free and client-side; the committed build must be validated and deterministic.

### 4.8 Automation over worker NPC labour

FACT: The user explicitly moved away from worker NPC labour because it is expensive to compute and because a robotic civilisation does not need simulated human workers. This is one of the strongest design decisions from the conversation.

The preserved rule should be: do not make worker NPCs the default mechanism for construction, production, or city simulation. Use automation, AI agents, machine controllers, drones, construction swarms, logistics graphs, and process abstractions. Wildlife/mobs may exist locally, but intelligent labour should be abstract unless deliberately added for a narrow reason.

### 4.9 Machines, factories, and process graphs

FACT: The user wants players to make machines, vehicles, rockets, devices, and factories, but wants the engine to summarise machines as process equations or functional objects wherever possible. The assistant called this a machine graph compiler.

This is central to performance and gameplay. A factory can be visually expanded when a player is nearby, but far away it should become a graph with inputs, outputs, throughput, energy use, heat, reliability, maintenance debt, and buffers. The same principle applies to player-created machines: the shape and parts create capabilities, but the server should compile the result into bounded functions.

### 4.10 Cities and progression

FACT/INFERENCE: The user wants cities to be easy to build but advanced industry to require city-scale infrastructure. The assistant proposed a tiered progression: mothership camp, outpost, settlement, industrial city, planetary infrastructure, terraforming civilisation, megaproject civilisation.

The important design point is that the basics should be accessible quickly. Advanced technology should require materials, power, precision, logistics, fabrication chains, clean environments, cooling, and coordination.

### 4.11 Fog of war and sensed-only simulation

FACT: The original user question required fog of war and simulating/loading only what players can sense. The assistant formalised this as an information model: current observation, remembered state, inferred state, unknown state, and server-only hidden truth.

For MMO play, this is not just a rendering feature. A client must not receive hidden enemy bases, rare resources, secret terrain edits, or other unavailable truth. This directly limits client-shared compute.

### 4.12 Single-player, private universes, and MMO

FACT: The user wants the game to support single-player multi-universe play and possibly MMO/private server play. The assistant recommended using the same core rules across modes, with trust and authority varying by mode.

Single-player can be local and more relaxed. Private servers can allow custom systems and mods. Official MMO mode should be strict: server authority, filtered fog-of-war data, auditability, anti-cheat, and careful limits on client compute.

### 4.13 Unreal’s role

INFERENCE/UNCERTAIN: The assistant recommended Unreal as a renderer/client/tooling layer rather than the authoritative universe engine. This is a strong architecture recommendation, but it remains unverified as a project decision. Future work should verify current Unreal features and decide how much of the client/runtime should be Unreal versus Domino custom code.

### 4.14 First vertical slice

INFERENCE: The assistant recommended a first vertical slice: one planet region, one mothership, one robot chassis, one resource deposit, one power source, cut/fill, blueprinting, nanobot construction, mine, refinery, fabricator, remote spawn lab, and fog-of-war sensor system. This has not been explicitly approved as final, but it is the best candidate next milestone because it tests the central gameplay loop without requiring full planet/MMO scale.

## 5. Decisions and status

| ID | Decision or design direction | Status | Label | Confidence |
|---|---|---|---|---|
| DECISION-01 | Dominium should use deterministic sparse simulation rather than full dense world simulation. | Strong direction; final implementation details open | FACT + INFERENCE | 4/5 |
| DECISION-02 | Planet generation should be scientifically bounded, not arbitrary. | User-stated direction | FACT | 5/5 |
| DECISION-03 | Designer override/painted fields should layer over procedural generation. | User-stated direction; format undecided | FACT | 4/5 |
| DECISION-04 | Save/pack/terraforming/construction systems should share field/delta technology where possible. | User-stated direction plus assistant formalisation | FACT + INFERENCE | 4/5 |
| DECISION-05 | The core lore is a robotic seed mothership restarting civilisation. | User-stated premise | FACT | 5/5 |
| DECISION-06 | Players are robot bodies manufactured by physical machines. | User-stated premise | FACT | 5/5 |
| DECISION-07 | New spawn points should be physical labs/fabricators players build. | User-stated direction | FACT | 5/5 |
| DECISION-08 | Mothership knowledge explains recipes, HUD, blueprints, and quest-like planning. | User-stated direction | FACT | 5/5 |
| DECISION-09 | Mothership fabrication must be limited by resources/throughput/energy/etc. | User-stated direction plus assistant constraints | FACT + INFERENCE | 4/5 |
| DECISION-10 | Avoid worker NPC labour as core simulation. | Strong user-stated direction | FACT | 5/5 |
| DECISION-11 | Use automation, nanobots, and machine/process graphs instead. | Strong user-stated direction | FACT | 5/5 |
| DECISION-12 | Machines/factories should collapse into equations/graphs when not actively viewed. | User-stated direction | FACT | 5/5 |
| DECISION-13 | Public MMO clients should not be trusted with hidden truth. | Assistant recommendation from fog-of-war logic | INFERENCE | 4/5 |
| DECISION-14 | Unreal should be client/renderer/tooling, not sole authoritative universe engine. | Assistant recommendation; requires user/project confirmation | INFERENCE / UNCERTAIN | 3/5 |
| DECISION-15 | First vertical slice should prove mothership-to-remote-spawn-lab loop. | Assistant recommendation | INFERENCE | 4/5 |

The main caveat is that DECISION-13 through DECISION-15 are not direct user decisions. They are strong recommendations that follow from the conversation, but they should be confirmed before becoming binding.

## 6. What was deferred or put off for later

Several important subjects were not fully specified and should remain open:

1. **Exact launch scope:** The user used broad language around solar systems, galaxies, universes, and multiverses. The first official scope still needs to be chosen.
2. **Planet generator schema:** The exact physical parameters, realism scoring, and solver mechanics remain undefined.
3. **Field/delta data format:** The project needs concrete schemas for procedural fields, painted overlays, saved deltas, terraforming, construction, destruction, and mod packs.
4. **Mothership economy:** Starting reserves, fabricator throughput, spawn costs, mission reserves, heat limits, replenishment rules, and failure/recovery modes need design.
5. **Robot chassis:** Candidate bodies were discussed, but launch chassis, stats, hardpoints, locomotion, inventory, and progression remain open.
6. **Nanobot tiers:** The ability set, range, throughput, energy cost, and construction rules remain open.
7. **Machine graph compiler:** The system that turns player-built machines into validated capabilities is a major unresolved technical design.
8. **City liveliness without workers:** The project needs ways to make automated cities feel alive through drones, logistics, lights, traffic, machine sound, sensors, screens, and infrastructure feedback.
9. **Fog-of-war sensor model:** Current observation, remembered maps, inferred maps, map sharing, survey tools, satellites, and hidden state rules need definition.
10. **Client-shared compute:** Public MMO, private server, and single-player trust boundaries need separate rules.
11. **Unreal integration:** Current Unreal capabilities and limits need verification before committing to an Unreal-heavy pipeline.
12. **Vertical slice:** The proposed first playable loop needs a formal milestone document.
13. **Governance, permissions, and griefing:** Claims, ownership, terraforming rights, destruction permissions, salvage rules, decay, and anti-lag budgets were identified but not designed.
14. **Versioning and migration:** Ruleset versions, generator versions, schema versions, mod versions, and old-save compatibility need design.
15. **Verification:** Current technical claims require fresh checking before inclusion in a formal spec.

## 7. Rejected, superseded, or deprioritised ideas

| ID | Idea | Status | Why preserved |
|---|---|---|---|
| REJECTED-01 | Manual painting as the primary planet creation method | Deprioritised | The user wants procedural science-bounded generation first, with painting as override. |
| REJECTED-02 | Arbitrary unrealistic planet sliders | Deprioritised | The user wants realistic bounds and plausibility. |
| REJECTED-03 | Worker NPC labour as the construction/city core | Strongly deprioritised | It creates pathfinding/scheduling cost and conflicts with robotic automation premise. |
| REJECTED-04 | Simulating every machine part everywhere | Rejected as infeasible | Machine functions should collapse into process graphs/equations. |
| REJECTED-05 | Treating Unreal Actors as every piece of authoritative world truth | Assistant-rejected | Too heavy and not appropriate for deterministic sparse planetary/MMO state. |
| REJECTED-06 | Trusting public clients with hidden fog-of-war truth | Assistant-rejected | Breaks secrecy and anti-cheat. |
| REJECTED-07 | Letting the mothership fabricate infinite finished goods | Rejected by design direction | Would erase the need for industry, cities, and logistics. |

These are important because future chats may accidentally reintroduce them as defaults. The most important rejected/default trap is worker NPC labour.

## 8. Key tradeoffs

### 8.1 Scale versus fidelity

The project wants full planets, cities, machines, factories, and possibly MMO scale. That cannot be done with dense active simulation everywhere. The proposed solution is multi-resolution simulation: active local fidelity near players, aggregate process graphs for distant systems, sparse deltas for terrain/building edits, and lazy fast-forward for unobserved systems.

### 8.2 Realism versus designer control

The user wants realistic generation, but also wants fun and designer control. The implied solution is bounded sliders, plausibility scores, and explicit override layers.

### 8.3 Convenience versus progression

Nanobots, blueprints, and mothership recipes make construction convenient. Finite materials, power, heat, throughput, logistics, and machine capability preserve progression.

### 8.4 Creativity versus exploit prevention

Players should create machines and megaprojects. But arbitrary designs can become server-load exploits or economy exploits. A machine compiler and construction complexity budgets are needed.

### 8.5 Client compute versus hidden information

Clients can help with rendering, mesh generation, local prediction, and visible/verifiable simulation. They cannot be trusted with hidden MMO truth, secret resources, enemy bases, or economy-critical state.

## 9. Artifact and file inventory explanation

Two generated file sets are present:

1. `Dominium_Deterministic_Solar_System_Architecture__...`  
   This is the latest full preservation package created after the uploaded prompt. It contains a manifest, human-readable report, context packet, spec sheet, registers, aggregator packet, reader brief, verification/audit file, future-chat bootstrap prompt, in-chat reader, and ZIP archive.

2. `Dominium_Robotic_Seed_Civilisation_Architecture__...`  
   This appears to be an earlier or alternate generated preservation file set focused on the robotic seed-civilisation framing. Because it exists in the workspace and is relevant, it is preserved in the consolidated ZIP rather than discarded.

3. `Pasted text.txt`  
   This is the uploaded maximum-fidelity preservation prompt. It is preserved as source context because it defines the required output structure and preservation standards.

4. This new companion report  
   This file adds a readable narrative explanation and checks that the current package preserves the conversation and generated artifacts.

5. Updated consolidated package index  
   A new index file describes what is in the consolidated ZIP and how to use it.

6. New consolidated ZIP  
   The final ZIP bundles the previous generated files, prior package variant, source prompt, this companion report, and the updated index into one archive.

## 10. Open questions and unresolved issues

The highest-priority open questions are:

1. **What is the first formal vertical slice?**  
   Recommended answer: mothership to remote spawn lab, but the user should confirm.

2. **What is the exact data model for fields and sparse deltas?**  
   This affects planets, saves, packs, terraforming, cut/fill, construction, and destruction.

3. **What exactly are the mothership’s limits?**  
   These limits are the foundation of progression.

4. **What are the initial robot chassis?**  
   This affects locomotion, inventory, construction capability, exploration, and identity.

5. **How do machines compile into simulation graphs?**  
   This is central to performance and player creativity.

6. **How does fog of war work mechanically and securely?**  
   It affects sensors, map data, client replication, hidden enemies/resources, and MMO trust.

7. **What can clients compute?**  
   Single-player, private servers, and official MMO need different trust models.

8. **What should Unreal be used for?**  
   The project needs a verified decision on Unreal as renderer/tooling/client versus deeper runtime integration.

9. **How do cities feel alive without worker NPCs?**  
   The automation-first model needs strong visual and systemic feedback.

10. **What governance and anti-griefing systems exist?**  
   Terraforming, construction, destruction, spawn labs, and megaprojects require claims, permissions, decay, and moderation rules.

## 11. Risks and failure modes

| Risk | Why it matters | Mitigation |
|---|---|---|
| Scope explosion | Full solar systems, MMOs, machines, cities, and terraforming could overwhelm development. | Build the vertical slice first. |
| Treating brainstorms as final | User’s exploratory ideas could be over-promoted into hard requirements. | Preserve labels and confirmation status. |
| Losing the automation pivot | Future designs might reintroduce worker NPC labour. | Mark no-worker-NPC labour as a core design direction unless explicitly revisited. |
| Nanobots becoming magic | Free construction would destroy progression and economy. | Require material, energy, time, heat, capability, permissions, and logistics. |
| Mothership trivialising industry | Infinite high-end fabrication erases the game loop. | Limit reserves, throughput, heat, wear, scale, and mission protocols. |
| Machine designs becoming lag machines | Player creativity can weaponise simulation cost. | Use compiler validation and complexity budgets. |
| Client compute leaking secrets | MMO fog-of-war can fail if hidden data is sent to clients. | Server-authoritative truth and filtered observation packets. |
| Unreal overreach | Treating Unreal as the whole universe engine may create deterministic and scale problems. | Keep Domino authoritative unless proven otherwise. |
| Empty automated cities | No worker NPCs may make cities feel lifeless. | Use drones, moving logistics, sound, lights, machine activity, sensor overlays, traffic abstractions. |
| Stale technical claims | Engine/network/API data may change. | Put external claims in verification queue. |
| Aggregation errors | Later master spec may merge conflicting reports incorrectly. | Use artifact IDs, labels, and manual review. |

## 12. Verification queue

Before formalising the technical spec, verify:

- Current Unreal Engine large-world, World Partition, PCG, MassEntity, Iris/Replication, runtime mesh, and deterministic limitations.
- Current licensing and usage conditions for NASA/JPL/Horizons/SPICE/IAU or any real solar-system datasets.
- Deterministic math strategy across platforms.
- Viability of sparse terrain deltas with planetary coordinate systems.
- Network/server authority strategy for fog-of-war and persistent MMO regions.
- Feasibility of a machine graph compiler and performance budgets.
- Storage and replay strategy for large persistent universes.
- Mod/planet-pack security and versioning.

## 13. Recommended next-action sequence

1. **Confirm the design pillars.**  
   Draft 5–8 pillars and mark which are hard requirements versus guiding principles.

2. **Define the first vertical slice.**  
   Write a milestone for the mothership-to-remote-spawn-lab loop.

3. **Specify the deterministic core invariants.**  
   Define tick model, command log, world hash, save/load, replay, and deterministic RNG.

4. **Specify field/delta data structures.**  
   Define terrain/material/climate/resource fields, overlays, edit logs, and conservation rules.

5. **Design the mothership economy.**  
   Define starting materials, spawn costs, fabrication throughput, energy, heat, wear, and replenishment.

6. **Design the first robot chassis.**  
   Pick two or three bodies that test locomotion, construction, cargo, and exploration.

7. **Design nanobot construction tiers.**  
   Define what early nanobots can cut, fill, assemble, repair, and survey.

8. **Draft the machine graph compiler.**  
   Define machine modules, ports, inputs, outputs, throughput, heat, reliability, and validation.

9. **Draft the fog-of-war model.**  
   Define sensors, current/remembered/inferred/unknown state, and hidden server truth.

10. **Verify Unreal integration assumptions.**  
   Decide what Unreal does, what Domino does, and where the boundary is.

## 14. What to preserve above all

- Dominium’s identity as a **robotic seed-civilisation game**.
- Domino’s likely role as a **deterministic sparse simulation/data engine**.
- The rule that **worlds are fields, graphs, ledgers, sparse deltas, event logs, and snapshots**, not just giant maps.
- The user’s strong preference to **avoid worker NPC labour** and use automation instead.
- The mothership as **knowledge, spawn source, finite precision fabricator, and early bottleneck**.
- The physical spawn economy: **remote spawn labs are built infrastructure**.
- The construction model: **blueprint, reserve, stage, execute, commit**.
- The machine model: **visual locally, aggregate/process-graph remotely**.
- The fog-of-war rule: **do not send hidden truth to clients in public MMO mode**.
- The immediate practical milestone: **prove the mothership-to-remote-spawn-lab loop**.

## 15. Best questions to ask next

### Understanding

1. What is the shortest accurate description of Dominium after this conversation?
2. Which parts are user-stated FACT and which are assistant INFERENCE?
3. What changed when the user moved away from worker NPC labour?

### Decisions

4. Should “automation over worker NPC labour” become a hard project pillar?
5. Should “Domino owns truth; Unreal renders local state” become a formal architecture rule?
6. Should the official launch scope be one designed star system rather than galaxy-scale?

### Tasks

7. Turn the first vertical slice into a formal milestone plan.
8. Draft the field/delta data model.
9. Draft the mothership economy.
10. Draft the machine graph compiler.

### Artifacts

11. Which of the two preservation file sets should be treated as canonical?
12. Merge the two file sets into one master report without duplication.

### Risks and verification

13. What current Unreal claims need verification before we commit?
14. How do we stop nanobot construction from breaking progression?
15. How do we make automated cities feel alive without worker NPCs?

### Spec-book integration

16. Which future master spec chapters should this chat feed into?
17. Which recommendations need user confirmation before becoming requirements?
18. What cross-chat conflicts should the aggregator look for?

## 16. Compact few-minute summary

This conversation established a major design direction for Dominium. The project should not be thought of as a normal open-world map with a huge number of objects. It should be a deterministic, sparse, data-driven universe simulation. The world is reconstructed from seeds, procedural fields, overlays, sparse deltas, command logs, graphs, ledgers, snapshots, and hashes. Rendering engines such as Unreal can show the local visible area, but they should not be assumed to own the authoritative world truth.

The user wants procedurally generated solar systems and planets that are scientifically bounded. Designers should set realistic physical parameters and nudge results rather than manually painting entire planets or using arbitrary fantasy sliders. The user also wants a possible reverse-generation workflow: specify the planet desired, then let the generator search for plausible orbital/geophysical parameters. Procedural fields should be layerable with painted fields, and the same field/delta technology should support saves, planet packs, terraforming, construction, and destruction.

The game premise became much clearer. Humans launched a robotic mothership to another solar system. The mothership lands on a habitable planet and manufactures robot bodies to restart civilisation. Players are robots. They spawn from physical fabrication machines, choose different robot chassis, and later build remote spawn labs so civilisation can expand across the planet. This premise explains the HUD, recipe knowledge, blueprints, AI guidance, respawn, construction, and why the player starts with advanced knowledge but not unlimited industrial capacity.

The mothership is not an infinite factory. It has finite reserves, limited throughput, energy limits, heat limits, wear, scale limits, and mission protocols. It can provide recipes and precision fabrication, but players must eventually mine, refine, build power, create factories, construct cities, and replenish the mothership. The ship is excellent at knowledge and precision; the planet is required for scale.

The strongest design pivot was away from worker NPC labour. The user considered workers, but rejected or deprioritised them because they require pathfinding, scheduling, physics, collision, and expensive simulation. Since the civilisation is robotic, work should be done directly by automation: nanobots, AI controllers, drones, machine graphs, logistics systems, and process diagrams. Cities should be easy to start and can be automated from the beginning, while advanced industry still requires complex infrastructure.

Construction should use blueprints and nanobots. Players can preview a plan for free, then commit it when materials, energy, permissions, tool capability, time, heat, and logistics are available. Cut/fill, terraforming, and construction should be deterministic and saved as sparse deltas. Nanobots provide the convenient interaction fantasy, but they must not become magic.

Factories and machines should be visually rich near the player but collapse into process graphs when distant. A player-built machine should compile into a functional object with inputs, outputs, power draw, heat output, throughput, buffers, reliability, and maintenance debt. This allows player creativity without simulating every gear, belt, item, or robot everywhere in the universe.

Fog of war matters both for gameplay and multiplayer security. The game should only load and simulate what players can sense at high fidelity. In public MMO mode, clients should not receive hidden truth. They may help with rendering, local prediction, visible mesh generation, or verifiable non-secret jobs, but they should not compute hidden enemy bases, secret resources, or authority-critical economy/combat outcomes.

The main unfinished work is formal specification. The best next action is to define the first vertical slice: one planet region, one mothership, one robot body, one resource deposit, one power source, cut/fill, blueprinting, nanobot construction, a mine, refinery, fabricator, remote spawn lab, and fog-of-war sensors. That loop proves the core identity of the game before attempting full planets, megaprojects, or MMO scale.

## 17. Final check performed

I checked the workspace for generated files and found two relevant preservation sets plus the uploaded source prompt. I created this new companion report, an updated consolidated package index, and a single ZIP containing the existing files plus the new materials. The package is intended to be readable by humans and useful for later aggregation.
