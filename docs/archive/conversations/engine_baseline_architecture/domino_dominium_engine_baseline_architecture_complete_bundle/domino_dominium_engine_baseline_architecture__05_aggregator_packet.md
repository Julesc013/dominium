# Aggregator Packet — Domino/Dominium Engine Baseline, Architecture, and Feasibility

## Packet Metadata

* Chat label: Domino/Dominium Engine Baseline, Architecture, and Feasibility
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: This chat only unless labelled PROJECT-CONTEXT
* Coverage: Partial but broad visible transcript plus fetched repo files and uploaded preservation prompt
* Confidence: 4/5
* Staleness risk: Medium
* Merge priority: High
* Main limitations: Local validation/build results were pasted by user but not independently rerun; repo may have changed after fetched files; some recommendations are not final decisions.

## Ultra-Condensed Carry-Forward Capsule

This chat is a major architecture and feasibility checkpoint for the Domino engine and Dominium game. It established that Domino should be treated as a reusable deterministic simulation substrate, while Dominium is one game/rules/product layer built on top. The engine/game/client/server boundaries are central: engine defines deterministic mechanisms; game defines rule meaning; client/render project data and issue intents; server/domain authority validates authoritative multiplayer truth.

The conversation first described the project from docs and GitHub, then expanded into how to make the engine portable, modular, extensible, efficient, powerful, and durable. The key design principle is that Domino should not simulate everything at full fidelity. It should virtualize expensive systems, activate only what matters, use event-driven work, collapse inactive regions into capsules/sufficient statistics, and preserve proof/replay determinism. Tooling, pack verification, capability negotiation, semantic contracts, registries, lockfiles, and generated docs are not optional extras; they are the system that makes the engine reusable and maintainable.

A later correction was crucial: the live repo already has more infrastructure than the early broad plan captured — AppShell, capability negotiation, pack verification, frozen invariants, semantic contracts, registry compile, determinism envelope, execution source, and early construction/fabrication logic. Therefore the plan changed from “design the architecture” to “converge and harden the existing architecture.”

The user asked whether the game needs a full CAD suite to allow players to build anything. The answer proposed layered authoring: ordinary players use templates, snapping, assisted intent, and accessibility-friendly controls; advanced players/developers can use CAD-grade tools. All authoring surfaces compile into canonical design artifacts. The user explicitly does not want ordinary gameplay based on recipes, tech trees, or experience levels, though those should remain supported for mods/game modes through packs, law, profiles, and capabilities.

For construction/destruction geometry, the recommended long-term model is hybrid: CSG/feature graphs for authoring, B-Rep for canonical solids, NURBS/B-splines for advanced curved faces, meshes as derived render/collision proxies, and sparse voxels/SDF/fields for terrain, mining, fluids, debris, and damage approximation. Do not make a voxel-first universal engine.

The biggest practical correction came when the user pasted a local assessment: compiled targets and some targeted tests reportedly pass, but the client advertises `support_claim_playable=false`; the playtest path is blocked; server Python entrypoint has circular import issues; session create/boot and bundle paths are not hardened; and the time-anchor policy registry is missing/invalid. The accepted sequencing is now **Milestone 0 first**: fix baseline blockers and make one canonical repo-local playable baseline command pass strict validation before starting builder/destruction or broad gameplay features.

The final future-vision discussion covered full-scale solar systems, planets, civilizations, terraforming, fog of war, client compute, and MMO persistence. The conclusion was: full scale is possible only if full fidelity everywhere is rejected. Use hierarchical domains, rail orbits, sparse planet overlays, collapsed civilization capsules, fog-of-war epistemics, domain-sharded authority, and proof-carrying client compute. Unreal can help with rendering/editor presentation but should not be treated as the authoritative deterministic simulation substrate.

## Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
|---|---|---|---|---|---|---|
| P0 | Make baseline path honest before gameplay | Decision/task | DECISION-03 / TASK-01–07 | Prevents building on broken runtime | FACT | High |
| P0 | Preserve engine/game boundary | Constraint | CONSTRAINT-03 | Enables reuse | FACT | High |
| P0 | Client/render not authoritative | Constraint | CONSTRAINT-04 | Prevents drift/cheats | FACT | High |
| P0 | Verify local build/test claims | Verification | VERIFY-01/02 | Needed for audit proof | UNVERIFIED | High |
| P1 | CAD-capable but not CAD-required | Design principle | DECISION-05 | Balances freedom/accessibility | INFERENCE | Medium-high |
| P1 | No recipes/tech trees/levels by default | User preference | DECISION-06 | Core game identity | FACT | High |
| P1 | Hybrid geometry approach | Architecture | DECISION-07 | Future building/destruction | INFERENCE | Medium |
| P1 | Full scale requires collapsed fidelity | Architecture | DECISION-09 | Makes universe feasible | INFERENCE | High |

