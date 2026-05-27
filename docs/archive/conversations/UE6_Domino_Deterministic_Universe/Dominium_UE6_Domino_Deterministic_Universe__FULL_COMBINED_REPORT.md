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


# STRUCTURED REGISTERS — Dominium UE6, Domino, and Deterministic Universe Feasibility

## 17. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | Engine/runtime strategy | Decide how UE5, UE6, Domino, and custom systems should relate | Recommended hybrid architecture exists | Explicit project-level engine strategy | Active | P0 | 4/5 | INFERENCE |
| WORKSTREAM-02 | Deterministic core | Build engine-independent canonical simulation | Concept defined | Cross-platform deterministic prototype | Active | P0 | 5/5 | INFERENCE |
| WORKSTREAM-03 | Sparse planetary world | Store procedural planets plus player deltas | Concept defined | Chunked sparse terrain/world database | Active | P0 | 4/5 | INFERENCE |
| WORKSTREAM-04 | Collapse/refine simulation | Simulate unseen regions cheaply while preserving accounting | Conceptual models listed | Tested macro/micro transition design | Active | P0 | 4/5 | INFERENCE |
| WORKSTREAM-05 | MMO authority/fog of war | Prevent cheating and hidden-state leakage | Principles defined | Server-authoritative interest-filtered prototype | Active | P0 | 5/5 | INFERENCE |
| WORKSTREAM-06 | Unreal client adapter | Use Unreal for rendering/tooling without owning game truth | Recommended | Thin client consuming Dominium state/API | Candidate | P1 | 4/5 | INFERENCE |
| WORKSTREAM-07 | Domino portability | Preserve later port path | Requirement inferred from user question | Domino adapter possible without rewriting core | Candidate | P1 | 3/5 | INFERENCE |

## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | Do not start directly on UE6 today | Recommended, not user-final | Visible answer on UE6 availability | Avoids basing architecture on unavailable/uncertain tech | Use UE5/custom core first | WORKSTREAM-01 | 4/5 | INFERENCE / UNVERIFIED |
| DECISION-02 | Unreal should be client/tooling, not canonical simulation | Recommended | Visible answer repeatedly states this | Protects determinism and portability | Custom core required | WORKSTREAM-01, WORKSTREAM-06 | 5/5 | INFERENCE |
| DECISION-03 | Build DominiumSim as custom deterministic core | Recommended | User requires determinism | Unreal gameplay stack unsuitable as truth layer | Headless prototype first | WORKSTREAM-02 | 5/5 | INFERENCE |
| DECISION-04 | Store planets as procedural base plus sparse deltas | Recommended | User requires full planets and edits | Avoids storing/simulating everything | WorldDB/event log needed | WORKSTREAM-03 | 4/5 | INFERENCE |
| DECISION-05 | Use server authority for persistent MMO outcomes | Recommended | Fog-of-war and cheating risks | Prevents client manipulation of resources/secrets | Client compute limited | WORKSTREAM-05 | 5/5 | INFERENCE |
| DECISION-06 | Define single universe as shared persistence with partitioned regions | Recommended | Millions in same local space rejected | Makes MMO goal tractable | Need region authority/interest management | WORKSTREAM-05 | 5/5 | INFERENCE |
| DECISION-07 | Keep Domino as future adapter | Recommended | User asked about later portability | Portability requires clean adapter boundary | Do not embed rules in Unreal | WORKSTREAM-07 | 4/5 | INFERENCE |

## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Define deterministic simulation MVP | P0 | U0 | User/project | None | Scope for machines/terrain/players | MVP spec | Choose minimal entities and tick model | WORKSTREAM-02 | INFERENCE |
| TASK-02 | Prototype fixed-tick command-log simulation | P0 | U1 | Project | TASK-01 | Language/toolchain | Running headless sim | Implement tick loop and state hashes | WORKSTREAM-02 | INFERENCE |
| TASK-03 | Define coordinate hierarchy | P0 | U1 | Project | TASK-01 | Solar-system scale targets | Coordinate spec | Pick integer/fixed-point representation | WORKSTREAM-03 | INFERENCE |
| TASK-04 | Prototype sparse terrain chunk edits | P0 | U1 | Project | TASK-03 | Terrain model choice | Save/load chunk delta demo | Implement chunk edit log | WORKSTREAM-03 | INFERENCE |
| TASK-05 | Model factory graph simulation | P0 | U1 | Project | TASK-01 | Machine/resource examples | Graph update prototype | Define node/edge invariants | WORKSTREAM-02 | INFERENCE |
| TASK-06 | Design collapse/refine rules | P0 | U1 | Project | TASK-05 | Macrostate invariants | Collapse/refine spec | Define accounting-preserving macro model | WORKSTREAM-04 | INFERENCE |
| TASK-07 | Define fog-of-war sensory model | P0 | U1 | Project | TASK-02 | Sensor/entity rules | Visibility and interest spec | List knowable vs hidden state | WORKSTREAM-05 | INFERENCE |
| TASK-08 | Define client authority boundaries | P0 | U1 | Project | TASK-07 | Trust model | Client/server authority matrix | Classify actions as propose/verify/commit | WORKSTREAM-05 | INFERENCE |
| TASK-09 | Build minimal server authority prototype | P1 | U2 | Project | TASK-02, TASK-07 | Networking/runtime choice | Server-owned state demo | Implement one region authority loop | WORKSTREAM-05 | INFERENCE |
| TASK-10 | Build Unreal visualization adapter | P1 | U2 | Project | TASK-02, TASK-04 | State API and mesh output | UE client demo | Render a local chunk from core data | WORKSTREAM-06 | INFERENCE |
| TASK-11 | Define Domino adapter contract | P1 | U2 | Project | TASK-01 | Domino capabilities | Adapter interface doc | Clarify Domino role | WORKSTREAM-07 | INFERENCE |
| TASK-12 | Verify current UE5/UE6 claims | P1 | U1 | Project | None | Official Epic docs/current sources | Verification memo | Browse official docs before hard decisions | WORKSTREAM-01 | UNVERIFIED |
| TASK-13 | Create engine strategy spec-book chapter | P1 | U2 | Project | This report | Aggregated Dominium context | Formal chapter | Merge with other Dominium reports | WORKSTREAM-01 | INFERENCE |
| TASK-14 | Define anti-lag/anti-abuse limits for player machines | P1 | U2 | Project | TASK-05 | Machine design goals | Limits/gas policy | Identify exploit classes | WORKSTREAM-02, WORKSTREAM-05 | INFERENCE |

