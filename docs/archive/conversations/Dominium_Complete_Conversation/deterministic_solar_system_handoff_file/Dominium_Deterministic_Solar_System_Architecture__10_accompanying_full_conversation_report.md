# Accompanying Human-Readable Complete Conversation Report — Dominium Deterministic Solar-System Architecture

**Date anchor:** 2026-05-27 Australia/Melbourne  
**Source scope:** This conversation only, plus the uploaded preservation prompt and generated files in the current workspace.  
**Purpose:** This companion report sits beside the full preservation package. It explains the substance of the conversation in one readable document, including the original design discussion, the architectural synthesis, the preservation/export work already done, and the remaining work that should be carried forward.

## 0. Coverage and reliability check

This report covers the visible conversation about **Domino engine** and **Dominium game** architecture, the user's long design monologue about procedural star systems and robotic seed civilisation gameplay, the earlier preservation/export package, and this final bundling request. It also includes the uploaded preservation prompt as a source artifact because that prompt defined the required preservation format and export expectations.

The extraction is high-confidence for the visible chat. It should not be treated as a complete capture of all possible Dominium project history, because there may be prior chats, project memory, or external files not visible here. Where a point came directly from the user, this report treats it as **FACT**. Where a point came from assistant synthesis or recommendation, this report marks it as **INFERENCE** or explains that it remains unconfirmed.

Main limitations:

- **FACT:** The user explicitly described procedural, science-bounded star/planet generation, robot player bodies, a mothership, physical spawn fabrication, nanobot/blueprint construction, finite mothership resources, and automation over worker NPC labour.
- **INFERENCE:** The assistant recommended a deterministic data/simulation core, sparse deltas, event sourcing, state hashes, server authority, and using Unreal mainly as a renderer/client/tooling layer. These are strong architectural recommendations but not necessarily final user-approved project decisions.
- **UNCERTAIN / UNVERIFIED:** Current Unreal capabilities, current NASA/JPL data access/licensing, MMO scale assumptions, and any external technical claims must be verified before becoming a formal project spec.
- **PROJECT-CONTEXT:** The broader names “Domino engine” and “Dominium game” come from the conversation and the project context, but this report does not claim access to hidden project documentation.

## 1. What this whole conversation was about

The conversation was about turning Dominium into an extremely ambitious but computationally plausible game: a deterministic, procedural, solar-system-scale robotic civilisation simulator where players can explore planets, terraform terrain, cut and fill land, construct cities, design machines, build factories, create megaprojects, and play either alone, on private servers, or potentially in a persistent MMO-like official universe.

The first major problem was **scale**. The user wanted full-scale solar systems and planets, potentially real or custom, with planets recreated or generated procedurally from data. The user also wanted the ability to build civilizations and terraform at planetary scale. This immediately created a computational problem: ordinary game engines cannot simulate or render whole planets, whole star systems, and millions of players at full fidelity all at once.

The assistant’s initial answer was therefore architectural: do not make the world a giant Unreal level or a giant scene graph. Make the world a deterministic, sparse, data-driven simulation first. The renderer should be a client of the simulation, not the source of truth. The simulation should use seeds, fields, sparse deltas, event logs, snapshots, hashes, and fixed-tick commands. Only what the player can sense should be expanded and rendered. Everything else should collapse into lower-resolution state, aggregate equations, or procedural seeds.

The second major problem was **game identity**. The user then described the game as a robotic seed-civilisation scenario. Humans in the past launched a robotic mothership to another star system. It lands on the most habitable planet and manufactures robot bodies to restart civilisation. Players are not humans with backpacks and pickaxes. They are robot agents, spawned from real fabrication machines, with diegetic HUDs, sensors, blueprint overlays, and access to inherited human knowledge stored in the ship.

