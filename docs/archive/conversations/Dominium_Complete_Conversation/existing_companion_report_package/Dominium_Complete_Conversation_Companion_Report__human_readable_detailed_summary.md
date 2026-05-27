# Dominium / Domino — Complete Conversation Companion Report

**Date anchor:** 2026-05-27 Australia/Melbourne  
**Source scope:** This conversation and the files created during this conversation.  
**Purpose:** This report is a human-readable companion to the structured preservation package. It explains, in ordinary language, what happened in the conversation, what was discussed, what was decided or only proposed, what was deferred, what artifacts were created, and what should be preserved for future Dominium / Domino work.

---

## 1. Executive Orientation

This conversation developed the foundation for **Dominium**, a deterministic, procedural, solar-system-scale robotic civilisation game built with or around a custom **Domino engine**. The central challenge was how to make a game that can contain full-scale solar systems, procedurally recreated or custom planets, terraforming, cut/fill construction, machines, devices, factories, megaprojects, fog of war, sparse destruction/construction, and both single-player/private-universe play and possible MMO-style persistent-universe play.

The key technical conclusion was that the world cannot be treated as a normal game-engine level full of live actors. The world must be a deterministic simulation and data system first. Domino should store the true universe as seeds, rules, fields, sparse deltas, event logs, snapshots, hashes, graphs, and ledgers. Rendering engines such as Unreal can be used to display and interact with the local area, but they should not be the sole source of authoritative world truth.

The key creative conclusion was that Dominium should be a **robotic seed-civilisation game**. Humans in the past launched a robotic mothership to another star system. The ship lands on a suitable planet and manufactures robot bodies to restart civilisation. Players are not ordinary human settlers. They are robot minds instantiated into physical chassis fabricated by machines. This premise explains the HUD, respawning, blueprint projection, recipe knowledge, construction automation, remote spawn labs, and the absence of worker NPC labour.

The strongest gameplay direction was to avoid simulating human-like workers as the foundation of cities and construction. The user explicitly identified labour, worker pathfinding, scheduling, and human-like simulation as expensive and unnecessary. Since the civilisation is robotic, the game should use nanobots, drones, machine controllers, AI planners, construction swarms, process graphs, and infrastructure systems instead. Cities should be made from power, logistics, fabrication, sensors, permissions, spawn labs, roads, rails, pipes, machines, and production networks rather than thousands of simulated people walking around.

The strongest technical design pattern was **high-fidelity when sensed, collapsed when not sensed**. A factory near the player can be visually rich. It can show belts, arms, lights, sparks, vehicles, modules, robots, and moving parts. Far away, the same factory should collapse into a deterministic process equation: inputs, outputs, power draw, heat, throughput, maintenance debt, buffers, and failure chances. A planet nobody has modified should exist mostly as seed plus generator version. A mined or terraformed area should exist as sparse deltas over the procedural base.

The conversation also produced a preservation/export package: a manifest, human-readable report, context transfer packet, spec sheet, structured registers, aggregator packet, reader brief, verification/audit file, future-chat bootstrap prompt, in-chat reader, and ZIP handoff package. This companion report adds a more narrative explanation and bundles all existing files into a single checked ZIP.

---

## 2. Chronological Story of the Conversation

### 2.1 The opening feasibility question

The user began with a broad, ambitious feasibility question: could Domino and Dominium support a deterministic game with a full-scale real solar system, recreated planets, custom solar systems and planets, procedural universe generation, player-built civilisations, terraforming, cut/fill terrain, megaprojects, machine and factory design, fog of war, sensed-only loading/simulation, sparse construction/destruction, MMO persistence, single-player multiverse play, and client-shared compute? The user also asked whether Unreal could do this without lag, with low latency and high FPS, and potentially millions of players spread across shards or private servers.

This set the technical frame: the problem was not simply graphical scale. It was about determinism, simulation ownership, sparse persistence, fog of war, distributed compute, and scalable interaction.

### 2.2 The first architecture response

