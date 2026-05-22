Status: DERIVED
Last Reviewed: 2026-05-22
Task: AIDE-WORKFLOW-LAW-01
Stability: provisional
Binding Sources: `AGENTS.md`, `contracts/aide/aide_workflow_law.v1.json`, `.aide/policies/branch-roles.yaml`, `.aide/policies/work-units.yaml`, `.aide/policies/recovery.yaml`, `.aide/policies/promotion-rules.yaml`

# AIDE Workflow Law

## Purpose

This file defines the minimum AIDE workflow law needed to run bounded Codex and
AIDE tasks without serially blocking all development.

The controlling rule is:

```text
development is non-blocking
promotion is evidence-blocked
```

AIDE coordinates tasks, context, blockers, branches, checkpoints, evidence, and
promotion decisions. Codex executes bounded patches and produces evidence.
Humans retain final authority for ambiguous architecture, unsafe actions,
irreversible git operations, and promotion overrides.

## Scope

This law governs AIDE task branches, repair branches, checkpoint branches,
dirty-worktree handling, blocker classification, warning acceptance, evidence
requirements, and limited parallel execution on one machine.

It does not implement a scheduler, branch automation, merge automation, repair
engine, Workbench Agent Board, product runtime, package runtime, replay runtime,
provider runtime, renderer, native GUI, gameplay, or release publication.

## Branch Roles

Branch roles are defined in `.aide/policy/branch_roles.md`.

The minimum roles are:

- `origin/main`: remote canonical baseline.
- `origin/dev`: remote integration baseline when present.
- `local/dev`: local integration branch, not canonical truth.
- `task/<task-id>`: bounded WorkUnit branch.
- `repair/<task-id>`: bounded blocker repair branch.
- `checkpoint/<wave-id>`: temporary evidence checkpoint branch.
- `quarantine/<reason>`: isolated risk branch.
- `experiment/<name>`: optional non-promotional exploratory branch.

`main` receives only checkpointed, evidence-backed, reviewed states. `dev` may
carry classified partials and warnings only under explicit policy.

## Task Lifecycle

Lifecycle states are defined in `.aide/policy/task_lifecycle.md`.

Ordinary blockers are not terminal. A task may move through `PARTIAL`,
`BLOCKED_REPAIRABLE`, `REPAIR_QUEUED`, and `RESUME_READY` while preserving
evidence. Only unsafe, destructive, semantic-authority, or human-review blockers
stop autonomous progress.

## Blocker Taxonomy

Blockers are defined in `.aide/policy/blocker_taxonomy.md`.

AIDE must classify blockers before stopping. Repairable blockers become repair
tasks. Missing prerequisites become prerequisite tasks. Human-review blockers
ask for a decision. Unsafe blockers stop and preserve evidence.

## Retry, Repair, And Resume Rules

Retries must be bounded and evidence-backed:

- Retry a command only when the failure is transient, timed out, or classified
  as flaky.
- Repair only inside the active task's allowed paths or an explicit repair task.
- Resume from recorded evidence; do not restart by overwriting partial work.
- Create a prerequisite task when a missing tool, capability, connector,
  schema, or policy surface is required.
- Stop for missing secrets, destructive git requirements, source-authority
  conflicts, or architecture decisions.

## Dirty-Worktree Policy

Dirty-worktree handling is defined in `.aide/policy/dirty_worktree_policy.md`.

Do not stop merely because the worktree is dirty. Classify dirtiness first,
preserve unrelated changes, avoid destructive git commands, and continue when
the active edits are path-disjoint and safe.

## Evidence Requirements

Evidence requirements are defined in `.aide/policy/evidence_requirements.md`.

Every task closeout must record changed files, commands run, validation output,
warnings, blockers, evidence refs, commit hash when committed, and next action.

## Warning Policy

Warning acceptance is defined in `.aide/policy/warning_acceptance_policy.md`.

Warnings may be accepted on `dev` when known, bounded, classified, and recorded.
Warnings must not be hidden or reworded as clean passes. Main promotion requires
checkpoint policy and explicit warning disposition.

## Dev, Checkpoint, And Main Promotion

`task/*` and `repair/*` may land on `dev` when scoped evidence exists and
warnings are classified. `dev` may advance to `checkpoint/*` for integration
proof. `checkpoint/*` may promote to `main` only after gate evidence, review, and
explicit warning disposition.

No direct task-to-main promotion is permitted except reviewed emergency hotfix
policy. Direct main mutation is discouraged and must produce stronger evidence.

## Parallelism Limits

Parallel execution law is defined in `.aide/policy/parallel_execution_law.md`.

Limited parallelism is allowed only for non-overlapping paths with clear
coordinator ownership. Large parallelism remains blocked until
`AIDE-WORKUNIT-SCHEMA-01`, `AIDE-DEV-MAIN-POLICY-01`, checkpoint/review policy,
and repair/resume policy are in place.

## Safety Rules

- Do not stage unrelated files.
- Do not overwrite unrelated user changes.
- Do not run destructive git commands without explicit reviewed authority.
- Do not fabricate validation, warnings, or clean state.
- Do not promote generated evidence into authority without provenance.
- Do not claim runtime/product implementation from docs, fixtures, or plans.
- Do not collapse `truth`, `perceived`, and `render` layers.
- Do not bypass `AGENTS.md`, canon, authority order, or review gates.