That premise solved several design problems at once. It explains why the player has a HUD. It explains why the player can use blueprints. It explains why there are recipe books and quest markers: the mothership AI and inherited human knowledge can translate goals into construction plans. It explains respawn: a new robot body is physically manufactured. It explains automation: this is a robotic civilisation, so construction and logistics can be handled by nanobots, AI controllers, drones, machine graphs, and factories instead of by simulating thousands of human workers.

The third major problem was **progression**. If the mothership already knows how to build CPUs, railways, calendars, rockets, and advanced machines, why does the player need to build anything? The answer discussed was that the mothership knows the recipes and can do precision fabrication, but it is limited by feedstock, energy, heat, wear, size, throughput, and mission reserves. It may be able to create starter bodies and small advanced parts, but it cannot create infinite cities, rail networks, megaprojects, or sustained planetary industry without players feeding it resources and building local industrial capacity.

The fourth major problem was **simulation cost**. The user explicitly considered worker NPCs but rejected or deprioritised them because labour is expensive to compute: pathfinding, scheduling, movement, stuck states, physics, and replication become a major burden. The user’s design move was to lean into automation from the start. If the computer is doing the work, the game does not need to pretend that a person is doing the work. Instead, factories and machines can be represented as process diagrams: inputs, ticks, outputs, power draw, heat, throughput, reliability, and maintenance debt.

The fifth major problem was **preservation**. The user uploaded a detailed preservation/export prompt and asked for a maximum-fidelity preservation package. The earlier response created a substantial report, registers, spec sheet, aggregator packet, audit, future-chat bootstrap prompt, reader guide, and ZIP package. This current companion report adds a readable bridge over that material and bundles all relevant files into one updated ZIP.

## 2. Chronological narrative of what happened

### 2.1 The initial technical question

The conversation began with the user asking whether Domino engine and Dominium game could support a deterministic game at extreme scale: a full-scale real solar system, fully recreated planets, custom solar systems, procedural universes, player-built civilisations, terraforming, cut/fill terrain editing, megaprojects, devices, machines, factories, fog of war, sensed-only loading/simulation, client-shared compute, MMO persistence, and single-player multi-universe play.

The user also asked whether Unreal could do this with low latency, high frame rates, and millions of players across shards or private universes. This framed the problem as both a simulation architecture question and a feasibility question.

### 2.2 The first architectural answer

The assistant responded that Dominium should be built as a deterministic simulation/database first, with Unreal or another engine only as the renderer/client. The assistant recommended fixed-tick deterministic state transitions, hierarchical coordinates for solar-system scale, procedural planets as immutable base generation plus sparse deltas, simulation LOD, fog-of-war filtering, and server authority for MMO mode.

The answer drew a line between what is plausible and what is not. Millions of accounts or players spread across a logical universe are possible in principle with distributed servers and interest management. Millions in one fully simulated low-latency bubble are not practical. Unreal can help with rendering, streaming, tooling, and local gameplay, but it should not be expected to serve as the authoritative deterministic universe simulator.

### 2.3 The user refined the world-generation model

The user then shifted from engine feasibility into design details. The user wanted a procedural star-system generator rather than arbitrary hand-painted planets. The generator should be science-bounded: designers set major parameters such as orbital ephemera / ephemerides, planet configuration, and physical constraints, then the system generates plausible planets. Designers should be able to tweak or nudge results, but not by manually painting everything from scratch by default.

The user also described a reverse-generation idea. Instead of only entering physical parameters and seeing what planet results, designers might specify the desired planet and have the system solve or search for plausible orbital and planetary parameters that produce something close to that target. This is important because purely forward procedural generation can produce unpredictable or slow-to-find results.

### 2.4 The user introduced field overlays, saves, packs, and terraforming

The user then connected world generation with save technology and terraforming. The same underlying data approach should support procedural fields, painted fields, designer overrides, player edits, planet packs, save files, and in-game terraforming. This implies that a planet is not one static mesh or one painted map. It is a stack of fields and deltas: base procedural data, overrides, gameplay changes, construction, destruction, and temporary previews.

