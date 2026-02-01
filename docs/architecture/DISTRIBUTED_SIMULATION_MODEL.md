Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: docs/archive/architecture/DISTRIBUTED_SIM_MODEL.md
Superseded By: none

# Distributed Simulation Model (MMO-SRZ)

Status: binding.
Scope: distributed execution, verification, and commit across SRZs and shards.

## Principle

> Distributed execution must not change outcomes.
> SRZ assignment chooses where work runs, not what work is.

All authoritative outcomes are replayable and auditable.
Execution backends may vary; semantics must not.

## Roles

SRZs separate three roles:
- Executor: runs processes (server or delegated client).
- Verifier: replays or checks invariants.
- Committer: applies verified results at commit boundaries.

These roles can co-locate but must be logically distinct.

## Commit boundaries

State transitions occur only at commit boundaries.
Commit order follows `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md`.
Logs, hash chains, and macro capsules are the canonical commit artifacts.

## Verification strategies

Supported strategies:
- strict_replay
- spot_check
- invariant_only

Verification must be deterministic and explainable.
Failed verification MUST emit refusal reasons and rejection evidence.

## Shards and SRZs

Shards own domains; SRZs may subdivide responsibility within or across shards.
Shard ownership never implies SRZ authority without explicit assignments.
SRZ reassignment occurs only at commit boundaries.

## Execution backends

Allowed backends:
- scalar (baseline, C89-safe)
- vectorized (SIMD, fixed-point only)
- batched/tiled
- distributed (multi-server SRZs)

Backend selection MUST NOT change semantics.
All reductions must be order-fixed and deterministic.

GPU/tensor use is allowed ONLY for:
- non-authoritative visualization
- tooling analytics
- optional verification acceleration (fixed-point only)

## Non-goals

- No wall-clock dependence.
- No hidden authoritative paths.
- No client-trusted outcomes without verification.

## See also
- `docs/architecture/DISTRIBUTED_TIME_MODEL.md`
- `docs/architecture/SRZ_MODEL.md`
- `docs/architecture/SCALING_MODEL.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`