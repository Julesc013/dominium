# 29. Context Transfer Packet for a Future Chat — Dominium Robotic Seed-Civilisation Architecture

## 29.1 Ultra-Condensed Bootstrap Brief

This prior chat developed Dominium from an enormous technical ambition into a coherent candidate game premise: a deterministic robotic seed-civilisation game. The user first asked how Domino/Dominium could support full-scale solar-system and planet generation, procedural data, terraforming, cut/fill, megaprojects, machines, factories, fog of war, sparse simulation, MMO persistence, single-player multi-universe play, client-shared compute, and Unreal integration. The assistant recommended a deterministic simulation/database core with sparse data and renderer clients, not a normal scene-graph/actor-world architecture.

The user then supplied the key design material. The official game likely starts with a generated/designed star or solar system, not a whole galaxy. Planets should be generated from realistic science-bounded parameters, not arbitrary sliders or manual painting. The editor should support both forward generation from orbital/planet parameters and reverse generation where a desired planet outcome is fitted to plausible parameters. Procedural fields should be overlayable with painted fields, data overrides, save deltas, packs, and terraforming layers.

The central lore/gameplay premise is that humans launched a robotic mothership to a new system. It lands on a habitable planet and fabricates robot bodies using nanotechnology to rebuild civilisation. Players spawn from physical machines as robot chassis such as biped, quadruped, spider, or tank-like forms. The mothership contains human knowledge, explaining recipe availability, but has limited resources, throughput, heat capacity, and fabrication scale, forcing players to mine, refine, build industry, replenish the ship, and create remote spawn labs.

The user strongly deprioritised worker NPC labour because it would require pathfinding and expensive simulation. The preferred model is automation from the start: AI planners, computers, nanobots, process graphs, and machine/factory controllers. Machines and vehicles may be visually designed by players, but authoritative simulation should compile them into functional summaries: inputs, outputs, tick rates, energy, heat, throughput, and constraints. Nanobots and robot HUDs provide diegetic blueprinting, cut/fill, and construction. The best immediate next step is to write a first playable slice spec proving: spawn from mothership, survey, mine, cut/fill, build power, refine, fabricate, construct remote spawn lab, and respawn/swap body there.

## 29.2 Source Hierarchy

1. Direct user statements in this chat.
2. Explicit decisions accepted by the user.
3. Current task register.
4. Constraint register.
5. Artifact ledger.
6. Inferences.
7. Assistant suggestions not accepted by the user.
8. General model knowledge.

## 29.3 Operating Rules for Future Assistants

- Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels.
- Do not treat every brainstorm as final.
- Do not treat assistant recommendations as accepted user decisions unless the user confirms.
- Do not re-ask answered questions.
- Ask clarifying questions only when materially necessary.
- Verify stale/current facts before relying on them, especially Unreal, NASA/JPL data, MMO scale, and software features.
- Do not invent missing mechanics, quantities, or lore decisions.
- Do not repeat rejected options as if they are new, especially worker NPC labour and unlimited mothership fabrication.
- Preserve artifacts and cite uncertainty when merging into a spec book.
- Use structured outputs when continuing.

## 29.4 Active Workstreams

- WORKSTREAM-01: Deterministic Domino simulation architecture.
- WORKSTREAM-02: Science-bounded procedural star-system/planet generation.
- WORKSTREAM-03: Field-layer planet data, saves, packs, and terraforming.
- WORKSTREAM-04: Robotic seedship lore, recipe book, and spawn economy.
- WORKSTREAM-05: Nanobot construction, blueprinting, cut/fill, and inventory.
- WORKSTREAM-06: Automation, machines, factories, and process graphs.
- WORKSTREAM-07: Fog of war, sensors, and information security.
- WORKSTREAM-08: Single-player, private servers, official MMO, and distributed authority.
- WORKSTREAM-09: Unreal and renderer/client role.
- WORKSTREAM-10: Vertical slice and spec-book preparation.

## 29.5 Current Priorities

1. First playable slice spec.
2. Generator/editor parameter model.
3. Field-layer schema.
4. Mothership/spawn economy.
5. Nanobot construction rules.
6. Machine compiler/process graph model.
7. Unreal/current-tech verification.

## 29.6 Current Open Questions

The main unresolved questions are the exact physical bounds for generation, reverse-generation algorithm, field schema, mothership reserves, chassis stats, nanobot limits, machine compiler rules, city liveliness without NPCs, MMO mode architecture, fog-of-war security, Unreal integration, and first-slice acceptance criteria.

## 29.7 Recommended First Action

Create a **Dominium First Playable Slice Spec** with acceptance criteria for: mothership spawn, robot chassis selection, survey, ore discovery, blueprinting, cut/fill, power generation, refining, fabrication, transport/logistics, construction of a remote spawn lab, and spawning or swapping into a new body there.
