# AIDE Review Packet

## Review Objective

Review `SCHEMA-PROTOCOL-LAW-01`: schema/protocol/registry evolution contracts,
canonical serialization, migration/refusal policy, validator, fixtures,
documentation, public-surface registration, diagnostics integration, inventory,
and evidence.

## Decision Requested

`PASS | PASS_WITH_NOTES | REQUEST_CHANGES | BLOCKED`

## Task Packet Reference

`.aide/context/latest-task-packet.md`

## Context Packet Reference

`.aide/context/latest-context-packet.md`

## Verification Report Reference

`.aide/reports/SCHEMA-PROTOCOL-LAW-01-validation.md`

## Evidence Packet References

- `contracts/schema/schema_evolution.contract.toml`
- `contracts/protocol/protocol_evolution.contract.toml`
- `contracts/registry/registry_evolution.contract.toml`
- `contracts/serialization/canonical_serialization.contract.toml`
- `contracts/migration/migration_policy.contract.toml`
- `contracts/schema/schema_policy.schema.json`
- `contracts/protocol/protocol_policy.schema.json`
- `contracts/registry/registry_policy.schema.json`
- `tools/validators/contracts/check_schema_protocol_evolution.py`
- `docs/architecture/schema_protocol_evolution.md`
- `docs/development/schema_protocol_guidelines.md`
- `tests/contract/schema_protocol/**`
- `.aide/reports/SCHEMA-PROTOCOL-LAW-01-status.md`
- `.aide/reports/SCHEMA-PROTOCOL-LAW-01-results.json`
- `.aide/reports/SCHEMA-PROTOCOL-LAW-01-fast-strict.md`
- `docs/repo/audits/SCHEMA_PROTOCOL_LAW_01.md`

## Changed Files Summary

Adds a provisional schema/protocol evolution governance spine and validator.
Registers schema/protocol law surfaces and diagnostics without implementing
runtime migration, protocol dispatch, package/save/replay loading, or Workbench
behavior.

## Validation Summary

The schema/protocol validator compiles and passes strict mode with 0 findings.
Fixture mode passes with 7 fixtures. Inventory mode scans 17,808 tracked files
and classifies 2,489 schema/protocol-like files descriptively. Diagnostics and
public-surface validators pass after schema/protocol integration.

## Token Summary

This review packet is intentionally compact; full validation details live in
`.aide/reports/SCHEMA-PROTOCOL-LAW-01-validation.md`.

## Risk Summary

The schema/protocol law is provisional. Existing schemas and registries are
inventoried but not migrated. Compatibility corpus, capability/refusal law,
provider model, runtime migration, and Workbench presentation remain future
Foundation Lock work.

## Non-Goals / Scope Guard

No feature implementation, runtime migration, protocol dispatch, package/save/
replay loader, Workbench UI, provider model, public release, or full CTest proof.

## Reviewer Instructions

Confirm that schema/protocol identity is semantic ID plus version/policy, not
path-based, and that existing schemas are inventoried rather than silently
migrated.
