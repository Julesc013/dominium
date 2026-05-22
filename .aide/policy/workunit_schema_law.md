Status: DERIVED
Last Reviewed: 2026-05-22
Task: AIDE-WORKUNIT-SCHEMA-01
Stability: provisional
Binding Sources: `AGENTS.md`, `.aide/policy/workflow_law.md`, `.aide/policy/task_lifecycle.md`, `.aide/policy/blocker_taxonomy.md`, `.aide/policy/evidence_requirements.md`, `.aide/policy/parallel_execution_law.md`, `contracts/aide/aide_workflow_law.v1.json`

# AIDE WorkUnit Schema Law

## Purpose

AIDE needs structured task objects because prompts, status packets, blocker
notes, and commit messages are not durable enough to coordinate bounded
parallel development. A WorkUnit records the task identity, allowed scope,
branch role, required reads, validation plan, blockers, attempts, warnings,
evidence, and next actions in a shape that tools can inspect without treating
free-form prose as source truth.

This law implements the workflow-law rule:

```text
development is non-blocking
promotion is evidence-blocked
```

It does not implement a scheduler, task runner, branch manager, merge engine,
repair engine, checkpoint runner, promotion automation, Workbench Agent Board,
or product/runtime feature.

## Relationship To Workflow Law

`AIDE-WORKFLOW-LAW-01` defines branch roles, lifecycle states, blocker classes,
dirty-worktree handling, evidence requirements, warning acceptance, and the
dev/checkpoint/main promotion boundary. The WorkUnit schema layer encodes those
vocabularies into machine-readable objects.

The WorkUnit `status` enum follows `.aide/policy/task_lifecycle.md`. The
Blocker `blocker_class` enum follows `.aide/policy/blocker_taxonomy.md`.
Promotion objects may record a decision, but they do not authorize automatic
promotion.

## Object Ownership

AIDE owns the schema vocabulary. A human or assigned agent owns a specific
WorkUnit depending on its `owner` field. Coordinator-owned files such as
`.aide/queue/current.toml`, latest packets, status reports, and warning
disposition files require explicit coordinator ownership before mutation.

Task branches own bounded task outputs. Repair branches own blocker repairs.
Checkpoint branches own integration evidence. Main promotion remains reviewed
and evidence-gated.

## Object Identity

WorkUnit identity is not a timestamp. `work_unit_id`, `task_id`, scope, and
evidence references are the durable identity surface. If timestamps are later
added as metadata, they must not become identity or authority.

Object IDs should be stable across retries and resumes. A new attempt gets a
new `attempt_id`; a repair or resume gets its own linked task object rather
than rewriting the original task history.

## Object Lifecycle

A WorkUnit may be proposed, ready, running, locally done, partial, repairable,
missing a prerequisite, waiting on decision, unsafe, repair-queued,
resume-ready, a merge candidate, merged to dev, checkpoint-candidate, under
checkpoint repair, promoted to main, quarantined, or superseded.

Partial work is valid evidence. It must not be reported as complete. Blocked
work is classified and linked to a blocker, repair task, prerequisite task, or
human decision rather than being silently dropped.

## Evidence Linkage

EvidencePacket objects record the evidence kind, path, producing command,
related artifacts, status, warnings, and notes. WorkUnits and attempts refer to
evidence by ID or path. Evidence may prove validation, tests, builds, diffs,
audits, reports, screenshots, replay, proofs, artifacts, logs, or human review.

Generated outputs remain evidence unless a stronger source explicitly promotes
them. Fixture-only support must not be described as implementation.

## Blocker Linkage

Blockers are first-class objects with blocker class, severity, stage,
description, evidence refs, affected paths, default policy, repair/prerequisite
links, human-decision flag, and unsafe-to-continue flag.

Ordinary blockers are not terminal. Repairable blockers create RepairTask
objects. Missing prerequisites create prerequisite tasks. Human-review blockers
stop at the review gate. Unsafe blockers stop or quarantine.

## Repair And Resume Linkage

RepairTask objects preserve the original blocker link and keep the repair scope
bounded. They define allowed paths, forbidden paths, expected fix, required
validation, merge-back policy, and status.

ResumeTask objects preserve the source WorkUnit, source attempt, resume commit,
context refs, partial outputs, remaining deliverables, path scope, validation,
and status. Resume is evidence-based continuation, not a restart that overwrites
partial work.

## Checkpoint And Promotion Linkage

CheckpointCandidate objects record selected source branches, included and
excluded WorkUnits, base and merge commits, validation plans and results,
warning dispositions, blockers, recommendation, and status.

PromotionDecision objects record a checkpoint decision, source and target
branch, required evidence, validation summary, accepted and rejected warnings,
human approver when required, rationale, and resulting commit when one exists.
They are records of decisions, not branch mutation tools.

## WorkUnits Versus Prompts

A prompt is an instruction surface. A WorkUnit is a durable task object derived
from a prompt, queue item, repair task, resume task, checkpoint review, or human
decision. A prompt may be stale, incomplete, or superseded. The WorkUnit records
the executable scope, evidence expectations, and outcome links that survive
context loss.

## WorkUnits Versus Commits

A commit records repository changes. A WorkUnit records intent, scope, policy,
attempts, evidence, blockers, warnings, validation, and next actions. A single
WorkUnit may produce multiple attempts or commits; a commit may include several
coordinated WorkUnits only when integration policy allows it.

Commits are evidence refs, not replacements for WorkUnit state.

## WorkUnits And Task Branches

Normal bounded work should use `task/<task-id>` branch-role semantics even when
the live branch is not physically named that way. Repair work uses repair-role
semantics. Checkpoint and promotion objects describe later gate surfaces without
implementing branch automation.

Task branches must not mutate shared coordinator files unless the WorkUnit owns
that coordinator scope.

## Source Truth And Derived Evidence

Source truth for this layer is:

- `AGENTS.md`
- `.aide/policy/workflow_law.md`
- `.aide/policy/task_lifecycle.md`
- `.aide/policy/blocker_taxonomy.md`
- `.aide/policy/evidence_requirements.md`
- `.aide/schema/*.schema.json`

Fixtures, validator reports, queue packets, latest packets, and generated
reports are evidence or operational mirrors. They must not compete with policy
or schema law.

## Deferred Scope

The small `capability_reality_record.schema.json` defines a record shape only.
The capability reality ledger, ledger population policy, and support-status
audit remain deferred to `AIDE-CAPABILITY-REALITY-LEDGER-01`.
