# COMPLETE CHAT PRESERVATION REPORT — Domino/Dominium Engine Baseline, Architecture, and Feasibility

## 0. Coverage and Reliability Assessment

| Field | Assessment |
|---|---|
| Chat label | Domino/Dominium Engine Baseline, Architecture, and Feasibility |
| Date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | This chat only unless labelled PROJECT-CONTEXT |
| Apparent access | Partial but broad |
| Previously generated files available? | No previously generated preservation files were visible before this task |
| Uploaded files or artifacts present? | Yes — `Pasted text.txt`, containing the preservation/export instructions |
| Contains future plans? | Yes |
| Contains decisions? | Yes, mostly tentative/strategic decisions and sequencing decisions |
| Contains pending tasks? | Yes |
| Contains unresolved questions? | Yes |
| Staleness risk | Medium |
| Extraction confidence | 4/5 |
| Safe for later aggregation? | Yes, with caveats |
| Main limitations | I can access the visible chat context and files fetched during the chat, but I cannot independently verify the user's local `C:/Inbox/...` paths, local build outputs, CTest results, or generated evidence files unless those are uploaded. Some repo facts may have changed after they were fetched. |

The uploaded preservation prompt requires a maximum-fidelity human-readable handoff, structured registers, spec sheet, aggregator packet, self-audit, and downloadable file package for this chat. That prompt itself is an artifact of this chat and should be preserved. Source: fileciteturn44file0

Limitations in plain language: this report reconstructs the conversation from the visible transcript and from repository files that were fetched during the chat. It does not prove that the local commands the user reported were actually run, because those local logs were pasted as claims rather than uploaded as verifiable build artifacts. It also does not claim that the full GitHub repository was exhaustively audited. The report is therefore suitable as a high-fidelity chat handoff, not as a final technical audit of the current repo.

## 1. One-Page Orientation

This chat was about the architecture, feasibility, state, and future direction of the Domino engine and Dominium game. The user wanted to understand what the project is, whether the engine exists in a meaningful sense, whether it is ready to support a game, how it can become portable and modular enough to be reused for multiple games or even CAD-like tools, and how to sequence the work without being overwhelmed by the enormous scope.

The conversation began with a request to read the project docs and GitHub repository and describe the total project, especially the engine and game. The answer framed Domino as the deterministic simulation substrate, Dominium as the rule/game layer, and XStack/governance as the proof/audit discipline. Repository CMake files were fetched showing real `domino_engine` and `dominium_game` targets, with substantial engine and game source composition. Later, the user pushed beyond description into strategy: how to make the engine better, how to make it do more for less, how to support many hardware/software targets, and how to build something durable for decades.

A major theme emerged: Domino should not try to become a conventional monolithic game engine. It should become a deterministic, contract-driven, capability-negotiated simulation kernel. Dominium should be one product/game built on top, not the reason the engine exists. The engine should define mechanisms such as Work IR, Access IR, scheduling, replay, domains, fields, capabilities, registries, and law gates. The game should define meaning: construction, life, agents, economy, governance, survival, war, CAD-like design, terraforming, and so on. Client/rendering should be projection and intent only. Server/domain authority should own authoritative multiplayer truth.

The user repeatedly emphasized portability, modularity, extensibility, future-proofing, and reuse. The recommendations converged on stable public contracts with replaceable implementations: semantic contracts version meaning; schemas version shape; capabilities define power; lockfiles define exact composition; proof/replay validates actual behavior. Directory layout was discussed, but the conclusion was that folder names alone do not create modularity. Real modularity comes from public/private boundaries, stable APIs, provider interfaces, explicit ownership, deterministic artifact formats, and compatibility tests.

Another major branch concerned building and destruction. The user asked whether the game would need to give players a full CAD suite. The answer proposed a layered authoring model: ordinary players use templates, snapping, assisted intent, or accessible UI; advanced users and developers can use CAD-grade design tools. The canonical artifact should be a design/blueprint/assembly/process object, independent of the UI surface used to create it. When the user asked about voxels versus B-Rep/CSG/NURBS, the conclusion was a hybrid: CSG/feature graphs for authoring, B-Rep for canonical solids, NURBS for advanced curved faces, meshes as derived render/collision proxies, and voxels/SDF/fields only for terrain, mining, fluids, debris, and sparse damage approximation.

The feasibility discussion became the most important practical correction. Initially the project was described as having a working deterministic foundation but not a finished game engine. The user then pasted a more precise local assessment: the repo builds real engine/game/client/server targets and some targeted tests pass, but the client advertises `support_claim_playable=false`, the playtest path is blocked, server Python startup has circular import issues, baseline bundle/session paths are not hardened, and a time-anchor policy registry is missing or invalid. The final corrected sequencing was: do not start with destruction, CAD, economy, agents, or broad gameplay. First complete **Milestone 0: Make the baseline path honest** — one canonical repo-local playable baseline command must pass strict validation. Only then should a tiny builder/destruction lab begin.