The assistant responded by reframing Dominium as a deterministic simulation/database problem. The recommendation was that Domino should be the authoritative world engine, and rendering engines should be clients. The world should be represented through deterministic rules, event logs, sparse deltas, state hashes, generator versions, fixed ticks, hierarchical coordinates, and simulation levels of detail.

The answer drew an important feasibility boundary: millions of players can share a logical universe if distributed across many cells, regions, shards, or private servers, but millions cannot all be in the same fully simulated low-latency local interaction bubble at once. This is not a stylistic point; it is a network, CPU, bandwidth, and simulation-limit point.

### 2.3 The user refined the project into a game identity

The user then gave the most important creative design monologue of the conversation. The project shifted from a generic scale question into a specific premise and loop.

The user described a procedurally generated solar system or configurable system, with as many planets as desired and realistic parameter bounds. Planet generation should use real science rather than arbitrary sliders. Designers should not manually paint everything by default; instead, they should set high-level physical parameters, get a procedural planet, and then nudge or override details where needed.

The user also proposed a reverse-generation idea. Instead of only choosing orbital and planetary parameters and seeing what planet results, a designer might specify the desired planet outcome and let the system search for plausible parameters that produce it. This would let designers make playable worlds without breaking the scientific tone.

The user then described field overlays. Procedural fields should be layered with painted fields and designer overrides. The same technology that powers save files should also support packs, planet design, terraforming, cut/fill, and in-game edits.

The lore premise then emerged: humans in the past launched a robotic mothership to another solar system. It lands on the most habitable planet and manufactures robots using advanced technology, possibly nanotechnology, in order to restart civilisation. There could be mystery lore involving later ships containing human eggs or payloads, but the main gameplay premise is the robotic restart of civilisation.

Players spawn from physical machines. A new player chooses a robot body type, such as a biped, quadruped, spider, tank-like body, or other chassis. The original mothership can fabricate early bodies from limited reserves. To expand across the planet, players must physically travel and build new labs or spawn points that can fabricate bodies from local materials and power.

Construction should be explained diegetically through robotic HUDs, blueprints, nanobots, and electromagnetic communication with construction swarms. The player can preview a build nondestructively as a holographic or HUD blueprint, then commit the build once resources, permissions, and construction capacity are available.

The user considered worker NPCs but moved away from them. Worker NPC labour would require pathfinding, scheduling, collision, and simulation. Since the civilisation is robotic, the game should not make the computer pretend to be people doing labour. It should let the computer be the worker: automation, nanobots, AI agents, machines, process diagrams, and construction systems.

The mothership should also explain why players have recipes and do not need to invent CPUs, rail gauges, calendars, or basic industrial theory from scratch. The ship already carries human knowledge. The progression challenge is not discovering the idea of a CPU; it is building the industrial chain capable of fabricating CPUs locally.

The user also identified the need to limit the mothership. If the mothership can fabricate anything perfectly at any scale, it invalidates the game. Therefore it should have finite material reserves, low throughput, heat limits, size limits, mission reserves, wear, and other constraints. It can help early, but players eventually need mines, refineries, factories, logistics, power grids, cities, and industrial capacity.

### 2.4 The second synthesis response

The assistant then synthesised the design into the phrase: **robotic seed-civilisation game**. It organised the ideas into systems: science-bounded procedural worldgen, reverse planet generation, field-layer stacks, mothership constraints, robot chassis, physical inventory, nanobot construction, cut/fill terrain, no worker NPCs, machine graph factories, city progression, AI-planner quest markers, fog-of-war sensors, single-player/private/MMO modes, Unreal as client/rendering/tooling, and the first vertical slice.

A key recommendation was that nanobots should be construction actuators, not magic. They can cut, fill, weld, assemble, disassemble, reinforce, repair, and survey, but each committed operation must require material, energy, time, heat handling, capability, permission, and deterministic validation.

Another key recommendation was that machines and factories should compile into process graphs. The player may build visually complex machines, but the simulation should reduce them to validated capabilities, inputs, outputs, throughput, power draw, heat, mass, maintenance, and reliability. This allows creative engineering while avoiding the need to simulate every part everywhere forever.