This became one of the key data-model ideas: the same kind of sparse field/delta system can support both development tools and gameplay systems, but gameplay layers must conserve material, energy, and time whereas editor layers may simply author or override content.

### 2.5 The user introduced the robotic mothership premise

The user then described the lore. Humans in the past created a robotic mothership that travels to another solar system, lands on the most habitable planet, and manufactures robots using advanced technology to restart civilisation. The user mentioned possible mystery lore: maybe a future ship contains human eggs or human payloads, and the robots might eventually be expected to prepare the world for humans.

The main gameplay result is that players spawn as robots. A new player enters through a physical spawn machine. The player may choose a robot form such as biped, quadruped, spider, tank-like chassis, or another body type. The mothership uses its reserves to manufacture the body. If players want to expand across the world, they need to travel, gather resources, build a lab/fabricator, and create new spawn points.

This makes frontier spawn points an actual construction and logistics milestone rather than an abstract fast-travel unlock.

### 2.6 The user described nanobot construction and blueprints

The user proposed that because the players are robots, the game can diegetically justify HUDs, blueprints, and construction overlays. Robots can project blueprint stages in the world, preview non-destructive plans, and then commit them when ready. Nanobots or invisible construction forces can perform cut/fill/build operations without requiring the engine to simulate every tiny actor. This is computationally useful and narratively coherent.

The assistant later formalised this as a staged pipeline: preview, plan, reserve, stage, execute, commit, operate. The key constraint is that nanobots should be a construction interface, not magic. They must consume material, energy, time, heat budget, and tool capability.

### 2.7 The user rejected worker NPC labour as the core model

The user considered having NPC workers or labour at first because it creates a reason to automate later. But then the user rejected or strongly deprioritised this. Labour is expensive to compute because it requires pathfinding and agent simulation. The user’s conclusion was that because the civilisation is robotic, the game can start with automation from the beginning. The computer does the work; the game does not need to pretend a person is physically doing every task.

This is one of the most important design pivots in the conversation. Dominium should not become a colonist-management game with thousands of simulated people. It should be a robot/infrastructure game where work is represented by machines, swarms, controllers, power grids, material flows, logistics, and process diagrams.

### 2.8 The user described mothership knowledge and progression

The user argued that players should not have to invent CPUs, railway gauges, calendars, or basic industrial standards because the ship already brought that information. The mothership can serve as a recipe book or design library. It can give the player programs, blueprints, goals, and construction plans.

The progression challenge is not discovering basic knowledge. It is acquiring the materials, energy, infrastructure, and manufacturing chain needed to build advanced things at scale. The mothership might synthesise some tools or parts, but it has finite reserves, low throughput, size limits, heat limits, and other constraints. Eventually players must feed resources back into the mothership and then build independent factories and cities.

### 2.9 The user described easy basic cities and hard advanced industry

The user wanted it to be easy for players to make the bare basics and to build cities, because large player-made cities are central to the game fantasy. But advanced technology should require a city or substantial infrastructure. This implies that the early game should support rapid establishment of outposts, power, mining, refining, fabrication, and transport, while the late game requires clean materials, rare resources, advanced processors, high-energy systems, and large logistics networks.

The assistant later summarised this as “basics are easy; scale and precision are hard.”

### 2.10 The user described machines as collapsible process equations

The user wanted players to make machines, vehicles, rockets, and factories. But those machines should not require full part-by-part simulation everywhere. The function of a whole unit assembly should be summarised as a one-step equation or process graph when possible. A distant factory should not simulate every belt item, pipe molecule, motor, and worker. It should simulate input rates, output rates, power draw, heat, buffers, reliability, and maintenance.

This links directly to the engine architecture: player creativity should be compiled into validated simulation graphs that can be expanded visually when nearby and collapsed into equations when distant.

### 2.11 The first preservation/export package was produced