The final design vision explored a deterministic full-scale solar-system/civilization game. The answer rejected “full fidelity everywhere” as impossible. The viable design is a multi-resolution universe: rail-orbit solar systems, hierarchical planet domains, sparse terrain overlays, collapsed civilization capsules, fog-of-war epistemic filtering, sparse construction/destruction, domain-sharded multiplayer authority, and proof-carrying client compute only where safe. Unreal was judged useful for rendering/editor-like presentation but not sufficient as the authoritative deterministic substrate for this project.

Future relevance: this chat should feed several chapters of a master project spec book: engine/game boundary, deterministic execution, portability and modularity doctrine, baseline milestone sequencing, CAD/build/destruction model, sparse full-scale universe architecture, MMO/sharding constraints, and project feasibility discipline. The most important thing to preserve is the corrected sequencing: **baseline first, vertical slice second, grand systems later**.

## 2. The Story of the Conversation

### 2.1 Project description and first architecture framing

The chat began with the user asking for a total description of the project by reading the docs and GitHub repository. Repository files were inspected, especially `engine/CMakeLists.txt` and `game/CMakeLists.txt`. This established that the repo contains real build targets rather than only planning notes: `domino_engine` is a static engine library and `dominium_game` is a static game library linking against it. The early report described Dominium as a deterministic, law-governed, multi-scale reality simulation game and product stack. The distinction between Domino and Dominium became foundational: Domino is the deterministic substrate; Dominium is the game/rules layer.

The report also emphasized that the project is not merely “Minecraft but real life.” It is more accurately a simulation OS or deterministic world runtime, with engine, game, client, server, launcher, setup, tools, and governance layers.

### 2.2 Learning from historical engines and making Domino better

The user then pasted a large analysis of revolutionary game engines — SCUMM, Doom, Quake, Unreal, RenderWare, Source, Havok, CryEngine, RAGE/Euphoria, Frostbite, Unity, id Tech 5, UE4, UE5, Decima — and asked what else Domino could do to be better, more efficient, portable, powerful, and durable. The response identified the deeper lessons: visibility/world representation, data-driven content, physics as gameplay, large-world streaming, material realism, and toolchains as the real engine.

The conversation then connected those lessons to Domino. The key recommendation was to virtualize everything expensive: geometry, textures, terrain, agents, economy, history, AI, physics, networking, and tools. Domino should maintain active sets rather than full world state in memory; it should use event queues instead of global scans; and it should use sufficient statistics and capsules for collapsed domains. This aligned with the repo’s documented deterministic execution model and invariants.

### 2.3 Live repo correction: more work exists than previously discussed

The user then clarified that the live repo had much more implemented work than the earlier description captured. New docs and code were fetched: Status Now, MVP Scope Lock, Extension Map, Repo Review 3, Frozen Invariants, AppShell Constitution, Capability Negotiation Constitution, Pack Verification Pipeline, execution IR source files, registry compile docs, determinism envelope report, canon conformance report, and more.

The conclusion changed: the project already had more infrastructure than the generic future plan assumed. The recommendation shifted from “invent the architecture” to “converge the architecture.” The answer proposed that Dominium should become a **contract-compiled simulation platform**: contracts → registries → compiled locks → capabilities → Work IR → deterministic runtime → proof/replay → product shells.

The main practical recommendations were validation unification, extension classification, provider descriptors, registry bundle grouping, deterministic scheduler/backend optimization, generated docs, platform matrix, pack doctor/mod templates, and AuditX triage.

### 2.4 CAD, building, and player freedom

The user then raised the problem of construction: if players can build all items, machines, and structures, does the game need a CAD suite? The answer proposed layered authoring. Ordinary players should not be forced to use CAD. Instead, the same canonical design artifact can be produced from different surfaces: simple templates, assisted snapping, parametric objects, constraint editing, full CAD, or generative/programmatic design.

The answer also rejected recipes/tech trees as the default gameplay model. Instead, it proposed affordances and constraints: materials, tools, machines, capabilities, processes, authority, environment, time, and energy determine what can be made. Recipes, tech trees, levels, or certifications can exist as optional mod/game-mode layers via packs, law, profiles, and capabilities.

### 2.5 Portability, modularity, and future-proofing

The user then emphasized that all code should be portable, modular, extensible, and reusable for different games or entirely different engine projects. The response gave a broad engineering doctrine: stable outside, flexible inside. Stable public APIs, semantic contracts, schema versioning, capability negotiation, provider interfaces, opaque handles, canonical serialization, golden replay corpora, and strict public/private boundaries matter more than directory aesthetics.

A long-term directory model was suggested, but with the caveat that the current repo’s v0.0.0 state should not be disrupted by broad restructuring. The repo should be organized by authority and ownership: contracts define what may exist; engine implements reusable mechanisms; runtime adapts host/platform/product shells; game defines Dominium meaning; content defines packs/profiles; products expose binaries; tools inspect/compile/validate/migrate; tests prove contracts; docs explain contracts.

### 2.6 B-Rep / CSG / NURBS versus voxels

