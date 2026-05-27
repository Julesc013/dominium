# Aggregator Packet — Dominium Build and Future-Proofing Architecture

## Packet Metadata

* Chat label: Dominium Build and Future-Proofing Architecture
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: Visible current chat only unless labelled PROJECT-CONTEXT/REPO-CONTEXT
* Coverage: Partial visible chat plus uploaded prompt and surfaced repo context
* Confidence: 4/5 for visible chat, lower for older implied context
* Staleness risk: Medium to High
* Merge priority: High, because it defines build and modularity governance candidates
* Main limitations: Recommendations were not all accepted; repo state must be reverified.

## Ultra-Condensed Carry-Forward Capsule

This chat should be merged into the master Dominium spec book as a candidate-governance packet, not as a final canon record. It has two primary contributions. First, it reframes Dominium's build/toolchain complexity as a tuple-contract problem. The user has multiple machines and historical toolchain goals, including VS2017, VS2022/VS2026, XP toolchains, old Visual Studio versions, Xcode 9, CodeWarrior Pro 9, and other legacy environments. The recommended architecture is: contracts define build tuples; machine probes detect local capability; generated `CMakeUserPresets.json` exposes buildable local lanes; CMake remains native build authority; CTest/TestX/RepoX provide proof; AIDE probes/explains/generates/verifies/records evidence; XStack orchestrates governance; dist/package manifests preserve artifact identity. This avoids one universal preset or one universal binary and aligns with the user's constraints: C89 engine, C++98 game, deterministic fixed-point execution, per-floor artifacts, no CRT mixing, and no silent API creep.

Second, the chat reframes Dominium as a portable deterministic engine platform rather than a one-off game repo. The user wants code reusable for other games on the Domino engine and even unrelated engine/game projects. They also want whole files/directories rewritable during future refactors. The recommended doctrine is stable contracts first, replaceable implementations second, products third, presentation last. The current top-level repo structure appears close to correct, but the missing mechanisms are public surface registry, dependency-edge contract, ABI/header conformance tests, schema/protocol compatibility harness, replacement protocol, game/domain cleanup, and content pack authority cleanup.

Merge warning: most architecture items are assistant recommendations, not explicitly accepted user decisions. Treat them as candidate requirements pending user acceptance and live repo verification.

## Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
|---|---|---|---|---|---|---|
| P0 | Do not treat recommendations as accepted canon | Warning | RISK-01 | Prevents bad spec merge | FACT | High |
| P0 | Tuple-driven build governance | Candidate requirement | WORKSTREAM-01 | Solves multi-machine/toolchain complexity | RECOMMENDATION | High |
| P0 | Public surface registry | Candidate requirement | WORKSTREAM-03 | Enables safe reuse/rewrite | RECOMMENDATION | High |
| P1 | Replacement protocol | Candidate requirement | WORKSTREAM-04 | Enables whole-module rewrites | RECOMMENDATION | High |
| P1 | Schema/protocol compatibility harness | Candidate requirement | WORKSTREAM-05 | Protects saves/replays/packages/protocols | RECOMMENDATION | High |

## Workstream Summaries

* WORKSTREAM-01: Build/toolchain governance. Objective: tuple-driven builds and generated local presets. Current state: recommended. Next action: draft `contracts/build`.
* WORKSTREAM-02: Repo/source structure. Objective: stable ownership layout. Current state: top-level close; deeper cleanup remains. Next action: verify current repo and dependency edges.
* WORKSTREAM-03: Public surface governance. Objective: registry for ABI/API/schema/protocol/command surfaces. Next action: draft registry schema.
* WORKSTREAM-04: Replacement protocol. Objective: rewrite modules behind black-box conformance. Next action: define protocol and tests.
* WORKSTREAM-05: Schema/protocol compatibility. Objective: fixture-based evolution proof. Next action: choose frozen schemas and fixtures.
* WORKSTREAM-06: Preservation/aggregation. Objective: preserve chat and merge later. Current state: complete.

## Compact Registers for Merge

Decisions: DECISION-01 is user-stated constraint; DECISION-02 through DECISION-07 are recommendations. Tasks: TASK-01 verify repo, TASK-02 confirm canon acceptance, TASK-03 public surface registry, TASK-04 build tuple contracts. Constraints: C89 engine, C++98 game, deterministic/no hidden behavior, per-floor artifacts, no CRT mixing, no silent API creep. Risks: recommendations treated as decisions; stale repo state; folder-focused cleanup without interface contracts. Verification: current repo HEAD/CI, current toolchain docs, schema freeze state.

## Possible Cross-Chat Duplicates

Build matrix/toolchain support, Dominium source spine, runtime naming, component matrix, C89/C++98 canon, AIDE/XStack governance, public surface/ABI policy, schema stability, content pack cleanup.

## Possible Cross-Chat Conflicts

Later chats may supersede top-level structure, toolchain priorities, VS2026 facts, repo HEAD, or task sequencing. Merge only after checking newer reports.

## Spec Book Integration Guidance

Feed this into chapters on Build Governance, Source Ownership, API/ABI Stability, Data Contracts, Refactor/Replacement Protocol, and Release/Distribution Proof. Formal requirements candidates require user confirmation. Do not prematurely merge assistant recommendations as final decisions.

## Aggregator Warnings

The user wants high-fidelity preservation. Avoid compressing away rationale. Keep uncertainty labels. Verify stale external facts. Do not generalize beyond this visible chat.