## 20. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-01 | Canonical simulation must be deterministic if determinism remains a requirement | Technical | Hard | User requirement | Use fixed-step, deterministic math/order | Desyncs, broken replay | 5/5 | INFERENCE |
| CONSTRAINT-02 | Hidden state must not be sent to unauthorized clients | Security/gameplay | Hard | Fog-of-war requirement | Server-side interest filtering | Cheating and espionage | 5/5 | INFERENCE |
| CONSTRAINT-03 | Persistent MMO outcomes must be server-authoritative | Security | Hard | Client-cheat risk | Client propose/server verify | Economy corruption | 5/5 | INFERENCE |
| CONSTRAINT-04 | Commercial engine systems cannot own portable core rules | Architecture | Hard if Domino portability matters | User asks about porting | Adapter boundaries required | Port becomes rewrite | 5/5 | INFERENCE |
| CONSTRAINT-05 | Full-fidelity simulation everywhere is impossible | Compute | Hard | Scale requirements | Use simulation LOD | Lag/cost explosion | 5/5 | INFERENCE |
| CONSTRAINT-06 | A single local area cannot support millions of fully interacting players at low latency | Networking | Hard | Bandwidth/interest limits | Partition/LOD/caps/time dilation | Unrealistic promises | 5/5 | INFERENCE |
| CONSTRAINT-07 | External UE6 facts are stale-prone | Factual | Hard | UE6 roadmap changes | Verify before relying | Bad planning assumptions | 5/5 | UNVERIFIED |
| CONSTRAINT-08 | Player-designed machines need compute/resource limits | Design/security | Hard | Lag-abuse risk | Gas budgets/operation caps | Lag weapons | 4/5 | INFERENCE |
| CONSTRAINT-09 | File/report outputs must distinguish fact from inference | Documentation | Hard | Uploaded prompt | Use labels | Bad aggregation | 5/5 | FACT |
| CONSTRAINT-10 | This package cannot claim full-chat coverage beyond available context | Epistemic | Hard | Limited transcript access | Mark partial coverage | False preservation | 5/5 | FACT |

## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
|---|---|---|---|---|---|---|---|
| PREF-01 | Human-readable explanation before machine-readable registers | Documentation | Explicit | Strong | Lead with prose | Output feels unusable | FACT |
| PREF-02 | Direct, source-grounded, audit-ready answers | Communication | Explicit from user profile | Strong | Include uncertainty and caveats | Loss of trust | PROJECT-CONTEXT |
| PREF-03 | Do not over-compress | Documentation | Explicit in prompt | Strong | Preserve rationale and alternatives | Missing context | FACT |
| PREF-04 | Preserve rejected and tentative ideas | Documentation | Explicit in prompt | Strong | Track status carefully | Bad future decisions | FACT |
| PREF-05 | Avoid asking to proceed when enough info exists | Workflow | Explicit in prompt | Strong | Proceed with best effort | Unnecessary delay | FACT |
| PREF-06 | Downloadable files when available | Artifact | Explicit in prompt | Strong | Create package files | Incomplete deliverable | FACT |
| PREF-07 | Use labels FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT | Epistemic | Explicit in prompt | Strong | Label uncertain claims | False certainty | FACT |
| PREF-08 | Prefer long-term architectural correctness over short-term convenience | Technical | Inferred | Medium-high | Recommend custom core | Over-engineering if wrong | INFERENCE |

## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | Should Unreal be first renderer/client? | Affects tooling and prototype path | Unreal recommended as useful frontend | Final choice not user-confirmed | Compare prototype costs | P1 | WORKSTREAM-06 | INFERENCE |
| QUESTION-02 | What exactly is Domino? | Determines portability target | Domino referenced as alternative/future runtime | Detailed capabilities not visible here | Retrieve/define Domino spec | P0 | WORKSTREAM-07 | UNCERTAIN |
| QUESTION-03 | What language for DominiumSim? | Affects determinism/tooling | C++/Rust/C possible | No final language choice in this chat | Decide based on portability and tests | P0 | WORKSTREAM-02 | UNCERTAIN |
| QUESTION-04 | What determinism standard is required? | Drives math/networking | Determinism required broadly | Exact standard not specified | Define deterministic test contract | P0 | WORKSTREAM-02 | UNCERTAIN |
| QUESTION-05 | What terrain representation should be used? | Affects planets/terraforming | Sparse voxel/SDF/hybrid discussed | Final representation undecided | Prototype alternatives | P0 | WORKSTREAM-03 | UNCERTAIN |
| QUESTION-06 | How exact must collapse/refine be? | Affects simulation LOD | Three models listed | Tolerance not specified | Define invariants | P0 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-07 | What MMO scale target is first? | Avoids impossible milestone | Millions local rejected | First player/bot target undecided | Choose test ladder | P1 | WORKSTREAM-05 | UNCERTAIN |
| QUESTION-08 | How to handle player-made lag machines? | Prevents abuse | Need gas/limits | Concrete limits undecided | Threat model and budget policy | P1 | WORKSTREAM-02 | INFERENCE |
| QUESTION-09 | Which UE5/UE6 facts are currently true? | Avoids stale planning | Earlier answers used external claims | Current 2026 state not verified in this pass | Check official docs/news | P1 | WORKSTREAM-01 | UNVERIFIED |
| QUESTION-10 | What source assets and schemas preserve portability? | Avoids Unreal lock-in | Source assets should stay portable | Exact formats/pipeline not specified | Define asset/data pipeline | P1 | WORKSTREAM-01 | INFERENCE |

