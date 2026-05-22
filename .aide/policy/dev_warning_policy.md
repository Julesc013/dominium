Status: DERIVED
Last Reviewed: 2026-05-22
Task: AIDE-DEV-MAIN-POLICY-01
Stability: provisional
Binding Sources: `.aide/policy/warning_acceptance_policy.md`, `.aide/policy/dev_main_policy.md`, `.aide/reports/latest-warning-disposition.md`

# AIDE Dev Warning Policy

## Purpose

This file specializes `.aide/policy/warning_acceptance_policy.md` for `dev` and
`main` branch decisions.

The base rule remains:

```text
Warnings must be classified, bounded, and recorded.
```

This file does not replace the base warning policy and must not contradict it.

## Dev Warning Acceptance

`origin/dev` may accept warnings when all of the following are true:

- the warning is classified
- the scope is bounded
- the warning is recorded in task evidence or warning disposition
- the warning does not hide a failed required proof
- the warning does not claim implemented runtime when work is fixture-only, stubbed, planned, or doc-only
- the warning is linked to follow-up, expiry, repair, or checkpoint disposition when needed
- no `BLOCKED_UNSAFE` blocker is present

Accepted dev warnings keep the task at `PASS_WITH_WARNINGS`, `PARTIAL`, or a
blocked lifecycle state as appropriate. They do not become clean `PASS`.

## Main Warning Acceptance

`origin/main` may accept warnings only when:

- the checkpoint report includes the warning
- the promotion decision explains the warning
- no warning contradicts public support, release, runtime, or product claims
- human approval or explicit policy approval exists
- the warning has an expiry, follow-up, or rationale when it remains open

Warnings that affect release, trust, publication, compatibility, public support,
or runtime correctness require stronger proof than ordinary dev integration.

## Warning Classes

The active base classes are inherited from
`.aide/policy/warning_acceptance_policy.md`:

- `full_gate_debt`
- `dependency_direction_warning`
- `review_ref_warning`
- `stale_evidence_warning`
- `runtime_not_implemented_gap`
- `planned_schema_gap`
- `new_warning`

Additional task-local warning labels may be used only when mapped to a base
class or recorded as `new_warning`.

## Rejection And Repair

Reject or require repair for warnings that:

- hide a failed required validator
- imply support that is not implemented
- cover up corrupted contracts or schemas
- expose secrets or local-only state
- leave migration/replacement half-applied
- leave unresolved conflict markers
- contradict release/public claims

Rejected warnings create a repair task, blocker, quarantine decision, or human
review item.

## Status Wording

Use `PASS_WITH_WARNINGS` when warnings are accepted.

Use `PASS` only when the active scope has no accepted warnings or when the base
policy explicitly rules the item as not a warning for that scope.

Do not rewrite `PASS_WITH_WARNINGS` as `PASS` to make a branch look cleaner.

## Checkpoint Interaction

Dev-accepted warnings are not automatically main-accepted warnings.

Checkpoint must re-state:

- warning ID or description
- warning class
- affected WorkUnit/branch
- evidence refs
- accepted/rejected decision
- rationale
- follow-up or expiry when needed

When `.aide/schema/warning_disposition.schema.json` exists, checkpoint and
promotion records should reference `dominium.aide.warning_disposition.v1`
without redefining the schema.
