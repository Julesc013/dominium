# COMPLETE CHAT PRESERVATION REPORT — Dominium UE6, Domino, and Deterministic Universe Feasibility

## 0. Coverage and Reliability Assessment

| Field | Assessment |
|---|---|
| Chat label | Dominium UE6, Domino, and Deterministic Universe Feasibility |
| Date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | THIS CHAT ONLY, plus clearly labelled PROJECT-CONTEXT where the current project summary is used |
| Apparent access | Partial |
| Previously generated files available? | No prior generated files from this chat were available before this task; this package creates new files |
| Uploaded files or artifacts present? | Yes: `Pasted text.txt`, containing the preservation-package prompt applied here |
| Contains future plans? | Yes |
| Contains decisions? | Yes, but some are assistant recommendations rather than user-confirmed final decisions |
| Contains pending tasks? | Yes |
| Contains unresolved questions? | Yes |
| Staleness risk | Medium to high for UE6/UE5 requirements, engine roadmaps, and external-source claims |
| Extraction confidence | 3/5 |
| Safe for later aggregation? | With caveats |
| Main limitations | The full long-running Dominium project transcript is not visible. Only the current visible turns, the uploaded prompt, and project-context summaries are available. Earlier uploaded files in the broader environment may have expired. External facts cited in the earlier answers were not freshly reverified during this packaging pass. |

### Plain-language limitations

FACT: This package preserves the currently visible chat about whether Dominium should use UE6, UE5, Domino, Unreal, or a custom engine layer for a highly ambitious deterministic solar-system-scale game. It also preserves the current uploaded prompt as an artifact because it defines this preservation task.

UNCERTAIN / UNVERIFIED: This is not a complete reconstruction of every Dominium conversation ever held. The project context shows that many other chats exist about platforms, renderers, setup, game architecture, ecology, ECS, launcher design, and development planning, but their full transcripts are not visible here. Those items are labelled PROJECT-CONTEXT when referenced.

PROJECT-CONTEXT: The broader Dominium doctrine includes a deterministic C89 engine, C++98 product shells, platform/renderer separation, CLI/TUI/native shells, distribution contracts, and cross-renderer architecture. That context strongly informs how the UE/Unreal/Domino discussion should be interpreted, but this report does not claim those details were all explicitly discussed in the visible turns of this chat.

## 1. One-Page Orientation

This chat was mainly about whether Dominium could or should be built on Unreal Engine 6, Unreal Engine 5, Domino, or some custom architecture that uses a commercial engine only as a frontend. The user began by pasting a confident external-style answer claiming that UE6 had been unveiled, that UE6 would raise baseline OS requirements, and that high-performance UE6 games would probably require modern Windows, macOS, and Linux targets. The user then asked the key strategic question: could Dominium be made on UE6 instead of Domino, and could it be made portable to Domino later?

The first answer established the central architectural position of this chat: Dominium should not wait for UE6 or treat UE6 as the whole game platform. The recommended path was to build using current Unreal technology where useful, structure the project for a future UE6 transition, and preserve portability to Domino by keeping the durable game logic outside Unreal-specific systems. The important distinction was between the game itself and the engine used to render or host it. The answer framed DominiumCore as the permanent game, Unreal or UE6 as one possible renderer/runtime, and Domino as a later renderer/runtime. That distinction matters because Dominium’s broader design is not a conventional Unreal game. It is intended to be a long-lived, portable, deterministic, multi-platform, simulation-heavy project.

The user then escalated the technical scope substantially. They asked whether UE5, UE6, or any other engine could handle a deterministic full-scale real solar system with fully recreated procedural planets, player-built civilizations, terraforming, cut-and-fill terrain, megaprojects, machine/device/factory design, fog of war, sparse simulation, collapsed unobserved regions, single-player multi-universe gameplay, an MMORPG single universe, and client-shared compute where each client simulates its own area or assists other areas when servers cannot keep up. The user also asked whether Unreal could do this without lag, with low latency, at high FPS, and with millions of players in the same universe.

The answer was deliberately blunt: no commercial engine, including UE5 or publicly known UE6, solves this combination out of the box. The decisive conclusion was not that Unreal is useless, but that Unreal should not be the authoritative simulation engine. Unreal can be valuable as the visual client, tooling environment, editor, animation/rendering stack, construction preview layer, and possibly debug frontend. The durable game must be a custom deterministic simulation core, backed by a sparse world database and an authority/server layer. The proposed permanent architecture became `DominiumSim + DominiumWorldDB + DominiumServer`, with `DominiumClient_UE` and a future `DominiumClient_Domino` as adapters.