## 23. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-01 | User-pasted UE6 requirements answer | Pasted text | Triggered UE6 vs Domino question | Preserved in visible chat | User | Yes, with verification caveat | External claims may be stale/wrong | FACT / UNVERIFIED |
| ARTIFACT-02 | Assistant UE5-now/UE6-later answer | Chat answer | Strategic engine guidance | Preserved | Assistant | Yes | Not user-final by itself | FACT |
| ARTIFACT-03 | User deterministic solar-system/MMO question | Chat prompt | Defines full technical challenge | Preserved | User | Yes | High-value requirements source | FACT |
| ARTIFACT-04 | Assistant hybrid architecture answer | Chat answer | Defines DominiumSim/WorldDB/Server pattern | Preserved | Assistant | Yes | Main architecture artifact | FACT |
| ARTIFACT-05 | Pasted text.txt | Uploaded prompt | Requests this preservation package | Available | User | Yes | Current uploaded file | FACT |
| ARTIFACT-06 | 00_manifest.md | Generated file | Package overview | Created by this task | Assistant/tool | Yes | New artifact | FACT |
| ARTIFACT-07 | 01_human_readable_report.md | Generated file | Sections 0–16 | Created by this task | Assistant/tool | Yes | New artifact | FACT |
| ARTIFACT-08 | 02_context_transfer_packet.md | Generated file | Future chat packet | Created by this task | Assistant/tool | Yes | New artifact | FACT |
| ARTIFACT-09 | 03_spec_sheet.yaml | Generated file | Aggregation spec | Created by this task | Assistant/tool | Yes | New artifact | FACT |
| ARTIFACT-10 | 04_registers.md | Generated file | Sections 17–28 | Created by this task | Assistant/tool | Yes | New artifact | FACT |
| ARTIFACT-11 | 05_aggregator_packet.md | Generated file | Central aggregation input | Created by this task | Assistant/tool | Yes | New artifact | FACT |
| ARTIFACT-12 | 06_reader_brief.md | Generated file | Short brief | Created by this task | Assistant/tool | Yes | New artifact | FACT |
| ARTIFACT-13 | 07_verification_and_audit.md | Generated file | Audit and verification | Created by this task | Assistant/tool | Yes | New artifact | FACT |
| ARTIFACT-14 | 08_future_chat_bootstrap_prompt.md | Generated file | Reuse prompt | Created by this task | Assistant/tool | Yes | New artifact | FACT |
| ARTIFACT-15 | 09_in_chat_reader.md | Generated file | Reader guide | Created by this task | Assistant/tool | Yes | New artifact | FACT |
| ARTIFACT-16 | handoff_package.zip | Generated ZIP | Bundled files | Created by this task | Assistant/tool | Yes | New artifact | FACT |

## 24. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| REJECTED-01 | Unreal as entire game | Rejected | Blocks determinism/portability | Tentative but strong | Only if goals are reduced | WORKSTREAM-01 | INFERENCE |
| REJECTED-02 | Wait for UE6 | Deprioritised | UE6 uncertain/unavailable | Tentative | If UE6 becomes public and uniquely useful | WORKSTREAM-01 | INFERENCE / UNVERIFIED |
| REJECTED-03 | Client authority for MMO simulation | Rejected | Cheating/secrecy/economy risk | Strong | Private single-player/co-op only | WORKSTREAM-05 | INFERENCE |
| REJECTED-04 | Millions in one local fully interactive space | Rejected | Networking/computation limits | Strong | Only abstracted/time-dilated/instanced | WORKSTREAM-05 | INFERENCE |
| REJECTED-05 | Full-fidelity sim everywhere | Rejected | Compute/storage impossible | Strong | Small offline worlds only | WORKSTREAM-04 | INFERENCE |
| REJECTED-06 | Unreal Blueprints as core source of truth | Rejected | Not portable to Domino | Strong if portability matters | Throwaway prototype only | WORKSTREAM-07 | INFERENCE |
| REJECTED-07 | Every factory object as active physics | Rejected | Scale infeasible | Strong | Tiny demos only | WORKSTREAM-02 | INFERENCE |

## 25. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Treating assistant recommendation as user-final decision | Misleading spec | Medium | High | Mark status and ask for confirmation before formalizing | All | INFERENCE |
| RISK-02 | Building too much inside Unreal | Domino port becomes rewrite | High | High | Enforce core/adapter separation | WORKSTREAM-01 | INFERENCE |
| RISK-03 | Determinism failure across platforms | Desync/replay breakage | High | High | Fixed math, state hashes, CI tests | WORKSTREAM-02 | INFERENCE |
| RISK-04 | Terrain storage explosion | Storage/cost failure | Medium | High | Sparse deltas/compression/snapshots | WORKSTREAM-03 | INFERENCE |
| RISK-05 | Collapse/refine breaks resource accounting | Economy inconsistency | Medium | High | Define invariants and audits | WORKSTREAM-04 | INFERENCE |
| RISK-06 | Fog-of-war leakage | Cheating/spoilers | Medium | High | Server interest filtering | WORKSTREAM-05 | INFERENCE |
| RISK-07 | Client compute abuse | Economy corruption | High | High | Server verification/commit only | WORKSTREAM-05 | INFERENCE |
| RISK-08 | MMO scale overpromise | Failed architecture expectations | High | High | Define scale tiers and load tests | WORKSTREAM-05 | INFERENCE |
| RISK-09 | UE6 claims become stale | Bad technology plan | High | Medium | Verify current official sources | WORKSTREAM-01 | UNVERIFIED |
| RISK-10 | Player machines become lag weapons | Server degradation | High | High | Gas/operation budgets | WORKSTREAM-02 | INFERENCE |
| RISK-11 | Spec book merges tentative content as requirement | Wrong commitments | Medium | High | Preserve labels | All | FACT |
| RISK-12 | Missing broader project context | Incomplete preservation | Medium | Medium | Merge with other chat reports later | All | PROJECT-CONTEXT |

## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Current UE6 public availability and roadmap | Time-sensitive | Official Epic announcements/docs | P0 | WORKSTREAM-01 | UNVERIFIED |
| VERIFY-02 | Current UE5 minimum/recommended platform requirements | Time-sensitive | Official Epic docs | P1 | WORKSTREAM-01 | UNVERIFIED |
| VERIFY-03 | Current Unreal determinism/networking capabilities | Version-sensitive | Epic docs/source/release notes | P1 | WORKSTREAM-02 | UNVERIFIED |
| VERIFY-04 | Domino technical capabilities | Missing definition | Project docs/source | P0 | WORKSTREAM-07 | UNCERTAIN |
| VERIFY-05 | Viability of Voxel Plugin/runtime terrain for MMO | Product/version-sensitive | Plugin docs/prototype | P2 | WORKSTREAM-03 | UNVERIFIED |
| VERIFY-06 | Best fixed-point/deterministic math library choices | Technical selection | Benchmarks/prototypes | P1 | WORKSTREAM-02 | UNVERIFIED |
| VERIFY-07 | Persistence backend options for sparse chunks/events | Architecture selection | Prototype/DB docs | P1 | WORKSTREAM-03 | UNVERIFIED |
| VERIFY-08 | Practical player-count targets by phase | Product planning | Benchmarks/design docs | P1 | WORKSTREAM-05 | UNCERTAIN |
| VERIFY-09 | Licensing implications of Unreal vs custom/Domino | Business/legal | Official licenses/legal review | P1 | WORKSTREAM-01 | UNVERIFIED |

## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
|---|---|---|---|---|---|
| 1 | User pasted UE6 platform answer | Introduced UE6 as possible Dominium base | Triggered architecture question | External claims need verification | 4/5 |
| 2 | User asked UE6 instead of Domino | Need for engine strategy became explicit | Dominium portability at stake | Core question remains relevant | 5/5 |
| 3 | Assistant recommended UE5 now/UE6 later/Domino portability | Set hybrid direction | Avoided waiting for UE6 | Main strategic guidance | 4/5 |
| 4 | User expanded to deterministic solar-system/MMO requirements | Scope widened dramatically | Engine choice became system architecture question | Central project framing | 5/5 |
| 5 | Assistant rejected out-of-box engine solution | Clarified no commercial engine solves all | Avoids unrealistic expectations | Important caveat | 5/5 |
| 6 | Assistant proposed DominiumSim/WorldDB/Server | Established core architecture | Gives portable path | Main carry-forward | 5/5 |
| 7 | Assistant detailed determinism, sparse terrain, fog, client trust, MMO limits | Created design principles | Identifies future work | High relevance | 5/5 |
| 8 | User uploaded preservation prompt | Requested report/files/registers | Turned chat into archival task | Current deliverable | 5/5 |

## 28. Spec Book Contribution Register

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
|---|---|---|---|---|---|
| Engine strategy | Unreal as frontend, not canonical simulation | DECISION-02 | Requirement candidate | 5/5 | Needs user confirmation |
| Deterministic simulation | Fixed-step custom core | DECISION-03 | Requirement candidate | 5/5 | Core prototype first |
| World persistence | Procedural planets plus sparse deltas | DECISION-04 | Requirement candidate | 4/5 | Terrain model still open |
| MMO authority | Server-authoritative persistent outcomes | DECISION-05 | Requirement candidate | 5/5 | Hard security constraint |
| Portability | Domino as adapter target | DECISION-07 | Context/open issue | 4/5 | Domino capabilities needed |
| Simulation LOD | Collapse/refine as core mechanic | WORKSTREAM-04 | Requirement candidate | 4/5 | Must prototype |
| Scale limits | Single universe not single local million-player room | DECISION-06 | Requirement/context | 5/5 | Prevents overpromise |


# CONTEXT TRANSFER PACKET FOR A FUTURE CHAT — Dominium UE6, Domino, and Deterministic Universe Feasibility

## 29.1 Ultra-Condensed Bootstrap Brief

This chat addressed whether Dominium should be built on UE6, UE5, Domino, Unreal, or a custom architecture. The key conclusion is that Dominium should not be treated as “an Unreal game” if its requirements remain deterministic simulation, full-scale solar-system worlds, procedural planets, terraforming, player-built civilizations, fog of war, sparse simulation, and single-universe MMO ambitions. Unreal/UE5/UE6 may be useful as a renderer, editor, tooling layer, and client frontend. The canonical game should be a custom deterministic simulation and world authority stack.

The recommended architecture is `DominiumSim + DominiumWorldDB + DominiumServer`, with clients/adapters such as `DominiumClient_UE` and a possible future `DominiumClient_Domino`. DominiumSim owns fixed-step deterministic simulation, machine/factory graphs, resource accounting, deterministic RNG, state hashes, and replay. DominiumWorldDB owns solar-system coordinate hierarchy, planet/chunk storage, procedural seeds, terrain/material deltas, event logs, snapshots, and versioning. DominiumServer owns authority, fog-of-war filtering, interest management, region handoff, anti-cheat validation, and persistence. Unreal should render local bubbles, play animation/audio, provide UI/tools, and display construction previews; it should not be the source of truth.

The chat rejected several tempting but unsafe paths: waiting for UE6, trusting clients with persistent MMO authority, assuming millions of players can share one local fully interactive space at low latency, simulating full fidelity everywhere, and embedding portable gameplay rules in Unreal Blueprints or `.uasset` assets. The practical meaning of “single universe” should be one persistent shared world with region authority and global services, not one server or one physics room.

Important unresolved questions remain: the exact role and capabilities of Domino, whether Unreal should be the first frontend, what language should implement DominiumSim, what terrain representation should be used, what determinism standard is required, how exact collapse/refine must be, and what early player-count benchmarks should be targeted. External facts about UE6/UE5 capabilities and platform requirements must be reverified before hard commitments.

