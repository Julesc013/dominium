Status: DERIVED
Last Reviewed: 2026-03-05
Supersedes: docs/system/SYSTEM_COMPOSITION_CONSTITUTION.md
Superseded By: none
Version: 1.1.0
Compatibility: SYS-1 interface signature, invariant, and macro model binding validation rules.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Interface and Invariant Rules

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Purpose
Define deterministic SYS-1 validation rules for system interfaces, boundary invariants, and macro model set bindings.

## A) InterfaceSignature Completeness Rules
Every system boundary interface must be complete and deterministic.

### Boundary Port Descriptor Requirements
Each boundary port descriptor must declare:

- `port_id`
- `port_type_id`
- `direction` (`in` | `out` | `bidir`)
- `allowed_bundle_ids` (registered quantity bundle IDs)
- `spec_limit_refs` (SPEC references used for rating checks)

### Signal Descriptor Requirements
Each signal descriptor must declare:

- `channel_type_id`
- `capacity`
- `delay`
- `access_policy_id`

### Interface-Level Requirements
Each interface signature must include:

- deterministic list of boundary port descriptors
- deterministic list of signal descriptors
- spec compliance reference surface compatible with SPEC-1 checks
- exposed boundary quantity bundles only from registered bundle sets

## B) BoundaryInvariant Evaluation Rules
Boundary invariants are declarative contracts over conserved/accounted quantities and tolerance policies.

Each invariant declaration must specify:

- conserved/accounted quantity IDs
- tolerance policy ID (`TOL` registry)
- whether boundary flux is allowed
- whether ledger transform is required for conservation accounting

Evaluation schedule:

- mandatory at `process.system_collapse`
- mandatory at `process.system_expand`
- optional periodic evaluation (budgeted, deterministic ordering)

Special rule:

- energy invariants require ledger transforms (`ledger_transform_required=true`)
- pollution-emitting systems must include pollution-accounting invariants

## C) Macro Model Binding Rules
Macro model sets used by capsules must be constitutive-model-based and boundary-signature-compatible.

Each macro model set must declare:

- model bindings consuming boundary inputs (port/signal quantities)
- model bindings producing boundary outputs/derived quantities/hazard hooks
- validity conditions (optional)
- error bound policy reference (`TOL`-compatible)
- required safety patterns for bounded safe operation

Validation requirements:

- every bound model must be registered
- model input/output signatures must match interface port IDs/channels
- model error bound policy must exist

## Determinism and Safety Constraints
- Validation ordering is deterministic (sorted by system_id, then stable key order).
- Validation failures must produce explicit refusal codes; no silent violations.
- SYS-1 introduces validation only and does not alter domain solver semantics.

## Spec and Safety Integration
- Interface validation must resolve `spec_compliance_ref` and port-level `spec_limit_refs` against registered SPEC types.
- Invariant-template-required safety patterns must be both:
  - declared by the system (`extensions.safety_pattern_ids`)
  - registered in the safety pattern registry.
- Missing required spec or safety declarations keep the system uncertifiable and force refusal on collapse/expand validation paths.
