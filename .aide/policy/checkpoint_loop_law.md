Status: DERIVED
Last Reviewed: 2026-05-22
Task: AIDE-CHECKPOINT-LOOP-01
Stability: provisional
Binding Sources: `.aide/policy/workflow_law.md`, `.aide/policy/dev_main_policy.md`, `.aide/policy/checkpoint_policy.md`, `.aide/policy/workunit_schema_law.md`, `.aide/schema/checkpoint_candidate.schema.json`, `.aide/schema/promotion_decision.schema.json`, `.aide/schema/warning_disposition.schema.json`

# AIDE Checkpoint Loop Law

## Purpose

This file defines the minimum repeatable checkpoint loop law for merging
bounded task-branch work into an integration checkpoint, classifying failures,
creating repair or resume work, and deciding whether a checkpoint may promote
to `origin/main`.

The controlling doctrine remains:

```text
development is non-blocking
promotion is evidence-blocked
```

`origin/dev` may accumulate classified development work. `origin/main` receives
only checkpointed, evidence-backed, reviewed states.

## Scope

This law applies to AIDE checkpoint candidates assembled from `origin/dev`,
`local/dev`, selected `task/<task-id>` branches, and selected
`repair/<task-id>` or `repair/<blocker-id>` branches.

It covers:

- checkpoint candidate creation
- source branch selection
- WorkUnit inclusion and exclusion
- checkpoint validation planning
- repair pass policy
- warning disposition
- promotion decision requirements
- rollback, defer, and quarantine outcomes
- coordinator file update rules
- evidence bundle requirements

It is policy only. It does not implement branch automation, automatic merging,
automatic promotion, a repair engine, a scheduler, Workbench Agent Board,
runtime modules, product features, or release publication.

## Checkpoint Loop Stages

The minimum loop is:

1. Select sources.
2. Create checkpoint candidate.
3. Assemble `checkpoint/<wave-id>` according to policy.
4. Run checkpoint validation.
5. Classify checkpoint outcome.
6. Create repair, prerequisite, resume, defer, or quarantine work when needed.
7. Rerun targeted validation after repair.
8. Write checkpoint review evidence.
9. Write promotion decision.
10. Close out queue/status, warnings, task ledger, checkpoint audit, and next
    tasks when the active task owns coordinator files.

Checkpoint outcomes are:

- `CHECKPOINT_PASS`
- `CHECKPOINT_PASS_WITH_WARNINGS`
- `CHECKPOINT_REPAIR_REQUIRED`
- `CHECKPOINT_BLOCKED_MISSING_PREREQ`
- `CHECKPOINT_BLOCKED_UNSAFE`
- `CHECKPOINT_QUARANTINE_REQUIRED`
- `CHECKPOINT_DEFERRED`

## Source Branch Selection

Allowed sources:

- `origin/dev`
- selected `task/<task-id>` branches with WorkUnit evidence
- selected `repair/<task-id>` or `repair/<blocker-id>` branches with repair
  evidence
- `local/dev` only when policy allows it and reconciliation evidence exists

Forbidden sources:

- unclassified raw task branches
- `experiment/<name>` branches unless converted into WorkUnits first
- `quarantine/<reason>` branches before explicit review or risk disposition
- branches with unresolved `BLOCKED_UNSAFE` blockers
- branches whose changed paths exceed their WorkUnit scope without review

Required source evidence:

- merge base
- source branch list
- source branch role
- WorkUnit or repair-task refs
- validation evidence refs
- warning disposition refs
- conflict report when conflicts exist
- excluded branch rationale
- generated artifact policy for any generated files included or rejected

## Checkpoint Candidate Creation

A checkpoint candidate must record:

- `checkpoint_id`
- `wave_id`
- `base_commit`
- source branches
- included WorkUnits
- excluded WorkUnits
- expected validation plan
- known warnings
- known blockers
- promotion target

When `.aide/schema/checkpoint_candidate.schema.json` is present, the candidate
should reference `dominium.aide.checkpoint_candidate.v1` and conform to that
schema rather than inventing a parallel object shape.

## WorkUnit Inclusion And Exclusion

Included WorkUnits require:

- WorkUnit ID or task ID
- source branch/ref
- status
- allowed and forbidden path summary
- changed paths or changed area summary
- evidence refs
- validation refs
- warning refs
- blocker refs
- contract/schema impact statement