Recommended first action: define and build the smallest deterministic headless prototype: fixed tick, command log, deterministic RNG, state hashes, a small factory graph, sparse terrain chunk edits, and replay validation across at least two platforms/toolchains.

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
- Do not assume access to the old chat.
- Do not re-ask answered questions.
- Verify stale engine, platform, licensing, and roadmap facts before relying on them.
- Do not treat assistant recommendations as user-final decisions unless the user confirms them.
- Do not claim UE6 solves determinism/MMO/sparse simulation unless verified.
- Preserve the core/adapter separation.
- Keep hidden chain-of-thought private; provide visible rationale only.
- Use the task register and open questions to drive next actions.

## 29.4 Active Workstreams

- WORKSTREAM-01: Engine/runtime strategy.
- WORKSTREAM-02: Deterministic core.
- WORKSTREAM-03: Sparse planetary world.
- WORKSTREAM-04: Collapse/refine simulation.
- WORKSTREAM-05: MMO authority and fog of war.
- WORKSTREAM-06: Unreal client adapter.
- WORKSTREAM-07: Domino portability.

## 29.5 Current Priorities

1. Define deterministic simulation MVP.
2. Clarify Domino’s technical role.
3. Verify current UE5/UE6 facts.
4. Prototype sparse terrain edits.
5. Define client/server authority boundaries.

## 29.6 Current Open Questions

The main open questions are Domino’s role, Unreal’s role as first client, deterministic language/math choices, terrain representation, collapse/refine exactness, and MMO scale targets.

## 29.7 Recommended First Action

Write a formal MVP spec for `DominiumSim`: tick model, command model, entity/resource schema, deterministic math, state hashing, replay, factory graph, and sparse terrain edit proof.


# SPEC SHEET