The assistant also proposed a first vertical slice: one planet region, one mothership, two robot chassis, one resource deposit, one power source, cut/fill, blueprinting, a nanobot construction swarm, a mine, a refinery, a fabricator, a remote spawn lab, and fog-of-war sensors.

### 2.5 The preservation/export package

The user uploaded a detailed preservation prompt requiring a maximum-fidelity human-readable report, structured registers, context transfer packet, spec sheet, aggregator packet, self-audit, files, and ZIP export. The assistant produced a complete package with sections 0–39, including the human-readable report, registers, spec sheet, future-chat packet, aggregator packet, audit, reader guide, and downloadable files.

### 2.6 This companion report and complete bundle

The user then asked for an accompanying human-readable detailed summary/report of the entire conversation and requested that everything be checked and bundled into a single ZIP. This file is that companion report. It sits alongside the earlier structured preservation files and is bundled with them in the new complete ZIP.

---

## 3. Major Design Outcomes

### 3.1 Domino should be treated as the authoritative deterministic core

**Status:** Assistant recommendation, strongly aligned with the user’s requirements.  
**Label:** INFERENCE unless explicitly ratified later.

The conversation repeatedly pointed toward a custom deterministic engine core. Domino should own true world state, deterministic simulation, field layers, sparse construction/destruction, event logs, state hashes, fog-of-war truth, material ledgers, machine graphs, and persistence. A renderer such as Unreal should display only local, sensed, permitted state.

This matters because a full-scale editable solar-system MMO cannot be built as one normal live scene. Determinism, replay, sparse persistence, and secret-state filtering require a simulation/data model deeper than a renderer.

### 3.2 Procedural planets should be science-bounded but designer-steerable

**Status:** User-stated design direction.  
**Label:** FACT.

Planet and system generation should be controlled by plausible physical parameters: orbital configuration, star type, planet mass/radius/density, atmosphere, water, climate, geology, resources, and related fields. Sliders should be bounded to realistic ranges where possible.

But the designer still needs control. The system should allow nudging, overrides, painted layers, and possibly reverse-solving from target planet qualities to plausible physical parameters.

### 3.3 The field-layer/delta model is central

**Status:** User-stated direction plus assistant formalisation.  
**Label:** FACT + INFERENCE.

The same data model should support world generation, designer overrides, planet packs, save files, terraforming, terrain edits, construction, damage, and destruction. The proposed structure is a stack of fields and sparse deltas over a procedural base.

The most important distinction is that editor/worldgen layers may create content without conservation requirements, while gameplay layers should generally conserve mass, material, energy, or equivalent game resources.

### 3.4 The mothership premise solves many design problems

**Status:** User-stated premise.  
**Label:** FACT.

The mothership explains why the player has a HUD, why respawn is physical, why recipes are known, why blueprints exist, why construction is automated, why the early game has a central hub, and why new spawn points are meaningful frontier infrastructure.

The mothership also creates progression tension. It has knowledge and precision fabrication, but limited material reserves, low throughput, heat limits, wear, and mission constraints. This forces players to build local industry.

### 3.5 Players are robot bodies/chassis, not ordinary human settlers

**Status:** User-stated direction.  
**Label:** FACT.

Players spawn into manufactured robot bodies. Possible forms include bipeds, quadrupeds, spiders, tank-like frames, drones, heavy industrial bodies, aquatic bodies, and aerial bodies. The exact launch list is deferred.

This supports diegetic inventory, construction, HUD, respawn, harsh environments, exploration, and body switching.

### 3.6 Automation replaces worker NPC labour

**Status:** Strong user-stated preference.  
**Label:** FACT.

This is one of the most important outcomes. The user explicitly moved away from intelligent worker NPCs because labour and pathfinding are expensive. The world should not need to simulate a society of human-like workers to explain construction or production.

Instead, the civilisation is machine-first: nanobots, drones, AI agents, process graphs, logistics systems, controllers, and construction swarms. Wildlife or mobs may exist, but cities do not rely on worker NPCs as the central productive system.

### 3.7 Machines and factories should compile into process graphs

