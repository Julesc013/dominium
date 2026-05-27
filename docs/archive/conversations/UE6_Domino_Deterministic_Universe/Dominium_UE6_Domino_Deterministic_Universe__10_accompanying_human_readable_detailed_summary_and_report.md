# ACCOMPANYING HUMAN-READABLE DETAILED SUMMARY AND REPORT — Dominium UE6, Domino, and Deterministic Universe Feasibility

**Date anchor:** 2026-05-27 Australia/Melbourne  
**Generated:** 2026-05-27 21:03 AEST  
**Source scope:** This visible chat, the uploaded preservation prompt `Pasted text.txt`, and the previously generated package files available in `/mnt/data`.  
**Reliability note:** This is an accompanying narrative report. It does not replace the formal preservation package; it explains it in a more direct, human-readable way and adds the current packaging step.

---

## 1. Executive Summary

This conversation clarified a core technical direction for **Dominium**: the project should not be treated as a normal Unreal, UE6, Domino, Unity, or single-engine game. The user asked whether Dominium could be made on **Unreal Engine 6** instead of **Domino**, whether it could remain portable to Domino later, and whether any engine could support a much larger vision: a deterministic full-scale real solar system with procedurally recreated planets, terraforming, cut-and-fill terrain, player-built civilizations, megaprojects, designed machines/devices/factories, fog of war, sparse construction/destruction, collapsed simulation for unseen areas, client-assisted compute, single-player multi-universe gameplay, and an MMO-scale single persistent universe.

The central conclusion was that no commercial engine can provide this whole stack out of the box. Unreal Engine can be useful, especially as a renderer, editor, visual client, construction-preview tool, and asset pipeline. UE6 may eventually be useful if and when its public tooling becomes available. Domino may also become useful as a future frontend or runtime target. But the canonical game cannot live inside Unreal, UE6, Domino, or any other general-purpose commercial engine if the requirements remain deterministic, portable, persistent, sparse, fog-of-war-secure, and MMO-scale.

The durable architecture that emerged was:

```text
DominiumSim
+ DominiumWorldDB
+ DominiumServer
+ Unreal / UE6 / Domino / other engines as replaceable clients or adapters
```

The important shift was from asking **“Which engine should Dominium use?”** to asking **“What must Dominium itself be, independent of any renderer?”** The answer is that Dominium needs its own deterministic simulation core, sparse persistent world database, region-authoritative server layer, trust model, and simulation-level-of-detail system. Engines can render or host slices of that state, but should not define the authoritative universe.

The conversation also produced a practical near-term direction: do not wait for UE6. Build a deterministic headless prototype first. Keep gameplay rules, world state, resource accounting, factory logic, terrain edits, fog-of-war authority, and persistence outside Unreal-specific systems. Use Unreal only if it accelerates visualization and tooling. Keep a Domino adapter possible by making all engine integrations adapters around a portable core.

This package now contains the original preservation outputs plus this companion report and a verification/index file. The result is intended to let the user read, preserve, aggregate, and continue the conversation later without needing to reconstruct it from memory.

---

## 2. Coverage and Reliability

| Field | Assessment |
|---|---|
| Chat label | Dominium UE6, Domino, and Deterministic Universe Feasibility |
| Date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | Visible chat plus uploaded preservation prompt and generated files present in `/mnt/data` |
| Apparent access | Partial, but enough to preserve this visible discussion |
| Previously generated files available? | Yes; manifest, human report, registers, spec sheet, aggregator packet, audit, reader brief, bootstrap prompt, full combined report, and prior ZIP were present |
| Uploaded files available? | Yes; `Pasted text.txt` was present and contains the preservation-package instruction prompt |
| Contains future plans? | Yes |
| Contains decisions? | Yes, though several are assistant recommendations needing user confirmation before becoming formal project decisions |
| Contains unresolved questions? | Yes |
| Staleness risk | Medium to high for UE5/UE6 facts, engine roadmaps, Domino capabilities, and external-source claims |
| Extraction confidence | 3/5 for full project history; 4/5 for the visible conversation and generated artifacts |
| Safe for later aggregation? | Yes, with caveats |

### Limitations