The user then focused on construction/destruction representation and argued that Dual Universe got it wrong by going voxel-based. The answer agreed with the direction but recommended a hybrid. Voxel-first is useful for terrain, mining, craters, debris, and volumetric fields, but poor for precise machines, CAD semantics, thin structures, interfaces, mass properties, and network replication. The preferred model was CSG/feature graphs for editable authoring, B-Rep for canonical validated solids, NURBS/B-splines for advanced curved surfaces, meshes only as derived proxies, and sparse voxels/SDFs for terrain/damage/fluid/debris approximations. Destruction should be tiered and sparse rather than global geometry recomputation.

### 2.7 Engine readiness and feasibility anxiety

The user expressed worry that the project might be impossible and that they did not know how to write engines. The initial answer said the project has a working deterministic substrate but not a finished game engine. Then the user pasted a more precise local assessment: targeted build and CTest slices had passed, but the client still reports `support_claim_playable=false`; the local playtest path is blocked; Python server entrypoint has circular import issues; session creation defaults to a lab bundle; the MVP bundle path refuses; and the baseline universe verifier fails because the time-anchor policy registry is missing or invalid.

This corrected the plan. The final sequencing became: first **Milestone 0: Make the baseline path honest**. That means fixing server/runtime circular import, CLI forwarding, `session_create -> session_boot`, missing time-anchor policy registry, and making the strict local playtest validator pass. Only after that should the builder/destruction lab begin.

### 2.8 Full-scale universe architecture and Unreal comparison

The user then described the full dream: deterministic procedural/authored hybrid solar systems, fully recreated/customizable planets, civilizations, terraforming, terrain cut/fill, megaprojects, designed machines/factories, fog of war, collapsed simulation for unobserved areas, MMO persistent universe, client-shared compute, sparse construction/destruction, and low latency/high FPS at scale. The answer said full scale is possible only if full fidelity everywhere is abandoned. The architecture should use domains, collapsed capsules, sparse overlays, planet tiles, event-driven processes, fog as epistemic filtering, domain sharding, and proof-carrying client delegation.

Unreal was judged incapable of the full authoritative simulation model out-of-the-box. It can help as a rendering/editor/client shell but not as the deterministic substrate for this architecture.

### 2.9 Preservation request

The final user action uploaded `Pasted text.txt`, a detailed instruction prompt requiring a full preservation report, structured registers, spec sheet, aggregator packet, self-audit, and downloadable file package for this chat. That request is the current task.

## 3. Main Topics Discussed

### Topic 1 — Domino engine versus Dominium game

The central architecture distinction was that Domino should be a reusable deterministic simulation substrate, while Dominium should be one game/product layer built on it. This came up immediately when the user asked for a total description of the project. It mattered because the user wants the code to be reusable for future games and possibly other engine projects.

The conclusion was that engine and game responsibilities must stay separated. Engine owns deterministic mechanisms, execution, storage, domains, fields, replay, capabilities, and law gates. Game owns meanings and rules such as construction, life, agents, economy, governance, survival, and war. Client/render is projection and intent only; server owns multiplayer authority. This aligns with the canonical constitution fetched later in the chat. fileciteturn40file0L3-L3

Uncertainty: the repo has many modules and some historical/legacy surfaces, so exact implementation maturity varies by subsystem. The distinction should remain a formal requirement in a master spec.

### Topic 2 — Deterministic execution and proof

The conversation repeatedly returned to determinism. The project’s value depends on identical inputs producing identical outputs, replay equivalence, stable commit ordering, named RNG streams, explicit Work IR/Access IR, and no hidden global scans. The assistant inspected execution model docs and source files such as task graph, access set, scheduler, and work queue.

The visible conclusion was that the engine has real deterministic substrate pieces, but these must be hardened through small playable slices and proof/replay tests. Determinism is not only a mathematical preference; it enables multiplayer authority, replay, audit, mod compatibility, and long-term artifact preservation.

Uncertainty: the full determinism envelope across all current modules was not independently re-run in this chat. User-supplied local validation results should be preserved but verified before being used as audit proof.

### Topic 3 — Engine improvement strategy

When the user asked how to make the engine better and more efficient, the answer was “virtualize everything expensive.” Domino should do more for less by activating only what matters, using event queues, collapsed capsules, sufficient statistics, budgeted fidelity, and provider backends. Large worlds should not be simulated by ticking every entity. Instead, the engine should preserve truth through sparse representations and deterministic expansion.

The conclusion was that future work should build active-set runtime, capsule/refinement contracts, compatibility edition matrix, golden replay corpus, and toolchain-first authoring. Later, after reading live repo docs, this plan was tightened into “contract-compiled simulation platform.”

### Topic 4 — Live repo maturity and convergence

The user corrected that the live repo had more work than the early answer acknowledged. After reading more docs and code, the plan shifted from speculative architecture to convergence. The repo already had MVP scope locks, AppShell, capability negotiation, pack verification, semantic contracts, frozen invariants, registry compile, determinism envelope reporting, and canon conformance reports. The answer recommended fewer stronger contracts, validation unification, provider descriptors, registry bundles, generated docs, and a pack doctor.