The conversation mattered because it clarified the difference between a game engine decision and a world-simulation architecture decision. If Dominium is treated as “an Unreal game,” it risks becoming locked into non-deterministic actor ticking, Unreal physics, Unreal replication, `.uasset` content, and engine-specific assumptions. If Dominium is treated as a portable deterministic simulation with Unreal as one client, it remains theoretically movable to Domino or another runtime later. The result is more difficult up front, but it preserves the design ambition.

The main outcome was a practical doctrine: use commercial engines for what they are good at, but do not delegate the canonical universe state to them. Determinism, resource accounting, fog-of-war authority, sparse planet edits, region handoff, client/server trust boundaries, simulation LOD, and persistence must be designed as first-class Dominium systems. The chat also produced a high-level phased roadmap: first build a deterministic headless simulation, then sparse planet chunks, then collapse/refine mechanics, then server authority and fog of war, then region authority, then MMO-scale load testing.

For a future assistant or human reader, the key thing to understand is that the chat did not reject Unreal. It rejected the idea that Unreal or UE6 could be the complete solution. The direction is hybrid: custom simulation and backend as the real engine, Unreal as the first high-quality client, UE6 as a possible future upgrade, and Domino as a possible later frontend/runtime if the core remains portable.

## 2. The Story of the Conversation

The visible conversation began after the user had obtained or drafted a confident answer about UE6 platform requirements. That pasted answer treated UE6 as a coming bleeding-edge technology with raised OS and hardware expectations and implied that modern Windows 10/11, macOS Sequoia or newer, and modern Linux distributions would be the practical targets. The user’s real question was not merely about OS compatibility. It was about whether the Dominium project could pivot from Domino to UE6, and whether that would still leave a path back to Domino later.

The first response corrected the framing. It said that public UE6 information is still too thin to treat UE6 as an available production base. It recommended a UE5-first path: build with a stable UE5 release now, structure the project so that a later UE6 migration is plausible, and maintain Domino portability by isolating engine-independent game systems. The important early architecture was a separation between `Core`, `UnrealAdapter`, `DominoAdapter`, source assets, Unreal-specific assets, and tools.

That response also introduced a rule that shaped the rest of the chat: Unreal should render and host Dominium, but Unreal should not define Dominium. That was the first major conceptual decision point. It reframed Dominium not as an engine project in the narrow sense, but as a portable game/simulation system with replaceable frontends.

The user then asked a far more ambitious question. They described a game with a deterministic real-scale solar system, data-driven procedural planets, player-built civilizations, terraforming, cut/fill terrain, megaprojects, player-designed machines and factories, fog of war, sparse simulation, collapsed unobserved state, MMORPG single-universe scale, single-player multi-universe options, and client-shared computation. They also asked if Unreal could do all of this without lag, with low latency and high FPS, for millions of players in the same universe.

The second response answered that no existing commercial engine can solve that full combination out of the box. It separated solvable requirements from impossible or tradeoff-bound requirements. Solar-system scale is possible with hierarchical coordinate systems. Procedural planets are possible with seeds, real data, and sparse deltas. Deterministic rules are possible with a fixed-step custom simulation. Terraforming is possible with sparse voxel, signed-distance-field, or hybrid terrain storage. Player-built factories are possible if treated as graph simulations rather than huge piles of individual physics actors. Fog of war is possible if the server never sends hidden state. A single shared universe is possible if it means one persistent world split into regions and authority domains. Millions of players in the same local mutually interacting space at low latency is not realistically possible.

The answer then proposed the architecture that became the main deliverable of the chat: `DominiumSim`, `DominiumWorldDB`, `DominiumServer`, `DominiumClient_UE`, and `DominiumClient_Domino`. This architecture makes the core simulation, world storage, and server authority independent from the renderer. Unreal becomes an adapter, not the source of truth. Domino becomes a future adapter if the project requires it.

The discussion then walked through major hard problems: determinism, coordinate scale, procedural planets, terraforming, factories, collapsed simulation, fog of war, client-shared compute, and MMO authority. It introduced the idea that the project must distinguish between what exists, what is simulated, what is rendered, what is knowable, and what is authoritative. That distinction is one of the most important concepts in the chat because it prevents the project from trying to run a full-fidelity universe everywhere all at once.

