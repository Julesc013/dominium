# AIDE Review Packet

## Review Objective

Review `DIAGNOSTIC-CODE-REGISTRY-01`: diagnostic code registry, severity/category
registries, evidence schemas, refusal cross-references, validator, fixtures,
documentation, public-surface registration, and evidence.

## Decision Requested

`PASS | PASS_WITH_NOTES | REQUEST_CHANGES | BLOCKED`

## Task Packet Reference

`.aide/context/latest-task-packet.md`

## Context Packet Reference

`.aide/context/latest-context-packet.md`

## Verification Report Reference

`.aide/reports/DIAGNOSTIC-CODE-REGISTRY-01-validation.md`

## Evidence Packet References

- `contracts/diagnostics/diagnostic_code.registry.json`
- `contracts/diagnostics/diagnostic_code.schema.json`
- `contracts/diagnostics/diagnostic_severity.registry.json`
- `contracts/diagnostics/diagnostic_category.registry.json`
- `contracts/diagnostics/diagnostic_policy.contract.toml`
- `contracts/evidence/evidence_packet.schema.json`
- `contracts/evidence/evidence_ref.schema.json`
- `contracts/event/event.schema.json`
- `contracts/refusal/refusal_code.registry.json`
- `tools/validators/contracts/check_diagnostics_registry.py`
- `docs/architecture/diagnostics_and_evidence.md`
- `docs/development/diagnostic_code_guidelines.md`
- `tests/contract/diagnostics/**`
- `.aide/reports/DIAGNOSTIC-CODE-REGISTRY-01-status.md`
- `.aide/reports/DIAGNOSTIC-CODE-REGISTRY-01-results.json`
- `.aide/reports/DIAGNOSTIC-CODE-REGISTRY-01-fast-strict.md`
- `docs/repo/audits/DIAGNOSTIC_CODE_REGISTRY_01.md`

## Changed Files Summary

Adds a provisional diagnostic/evidence governance spine and validator. Registers
foundational diagnostic codes without implementing runtime dispatch, Workbench
presentation, package behavior, or release publication.

## Validation Summary

The diagnostic validator compiles and passes strict mode with 14 provisional
diagnostic codes, 7 severities, 26 categories, and 0 findings. Fixture mode
passes. Public-surface validation passes with diagnostic/evidence surfaces
registered. Dependency-direction strict validation still fails on known existing
debt from DEPENDENCY-DIRECTION-01.

## Token Summary

This review packet is intentionally compact; full validation details live in
`.aide/reports/DIAGNOSTIC-CODE-REGISTRY-01-validation.md`.

## Risk Summary

The diagnostic registry is provisional. Runtime diagnostic dispatch, Workbench
presentation, capability/refusal law, artifact identity law, and full/release
proof remain future Foundation Lock work.

## Non-Goals / Scope Guard

No feature implementation, diagnostic runtime dispatch, Workbench UI, provider
model, package runtime change, public release, or full CTest proof.

## Reviewer Instructions

Confirm that diagnostic IDs, display codes, severities, categories, evidence
references, refusal links, and public-surface registrations are provisional,
honest, and machine-readable.
