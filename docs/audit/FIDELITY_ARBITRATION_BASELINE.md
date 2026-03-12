Status: DERIVED
Last Reviewed: 2026-03-01
Scope: CTRL-5 unified fidelity and budget arbitration baseline
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Fidelity Arbitration Baseline

## Negotiation Algorithm
- Canonical engine: `src/control/fidelity/fidelity_engine.py`.
- Input:
  - list of `fidelity_request` rows for current tick
  - RS-5 envelope/runtime state
  - server/fairness policy context
- Deterministic request order:
  - `priority` (descending)
  - `requester_subject_id` (ascending)
  - `fidelity_request_id` (ascending)
- For each request:
  - attempt requested level if allowed and budget-satisfiable
  - deterministic fallback chain: `micro -> meso -> macro`
  - refuse with `refusal.ctrl.fidelity_denied` when no allowed level remains
- Outputs:
  - per-request `fidelity_allocation`
  - per-subject `budget_allocation_record`
  - deterministic arbitration fingerprint and decision-log entries

## Fairness Policies
- `fidelity.policy.default`:
  - deterministic priority-first allocation under envelope limits
- `fidelity.policy.rank_fair`:
  - per-subject equal baseline share first
  - deterministic leftover assignment using canonical order
  - no starvation under ranked equal-share stage
- `fidelity.policy.singleplayer_relaxed`:
  - relaxed single-subject behavior, still bounded by RS-5 envelope

## Domain Migration Summary
- MAT-7 materialization migrated to fidelity requests/allocation:
  - `src/materials/materialization/materialization_engine.py`
- MAT-9 inspection fidelity/depth budgeting migrated:
  - `src/inspection/inspection_engine.py`
  - `tools/xstack/sessionx/process_runtime.py`
- MAT-8 reenactment fidelity migrated:
  - `src/materials/commitments/commitment_engine.py`
  - `tools/xstack/sessionx/process_runtime.py`
- Domain-local inline downgrade chains removed from migrated paths; control now flows through CTRL-5 fidelity engine.

## Decision Log Integration
- Fidelity allocations are persisted as deterministic decision-log entries in process runtime state:
  - `fidelity_decision_entries`
- Each entry carries:
  - request/allocation linkage
  - downgrade reason
  - allocated cost
  - envelope/policy context

## Enforcement and Audit Hooks
- RepoX invariants:
  - `INV-NO-DOMAIN-FIDELITY-DOWNGRADE`
  - `INV-FIDELITY-USES-ENGINE`
- AuditX smells:
  - `SilentFidelityDowngradeSmell`
  - `UnboundedCostSmell`

## Gate Run Snapshot
- RepoX:
  - `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - `status=pass` (1 warning-only finding: AuditX high-risk threshold)
- AuditX:
  - `py -3 tools/xstack/auditx/check.py --repo-root . --profile STRICT`
  - `status=pass` (non-gating warning findings)
- TestX (CTRL-5 required subset):
  - `py -3 tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset test_fidelity_deterministic_allocation,test_micro_to_meso_downgrade,test_ranked_equal_share,test_cost_envelope_never_exceeded,test_domain_migration_equivalence`
  - `status=pass` (`selected_tests=5`)
- strict build (full xstack strict profile):
  - `py -3 tools/xstack/run.py strict --repo-root . --cache on`
  - `status=refusal` due pre-existing repository-baseline gates outside CTRL-5 scope (`compatx` findings, full-suite `testx` failures, packaging refusal)

## Topology Update
- Topology artifacts regenerated to include CTRL-5 contracts:
  - `docs/audit/TOPOLOGY_MAP.json`
  - `docs/audit/TOPOLOGY_MAP.md`

## Extension Points (MOB Micro Sim)
- MOB can submit `target_kind=vehicle|graph|region` requests directly to CTRL-5 without adding domain-local downgrade code.
- Ranked server policy can tune share computation through fidelity policy registry rows while preserving deterministic ordering.
- Future proof bundles can include fidelity arbitration fingerprints and per-tick allocation hashes.