Finally, the user uploaded a preservation-package prompt asking for this chat to be turned into a human-readable report, registers, spec-prep packet, aggregator packet, audit, and downloadable files. This output is the resulting preservation package. The final state of the chat is therefore not a final engine selection, but a clearly stated architecture strategy: do not rely on UE6 as the game; build a portable deterministic core, use Unreal where it is useful, and preserve the option to port to Domino later.

## 3. Main Topics Discussed

### Topic 1 — UE6, UE5, and Domino as strategic options

The first topic was whether Dominium should be made on UE6 instead of Domino. The answer separated availability from suitability. UE6 was treated as not yet available enough for production planning. UE5 was treated as a practical near-term renderer/tooling base. Domino was treated as a possible future runtime or custom engine path, not something that can be reached by automatically exporting an Unreal project.

Conclusion: use Unreal/UE5 as a practical client layer if useful, do not wait for UE6, and do not make Unreal-specific systems the canonical game.

Uncertainty: public UE6 technical capabilities and requirements remain time-sensitive and need verification before any future hard commitment.

### Topic 2 — Engine-independent Dominium core

The chat repeatedly returned to the need for an engine-independent core. This means rules, simulation, save/load, economy, fog of war, machine graphs, resource accounting, and deterministic replay should live outside Unreal `UObject`, `AActor`, Blueprint, Chaos physics, or Unreal replication assumptions.

Conclusion: Dominium’s durable product should be its simulation and world model. Unreal and Domino should be adapters.

### Topic 3 — Deterministic full-scale simulation

The user’s vision requires deterministic behavior across machines, platforms, and possibly long-running worlds. The answer explained that Unreal’s ordinary gameplay stack is not appropriate as a canonical deterministic simulation because of floating-point behavior, engine ticking, physics, and network replication. A custom fixed-step simulation with fixed-point or integer math, deterministic RNG, stable ordering, replay logs, and state hashes is needed.

Conclusion: strict determinism is possible only if treated as a core architecture requirement from the beginning.

### Topic 4 — Solar-system and planet scale

The user wanted real solar-system scale and fully recreated planets. The answer distinguished rendering scale from simulation scale. Unreal Large World Coordinates may help render large environments, but a real solar system should not be treated as a single flat Unreal coordinate space. The correct model is hierarchical: solar-system coordinates, orbit coordinates, planet surface coordinates, region coordinates, chunk coordinates, and local render coordinates.

Conclusion: solar-system scale is possible, but only through coordinate hierarchy and local render bubbles.

### Topic 5 — Procedural planets, terrain edits, and megaprojects

The user described planets generated procedurally from data, with player terraforming, cut/fill, construction, and megaprojects. The answer argued that base terrain should be procedural and immutable by default, while player changes are sparse deltas or operation logs. Terrain should likely use sparse voxels, SDF chunks, heightfield-plus-edit layers, or a hybrid model.

Conclusion: arbitrary terrain modification is feasible only if sparse, chunked, versioned, and separate from the renderer’s terrain representation.

### Topic 6 — Factories, machines, and designed devices

The game vision includes factories and player-designed devices. The response warned that simulating every physical object everywhere is infeasible. Factories should be graphs: machines as nodes, belts/pipes/cables/routes as edges, and deterministic transfer rules. Distant or unseen factories should collapse into macrostate rates and inventories while preserving accounting.

Conclusion: machine gameplay must be designed as a scalable graph simulation, not as unrestricted physics.

### Topic 7 — Fog of war, secrets, and knowability

Fog of war means clients must not receive hidden state. This conflicts with naive client-shared compute. The answer distinguished safe client work from unsafe authority. Clients can generate meshes, predict local motion, preview builds, suggest paths, and simulate non-authoritative UI states. They should not authoritatively decide hidden resources, enemy bases, persistent production, combat results, or market-relevant outcomes.

Conclusion: server-side sensory authority is mandatory for an MMO with fog of war.

### Topic 8 — Single-universe MMO and millions of players

The user asked about millions of players in the same universe. The answer distinguished a single persistent universe from a single local mutually interacting space. A single universe can exist through region authority, sharded or meshed simulation, shared databases, global economy/social systems, and interest management. Millions of players in one local space at low latency and high FPS is not a realistic target.

