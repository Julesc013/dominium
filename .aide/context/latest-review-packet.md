# AIDE Review Packet

## Review Objective

Review `PROVIDER-MODEL-01`: provider model contract, descriptor and selection
schemas, kind/lifecycle registries, conformance/capability/trust policies,
validator, fixtures, documentation, public-surface registration,
diagnostics/refusal/capability integration, inventory, and evidence.

## Decision Requested

`PASS | PASS_WITH_NOTES | REQUEST_CHANGES | BLOCKED`

## Task Packet Reference

`.aide/context/latest-task-packet.md`

## Context Packet Reference

`.aide/context/latest-context-packet.md`

## Verification Report Reference

`.aide/reports/PROVIDER-MODEL-01-validation.md`

## Evidence Packet References

- `contracts/provider/provider.contract.toml`
- `contracts/provider/provider.registry.json`
- `contracts/provider/provider.schema.json`
- `contracts/provider/provider_descriptor.schema.json`
- `contracts/provider/provider_kind.registry.json`
- `contracts/provider/provider_lifecycle.registry.json`
- `contracts/provider/provider_selection_request.schema.json`
- `contracts/provider/provider_selection_decision.schema.json`
- `contracts/provider/provider_conformance.contract.toml`
- `contracts/provider/provider_capability_policy.contract.toml`
- `contracts/provider/provider_trust_policy.contract.toml`
- `tools/validators/contracts/check_provider_model.py`
- `docs/architecture/provider_model.md`
- `docs/development/provider_guidelines.md`
- `tests/contract/provider/**`
- `.aide/reports/PROVIDER-MODEL-01-status.md`
- `.aide/reports/PROVIDER-MODEL-01-results.json`
- `.aide/reports/PROVIDER-MODEL-01-fast-strict.md`
- `docs/repo/audits/PROVIDER_MODEL_01.md`

## Changed Files Summary

Adds a provisional provider governance spine and validator. Registers provider
model surfaces and provider diagnostics/refusals without implementing runtime
provider resolution, dynamic loading, renderer/platform fallback, package
runtime, or Workbench behavior.

## Validation Summary

The provider validator compiles and passes strict mode with 0 findings. Fixture
mode passes with 9 fixtures. Inventory mode scans 17,865 tracked files and
classifies 1,396 provider/backend/service/adapter/capability candidates
descriptively. Capability/refusal, diagnostics, command-surface, public-surface,
schema/protocol, artifact, and ABI validators pass. Dependency-direction debt
remains known existing debt.

## Token Summary

This review packet is intentionally compact; full validation details live in
`.aide/reports/PROVIDER-MODEL-01-validation.md`.

## Risk Summary

The provider model is provisional. Current providers, backends, Workbench
modules, packs, and runtime systems are inventoried but not migrated. Runtime
provider selection, dynamic/native loading, conformance suites, and mod/native
trust hardening remain future work.

## Non-Goals / Scope Guard

No feature implementation, provider runtime resolver, dynamic loader,
renderer/platform fallback, package/profile loader runtime, Workbench UI, public
release, or full CTest proof.

## Reviewer Instructions

Confirm that provider identity is not path identity, that selection/fallback is
typed through capability/refusal/degradation/evidence law, and that current
providers are inventoried rather than silently migrated.