## Workstream Summaries

### WORKSTREAM-02 — Baseline path hardening
Objective: make one canonical repo-local playable baseline command pass strict validation. Current state: substrate exists, playtest path blocked/fragile. Desired state: strict validator passes, proof_status unblocked. Tasks: fix circular import, CLI forwarding, session create/boot, bundle seam, time-anchor registry, canonical command. Risks: overstatement, skipping baseline. Next action: reproduce and fix circular import.

### WORKSTREAM-06 — CAD/design/building
Objective: support build-anything freedom through layered authoring and canonical design artifacts. Current state: concept plus early physical/FAB code. Desired state: DesignArtifact contract and multiple UI/tool surfaces. Priority after baseline.

### WORKSTREAM-08 — Sparse full-scale universe
Objective: support solar systems/planets/civilizations/MMO through domains, collapse, sparse overlays, fog, sharding. Current state: strategic architecture. Desired state: formal domain/capsule contracts. Not near-term.

## Compact Registers for Merge

### Decisions
- DECISION-01: Domino substrate, Dominium game layer.
- DECISION-02: Not a finished playable engine.
- DECISION-03: Milestone 0 before builder/destruction.
- DECISION-05: CAD-capable, not CAD-required.
- DECISION-06: No default recipes/tech trees/levels.
- DECISION-07: Hybrid geometry recommended.
- DECISION-09: Full scale, not full fidelity everywhere.

### Tasks
- TASK-01: Fix server/runtime circular import.
- TASK-02: Fix server CLI forwarding.
- TASK-03: Make `session_create -> session_boot` pass.
- TASK-04: Resolve baseline bundle seam.
- TASK-05: Fix time-anchor policy registry.
- TASK-06: Add canonical repo-local playtest command.
- TASK-07: Make strict local playtest validator pass.
- TASK-09: After baseline, implement one deterministic build action.

### Constraints
- CONSTRAINT-01: Determinism primary.
- CONSTRAINT-02: Process-only mutation.
- CONSTRAINT-03: Engine/game boundary.
- CONSTRAINT-06: No silent fallback.
- CONSTRAINT-07: No default recipes/tech trees/levels.
- CONSTRAINT-08: Baseline first.
- CONSTRAINT-09: Full scale requires collapsed fidelity.

### Open Questions
- Exact circular import fix.
- Baseline bundle/default strategy.
- Missing/invalid time-anchor registry.
- Canonical playtest command name/interface.
- Exact DesignArtifact schema.
- Geometry provider strategy.
- Unreal shell decision.

### Artifacts
- Uploaded preservation prompt.
- Engine/game CMake files.
- Constitution/current reality docs.
- Client `support_claim_playable=false` source.
- Registry constants default bundle source.
- Physical/FAB source files.
- User pasted readiness assessment.
- Generated preservation package.

### Risks
- Overstating readiness.
- Skipping Milestone 0.
- Scope explosion.
- Treating recommendations as decisions.
- Full-fidelity universe assumption.
- Geometry nondeterminism.

### Verification Queue
- User-reported CTest/MP0 pass.
- Circular import stack.
- Session boot refusal.
- Time-anchor registry failure.
- Live repo freshness.
- External Unreal/geometry-library facts.

## Possible Cross-Chat Duplicates

- Engine/game boundary.
- XStack/governance and compatibility.
- Pack/capability architecture.
- CAD/building plans.
- Playable baseline blockers.
- Full-scale universe simulation.

## Possible Cross-Chat Conflicts

- Older chats may claim the engine/game is more ready.
- Other chats may propose feature work before Milestone 0.
- Other chats may prefer voxel-first construction.
- Other chats may assume recipes/tech trees.
- Other chats may propose repo restructuring before baseline.

## Spec Book Integration Guidance

Feed into chapters: architecture, deterministic execution, roadmap, pack/mod system, CAD/building, geometry/destruction, planet/universe simulation, multiplayer/sharding, accessibility, project risks. Formalize Milestone 0 and engine/game boundary. Treat CAD/MMO/full-universe content as long-term context unless confirmed as staged requirements. Do not merge assistant-only recommendations as final decisions without user confirmation.

## Aggregator Warnings

Do not overstate readiness. Do not skip Milestone 0. Do not confuse full scale with full fidelity. Do not make Unreal authoritative. Do not turn no-recipes preference into “recipes can never exist”; they can exist in modded modes. Do not treat geometry hybrid as final implementation selection without further confirmation.
