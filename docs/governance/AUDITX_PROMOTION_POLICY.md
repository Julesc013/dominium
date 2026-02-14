Status: CANONICAL
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none

# AuditX -> RepoX Promotion Policy

## Purpose

This policy defines when AuditX findings should be promoted into blocking RepoX invariants.
Promotion is a governance change and must be explicit, reviewable, and reversible.

## Thresholds

- Promote only when finding severity is `VIOLATION` or `RISK`.
- Promote only when finding confidence is `>= 0.85`.
- Require repeat evidence across at least two independent scans or one scan plus one TestX failure.
- Never auto-promote analyzer output directly into blocking rules.

## Promotion Flow

1. AuditX emits findings and optional promotion candidates in `docs/audit/auditx/PROMOTION_CANDIDATES.json`.
2. Maintainer reviews evidence paths, false-positive risk, and rule scope boundaries.
3. New rule is authored in `repo/repox/rulesets/*.json` with documentation in `docs/governance/REPOX_RULESETS.md`.
4. RepoX checker implementation is added in `scripts/ci/check_repox_rules.py`.
5. TestX regression proof is added for the promoted invariant.
6. Rule starts as `WARN` only when needed; ratchets to `FAIL` after stabilization.

## Human Sign-Off Requirements

- At least one governance maintainer signs off on promotion intent.
- At least one subsystem owner signs off on scope impact.
- Promotion commit message must reference the originating AuditX analyzer and finding class.

## Invariant Retirement

- Retirement requires explicit rationale in commit history and rule documentation updates.
- Retired rules are removed from rulesets and checker code in the same change.
- If replaced, the replacement invariant must be linked in the retirement note.