This report does **not** claim to capture every older Dominium conversation. The accessible material shows that this is part of a broader Dominium project, but the complete historical project transcript is not visible here. Some previously uploaded files in the broader environment may have expired. Therefore, this package should be treated as a preservation package for **this chat’s visible UE6/Domino/deterministic-universe discussion**, not as the master Dominium specification.

The package also preserves assistant recommendations, but it does not treat every recommendation as a final user decision. The user clearly asked strategic questions and requested preservation. They did not explicitly ratify every architecture detail as a locked requirement. Future chats should preserve this distinction.

External factual claims about UE5, UE6, macOS/Windows/Linux support, Epic roadmaps, Unreal features, and third-party engines should be verified before being used as final project basis. The earlier answers used web citations, but this packaging step is primarily a preservation task, not a fresh technical verification pass.

---

## 3. Chronological Story of the Conversation

### 3.1 Initial UE6 and Domino question

The visible technical discussion began with a pasted answer about Unreal Engine 6. That pasted answer claimed that UE6 had been officially unveiled, that it would be a bleeding-edge architecture, that modern OS baselines would be necessary, and that UE6 public preview or production timelines would be years out. The user’s underlying question was not simply about operating systems. The real question was whether Dominium could be made on UE6 instead of Domino, and whether it could remain portable to Domino later.

The answer challenged the framing. It said that UE6 should not be treated as a present production target because public UE6 tooling and detailed requirements were not established in the visible sources. It recommended building in current Unreal technology where useful, likely UE5, while keeping the core independent enough to migrate to UE6 later if UE6 becomes useful. The answer also emphasized that portability to Domino would not happen automatically. A UE project cannot simply be exported into Domino. Portability would require a clean separation between Dominium’s permanent game logic and engine-specific rendering/runtime layers.

The first major architectural idea therefore became:

```text
DominiumCore = permanent game logic and state
Unreal / UE6 = possible first renderer/runtime
Domino = possible future renderer/runtime
```

This mattered because it rejected both extremes: do not wait for UE6 as a savior, but also do not discard Unreal if it can help as a visual and tooling layer.

### 3.2 Expansion into the full Dominium vision

The user then asked a much larger feasibility question. They described a deterministic game with a full-scale real solar system, fully recreated procedural planets, player-built civilizations, terraforming, cut-and-fill construction, megaprojects, designed machines/devices/factories, fog of war, sparse loading and simulation, collapsed unobserved areas, single-player multi-universe gameplay, an MMO single universe, client-shared compute, and low-latency high-FPS gameplay with millions of players.

The answer framed this as far beyond what UE5, UE6, Domino, or any ordinary game engine can do out of the box. It clarified that the problem is not merely rendering scale. The hard problems include deterministic simulation, server authority, interest management, persistence, database write throughput, world streaming, terrain edits, trust boundaries, fog-of-war secrecy, client cheating, factory graph scaling, state collapse/refinement, and network fanout.

The answer’s central position was:

```text
Unreal should not be the simulation engine.
Unreal can be the visual client and tooling layer.
The real Dominium engine is DominiumSim + DominiumWorldDB + DominiumServer.
```

### 3.3 Clarifying what is possible and impossible

The conversation separated the user’s large vision into solvable, partially solvable, and impossible-in-literal-form components.

A single persistent universe is possible if it means one shared identity, persistence layer, economy, map, and social/civilizational reality spread across many authoritative regions. Millions of players can exist in the same universe in this sense.

Millions of players in the same local area, mutually interacting at low latency and high FPS, is not realistic. The bottleneck is not only graphics; it is interest management, bandwidth, latency, simulation load, server authority, and database writes. The answer emphasized that the design must avoid making all players mutually relevant at once.

The conversation also clarified that full fidelity everywhere is not possible under compute constraints. The system must distinguish between:

```text
what exists
what is simulated
what is rendered
what is knowable
what is authoritative
```

This distinction became one of the most important conceptual tools from the chat. A distant planet can exist as procedural data and sparse edits without being actively simulated at per-object fidelity. A factory can exist and produce resources as a graph/rate model without every belt item being simulated. A hidden base can be authoritative on the server but unknown to the client. A region can be collapsed into macrostate and later refined when observed.

### 3.4 The proposed hybrid architecture

The answer proposed a layered architecture:

