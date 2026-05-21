Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional
Task: DOMINIUM-DOCTRINE-RECOVERY-MATRIX-01
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`
Machine Registry: `contracts/registry/governance/doctrine_recovery_matrix.json`
Schema: `contracts/governance/doctrine_recovery_matrix.schema.json`

# Dominium Doctrine Recovery Matrix

## 1. Non-Canonical Status

This matrix is a derived recovery and disposition projection. It does not
change canon, glossary meaning, authority order, intake law, ownership review,
or any protected planning doctrine.

When this document, its registry, validators, generated mirrors, status files,
or audit notes disagree with stronger doctrine, the stronger doctrine wins. The
matrix records how to classify and repair drift without silently rewriting
canon.

## 2. Recovery Floor

The recovery floor is:

1. `docs/canon/constitution_v1.md`
2. `docs/canon/glossary_v1.md`
3. `AGENTS.md`
4. task-scoped canonical planning, semantic, schema, contract, release, and
   policy artifacts named by the active task
5. operational registries, projections, mirrors, manifests, and generated
   evidence with intact provenance
6. chat summaries, remembered transcript claims, and uncommitted planning notes

Recovery never uses lower evidence to reinterpret higher authority. If multiple
same-tier authoritative sources conflict materially, the correct recovery is
quarantine plus review, not best-effort synthesis.

## 3. Drift Classes

| Drift Class | Meaning | Default Disposition |
| --- | --- | --- |
| `doc_drift` | A lower document, mirror, audit note, README, or status prose conflicts with stronger doctrine. | Preserve the stronger source; mark or repair only the lower artifact if in scope. |
| `generated_mirror_drift` | A generated mirror, projection, cache, build echo, or run artifact no longer matches its source. | Treat as evidence only; refresh or quarantine the mirror, never promote it to canon. |
| `validator_drift` | A validator or fixture enforces behavior that stronger doctrine does not authorize. | Repair the validator or fixture; escalate if contract meaning would change. |
| `status_file_drift` | A status, audit, report, queue, or latest-context surface disagrees with repo truth. | Preserve repo truth; mark the status stale or refresh through an allowed process. |
| `registry_projection_drift` | A machine registry or projection differs from the stronger doc or schema law it mirrors. | Restore projection lineage or quarantine material disagreement. |
| `same_tier_conflict` | Two same-tier authoritative sources make incompatible claims. | Stop autonomous recovery and route a review packet. |
| `ownership_split_drift` | A duplicated or transitional root is treated as the semantic owner by convenience. | Bind to the reviewed owner or keep scoped split/quarantine explicit. |

## 4. Recovery Actions

| Action ID | Action | Review Gate |
| --- | --- | --- |
| `preserve_higher_authority` | Use the higher authority source, record lower drift, and do not mutate protected canon. | `none_if_lower_artifact_only`; otherwise `protected_root_review` |
| `refresh_derived_projection` | Regenerate or edit a derived projection so it restates its source without new meaning. | `none_if_lower_artifact_only` |
| `repair_validator_contract` | Align validator or fixture behavior to the registry, schema, and stronger doctrine. | `contract_schema_review` if behavior meaning changes |
| `record_status_staleness` | Mark status or audit prose stale, superseded, or partial without claiming doctrine change. | `none_if_lower_artifact_only` |
| `quarantine_same_tier_conflict` | Preserve both candidates, stop autonomous resolution, and emit conflict evidence. | `quarantine_required` |
| `route_human_review` | Produce a bounded review packet for a protected root, ownership split, or policy change. | `human_review_required` |
| `refuse_silent_promotion` | Reject attempts to treat generated, projected, transitional, or status evidence as canon. | `human_review_required` if promotion is requested |

## 5. Protected Roots

The registry lists protected roots explicitly. The minimum protected set is:

- `docs/canon/**`
- `AGENTS.md`
- `docs/planning/AUTHORITY_ORDER.md`
- `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
- `docs/planning/MERGED_PROGRAM_STATE.md`
- `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`
- `docs/planning/GATES_AND_PROOFS.md`
- `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`
- `specs/reality/**`
- `schema/**`
- `docs/release/**`
- `release/**`
- `repo/**`
- `updates/**`
- `security/**`
- `build/**`
- `archive/generated/artifacts/**`
- `.xstack_cache/**`
- `run_meta/**`
- `docs/repo/FOUNDATION_LOCK.md`
- `.aide/context/latest-*`
- `.aide/reports/latest-*`
- `.aide/queue/current.toml`

Protected does not mean untouchable. It means recovery must identify explicit
scope, review gate, and provenance before any mutation. Generated protected
roots remain evidence only unless a stronger emission contract promotes a
specific artifact for a specific operational scope.

## 6. Surface Matrix

| Surface ID | Source Family | Drift Examples | Recovery / Disposition |
| --- | --- | --- | --- |
| `canon_root_governance` | Constitution, glossary, and `AGENTS.md` | Lower docs, validators, generated mirrors, or status notes claim different semantic meaning. | Preserve canon/glossary/AGENTS. Do not rewrite canon through recovery. Repair lower artifacts only when in scope; otherwise route review. |
| `planning_intake_authority` | P-0/P-series planning authority and gates | Generated planning mirrors, status files, or later docs conflict with intake law, authority order, gates, or ownership review. | Use planning authority inside its scope. Quarantine same-tier planning conflicts and keep execution gates visible. |
| `schema_contract_law` | `schema/**`, contract docs, contract-facing registries | Validator projections, schemas mirrors, or runtime convenience disagree with schema law or migration/refusal obligations. | Preserve schema law. Repair projections/validators or quarantine material disagreements; no silent migrations. |
| `governance_projection_surfaces` | Derived governance docs, mirrors, registries, adapter surfaces | Governance mirrors drift from `AGENTS.md` or claim canonical status. | Refresh derived projections and refuse silent promotion. `AGENTS.md` remains the execution governance owner. |
| `ownership_sensitive_roots` | `fields/field`, `schema/schemas`, `packs/data/packs`, `specs/data`, `docs/data` split families | A task binds to a projection, wrapper, or transitional root as semantic owner by convenience. | Apply `SEMANTIC_OWNERSHIP_REVIEW.md`; preserve scoped ownership and quarantine unresolved split claims. |
| `generated_evidence_surfaces` | `build/**`, `archive/generated/artifacts/**`, `.xstack_cache/**`, `run_meta/**` | Generated outputs are stale, missing provenance, or treated as doctrine because they are easier to parse. | Treat as evidence only. Refresh from source if allowed; otherwise record staleness or quarantine attempted promotion. |
| `validators_and_contract_tests` | `tools/validators/**`, `tests/contract/**`, fixtures | A validator accepts silent fallback, demotes protected authority, or rejects a lawful derived projection. | Repair validator and fixtures to enforce explicit authority, recovery action, and review gate contracts. |
| `status_and_audit_surfaces` | Audit notes, foundation/status docs, queue/latest-context reports | A status file claims progress, gate closure, or authority not supported by current repo artifacts. | Preserve repo truth, mark lower status stale, and avoid mutating forbidden latest-context or protected status files outside scope. |

## 7. Review Gates

| Gate ID | Required When |
| --- | --- |
| `none_if_lower_artifact_only` | Recovery edits only a lower derived artifact, does not touch protected roots, and does not change meaning. |
| `protected_root_review` | Recovery would touch a protected root or alter the interpretation of a protected source. |
| `contract_schema_review` | Recovery changes schema, contract, registry, migration, compatibility, or validator-facing meaning. |
| `ownership_review_required` | Recovery enters a split or transitional ownership family with unresolved scope. |
| `quarantine_required` | Same-tier conflict, insufficient evidence, missing provenance, or material projection drift blocks autonomous recovery. |
| `human_review_required` | Recovery would change canon meaning, authority order, release/trust policy, public policy, or promote generated/status evidence. |

## 8. Operational Use

Recovery steps must:

1. Classify the claim domain and drift class.
2. Rank candidate sources under authority order.
3. Identify the protected root and review gate, if any.
4. Apply the registry action without changing higher doctrine meaning.
5. Record evidence, validation, and any unrun checks honestly.

Recovery steps must not:

- create a competing governance canon
- treat generated outputs as canonical by convenience
- bind runtime, governance, release, or task work to quarantined roots silently
- repair status drift by editing forbidden latest-context files
- use validator success as permission to reinterpret doctrine
