Status: DERIVED
Last Reviewed: 2026-05-22
Task: AIDE-CHECKPOINT-LOOP-01
Result: PASS_WITH_WARNINGS
Stability: provisional
Binding Sources: `AGENTS.md`, `.aide/policy/workflow_law.md`, `.aide/policy/dev_main_policy.md`, `.aide/policy/checkpoint_policy.md`, `.aide/policy/workunit_schema_law.md`, `.aide/schema/checkpoint_candidate.schema.json`, `.aide/schema/promotion_decision.schema.json`, `.aide/schema/warning_disposition.schema.json`

# AIDE-CHECKPOINT-LOOP-01

## Status

`PASS_WITH_WARNINGS`

This task defines the minimum checkpoint loop law needed to assemble bounded
task-branch work into checkpoint candidates, validate the checkpoint, create
repair/resume/prerequisite work, classify warnings, and decide whether a
checkpoint may promote to `origin/main`.

It ran in parallel-lane mode. Coordinator update deferred to
checkpoint/coordinator task.

## Baseline

| Field | Value |
| --- | --- |
| intake branch | `main` |
| intake HEAD | `2c29ea663 feat(aide): define workflow law` |
| closeout-observed HEAD | `971c58894 reconcile(aide): advance status after workflow law` |
| coordinator mode | not claimed |
| lane mode | parallel-lane |
| full CTest | not run; T4/full-gate debt |

The worktree changed while this task was running because sibling AIDE prerequisite
work landed in the local working tree. This task consumed the resulting
`AIDE-WORKUNIT-SCHEMA-01` and `AIDE-DEV-MAIN-POLICY-01` audits as live
worktree evidence, but did not edit coordinator/latest packet files.

## Files Inspected

- `git status --short --branch`
- `git log --oneline -n 12`
- `.aide/queue/current.toml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`
- `docs/repo/FOUNDATION_LOCK.md`
- `docs/repo/audits/PRODUCT_SPINE_REVIEW_01.md`
- `docs/repo/audits/AIDE_WORKFLOW_LAW_01.md`
- `docs/repo/audits/AIDE_WORKUNIT_SCHEMA_01.md`
- `docs/repo/audits/AIDE_DEV_MAIN_POLICY_01.md`
- `.aide/policy/workflow_law.md`
- `.aide/policy/dev_main_policy.md`
- `.aide/policy/checkpoint_policy.md`
- `.aide/policy/parallel_worktree_policy.md`
- `.aide/schema/work_unit.schema.json`
- `.aide/schema/checkpoint_candidate.schema.json`
- `.aide/schema/promotion_decision.schema.json`
- `.aide/schema/warning_disposition.schema.json`
- existing AIDE tool/validator/test locations under `tools/aide/`,
  `tools/validators/aide/`, and `tests/contract/aide/`
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

`specs/reality/` and `data/reality/` were checked and are absent in this live
checkout. Current Lambda reality specs are under `docs/reference/specs/reality/`
and `contracts/abi/reality/` as recorded by the dev/main audit.

## Files Changed

- `.aide/policy/checkpoint_loop_law.md`
- `.aide/policy/checkpoint_validation_tiers.md`
- `.aide/policy/checkpoint_repair_policy.md`
- `.aide/policy/checkpoint_promotion_policy.md`
- `.aide/fixtures/checkpoint/valid_checkpoint_candidate_minimal.json`
- `.aide/fixtures/checkpoint/valid_checkpoint_candidate_with_repair.json`
- `.aide/fixtures/checkpoint/valid_promotion_decision_promote.json`
- `.aide/fixtures/checkpoint/valid_promotion_decision_defer.json`
- `.aide/fixtures/checkpoint/invalid_checkpoint_missing_validation_plan.json`
- `.aide/fixtures/checkpoint/invalid_promotion_missing_evidence.json`
- `.aide/fixtures/checkpoint/invalid_promotion_unclassified_warning.json`
- `tools/aide/check_checkpoint_loop.py`
- `docs/repo/audits/AIDE_CHECKPOINT_LOOP_01.md`

No product/runtime behavior changed.

## Policies Created

- `checkpoint_loop_law.md` defines source selection, candidate creation,
  WorkUnit inclusion/exclusion, validation, repair, warning disposition,
  promotion decision, quarantine/defer, coordinator update, evidence, and
  safety rules.
- `checkpoint_validation_tiers.md` defines T0 through T4 validation tiers and
  states that T4 is not required for ordinary dev checkpoints.
- `checkpoint_repair_policy.md` defines repair, prerequisite, resume,
  quarantine, defer, targeted validation, and repeated-failure policy.