**Status:** User-stated direction.  
**Label:** FACT.

The user wants players to build machines, vehicles, factories, rockets, and devices, but does not want every component simulated forever. The answer is a machine compiler: visible assemblies become validated functional graphs with inputs, outputs, energy, heat, throughput, reliability, storage, and constraints.

This supports player creativity without allowing unlimited performance costs.

### 3.8 Fog of war is both gameplay and data security

**Status:** User required fog of war; assistant formalised security implications.  
**Label:** FACT + INFERENCE.

Fog of war is not just a visual overlay. It controls what exists in a client’s knowledge, what the server sends, what can be simulated by the player’s machine, and what remains hidden. A client cannot help compute hidden enemy bases or secret resource locations in a public MMO without compromising the game.

### 3.9 Unreal should probably be a client/tooling layer, not the universe authority

**Status:** Assistant recommendation, not user-final.  
**Label:** INFERENCE / UNVERIFIED.

The conversation repeatedly suggested that Unreal can help with rendering, local interaction, UI, visual streaming, animation, PCG tooling, and high-fidelity presentation. It should not be the sole authoritative state engine for a full deterministic editable universe.

This needs verification against current engine capabilities and project needs before becoming a binding architecture decision.

### 3.10 The first vertical slice should prove the core loop

**Status:** Assistant recommendation, not yet user-approved.  
**Label:** INFERENCE.

The proposed first slice is not a full MMO and not a full solar system. It is one playable loop:

1. Spawn from the mothership.
2. Survey terrain.
3. Find ore.
4. Use cut/fill and blueprints.
5. Build power.
6. Build mine/refinery/fabricator.
7. Transport or reserve materials.
8. Construct a remote spawn lab.
9. Spawn or switch body from that lab.
10. Preserve fog-of-war and deterministic replay.

This loop tests almost every core system at small scale.

---

## 4. What Was Decided, What Was Only Proposed, and What Was Deferred

### 4.1 Strong user-stated decisions or directions

These are safest to carry forward as user-originated design direction:

- Dominium should involve procedural solar systems and planets.
- World generation should be science-bounded rather than arbitrary slider art.
- Designers should be able to nudge or override generated planets.
- Field overlays should support procedural generation, painted data, saves, planet packs, and terraforming.
- The lore centres on a robotic mothership that manufactures robots to restart civilisation.
- Players spawn as robot bodies from physical machines.
- Remote spawn points should be built physically by players as frontier infrastructure.
- The mothership contains recipes/knowledge so players do not need to reinvent industrial basics.
- The mothership must have finite capacity, limited resources, or other bottlenecks so local industry matters.
- Nanobot/automated construction is preferred over person-like manual labour simulation.
- Worker NPC labour is deprioritised because pathfinding and labour simulation are expensive.
- Machines/factories should be reducible to process diagrams/equations when possible.
- The game should support single-player/private universes and possibly official MMO-style persistent play.

### 4.2 Assistant recommendations not yet final

These are useful, but should not be treated as user-final decisions unless later accepted:

- Domino as a custom deterministic simulation core separate from Unreal.
- Unreal as a renderer/client/tooling layer rather than authoritative engine.
- Fixed-tick event-sourced architecture with snapshots and hashes.
- Hierarchical coordinate frames for solar-system scale.
- Machine graph compiler as the formal implementation model.
- Server authority over public MMO truth.
- Strict hidden-state filtering for fog of war.
- The specific first vertical slice composition.
- Exact planet generator scoring categories.
- Exact chassis categories and city tier table.

### 4.3 Things explicitly or implicitly put off for later

The conversation deliberately left many items unresolved:

