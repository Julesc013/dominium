Status: DERIVED
Last Reviewed: 2026-05-22
Task: AIDE-DEV-MAIN-POLICY-01
Stability: provisional
Binding Sources: `.aide/policy/dev_main_policy.md`, `.aide/policy/parallel_execution_law.md`, `.aide/policy/dirty_worktree_policy.md`, `.aide/policy/blocker_taxonomy.md`

# AIDE Parallel Worktree Policy

## Purpose

This file defines practical same-machine parallelism rules for bounded AIDE and
Codex work.

It permits narrow, evidence-backed parallel work while preserving coordinator
ownership, path ownership, and checkpoint-based promotion.

## Core Rules

- Use one worktree per task branch.
- Use one task branch per WorkUnit.
- Do not let two task branches edit the same coordinator file unless assigned.
- Only the coordinator task may update `.aide/queue/current.toml`.
- Only the coordinator task may update latest task, review, status, or warning packets unless explicitly assigned.
- Task branches may write task-local reports and audits.
- Shared generated outputs require ownership assignment.
- Do not use destructive git commands without explicit approval.

## Coordinator File Exclusivity

Exclusive coordinator files:

- `.aide/queue/current.toml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`

Parallel lane tasks should write task-specific reports such as:

- `.aide/reports/<task-id>-summary.md`
- `.aide/reports/<task-id>-validation.json`
- `docs/repo/audits/<TASK_ID>.md`

The checkpoint or coordinator task merges task-local reports into latest status.

## Path Ownership

Each WorkUnit must declare:

- allowed paths
- forbidden paths
- expected generated outputs
- coordinator ownership status
- global build/root/contract ownership status

High-risk path families require explicit lane ownership:

- CMake and global build files
- root layout contracts
- contract/schema law
- release/trust/publication policy
- shared generated outputs
- structure moves
- broad formatting

Runtime, product, Workbench, renderer, native GUI, gameplay, provider runtime,
package runtime, release publication, and source tree movement remain blocked
unless a future task explicitly authorizes them.

## Safe Concurrent Tasks

Generally safe for early limited parallelism when paths do not overlap:

- task-specific policy documents
- task-specific audits and reports
- schema fixtures owned by one task
- validators owned by one task
- docs-only hardening in separate directories
- read-only analysis

These tasks still need validation and evidence.

## Unsafe Concurrent Tasks

Not safe for early parallelism without explicit coordination:

- broad formatting tasks
- semantic edits to the same policy or contract file
- CMake/global build edits
- root layout or source movement
- dependency-direction law changes
- schema/projection convergence
- release/trust/publication changes
- shared generated output refreshes
- queue/current and latest packet updates
- product/runtime implementation

## Conflict Classification

If a conflict occurs, classify it before editing:

- `merge_conflict`
- `dirty_worktree_unrelated`
- `dirty_worktree_same_task`
- `stale_queue_state`
- `stale_context_packet`
- `source_authority_conflict`
- `destructive_git_required`

Owned conflicts may be repaired in the active task or repair branch. Unowned or
ambiguous conflicts create a repair task or require coordinator review.

## Same-Machine Layout

Recommended local layout:

```text
<repo>-main/
<repo>-dev/
<repo>-task-AIDE-WORKFLOW-LAW-01/
<repo>-task-AIDE-WORKUNIT-SCHEMA-01/
<repo>-task-AIDE-DEV-MAIN-POLICY-01/
```

This task documents the layout but does not create those directories.

## Merge And Rebase Safety

- Rebase task branches only when clean, local, and owned by the operator.
- Do not rewrite public/shared branches without explicit approval.
- Prefer traceable merges for `dev` and checkpoint branches when evidence matters.
- Preserve source task refs until checkpoint/promotion evidence is complete.
- Do not run `git reset --hard`, force checkout, branch delete, or force-push without explicit approval.

## Early Parallelism Authorization

Limited parallel task execution becomes eligible only when:

- `AIDE-WORKFLOW-LAW-01` is complete
- `AIDE-WORKUNIT-SCHEMA-01` is complete
- `AIDE-DEV-MAIN-POLICY-01` passes
- coordinator file ownership rules are active
- task paths are non-overlapping
- checkpoint policy exists

Large parallel execution remains unauthorized until a later checkpoint-loop task
explicitly approves it.

## Non-Goals

This policy does not implement worktree creation, branch automation, conflict
resolution automation, schedulers, merge bots, repair engines, or product/runtime
features.
