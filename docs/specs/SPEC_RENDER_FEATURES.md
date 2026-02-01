Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Render Feature Declaration Spec (REND0)

Render features are declarative and validated.
Every feature MUST declare requirements, fallback, and cost model.

## Feature Declaration Format (Canonical)

Each feature declaration MUST include:
- `feature_id`
- `requires` (RenderCaps predicate)
- `fallback` (feature_id or "collapse")
- `cost` (explicit cost model)

Example (pseudo):
```
feature_id: "volumetric_fog"
requires:
  caps:
    supports_compute: true
    max_storage_bytes: >= 262144
fallback: "fog_basic"
cost:
  ms_estimate: 1.2
  memory_kb: 512
  bandwidth_kb: 128
```

## Requirements

- `requires` MUST reference RenderCaps fields only.
- `fallback` MUST NOT require higher caps than the feature itself.
- `cost` MUST be present and bounded.
- Missing fallback is REFUSE.

## Validator Requirements

Validators MUST refuse a feature module if:
- `requires` is missing.
- `fallback` is missing.
- `cost` is missing or unbounded.
- `fallback` forms a cycle or points to an unknown feature.

## Prohibitions

- Ad-hoc feature enablement without a declaration is FORBIDDEN.
- Feature modules without cost models are FORBIDDEN.