This topic matters because it prevents wasted work. The project should not add broad new systems before stabilizing existing baseline paths.

### Topic 5 — CAD, construction, and player freedom

The user wanted players to build anything but also enjoy the game without skill. The solution was layered authoring. Ordinary players should use simple templates, assisted snapping, intent-based building, or accessibility-first controls. Advanced players and developers can use a full CAD suite. All authoring surfaces compile into a canonical design artifact.

The conclusion was that the engine should support CAD-like design without requiring CAD-like gameplay. Recipes and tech trees should not be default mechanics; they should be optional pack/law/profile/capability layers for modders and game modes.

### Topic 6 — Geometry representation for building/destruction

The user suggested B-Rep, CSG, NURBS, or hybrid rather than voxels. The recommendation was hybrid: CSG/feature graphs for authoring, B-Rep for canonical solids, NURBS for advanced curved faces, meshes as derived render/collision proxies, voxels/SDFs for terrain/mining/damage/fluid/debris. Destruction should be tiered and sparse.

This connects to future work because a construction/destruction game cannot rely on one universal representation. Different domains need different data structures.

### Topic 7 — Portability, modularity, and future-proofing

The user wanted code reusable across games and engine projects. The answer emphasized stable public contracts, opaque handles, C ABI-like boundaries, public/private header discipline, provider interfaces, schema/semantic-contract separation, canonical serialization, artifact versioning, and golden compatibility corpora. Directory structure matters, but enforcement matters more.

The conclusion was “stable at the boundary, ruthless inside.” Internal implementation can be rewritten if public contracts, tests, formats, and migration/refusal behavior hold.

### Topic 8 — Baseline readiness and Milestone 0

This became the practical pivot. The user pasted evidence that the repo has compiled targets and some passing tests but lacks a finished playable path. The final decision was that before game features, the team must create one canonical repo-local playable baseline command that passes strict validation.

This matters because it turns overwhelming ambition into concrete blocker-fixing: circular imports, CLI forwarding, session materialization, bundle mismatch, missing time-anchor registry, and strict playtest validator.

### Topic 9 — Full-scale solar-system/civilization/MMO architecture

The user described the full ambition. The answer stated that full-scale is only possible with collapsed multi-resolution simulation. Domains, fields, sparse overlays, planet tiles, collapsed civilization capsules, fog-of-war epistemics, sharding, and proof-carrying delegated compute are required. Unreal can help with rendering/editor surfaces but not with this deterministic authoritative simulation model.

Uncertainty: this remains strategic architecture, not an implemented decision.

## 4. What We Were Trying to Achieve

### 4.1 Explicit Goals

The user explicitly wanted to understand and preserve:
- what the project is;
- whether Domino has a working engine;
- whether Dominium can start game work;
- how to make the engine portable, modular, reusable, and future-proof;
- how to support full-scale solar systems, planets, construction, destruction, and civilizations;
- how to avoid requiring recipes/tech trees in normal gameplay;
- how to support CAD-level freedom without overwhelming players;
- how to sequence the project so it is not impossible;
- how to preserve this chat for future aggregation.

These goals mattered because the project scope is extremely large and the user was concerned about feasibility and implementation ability.

### 4.2 Inferred Goals

INFERENCE: the user wants a development doctrine that makes the project less emotionally and technically overwhelming. The repeated questions about impossibility, not knowing how to write engines, and needing future-proof structure indicate a need for practical sequencing as much as architecture.

INFERENCE: the user wants the engine to outlive Dominium and serve as a platform for multiple future projects.

### 4.3 Goals That Changed Over Time

The conversation moved from broad architecture description to implementation readiness. Early answers focused on what the project could be and how to architect it. Later, the user's pasted local assessment forced a stricter current-state view: the immediate goal is not more game design; it is making the baseline path honest.

The goal also shifted from “support everything” to “support everything through sparse, collapsed, capability-gated, provider-based architecture.”

### 4.4 Goals Still Unresolved

Unresolved goals include:
- exact Milestone 0 implementation plan at code level;
- verification of local build/test claims;
- exact canonical playtest command name and behavior;
- exact design artifact schema for CAD/building;
- exact geometry kernel approach and library/provider strategy;
- exact sharding and client-compute proof model;
- whether Unreal will be used at all as a client/editor shell.

## 5. Decisions Made and Why