The user uploaded a detailed preservation prompt asking for a maximum-fidelity chat preservation package. The assistant produced a long human-readable report, structured registers, context transfer packet, spec sheet, aggregator packet, self-audit, future-chat prompt, reader guide, and ZIP handoff package.

Those files are now included in the workspace and have been included in the new complete bundle. The earlier package’s main label was `Dominium_Deterministic_Solar_System_Architecture`, and there is also an earlier/alternate set labelled `Dominium_Robotic_Seed_Civilisation_Architecture`. The current bundle preserves both sets rather than discarding one.

### 2.12 This companion report and bundle were requested

The user then asked for an accompanying human-readable detailed summary/report of the entire conversation, including everything discussed, decided, deferred, and anything else that may have been missed, and asked for everything to be bundled into a single ZIP with all files. This report and the updated bundle respond to that request.

## 3. Main conclusions and their status

### 3.1 Dominium should be simulation-first, renderer-second

**Status:** INFERENCE / assistant recommendation, not yet a user-confirmed final decision.

The architecture that best matches the requested scale is a deterministic simulation/data core. The world should be represented by seeds, fields, graphs, ledgers, sparse deltas, and event logs. Unreal or another renderer should request the local visible/sensed subset and render it. This avoids treating a solar system as one giant live map.

This matters because the requested game includes full planets, construction, machines, fog of war, and MMO persistence. A normal scene graph cannot be the source of truth for that.

### 3.2 The world generator should be science-bounded but designer-steerable

**Status:** FACT from user direction.

The user wants planets generated from physically meaningful parameters rather than arbitrary sliders or manual painting. However, the user also wants the ability to nudge results and possibly reverse-solve from a desired planet. This creates a useful design principle: the editor should expose realism-bounded controls, plausibility scoring, and override layers.

### 3.3 Field overlays should unify worldgen, saves, packs, terraforming, construction, and destruction

**Status:** FACT + INFERENCE.

The user explicitly wanted procedural fields overlaid with painted/designer fields and wanted the same save-file technology to support planet packs and terraforming. The assistant formalised this as a field-layer stack. This should probably become a core engine requirement because it connects tools, save systems, and gameplay.

### 3.4 The game identity is robotic seed civilisation

**Status:** FACT from user direction.

The premise is not generic survival crafting. The player is a robot manufactured by a human seed ship. The civilisation is built by robots, machines, and automation. This is the central creative identity of the chat.

### 3.5 Physical spawn machines are part of the economy

**Status:** FACT from user direction.

New players or respawned bodies should emerge from actual machines. Remote spawn points should be built from resources and power. This gives exploration and infrastructure expansion a clear milestone.

### 3.6 Nanobot construction should be convenient but bounded

**Status:** FACT for nanobot/blueprint construction; INFERENCE for exact constraints.

The user proposed nanobots/invisible construction force for computational and diegetic reasons. The assistant added constraints: material, energy, time, heat, permission, capability, and sensor coverage. This constraint package should be preserved because it prevents nanobots from erasing the game.

### 3.7 Worker NPC labour should not be the core simulation model

**Status:** FACT / strong user preference.

The user explicitly moved away from worker NPC labour due to compute cost. This is one of the clearest design decisions. Future chats should not keep proposing colonist-worker simulation as the default solution.

### 3.8 Machines and factories should compile into process graphs

**Status:** FACT from user direction; exact implementation unresolved.

The user wants player-created machines, vehicles, rockets, and factories, but wants them to collapse into equations or simple functional objects when not actively observed. The future work is to define a machine graph compiler that validates assemblies and derives power, throughput, mass, heat, reliability, and outputs.

### 3.9 Fog of war must be a data/security system, not only a visual effect

**Status:** FACT for fog of war; INFERENCE for security architecture.

The user required fog of war and sensed-only simulation. The assistant argued that in MMO mode hidden state must not be sent to the client. This affects client-shared compute. Clients can help with safe visible work, but not with hidden enemy bases, undiscovered resources, or authoritative economy/combat results.

