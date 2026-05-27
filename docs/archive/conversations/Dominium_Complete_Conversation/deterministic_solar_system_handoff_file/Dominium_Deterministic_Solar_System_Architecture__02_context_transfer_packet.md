## 29. Context Transfer Packet for a Future Chat

### 29.1 Ultra-Condensed Bootstrap Brief

This chat concerns **Dominium**, a proposed deterministic robotic seed-civilisation game built with or around the **Domino engine**. The user first asked how to build a deterministic, full-scale procedural solar-system game with editable planets, terraforming, cut/fill construction, megaprojects, machines, factories, fog of war, sparse simulation, client-shared compute, single-player universes, and MMO persistent universes. The assistant recommended a custom deterministic simulation/data core separate from rendering, with Unreal only as a possible client/visual/tooling layer.

The user then refined the game premise. Dominium should generate star systems and planets from realistic-bounded scientific parameters, with designer nudging and overlays rather than manual painting as the main workflow. The same field/delta technology should support world generation, saves, packs, painted overrides, and in-game terraforming. The lore premise is a robotic mothership launched by humans to another solar system. It lands on the most habitable planet, manufactures robot bodies, and tries to restart civilisation. Players spawn as robots from physical fabrication machines and can later build remote spawn labs if they gather the materials and power.

The strongest design direction is automation-first. The user explicitly moved away from worker NPC labour because pathfinding and person-like simulation are expensive. Since the civilisation is robotic, construction can be performed by nanobots, AI agents, machine controllers, and process graphs. The mothership explains HUDs, blueprints, recipes, quest-like guidance, and advanced knowledge, but finite resources and low throughput force players to build mines, refineries, factories, cities, and industrial chains. Machines and factories should be visually rich when local but compile into aggregate equations when distant.

Treat user-stated ideas as FACT where clearly stated, assistant architecture as INFERENCE unless later accepted, and external engine/data claims as UNCERTAIN / UNVERIFIED until checked. The best immediate next action is to formalise the first vertical slice: one planet region, mothership, robot body, survey, ore, power, cut/fill, blueprinting, nanobot construction, mine, refinery, fabricator, remote spawn lab, and fog-of-war sensor model.

### 29.2 Source Hierarchy

1. Direct user statements in this chat.
2. Explicit decisions accepted by the user.
3. Current task register.
4. Constraint register.
5. Artifact ledger.
6. Inferences from the visible conversation.
7. Assistant suggestions not accepted by the user.
8. General model knowledge.

### 29.3 Operating Rules for Future Assistants

- Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels.
- Do not re-ask answered questions.
- Ask clarifying questions only when materially necessary.
- Verify stale facts before relying on them.
- Do not invent missing details.
- Do not treat tentative items as final.
- Do not repeat rejected options such as default worker NPC labour or dense planet simulation.
- Preserve artifacts and generated files.
- Use structured outputs when continuing.

### 29.4 Active Workstreams

Active workstreams are WORKSTREAM-01 through WORKSTREAM-13. Highest priority: deterministic core, science-bounded world generation, field/delta model, mothership economy, nanobot construction, machine graph compiler, fog of war, MMO trust boundaries, and vertical slice.

### 29.5 Current Priorities

1. Define design pillars.
2. Approve/refine the first vertical slice.
3. Specify deterministic core and field/delta model.
4. Specify mothership/spawn economy.
5. Specify construction and machine graph systems.
6. Verify Unreal/current engine assumptions.

### 29.6 Current Open Questions

Main unresolved issues: official scope, planet realism bounds, field format, mothership reserves, robot chassis, nanobot limits, machine compiler, city liveliness without NPCs, fog-of-war data rules, client compute boundaries, Unreal role, and first vertical slice.

### 29.7 Recommended First Action

Turn the proposed vertical slice into a formal milestone document with goals, non-goals, required systems, data structures, success tests, and risks.
