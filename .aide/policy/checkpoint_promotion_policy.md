Status: DERIVED
Last Reviewed: 2026-05-22
Task: AIDE-CHECKPOINT-LOOP-01
Stability: provisional
Binding Sources: `.aide/policy/dev_main_policy.md`, `.aide/policy/checkpoint_policy.md`, `.aide/policy/checkpoint_loop_law.md`, `.aide/schema/promotion_decision.schema.json`

# AIDE Checkpoint Promotion Policy

## Purpose

This file defines the minimum promotion decision policy for checkpointed AIDE
work.

It specializes `.aide/policy/dev_main_policy.md` and does not replace it.
`origin/main` remains promoted truth. `origin/dev` remains integration truth.

## Promotion Decision Requirements

Every promotion decision must say exactly one of:

- `promote`
- `reject`
- `repair_required`
- `quarantine`
- `defer`

Every decision must include:

- promotion ID
- checkpoint ID
- source branch/ref
- target branch
- decision
- required evidence refs
- validation summary
- warnings accepted
- warnings rejected
- blocker disposition
- approval source
- rationale
- resulting commit when promotion occurs

When `.aide/schema/promotion_decision.schema.json` is present, promotion
records should reference `dominium.aide.promotion_decision.v1`.

## Minimum Evidence For Main Promotion

Promotion to `origin/main` requires:

- checkpoint branch or checkpoint ref
- checkpoint candidate
- source branch list
- merge base
- included WorkUnits
- excluded WorkUnits
- validation plan
- validation results
- warning disposition
- blocker disposition
- repair evidence when repairs occurred
- human approval or explicit reviewed policy approval
- resulting commit after promotion

Missing evidence produces `repair_required` or `defer`, not `promote`.

## Warning Acceptance Rules

Main promotion may accept warnings only when:

- each warning is classified
- each warning is accepted for main or rejected with consequence
- dev-only accepted warnings are not silently promoted
- deferred warnings have expiry or next review
- repair-required warnings are resolved or block promotion
- escalated warnings become blockers
- the promotion decision explains the warning disposition

Warnings cannot be hidden by renaming `PASS_WITH_WARNINGS` to `PASS`.

## Human Approval Rules

Human approval is required for:

- promotion to `origin/main`
- accepting warnings for main when they affect support claims
- release, trust, publication, signing, licensing, or public policy meaning
- crossing review-gated or quarantine-sensitive areas
- destructive git, history rewriting, or public branch mutation
- emergency direct-to-main exceptions

Automatic promotion is not authorized by this policy.

## Rollback, Defer, And Quarantine Outcomes

Rollback after promotion requires:

- reviewed revert or hotfix path
- retained checkpoint evidence
- retained promotion decision
- explicit rationale
- no silent public history rewrite

Defer outcome requires:

- deferred WorkUnits
- unresolved evidence, warning, blocker, or approval gap
- resume or repair task when useful
- next review point

Quarantine outcome requires:

- quarantine reason
- affected branches or WorkUnits
- evidence retained
- review or repair condition for release from quarantine

Reject outcome requires:

- rationale
- affected WorkUnits
- whether work is superseded, retired, or returned for redesign

## Promotion Audit Requirements

Promotion audits must record:

- checkpoint ID and wave ID
- promotion decision
- files inspected
- files changed
- policies and schemas touched
- validation commands and results
- warnings accepted and rejected
- blockers resolved, deferred, or quarantined
- human approval source
- resulting commit when promotion occurs
- next tasks

## Non-Goals

This policy does not implement automatic promotion, automatic branch mutation,
release publication, rollback tooling, signing, scheduler behavior, or
Workbench Agent Board behavior.