| ID | Decision | Status | Why it mattered | Confidence | Label |
|---|---|---|---|---|---|
| DECISION-01 | Domino is the reusable deterministic substrate; Dominium is one game layer | Accepted direction | Prevents Dominium-specific coupling in engine | High | FACT / accepted framing |
| DECISION-02 | Do not treat the engine as a finished playable game engine | Accepted after correction | Avoids premature feature work | High | FACT / user-corrected |
| DECISION-03 | Milestone 0 must precede builder/destruction lab | Accepted by user framing | Fixes baseline blockers first | High | FACT / accepted sequencing |
| DECISION-04 | Use contract/capability/registry/proof architecture for extensibility | Strong recommended direction, broadly accepted | Enables modularity, modding, compatibility | Medium-high | INFERENCE |
| DECISION-05 | CAD should be supported as an advanced/tooling surface, not required normal gameplay | Strong recommended direction | Balances freedom and accessibility | Medium-high | INFERENCE |
| DECISION-06 | Avoid recipes/tech trees as default gameplay; support them via packs/law/capabilities | User-stated preference + assistant architecture | Preserves freedom while enabling modded modes | High | FACT |
| DECISION-07 | Use hybrid CSG/B-Rep/NURBS/mesh/SDF approach, not voxel-first | Assistant recommendation, not explicitly rejected | Supports precise building/destruction | Medium | INFERENCE |
| DECISION-08 | Unreal is not sufficient as authoritative simulation substrate | Assistant conclusion | Clarifies engine strategy | Medium | INFERENCE / external facts stale risk |
| DECISION-09 | Full-scale universe must be multi-resolution and collapsed, not full-fidelity everywhere | Strong strategic conclusion | Makes project feasible | High | INFERENCE |
| DECISION-10 | Avoid broad restructuring before v0.0.0/baseline hardening | Based on repo docs and assistant recommendation | Prevents breaking fragile paths | High | FACT / recommendation |

### DECISION-01 — Domino as substrate, Dominium as game

The conversation consistently preserved this boundary. The engine should define deterministic mechanisms; the game defines rules and meaning. This affects directory layout, APIs, naming, dependencies, modding, and future reuse. It would be revisited only if the project intentionally stopped trying to make Domino reusable, which contradicts the user's stated goal.

### DECISION-02 — Engine exists, but playable game engine does not

This was corrected over time. Earlier descriptions could have sounded too optimistic. The user's pasted local assessment tightened it: compiled substrate exists, targeted tests may pass, but the client itself advertises no playable support. This affects all next steps.

### DECISION-03 — Milestone 0 first

The user explicitly accepted the correction that before a builder/destruction lab, the first deliverable should be one canonical repo-local playable baseline command passing strict validation. This is the most important sequencing decision in the chat.

### DECISION-04 — Contract-compiled simulation platform

This was a recommended architectural conclusion after reading live repo docs. It is not a single user-typed acceptance sentence, but the user continued building on it. It should be treated as a strong strategic direction, not a final immutable spec.

### DECISION-05 — CAD-capable, not CAD-required

The user wanted full freedom and low-skill enjoyment. The answer resolved this with layered authoring. This should become a future spec requirement: every advanced design surface should compile to a canonical artifact, but ordinary users should have assisted modes.

### DECISION-06 — No default recipes/tech trees/levels

The user explicitly stated they do not want usual gameplay to rely on technology trees, recipes, or experience levels, while wanting the engine to support those for mods/game modes. This is a strong product preference.

### DECISION-07 — Geometry hybrid

The assistant recommended a hybrid representation. The user did not explicitly confirm after that response in the visible transcript. Treat as a strong recommendation to preserve, not a final decision.

### DECISION-08 — Unreal as possible shell, not authoritative core

The answer said Unreal can help with rendering/editor/client presentation but cannot solve the deterministic full universe architecture out-of-the-box. This is a strategic conclusion and should be verified if the project later seriously considers Unreal integration.

### DECISION-09 — Full-scale means collapsed multi-resolution

This became the core feasibility doctrine. It should become a formal architecture principle: full scale yes, full fidelity everywhere no.

### DECISION-10 — No broad restructure before baseline

The assistant recommended this based on repo docs. It should remain a strong constraint unless the repo state changes.

## 6. Ideas Considered but Rejected, Superseded, or Deprioritised

### REJECTED-01 — Build the full engine before game work

Rejected because it creates an infinite engine project. The better plan is narrow vertical slices that harden the engine.

### REJECTED-02 — Start with CAD/destruction before baseline

Superseded by Milestone 0. CAD/destruction remains important but should not precede playable baseline hardening.

### REJECTED-03 — Voxel-first universal building engine

Rejected/deprioritized because voxels are poor for precise machines, CAD semantics, interfaces, thin surfaces, and network-efficient authoritative objects. Voxels/SDF remain useful for terrain, mining, damage approximation, fluids, and debris.

### REJECTED-04 — Full fidelity universe everywhere

Rejected as impossible. The viable plan is full-scale but collapsed multi-resolution fidelity.

### REJECTED-05 — Unreal as authoritative simulation substrate

Rejected as a default plan. Unreal may still be useful as a client/editor/rendering shell.

### REJECTED-06 — Recipes/tech trees/levels as default gameplay

Rejected by user preference. Still supported as optional mod/game-mode layers.

### REJECTED-07 — Broad repo restructure before baseline

Deprioritized because current baseline paths are fragile and v0.0.0/current-reality docs prioritize preserving them.

## 7. Important Reasoning, Rationale, and Tradeoffs