- `checkpoint_promotion_policy.md` defines promotion decision requirements,
  minimum main-promotion evidence, warning acceptance, human approval,
  rollback/defer/quarantine outcomes, and audit requirements.

## Fixtures Created

- `valid_checkpoint_candidate_minimal.json`
- `valid_checkpoint_candidate_with_repair.json`
- `valid_promotion_decision_promote.json`
- `valid_promotion_decision_defer.json`
- `invalid_checkpoint_missing_validation_plan.json`
- `invalid_promotion_missing_evidence.json`
- `invalid_promotion_unclassified_warning.json`

The fixtures are intentionally tiny and live under `.aide/fixtures/checkpoint/`.

## Validator Added

`tools/aide/check_checkpoint_loop.py` validates:

- required checkpoint-loop policy files exist
- validation tiers are defined
- repair and promotion policy snippets are present
- valid checkpoint candidates pass
- invalid checkpoint candidates fail
- valid promotion decisions pass
- promotion without evidence fails
- promotion with unclassified warnings fails

It does not implement scheduler, branch automation, merge automation,
promotion automation, or a repair engine.

## Relationship To Prerequisites

- `AIDE-WORKFLOW-LAW-01`: consumed as governing doctrine. Development remains
  non-blocking and promotion remains evidence-blocked.
- `AIDE-WORKUNIT-SCHEMA-01`: consumed as the object schema layer for WorkUnits,
  checkpoint candidates, promotion decisions, and warning dispositions.
- `AIDE-DEV-MAIN-POLICY-01`: consumed as the branch and dev/main promotion
  policy. This task specializes its checkpoint path without replacing it.

## Warning Disposition

Warnings preserved:

- Full CTest not run; retained as T4/full-gate debt.
- Dependency-direction strict warnings remain known prior warning debt with
  zero-violation evidence.
- AIDE Lite coordinator validation currently fails on out-of-scope latest task
  packet structure; this task did not edit coordinator/latest packet files.
- Stale AuditX output remains known RepoX debt.
- Runtime package mount, provider runtime, runtime module loader, Workbench
  shell, renderer, native GUI, gameplay/domain implementation, and release
  publication remain blocked.
- Coordinator update was deferred because this task ran in parallel-lane mode.

## Validation Commands Run

| Command | Result |
| --- | --- |
| `py -3 .aide/scripts/aide_lite.py doctor` | FAIL; reports validation should be run because current AIDE Lite validation is failing |
| `py -3 .aide/scripts/aide_lite.py validate` | FAIL; current latest task packet is missing required `EVIDENCE` section and review refs warn |
| `py -3 .aide/scripts/aide_lite.py pack --task "AIDE-CHECKPOINT-LOOP-01 prerequisite check"` | PASS but writes latest task packet; generated content was reverted and pack was not rerun |
| `python -m tools.aide.doctor` | unavailable; module not present |
| `python -m tools.aide.validate` | unavailable; module not present |
| `py -3 -m tools.aide.validate_workunits --repo-root .` | PASS |
| `py -3 tools/aide/check_dev_main_policy.py .` | PASS |
| `py -3 tools/aide/check_checkpoint_loop.py .` | PASS |
| `python -m json.tool .aide/fixtures/checkpoint/valid_checkpoint_candidate_minimal.json` | PASS |
| `python -m json.tool .aide/fixtures/checkpoint/valid_promotion_decision_promote.json` | PASS |
| `git diff --check` | PASS |

Full CTest and broad builds were not run.

## Limited Parallel Development

Limited parallel development is now better defined at the policy level:

- prerequisites exist in the worktree
- dev/main policy defines branch roles and coordinator ownership
- checkpoint-loop policy defines validation, repair, warning disposition, and
  promotion decision requirements

Limited parallel task execution still requires explicit coordinator ownership,
path isolation, and checkpoint/coordinator closeout. This lane task did not
authorize large parallel execution.

## Non-Goals Preserved

No full AIDE scheduler, automatic task runner, automatic branch/worktree
automation, automatic merging, automatic main promotion, repair engine,
Workbench Agent Board, runtime modules, runtime package mount, provider
runtime, renderer, native GUI, gameplay, release publication, product feature
work, source directory move, broad build, or full CTest was implemented.

## Next Tasks

- `AIDE-CAPABILITY-REALITY-LEDGER-01`
- `PRESENTATION-CONTRACT-01`
- `PROJECTION-CONFORMANCE-01`
- `POINTER-WIDTH-SERIALIZATION-AUDIT-01`

Coordinator update deferred to checkpoint/coordinator task.
