Status: BASELINE
Last Reviewed: 2026-03-05
Supersedes: docs/system/SYSTEM_COMPOSITION_CONSTITUTION.md
Superseded By: none
Version: 1.0.0
Compatibility: SYS-2 macro capsule behavior execution contract.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# MacroCapsule Behavior Model

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Purpose
Define deterministic SYS-2 runtime behavior for collapsed Systems so macro capsules remain active, bounded, auditable boundary models.

## A) MacroCapsule Execution Loop
Per canonical tick, for capsules in `tier_mode=macro`:

1. Enumerate active capsules in deterministic order (`capsule_id` ascending).
2. Validate capsule interface and macro model set compatibility (cached where possible).
3. Gather boundary inputs deterministically:
   - boundary flow quantities by declared interface ports
   - signal channel inputs
   - safety state and declared hazard hooks
   - optional declared field samples
4. Compute deterministic `boundary_inputs_hash`.
5. Evaluate capsule macro model set through META-MODEL constitutive model execution only.
6. Translate outputs into process-governed effects:
   - `process.flow_adjust`
   - `process.effect_apply`
   - energy transform pathway (ledger-accounted)
   - `process.pollution_emit` when emission outputs are declared
7. Update capsule internal runtime state vector deterministically.
8. Emit bounded derived macro output observations for replay/proof.

Constraints:
- No direct truth mutation outside process/runtime commit boundaries.
- No wall-clock usage.
- No bespoke per-object macro solver branch.

## B) Error Bounds and Validity
Each `macro_model_set` must declare:

- `error_bound_policy_id`
- optional `validity_conditions`

Evaluation must compute:

- per-capsule residual/error estimate against declared policy
- validity status against declared conditions

Policy behavior when exceeded:

- either trigger forced expand (`reason_code=error_bound_exceeded`), or
- apply deterministic degraded outputs, if explicitly policy-allowed.

No silent over-bound operation is permitted.

## C) Forced Expand Triggers
Forced expand request is required when any of the following apply:

- near-failure hazard threshold (from safety/reliability hooks)
- explicit inspection/fidelity request from control-plane
- required safety pattern requires higher-fidelity branch
- macro model validity condition violated
- model error bound exceeded

Forced expand outcomes:

- approved: emit canonical forced-expand event and transition request.
- denied: deterministic refusal + fail-safe macro output profile + decision log.

## D) Safety and Compliance
Macro capsule fail-safe contract:

- if uncertainty is over policy bound, capsule must refuse unsafe output or shut down deterministically.
- fail-safe outputs must still respect boundary invariants and process discipline.

Required explain surfaces for SYS-2:

- forced expand explanation
- safety shutdown explanation
- output degradation explanation

These are derived artifacts referencing canonical events and policy identifiers.

## Determinism and Replay Guarantees
- Deterministic ordering: capsule IDs, model bindings, and output application sequence are stable.
- Named RNG is disallowed by default for SYS-2 macro behavior; any stochastic policy must be explicitly declared and proof-logged.
- Macro output records are derived/compactable; forced-expand events remain canonical.

## Non-Goals
- No replacement of domain semantics.
- No CFD or bespoke dynamics solver.
- No hidden capsule state outside declared internal state vector/runtime state rows.
