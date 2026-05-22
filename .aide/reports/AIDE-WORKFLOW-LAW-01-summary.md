Status: PASS_WITH_WARNINGS
Task: AIDE-WORKFLOW-LAW-01
Date: 2026-05-22

# AIDE-WORKFLOW-LAW-01 Summary

## Result

PASS_WITH_WARNINGS. AIDE workflow law is now defined as a provisional
machine-readable contract and derived development document.

## Added

- `contracts/aide/aide_workflow_law.v1.json`
- `.aide/policy/workflow_law.md`
- `.aide/policy/branch_roles.md`
- `.aide/policy/task_lifecycle.md`
- `.aide/policy/blocker_taxonomy.md`
- `.aide/policy/dirty_worktree_policy.md`
- `.aide/policy/parallel_execution_law.md`
- `.aide/policy/evidence_requirements.md`
- `.aide/policy/warning_acceptance_policy.md`
- `docs/development/aide/AIDE_WORKFLOW_LAW_01.md`
- `docs/repo/audits/AIDE_WORKFLOW_LAW_01.md`
- `tools/aide/check_workflow_law.py`

## Updated

- `.aide/queue/current.toml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`
- `.aide/ledgers/migration_ledger.jsonl`
- `contracts/public_surface/public_surface.contract.toml`

## Law Coverage

- Branch roles: `origin/main`, `origin/dev`, `local/dev`, `task/<task-id>`,
  `repair/<task-id>`, `checkpoint/<wave-id>`, `quarantine/<reason>`, and
  `experiment/<name>`
- Lifecycle states from `PROPOSED` through `PROMOTED_TO_MAIN`,
- `QUARANTINED`, and `SUPERSEDED`, including `CHECKPOINT_REPAIR`
- Required blocker classes from dirty worktree through source authority conflict
- Dirty-worktree policy
- Warning classification policy
- WorkUnit minimum fields
- Repair/resume behavior
- Task-to-dev, dev-to-checkpoint, and checkpoint-to-main gates
- Parallel-wave limits before and after later AIDE hardening

## Validation

Validation is recorded in
`.aide/reports/AIDE-WORKFLOW-LAW-01-validation.json`.

- AIDE doctor: PASS
- AIDE validate: PASS with known review-ref warnings
- Public surface strict: PASS
- Dependency-direction strict: PASS with known warnings and 0 violations
- Component matrix strict: PASS
- Portability matrix strict: PASS
- Docs sanity: PASS
- Fast strict: PASS
- Workflow law validator: PASS after this policy packet update

## Known Warnings

- Full CTest remains T4/full-gate debt.
- Dependency-direction warnings remain known with 0 violations.
- AIDE review-ref warnings may remain.
- Stale AuditX output warning remains.
- Broad product/runtime feature work remains blocked.

## Next

`AIDE-WORKUNIT-SCHEMA-01`.

Follow-ups:

- `AIDE-DEV-MAIN-POLICY-01`
- `AIDE-CHECKPOINT-LOOP-01`
- `AIDE-CAPABILITY-REALITY-LEDGER-01`
