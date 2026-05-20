# AIDE Review Packet

## Review Objective

Review `COMMAND-SURFACE-01`: command/result/view/event/refusal/evidence surface
law, validator, fixtures, documentation, public-surface registration, and
evidence.

## Decision Requested

`PASS | PASS_WITH_NOTES | REQUEST_CHANGES | BLOCKED`

## Task Packet Reference

`.aide/context/latest-task-packet.md`

## Context Packet Reference

`.aide/context/latest-context-packet.md`

## Verification Report Reference

`.aide/reports/COMMAND-SURFACE-01-validation.md`

## Evidence Packet References

- `contracts/command/command_surface.contract.toml`
- `contracts/command/command.schema.json`
- `contracts/result/result.schema.json`
- `contracts/view/view_surface.contract.toml`
- `contracts/event/event_surface.contract.toml`
- `contracts/refusal/refusal_code.registry.json`
- `contracts/evidence/evidence_packet.schema.json`
- `tools/validators/contracts/check_command_surface.py`
- `docs/architecture/command_view_event_refusal.md`
- `docs/development/command_surface_guidelines.md`
- `tests/contract/command_surface/**`
- `.aide/reports/COMMAND-SURFACE-01-status.md`
- `.aide/reports/COMMAND-SURFACE-01-results.json`
- `.aide/reports/COMMAND-SURFACE-01-fast-strict.md`
- `docs/repo/audits/COMMAND_SURFACE_01.md`

## Changed Files Summary

Adds a provisional command-surface governance spine and validator. Registers
foundational validation/test commands without implementing runtime dispatch or
Workbench behavior.

## Validation Summary

The command validator compiles and passes strict mode with 5 provisional
commands and 0 findings. Fixture mode passes. Public-surface validation passes
with command-related surfaces registered. Dependency-direction strict validation
still fails on known existing debt from DEPENDENCY-DIRECTION-01.

## Token Summary

This review packet is intentionally compact; full validation details live in
`.aide/reports/COMMAND-SURFACE-01-validation.md`.

## Risk Summary

The command surface is provisional. Runtime dispatch, Workbench integration,
full diagnostic codes, and capability/refusal law remain future Foundation Lock
work.

## Non-Goals / Scope Guard

No feature implementation, command runtime dispatch, Workbench UI, provider
model, compatibility corpus, package runtime change, public release, or full
CTest proof.

## Reviewer Instructions

Confirm that command IDs, schemas, refusals, views, events, and evidence are
registered honestly and that Workbench/CLI/AIDE surfaces are not granted
separate authority.
