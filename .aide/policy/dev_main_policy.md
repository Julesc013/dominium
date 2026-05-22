Status: DERIVED
Last Reviewed: 2026-05-22
Task: AIDE-DEV-MAIN-POLICY-01
Stability: provisional
Binding Sources: `AGENTS.md`, `.aide/policy/workflow_law.md`, `.aide/policy/branch_roles.md`, `.aide/policy/task_lifecycle.md`, `.aide/policy/blocker_taxonomy.md`, `.aide/policy/dirty_worktree_policy.md`, `.aide/policy/parallel_execution_law.md`, `.aide/policy/evidence_requirements.md`, `.aide/policy/warning_acceptance_policy.md`, `.aide/policies/branch-roles.yaml`, `.aide/policies/promotion-rules.yaml`, `.aide/policies/work-units.yaml`, `.aide/policies/recovery.yaml`

# AIDE Dev/Main/Checkpoint Policy

## Purpose

This file defines the minimum branch and promotion policy needed to run bounded
parallel Codex/AIDE work while preserving an evidence-backed `main`.

The controlling rule is:

```text
development is non-blocking
promotion is evidence-blocked
```

Task branches may keep making scoped progress, including classified partials.
`origin/dev` may integrate accepted work and repair work under policy. `origin/main`
receives only checkpointed, evidence-backed states with explicit warning
disposition and approval.

This policy is intentionally documentary and contract-facing. It does not
implement branch automation, scheduling, merge bots, repair engines, Workbench
Agent Board behavior, runtime modules, product features, or release publication.

## Branch Roles

### `origin/main`

Purpose:

- promoted truth
- public canonical history
- evidence-backed state only

Allowed:

- checkpoint-promoted commits
- release, tag, or pre-release states when release policy allows them
- policy-approved warning dispositions recorded by checkpoint evidence

Forbidden:

- raw task output
- unclassified partials
- unresolved conflicts
- broad feature claims without evidence
- dirty or accidental generated output
- direct task-to-main promotion

Promotion requirements:

- `checkpoint/<wave-id>` exists
- checkpoint validation completed and recorded
- warning disposition reviewed
- evidence packet exists
- human approval recorded unless a stronger repo policy explicitly permits automatic promotion
- no known unsafe blockers

### `origin/dev`

Purpose:

- integration branch for accepted task results
- non-final development truth
- place where partial progress may accumulate only when classified

Allowed:

- task outputs with evidence
- `PASS` and `PASS_WITH_WARNINGS` tasks
- `PARTIAL` tasks only when explicitly classified and non-dangerous
- repair branches
- coordinator status updates by the active coordinator task

Forbidden:

- unsafe or destructive states
- secret leakage
- corrupted contracts
- broken root layout
- hidden broad blockers
- undocumented generated noise
- raw conflicting task branches
- false implementation claims from docs, fixtures, or plans

Required before merge to dev:

- WorkUnit or task packet exists
- allowed and forbidden paths are declared
- status is `PASS`, `PASS_WITH_WARNINGS`, or policy-approved `PARTIAL`
- validation is appropriate to the task type
- changed files are known
- evidence refs are recorded
- warnings and blockers are classified
- no `BLOCKED_UNSAFE` blocker exists
- no forbidden path edits occurred unless the task explicitly allowed them
- coordinator files were not edited without ownership

### `local/dev`

Purpose:

- local integration mirror
- staging before pushing `origin/dev`
- local aggregation branch that may be dirtier than `origin/dev`

Rules:

- may accumulate local task merges and repair merges
- must be reconciled before checkpoint
- must not be treated as promoted truth without evidence
- may be reset or recreated only with explicit user approval or a documented safe procedure
- must preserve unrelated dirty work and classify it before integration

### `task/<task-id>`

Purpose:

- one task, one prompt, one Codex run, or one human WorkUnit

Rules:

- branch from `origin/main` or `origin/dev` as specified by the WorkUnit
- touch only allowed paths
- do not stage unrelated files
- produce evidence
- may end `PASS`, `PASS_WITH_WARNINGS`, `PARTIAL`, or `BLOCKED`
- never promote directly to `origin/main`

### `repair/<task-id>` Or `repair/<blocker-id>`

Purpose:

- fix one classified blocker

Rules:

- link to the source task, blocker, failed validation, or checkpoint finding
- keep allowed paths narrow
- produce repair evidence
- merge back to the source task branch or `dev` according to the blocker policy
- do not expand into feature work

### `checkpoint/<wave-id>`

Purpose:

- merge/proof branch before `main` promotion

Rules:

- collect selected task and dev state
- run checkpoint validation
- record warnings and blockers
- spawn repair branches when needed
- only a checkpoint branch may promote to `main`
- do not use the checkpoint branch for new feature development

### `quarantine/<reason>` Or `quarantine/<task-id>`

Purpose:

- isolate unsafe, corrupt, ownership-conflicted, or unmergeable work

