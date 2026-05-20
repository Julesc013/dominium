# AIDE Review Packet

## Review Objective

Review `DEPENDENCY-DIRECTION-01`: repository dependency-direction law,
validator, fixtures, documentation, public-surface registration, and evidence.

## Decision Requested

`PASS | PASS_WITH_NOTES | REQUEST_CHANGES | BLOCKED`

## Task Packet Reference

`.aide/context/latest-task-packet.md`

## Context Packet Reference

`.aide/context/latest-context-packet.md`

## Verification Report Reference

`.aide/reports/DEPENDENCY-DIRECTION-01-validation.md`

## Evidence Packet References

- `contracts/repo/dependency_directions.contract.toml`
- `contracts/repo/dependency_direction.schema.json`
- `contracts/repo/dependency_direction_exceptions.toml`
- `tools/validators/repo/check_dependency_directions.py`
- `docs/architecture/dependency_direction_law.md`
- `docs/development/dependency_direction_guidelines.md`
- `tests/contract/dependency_direction/**`
- `.aide/reports/DEPENDENCY-DIRECTION-01-status.md`
- `.aide/reports/DEPENDENCY-DIRECTION-01-results.json`
- `.aide/reports/DEPENDENCY-DIRECTION-01-initial-scan.md`
- `.aide/reports/DEPENDENCY-DIRECTION-01-initial-scan.json`
- `.aide/reports/DEPENDENCY-DIRECTION-01-fast-strict.md`
- `docs/repo/audits/DEPENDENCY_DIRECTION_01.md`

## Changed Files Summary

Adds provisional repository dependency-direction law and a strict tracked-file
validator. Registers the law in public-surface governance and records current
dependency-direction violations as debt rather than hiding them.

## Validation Summary

The validator compiles and parser checks pass. The dependency-direction strict
scan currently fails with existing repo debt: 358 violations and 38 warnings in
the initial scan. Surrounding public-surface, ABI, repo layout, root allowlist,
distribution, component, docs, build-boundary, UI, and ABI checks pass.

## Token Summary

This review packet is intentionally compact; full scan findings live in
`.aide/reports/DEPENDENCY-DIRECTION-01-initial-scan.json`.

## Risk Summary

The dependency graph is not clean. Existing Python imports from active roots into
`tools/` remain current debt and must be repaired or precisely excepted in a
future bounded task.

## Non-Goals / Scope Guard

No feature implementation, command surface, provider model, compatibility corpus,
package runtime change, public release, or full CTest proof.

## Reviewer Instructions

Confirm that the law is explicit, the validator does not silently weaken real
violations, and current debt is reported honestly.
