# AIDE-MOVE-02-PLAN Review

## What Would Move

Nothing. No second move candidate is selected.

## Why

The second move needs to be as narrow and reversible as the first. After the IDE README move, the remaining preferred roots do not contain a small docs-only or evidence-only candidate:

- `ide/` contains deferred machine-readable manifests.
- `performance/` contains active Python helpers referenced by product/client code and tooling.
- `validation/` contains active validation tooling.
- `governance/` contains policy/governance Python helpers.
- `meta/` is broad, Python-heavy, and high-reference.

## What Would Not Move

All source roots, product roots, active tooling roots, machine-readable manifests, and high-risk root families remain untouched.

## What Would Be Rewritten

Nothing. The reference rewrite plan contains zero apply-phase rewrites.

## Validators

Tier 0 validators remain required for this planning evidence. No Tier 1 or Tier 2 apply validators are activated because no move is selected.

## Rollback

No rollback action is needed because no files are planned to move and no references are planned to change.

## Review Decision

This plan is safe as no-apply evidence, but it is not ready for AIDE-GATE-04. The next step should be candidate refinement, not apply-gate review.
