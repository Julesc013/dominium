Status: DERIVED
Last Reviewed: 2026-05-22
Task: AIDE-CHECKPOINT-LOOP-01
Stability: provisional
Binding Sources: `.aide/policy/checkpoint_loop_law.md`, `.aide/policy/blocker_taxonomy.md`, `.aide/policy/task_lifecycle.md`, `.aide/schema/repair_task.schema.json`, `.aide/schema/resume_task.schema.json`

# AIDE Checkpoint Repair Policy

## Purpose

This file defines how checkpoint failures become repair, prerequisite, resume,
defer, or quarantine work.

Ordinary blockers are not terminal. Unsafe blockers are not repaired by
convenience.

## Create Repair WorkUnits

Create a repair WorkUnit when a checkpoint failure is:

- bounded to known files or policy surfaces
- inside allowed paths
- caused by parse failure, fixture mismatch, stale generated evidence, missing
  report fields, warning disposition gaps, or targeted validation failure
- fixable without changing product/runtime behavior outside the active scope
- fixable without semantic authority or human review decisions

Repair branches use:

```text
repair/<blocker-id>
repair/<task-id>
```

Repair evidence must include:

- source checkpoint ID
- blocker ID
- failed validation command
- changed files
- targeted validation rerun
- warning/blocker disposition after repair
- next action

## Create Prerequisite Tasks

Create a prerequisite task when the checkpoint cannot proceed because required
law, schema, tool, fixture, evidence, connector, secret, approval, or reviewed
decision is absent.

Missing prerequisite outcomes use:

```text
CHECKPOINT_BLOCKED_MISSING_PREREQ
```

The checkpoint must not fake prerequisite completion.

## Create Resume Tasks

Create a resume task when useful work exists but the current checkpoint must
pause for path ownership, coordinator ownership, validation time, review order,
or safe sequencing.

Resume tasks must record:

- source checkpoint ID
- last known good evidence
- remaining validation or review steps
- deferred warnings or blockers
- allowed paths for resume

## Quarantine Work

Quarantine work when a checkpoint exposes:

- `BLOCKED_UNSAFE`
- secret exposure
- unresolved destructive git requirement
- corrupt contract/schema meaning
- same-tier authority conflict
- unresolved ownership quarantine
- release/trust/publication decision without review
- false implementation or support claims that cannot be bounded safely

Quarantine branches use:

```text
quarantine/<reason>
quarantine/<task-id>
```

Quarantined work cannot promote until review, repair, or retirement clears the
quarantine.

## Defer Promotion

Defer promotion when work is not unsafe but cannot meet the active validation,
warning, evidence, or approval bar during the checkpoint pass.

Deferral must record:

- deferred WorkUnits
- blocker or warning IDs
- expiry or next review point
- resume or repair task IDs when useful
- retained checkpoint ref when retained

## Targeted Validation After Repair

After repair, rerun only the checks needed to prove the repaired surface plus
any dependency checks affected by the repair.

Targeted validation may include:

- JSON/TOML parse checks
- touched fixture validator
- touched policy validator
- previously failed command
- `git diff --check`
- higher tier checks when the repair affects higher tier surfaces

Do not claim full checkpoint pass from targeted repair validation unless the
checkpoint validation plan has been rerun or explicitly remains valid.

## Repeated Failures

Repeated failure policy:

- first bounded failure: create repair WorkUnit
- repeated same failure after repair: escalate to resume or prerequisite task
- repeated unsafe or authority-sensitive failure: quarantine or human decision
- flaky or timeout failure: classify as flaky before retrying; record retry
  count and evidence

Repeated failures must not be hidden by opening unrelated refactors.

## Non-Goals

This policy does not implement a repair engine, automatic branch creation,
automatic merging, test retry service, or scheduler.
