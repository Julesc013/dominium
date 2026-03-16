Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Entropy Policy

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: CANONICAL
Last Updated: 2026-03-04
Scope: PHYS-4 deterministic entropy and irreversibility doctrine.

## 1) Entropy Concept

Canonical diagnostic quantity:

- `quantity.entropy_index` (dimension policy: diagnostic scalar for deterministic gameplay irreversibility hooks)

Tracking scope:

- per assembly (for machine/component degradation)
- per network target (where routing/flow subsystems choose to map targets)
- per batch (materials/process transformations)

Invariant:

- entropy is not globally conserved
- entropy is monotonically non-decreasing by default
- entropy reduction is allowed only through explicit maintenance/repair process logs

## 2) Entropy Sources

Entropy contributions are model-driven and transformation-linked through registry mappings:

- friction/loss transforms
- combustion transforms
- plastic deformation stubs
- phase change irreversibility stubs
- additional irreversible source mappings may be added via registry extension

No silent inline entropy source math is permitted in domain runtime code.

## 3) Effects of Entropy

Entropy effect policies provide deterministic outputs:

- efficiency multiplier (permille)
- hazard multiplier (permille)
- maintenance interval modifier (permille)

Effect policies are profile-selectable and must be evaluated through entropy runtime hooks (not hardcoded mode flags).

## 4) Reset / Reduction

Maintenance or repair processes may reduce entropy when explicitly invoked:

- reduction amount is profile/policy controlled
- reset emits explicit `entropy_reset_event` records
- reset contributes to deterministic entropy reset hash chain

Silent reset is forbidden.

## 5) Physics Profile Defaults

Profile contract:

- `phys.realistic.default`:
  - `entropy_tracking = true`
  - `entropy_effect_policy_id = entropy_effect.basic_linear`
- `phys.realistic.rank_strict`:
  - `entropy_tracking = true`
  - `entropy_effect_policy_id = entropy_effect.strict`
  - `entropy_requires_efficiency_influence = true`
- `phys.lab.exotic`:
  - `entropy_tracking = false`
  - `entropy_effect_policy_id = entropy_effect.none`
  - entropy events remain loggable when explicitly requested by process/profile rules

## 6) Coupling Discipline

Cross-domain entropy coupling remains:

`Field/Flow/State -> ConstitutiveModel/Transformation -> Entropy contribution -> Entropy effects`

Direct domain-to-domain mutation remains forbidden.

## 7) Proof and Replay Hooks

When entropy rows/events are present, deterministic proof surfaces must include:

- `entropy_hash_chain`
- `entropy_reset_events_hash_chain`

Replay windows must reproduce:

- ordered entropy contribution events
- ordered reset events
- matching entropy hash chains for equivalent input windows

## 8) Non-goals

- no statistical thermodynamics solver
- no global PDE entropy simulation
- no wall-clock driven entropy updates
- no bypass of process-only mutation contract