The main tradeoff was ambition versus feasibility. The user wants a universe-scale game with CAD-like construction, sparse destruction, civilization building, fog of war, and MMO persistence. The answer repeatedly reframed this as possible only through representations that do less work: collapsed capsules, event-driven processes, sparse overlays, active sets, domain sharding, and derived proxies.

Another key tradeoff was player freedom versus accessibility. A full CAD suite gives freedom but alienates low-skill players and increases complexity. Templates and simple parts are accessible but can feel restrictive. The proposed compromise is layered authoring over a single canonical design artifact.

A third tradeoff was portability versus feature richness. Full modern rendering, CAD, and massive multiplayer cannot be required for all hardware. The answer proposed capability profiles and explicit degradation/refusal. Every target gets the same truth contract, not the same fidelity.

A fourth tradeoff was modularity versus restructuring. The user wanted replaceable directories and reusable code. The answer argued that contracts, APIs, tests, and provider interfaces matter more than directory layout. Broad restructure before baseline would risk breaking fragile run paths.

The final tradeoff was engine-first versus game-first. The conclusion was neither: build minimal vertical slices that are simultaneously game work and engine proof.

## 8. Plans, Future Work, and Next Steps

### 8.1 Milestone 0 — Make the baseline path honest

This is the immediate next work. It matters because without a reliable local playable path, later feature work will be built on unstable foundations.

Tasks:
1. Fix Python server/runtime circular import and entrypoint CLI forwarding.
2. Make `session_create -> session_boot` pass for intended MVP/baseline bundle.
3. Fix missing/invalid time-anchor policy registry.
4. Add one canonical repo-local playtest command.
5. Make `check_local_playtest_path.py --strict` pass.
6. Preserve user-reported validation evidence or rerun it as audit-grade logs.

Expected output: one command that creates/materializes session, boots it, starts local loopback authority, runs deterministic client/server smoke path, emits proof/replay/hash/compat artifacts, and exits with deterministic pass/fail.

### 8.2 Milestone 1 — One deterministic game action

After Milestone 0, implement one accepted and one refused game action, likely a simple build/place-part action. It should pass through authority/law, Work IR/process, commit, replay/hash, and client projection.

### 8.3 Milestone 2 — One deterministic removal/damage action

Add simple part removal or damage that affects an assembly/support graph. Do not start with full CAD/CSG destruction.

### 8.4 Milestone 3 — Minimal projection/rendering

Show the object/action through null/software/TUI/simple rendered projection. Rendering must not mutate truth.

### 8.5 Milestone 4 — Pack-driven part/action

Move the part/action into pack/registry/lockfile flow so modding and data-driven content are proven early.

### 8.6 Long-term work

Long-term work includes CAD/design substrate, geometry kernel providers, sparse terrain overlays, planet/domain hierarchy, collapsed civilization capsules, sharding, proof-carrying client compute, generated docs, platform matrix, validation unification, and modder toolchain.

## 9. Constraints, Preferences, and Non-Negotiables

### 9.1 Explicit Constraints and Preferences

- User wants direct, rigorous, source-grounded answers.
- User wants uncertainty labelled and framing corrected when evidence disagrees.
- User wants Domino code portable, modular, extensible, and reusable for other games/engines.
- User wants not to rely on recipes, tech trees, or levels in usual gameplay.
- User wants those systems supported for mods/game modes through capabilities/law/packs.
- User wants players limited by imagination but also able to play without special skills.
- User wants low-performance, disability controls, minimal GUI, and accessibility support.
- User wants full preservation of this chat for later aggregation.

### 9.2 Inferred Constraints and Preferences

- INFERENCE: prefer engineering plans that reduce overwhelm and produce concrete next actions.
- INFERENCE: prefer reusable contracts over ad hoc feature code.
- INFERENCE: prefer maximal freedom only if bounded by deterministic validation, budgets, and law/capability systems.
- INFERENCE: prefer not to depend on Unreal or another engine as authoritative core.

### 9.3 Uncertain or Unestablished Preferences

- UNCERTAIN: whether the user wants Unreal integration at all as a client/editor.
- UNCERTAIN: exact tolerance for using external geometry libraries.
- UNCERTAIN: whether broad repo restructuring will be desired after Milestone 0.
- UNCERTAIN: exact visual style, UI stack, or programming language evolution.

## 10. Files, Artifacts, Outputs, and Prompts

### ARTIFACT — Uploaded preservation prompt

`Pasted text.txt` contains the current preservation/export instructions. It is the source for this report’s requested structure. Preserve it. fileciteturn44file0

### ARTIFACT — Repository/docs/code references fetched during chat