- The exact launch scope: one designed star system, many systems, or true galaxy-scale play.
- The exact deterministic math model.
- The field-layer and sparse-delta file format.
- The exact planet generation parameter schema.
- The reverse-generation solver design.
- The mothership’s reserves, throughput, heat limits, and fabrication rules.
- The robot chassis list and body progression.
- Death, backup, respawn, and memory-state rules.
- Nanobot construction tiers and limitations.
- The machine graph compiler and validation rules.
- Vehicle, rocket, and megaproject abstraction.
- City liveliness without worker NPCs.
- Economy, permissions, factions, governance, griefing, war, and claims.
- Fog-of-war sensor mechanics and map sharing.
- MMO architecture, shard/cell boundaries, authority, and client compute policy.
- Unreal integration details.
- External data and licensing verification.
- The final vertical slice milestone spec.

---

## 5. Artifacts Created or Present

This conversation now contains two preservation/export sets plus this companion report.

### 5.1 Earlier robotic seed-civilisation package

Files named `Dominium_Robotic_Seed_Civilisation_Architecture__...` appear to be an earlier preservation package. They include a manifest, report, context packet, spec sheet, registers, aggregator packet, reader brief, verification/audit file, bootstrap prompt, in-chat reader, and handoff ZIP.

### 5.2 Later deterministic solar-system package

Files named `Dominium_Deterministic_Solar_System_Architecture__...` are the later and more complete preservation package generated after the uploaded preservation prompt. These files cover the human-readable report, context transfer, structured registers, spec sheet, aggregator packet, audit, future-chat bootstrap, and package ZIP.

### 5.3 Uploaded preservation prompt

The file `Pasted text.txt` contains the user’s maximum-fidelity preservation/export instructions. It is an important artifact because it defines the required shape of the preservation package.

### 5.4 This companion report and complete bundle

This report adds a narrative companion summary that focuses on human understanding rather than only structured handoff. It is included in the new complete ZIP together with the existing files.

---

## 6. Key Risks and Failure Modes

### Risk 1 — Treating brainstorms as final decisions

Much of the conversation contains ideas and recommendations. Future work must not treat every assistant-supplied detail as accepted canon. The preservation package uses labels such as FACT, INFERENCE, and UNVERIFIED to avoid this.

### Risk 2 — Reintroducing worker NPC labour by default

The user clearly moved away from worker NPCs because they are computationally expensive and unnecessary for a robotic civilisation. Future assistants should not casually propose a colony-sim labour model unless explicitly exploring an alternative.

### Risk 3 — Making nanobots into magic

Nanobots are useful as a construction interface, but they must be bounded by energy, material, time, heat, capability, storage, permissions, and deterministic validation. Otherwise they trivialise mining, construction, logistics, and industry.

### Risk 4 — Letting the mothership trivialise progression

The mothership can know recipes and perform precision fabrication. It should not be an infinite free factory. Its limits are what force players to build civilisation.

### Risk 5 — Confusing rendering with simulation truth

Unreal or any renderer can display local state, but the project’s scale requires a deeper authoritative data model. If future design puts all truth into live engine actors, the architecture will likely collapse under scale.

### Risk 6 — Hidden-state leaks through client compute

Client-shared compute sounds attractive, but a public MMO cannot give clients hidden fog-of-war state. Clients can help with rendering, visible generation, prediction, or verifiable jobs, not secret enemy or resource simulation.

### Risk 7 — Over-scoping before proving the core loop

The project includes planets, civilisations, terraforming, factories, megaprojects, and MMO persistence. The immediate risk is trying to build all of it before proving the smallest fun loop.

---

## 7. Recommended Next Work

The best next step is to turn the proposed first vertical slice into a formal milestone document. That document should include goals, non-goals, required systems, data structures, success criteria, tests, risks, and scope limits.

Recommended order:

1. Define the core design pillars.
2. Specify the first vertical slice.
3. Define deterministic simulation invariants.
4. Draft the field-layer/sparse-delta model.
5. Define the mothership economy.
6. Define the initial robot chassis.
7. Define nanobot construction operations.
8. Define the first machine graph/process model.
9. Define fog-of-war sensor states.
10. Decide Unreal’s role after current verification.
11. Create a master spec book chapter outline.
12. Compare this package with other old-chat reports and merge carefully.

The first vertical slice should be deliberately small. It should prove that the player can spawn as a robot, survey terrain, find resources, use blueprint/cut-fill construction, build power, mine/refine materials, fabricate parts, create a remote spawn lab, and persist/replay the result deterministically.

