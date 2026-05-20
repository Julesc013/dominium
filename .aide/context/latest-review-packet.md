# AIDE Review Packet

## Review Objective

Review `VERSION-DEPRECATION-LAW-01`: versioning law, lifecycle registry,
compatibility/deprecation/transition schemas, deprecation/retirement/removal
policies, validator, fixtures, docs, public-surface registration,
diagnostics/refusal integration, inventory, and evidence.

## Decision Requested

`PASS | PASS_WITH_NOTES | REQUEST_CHANGES | BLOCKED`

## Task Packet Reference

`.aide/context/latest-task-packet.md`

## Context Packet Reference

`.aide/context/latest-context-packet.md`

## Verification Report Reference

`.aide/reports/VERSION-DEPRECATION-LAW-01-validation.md`

## Evidence Packet References

- `contracts/versioning/versioning.contract.toml`
- `contracts/versioning/lifecycle_state.registry.json`
- `contracts/versioning/version_compatibility.schema.json`
- `contracts/versioning/compatibility_range.schema.json`
- `contracts/versioning/deprecation_notice.schema.json`
- `contracts/versioning/version_transition.schema.json`
- `contracts/versioning/deprecation_policy.contract.toml`
- `contracts/versioning/retirement_policy.contract.toml`
- `contracts/versioning/removal_policy.contract.toml`
- `contracts/versioning/surface_lifecycle.contract.toml`
- `tools/validators/contracts/check_version_deprecation.py`
- `tests/contract/versioning/**`
- `docs/architecture/versioning_and_deprecation.md`
- `docs/development/versioning_deprecation_guidelines.md`
- `.aide/reports/VERSION-DEPRECATION-LAW-01-status.md`
- `.aide/reports/VERSION-DEPRECATION-LAW-01-results.json`
- `.aide/reports/VERSION-DEPRECATION-LAW-01-fast-strict.md`
- `docs/repo/audits/VERSION_DEPRECATION_LAW_01.md`

## Changed Files Summary

Adds a provisional versioning/deprecation governance spine. Registers lifecycle,
compatibility, deprecation, retirement, removal, transition, diagnostic, refusal,
and validator surfaces without deprecating, retiring, removing, migrating, or
promoting any active surface.

## Validation Summary

Version/deprecation validator compiles and passes strict mode with 0 findings.
Fixture mode passes with 3 valid fixtures and 4 negative fixtures. Inventory mode
classifies current version-like surfaces descriptively. Dependency-direction debt
remains known existing debt.

## Token Summary

This review packet is compact; full validation details live in
`.aide/reports/VERSION-DEPRECATION-LAW-01-validation.md`.

## Risk Summary

Version/deprecation law is provisional. Existing version-like surfaces are
inventoried but not migrated. Runtime migration, release promotion,
compatibility corpus, and mod/pack trust remain future work.

## Non-Goals / Scope Guard

No actual deprecation, retirement, removal, migration runtime, release
promotion, Workbench UI, product behavior, gameplay, renderer, native GUI, or
active version rewrite.

## Reviewer Instructions

Confirm that stable surfaces require compatibility/proof, lifecycle transitions
are explicit, deprecation requires replacement or no-replacement reason, and
removal requires retirement history or deterministic refusal/bridge policy.