```yaml
spec_sheet:
  metadata:
    chat_label: "Dominium UE6, Domino, and Deterministic Universe Feasibility"
    date_anchor: "2026-05-27 Australia/Melbourne"
    source_scope: "This chat only, plus labelled PROJECT-CONTEXT where used"
    apparent_coverage: "Partial"
    confidence_1_to_5: 3
    staleness_risk: "Medium to high for engine and platform claims"
    safe_for_aggregation: "With caveats"
    main_limitations:
      - "Full historical Dominium transcript not visible."
      - "External UE5/UE6 claims were not freshly verified during this packaging pass."
      - "Some prior uploaded files in the broader environment may have expired."

  summary:
    one_sentence: "Dominium should use a custom deterministic simulation/world/server core with Unreal/UE as a possible frontend and Domino as a possible later adapter, not rely on UE6 or any commercial engine as the complete game."
    short_brief: "The chat evaluated UE6, UE5, Unreal, Domino, and other engines against an ambitious deterministic solar-system-scale MMO/civilization-building vision. It concluded that no commercial engine solves the full requirement set out of the box. The carry-forward architecture is DominiumSim plus DominiumWorldDB plus DominiumServer, with Unreal and Domino clients as replaceable adapters."
    main_topics:
      - "UE6 versus UE5 versus Domino"
      - "Engine-independent simulation core"
      - "Deterministic full-scale world simulation"
      - "Sparse planets and terrain edits"
      - "Fog of war and server authority"
      - "Single-universe MMO limits"
      - "Client-shared compute boundaries"
    main_outputs:
      - "Hybrid architecture recommendation"
      - "Decision and risk registers"
      - "Prototype roadmap"
      - "Verification queue"
    highest_priority_carry_forward:
      - "Build deterministic headless prototype first."
      - "Do not put canonical game truth in Unreal."
      - "Clarify Domino’s role."
      - "Verify current UE5/UE6 facts."

  source_rules:
    labels_used:
      - "FACT"
      - "INFERENCE"
      - "UNCERTAIN / UNVERIFIED"
      - "PROJECT-CONTEXT"
    conflict_rules:
      - "Direct user statements outrank assistant recommendations."
      - "Assistant suggestions are not final decisions unless user accepted them."
      - "Current verified official sources outrank older claims."
    staleness_rules:
      - "Engine roadmaps, platform requirements, licensing, and plugin capabilities require re-verification."
      - "Speculative UE6 claims must not become requirements without current confirmation."

  user_preferences:
    explicit:
      - "Human-readable report before machine-readable handoff."
      - "Preserve uncertainty labels."
      - "Do not invent facts or silently infer."
      - "Create files if tools are available."
    inferred:
      - "Prefer architectural optionality and long-term correctness."
      - "Prefer direct feasibility analysis over optimistic framing."
    uncertain_or_not_established:
      - "Final tolerance for custom-engine complexity versus commercial-engine speed."

  workstreams:
    - id: "WORKSTREAM-01"
      name: "Engine/runtime strategy"
      label: "INFERENCE"
      objective: "Define how UE5, UE6, Domino, and custom layers relate."
      current_state: "Hybrid recommendation exists."
      desired_end_state: "Formal engine strategy with accepted decisions."
      status: "active"
      priority: "P0"
      background: "User asked whether Dominium could use UE6 instead of Domino and later port to Domino."
      decisions_made: ["DECISION-01", "DECISION-02", "DECISION-07"]
      decisions_pending: ["Should Unreal be first renderer?", "What is Domino’s exact role?"]
      tasks: ["TASK-12", "TASK-13"]
      constraints: ["CONSTRAINT-04", "CONSTRAINT-07"]
      dependencies: ["Domino capabilities", "Current UE facts"]
      timeline: "Near-term architecture planning."
      blockers: ["Unverified UE6 facts", "Unclear Domino role"]
      risks: ["RISK-02", "RISK-09"]
      artifacts: ["ARTIFACT-02", "ARTIFACT-04"]
      success_criteria: ["Core/adapter boundaries are explicit", "No canonical rule depends on Unreal"]
      next_action: "Verify UE facts and clarify Domino."
      verification_needed: ["VERIFY-01", "VERIFY-02", "VERIFY-09"]
      confidence: 4
    - id: "WORKSTREAM-02"
      name: "Deterministic core"
      label: "INFERENCE"
      objective: "Build portable fixed-step canonical simulation."
      current_state: "Concept defined."
      desired_end_state: "Cross-platform deterministic prototype."
      status: "active"
      priority: "P0"
      background: "Required by user’s deterministic game requirement."
      decisions_made: ["DECISION-03"]
      decisions_pending: ["Language", "Math representation", "Determinism standard"]
      tasks: ["TASK-01", "TASK-02", "TASK-05", "TASK-14"]
      constraints: ["CONSTRAINT-01", "CONSTRAINT-08"]
      dependencies: ["MVP scope"]
      timeline: "First technical proof."
      blockers: ["Undefined MVP"]
      risks: ["RISK-03", "RISK-10"]
      artifacts: ["ARTIFACT-04"]
      success_criteria: ["Same input log yields same state hash"]
      next_action: "Specify deterministic MVP."
      verification_needed: ["VERIFY-06"]
      confidence: 5

  decisions:
    - id: "DECISION-01"
      decision: "Do not start directly on UE6 today."
      status: "assistant recommendation, not user-final"
      label: "INFERENCE / UNVERIFIED"
      evidence_or_basis: "Visible assistant response stated public UE6 information is too thin."
      rationale: "Avoids dependence on unavailable or unstable technology."
      implications: "Use UE5/custom core now; revisit UE6 later."
      related_workstreams: ["WORKSTREAM-01"]
      uncertainty: "Requires current verification."
    - id: "DECISION-03"
      decision: "Build custom deterministic simulation core."
      status: "assistant recommendation"
      label: "INFERENCE"
      evidence_or_basis: "User requires deterministic game and large-scale sparse simulation."
      rationale: "Commercial engine gameplay stacks are not suitable as canonical deterministic truth."
      implications: "Prototype headless DominiumSim first."
      related_workstreams: ["WORKSTREAM-02"]
      uncertainty: "Implementation language and exact determinism standard remain undecided."

  tasks:
    - id: "TASK-01"
      task: "Define deterministic simulation MVP."
      priority: "P0"
      urgency: "U0"
      owner: "Project/user"
      dependencies: []
      inputs_needed: ["Minimal entities", "factory graph scope", "terrain edit scope"]
      expected_output: "MVP technical spec"
      next_step: "Choose tick model and state hash contents."
      related_workstreams: ["WORKSTREAM-02"]
      label: "INFERENCE"
      confidence: 5

  constraints:
    - id: "CONSTRAINT-01"
      constraint: "Canonical simulation must be deterministic if determinism remains a requirement."
      type: "technical"
      hard_or_soft: "hard"
      source_or_basis: "User requirement"
      implication: "Use fixed-step deterministic core."
      violation_risk: "Desyncs and non-portable simulation."
      label: "INFERENCE"
      confidence: 5

  open_questions:
    - id: "QUESTION-02"
      question: "What exactly is Domino’s technical scope and role?"
      why_it_matters: "Determines what portability requires."
      known: "User contrasts Domino with UE6 and asks about later portability."
      unknown: "Domino capabilities and intended boundary."
      resolution_path: "Retrieve or write Domino architecture definition."
      priority: "P0"
      related_workstreams: ["WORKSTREAM-07"]
      label: "UNCERTAIN"

  rejected_or_superseded_options:
    - id: "REJECTED-01"
      option: "Unreal as the entire game."
      status: "rejected as recommended architecture"
      reason: "Blocks determinism and portability."
      final_or_tentative: "tentative but strong"
      reconsider_conditions: "Only if project goals are reduced."
      related_workstreams: ["WORKSTREAM-01"]
      label: "INFERENCE"

  artifacts:
    - id: "ARTIFACT-05"
      name_or_description: "Pasted text.txt"
      type: "uploaded prompt"
      purpose: "Requested this preservation package."
      status: "available during this task"
      origin: "user"
      carry_forward: true
      notes: "Defines output structure and reliability labels."
      label: "FACT"

  risks:
    - id: "RISK-02"
      risk: "Building too much inside Unreal."
      consequence: "Domino port becomes rewrite and determinism weakens."
      likelihood: "high"
      severity: "high"
      mitigation: "Enforce core/adapter separation."
      related_workstreams: ["WORKSTREAM-01", "WORKSTREAM-06", "WORKSTREAM-07"]
      label: "INFERENCE"

  verification_queue:
    - id: "VERIFY-01"
      item: "Current UE6 public availability and roadmap."
      why_verification_needed: "UE6 claims are time-sensitive."
      suggested_source_type: "Official Epic sources and current announcements."
      priority: "P0"
      related_workstreams: ["WORKSTREAM-01"]
      label: "UNVERIFIED"

  spec_book_notes:
    likely_sections:
      - "Engine/runtime strategy"
      - "Deterministic simulation"
      - "World persistence and terrain"
      - "MMO authority and fog of war"
      - "Renderer/client adapters"
    unique_contributions:
      - "Clear separation between Dominium as simulation/backend and Unreal as frontend."
      - "Explicit rejection of millions of players in one local fully interactive space."
    possible_duplicates_with_other_chats:
      - "Platform/renderer separation doctrine"
      - "Dominium deterministic C engine doctrine"
      - "Distribution/setup architecture"
    conflicts_to_watch_for:
      - "Any chat that treats Domino as the only possible first implementation."
      - "Any chat that embeds game rules in renderer-specific systems."
    formal_requirements_candidates:
      - "Engine-independent core"
      - "Server-authoritative MMO outcomes"
      - "Simulation LOD/collapse-refine"
    background_context_candidates:
      - "Engine examples to study: Factorio, EVE, Cesium, UNIGINE, SpaceEngine-like systems."
    needs_user_confirmation:
      - "Whether to accept Unreal as first client."
      - "Whether to formalize custom deterministic core as non-negotiable."

  final_recommendations:
    next_action_if_continuing_this_chat: "Define DominiumSim deterministic MVP."
    next_action_for_aggregator: "Merge this as the engine/runtime strategy and simulation authority chapter input."
    user_checks_required:
      - "Confirm whether the assistant recommendations should become project decisions."
      - "Clarify Domino’s role."
      - "Verify UE5/UE6 facts with current official sources."
```