Rules:

- no promotion
- evidence is retained
- exit requires human review, explicit retirement, or repair evidence
- quarantine refs must not be renamed as passing work

### `experiment/<name>`

Purpose:

- exploratory work not intended for promotion

Rules:

- cannot merge to `dev` or `main` without conversion into a task WorkUnit
- must not update queue/status as official progress
- must not make support claims

## Dev Integration Policy

A task may merge into `origin/dev` when all of the following are true:

- it has a WorkUnit or task packet
- allowed and forbidden paths are declared
- changed files are known
- status is `PASS`, `PASS_WITH_WARNINGS`, or policy-approved `PARTIAL`
- validation appropriate to the task type has run or is recorded as unavailable/not applicable
- evidence refs exist
- classified warnings are recorded before integration
- known warnings have warning disposition
- known blockers are classified
- no `BLOCKED_UNSAFE` blocker exists
- it does not edit coordinator files without ownership
- it does not silently broaden scope
- it does not make false implementation claims

`PARTIAL` work may merge to `origin/dev` only when:

- incomplete surfaces are explicitly marked `fixture_only`, `stubbed`, `partial`, or `planned`
- no product/runtime support claims are made
- no public stable surface is broken
- no migration or replacement is left half-applied
- a resume, repair, or follow-up WorkUnit is created or recorded

`PARTIAL` work must not promote to `origin/main` unless checkpoint policy
explicitly accepts it as non-runtime, inert, doc-only, or otherwise safe with
clear warnings.

## Main Promotion Policy

`origin/main` promotion requires a checkpoint.

Minimum requirements:

- `checkpoint/<wave-id>` exists
- included WorkUnits are listed
- excluded WorkUnits are listed
- validation plan has run
- validation results are recorded
- warnings are accepted or rejected
- blockers are resolved or accepted as non-blocking with rationale
- evidence packet exists
- promotion decision exists
- human approval exists unless repo policy explicitly permits automatic promotion
- no broad blockers are hidden

Release or trust-bearing promotion requires stronger proof:

- FAST/STRICT validation as applicable
- relevant contract and schema validators
- dependency-direction strict
- public surface validator
- product-spine validators where applicable
- compatibility, replay, or package tests where touched
- full CTest only when release/full-gate policy requires it

Full CTest remains T4/full-gate debt unless live repo evidence says otherwise.
It is not required for ordinary dev integration.

## Merge And Rebase Policy

- Task branches may rebase onto their declared base only when clean and owned by the operator.
- Public or shared branches must not be rewritten without explicit approval.
- `origin/dev` should prefer merge commits or controlled squash according to repo convention and evidence needs.
- Checkpoint branches may merge multiple task branches.
- Main promotion must preserve traceability to the checkpoint decision.
- Repair branches must reference their source blocker or task.
- Destructive git commands require explicit approval.

## Warning Acceptance

`.aide/policy/warning_acceptance_policy.md` is the base warning policy.
`.aide/policy/dev_warning_policy.md` specializes warning treatment for dev and
main.

Dev may accept warnings when they are classified, bounded, recorded, not hiding
a failed required proof, not claiming runtime implementation from fixture-only
work, and linked to follow-up or expiry where needed.

Main may accept warnings only when the checkpoint report includes them, the
promotion decision explains them, no warning contradicts support or release
claims, and human or policy approval exists.

`PASS_WITH_WARNINGS` must not be rewritten as `PASS` unless warnings are
resolved or policy classifies them as non-warning in the active scope.

## Coordinator File Ownership

Exclusive coordinator files:

- `.aide/queue/current.toml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`

Rules:

- only one active coordinator task may modify these at once
- parallel lane tasks write task-specific reports instead
- checkpoint/coordinator tasks merge task reports into latest status
- a non-coordinator task may edit these files only after declaring coordinator ownership

## Evidence Requirements

Dev integration evidence must record:

- WorkUnit or task packet ref
- branch/ref and base commit
- changed files
- validation commands and results
- warning dispositions
- blocker classification
- contract/schema impact
- coordinator file ownership status
- commit hash when committed

Main promotion evidence must additionally record:

- checkpoint branch
- included and excluded WorkUnits
- validation plan and results
- repair branches created and outcomes
- warning acceptance/rejection
- promotion decision
- approval source
- resulting commit

When `.aide/schema/work_unit.schema.json`,
`.aide/schema/checkpoint_candidate.schema.json`,
`.aide/schema/promotion_decision.schema.json`, or
`.aide/schema/warning_disposition.schema.json` are present, these policy records
should cross-reference those schema identities without taking ownership of the
schema definitions.

## Non-Goals

This policy does not implement:

- AIDE scheduler
- automatic task runner
- branch/worktree automation
- automatic merge or promotion engine
- repair engine
- Workbench Agent Board
- runtime modules
- runtime package mount
- provider runtime
- renderer
- native GUI
- gameplay
- release publication
- product feature work