Important fetched files included:
- `engine/CMakeLists.txt` — evidence for `domino_engine` and engine module composition.
- `game/CMakeLists.txt` — evidence for `dominium_game` and game module composition.
- `docs/canon/constitution_v1.md` — authoritative architecture/execution contract.
- `docs/repo/REPO_NON_NEGOTIABLES_AND_CURRENT_REALITY.md` — current baseline-first repo reality packet.
- `apps/client/main_client.c` — evidence that client advertises unavailable gameplay/world/package/provider/module runtime and `support_claim_playable=false`.
- `tools/xstack/registry_compile/constants.py` — evidence of `DEFAULT_BUNDLE_ID = "bundle.base.lab"`.
- `game/rules/physical/parts_and_assemblies.cpp`, `construction_processes.cpp`, `fab_interpreters.cpp` — evidence for early construction/fabrication substrates.
- Various docs: AppShell, capability negotiation, pack verification, semantic contracts, frozen invariants, MVP scope lock, registry compile, determinism envelope, canon conformance.

### ARTIFACT — User pasted local validation assessment

The user pasted a detailed local assessment listing passing build/test slices and blockers. Treat as user-supplied evidence unless independently verified. Preserve it because it corrected the plan.

### ARTIFACT — This preservation package

Created by this task: Markdown/YAML files and ZIP handoff package. These should feed future aggregation and spec book creation.

## 11. Open Questions and Unresolved Issues

1. Does the current live repo still match the fetched GitHub state?
2. Are the user-reported build/CTest results reproducible now?
3. What is the exact canonical playtest command name and interface?
4. Should `session_create` default stay `bundle.base.lab`, or should the MVP wrapper explicitly select `profile.bundle.mvp_default`?
5. What file/module refactor fixes the circular import without violating boundaries?
6. What registry artifact is missing or invalid for time-anchor policy?
7. What exact design artifact schema should support CAD/building later?
8. Which geometry provider/library strategy should be used for B-Rep/CSG/NURBS?
9. Will Unreal be used as a client/editor/render shell, or avoided entirely?
10. What is the minimum acceptable first playable slice?

## 12. Risks, Failure Modes, and What Future Chats Might Get Wrong

Future chats might overstate engine readiness by saying “the engine works” without noting `support_claim_playable=false` and blocked baseline paths. They might also forget Milestone 0 and jump into CAD, destruction, multiplayer, or universe-scale simulation prematurely.

Another risk is treating assistant recommendations as user decisions. For example, the CSG/B-Rep/NURBS hybrid is a strong recommendation but not yet a user-finalized decision. Unreal-as-shell is also a recommendation, not a committed plan.

A future assistant might merge this chat into a master spec as if every ambitious idea is a requirement for v0.0.0. That would be wrong. The chat clearly moved toward baseline-first sequencing and deferred major systems.

A future assistant might also miss the distinction between full scale and full fidelity. The project can aim for full-scale solar systems and planets only by using collapsed, sparse, hierarchical representations.

Finally, there is a risk of relying on stale GitHub/doc facts. Any implementation-sensitive claim should be verified against the current repo.

## 13. What This Chat Contributes to the Larger Project or Future Spec Book

This chat contributes:
- a high-level project identity: Domino substrate, Dominium game, XStack/governance;
- a modularity/future-proofing doctrine;
- a current readiness correction and baseline-first roadmap;
- a CAD/building authoring model;
- a geometry representation strategy;
- a full-scale universe architecture strategy;
- an MMO/client-compute feasibility frame;
- a list of immediate blockers and tasks.

It should feed spec book chapters on:
- architecture principles;
- engine/game/product boundaries;
- deterministic execution and proof;
- content/mod/pack system;
- construction/design/CAD;
- geometry/destruction;
- universe/planet/domain simulation;
- multiplayer/sharding/client compute;
- project roadmap and milestones;
- risks and non-goals.

Do not merge the full universe/MMO/CAD material as near-term implementation requirements. They belong as long-term architecture context unless later accepted as staged requirements.

## 14. What I Should Remember

- The engine substrate is real, but the playable game engine is not finished.
- The client explicitly reports `support_claim_playable=false`.
- The most important next milestone is not building/destruction; it is making one canonical repo-local playable baseline command pass strict validation.
- Domino should be reusable and deterministic; Dominium should not contaminate the engine substrate with game-specific meaning.
- The project is only feasible if it uses collapsed multi-resolution simulation, sparse overlays, event-driven scheduling, and proof/replay.
- Normal gameplay should avoid default recipes/tech trees/levels; those remain optional pack/law/profile features.
- CAD should be supported as an advanced/tooling surface, not required for casual play.
- Geometry should likely be hybrid: CSG/feature authoring, B-Rep canonical solids, NURBS optional faces, mesh derived, voxel/SDF for terrain/damage fields.
- Unreal cannot simply solve the authoritative simulation problem, though it might be useful for rendering/editor surfaces.
- Preserve the user's pasted local validation correction because it changed the plan.

## 15. Best Questions I Can Ask Next in This Chat

### 15.1 Understanding the Chat
- “Explain the difference between Domino substrate and Dominium game layer again, using examples from the repo.”
- “What changed after I pasted the local engine readiness assessment?”

### 15.2 Decisions
- “Which recommendations in this chat are actually accepted decisions, and which are just candidate architecture?”
- “What exactly did we decide about Milestone 0?”

