Status: DERIVED
Last Reviewed: 2026-05-22
Task: AIDE-WORKUNIT-SCHEMA-01
Result: PASS_WITH_WARNINGS

# AIDE-WORKUNIT-SCHEMA-01

## Status

`PASS_WITH_WARNINGS`

Baseline commit: `971c58894 reconcile(aide): advance status after workflow law`.

Current task: `AIDE-WORKUNIT-SCHEMA-01`.

Next task: `AIDE-DEV-MAIN-POLICY-01`.

Alternate next task: `AIDE-CHECKPOINT-LOOP-01`.

Secondary follow-up: `AIDE-CAPABILITY-REALITY-LEDGER-01`.

Recommended parallel candidate: `PRESENTATION-CONTRACT-01`.

Large parallel execution authorized: `false`.

Limited parallel task execution authorized: `false` until a future task set is
path-isolated and coordinator ownership is explicit.

## Files Inspected

- `git status --short --branch`
- `git log --oneline -n 12`
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
- `.aide/queue/current.toml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`
- `.aide/policy/workflow_law.md`
- `.aide/policy/branch_roles.md`
- `.aide/policy/task_lifecycle.md`
- `.aide/policy/blocker_taxonomy.md`
- `.aide/policy/dirty_worktree_policy.md`
- `.aide/policy/parallel_execution_law.md`
- `.aide/policy/evidence_requirements.md`
- `.aide/policy/warning_acceptance_policy.md`
- `docs/repo/audits/AIDE_WORKFLOW_LAW_01.md`
- `contracts/aide/aide_workflow_law.v1.json`
- representative existing schema files under `contracts/**` and `.aide/**`
- representative existing validators under `tools/aide/**` and
  `tools/validators/**`

`specs/reality/` and `data/reality/` are absent in this live checkout; no
semantic-domain or runtime binding was inferred from missing paths.

## Dirty Worktree Classification

The worktree contained AIDE workflow-law and status-reconciliation changes when
this task began; those are now represented by the parent commits
`54cf927dd aide: complete workflow law policy packet` and
`971c58894 reconcile(aide): advance status after workflow law`.

During validation, additional untracked AIDE dev/main and checkpoint-policy
files appeared outside this WorkUnit schema deliverable. They are classified as
path-disjoint follow-up-task evidence and are not staged by this task. No
destructive git command was used and no product/runtime files were edited.

## Files Changed

- `.aide/schema/work_unit.schema.json`
- `.aide/schema/task_attempt.schema.json`
- `.aide/schema/blocker.schema.json`
- `.aide/schema/evidence_packet.schema.json`
- `.aide/schema/repair_task.schema.json`
- `.aide/schema/resume_task.schema.json`
- `.aide/schema/checkpoint_candidate.schema.json`
- `.aide/schema/promotion_decision.schema.json`
- `.aide/schema/warning_disposition.schema.json`
- `.aide/schema/capability_reality_record.schema.json`
- `.aide/fixtures/work_unit/*.json`
- `.aide/policy/workunit_schema_law.md`
- `tools/aide/validate_workunits.py`
- `.aide/reports/AIDE-WORKUNIT-SCHEMA-01-validation.json`
- `docs/repo/audits/AIDE_WORKUNIT_SCHEMA_01.md`
- AIDE queue, status, warning, task-packet, and review-packet closeout surfaces

## Schemas Created

- WorkUnit
- TaskAttempt
- Blocker
- EvidencePacket
- RepairTask
- ResumeTask
- CheckpointCandidate
- PromotionDecision
- WarningDisposition
- CapabilityRealityRecord

The capability reality schema is only a small record shape. Capability reality
ledger policy and ledger population remain deferred to
`AIDE-CAPABILITY-REALITY-LEDGER-01`.

## Fixtures Created

- `valid_work_unit_minimal.json`
- `valid_task_attempt_minimal.json`
- `valid_blocker_repairable.json`
- `valid_evidence_packet_validation.json`
- `valid_repair_task.json`
- `valid_resume_task.json`
- `valid_checkpoint_candidate.json`
- `valid_promotion_decision.json`
- `invalid_work_unit_missing_task_id.json`
- `invalid_blocker_unknown_class.json`
- `invalid_promotion_missing_evidence.json`

## Validator Added

`tools/aide/validate_workunits.py` is a small dependency-free validator for this
schema slice. It checks:

- required schema files exist and parse
- valid fixtures pass
- invalid fixtures fail
- blocker schema classes match `.aide/policy/blocker_taxonomy.md`
- WorkUnit lifecycle status values match `.aide/policy/task_lifecycle.md`

It does not implement scheduling, task execution, branch automation, repair,
checkpoint, or promotion behavior.

## Validators Run

- `py -3 .aide/scripts/aide_lite.py doctor` - PASS
- `py -3 .aide/scripts/aide_lite.py validate` - PASS with known review-packet
  reference warnings
- `py -3 .aide/scripts/aide_lite.py pack --task "AIDE-WORKUNIT-SCHEMA-01"` -
  PASS, rewrote latest task packet; this task later replaced it with
  task-specific closeout content
- `py -3 -m tools.aide.validate_workunits --repo-root . --json-out .aide/reports/AIDE-WORKUNIT-SCHEMA-01-validation.json` -
  PASS
- JSON/TOML parse check for `.aide/schema/*.json`,
  `.aide/fixtures/work_unit/*.json`,
  `.aide/reports/AIDE-WORKUNIT-SCHEMA-01-validation.json`, and
  `.aide/queue/current.toml` - PASS
- `git diff --check` - PASS

Final lightweight validation results are recorded in this task closeout and
must not be read as full CTest or broad build evidence.

## Warnings Preserved

- Full CTest remains T4/full-gate debt.
- Existing AIDE review-packet reference warnings remain known.
- Stale AuditX output remains known prior RepoX warning.
- Product/runtime support gaps remain blocked and are not reclassified as
  implemented.
- WorkUnit schemas are schema/fixture/validator support only; they do not
  authorize broad parallel execution.

## Non-Goals Preserved

No scheduler, automatic task runner, branch/worktree automation, merge
automation, promotion automation, repair engine, Workbench Agent Board,
runtime module loader, runtime package mount, provider runtime, renderer,
native GUI, gameplay/domain implementation, release publication, product
feature work, source directory move, root layout change, broad build, or full
CTest was implemented.

## Contract And Schema Impact

AIDE schema impact changed. Product/runtime contract meaning did not change.

The new schemas are `.aide/schema/*.schema.json` and derive their lifecycle,
blocker, warning, evidence, checkpoint, and promotion vocabulary from
`AIDE-WORKFLOW-LAW-01`.

## Relationship To AIDE-WORKFLOW-LAW-01

`AIDE-WORKFLOW-LAW-01` remains the governing law. This task encodes its minimum
object model so AIDE can represent bounded work, attempts, blockers, evidence,
repairs, resumes, checkpoints, promotion decisions, warning dispositions, and
capability reality records without relying on chat memory.

Development remains non-blocking. Promotion remains evidence-blocked.

## Next Tasks

- `AIDE-DEV-MAIN-POLICY-01`
- `AIDE-CHECKPOINT-LOOP-01`
- `AIDE-CAPABILITY-REALITY-LEDGER-01`