Excluded WorkUnits require:

- WorkUnit ID or task ID when known
- exclusion reason
- disposition: `deferred`, `blocked`, `superseded`, `quarantined`, or
  `out_of_scope`
- whether a repair, resume, or prerequisite WorkUnit is needed

Partial work may remain on `dev`, but it must not become promoted truth unless
checkpoint policy explicitly accepts it for the promoted scope.

## Validation Tiers

Checkpoint validation tiers are defined in
`.aide/policy/checkpoint_validation_tiers.md`.

At minimum, ordinary checkpoints use:

- T0 coordinator consistency
- T1 policy/schema consistency
- touched-area validators
- `git diff --check`

Scope expansion raises validation strength. Release, trust, compatibility,
public-surface, package, replay, client, or product-spine changes require the
relevant higher tiers.

T4 full/release gate is not required for ordinary dev checkpoints unless the
promotion target or policy requires it. Full CTest remains T4/full-gate debt
unless live repo evidence says otherwise.

## Repair Pass Policy

Repair policy is defined in `.aide/policy/checkpoint_repair_policy.md`.

Repairable checkpoint failures create repair WorkUnits and
`repair/<blocker-id>` or `repair/<task-id>` branch policy. Repair evidence must
link back to the checkpoint, failed validation, changed files, rerun targeted
validation, and updated warning/blocker disposition.

Unsafe, authority-conflicted, destructive, secret-related, or review-gated
failures must not be repaired by convenience. They defer, quarantine, or stop
for human decision.

## Warning Disposition Policy

Every checkpoint warning must be classified. Warnings must not be hidden by
renaming `PASS_WITH_WARNINGS` to `PASS`.

Allowed warning dispositions:

- accepted for dev only
- accepted for main
- repair required
- deferred with expiry
- retired
- escalated to blocker

Main-accepted warnings require checkpoint evidence, a promotion-decision
rationale, and approval. Dev-accepted warnings are not automatically
main-accepted warnings.

## Promotion Decision Policy

Promotion policy is defined in `.aide/policy/checkpoint_promotion_policy.md`.

Promotion decisions must say exactly one of:

- `promote`
- `reject`
- `repair_required`
- `quarantine`
- `defer`

Promotion to `origin/main` requires:

- checkpoint ID and branch/ref
- evidence refs
- validation summary
- warning accept/reject summary
- blocker summary
- human or policy approval
- resulting commit if promotion occurs

No direct task-to-main promotion is permitted except a stronger reviewed
emergency policy.

## Quarantine And Defer Policy

Use `CHECKPOINT_QUARANTINE_REQUIRED` when work is unsafe, corrupt, ownership
conflicted, secret-bearing, or too ambiguous to repair safely.

Use `CHECKPOINT_DEFERRED` when work is not unsafe but cannot meet the active
checkpoint or promotion bar within this pass.

Deferred work remains eligible for future resume or repair. Quarantined work is
not eligible for promotion until explicit review, retirement, or repair
evidence clears the quarantine.

## Coordinator File Update Policy

Exclusive coordinator files are:

- `.aide/queue/current.toml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`

Only the active coordinator/checkpoint task may update these files. Parallel
lane tasks must write task-specific reports and audits only.

Checkpoint closeout updates coordinator files only when coordinator ownership
is explicit. Otherwise, closeout must state that coordinator update is deferred
to checkpoint/coordinator task.

## Evidence Bundle Requirements

Checkpoint evidence must include:

- checkpoint candidate
- source branch list
- merge base
- conflict report or no-conflict statement
- included and excluded WorkUnits
- validation plan and results
- warning dispositions
- blockers and outcomes
- repair branches and repair evidence, when any
- promotion decision
- checkpoint audit
- resulting commit when promotion occurs

Generated artifacts are evidence only unless a stronger source explicitly
promotes them.

## Safety Rules

- Do not stage unrelated files.
- Do not overwrite unrelated user or sibling-lane changes.
- Do not run destructive git commands without explicit reviewed authority.
- Do not fabricate clean state, validation, warnings, or approval.
- Do not treat `dev` as promoted truth.
- Do not promote unclassified partials.
- Do not hide full-gate debt.
- Do not infer runtime/product implementation from docs, fixtures, or policy.
- Do not mutate product/runtime behavior from this policy task.