### 15.3 Tasks and Next Actions
- “Turn Milestone 0 into a detailed implementation prompt for Codex/AIDE.”
- “Write the task card for fixing the server circular import.”
- “Write the task card for `session_create -> session_boot` baseline validation.”

### 15.4 Artifacts and Files
- “List every repo file cited in this chat and what it proved.”
- “Make a minimal evidence bundle checklist for the local validation results I pasted.”

### 15.5 Risks and Verification
- “What claims in this chat need to be re-verified against the live repo?”
- “What would make the project impossible again if we ignore it?”

### 15.6 Future Spec Book / Aggregation
- “Extract only the formal requirements from this chat.”
- “Extract only the future-spec context, excluding near-term tasks.”

### 15.7 Deep-Dive Questions Specific to This Chat
- “Design the exact first builder/destruction lab after Milestone 0.”
- “Define the CAD DesignArtifact schema from this chat’s recommendations.”
- “Define the sparse planet/terrain overlay model as a formal contract.”
- “Compare using Unreal as a renderer shell versus not using it at all.”

## 16. Compact Human Summary

This chat was a deep architecture and feasibility discussion about the Domino engine and Dominium game. It began with a request to read the project docs and GitHub repo and describe the whole project, especially the engine and game. The answer established the core distinction: Domino is the deterministic simulation substrate and Dominium is a game/rules/product layer built on top. The repository contains real CMake targets for `domino_engine` and `dominium_game`, so the project is not just a set of notes, but the engine is not yet a finished playable game engine.

The user then asked how to make the engine better, more efficient, portable, extensible, and durable. The answer compared lessons from major historical engines and concluded that Domino should not be a monolithic engine. It should be a deterministic, contract-driven, capability-negotiated simulation kernel. It should activate only what matters, use event-driven work rather than global scans, collapse inactive regions into capsules and sufficient statistics, and treat rendering as projection rather than truth.

The user later clarified that the live repo had more implemented work than discussed. After reading more docs and code, the plan shifted from broad future architecture to convergence. The project already has many serious systems: AppShell, capability negotiation, pack verification, semantic contracts, frozen invariants, registry compilation, determinism envelope reports, and execution source files. The recommendation became to reduce the architecture into fewer stronger extension contracts, improve validation unification, generate docs from registries, group registry bundles, add provider descriptors, create platform matrices, and harden the existing baseline instead of expanding.

A major topic was building and destruction. The user wanted players to build machines, structures, items, and megaprojects with maximum freedom, but not require skill. The answer proposed a CAD-capable but not CAD-required design substrate. Ordinary players should use templates, snapping, assisted intent, and accessibility-friendly controls. Advanced players and developers should be able to use CAD-like tools. All surfaces should compile into canonical design artifacts. The user also stated they do not want ordinary gameplay to rely on recipes, tech trees, or experience levels. The answer preserved that as a strong product preference: those systems may exist for mods or game modes via packs, law, capabilities, and profiles, but not as default core gameplay.

The geometry discussion concluded that a voxel-first approach like Dual Universe is not ideal. The recommended model is hybrid: CSG or feature graphs for authoring, B-Rep for canonical solids, NURBS/B-splines for advanced curved faces, meshes as derived render/collision proxies, and sparse voxels/SDF/fields for terrain, mining, damage approximation, fluids, debris, and volumetric phenomena. Destruction should be tiered and sparse, often represented as damage events and structural graph updates rather than constant full geometry recomputation.

The most important correction came when the user expressed worry that the project might be impossible and pasted a precise local readiness assessment. The corrected view is: the project has a working deterministic substrate, but not a finished playable engine. Some targeted tests and MP0 smoke paths reportedly pass, but the client source advertises unavailable gameplay/world/package/provider/module runtime and `support_claim_playable=false`; the playtest path is blocked; server Python entrypoint has circular import issues; session bundle paths are not hardened; and the time-anchor policy registry is missing or invalid. Therefore, before any CAD, destruction, economy, agents, or broad gameplay, the project needs **Milestone 0: Make the baseline path honest**.

Milestone 0 means fixing server/runtime circular import and CLI forwarding, making `session_create -> session_boot` pass for the intended MVP/baseline bundle, fixing the time-anchor policy registry, adding one canonical repo-local playtest command, and making the strict local playtest validator pass. Only after that should the first builder/destruction lab begin: one deterministic accepted/refused build action, one deterministic damage/removal action, minimal projection/rendering, and then pack-driven content.

The final architectural discussion concerned full-scale solar systems, planets, civilizations, fog of war, client-shared compute, and MMO persistence. The answer made the feasibility rule explicit: full scale is possible only if full fidelity everywhere is rejected. Domino should use hierarchical domains, rail-orbit providers, planet tiles, sparse terrain overlays, collapsed civilization capsules, fog-of-war epistemic filtering, domain-sharded authority, and proof-carrying client delegation. Unreal can help with rendering or editor tooling, but it cannot provide the full deterministic authoritative simulation model out-of-the-box.

The most important thing to carry forward is the sequencing: **baseline first, tiny vertical slice second, grand systems later**.
