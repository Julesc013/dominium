Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# FIELD Shard Boundary Enforcement

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: normative  
Version: 1.0.0  
Scope: PHYS FIELD discipline for shard-safe deterministic execution

## 1) Core Rule
- Direct cross-shard field access is forbidden.
- A shard may read/write only its local authoritative field state.

## 2) Allowed Cross-Shard Mechanism
- Cross-shard field influence must flow through boundary artifacts only.
- Boundary artifacts must be deterministic and mergeable.
- Canonical pathway:
  `local field state -> boundary artifact emit -> deterministic merge -> target shard boundary application`

## 3) Mutation Discipline
- Field mutation is allowed only through:
1. `process.field_update`
2. declared constitutive model outputs that emit field updates
3. scheduled field update policy execution
- No domain/runtime module may mutate field storage directly.

## 4) Sampling Discipline
- Field reads must use standardized field sampling APIs.
- Sampling cache key is canonical:
  `(field_id, spatial_node_id, tick)`
- Derived/inspection consumers read `field_sample_rows` rather than bypassing field APIs.

## 5) Deterministic Merge Requirements
- Boundary artifacts are sorted deterministically before application.
- Merge order key:
  `(tick, portal_or_boundary_id, source_process_id)`
- Replay of identical inputs must reproduce:
  - `field_update_hash_chain`
  - `field_sample_hash_chain`
  - `boundary_field_exchange_hash_chain`

## 6) Governance
- RepoX strict gates:
  - `INV-FIELD-MUTATION-PROCESS-ONLY`
  - `INV-FIELD-SAMPLE-API-ONLY`
  - `INV-NO-CROSS-SHARD-FIELD-DIRECT`
- AuditX strict analyzers:
  - `DirectFieldWriteSmell`
  - `InlineFieldModifierSmell`
  - `CrossShardFieldAccessSmell`