Conclusion: design for one universe identity, not one physics room containing everyone.

### Topic 9 — Client-shared compute

The user asked whether every client can share compute load. The answer said this is only safe in limited forms. The core pattern must be client proposes, server verifies, server commits. Full client authority would break the economy, fog of war, and anti-cheat model.

Conclusion: client compute can assist rendering, prediction, meshing, path proposals, and single-player/private worlds, but not persistent MMO authority.

### Topic 10 — Engines and systems to study

The response named several references: Unreal for rendering/tooling, UNIGINE for geospatial precision and planet-scale simulation, Factorio for deterministic factory simulation and desync discipline, EVE Online for single-shard/social scale and time dilation, Unity DOTS/Bevy for data-oriented ECS design, Cesium/3D Tiles for geospatial streaming, and SpaceEngine/Outerra-like systems for astronomical/procedural planet-scale ideas.

Conclusion: copy architecture ideas, not entire engines.

## 4. What We Were Trying to Achieve

### 4.1 Explicit Goals

The user explicitly wanted to know whether Dominium could be built on UE6 instead of Domino and whether it could later be ported to Domino. Later, the user explicitly wanted to know whether any engine could handle the full deterministic solar-system/MMO/civilization-building vision with high performance and low latency.

These goals mattered because they affect the deepest architecture of Dominium. If the project starts in an engine-specific way, portability and determinism may become impossible later.

### 4.2 Inferred Goals

INFERENCE: The user is trying to avoid choosing a technology stack that prematurely blocks the full Dominium vision. The user also seems to want an engine strategy that supports both near-term development velocity and long-term architectural control.

INFERENCE: The user wants a high-level but technically honest feasibility assessment, not encouragement that ignores determinism, networking, scale, or persistence constraints.

### 4.3 Goals That Changed Over Time

The conversation moved from a narrower platform question, “Can Dominium use UE6 instead of Domino?”, to a deeper systems question: “What architecture could ever support this game at all?” The engine choice became secondary to the simulation/backend architecture.

### 4.4 Goals Still Unresolved

The chat did not settle whether Unreal should definitely be used as the first client. It recommended Unreal as a plausible first high-quality frontend, but the final choice still depends on prototype results, licensing, team capacity, platform targets, and how much custom simulation work is required.

The chat also did not resolve Domino’s exact role because Domino’s current technical state and intended capabilities were not fully specified in the visible transcript.

## 5. Decisions Made and Why

| ID | Decision | Status | Why it mattered | Confidence | Label |
|---|---|---|---|---|---|
| DECISION-01 | Do not treat UE6 as the current production base | Assistant recommendation; not explicitly user-final | UE6 public details are insufficient for direct production planning | 4/5 | INFERENCE / UNVERIFIED external facts |
| DECISION-02 | Use UE5/Unreal only as a client/tooling layer if used | Assistant recommendation | Prevents Unreal from defining the canonical universe | 4/5 | INFERENCE |
| DECISION-03 | Keep DominiumCore engine-independent | Assistant recommendation strongly supported by user goals | Preserves UE6/Domino portability | 5/5 | INFERENCE |
| DECISION-04 | Build a custom deterministic simulation core | Assistant recommendation | Required for deterministic factories, world state, and replay | 5/5 | INFERENCE |
| DECISION-05 | Do not trust clients with MMO authority | Assistant recommendation | Prevents cheating, fog-of-war leaks, and economy corruption | 5/5 | INFERENCE |
| DECISION-06 | Treat “single universe” as shared persistence plus partitioned authority | Assistant recommendation | Makes MMO scale plausible while rejecting impossible local concurrency | 5/5 | INFERENCE |
| DECISION-07 | Preserve Domino as a future adapter, not an automatic Unreal export target | Assistant recommendation | Avoids false portability assumptions | 4/5 | INFERENCE |

### DECISION-01 — Do not treat UE6 as the current production base

The assistant recommended against starting directly on UE6 because public technical access and production documentation were not treated as available in the visible chat. This was not framed as a permanent rejection of UE6. It was a timing decision: do not wait for a future engine to solve current architecture problems.

### DECISION-02 — Use UE5/Unreal only as a client/tooling layer if used

