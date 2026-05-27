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
