Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional
Task: AIDE-WORKFLOW-LAW-01
Result: PASS_WITH_WARNINGS

# AIDE-WORKFLOW-LAW-01

## Status

`PASS_WITH_WARNINGS`

Baseline commit: `8e5180e25 fix(repo): close structure canon sweep gates`.

Existing local workflow-law commit preserved: `2c29ea663 feat(aide): define workflow law`.

## Decision

Next task: `AIDE-WORKUNIT-SCHEMA-01`.

Alternate next task: `AIDE-DEV-MAIN-POLICY-01`.

Secondary follow-up: `AIDE-CHECKPOINT-LOOP-01`.

Additional follow-up: `AIDE-CAPABILITY-REALITY-LEDGER-01`.

Recommended parallel candidate: `PRESENTATION-CONTRACT-01`.

Large parallel execution authorized: `false`.

Limited parallel prompt generation authorized: `true`.

Limited parallel task execution authorized: `false` until non-overlapping allowed
paths and coordinator ownership are explicitly assigned.

## Files Inspected

- `git status --short --branch`
- `git log -8 --oneline --decorate`
- `.aide/queue/current.toml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`
- `docs/repo/FOUNDATION_LOCK.md`
- `docs/repo/audits/PRODUCT_SPINE_REVIEW_01.md`
- `docs/repo/audits/STATUS_RECONCILE_02.md` when present
- `AGENTS.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
- `docs/planning/AUTHORITY_ORDER.md`
- `docs/planning/MERGED_PROGRAM_STATE.md`
- `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`
- `docs/planning/GATES_AND_PROOFS.md`
- `docs/planning/POST_PI_EXECUTION_PLAN.md`
- `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`
- `docs/planning/PLAYER_DESIRE_ACCEPTANCE_MAP.md`
- `contracts/planning/final_prompt_inventory.json`
- `contracts/planning/dependency_graph_post_pi.json`
- `.aide/policies/branch-roles.yaml`
- `.aide/policies/work-units.yaml`
- `.aide/policies/recovery.yaml`
- `.aide/policies/promotion-rules.yaml`
- `.aide/policies/git-workflow.yaml`
- `.aide/policies/evidence.toml`

`specs/reality/` and `data/reality/` are absent in this live checkout; no
runtime or semantic-domain binding was inferred from those missing paths.

## Files Changed

- `.aide/policy/workflow_law.md`
- `.aide/policy/branch_roles.md`
- `.aide/policy/task_lifecycle.md`
- `.aide/policy/blocker_taxonomy.md`
- `.aide/policy/dirty_worktree_policy.md`
- `.aide/policy/parallel_execution_law.md`
- `.aide/policy/evidence_requirements.md`
- `.aide/policy/warning_acceptance_policy.md`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/current.toml`
- `.aide/reports/AIDE-WORKFLOW-LAW-01-summary.md`
- `.aide/reports/AIDE-WORKFLOW-LAW-01-validation.json`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`
- `contracts/aide/aide_workflow_law.v1.json`
- `docs/development/aide/AIDE_WORKFLOW_LAW_01.md`
- `docs/repo/audits/AIDE_WORKFLOW_LAW_01.md`
- `tools/aide/check_workflow_law.py`

## Doctrine Encoded

The policy packet encodes:

- branch roles for `origin/main`, `origin/dev`, `local/dev`, `task/<task-id>`,
  `repair/<task-id>`, `checkpoint/<wave-id>`, `quarantine/<reason>`, and
  `experiment/<name>`
- lifecycle states from `PROPOSED` through `PROMOTED_TO_MAIN`,
  `QUARANTINED`, and `SUPERSEDED`, including `CHECKPOINT_REPAIR`
- blocker taxonomy for dirty worktrees, validation failures, missing
  prerequisites/tools/connectors/capabilities/secrets, unsafe operations,
  destructive git, architecture/human review, timeouts, flaky tests, generated
  drift, stale queue/context packets, and source authority conflicts
- dirty-worktree handling that requires classification before blocking
- retry, repair, and resume policy
- evidence requirements per task type
- warning acceptance policy
- dev/checkpoint/main promotion overview
- limited versus large parallelism rules

## Validators Run

Recorded in `.aide/reports/AIDE-WORKFLOW-LAW-01-validation.json`.

The previous local workflow-law commit recorded fast strict as `PASS` with known
warnings. This corrective policy packet reruns lightweight validation only and
does not rerun full CTest.

## Warnings Preserved

- Full CTest remains T4/full-gate debt.
- Dependency-direction warnings remain known with 0 violations in prior strict
  evidence.
- Existing AIDE review-packet reference warnings remain classified.
- Stale AuditX output warning remains known.
- Product/runtime support gaps remain blocked and are not reclassified as
  implemented.
- WorkUnit schemas remain a follow-up, not completed by this task.

## Non-Goals Preserved

No full scheduler, automatic branch/worktree manager, automatic merge or
promotion engine, repair engine, Workbench Agent Board, runtime module loader,
runtime package mount, provider runtime, renderer, native GUI, gameplay,
release publication, product feature work, directory move, root layout change,
or application/runtime behavior change was implemented.

## Contract And Schema Impact

Contract impact changed only for AIDE workflow law:

```text
contracts/aide/aide_workflow_law.v1.json
```

No product/runtime schema or compatibility meaning changed.

## Next Tasks

- `AIDE-WORKUNIT-SCHEMA-01`
- `AIDE-DEV-MAIN-POLICY-01`
- `AIDE-CHECKPOINT-LOOP-01`
- `AIDE-CAPABILITY-REALITY-LEDGER-01`
