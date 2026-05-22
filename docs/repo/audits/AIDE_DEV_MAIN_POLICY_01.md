Status: DERIVED
Last Reviewed: 2026-05-22
Task: AIDE-DEV-MAIN-POLICY-01
Result: PASS_WITH_WARNINGS
Stability: provisional

# AIDE-DEV-MAIN-POLICY-01

## Status

`PASS_WITH_WARNINGS`

This task defined the minimum dev/main/checkpoint policy for bounded parallel
Codex/AIDE development. It ran in parallel-lane mode because no coordinator
ownership environment variable was present and the shared queue/latest packet
files were already dirty from sibling AIDE work.

Coordinator update deferred to checkpoint/coordinator task.

## Baseline

| Field | Value |
| --- | --- |
| initial baseline commit | `2c29ea663` |
| closeout HEAD before task commit | `971c58894` |
| branch at inspection | `main` |
| origin tracking | `main...origin/main` |
| coordinator mode | not detected |
| lane mode | parallel-lane |

## Files Inspected

- `git status --short --branch`
- `git log --oneline --decorate -n 12`
- `.aide/queue/current.toml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`
- `docs/repo/FOUNDATION_LOCK.md`
- `docs/repo/audits/PRODUCT_SPINE_REVIEW_01.md`
- `docs/repo/audits/STATUS_RECONCILE_02.md`
- `.aide/policy/workflow_law.md`
- `.aide/policy/branch_roles.md`
- `.aide/policy/task_lifecycle.md`
- `.aide/policy/parallel_execution_law.md`
- `.aide/policy/evidence_requirements.md`
- `.aide/policy/warning_acceptance_policy.md`
- `.aide/schema/work_unit.schema.json`
- `.aide/schema/checkpoint_candidate.schema.json`
- `.aide/schema/promotion_decision.schema.json`
- `.aide/schema/warning_disposition.schema.json`
- `.aide/policies/branch-roles.yaml`
- `.aide/policies/promotion-rules.yaml`
- `.aide/policies/work-units.yaml`
- `.aide/policies/recovery.yaml`
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
- `docs/reference/specs/reality/SPEC_DOMINIUM_UNIVERSAL_REALITY_FRAMEWORK.md`
- `docs/reference/specs/reality/SPEC_DOMAIN_CONTRACT_TEMPLATE.md`
- `contracts/abi/reality/SPEC_CAPABILITY_SURFACES.md`
- `docs/reference/specs/reality/SPEC_REPRESENTATION_LADDERS.md`
- `docs/reference/specs/reality/SPEC_FORMALIZATION_CHAIN.md`
- `docs/reference/specs/reality/SPEC_CROSS_DOMAIN_BRIDGES.md`
- `contracts/planning/final_prompt_inventory.json`
- `contracts/planning/dependency_graph_post_pi.json`
- existing AIDE validator/tool conventions under `tools/aide/`

Note: `specs/reality/` and `data/reality/` were not present as top-level roots
in the live worktree. The current Lambda reality specs were present under
`docs/reference/specs/reality/` and `contracts/abi/reality/`.

## Files Changed

- `.aide/policy/dev_main_policy.md`
- `.aide/policy/checkpoint_policy.md`
- `.aide/policy/parallel_worktree_policy.md`
- `.aide/policy/dev_warning_policy.md`
- `.aide/fixtures/dev_main/valid_dev_integration.json`
- `.aide/fixtures/dev_main/valid_checkpoint_decision.json`
- `.aide/fixtures/dev_main/invalid_main_promotion_without_evidence.json`
- `tools/aide/check_dev_main_policy.py`
- `.aide/reports/AIDE-DEV-MAIN-POLICY-01-validation.json`
- `docs/repo/audits/AIDE_DEV_MAIN_POLICY_01.md`

No product/runtime behavior changed.

## Policy Decisions

- `origin/main` is promoted truth and receives only checkpointed, evidence-backed states.
- `origin/dev` is non-final integration truth and may accept classified warnings or classified partials under policy.
- `local/dev` is a local staging mirror and is not promoted truth.
- `task/<task-id>` branches never promote directly to `main`.
- `repair/<task-id>` and `repair/<blocker-id>` branches must stay linked to classified blockers.
- `checkpoint/<wave-id>` is the only normal promotion path into `main`.
- `quarantine/<reason>` and `quarantine/<task-id>` branches isolate unsafe or unmergeable work.
- `experiment/<name>` branches cannot merge without conversion into a WorkUnit.
- `PARTIAL` work can land on `dev` only when incomplete surfaces are marked and no support claims are made.
- Main promotion requires checkpoint branch, validation evidence, warning disposition, promotion decision, and approval.
- Full CTest remains T4/full-gate debt unless release/full-gate policy requires it.
- Coordinator files are exclusive to one active coordinator task.

