Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Decay Failure Maintenance

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Purpose
Define deterministic MAT-6 decay, failure, and maintenance contracts for macro/meso structure health progression without requiring micro-scale simulation.

## Process Family
- Decay is a deterministic process family operating on installed structure instances and AG-derived assets.
- Failure modes are registry-defined models; runtime must not hardcode mode logic.
- Maintenance backlog is authoritative explicit state on asset health records.
- Maintenance is commitment-driven and process-executed.

Authoritative process IDs:
- `process.decay_tick`
- `process.maintenance_schedule`
- `process.inspection_perform`
- `process.maintenance_perform`

No silent state edits are permitted.

## Failure Model
- Failure modes are loaded from `failure_mode_registry`.
- Macro/meso default triggering uses deterministic threshold crossing.
- Optional stochastic triggering is policy-gated and must use named RNG streams.
- Triggering a failure must emit:
  - `failure_event`
  - linked MAT-5 provenance event
  - process-scoped ledger/accounting deltas when state/material channels change.

## Maintenance Model
- Policies are loaded from `maintenance_policy_registry` and backlog growth rules from `backlog_growth_rule_registry`.
- Maintenance schedule process creates deterministic inspection/maintenance commitments.
- Inspection updates inspection tick and produces provenance output.
- Maintenance reduces backlog deterministically and may partially reset wear via policy model hooks.
- Missing required maintenance materials must refuse with `refusal.maintenance.materials_missing`.
- Law/profile denial must refuse with `refusal.maintenance.forbidden_by_law`.

## Time Warp Determinism
- Decay integrates over `dt_ticks` in deterministic bounded sub-steps.
- No wall-clock integration is allowed.
- Large `dt_ticks` updates must remain stable and replay-equivalent across thread counts.

## Ledger and Exceptions
- Failure consequences must be ledger-accounted.
- Preferred closed-universe transformation:
  - usable material -> `material.scrap.generic`
  - entropy metric increase (`quantity.entropy_metric`).
- If policy permits destructive loss, use explicit exception entries only.

## Observability and Epistemics
- Inspection snapshots expose quantized risk/backlog according to epistemic policy.
- Diegetic default view is coarse (e.g. warning/severity buckets).
- Lab/admin scopes may observe detailed deterministic values.
- Refinement must not leak forbidden internal defect details.

## Multiplayer Safety
- Server-authoritative/hybrid: server computes decay/failure/maintenance and broadcasts perceived deltas.
- Lockstep: identical deterministic decay progression across peers.
- Clients submit intents only; server validates maintenance legality and resources.

## Constitutional Alignment
- A1 Determinism: tick-ordered, replay-safe wear/failure progression.
- A2 Process-only mutation: no direct state mutation outside process runtime.
- A5 Event-driven advancement: failures/maintenance represented as events.
- A6 Provenance continuity: every failure/maintenance mutation is traceable.
- A9 Pack-driven integration: failure/policy/backlog models are registry-defined.