```text
DominiumSim
  deterministic fixed-step simulation
  fixed-point/integer math
  deterministic RNG
  factory graph simulation
  economy/civilization state
  terrain/material state model
  fog-of-war and sensing rules
  replay/hash/desync testing

DominiumWorldDB
  coordinate hierarchy
  planet/tile/chunk storage
  sparse voxel/SDF/terrain deltas
  construction operation logs
  event sourcing
  snapshots/checkpoints
  rollback/version migration

DominiumServer
  region authority
  interest management
  authority handoff
  anti-cheat validation
  simulation LOD scheduling
  global persistence/economy/social systems

DominiumClient_UE
  rendering
  animation/audio/UI
  construction preview
  terrain visualization
  debugging/editor tools

DominiumClient_Domino
  later adapter if Domino becomes an appropriate target
```

This architecture is the main technical carry-forward from the chat.

### 3.5 Preservation task and generated package

The user uploaded a long preservation prompt in `Pasted text.txt`. That prompt instructed the assistant to produce a maximum-fidelity chat preservation package, including a human-readable report, structured registers, context transfer packet, spec sheet, aggregator packet, self-audit, file export package, and final in-chat reader.

A set of files was then created in `/mnt/data`, including a manifest, human-readable report, context transfer packet, spec sheet, registers, aggregator packet, reader brief, verification/audit file, future chat bootstrap prompt, in-chat reader, full combined report, and a ZIP package.

The current user request asked for an accompanying human-readable detailed summary/report of the entire conversation and a new single ZIP containing all files. This companion report is the answer to that request, and the package was rebuilt with this file included.

---

## 4. Main Technical Conclusions

### 4.1 Unreal Engine is useful but should not own the game

The conversation did not reject Unreal. It rejected treating Unreal as the authoritative world engine for Dominium. Unreal can provide high-quality rendering, animation, editor workflows, UI, asset import, debugging views, and construction previews. It may be a practical first client for a complex simulation game because it gives a mature visual stack.

However, Unreal’s actor model, physics, replication, world partition, and asset system should not define canonical game truth. Dominium’s deterministic simulation, resource accounting, terrain edit state, machine logic, fog-of-war visibility, persistent economy, and server authority need to live outside Unreal-specific systems.

### 4.2 UE6 should not be waited on as a solution

The earlier pasted answer discussed UE6 as if it were a near-term design target. The assistant’s answer treated UE6 facts as uncertain and warned that public UE6 details were insufficient for production planning. The recommendation was not to stop work until UE6 arrives. Instead, build the portable core now and make future UE6 support an adapter/runtime question.

### 4.3 Domino portability requires architecture, not hope

Portability to Domino is possible only if the game is designed with engine separation from the start. If Dominium logic is built into Unreal Blueprints, Actors, Components, UMG, Materials, and Unreal replication, it will not be portable in a meaningful way. If the gameplay exists in a deterministic core with clear data schemas and adapter APIs, Domino can later become another frontend/runtime.

The key rule is:

```text
Unreal should render and host Dominium.
Unreal should not define Dominium.
```

### 4.4 Determinism requires a custom simulation layer

Strict determinism is incompatible with naive use of engine physics, variable tick ordering, nondeterministic floating-point behavior, and platform-dependent computation. Dominium needs fixed tick simulation, deterministic RNG, stable iteration order, fixed-point/integer math where needed, replay logs, and state hashes.

This is especially important because the user wants factories, machines, resource accounting, sparse world edits, and possibly multiplayer. If the same input log does not produce the same state hash, the system cannot support reliable replays, desync detection, deterministic collapse/refinement, or authoritative verification.

### 4.5 The solar system should be hierarchical, not one giant world coordinate space

Even if Unreal’s Large World Coordinates help with large rendered worlds, a full real-scale solar system should not be represented as one continuous Unreal physics space. Dominium should use a coordinate hierarchy:

```text
Solar system
  Planet/orbit
    Planet surface
      Region
        Chunk
          Local render bubble
```

The server/database can store precise absolute coordinates using deterministic integer/fixed-point representations. The client only renders a local bubble around the player or camera.

### 4.6 Terrain and construction must be sparse