# Aggregator Packet — Dominium UE6, Domino, and Deterministic Universe Feasibility

## Packet Metadata

* Chat label: Dominium UE6, Domino, and Deterministic Universe Feasibility
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: This chat only, plus labelled PROJECT-CONTEXT where used
* Coverage: Partial
* Confidence: 3/5
* Staleness risk: Medium to high for external engine claims
* Merge priority: High for Dominium architecture/spec book
* Main limitations: Full historical project transcript not visible; UE6/UE5 facts require re-verification; assistant recommendations are not automatically user-final decisions.

## Ultra-Condensed Carry-Forward Capsule

This chat is a high-value engine/runtime strategy discussion for Dominium. The user first asked whether Dominium could be made on UE6 instead of Domino and later ported to Domino. The answer recommended not waiting for UE6 and not using Unreal as the whole game. It proposed a portable architecture where DominiumCore is permanent and Unreal/UE6/Domino are adapters. The user then expanded the question to the full game vision: deterministic real-scale solar system, procedural planets, player-built civilizations, terraforming, cut/fill, megaprojects, player-designed machines and factories, fog of war, collapsed unseen areas, client-shared compute, single-player multi-universe gameplay, and MMORPG single-universe scale.

The core conclusion is that no commercial engine, including UE5 or publicly known UE6, can deliver this entire combination out of the box. Unreal remains useful for rendering, tooling, editor workflows, animation, UI, construction previews, and local visualization. It should not own the canonical deterministic simulation or persistent universe authority. The durable architecture should be `DominiumSim + DominiumWorldDB + DominiumServer`, with `DominiumClient_UE` and `DominiumClient_Domino` as replaceable clients/adapters.

DominiumSim should own fixed-step deterministic simulation, fixed-point/integer math where needed, deterministic RNG, stable ordering, command logs, state hashes, factory graph simulation, resource accounting, replay, and desync tests. DominiumWorldDB should own solar-system coordinate hierarchy, planet seed data, chunk storage, sparse terrain/material deltas, construction/destruction operation logs, snapshots, version migration, and persistence. DominiumServer should own authority, fog-of-war filtering, interest management, anti-cheat validation, region handoff, load balancing, and global persistence/economy services.

Important rejected options: Unreal as entire game, waiting for UE6, trusting clients with persistent MMO outcomes, simulating full fidelity everywhere, supporting millions of players in one local mutually interacting space at low latency, and storing portable core rules in Unreal-only assets/Blueprints. Important unresolved questions: Domino’s exact role, whether Unreal should be first client, language/math for DominiumSim, terrain representation, collapse/refine exactness, and practical MMO scale targets.

The best next action is to define a deterministic headless MVP: fixed tick, command log, deterministic RNG, state hashes, small factory graph, sparse terrain chunk edits, and replay validation.

## Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
|---|---|---|---|---|---|---|
| P0 | Custom deterministic core | Requirement candidate | DECISION-03 | Makes determinism and portability possible | INFERENCE | 5/5 |
| P0 | Unreal as frontend only | Architecture rule | DECISION-02 | Avoids engine lock-in | INFERENCE | 5/5 |
| P0 | Server-authoritative MMO outcomes | Security rule | DECISION-05 | Prevents cheating/fog leakage | INFERENCE | 5/5 |
| P0 | Sparse procedural planets | World model | DECISION-04 | Makes planet-scale edits feasible | INFERENCE | 4/5 |
| P1 | Verify UE6 facts | Verification | VERIFY-01 | Avoid stale planning | UNVERIFIED | 5/5 |
| P1 | Clarify Domino role | Open question | QUESTION-02 | Determines port path | UNCERTAIN | 5/5 |

## Workstream Summaries

* WORKSTREAM-01: Engine/runtime strategy. Objective: define UE5/UE6/Domino/custom relationship. Priority: P0. Next action: verify UE facts and clarify Domino.
* WORKSTREAM-02: Deterministic core. Objective: fixed-step portable simulation. Priority: P0. Next action: write MVP spec.
* WORKSTREAM-03: Sparse planetary world. Objective: procedural planets plus sparse deltas. Priority: P0. Next action: prototype terrain chunks.
* WORKSTREAM-04: Collapse/refine simulation. Objective: maintain fidelity/accounting without simulating everything. Priority: P0. Next action: define macrostate invariants.
* WORKSTREAM-05: MMO authority/fog of war. Objective: server-authoritative hidden-state-safe universe. Priority: P0. Next action: define client/server authority matrix.
* WORKSTREAM-06: Unreal client adapter. Objective: render and tool Dominium without owning game truth. Priority: P1. Next action: render state from core API.
* WORKSTREAM-07: Domino portability. Objective: keep future port path. Priority: P1. Next action: define Domino adapter contract.

## Compact Registers for Merge

Use the full register file for detailed merge. Highest-priority records: DECISION-02, DECISION-03, DECISION-05, CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-03, TASK-01, TASK-02, TASK-06, QUESTION-02, VERIFY-01.

## Possible Cross-Chat Duplicates

- Dominium platform/renderer separation doctrine.
- C89 deterministic engine / C++98 shell discussions.
- Domino runtime discussions.
- Launcher/setup/distribution architecture discussions.
- Solar-system procedural planet generation discussions.

## Possible Cross-Chat Conflicts

- Other chats may treat Domino as primary engine rather than future adapter.
- Other chats may assume Unreal is unsuitable entirely; this chat says Unreal is useful as frontend.
- Other chats may use “single universe” more literally; this chat constrains it to shared persistence plus partitioned authority.

## Spec Book Integration Guidance

Feed this chat into chapters on engine/runtime strategy, deterministic simulation, world persistence, MMO authority, fog of war, sparse terrain, renderer/client adapters, and prototype roadmap. Convert custom deterministic core and server authority into requirement candidates, but do not finalize Unreal-first or Domino roles without user confirmation and verification.

## Aggregator Warnings

Do not collapse “UE frontend” into “UE game.” Do not treat assistant recommendations as final user decisions. Do not merge UE6 claims without current official verification. Do not promise literal million-player local interaction.


