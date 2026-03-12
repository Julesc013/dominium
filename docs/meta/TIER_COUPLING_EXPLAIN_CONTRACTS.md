Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Tier/Coupling/Explain Contracts

Status: CANONICAL
Last Updated: 2026-03-06
Scope: META-CONTRACT-0/1 mandatory declarations and hard-gate enforcement for tier discipline, cross-domain coupling, and explainability.

## 1) Purpose

This contract freezes three mandatory declaration classes for all present and future domain/process families:

- Tier Contract
- Coupling Contract
- Explainability Contract

The objective is to make architectural completeness mechanically enforceable through schema, registry, RepoX, AuditX, TestX, and topology impact tooling.

## 2) Tier Contract (Mandatory)

Each subsystem/process family must declare a tier contract row containing:

- `supported_tiers`:
  - subset of `macro|meso|micro`
- `deterministic_degradation_order`:
  - total order used when budget pressure requires downgrade
  - order is deterministic, data-declared, and reproducible
- `cost_model_id`:
  - canonical cost accounting model id used for budget arbitration
- `micro_roi_requirements`:
  - optional declaration of ROI constraints when micro execution is supported
- `shard_safe`:
  - boolean declaration of cross-shard compatibility

Normative requirements:

- No runtime-local tier fallback logic outside declared degradation order.
- Downgrade/refusal outcomes must remain explicit and logged.

## 3) Coupling Contract (Mandatory)

All cross-domain influence must be declared through one of these legal mechanisms:

- constitutive model binding
- registered energy transformation
- registered field update policy
- registered signal/policy coupling

Direct cross-domain mutation is forbidden.

Mandatory coupling classes:

- `energy_coupling`
- `force_coupling`
- `info_coupling`
- `pollution_coupling`
- `safety_coupling`
- `compliance_coupling`

Normative requirements:

- Each coupling row declares:
  - source domain
  - target domain
  - mechanism kind
  - mechanism id
- Coupling declarations must reference existing registry/model/policy ids.
- Undeclared coupling is governance-invalid even if runtime behavior exists.

## 4) Explainability Contract (Mandatory)

Any hazard/failure/refusal event class must declare explainability requirements:

- `explain_artifact_type_id`
- bounded cause-chain keys
- bounded remediation hint keys
- required evidence inputs (decision logs, hazard rows, safety events, compliance rows, model outputs, etc.)

Explain artifacts are:

- derived only
- deterministic
- cacheable
- policy-redactable

Explain artifacts must not mutate authoritative truth.

## 5) Explain Artifact Contract

Canonical explain artifact includes:

- deterministic `explain_id`
- event/target identity binding
- bounded `cause_chain`
- bounded `referenced_artifacts`
- bounded `remediation_hints`
- deterministic fingerprint

Cache key contract:

- `H(event_id, truth_hash_anchor, epistemic_policy_id)`

Redaction contract:

- redaction depends on epistemic policy
- redaction must be deterministic for equivalent policy and input artifact

## 6) Governance and Enforcement Contract

RepoX strict invariants enforce declaration presence and undeclared coupling refusals.

AuditX emits targeted smells for:

- missing tier contract
- undeclared coupling
- missing explain contract
- missing cost model declaration

TestX validates:

- required declaration coverage for baseline domains
- deterministic explain artifact generation and redaction
- schema/registry integrity

STRICT hard-gate invariants:

- `INV-TIER-CONTRACT-REQUIRED`
- `INV-COST-MODEL-REQUIRED`
- `INV-COUPLING-CONTRACT-REQUIRED`
- `INV-EXPLAIN-CONTRACT-REQUIRED`
- `INV-NO-UNDECLARED-COUPLING`

Current baseline domain coverage:

- ELEC
- THERM
- MOB
- SIG
- PHYS
- FLUID

PROC-0 template coverage:

- Tier template:
  - `tier.proc.default`
  - lifecycle tier expectations:
    - exploration/defined: micro+meso
    - stabilized/certified: meso+macro
    - capsule: macro
    - drifted: micro+meso revalidation path
- Coupling templates:
  - `coupling.proc.capsule_to_chem.outputs`
  - `coupling.proc.qc_to_sig.report`
  - `coupling.proc.drift_to_sys.fidelity`
- Explain templates:
  - `explain.qc_failure`
  - `explain.drift_detected`
  - `explain.yield_drop`
  - `explain.process_refusal`

Topology/semantic-impact integration must include:

- tier/coupling/explain contract nodes
- coupling contract change -> affected domain suite escalation
- tier contract change -> performance envelope test escalation
- explain contract change -> explain engine test escalation

## 7) Non-Goals

- This contract does not introduce new solvers.
- This contract does not change simulation semantics.
- This contract does not authorize nondeterministic or wall-clock behavior.
- This contract does not relax process-only mutation.