Fully storing every planet at maximum resolution is infeasible. The correct model is procedural base data plus sparse player deltas. Unchanged areas come from seeds, real-world datasets where appropriate, and procedural generation. Edited areas store compressed operations, material deltas, ownership/permission metadata, and version history.

Terrain should not rely solely on Unreal Landscape if arbitrary cut/fill, tunnels, caves, overhangs, and megaproject excavation are central mechanics. A hybrid heightfield/SDF/sparse-voxel approach is more plausible.

### 4.7 Factories and machines should be graph simulations

Factories should not be simulated as arbitrary physics actors everywhere. They should be deterministic graphs of machines, storage, pipes, belts, routes, power, heat, and signals. Nearby systems can be animated at high fidelity; distant systems should collapse into rate/inventory/accounting models.

The resource accounting must remain exact or auditable, while the visual microstate can be reconstructed or approximated when observed.

### 4.8 Fog of war limits client-shared compute

The user wanted clients to share simulation load. The answer distinguished safe client assistance from unsafe authority. Clients can safely help with rendering, mesh generation, local prediction, build previews, pathfinding proposals, and non-authoritative local views. Clients should not authoritatively simulate hidden enemies, rare resources, production outputs, combat, market-affecting state, or secret world data.

The safe rule is:

```text
client proposes
server verifies
server commits
```

### 4.9 Single-universe MMO means shared persistence, not one local room

The chat concluded that a single persistent universe is possible in principle with partitioned regional authority, interest management, global persistence, and simulation LOD. But millions of players in one mutually interacting local space at high FPS and low latency is not a credible literal target. The design must use region boundaries, caps, time dilation, instancing or soft instancing, abstraction, and relevance filtering.

### 4.10 Simulation collapse/refinement must be a game rule

The idea of “collapsing” everything players cannot sense is viable only if it is designed into the rules from the beginning. A collapsed factory must still preserve resource totals. A collapsed civilization must still have population/economy/security/climate states. When observed, it must refine into a visible state that is consistent with the macrostate, even if the exact per-object microstate was not simulated the whole time.

This is a core mechanic, not an optimization that can be bolted on later.

---

## 5. Decisions, Recommendations, and Their Status

| ID | Decision / Recommendation | Status | Why it matters | Confidence | Label |
|---|---|---|---|---|---|
| D-01 | Do not wait for UE6 as the starting production engine | Assistant recommendation; not separately user-ratified | Avoids delaying work for unavailable/uncertain tooling | Medium-high | INFERENCE / UNVERIFIED external facts |
| D-02 | Use Unreal, if used, as renderer/client/tooling rather than canonical simulation | Strong recommendation | Prevents engine lock-in and nondeterministic world truth | High | INFERENCE |
| D-03 | Keep Dominium’s core simulation engine-independent | Strong recommendation aligned with user’s portability goal | Enables UE6/Domino/other adapters later | High | INFERENCE |
| D-04 | Build custom `DominiumSim + DominiumWorldDB + DominiumServer` | Strong recommendation | Required for determinism, persistence, fog of war, sparse world state, and MMO authority | High | INFERENCE |
| D-05 | Do not trust clients with persistent MMO authority | Strong recommendation | Protects anti-cheat, economy, secrets, and fog of war | High | INFERENCE |
| D-06 | Treat millions in one local space as infeasible; design one persistent universe instead | Strong recommendation | Prevents impossible networking/performance target | High | INFERENCE |
| D-07 | Start with a deterministic headless MVP | Strong recommendation | Proves the hardest invariant before renderer work dominates | High | INFERENCE |
| D-08 | Preserve all generated reports and package files for future aggregation | User requested and assistant executed | Maintains continuity across chats | High | FACT |

Important caveat: these are mostly preserved as **recommendations and working conclusions**, not as final locked product requirements. A future planning pass should explicitly ask which items become formal Dominium requirements.

---

## 6. What Was Put Off for Later

The conversation deferred several necessary decisions and implementation details:

1. **Domino’s exact role.** The chat did not define what Domino can currently do, what platforms it targets, whether it supports necessary rendering or scripting features, or whether it is meant to be a primary runtime or later adapter.

2. **Final engine/client choice.** Unreal was recommended as a plausible first visual client, but the project has not formally committed to Unreal as the first frontend.

3. **UE6 verification.** Public UE6 details, release timing, feature set, and system requirements need current verification before they influence planning.