---

## 8. What Future Assistants Must Preserve

Future assistants should preserve the following without forcing the user to re-explain it:

- Dominium is being shaped as a robotic seed-civilisation game.
- Domino should probably be a deterministic sparse simulation core.
- Planets are generated from science-bounded parameters and editable field overlays.
- The mothership explains recipes, HUD, spawning, blueprints, and early fabrication.
- The mothership must be limited so local industry matters.
- Players are robot bodies/chassis, not normal humans.
- Remote spawn labs are physical expansion milestones.
- Worker NPC labour is not the default city/construction model.
- Automation, nanobots, AI agents, machine controllers, and process graphs are central.
- Machines/factories should collapse into equations when not locally observed.
- Fog of war is a data/security model, not only a visual layer.
- Public MMO client compute must not reveal hidden state.
- Unreal may be useful as client/tooling, but its role is not final.
- The next practical task is a first vertical-slice spec.

---

## 9. Open Questions to Carry Forward

The following unresolved issues should remain visible:

1. Is the official scope one star system, multiple star systems, or a true galaxy-scale universe?
2. What exact scientific constraints define realistic planet generation?
3. How does reverse planet generation work?
4. What is the field-layer and sparse-delta schema?
5. How are designer/editor layers separated from gameplay-conserved layers?
6. What exact resources does the mothership start with?
7. How fast can the mothership fabricate, and what limits it?
8. What robot bodies exist at launch?
9. How does player identity, death, backup, and respawn work?
10. What can nanobots do at each technology tier?
11. How does the machine graph compiler validate player-created devices?
12. How do cities feel alive without worker NPCs?
13. What are the ownership, claims, permissions, and anti-griefing rules?
14. What exactly does fog of war hide, remember, reveal, or infer?
15. What client compute is safe in public MMO mode?
16. What should Unreal do, and what should remain in Domino?
17. What external data sources and licenses are needed for real solar-system recreation?
18. What is the exact first vertical slice?

---

## 10. Short Human Summary

This conversation defined the foundations of Dominium as a deterministic robotic civilisation game. The first question asked how to support a vast procedural game with full-scale solar systems, planets, terraforming, cut/fill terrain editing, megaprojects, factories, fog of war, sparse simulation, single-player universes, and MMO persistence. The key answer was that this cannot be built as a normal giant Unreal map. It needs a deterministic data/simulation core. Domino should own true world state; a renderer should display only what the player can sense.

The user then gave the project its strongest identity. Humans sent a robotic mothership to another solar system. It lands, manufactures robot bodies, and begins rebuilding civilisation. Players spawn as robots from physical machines. They can choose different chassis and later build remote spawn labs on the frontier. The mothership carries knowledge and recipes, so players do not reinvent basic technology, but it has limited materials and throughput, so players must build mines, refineries, factories, power systems, logistics, cities, and eventually megaprojects.

The user also clarified the world-generation philosophy. Star systems and planets should be procedurally generated from realistic scientific parameters, not arbitrary sliders. Designers should be able to nudge or override outcomes, and the same field/delta technology should support planet packs, save files, painted overrides, terraforming, cut/fill construction, and destruction.

A major design pivot was rejecting worker NPC labour as the main construction/city model. Since the game is about robots, the project does not need to simulate human workers doing jobs. It should use nanobots, drones, AI controllers, machine graphs, and process diagrams. Machines and factories can be visually rich when the player is nearby, but far away they should collapse into deterministic equations for input, output, energy, heat, throughput, buffers, reliability, and maintenance.

The main work still to do is specification. The project needs a first vertical slice, deterministic data model, field-layer schema, mothership economy, chassis list, nanobot construction rules, machine graph compiler, fog-of-war system, multiplayer authority model, and Unreal integration decision. The best next action is to formalise the first playable loop: spawn from the mothership, survey terrain, find ore, use blueprints and cut/fill, build power, build a mine/refinery/fabricator, construct a remote spawn lab, and prove that the result is deterministic, persistent, and fun.
