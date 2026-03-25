Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: PI
Replacement Target: snapshot-anchored blueprint index after repository convergence and freeze

# Meta Blueprint Index

## Purpose

This document is the master planning layer for the post-Ξ future of Dominium.
It links the current audited repository evidence to the intended Σ, Φ, Υ, and Ζ implementation arcs without changing runtime semantics.

## Current Evidence Snapshot

- Architecture modules: 1743
- Architecture concepts: 316
- Module dependency edges: 2319
- Build targets: 471
- Source-like directories still present in current working tree evidence: 258

Dominant module domains:
- `unknown`: 439 modules
- `tests`: 232 modules
- `tools`: 218 modules
- `data`: 216 modules
- `docs`: 151 modules
- `game`: 122 modules
- `packs`: 95 modules
- `schemas`: 90 modules

Available Ξ evidence in the current workspace:
- `XI_0`: present
- `XI_1`: present
- `XI_2`: present
- `XI_3`: present
- `XI_4`: not_present
- `XI_5`: not_present
- `XI_6`: not_present
- `XI_7`: not_present
- `XI_8`: not_present

## Artifact Index

| Artifact | Purpose |
| --- | --- |
| `META_BLUEPRINT_SUMMARY.md` | Executive framing of the system as a multi-layer, OS-like platform. |
| `RUNTIME_ARCHITECTURE_DIAGRAM.md` | Layered runtime target map from applications to the deterministic kernel. |
| `REPOSITORY_GOVERNANCE_DIAGRAM.md` | XStack, architecture graph, and governance surface map. |
| `DISTRIBUTION_AND_ARCHIVE_DIAGRAM.md` | Release, archive, trust, and install flow map. |
| `LIVE_OPERATIONS_DIAGRAM.md` | Future Ζ live-operations capability map. |
| `SERIES_DEPENDENCY_MAP.md` | Σ/Φ/Υ/Ζ dependency map plus Ω and Ξ foundations. |
| `CAPABILITY_LADDER.md` | Capability levels from frozen MVP to speculative live operations. |
| `FOUNDATION_READINESS_MATRIX.md` | Capability readiness classifications and blockers. |
| `PIPE_DREAMS_MATRIX.md` | Advanced concepts, feasibility tiers, and prerequisites. |
| `SNAPSHOT_MAPPING_NOTES.md` | Pre-snapshot assumptions and the follow-up mapping pass contract. |

## Best Practices to Borrow and Adapt

- `Databases and WAL systems` -> Use append-only journals, snapshot isolation, and replayable recovery.
  Dominium translation: Pair proof anchors with deterministic replay, checkpoint plus event-tail sync, and rollback receipts.
- `Erlang/BEAM hot upgrades` -> Upgrade code through planned state handoff instead of blind in-place mutation.
  Dominium translation: Model live cutovers as state export/import plus proof-backed replacement plans issued by the lifecycle manager.
- `Formal deployment controllers` -> Represent rollouts as plans with preconditions, policy, and rollback steps.
  Dominium translation: ControlX should emit explainable upgrade and cutover plans instead of imperative scripts.
- `Framegraph renderers` -> Separate render intent from backend execution through explicit dependency graphs.
  Dominium translation: A future render service should consume framegraph-style plans rather than letting backend specifics leak into truth paths.
- `Kubernetes rollouts and canaries` -> Prefer staged rollout, health checks, and reversible promotion gates.
  Dominium translation: Adopt canary mod deployment, blue/green services, and quarantine-first rollout policy backed by XStack gates.
- `Microkernels` -> Keep the kernel minimal and push replaceable behavior into controlled services.
  Dominium translation: Use the deterministic engine kernel for truth, then grow a service registry around it rather than bloating core process execution.
- `Package managers` -> Treat compatibility, dependency graphs, and rollback as first-class governance artifacts.
  Dominium translation: Extend pack compat, component graphs, release indexes, and deterministic downgrade planning.
- `Service meshes` -> Make routing, observability, and policy explicit instead of ad hoc.
  Dominium translation: Use side-by-side execution, attach negotiation, and proof-aware traffic policy for service cutovers.
- `Zero-downtime migration systems` -> Dual-write, verify, and cut over only after proof of equivalence.
  Dominium translation: Future live migrations should compare replay hashes, proof anchors, and compatibility receipts before promotion.

## Bridge Statement

This blueprint is pre-snapshot and architecture-driven.
It describes the safe bridge from the current audited repository surface to the intended post-Ξ, post-Ω implementation work, while explicitly preserving constitutional invariants.

