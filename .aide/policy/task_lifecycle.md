Status: DERIVED
Last Reviewed: 2026-05-22
Task: AIDE-WORKFLOW-LAW-01
Stability: provisional
Binding Sources: `.aide/policies/work-units.yaml`, `.aide/policies/recovery.yaml`, `.aide/policies/promotion-rules.yaml`

# AIDE Task Lifecycle

## State Rules

| State | Meaning | Allowed Next States | Required Evidence | Allowed On Dev | Promotable To Main |
| --- | --- | --- | --- | --- | --- |
| `PROPOSED` | Task intent exists but is not ready. | `READY`, `SUPERSEDED`, `BLOCKED_MISSING_PREREQ`, `BLOCKED_NEEDS_DECISION` | Intent, goal, initial scope. | No | No |
| `READY` | Scope, paths, dependencies, validation, and evidence expectations are explicit. | `RUNNING`, `SUPERSEDED`, `BLOCKED_MISSING_PREREQ` | Task packet or WorkUnit draft. | No | No |
| `RUNNING` | A worker is executing the task. | `DONE_LOCAL`, `PARTIAL`, `BLOCKED_REPAIRABLE`, `BLOCKED_MISSING_PREREQ`, `BLOCKED_NEEDS_DECISION`, `BLOCKED_UNSAFE` | Assigned branch, current diff, commands run. | No, except coordinator tasks on `local/dev` | No |
| `DONE_LOCAL` | Local work is complete but not integrated. | `MERGE_CANDIDATE`, `REPAIR_QUEUED`, `SUPERSEDED` | Changed files, validation, warnings, evidence refs. | No | No |
| `PARTIAL` | Useful bounded work exists but acceptance is incomplete. | `RESUME_READY`, `REPAIR_QUEUED`, `BLOCKED_MISSING_PREREQ`, `QUARANTINED`, `SUPERSEDED` | Partial diff, remaining tasks, blockers. | Yes, only if policy accepts classified partials | No |
| `BLOCKED_REPAIRABLE` | A bounded repair can unblock progress. | `REPAIR_QUEUED`, `RESUME_READY`, `QUARANTINED` | Blocker class, failed command, repair scope. | Yes, if recorded as dev blocker evidence | No |
| `BLOCKED_MISSING_PREREQ` | A prerequisite task or contract must land first. | `REPAIR_QUEUED`, `READY`, `SUPERSEDED` | Missing prerequisite ID and dependency rationale. | Yes, as dependency evidence only | No |
| `BLOCKED_NEEDS_DECISION` | Human or governance decision is required. | `READY`, `REPAIR_QUEUED`, `QUARANTINED`, `SUPERSEDED` | Decision question, options, risk. | Yes, as blocked evidence only | No |
| `BLOCKED_UNSAFE` | Secret, destructive, or unsafe condition prevents progress. | `QUARANTINED`, `SUPERSEDED` | Unsafe risk, affected paths, stop reason. | No, except quarantine evidence | No |
| `REPAIR_QUEUED` | Repair task is created or selected. | `RUNNING`, `RESUME_READY`, `BLOCKED_NEEDS_DECISION`, `SUPERSEDED` | Repair task ID, blocker link. | Yes | No |
| `RESUME_READY` | Partial work can continue from evidence. | `RUNNING`, `DONE_LOCAL`, `SUPERSEDED` | Resume point, prior evidence, dirty-tree classification. | Yes | No |
| `MERGE_CANDIDATE` | Task branch can integrate to dev. | `MERGED_TO_DEV`, `CHECKPOINT_CANDIDATE`, `REPAIR_QUEUED`, `QUARANTINED` | Task evidence, validation, warning disposition. | Yes | No |
| `MERGED_TO_DEV` | Work is integrated into dev, not main truth. | `CHECKPOINT_CANDIDATE`, `CHECKPOINT_REPAIR`, `QUARANTINED`, `SUPERSEDED` | Merge evidence, dev validation, conflict disposition. | Yes | No |
| `CHECKPOINT_CANDIDATE` | Integrated work is ready for checkpoint proof. | `CHECKPOINT_REPAIR`, `PROMOTED_TO_MAIN`, `QUARANTINED`, `SUPERSEDED` | Checkpoint plan, selected tasks, required gates. | Yes | No |
| `CHECKPOINT_REPAIR` | Checkpoint failed but can be repaired. | `CHECKPOINT_CANDIDATE`, `REPAIR_QUEUED`, `QUARANTINED`, `SUPERSEDED` | Failed gate, repair scope, rerun plan. | Yes | No |
| `PROMOTED_TO_MAIN` | Work landed on main through evidence-backed promotion. | `SUPERSEDED` | Commit hash, checkpoint evidence, review decision. | N/A | Already promoted |
| `QUARANTINED` | Work is isolated from integration or promotion. | `REPAIR_QUEUED`, `RESUME_READY`, `SUPERSEDED` | Risk class, quarantine branch/ref, review need. | No, except quarantine refs | No |
| `SUPERSEDED` | Later work replaces this task. | None | Superseding task, preserved evidence. | Yes, as history | No |

## Lifecycle Invariants

- `PARTIAL` is a valid outcome and must not be called `DONE_LOCAL`.
- `MERGED_TO_DEV` is not canonical truth.
- `PROMOTED_TO_MAIN` requires checkpoint or reviewed hotfix evidence.
- `QUARANTINED` work cannot promote until risk disposition and revalidation.
- Missing schemas, implementation, or fixtures must not be described as complete.
