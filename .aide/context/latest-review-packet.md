# AIDE Review Packet

## Review Objective

Review `REPLACEMENT-PROTOCOL-01`: replacement protocol law, packet/impact/proof
schemas, kind/status registries, rollback/conformance/migration-refusal
policies, validator, fixtures, docs, public-surface registration,
diagnostics/refusal integration, inventory, and evidence.

## Decision Requested

`PASS | PASS_WITH_NOTES | REQUEST_CHANGES | BLOCKED`

## Task Packet Reference

`.aide/context/latest-task-packet.md`

## Context Packet Reference

`.aide/context/latest-context-packet.md`

## Verification Report Reference

`.aide/reports/REPLACEMENT-PROTOCOL-01-validation.md`

## Evidence Packet References

- `contracts/replacement/replacement.contract.toml`
- `contracts/replacement/replacement_packet.schema.json`
- `contracts/replacement/replacement_kind.registry.json`
- `contracts/replacement/replacement_status.registry.json`
- `contracts/replacement/replacement_impact.schema.json`
- `contracts/replacement/replacement_proof.schema.json`
- `contracts/replacement/rollback_policy.contract.toml`
- `contracts/replacement/conformance_policy.contract.toml`
- `contracts/replacement/migration_refusal_policy.contract.toml`
- `tools/validators/repo/check_replacement_packet.py`
- `tests/contract/replacement/**`
- `docs/architecture/replacement_protocol.md`
- `docs/development/replacement_protocol_guidelines.md`
- `.aide/reports/REPLACEMENT-PROTOCOL-01-status.md`
- `.aide/reports/REPLACEMENT-PROTOCOL-01-results.json`
- `.aide/reports/REPLACEMENT-PROTOCOL-01-fast-strict.md`
- `docs/repo/audits/REPLACEMENT_PROTOCOL_01.md`

## Changed Files Summary

Adds a provisional replacement protocol governance spine. Registers replacement
surfaces, diagnostics, and refusal codes without performing an actual
implementation replacement, migration, rollback, runtime loader, or directory
move.

## Validation Summary

Replacement validator compiles and passes strict mode with 0 findings. Fixture
mode passes with 4 valid replacement packet fixtures and 4 negative fixtures.
Inventory mode scans 17,942 tracked files and classifies 1,824 replacement-like
historical/future-candidate files descriptively. Dependency-direction debt
remains known existing debt.

## Token Summary

This review packet is intentionally compact; full validation details live in
`.aide/reports/REPLACEMENT-PROTOCOL-01-validation.md`.

## Risk Summary

Replacement protocol is provisional. Historical refactors are inventoried but
not retroactively converted into full packets. Runtime migration, rollback,
provider resolver, Workbench UI, and version/deprecation law remain future work.

## Non-Goals / Scope Guard

No actual replacement, rewrite, directory move, runtime module/provider loading,
migration runtime, rollback runtime, Workbench UI, release publication, or
product behavior change.

## Reviewer Instructions

Confirm that replacement identity is not implementation path, public/durable
compatibility changes require proof or migration/refusal, and active
replacement packets require rollback evidence.
