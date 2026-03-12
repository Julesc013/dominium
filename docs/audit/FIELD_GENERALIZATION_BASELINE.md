Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Field Generalization Baseline

Status: BASELINE
Last Updated: 2026-03-04
Scope: PHYS-2 completion baseline for deterministic generalized fields.

## 1) Field Catalog

Canonical registered field set (PHYS-2):

- `field.temperature`
- `field.gravity_vector`
- `field.radiation_intensity`
- `field.magnetic_flux_stub`
- `field.irradiance`

Compatibility aliases retained:

- `field.gravity.vector`
- `field.radiation`

## 2) Update Policies

Registered policy IDs:

- `field.static_default` (`F0`)
- `field.scheduled_linear` (`F1`)
- `field.profile_defined` (`F0`, process-updatable)
- compatibility aliases: `field.static`, `field.scheduled`

Policy enforcement:

- process updates are allowed only when policy permits (`allow_process_field_update` / profile-defined).

## 3) Coupling Contract

Coupling remains model-only:

- models read fields through input signatures
- models emit effects/hazards/flow adjustments/derived outputs
- field mutation from model outputs routes through `process.field_update`

RepoX additions:

- `INV-FIELD-TYPE-REGISTERED`
- `INV-FIELD-MUTATION-THROUGH-PROCESS`

AuditX additions:

- `DirectFieldWriteSmell`
- `UnregisteredFieldSmell`

## 4) Runtime Determinism Highlights

- field update path centralized in `_apply_field_updates`
- deterministic ordering on field IDs and spatial node IDs
- deterministic sample records in `field_sample_rows`
- model-evaluated field updates now persisted to authoritative field state and metadata

## 5) Shard Rules

Shard doctrine documented in `docs/physics/FIELD_SHARD_RULES.md`:

- no direct cross-shard field reads/writes
- boundary artifact exchange only
- deterministic merge required

## 6) PHYS-3 Readiness

This baseline is ready for PHYS-3 ledger/transformation integration with:

- canonical field catalog in registries
- process-only mutation guardrails
- model coupling discipline
- deterministic sample substrate for proof/replay

## 7) Gate Execution

Validation status for this change set:

- RepoX STRICT: pass (warnings only; no refusal/fail findings)
- AuditX STRICT: fail (pre-existing promoted `E179_INLINE_RESPONSE_CURVE_SMELL` blockers outside PHYS-2 delta)
- TestX PHYS-2 targeted: pass
  - `test_field_sampling_deterministic`
  - `test_field_update_policy_respected`
  - `test_gravity_force_model_applies`
  - `test_no_direct_field_mutation`
  - `test_cross_platform_field_hash`
- strict build: not run in this pass
- topology map refresh: complete (`docs/audit/TOPOLOGY_MAP.json` regenerated)