The chat treated Unreal as valuable for rendering, animation, editor workflows, UI, construction preview, and visual streaming. It should not own the canonical simulation. The alternative was an “Unreal is the whole game” approach, which was rejected because it would entangle gameplay with engine-specific non-deterministic systems.

### DECISION-03 — Keep DominiumCore engine-independent

This is the highest-value decision candidate. Core rules, simulation, save format, economy, factory logic, fog-of-war state, and replay/hash systems should be portable. This matters because Domino portability is only plausible if the core does not depend on Unreal object lifecycles and assets.

### DECISION-04 — Build a custom deterministic simulation core

The user’s requirements imply determinism. The assistant recommended a fixed-step deterministic core with fixed-point/integer math, stable iteration order, deterministic random numbers, command logs, and state hashes. This is not optional if deterministic multiplayer, replay, collapsed regions, and auditability are serious requirements.

### DECISION-05 — Do not trust clients with MMO authority

The chat rejected the idea that clients can authoritatively simulate resource production, hidden state, enemy bases, combat, or persistent terrain changes in an MMO. Clients can assist, but the server must verify and commit.

### DECISION-06 — Define single-universe MMO carefully

The chat accepted a practical definition of a single universe: one persistent identity and shared world, partitioned across regions, servers, databases, and interest sets. It rejected the literal idea that millions of players can all share one local mutually interacting space at low latency and high FPS.

### DECISION-07 — Preserve Domino portability through adapters

The chat recommended making Domino a future adapter target. Portability comes from architecture, not from a future conversion button.

## 6. Ideas Considered but Rejected, Superseded, or Deprioritised

- REJECTED-01: Treating Unreal or UE6 as the whole game engine. Rejected because determinism, persistence, server authority, and portability need custom control.
- REJECTED-02: Waiting for UE6 before beginning serious work. Deprioritised because UE6 availability and capabilities remain uncertain.
- REJECTED-03: Trusting clients with persistent MMO simulation. Rejected for anti-cheat, fog-of-war, and economy-integrity reasons.
- REJECTED-04: Supporting millions of players in one local fully interactive space at low latency. Rejected as a networking and computation impossibility under normal internet/consumer-client assumptions.
- REJECTED-05: Simulating full fidelity everywhere at all times. Rejected because it directly contradicts finite compute and storage.
- REJECTED-06: Making `.uasset` or Unreal Blueprints the source of truth for portable game rules. Rejected because they are not engine-portable.
- REJECTED-07: Simulating every machine/device/factory as full physics everywhere. Rejected because player-made factories require graph and LOD simulation.

## 7. Important Reasoning, Rationale, and Tradeoffs

The central tradeoff is between engine convenience and architectural control. Unreal gives rendering, tooling, animation, UI, asset workflows, and a mature editor. But the more Dominium relies on Unreal for gameplay truth, the harder determinism, portability, and Domino migration become.

A second tradeoff is between scale and fidelity. The user wants full-scale planets and civilizations, but a full-fidelity simulation everywhere would be computationally impossible. The chat’s solution is simulation LOD: active areas are detailed, distant areas are summarized, and unobserved details are generated or refined deterministically as needed.

A third tradeoff is between client-shared compute and authority. Allowing clients to compute more can reduce server load, but allowing them to decide persistent outcomes creates cheating and secrecy problems. The safe model is proposal, verification, and commit.

A fourth tradeoff is between single-universe identity and local concurrency. A single persistent universe is plausible. A single local space with millions of fully relevant players is not. Dominium must use spatial partitioning, interest management, time dilation or degradation modes, region caps, and possibly soft instancing for local overload.

## 8. Plans, Future Work, and Next Steps

The recommended roadmap is staged:

1. Build a deterministic headless core with fixed ticks, deterministic RNG, replay logs, and state hashes.
2. Build a sparse planet-region prototype with procedural terrain, chunked edits, material inventory, and save/load.
3. Implement collapse/refine simulation for factories and regions, proving that active and macro simulation preserve resource accounting.
4. Add server authority and fog-of-war filtering so clients receive only knowable state.
5. Implement region authority, handoff, persistence, and load balancing.
6. Run MMO-scale testing with bots before claiming large player counts.
7. Only after these prototypes should the project decide how much should live in Unreal, Domino, or custom runtime layers.

The best immediate next action is to define the first deterministic simulation proof: a headless prototype with a small factory graph, terrain chunk edits, player command logs, and cross-platform hash checks.