### 3.10 Unreal is useful but should not be assumed to solve the whole game

**Status:** INFERENCE / assistant recommendation; requires verification.

Unreal can help with visuals, streaming, local gameplay, and tooling. It should not be assumed to provide deterministic planetary-scale MMO authority. This must be checked against current Unreal capabilities before becoming binding.

## 4. What was decided versus what remains tentative

### Strongest user-stated decisions or directions

1. **Procedural star/planet generation should be science-bounded.** Designers should set meaningful parameters and nudge results, not manually paint everything by default.
2. **Field overlays are needed.** Procedural generation should combine with painted/designer/player layers.
3. **The setting involves a robotic mothership.** Humans sent a ship that manufactures robots to rebuild civilisation.
4. **Players are robots.** Robot chassis/body choice is part of spawning and gameplay.
5. **Spawn points are physical machines.** Expansion requires building new labs/fabricators.
6. **The mothership provides knowledge/recipes.** Players do not need to reinvent industrial standards.
7. **The mothership must be limited.** Its resources and throughput should not trivialise local industry.
8. **Nanobot/blueprint construction is desirable.** It is diegetic and computationally efficient.
9. **Worker NPC labour should be avoided or deprioritised.** Automation should be used from the beginning.
10. **Machines/factories should collapse into process equations.** The engine should not simulate every part everywhere.

### Strong assistant recommendations not yet final user decisions

1. Domino should be the deterministic authoritative simulation core.
2. Unreal should be a renderer/client/tooling layer rather than the source of truth.
3. The world should use event sourcing, snapshots, state hashes, sparse deltas, and fixed ticks.
4. Public MMO clients should not be trusted with hidden state or authority-critical simulation.
5. The first milestone should be a mothership-to-remote-spawn-lab vertical slice.
6. Nanobot actions should be staged through preview, plan, reserve, stage, execute, commit, and operate.
7. Player machines should be validated by a machine graph compiler.

These recommendations are coherent with the user’s goals, but they should be explicitly confirmed before being promoted to formal project requirements.

## 5. What was put off for later

Many topics were intentionally left open because this conversation was about architecture and identity, not final implementation. The deferred items include:

- exact launch scope: one designed star system, many systems, or galaxy-like multi-system generation;
- exact level of realism in planet generation;
- exact data schema for planet fields and terrain deltas;
- exact resource, energy, heat, and wear constraints on the mothership;
- robot chassis list and balancing;
- death, respawn, backup, and body-transfer rules;
- exact nanobot capability tiers;
- construction permissions, claims, and anti-griefing;
- exact machine graph compiler design;
- exact city progression and how cities feel alive without NPC workers;
- wildlife/mobs and local active agents;
- fog-of-war sensor model;
- client-shared compute rules;
- official MMO region/shard/server authority model;
- private server and modding rules;
- current Unreal feasibility verification;
- external data/source licensing for real solar system information;
- detailed vertical-slice task plan.

The most important deferred technical work is the data model: deterministic state, field layers, sparse deltas, construction ledgers, machine graphs, and simulation LOD. The most important deferred design work is the first playable loop.

## 6. What artifacts now exist

The workspace contained two generated preservation-package sets plus the uploaded prompt. This complete bundle preserves all of them.