## Relationship To AIDE-WORKFLOW-LAW-01

This task extends `AIDE-WORKFLOW-LAW-01` without replacing it. The workflow law
defines the controlling doctrine: development is non-blocking and promotion is
evidence-blocked. This policy specializes that doctrine into concrete
dev/main/checkpoint branch rules, warning treatment, same-machine worktree
rules, and evidence requirements.

The existing workflow-law policy files were read and preserved.

## Relationship To AIDE-WORKUNIT-SCHEMA-01

The WorkUnit, checkpoint candidate, promotion decision, and warning disposition
schemas were present in the working tree as sibling task output. This task did
not edit or duplicate those schemas. The new policy documents reference those
schema identities when present and explicitly leave schema ownership to
`AIDE-WORKUNIT-SCHEMA-01`.

## Parallel Execution Readiness

This task is lane-safe:

- it did not edit `.aide/queue/current.toml`
- it did not edit latest task/review/status/warning packets
- it wrote only task-specific policy, fixture, validator, report, and audit artifacts
- it classified the existing coordinator/latest packet dirtiness as out of scope

Limited parallel task execution is policy-eligible only after:

- `AIDE-WORKFLOW-LAW-01` is complete
- `AIDE-WORKUNIT-SCHEMA-01` is complete
- `AIDE-DEV-MAIN-POLICY-01` passes
- coordinator ownership rules are active
- task paths are non-overlapping

Large parallel execution remains unauthorized.

## Warnings Preserved

- Full CTest not run; retained as T4/full-gate debt.
- Dependency-direction strict warnings remain known warning debt with prior zero-violation evidence.
- AIDE review-packet reference warnings remain accepted when AIDE validate passes.
- Stale AuditX output warning remains known RepoX debt.
- Runtime package mount, provider runtime, runtime module loader, Workbench shell, renderer, native GUI, gameplay/domain implementation, and release publication remain blocked.
- WorkUnit schema outputs are present as sibling/uncommitted work; this task references but does not own them.
- Coordinator update was deferred because this task ran in parallel-lane mode.

## Validation Commands Run

| Command | Result |
| --- | --- |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS_WITH_WARNINGS; known review-packet reference warnings |
| `py -3 .aide/scripts/aide_lite.py pack --help` | PASS; pack command available |
| `python -m tools.aide.validate` | unavailable; module not present |
| `python -m tools.aide.doctor` | unavailable; module not present |
| `python tools/aide/check_dev_main_policy.py .` | PASS |
| `python tools/aide/check_workflow_law.py .` | FAIL_OUT_OF_SCOPE; existing validator hardcodes old queue closeout fields and fails after live queue advanced to `AIDE-WORKUNIT-SCHEMA-01` |
| `python -m json.tool .aide/fixtures/dev_main/valid_dev_integration.json` | PASS |
| `python -m json.tool .aide/fixtures/dev_main/valid_checkpoint_decision.json` | PASS |
| `python -m json.tool .aide/fixtures/dev_main/invalid_main_promotion_without_evidence.json` | PASS |
| `py -3 .aide/scripts/aide_lite.py task status` | PASS; informational existing task status |
| `py -3 .aide/scripts/aide_lite.py task current` | PASS; informational current AIDE Lite task |
| `py -3 .aide/scripts/aide_lite.py git plan` | BLOCKED_DIRTY_TREE; dry-run helper reported dirty tree, and this task reverted its generated helper-plan output because `.aide/git` is outside scope |
| `git diff --check` | PASS |
| `git diff --check -- <task paths>` | PASS |

`py -3 .aide/scripts/aide_lite.py pack --task "AIDE-DEV-MAIN-POLICY-01"` was
not run because it writes `.aide/context/latest-task-packet.md`, and this task
does not own coordinator/latest packet mutation.

## Next Tasks

- `AIDE-CHECKPOINT-LOOP-01`
- `AIDE-CAPABILITY-REALITY-LEDGER-01`
- `PRESENTATION-CONTRACT-01`