## 9. Constraints, Preferences, and Non-Negotiables

### 9.1 Explicit Constraints and Preferences

The user wants direct, source-grounded, audit-ready answers; explicit uncertainty; bounded estimates; and correction when framing is wrong. The preservation prompt explicitly requires human-readable explanation first, structured registers second, uncertainty labels, no invented facts, no hidden chain-of-thought, and downloadable files if tools are available.

### 9.2 Inferred Constraints and Preferences

INFERENCE: The user values long-term architectural optionality more than short-term engine convenience. They also prefer explicit handling of failure modes, stale facts, and future aggregation.

### 9.3 Uncertain or Unestablished Preferences

UNCERTAIN: The final intended role of Domino remains unclear in the visible transcript. It may be a custom engine, target runtime, renderer, or broader platform plan, but the current chat does not fully define it.

## 10. Files, Artifacts, Outputs, and Prompts

- ARTIFACT-01: Pasted UE6 OS/requirements answer from the user. Purpose: triggered the UE6 vs Domino question. Status: preserved as context; external claims require verification.
- ARTIFACT-02: Assistant response recommending UE5-now/UE6-later/Domino-portable architecture. Purpose: first strategic answer.
- ARTIFACT-03: User’s expanded deterministic solar-system/MMO feasibility question. Purpose: defined the true scale of the technical challenge.
- ARTIFACT-04: Assistant response proposing `DominiumSim + DominiumWorldDB + DominiumServer`. Purpose: core architecture answer.
- ARTIFACT-05: Uploaded `Pasted text.txt`. Purpose: maximum-fidelity preservation prompt.
- ARTIFACT-06 to ARTIFACT-15: The files created by this preservation task, listed in the file index.

## 11. Open Questions and Unresolved Issues

- QUESTION-01: Should Unreal definitely be used as the first high-fidelity client, or should an in-house/experimental renderer come first?
- QUESTION-02: What exactly is Domino’s current technical scope and target role?
- QUESTION-03: Which language should the deterministic core use: C, C++, Rust, or a split architecture?
- QUESTION-04: What determinism level is required across platforms: strict lockstep, server-only deterministic, replay deterministic, or audit deterministic?
- QUESTION-05: How much terrain modification is required: heightfield-only, voxel, SDF, or hybrid?
- QUESTION-06: What is the minimum viable prototype scope for factories, machines, and devices?
- QUESTION-07: How will collapsed simulation reconcile with exact resource accounting?
- QUESTION-08: What player count target is meaningful for phase-one MMO testing?
- QUESTION-09: What external engine claims from UE5/UE6 need re-verification before planning?
- QUESTION-10: How will the project prevent player-designed machines from becoming lag weapons?

## 12. Risks, Failure Modes, and What Future Chats Might Get Wrong

Future chats could incorrectly treat this as a decision to use Unreal for the whole game. They could also incorrectly treat UE6 as currently available and documented enough for production. Another risk is treating assistant recommendations as user-final decisions. The safe interpretation is that this chat produced a recommended architecture, not a signed-off implementation plan.

Future assistants might also overstate portability. A UE project cannot simply be exported to Domino. Portability exists only if the simulation core, data schemas, protocol, and source assets remain engine-independent.

A major technical risk is underestimating the backend. For this game, persistence, region authority, event logs, chunk deltas, anti-cheat, fog-of-war filtering, and simulation LOD are not secondary services. They are the game.

## 13. What This Chat Contributes to the Larger Project or Future Spec Book

This chat should feed the following future spec-book areas:

- Engine and runtime strategy
- Renderer/frontend separation
- Deterministic simulation requirements
- Planetary coordinate and terrain architecture
- Sparse world persistence
- MMO authority and trust model
- Simulation LOD / collapse-refine design
- Fog-of-war and secrecy model
- Portability to Domino or future clients
- Prototype roadmap and validation gates

It should not be merged as a final commitment to Unreal. It should be merged as a strong argument for separating the permanent Dominium core from any commercial rendering frontend.

## 14. What I Should Remember

