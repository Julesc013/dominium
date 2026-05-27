# Aggregator Packet — Dominium Omega/Xi/Pi Architecture & Future-Proofing Planning

## Packet Metadata

* Chat label: Dominium Omega/Xi/Pi Architecture & Future-Proofing Planning
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: This chat only unless labelled PROJECT-CONTEXT
* Coverage: broad but not literal full-token complete
* Confidence: 4/5 major themes, 3/5 current repo state
* Staleness risk: medium-high
* Merge priority: high
* Main limitations: user-reported repo status should be verified; uploaded snapshots may be stale.

## Ultra-Condensed Carry-Forward Capsule

This chat is a major architecture and continuity node for the Dominium project. Dominium is a deterministic simulation/game/platform ecosystem built on the reusable Domino engine. The user wants it to be portable, modular, extensible, reusable for other games and engine projects, replaceable down to files/directories/code/data, and engineered like a proper OS/platform rather than a one-off indie project.

The central doctrine established here is: stable contracts, replaceable implementations, deterministic behavior, manifest-based identity, tool-agnostic development, XStack-enforced architecture, and human-readable plus machine-readable everything. The project should not try to make every file stable. It should make boundaries explicit, versioned, testable, migratable, and replaceable.

A long series of plans was produced. Ω-series freezes the MVP runtime/distribution world: worldgen lock, baseline universe, gameplay loop, disaster suite, ecosystem verify, update sim, trust strict suite, offline archive, toolchain matrix, final dist plan/execution. Ξ-series handles repository convergence and drift immunity: architecture graph, duplicate scan, implementation scoring, convergence plan, execution, src removal, architecture graph freeze, CI guardrails, repository freeze. Π-series produces meta-blueprints and final future prompt inventory. The user reports Xi-6/Xi-7/Xi-8 and Pi-0/Pi-1/Pi-2 are complete in public GitHub `julesc013/dominium/main`, with many hashes and commits. Treat these as user-reported facts unless verified.

The immediate next phase is Ρ-series: snapshot-driven final planning. Ρ-0 Snapshot Intake, Ρ-1 Reality Extraction, Ρ-2 Blueprint Reconciliation, Ρ-3 Foundation Readiness, Ρ-4 Final Prompt Synthesis. This must be done before implementing Σ/Φ/Υ/Z because the current repo may differ from abstract plans and older uploaded snapshots.

Future series: Σ for agent/human governance and vendor-neutral task interfaces; Φ for runtime component/service/kernel architecture; Υ for build/release/distribution/control plane; Ζ for future live operations like hot-swappable renderers, live save/schema/protocol migration, mod hot activation, distributed shard relocation, trust-root rotation, canary cutovers, and deterministic live operations. Do not implement Ζ before lifecycle manager, state externalization, event log, snapshot service, release transaction log, trust/migration policies, and service isolation exist.

Important conflict: the uploaded repo snapshot shows generic `src`/`source` pockets, but the user reports Xi-5/6/8 removed or classified them. Future work must verify current GitHub main before treating either state as current.

## Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
|---|---|---|---|---|---|---|
| P0 | Run Ρ-series next | Task | TASK-01..05 | Grounds plans in repo reality | FACT | High |
| P0 | Verify current repo state | Verification | VERIFY-01 | Resolves snapshot contradiction | UNCERTAIN | High |
| P0 | Preserve stable contracts/replaceable impl doctrine | Decision | DECISION-11 | Core architecture law | FACT | High |
| P1 | Build Σ agent governance | Workstream | WORKSTREAM-06 | Prevents AI/human drift | FACT | High |
| P1 | Build Φ runtime component foundations | Workstream | WORKSTREAM-07 | Enables Z later | FACT | Medium |
| P1 | Build Υ release/control plane | Workstream | WORKSTREAM-08 | Enables updates/archives | FACT | Medium |

## Workstream Summaries

See Workstream Register in full package. Most important active workstream is Ρ-series.

## Compact Registers for Merge

Key decisions: DECISION-01 through DECISION-12.
Key tasks: TASK-01 through TASK-10.
Key constraints: CONSTRAINT-01 through CONSTRAINT-10.
Key risks: RISK-01 through RISK-08.
Key verification items: VERIFY-01 through VERIFY-07.

## Possible Cross-Chat Duplicates

- Repo layout/naming discussions.
- Runtime/platform/render architecture.
- Agent governance.
- Release/distribution/versioning.
- Earth/Sol/Galaxy MVP stubs.

## Possible Cross-Chat Conflicts

- Exact top-level directory model.
- Whether `runtime/` exists or should be introduced.
- Whether current repo has `src` roots.
- Details of AGENTS/Copilot/Claude support.
- Whether Workbench is a product root or app under existing roots.

## Spec Book Integration Guidance

This chat should inform chapters on architecture doctrine, repo governance, XStack, versioning/release, agent governance, runtime componentization, live operations roadmap, coding/API/schema standards, and project continuity. It should not be merged as verified current repo state until the live repo is inspected.

## Aggregator Warnings

Do not flatten the staged plan into “implement everything.” The whole point is sequence and dependencies: Ρ before Σ/Φ/Υ/Z; Φ/Υ before Z; XStack gates before claims.