| File | Size | SHA-256 prefix |
|---|---:|---|
| `Dominium_Deterministic_Solar_System_Architecture__00_manifest.md` | 2,389 | `d8e9ad908bbef8e5…` |
| `Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` | 57,540 | `320d5e21af78e139…` |
| `Dominium_Deterministic_Solar_System_Architecture__02_context_transfer_packet.md` | 4,303 | `a07ff9d193d55bc2…` |
| `Dominium_Deterministic_Solar_System_Architecture__03_spec_sheet.yaml` | 58,575 | `0dcbbc5509d71342…` |
| `Dominium_Deterministic_Solar_System_Architecture__04_registers.md` | 40,599 | `3c7af3db6949e29e…` |
| `Dominium_Deterministic_Solar_System_Architecture__05_aggregator_packet.md` | 27,431 | `9674464e0379b64f…` |
| `Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md` | 3,264 | `56d50d85c678d79c…` |
| `Dominium_Deterministic_Solar_System_Architecture__07_verification_and_audit.md` | 4,723 | `6a7e79ed0adad485…` |
| `Dominium_Deterministic_Solar_System_Architecture__08_future_chat_bootstrap_prompt.md` | 978 | `984d223840f548c1…` |
| `Dominium_Deterministic_Solar_System_Architecture__09_in_chat_reader.md` | 2,199 | `6cd8b657a8b1b9cf…` |
| `Dominium_Deterministic_Solar_System_Architecture__handoff_package.zip` | 63,147 | `469bfb68b19198d9…` |
| `Dominium_Robotic_Seed_Civilisation_Architecture__00_manifest.md` | 2,627 | `320c1fb070acf1ed…` |
| `Dominium_Robotic_Seed_Civilisation_Architecture__01_human_readable_report.md` | 33,167 | `0b1e56f0d8e57246…` |
| `Dominium_Robotic_Seed_Civilisation_Architecture__02_context_transfer_packet.md` | 5,362 | `2212c0a5be7f1ecf…` |
| `Dominium_Robotic_Seed_Civilisation_Architecture__03_spec_sheet.yaml` | 53,240 | `3b0368853afb7ef7…` |
| `Dominium_Robotic_Seed_Civilisation_Architecture__04_registers.md` | 37,669 | `d02a062de85e840f…` |
| `Dominium_Robotic_Seed_Civilisation_Architecture__05_aggregator_packet.md` | 25,376 | `056eb47ecc86358d…` |
| `Dominium_Robotic_Seed_Civilisation_Architecture__06_reader_brief.md` | 3,058 | `95b5d819810c1aaa…` |
| `Dominium_Robotic_Seed_Civilisation_Architecture__07_verification_and_audit.md` | 5,158 | `046540e67e94aea1…` |
| `Dominium_Robotic_Seed_Civilisation_Architecture__08_future_chat_bootstrap_prompt.md` | 980 | `4a95d64912ca6a74…` |
| `Dominium_Robotic_Seed_Civilisation_Architecture__09_in_chat_reader.md` | 2,406 | `f52c2ca140b41e32…` |
| `Dominium_Robotic_Seed_Civilisation_Architecture__handoff_package.zip` | 54,889 | `972af06794dd4713…` |
| `Pasted text.txt` | 31,225 | `6686114753accfa0…` |

The new companion files created by this step are:

- `Dominium_Deterministic_Solar_System_Architecture__10_accompanying_full_conversation_report.md` — this detailed readable report.
- `Dominium_Deterministic_Solar_System_Architecture__11_complete_bundle_manifest.md` — the updated complete bundle manifest.
- `Dominium_Deterministic_Solar_System_Architecture__12_bundle_verification.md` — verification notes and package checks.
- `Dominium_Deterministic_Solar_System_Architecture__complete_conversation_bundle.zip` — the final single ZIP package containing the relevant files.

## 7. What future assistants must not get wrong

Future assistants should not flatten the conversation into “make a big procedural MMO in Unreal.” That loses the point. The actual design is more specific:

- Dominium is a **robotic seed-civilisation game**.
- The requested scale requires a **deterministic sparse simulation/data architecture**.
- The user specifically moved away from **worker NPC labour** because of compute cost.
- The mothership provides **knowledge and precision**, not infinite free industry.
- Nanobots are an **interface for construction**, not a source of free matter or energy.
- Player machines and factories should **compile into process graphs**.
- Fog of war must control **what clients can know**, not just what the screen darkens.
- Unreal may help with the visible client, but it should not be assumed to solve deterministic planetary MMO simulation.