- Dominium should not be architected as “an Unreal game” if determinism and Domino portability matter.
- UE5 or future UE6 can be useful for rendering, tooling, and iteration.
- The durable architecture is `DominiumSim + DominiumWorldDB + DominiumServer`.
- Single universe is plausible as shared persistence plus partitioned authority, not millions of players in one local fully interactive space.
- Client-shared compute is useful only when the server validates or when the work has no persistent competitive value.
- Fog of war means hidden state must never be sent to unauthorized clients.
- Procedural planets should be seeds plus sparse deltas, not fully stored static worlds.
- Factories should be graph simulations with LOD, not physics actors everywhere.
- The next serious task is a deterministic headless proof, not an engine beauty prototype.

## 15. Best Questions I Can Ask Next in This Chat

### 15.1 Understanding the Chat

- “Explain again why Unreal should be a client rather than the canonical Dominium engine.”
- “What is the smallest architecture that preserves UE, UE6, and Domino options?”

### 15.2 Decisions

- “Which recommendations in this chat should become actual project decisions?”
- “Which decisions still require my explicit confirmation?”

### 15.3 Tasks and Next Actions

- “Define the first deterministic DominiumSim prototype in detail.”
- “Write a milestone plan for proving sparse terrain edits and collapsed factories.”

### 15.4 Artifacts and Files

- “Turn the architecture answer into a formal engine strategy document.”
- “Extract a clean requirements list from the MMO feasibility answer.”

### 15.5 Risks and Verification

- “List all claims about UE5/UE6 that need current-source verification.”
- “What are the top ten ways this architecture could fail?”

### 15.6 Future Spec Book / Aggregation

- “Convert this chat into a spec-book chapter on engine/runtime strategy.”
- “Merge this with the Dominium platform/renderer doctrine from other chats.”

### 15.7 Deep-Dive Questions Specific to This Chat

- “Design the collapse/refine algorithm for factories.”
- “Design the fog-of-war authority model for a single-universe MMO.”
- “Define the coordinate hierarchy for a real-scale solar system.”

## 16. Compact Human Summary

This chat clarified that Dominium’s engine choice cannot be answered by simply choosing UE6, UE5, Domino, Unity, or any other commercial engine. The user’s requirements are far beyond a normal engine decision: deterministic simulation, full-scale solar-system structure, procedural/data-driven planets, player-built civilizations, terraforming, cut/fill terrain, megaprojects, machine and factory design, fog of war, collapsed unobserved regions, single-player multi-universe possibilities, and MMO-scale single-universe ambitions.

The first question asked whether Dominium could be made on UE6 instead of Domino and later ported to Domino. The answer was that UE6 should not be treated as a current production base because public information and tooling are too uncertain. UE5 or Unreal may be useful now, but only if Dominium’s core remains independent. The recommended model was `DominiumCore` as the permanent game, with Unreal/UE6 and Domino as adapters or frontends.

The second question pushed much deeper: can Unreal, UE6, or any other engine actually support the dream game? The answer was no, not out of the box. No commercial engine gives strict determinism, massive sparse world persistence, real-scale planetary systems, arbitrary construction/destruction, fog-of-war secrecy, distributed compute, and millions of players in one universe at high FPS and low latency. Some requirements are solvable, but only with a custom architecture and hard tradeoffs.

The most important architectural output was the proposed split: `DominiumSim` for deterministic rules and simulation, `DominiumWorldDB` for sparse planets, terrain edits, events, and persistence, `DominiumServer` for authority, interest management, fog of war, and region handoff, and then separate clients such as `DominiumClient_UE` and `DominiumClient_Domino`. This makes Unreal a renderer/editor/client rather than the source of truth.

The chat also established key constraints. Clients cannot be trusted with persistent MMO authority because they can cheat, leak hidden state, or corrupt the economy. Fog of war means the server must not send hidden state to the client. Millions of players can exist in one persistent universe only if the universe is partitioned into regions and interest sets; millions cannot all be in one fully interactive local space with low latency. Factories and machines must be graph simulations with LOD, not physics actors everywhere. Terrain must be sparse and chunked, using procedural base state plus deltas and operation logs. Unobserved areas must collapse into macrostate, exact fast-forward, or deterministic late-bound detail depending on gameplay need.

The practical next step is not choosing UE6. It is building a small deterministic headless prototype. That prototype should prove fixed ticks, deterministic commands, cross-platform hashes, basic factory graphs, terrain chunk edits, and replay. Only after that should Dominium invest heavily in a renderer. Unreal remains useful, but the real Dominium engine is the custom simulation, world database, and authority layer.
