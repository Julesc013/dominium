# AIDE Review Packet

## Review Objective

Review `CAPABILITY-REFUSAL-LAW-01`: capability registry, request/decision
schemas, degradation/recovery policy, refusal contract/schema/registry,
validator, fixtures, documentation, public-surface registration, diagnostics and
command-surface integration, inventory, and evidence.

## Decision Requested

`PASS | PASS_WITH_NOTES | REQUEST_CHANGES | BLOCKED`

## Task Packet Reference

`.aide/context/latest-task-packet.md`

## Context Packet Reference

`.aide/context/latest-context-packet.md`

## Verification Report Reference

`.aide/reports/CAPABILITY-REFUSAL-LAW-01-validation.md`

## Evidence Packet References

- `contracts/capability/capability.contract.toml`
- `contracts/capability/capability.registry.json`
- `contracts/capability/capability.schema.json`
- `contracts/capability/capability_request.schema.json`
- `contracts/capability/capability_decision.schema.json`
- `contracts/capability/degradation_policy.contract.toml`
- `contracts/capability/recovery_policy.contract.toml`
- `contracts/refusal/refusal.contract.toml`
- `contracts/refusal/refusal_code.registry.json`
- `contracts/refusal/refusal.schema.json`
- `tools/validators/contracts/check_capability_refusal.py`
- `docs/architecture/capability_refusal_law.md`
- `docs/development/capability_refusal_guidelines.md`
- `tests/contract/capability_refusal/**`
- `.aide/reports/CAPABILITY-REFUSAL-LAW-01-status.md`
- `.aide/reports/CAPABILITY-REFUSAL-LAW-01-results.json`
- `.aide/reports/CAPABILITY-REFUSAL-LAW-01-fast-strict.md`
- `docs/repo/audits/CAPABILITY_REFUSAL_LAW_01.md`

## Changed Files Summary

Adds a provisional capability/refusal governance spine and validator. Registers
capability/refusal law surfaces and diagnostics without implementing runtime
capability resolution, provider selection, renderer/platform fallback, package
runtime, or Workbench behavior.

## Validation Summary

The capability/refusal validator compiles and passes strict mode with 0
findings. Fixture mode passes with 8 fixtures. Inventory mode scans 17,837
tracked files and classifies 1,190 capability/refusal/provider/trust candidates
descriptively. Diagnostics, command-surface, and public-surface validators are
expected to pass after integration.

## Token Summary

This review packet is intentionally compact; full validation details live in
`.aide/reports/SCHEMA-PROTOCOL-LAW-01-validation.md`.

## Risk Summary

The capability/refusal law is provisional. Current providers, backends, packs,
and Workbench modules are inventoried but not migrated. Provider model, runtime
capability resolution, mod/pack trust runtime, and Workbench presentation remain
future Foundation Lock work.

## Non-Goals / Scope Guard

No feature implementation, provider model, runtime capability resolver,
renderer/platform fallback, package/mod trust runtime, Workbench UI, public
release, or full CTest proof.

## Reviewer Instructions

Confirm that capability/refusal outcomes are typed and evidenced, that silent
fallback is forbidden, and that current providers are inventoried rather than
silently migrated.