4. **Deterministic math design.** The chat recommended fixed-point/integer deterministic math but did not specify bit widths, units, overflow rules, coordinate encoding, or numerical libraries.

5. **Planet data model.** The chat proposed procedural base data plus sparse edits but did not decide the exact terrain representation: heightfield, voxel, SDF, hybrid, or another system.

6. **Collapse/refine rules.** The concept was discussed, but exact macrostate variables, refinement constraints, and fairness rules remain open.

7. **Networking architecture.** The chat described server authority, region partitioning, and interest management, but did not specify protocols, tick rates, authority handoff mechanics, database layout, or failure recovery.

8. **MMO scale target.** The chat separated “single universe” from “millions in one local space,” but actual concurrency targets and performance budgets remain undefined.

9. **Database/persistence system.** Event sourcing, snapshots, sparse chunk diffs, rollback, and audit trails were proposed, but no database technology or schema was chosen.

10. **Security and abuse controls.** Lag machines, player-made computation, economy exploits, griefing, and client tampering were identified, but no concrete rule limits were designed.

11. **Prototype scope.** The recommended next action is a deterministic `DominiumSim` MVP, but its exact acceptance tests still need to be defined.

---

## 7. Engines, Systems, and Ideas to Copy or Study

The conversation suggested copying ideas from multiple systems rather than trying to combine full engines at runtime.

| Reference | What to study or copy | What not to assume |
|---|---|---|
| Unreal Engine 5 / future UE6 | Rendering, editor, animation, asset tools, client frontend, construction visualization | Do not assume it can be the deterministic MMO universe engine |
| Domino | Possible future frontend/runtime adapter | Do not assume portability unless core/adapter separation is built now |
| Factorio | Deterministic factory simulation, replay discipline, desync detection, graph-like production systems | Its lockstep model does not directly solve MMO authority at planetary scale |
| EVE Online | Single-shard social/economic world, regional load handling, time dilation philosophy | Does not solve fully destructible planets or deterministic factory terraforming |
| Cesium / 3D Tiles | Massive geospatial streaming and hierarchical tiles | Not a game simulation solution by itself |
| UNIGINE / Outerra-like systems | Planet-scale precision and world rendering ideas | Does not solve the entire MMO simulation and economy stack |
| Unity DOTS / Bevy / ECS systems | Data-oriented design and parallel simulation ideas | Not enough by themselves for deterministic persistent planetary MMO |
| SpaceEngine-like procedural universe systems | Astronomical scale, procedural generation, LOD concepts | Rendering/exploration scale is not the same as editable persistent multiplayer simulation |

The strategic recommendation was to copy architectural ideas and algorithms, not to bolt multiple full engines together.

---

## 8. Near-Term Recommended Roadmap

### Phase 1 — Deterministic headless core

Build a small command-driven simulation with fixed ticks, deterministic RNG, stable iteration order, state hashing, replay logs, and identical results across supported platforms.

Suggested MVP target from the earlier report:

```text
10,000 machines
1,000 terrain chunks
100 players as command streams
fixed tick
state hash every tick
replay from command log
same result on Windows/Linux/macOS
```

The exact numbers are candidates, not final requirements.

### Phase 2 — Sparse planet region

Create one procedural planet region with chunked terrain, editable material state, construction placement, save/load, and sparse deltas. Render it in a simple viewer or Unreal client.

### Phase 3 — Collapse/refine simulation

Implement active vs collapsed factories and settlements. Test whether resource accounting remains consistent when regions sleep, fast-forward, and wake.

### Phase 4 — Server authority and fog of war

Add server-owned hidden state, client visibility filtering, sensor rules, interest management, and anti-cheat validation.

### Phase 5 — Region authority and persistence

Implement multiple authoritative regions, handoff, persistent chunk database, event logs, snapshots, and graceful overload behavior.

### Phase 6 — MMO-scale testing

Scale gradually: local deterministic tests, then simulated clients, then multiple regions, then stress tests. Do not design around “millions in one room.” Design around load-bounded regions in a single persistent universe.

---

## 9. Artifact Ledger and File Package

The package contains the previously created preservation files plus this companion report and verification index.

