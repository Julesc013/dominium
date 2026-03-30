Status: DERIVED
Last Reviewed: 2026-03-31
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: PI
Replacement Target: snapshot-anchored phase execution plan after repository remapping

# Foundation Phases

## Phase Order

The work proceeds through phases A through E. Later phases may be designed early but must not be implemented before their prerequisites are satisfied.

## Phase A - Governance & Interface Foundations

Objective: Stabilize the human and agent governance surface before any advanced runtime automation.

Prerequisites:
- XI architecture freeze, module boundaries, CI guardrails, and repository structure lock present
- OMEGA baseline verification inventory confirmed current

Completion criteria:
- AGENTS governance mirrored into XStack artifacts
- task types mapped to validation levels and refusal codes
- operator policy model and declarative cutover language reviewed
- manual review gate definitions frozen for high-risk areas

Blocked capabilities:
- agent-driven change execution at scale
- live feature flag cutovers
- runtime privilege revocation

## Phase B - Runtime Component Foundations

Objective: Define the kernel, service, module, and state boundaries required for lawful replaceability.

Prerequisites:
- Phase A complete
- fresh repository snapshot mapped to exact insertion points
- runtime boundary doctrine accepted in manual design review

Completion criteria:
- component ownership and service registry boundaries frozen
- module loader insertion points mapped and validated
- state externalization and lifecycle semantics have replay-safe contracts
- module ABI boundaries reviewed for compatibility and rollback

Blocked capabilities:
- hot-swappable renderers
- partial live module reload
- shadow service startup
- non-blocking save handoff

## Phase C - Build / Release / Control Plane Foundations

Objective: Freeze the control plane needed to ship, rehearse, roll forward, and roll back deterministically.

Prerequisites:
- Phase A complete
- versioning, release index, rollback, and rollout policy surfaces designed
- fresh build graph and release surface re-audited before exact lock and preset wiring
- archive and publication policies aligned with OMEGA verification

Completion criteria:
- build graph lock is generated from the live repository state
- release transaction log and rollback policy exist as inspectable artifacts
- canary, blue-green, and downgrade policy pass governance review
- release rehearsal workflow defined with deterministic checkpoints

Blocked capabilities:
- automatic yanking with deterministic downgrade
- release rehearsal sandbox
- live trust-root rotation
- mod live mount and live cutover

## Phase D - Advanced Replaceability

Objective: Enable the earliest safe ZETA features once governance, componentization, and release control are complete.

Prerequisites:
- Phase A complete
- Phase B complete
- Phase C complete
- OMEGA worldgen, baseline, gameplay, disaster, ecosystem, and trust gates current

Completion criteria:
- renderer and service replacement boundaries are proven by smoke harnesses
- early shadow services and pack mount workflows have rollback receipts
- sidecars and offscreen validation paths do not leak truth mutation
- all replacement plans use declarative cutover artifacts and transaction logs

Blocked capabilities:
- distributed shard relocation
- deterministic replicated simulation
- restartless core engine replacement

## Phase E - Distributed Live Operations

Objective: Pursue distributed runtime and extreme live operations only after earlier phases are complete and boring.

Prerequisites:
- Phase D complete
- event log and snapshot proofs validated under rehearsal
- authority handoff model and proof-anchor quorum semantics manually approved

Completion criteria:
- deterministic replication and authority handoff proven under controlled rehearsal
- cluster failover, downgrade, and replay verification remain within OMEGA tolerances
- protocol and schema live evolution guarded by multi-version coexistence and rollback policy
- extreme operations remain quarantined unless every lower-level invariant still passes

Blocked capabilities:
- cluster-of-clusters rollout
- restartless core replacement by default
- live schema evolution by default