## 8. Recommended next action sequence

The best next action is to turn the proposed first vertical slice into a formal milestone. That milestone should prove the core loop before any broader MMO or solar-system claims.

Recommended order:

1. **Write the design pillars.** Capture the non-negotiables: robotic seed civilisation, deterministic sparse simulation, science-bounded generation, field/delta planets, automation over worker NPCs, physical spawn economy, and machine graph abstraction.
2. **Define the first playable loop.** Mothership spawn → survey → mine → refine → fabricate → build remote spawn lab → spawn/swap body at new lab.
3. **Specify the deterministic core data model.** Ticks, commands, IDs, state hashes, event logs, snapshots, sparse deltas.
4. **Specify the field-layer system.** Procedural base, real-data layer, designer override, planet pack, gameplay terraforming, construction, damage, temporary preview.
5. **Specify mothership constraints.** Feedstock, throughput, heat, wear, mission reserves, size limits, and recovery modes.
6. **Specify robot chassis.** Launch with a small set: biped, quadruped/spider, tracked/heavy industrial, scout drone or similar.
7. **Specify construction.** Blueprint preview, resource reservation, staging, nanobot execution, deterministic commit.
8. **Specify machine graph compiler.** Inputs, outputs, power, heat, mass, throughput, reliability, maintenance debt, complexity budget.
9. **Specify fog of war and sensors.** Observed, remembered, inferred, unknown, and secret states.
10. **Verify Unreal and external-data claims.** Only after the core model is clear.

## 9. Verification and checks performed for this bundle

During this bundling step, the workspace was checked for relevant files. The existing generated files were found and included. The uploaded preservation prompt was also included as a source artifact. The new companion report, manifest, verification file, and final ZIP were created in `/mnt/data`.

The ZIP was then opened and tested with Python’s `zipfile` module. The test did not report corrupt members. A member list and file counts are included in the verification file.

## 10. Final compact summary

This entire conversation established Dominium as a robotic seed-civilisation game and Domino as the likely deterministic simulation/data foundation that would make that game possible. The user started with a very large technical ambition: full-scale procedural planets and solar systems, terraformable construction, machines, factories, megaprojects, fog of war, sparse simulation, client-shared compute, single-player universes, and MMO persistence. The assistant responded by recommending a deterministic, sparse, data-first architecture rather than a giant Unreal world.

The user then gave the project its clearer identity. Humans sent a robotic mothership to another solar system. It lands on a habitable planet and manufactures robot bodies. Players spawn as robots from physical machines, choose chassis types, and expand by building remote spawn labs. The ship contains recipes and inherited human knowledge, so players do not need to invent CPUs or rail gauges. But the ship cannot fabricate civilisation at infinite scale because its resources, energy, heat, throughput, and wear are constrained.

The user also clarified the worldgen philosophy. Planets should be generated from realistic-bounded scientific parameters, not arbitrary sliders or manual painting. Designers should be able to nudge results or reverse-solve desired planets, and procedural fields should be overlayable with painted/designer/player layers. The same field/delta technology should support worldgen, saves, planet packs, terraforming, cut/fill, construction, and destruction.

The most important gameplay pivot was away from worker NPCs. The user recognised that labour simulation would create expensive pathfinding and agent problems. Since the civilisation is robotic, the game can use automation from the start: nanobots, construction swarms, AI controllers, drones, machine graphs, process diagrams, and infrastructure systems. Machines and factories should be visually rich when local but collapse into equations when distant.

The most important unresolved work is formalising the first vertical slice and the foundational data formats. The next useful spec should define the mothership-to-remote-spawn-lab loop, deterministic data model, field/delta system, construction/nanobot pipeline, machine graph compiler, and fog-of-war sensor model. Once that is clear, engine integration and Unreal feasibility can be verified.