# VERIFICATION AND AUDIT — Dominium UE6, Domino, and Deterministic Universe Feasibility

## 32. Adversarial Self-Audit

| Issue | Severity | Correction needed | Correction applied? | Residual risk |
|---|---|---|---|---|
| Full historic Dominium transcript not visible | High | Mark coverage partial | Yes | Broader project details may be missing |
| UE6/UE5 claims time-sensitive | High | Add verification queue | Yes | Requires future browsing/official docs |
| Assistant recommendations could be mistaken for decisions | High | Mark decision status | Yes | User should confirm formal decisions |
| Domino role unclear | High | Add open question | Yes | Cannot specify adapter details yet |
| Report could overstate Unreal usefulness | Medium | Limit Unreal to frontend/tooling role | Yes | Prototype may still reveal issues |
| Report could understate custom-engine cost | Medium | Include risks/tasks | Yes | Needs implementation estimates later |
| File package may be less exhaustive than impossible full transcript | High | State limitations | Yes | Manual review recommended |
| Project context could contaminate chat-only scope | Medium | Label PROJECT-CONTEXT | Yes | Some context may still influence phrasing |
| External engine examples not freshly cited | Medium | Put in verification queue | Yes | Future source-grounded spec needed |
| Output could be too machine-like | Medium | Human report included first | Yes | User may still want more narrative detail |

## 33. Corrections Applied

- Coverage was explicitly marked Partial rather than Full.
- UE6/UE5 platform and roadmap facts were put in the verification queue.
- Assistant recommendations were labelled as recommendations unless user acceptance was explicit.
- Domino’s role was marked UNCERTAIN.
- The report separated visible chat facts from project-context carry-forward.
- A concrete next action was selected: deterministic headless MVP specification.

## 34. Final Reliability Assessment

* Completeness rating 1–5: 3
* Reliability rating 1–5: 4 for visible-chat reconstruction; 2–3 for full-project reconstruction
* Human-readability rating 1–5: 4
* Aggregation-readiness rating 1–5: 4 with caveats
* Main remaining uncertainty sources: incomplete transcript, unverified UE6/UE5 facts, unclear Domino capabilities, assistant recommendations not user-final.
* Manual review before merge: Yes.

## Verification Queue

See Section 26 in the registers file. Highest priority: VERIFY-01 current UE6 public availability/roadmap; VERIFY-04 Domino technical capabilities; VERIFY-09 licensing implications.


# IN-CHAT READER — Dominium UE6, Domino, and Deterministic Universe Feasibility

## Package overview

This package preserves the visible chat about Dominium’s engine/runtime strategy. It explains why Unreal/UE6 should not be treated as the whole game, why a custom deterministic core is required, how Domino portability can be preserved, and what work should happen next.

## File index

| File | Purpose | What it contains | When to use it | Importance |
|---|---|---|---|---|
| 00_manifest.md | Package overview | File list, purposes, caveats, status | First file to inspect | High |
| 01_human_readable_report.md | Main explanation | Sections 0–16 | To understand the chat | Highest |
| 02_context_transfer_packet.md | Future chat handoff | Section 29 | To continue in a new chat | High |
| 03_spec_sheet.yaml | Structured spec | Section 30 | For machine-assisted aggregation | High |
| 04_registers.md | Structured records | Sections 17–28 | For decisions/tasks/risks | High |
| 05_aggregator_packet.md | Merge packet | Section 31 | For central spec book | High |
| 06_reader_brief.md | Short guide | Top things to know | Fast review | Medium-high |
| 07_verification_and_audit.md | Audit | Sections 32–34 and verification | Before relying on facts | High |
| 08_future_chat_bootstrap_prompt.md | Prompt | Standalone continuation prompt | To start a new chat | Medium-high |
| 09_in_chat_reader.md | Navigation guide | This guide | To ask follow-ups here | Medium |

## Plain-English explanation

The chat concluded that Dominium’s requirements exceed what UE5, UE6, Domino, or any single commercial engine can provide out of the box. The game should be architected as a custom deterministic simulation and persistent world backend, with Unreal as a possible frontend and Domino as a possible later adapter. The most important immediate task is a deterministic headless prototype, not a final renderer choice.

## Question menu

- Explain the hybrid architecture again in simpler terms.
- Which items should become formal project requirements?
- What does the first deterministic prototype need to include?
- How should collapse/refine simulation work?
- How should server authority and fog of war interact?
- What does Domino need to support for a later port?
- What UE5/UE6 facts need verification?

## Top things to preserve

- `DominiumSim + DominiumWorldDB + DominiumServer` is the main architecture.
- Unreal is frontend/tooling, not canonical truth.
- Domino portability requires core/adapter separation.
- Client compute must not commit persistent MMO outcomes.
- Single universe means shared persistence plus partitioned authority.
- External engine facts require current verification.

## Safest next actions

1. Confirm whether the architecture recommendations should become project decisions.
2. Define Domino’s role.
3. Verify UE5/UE6 facts.
4. Specify the deterministic MVP.
5. Prototype fixed-tick replay and state hashes.

# Final Package Status

* Chat label: Dominium UE6, Domino, and Deterministic Universe Feasibility
* Report type: full human-readable + structured handoff + spec-prep package
* Files created: yes
* ZIP created: yes
* Safe for later aggregation: with caveats
* Extraction confidence: 3/5
* Main value of this chat: It establishes the Dominium engine/runtime strategy: custom deterministic simulation and backend first, Unreal/UE as frontend, Domino as possible adapter.
* Most important decision: Keep the canonical game state outside Unreal and commercial engine systems.
* Most important unresolved issue: Domino’s exact role and capabilities are not defined in the visible chat.
* Most important next action: Define the first deterministic `DominiumSim` MVP.
* Main caveats: Partial transcript access; UE5/UE6 facts need verification; assistant recommendations need user confirmation before becoming final project decisions.
* Best thing for me to read first: `01_human_readable_report.md`
* Best question for me to ask next: “Define the first deterministic DominiumSim prototype in detail.”
