Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.

# Nothing Just Happens (MAT-8)

## Purpose
Define canonical causality strictness policies for material-domain macro/meso changes and freeze enforcement expectations before full micro reenactment zones.

## Causality Strictness Levels
- `causality.C0` (default)
  - Macro/meso mutation requires deterministic process execution and emitted provenance events.
  - Commitments are strongly recommended and required for process families that already define commitment artifacts (construction, logistics, maintenance), but missing commitment does not globally refuse all macro changes.
- `causality.C1`
  - Major macro/meso changes require commitments and events.
  - Applies to construction, logistics shipment lifecycle changes, and maintenance execution affecting asset/material state.
  - Missing required commitment yields deterministic refusal `refusal.commitment.required_missing`.
- `causality.C2` (reserved)
  - C1 guarantees plus commitment-gated micro actions inside declared micro reenactment zones.
  - MAT-8 reserves schema/runtime hooks only; bounded micro enforcement remains future work.

## Canonical Rule
No macro state change without:
1. deterministic process execution,
2. at least one provenance event, and
3. commitment linkage when required by active causality strictness.

This satisfies MAT-0 nothing-just-happens and A2 process-only mutation.

## Policy Declaration Location
- Preferred: Scenario/Session policy pack (`policy_context.causality_strictness_id`).
- Allowed fallback: UniversePhysicsProfile extension field (`extensions.default_causality_strictness_id`).
- Default when unspecified: `causality.C0`.

## Enforcement Surface
- Runtime validates commitment requirements for major material process families.
- Event stream indices and reenactment artifacts are derived views and never mutate canonical truth.
- Refusals are deterministic and auditable.

## Invariants
- Causality policy changes may alter allowed/refused process outcomes but must never introduce nondeterminism.
- Event ordering and commitment linkage are deterministic (sorted IDs and stable fingerprints).
- Compaction/checkpointing may summarize events but must preserve commitment/event lineage continuity.
