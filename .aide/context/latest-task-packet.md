# AIDE Latest Task Packet

## PHASE

AIDE-CHECKPOINT-LOOP-01 coordinator closeout

## GOAL

Define and verify the minimum AIDE checkpoint loop law, then reconcile
coordinator state without moving the queue backward from live repo evidence.

## WHY

Bounded parallel development needs an explicit checkpoint loop before task
branches can be merged into evidence-backed integration checkpoints and before
any checkpoint can be considered for `main` promotion.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/current.toml`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`
- `docs/repo/audits/AIDE_WORKFLOW_LAW_01.md`
- `docs/repo/audits/AIDE_WORKUNIT_SCHEMA_01.md`
- `docs/repo/audits/AIDE_DEV_MAIN_POLICY_01.md`
- `docs/repo/audits/AIDE_CHECKPOINT_LOOP_01.md`
- `docs/repo/audits/AIDE_CAPABILITY_REALITY_LEDGER_01.md`
- `.aide/policy/checkpoint_loop_law.md`
- `.aide/policy/checkpoint_validation_tiers.md`
- `.aide/policy/checkpoint_repair_policy.md`
- `.aide/policy/checkpoint_promotion_policy.md`
- `.aide/fixtures/checkpoint/`
- `tools/aide/check_checkpoint_loop.py`

## ALLOWED_PATHS

- `.aide/policy/`
- `.aide/fixtures/checkpoint/`
- `.aide/reports/AIDE-CHECKPOINT-LOOP-01-*`
- `.aide/queue/current.toml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`
- `docs/repo/audits/AIDE_CHECKPOINT_LOOP_01.md`
- `tools/aide/`

## FORBIDDEN_PATHS

- product/runtime implementation paths
- release publication paths
- broad build or source-layout roots
- Workbench implementation paths
- renderer, native GUI, gameplay, provider runtime, package runtime, and
  runtime module loader implementation paths

## IMPLEMENTATION

- Preserve the existing checkpoint-loop policy packet created by
  `acebb0f4f aide: define checkpoint loop policy`.
- Do not fake missing prerequisites; `AIDE-WORKFLOW-LAW-01`,
  `AIDE-WORKUNIT-SCHEMA-01`, and `AIDE-DEV-MAIN-POLICY-01` are present.
- Treat `AIDE-CAPABILITY-REALITY-LEDGER-01` as already present in live history
  at `3fdd78a3b`; do not move the queue backward.
- Update coordinator surfaces as a checkpoint/coordinator closeout only.

## VALIDATION

- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py pack --task "AIDE-CHECKPOINT-LOOP-01"`
- `py -3 -m tools.aide.validate_workunits --repo-root .`
- `py -3 tools/aide/check_dev_main_policy.py .`
- `py -3 tools/aide/check_checkpoint_loop.py .`
- `py -3 tools/aide/validate_capability_reality.py --repo-root . --summary-out .aide/reports/capability-reality-summary.md`
- `git diff --check`

## EVIDENCE

- changed files
- validation commands and results
- existing checkpoint-loop commit hash
- existing capability-ledger commit hash
- preserved warning disposition
- coordinator update decision

## NON_GOALS

- No scheduler.
- No automatic branch automation.
- No automatic merging.
- No automatic promotion to `main`.
- No repair engine.
- No Workbench Agent Board.
- No product/runtime behavior change.
- No full CTest or broad build.

## ACCEPTANCE

- Checkpoint loop law exists.
- Checkpoint validation tiers, repair policy, and promotion policy exist.
- Valid checkpoint and promotion fixtures pass targeted validation.
- Invalid checkpoint and promotion fixtures fail targeted validation.
- Promotion requires evidence.
- Unclassified promotion warnings are rejected.
- Coordinator surfaces reflect live repo evidence without hiding full-gate debt.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`,
`CHANGED_FILES`, `VALIDATION`, `WARNINGS`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 4050
- approx_tokens: 1013
- budget_status: PASS
- warnings:
  - none
