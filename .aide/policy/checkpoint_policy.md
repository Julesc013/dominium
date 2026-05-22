Status: DERIVED
Last Reviewed: 2026-05-22
Task: AIDE-DEV-MAIN-POLICY-01
Stability: provisional
Binding Sources: `.aide/policy/dev_main_policy.md`, `.aide/policy/evidence_requirements.md`, `.aide/policy/warning_acceptance_policy.md`, `.aide/policies/promotion-rules.yaml`

# AIDE Checkpoint Policy

## Purpose

This file defines the checkpoint workflow used to prove selected `dev` or task
state before promotion to `origin/main`.

Checkpoint policy is evidence policy. It does not create an automatic merge bot,
automatic scheduler, repair engine, or branch promotion tool.

## Branch Naming

Checkpoint branches use:

```text
checkpoint/<wave-id>
```

`<wave-id>` must be stable enough to connect the checkpoint report, promotion
decision, included WorkUnits, repair tasks, and resulting commit.

## Workflow

```text
origin/dev or selected task branches
-> checkpoint/<wave-id>
-> merge selected tasks
-> run checkpoint validation
-> classify warnings/blockers
-> spawn repair branches if needed
-> rerun targeted validation
-> produce checkpoint report
-> create promotion decision
-> promote or defer
```

## Source Branch Selection

The checkpoint owner must list source branches before merging.

Allowed sources:

- `origin/dev`
- `local/dev` only when reconciled and evidence-backed
- selected `task/<task-id>` branches with WorkUnits and validation evidence
- selected `repair/<task-id>` or `repair/<blocker-id>` branches with repair evidence

Forbidden sources:

- unclassified raw task branches
- `experiment/<name>` branches unless converted into WorkUnits first
- `quarantine/<reason>` branches before human review or explicit risk disposition
- branches with unresolved `BLOCKED_UNSAFE` blockers

## Included And Excluded WorkUnits

The checkpoint report must list both:

- included WorkUnits
- excluded WorkUnits

Included WorkUnits require:

- task ID or WorkUnit ID
- source branch/ref
- status
- changed areas
- evidence refs
- warnings
- blockers

Excluded WorkUnits require:

- task ID or WorkUnit ID when known
- exclusion reason
- whether they are deferred, blocked, superseded, quarantined, or out of scope

## Validation Plan

The checkpoint owner records the validation plan before claiming a checkpoint
result.

Minimum validation:

- task-specific validators for included work
- policy validator for AIDE policy changes
- JSON parse checks for touched JSON fixtures/schema artifacts
- contract/schema validators where touched
- `git diff --check`

Stronger validation is required when scope expands into release, trust,
dependency direction, public surfaces, compatibility, package, replay, or
product-spine behavior.

Full CTest remains T4/full-gate debt unless the active release/full-gate policy
requires it. Ordinary dev integration and non-release checkpoints do not require
full CTest.

## Repair Pass

When checkpoint validation fails:

- classify the failure
- create `repair/<task-id>` or `repair/<blocker-id>` when the issue is bounded
- keep repair scope narrow
- rerun targeted validation after repair
- record repair tasks created and their outcomes

If the failure requires semantic authority, destructive git, release/trust
policy, or public support decisions, stop for human review instead of repairing
by convenience.

## Warning Disposition

Checkpoint warnings must be recorded as accepted, rejected, or repair-required.

Accepted warnings require:

- warning class
- affected WorkUnit or branch
- evidence refs
- rationale
- expiry or follow-up when needed

A checkpoint must not hide warnings by renaming `PASS_WITH_WARNINGS` to `PASS`.

## Blockers

Blockers must be classified before promotion recommendation.

Blocking for main promotion:

- `BLOCKED_UNSAFE`
- unresolved merge conflicts
- unresolved contract/schema corruption
- missing required evidence
- false implementation claims
- unresolved human review gates
- secret exposure or local-only secret dependency
- hidden broad blockers

Non-blocking blockers may be accepted only when the checkpoint report explains
why they do not affect the promoted scope.

## Checkpoint Report

The checkpoint report must include:

- `wave_id`
- `base_commit`
- source branches
- included WorkUnits
- excluded WorkUnits
- changed areas
- validation commands
- validation results
- warning dispositions
- blockers
- repair tasks created
- promotion recommendation
- next actions

When `.aide/schema/checkpoint_candidate.schema.json` exists, the report should
reference `dominium.aide.checkpoint_candidate.v1` without redefining it.

## Promotion Decision

Promotion decision is a separate record from the checkpoint report.

It must include:

- checkpoint ID
- source branch
- target branch
- decision: promote, reject, repair_required, quarantine, or defer
- required evidence refs
- validation summary
- warnings accepted and rejected
- human approver or policy approval source
- rationale
- resulting commit after promotion, if any

When `.aide/schema/promotion_decision.schema.json` exists, the decision should
reference `dominium.aide.promotion_decision.v1` without redefining it.

## Rollback And Defer Handling

If promotion is deferred:

- preserve the checkpoint branch or report the retained ref
- record deferred WorkUnits and blockers
- create repair/resume tasks where useful
- do not rewrite `origin/main`

If promotion lands and must be undone later:

- use a reviewed revert or hotfix path
- preserve the checkpoint and promotion decision evidence
- do not rewrite public/shared history without explicit approval

## Non-Goals

This policy does not implement checkpoint automation, branch mutation, merge
automation, GitHub mutation, release publication, or runtime/product behavior.