| Artifact | Purpose | Notes |
|---|---|---|
| `00_manifest.md` | Overview of files and package status | Updated to include the companion report and verification file |
| `01_human_readable_report.md` | Main formal preservation report | Sections 0–16 from the original preservation task |
| `02_context_transfer_packet.md` | Handoff for a future chat | Use when continuing work elsewhere |
| `03_spec_sheet.yaml` | Structured YAML-style spec sheet | For later aggregation into a master project spec book |
| `04_registers.md` | Workstreams, decisions, tasks, constraints, risks, verification queue | Use for project tracking and cross-chat merging |
| `05_aggregator_packet.md` | Compact merge packet | For a central aggregation chat |
| `06_reader_brief.md` | Short human-readable brief | Use for fast reacquaintance |
| `07_verification_and_audit.md` | Audit and verification needs | Use before turning recommendations into formal requirements |
| `08_future_chat_bootstrap_prompt.md` | Prompt for starting a future chat | Paste with the context transfer packet |
| `09_in_chat_reader.md` | In-chat navigation guide | Use for asking follow-up questions inside this chat |
| `10_accompanying_human_readable_detailed_summary_and_report.md` | This file | Companion summary/report requested in the latest user turn |
| `11_package_verification_and_file_index.md` | Created during this request | Lists files, sizes, checksums, and inclusion status |
| `FULL_COMBINED_REPORT.md` | Combined report generated earlier | Longer archive of the formal report and related sections |
| `handoff_package.zip` | Prior ZIP package | Preserved as a prior artifact inside the new complete package |
| `Pasted text.txt` | Uploaded preservation prompt | Source artifact defining the preservation task |

---

## 10. Main Open Questions

1. **What exactly is Domino?** The chat assumes Domino may be a future runtime or adapter, but its actual capabilities and constraints need definition.

2. **Should Unreal be the first visual client?** It is recommended as plausible, not formally chosen.

3. **What is the exact deterministic MVP?** The project needs a concrete first prototype specification.

4. **What numerical model should Dominium use?** Fixed-point/integer math is recommended, but the coordinate and units system remains open.

5. **How should collapsed simulation preserve fairness and accounting?** Exact rules need design.

6. **What is the terrain representation?** Sparse voxels, SDFs, heightfields, or hybrid systems remain to be tested.

7. **What MMO scale is actually targeted?** “Millions in universe” needs bounded definitions: concurrent, daily active, region-local, visible, simulated, and interactable.

8. **What can clients safely compute?** A trust matrix should be formalized.

9. **How should the database handle persistent edits?** Event logs, snapshots, diffs, compression, and rollback need design.

10. **Which earlier assistant statements require re-verification?** UE6, UE5, platform requirements, and engine feature claims should be checked before formal adoption.

---

## 11. Risks and Failure Modes

| Risk | Consequence | Mitigation |
|---|---|---|
| Treating Unreal as the whole game | Engine lock-in, nondeterminism, hard Domino migration | Keep canonical state in DominiumSim/WorldDB/Server |
| Waiting for UE6 | Delayed progress based on uncertain tooling | Prototype deterministic core now |
| Trusting clients with MMO authority | Cheating, economy corruption, fog-of-war leaks | Server verifies and commits authoritative state |
| Trying to simulate full fidelity everywhere | Impossible compute and bandwidth costs | Use simulation LOD and collapse/refine rules |
| Designing player machines without limits | Lag weapons and unbounded computation | Add operation, graph, power, bandwidth, and tick-budget limits |
| Treating recommendations as final decisions | Future confusion and bad aggregation | Preserve status labels and require user confirmation |
| Forgetting artifact provenance | Misuse of stale or partial reports | Preserve manifest, verification, and source scope labels |
| Relying on stale UE6 claims | Wrong platform and roadmap assumptions | Verify before final planning |
| Confusing single universe with single local space | Impossible networking/performance target | Define universe, region, visibility, and interaction scopes separately |

---

## 12. What a Future Assistant Must Not Get Wrong

A future assistant should not reduce this chat to “use Unreal” or “do not use Unreal.” The actual conclusion is more specific: use Unreal only if it helps as a replaceable client/tooling layer, while keeping the authoritative deterministic game outside it.

A future assistant should also not claim that UE6 solves the project. The chat treated UE6 as uncertain and not currently sufficient as a foundation for planning.

