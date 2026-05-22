# AIDE Latest Task Packet

## PHASE

Post-WorkUnit-schema dev/main policy hardening.

## GOAL

`AIDE-DEV-MAIN-POLICY-01` - define the explicit dev/main/checkpoint promotion
policy that consumes `AIDE-WORKFLOW-LAW-01` and the WorkUnit schema layer.

## WHY

`AIDE-WORKUNIT-SCHEMA-01` provides durable objects for WorkUnits, attempts,
blockers, evidence, repair/resume tasks, checkpoints, promotion decisions,
warning dispositions, and capability reality records. The next gap is policy
for how bounded task branches may integrate to dev and how checkpoint evidence
may later support main promotion without authorizing automatic branch mutation.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/current.toml`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`
- `.aide/policy/workflow_law.md`
- `.aide/policy/branch_roles.md`
- `.aide/policy/task_lifecycle.md`
- `.aide/policy/blocker_taxonomy.md`
- `.aide/policy/parallel_execution_law.md`
- `.aide/policy/evidence_requirements.md`
- `.aide/policy/warning_acceptance_policy.md`
- `.aide/policy/workunit_schema_law.md`
- `.aide/schema/work_unit.schema.json`
- `.aide/schema/task_attempt.schema.json`
- `.aide/schema/blocker.schema.json`
- `.aide/schema/evidence_packet.schema.json`
- `.aide/schema/checkpoint_candidate.schema.json`
- `.aide/schema/promotion_decision.schema.json`
- `docs/repo/audits/AIDE_WORKFLOW_LAW_01.md`
- `docs/repo/audits/AIDE_WORKUNIT_SCHEMA_01.md`
- `contracts/aide/aide_workflow_law.v1.json`

## ALLOWED_PATHS

- `.aide/policy/`
- `.aide/schema/` only for narrow schema alignment if required
- `.aide/fixtures/` only for narrow policy fixture alignment if required
- `.aide/queue/current.toml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`
- `.aide/reports/AIDE-DEV-MAIN-POLICY-01-*`
- `.aide/ledgers/`
- `docs/repo/audits/AIDE_DEV_MAIN_POLICY_01.md`
- `tools/aide/` only for targeted policy validation

## FORBIDDEN_PATHS

- product/runtime implementation paths
- package runtime
- replay runtime
- provider runtime
- runtime module loader
- Workbench shell
- renderer/native GUI
- gameplay/domain implementation
- release publication
- branch automation, force-push automation, direct main-promotion automation

## IMPLEMENTATION

- Define policy before automation.
- Keep dev as integration evidence, not canonical truth.
- Keep main promotion checkpointed, reviewed, and evidence-blocked.
- Use WorkUnit, CheckpointCandidate, PromotionDecision, and WarningDisposition
  objects as policy inputs.
- Preserve broad blockers and warning debt.

## VALIDATION

- AIDE doctor/validate when available
- targeted WorkUnit schema validator when relevant
- JSON/TOML parse checks for touched machine-readable files
- `git diff --check`

Do not run full CTest or broad builds unless a future prompt explicitly raises
validation level.

## EVIDENCE

- changed files
- policy documents added or updated
- validator commands and results
- known warnings and warning dispositions
- queue/status packet changes
- non-goals preserved

## NON_GOALS

- no scheduler
- no automatic branch/worktree automation
- no automatic merge or promotion engine
- no repair engine
- no Workbench Agent Board
- no product/runtime feature work
- no release publication

## ACCEPTANCE

- dev/main/checkpoint policy is explicit and derives from workflow law
- policy consumes WorkUnit schema objects without implementing automation
- large parallel execution remains blocked unless future gates explicitly open it
- broad feature blockers remain visible

## NEXT_AFTER

Expected follow-up: `AIDE-CHECKPOINT-LOOP-01`.

Secondary follow-up: `AIDE-CAPABILITY-REALITY-LEDGER-01`.

Recommended parallel candidate: `PRESENTATION-CONTRACT-01`, only with explicit
path isolation and coordinator ownership.

## OUTPUT_SCHEMA

Return compact closeout with `STATUS`, `SUMMARY`, `COMMITS`,
`CHANGED_FILES`, `VALIDATION`, `WARNINGS`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- approx_tokens: 850
- budget_status: PASS
