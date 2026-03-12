Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Stability Classification

## Purpose

Stability classification prevents two failure modes:

- provisional MVP stubs silently becoming permanent untracked debt
- stable semantics drifting without the required contract/version discipline

The classification is metadata-only. It must not change runtime semantics, execution order, or capability decisions by itself.

## Stability Classes

### `stable`

Use `stable` only when the item's semantics are frozen under an explicit semantic contract.

Requirements:

- semantics are frozen under the declared semantic contract version
- any semantic change requires:
  - COMPAT-SEM contract bump
  - migration plan if persisted data depends on the item
  - regression baseline update when fingerprints or behavior change

### `provisional`

Use `provisional` for MVP stubs, evolving registries, incomplete generators, and intentionally temporary default implementations.

Requirements:

- the item must declare:
  - `future_series`
  - `replacement_target`
- behavior may change without a contract bump
- behavior changes must still update regression baselines when the observable output or deterministic hashes change

### `experimental`

Use `experimental` only for explicitly gated items.

Requirements:

- the item must be enabled only by explicit profile or entitlement gating
- the item must emit an exception event when activated or used
- the item may be removed or changed without compatibility guarantees

Experimental gating metadata is carried through `stability.extensions`:

- `profile_gate_id` or `entitlement_gate_id`
- `exception_event_id`

## Required Metadata

Each tagged item must carry a `stability` object with:

- `schema_version`
- `stability_class_id`
- `rationale`
- `future_series`
  - required for `provisional`
  - optional otherwise
- `replacement_target`
  - required for `provisional`
  - optional otherwise
- `contract_id`
  - required for `stable`
  - optional otherwise
- `deprecated`
  - optional boolean
- `deterministic_fingerprint`
- `extensions`

Rules:

- `schema_version` for the embedded stability marker is `1.0.0`
- `deterministic_fingerprint` is computed with the fingerprint field blanked
- the containing registry-entry fingerprint must include the normalized `stability` object
- unknown `extensions` fields are allowed but must serialize deterministically

## Applicability

### Mandatory

- registry entries
- generator model registries

### Recommended

- `pack.compat` manifests
- artifact manifests
- profile and install manifests that participate in deterministic bundle identity

## Class Discipline

### Stable Discipline

For `stable` items:

- do not change semantic meaning in place
- do not repurpose IDs
- if persisted artifacts depend on the item, provide migration or explicit refusal before changing it

### Provisional Discipline

For `provisional` items:

- be explicit about where the item is expected to evolve
- do not leave `future_series` or `replacement_target` blank
- do not treat `provisional` as a permanent default; it is a tracked replacement obligation

### Experimental Discipline

For `experimental` items:

- gating must be explicit
- activation/use must be inspectable through exception logging
- silent activation is forbidden

## Determinism Rules

- stability metadata must be normalized before hashing
- validation output must be deterministic for identical input files
- adding or changing stability metadata may change registry fingerprints, but must not change simulation semantics by itself

## Initial MVP Posture

The initial rollout is intentionally conservative:

- default to `provisional`
- keep `stable` small and explicit
- avoid introducing `experimental` unless a real explicit gate already exists

## Enforcement Summary

META-STABILITY-0 enforcement requires:

- registry entries in the scoped families must carry `stability`
- `stable` requires `contract_id`
- `provisional` requires `future_series` and `replacement_target`
- `experimental` requires explicit gate metadata and exception logging metadata