A future assistant should not assume Domino portability happens automatically. It only happens if Dominium is architected around a portable core and engine adapters.

A future assistant should preserve the distinction between a single persistent universe and a single local mutually interacting space. The first is plausible with partitioning. The second is not plausible at the scale of millions with low latency and high FPS.

A future assistant should not treat every assistant suggestion as a user-approved final decision. Many items are strong recommendations that need user confirmation before entering the formal spec.

---

## 13. Best Next Action

The best next action is:

```text
Define the first deterministic DominiumSim prototype in detail.
```

That should produce a small, testable specification covering:

- simulation tick rate,
- command input format,
- deterministic RNG,
- fixed-point/integer math rules,
- state hashing,
- replay logs,
- machine/factory graph model,
- terrain chunk edit model,
- save/load format,
- cross-platform determinism tests,
- pass/fail acceptance criteria.

This should happen before deep Unreal/UE6/Domino integration work, because it validates the hardest architectural invariant: whether Dominium can have a portable deterministic canonical simulation at all.

---

## 14. Compact Carry-Forward Summary

Dominium should be treated as a custom deterministic simulation and persistent-world system with replaceable visual clients. Unreal/UE5/UE6 can help render and edit the world, but should not own canonical game state. Domino may be a later frontend or runtime, but portability requires deliberate core/adapter separation from the beginning. No commercial engine currently solves the full target: deterministic real-scale solar system, sparse procedural planets, terrain editing, machines/factories, fog of war, client compute, and MMO-scale single-universe persistence.

The permanent architecture is:

```text
DominiumSim + DominiumWorldDB + DominiumServer
```

The renderer/client layer can be:

```text
Unreal now, UE6 later if useful, Domino later if useful, or other adapters
```

The most important rule is that the game must separate existence, simulation, rendering, knowability, and authority. Distant or unseen areas can exist in the database without being rendered or fully simulated. Factories can collapse into exact accounting graphs or rate models. Hidden enemy state can remain authoritative on the server without being sent to clients. Players can help compute visuals or proposals, but clients must not authoritatively decide MMO-persistent outcomes.

The next project step is to define and build a deterministic headless `DominiumSim` MVP with replay, state hashes, fixed ticks, deterministic math, and a small factory/terrain model. Only after that should renderer choice dominate the work.

---

## 15. Specific Follow-Up Questions to Ask Next

### Architecture

1. Define the first deterministic DominiumSim prototype in detail.
2. What belongs in DominiumSim, DominiumWorldDB, DominiumServer, and DominiumClient?
3. What is the exact API boundary between the simulation core and Unreal/Domino adapters?

### Determinism

4. What fixed-point or integer coordinate system should Dominium use?
5. How should state hashing and replay logs work?
6. What operations must be forbidden or wrapped to preserve determinism?

### Planet and terrain

7. Should Dominium use sparse voxels, SDF chunks, heightfields, or a hybrid for planets?
8. How should cut/fill operations store material conservation and ownership?
9. How should a real-scale solar system coordinate hierarchy be encoded?

### Factories and machines

10. How should player-designed machines be represented as deterministic graphs?
11. What limits prevent player-made lag machines or general-computation exploits?
12. How should active and collapsed factories reconcile state?

### Networking and MMO scale

13. What is a realistic first multiplayer target for Dominium?
14. How should fog of war and client interest filtering be designed?
15. What computations can clients safely assist with?
16. How should server region authority and handoff work?

### Project preservation and spec book

17. Which recommendations from this chat should become formal Dominium requirements?
18. Which parts should remain background context rather than hard requirements?
19. How should this package be merged with other Dominium preservation reports?
20. What external facts should be verified before final architecture planning?

---

## 16. Final Status of This Companion Report

This companion report was created to make the package easier to read without opening the full formal preservation report first. It preserves the entire visible conversation at a high but human-readable level, adds the latest packaging request, and explains how to use the generated files.

The report is safe to carry forward into future Dominium planning with these caveats:

- It is not a full master project spec.
- It does not include every older Dominium chat.
- It relies on the visible conversation and existing package files.
- It distinguishes assistant recommendations from user-final decisions.
- It marks UE6/engine facts as needing verification before formal use.

