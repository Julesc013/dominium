Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional
Task: AIDE-WORKFLOW-LAW-01
Result: PASS_WITH_WARNINGS

# AIDE-WORKFLOW-LAW-01

## Purpose

This document defines the minimum AIDE task operating system law needed after
the product-spine review. The rule is:

```text
Development should be non-blocking.
Promotion should be evidence-blocked.
```

This is governance and control-plane law only. It does not implement branch
automation, remote mutation, Workbench shell behavior, package runtime, replay
runtime, provider runtime, module loading, gameplay, renderer, native GUI, or
release publication.

## Binding Surface

The machine-readable law is:

```text
contracts/aide/aide_workflow_law.v1.json
```

The operator policy packet is:

```text
.aide/policy/
```

It derives from existing AIDE fragments:

- `.aide/policy/workflow_law.md`
- `.aide/policy/branch_roles.md`
- `.aide/policy/task_lifecycle.md`
- `.aide/policy/blocker_taxonomy.md`
- `.aide/policy/dirty_worktree_policy.md`
- `.aide/policy/parallel_execution_law.md`
- `.aide/policy/evidence_requirements.md`
- `.aide/policy/warning_acceptance_policy.md`
- `.aide/policies/branch-roles.yaml`
- `.aide/policies/git-workflow.yaml`
- `.aide/policies/work-units.yaml`
- `.aide/policies/recovery.yaml`
- `.aide/policies/promotion-rules.yaml`
- `.aide/policies/workunit-sizing.yaml`

Those fragments remain valid. This slice binds them into one post-product-spine
operating law.

## Branch Roles

| Role | Meaning | Default Action |
| --- | --- | --- |
| `main` | canonical reviewed truth | do not edit directly except reviewed checkpoint/hotfix/emergency repair |
| `dev` | shared integration, not canonical truth | integrate bounded work and run integration proof |
| `task/*` | normal bounded WorkUnit branch | preferred lane for most work |
| `repair/*` | blocker or validation repair | scoped to the blocker evidence |
| `checkpoint/*` | temporary merge/proof branch | validates dev/task integration before main |
| `quarantine/*` | risky or untrusted work | inspect, classify, and repair before integration |
| `unknown` | unclassified branch | inspect before editing or promotion |

Workers commit to task or repair branches where practical. AIDE integrates safe
work to `dev`. Checkpoint branches prove integrated truth before `main`.

## Lifecycle States

The lifecycle vocabulary is:

```text
PROPOSED
READY
RUNNING
DONE_LOCAL
PARTIAL
BLOCKED_REPAIRABLE
BLOCKED_MISSING_PREREQ
BLOCKED_NEEDS_DECISION
BLOCKED_UNSAFE
REPAIR_QUEUED
RESUME_READY
MERGE_CANDIDATE
MERGED_TO_DEV
CHECKPOINT_CANDIDATE
PROMOTION_CANDIDATE
PROMOTED_TO_MAIN
QUARANTINED
SUPERSEDED
NOOP_ALREADY_COMPLETE
```

Most blockers are not terminal. AIDE should convert ordinary blockers into
bounded repair, prerequisite, or resume work. Unsafe blockers remain terminal
until reviewed.

## Blocker Taxonomy

Repairable blockers:

- dirty worktree path-disjoint from current scope
- dirty worktree overlap that can be classified
- generated or transient residue
- missing dependency
- validation failure inside task scope
- merge conflict inside owned scope
- stale status or queue packet

Terminal blockers:

- missing secret
- unsafe operation
- destructive git required
- architecture decision required
- human review required
- source authority conflict

Terminal means stop and record evidence. It does not mean invent success.

## Warning Policy

Known warnings may pass only when classified. New warnings must be classified.
Warnings must not be hidden by status wording.

Accepted current warning families include:

- full CTest remains T4/full-gate debt
- dependency-direction warnings with 0 violations
- AIDE review-ref warnings
- stale AuditX output
- contract-only/runtime-not-implemented gaps

Warnings become blockers if they contradict a support claim, create a strict
validator violation, or require forbidden-path work.

## WorkUnit Requirements

A ready WorkUnit must declare:

- task ID and goal
- allowed and forbidden paths
- dependencies
- validation
- evidence outputs
- non-goals
- acceptance criteria

Idempotency is based on task ID, allowed-path scope, and acceptance criteria.
Repeated work must no-op when already proven, resume when partial, or repair
when evidence shows a blocker.

## Repair And Resume

AIDE should attempt bounded remediation before reporting blocked:

1. Inspect current status and evidence.
2. Classify dirty paths and blockers.
3. Continue path-disjoint work if safe.
4. Repair inside the task scope when allowed.
5. Create prerequisite, repair, or resume work when needed.
6. Stop only for unsafe blockers or required decisions.

No repair may delete unrelated work, rewrite shared history, expose secrets, or
claim evidence that was not produced.

## Promotion Gates

Task to `dev` requires:

- scoped changed-file evidence
- targeted validation
- forbidden-path proof
- warnings classified

`dev` to checkpoint requires:

- selected task branches or dev integration identified
- merge conflicts resolved with evidence
- checkpoint validation plan recorded

Checkpoint to `main` requires:

- checkpoint gate pass or accepted warning disposition
- dependency/public-surface/contract gates relevant to touched areas
- full CTest disposition recorded
- broad feature blockers visible
- reviewed, non-automatic promotion intent

`main` must not receive raw task output without checkpoint or reviewed hotfix
evidence.

## Parallel Wave Limits

Before WorkUnit schema and dev/main policy are hardened, keep parallelism small:

```text
recommended: 2 concurrent tasks
maximum: 4 concurrent tasks
```

After WorkUnit schema and dev/main policy:

```text
recommended: 4 concurrent tasks
maximum: 8 concurrent tasks
```

After checkpoint automation:

```text
recommended: 8 concurrent tasks
maximum: 12 concurrent tasks
```

The limit is coordination capacity, not token capacity.

## Non-Goals

This law does not authorize:

- broad Workbench UI
- runtime module loader
- provider runtime
- package runtime
- gameplay/domain implementation
- renderer implementation
- native GUI
- release publication
- direct main promotion automation
- force pushes or branch deletion

## Next

The next task should define explicit WorkUnit, attempt, blocker, and evidence
packet schemas:

```text
AIDE-WORKUNIT-SCHEMA-01
```

Immediate policy follow-ups remain:

```text
AIDE-DEV-MAIN-POLICY-01
AIDE-CHECKPOINT-LOOP-01
AIDE-CAPABILITY-REALITY-LEDGER-01
```
