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
