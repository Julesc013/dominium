Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, MAT-0, RS-2, RS-4, RS-5, and ED-4.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Macro Micro Mapping

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Purpose
Define deterministic expansion/collapse contracts for materialized micro part entities derived from canonical macro material and assembly state.

## Canonical Principle
- Macro material state is canonical:
  - stock ledgers
  - aggregate distributions
  - installed assembly graph node completion state
- Micro part instances are ephemeral deterministic refinements of canonical macro state.
- Micro state must be reproducible from:
  - canonical macro state
  - deterministic seed derivation
  - policy context

## Deterministic Sampling
- Micro IDs are derived from stable content hash:
  - `H(parent_structure_id, ag_node_id, batch_id, index)`
- Materialization seed is deterministic and namespaced:
  - `named_rng_stream("materialization", parent_id, tick_bucket)`
- Implementations must not use anonymous RNG or wall-clock inputs.
- Distribution sampling must be deterministic for identical inputs, including budget truncation decisions.

## Collapse Invariants
On collapse (dematerialization), engine must preserve:
- `sum(micro.part.mass_raw) == aggregate.total_mass_raw` within configured tolerance
- defect and wear distribution continuity within declared quantization tolerance
- batch lineage linkage continuity for all returned aggregates

Micro-only details that may persist after collapse:
- aggregate statistics only

Micro-only details that must not persist:
- per-instance transforms
- per-instance opaque IDs not represented in aggregate descriptors

## Epistemic Safety
- Micro entities only exist inside ROI materialization scope.
- Outside ROI:
  - TruthModel may retain macro aggregates
  - PerceivedModel must not imply per-bolt existence
- Inspection payloads must be quantized/redacted by visibility policy unless privileged inspection is explicitly allowed.

## Performance Constraint
- RS-5 budget caps maximum micro parts per ROI.
- If cap is exceeded, runtime must either:
  - refuse with `refusal.materialization.budget_exceeded` (strict mode), or
  - deterministically truncate in stable order.
- Truncation order is stable:
  - `ag_node_id`, `batch_id`, `index`
- Truncation decisions are recorded in run metadata.

## Process-Only Mutation
Canonical process IDs for MAT-7:
- `process.materialize_structure_roi`
- `process.dematerialize_structure_roi`

No direct UI/renderer mutation is allowed.

## Transition Invariant Integration
Expand/collapse transitions must emit invariant checks into RS-4 transition-event channels.
- expand check: generated micro mass vs source aggregate mass
- collapse check: collapsed aggregate mass vs removed micro mass

Strict-mode invariant violations:
- `refusal.transition.invariant_violation`

Non-strict numeric drift path:
- `exception.numeric_error_budget`

## Reenactment Contract Hooks
Each micro part instance records deterministic seed and provenance links so MAT-8 reenactment can reconstruct identical micro timelines for equivalent authoritative state.
