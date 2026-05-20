# AIDE Review Packet

## Review Objective

Review `PORTABILITY-MATRIX-01`: portability contract, platform floor registry,
architecture registry, toolchain registry, status registry, runtime/renderer/
product/package matrices, evidence schema, refusal policy, validator, fixtures,
docs, public-surface registration, diagnostics/refusal/capability integration,
inventory, and fast strict proof.

## Decision Requested

`PASS | PASS_WITH_NOTES | REQUEST_CHANGES | BLOCKED`

## Task Packet Reference

`.aide/context/latest-task-packet.md`

## Context Packet Reference

`.aide/context/latest-context-packet.md`

## Verification Report Reference

`.aide/reports/PORTABILITY-MATRIX-01-validation.md`

## Evidence Packet References

- `contracts/platform/portability_matrix.contract.toml`
- `contracts/platform/platform_floor.registry.json`
- `contracts/platform/architecture.registry.json`
- `contracts/platform/toolchain.registry.json`
- `contracts/platform/platform_capability.schema.json`
- `contracts/platform/portability_evidence.schema.json`
- `contracts/platform/runtime_portability.matrix.json`
- `contracts/platform/renderer_portability.matrix.json`
- `contracts/platform/product_mode_portability.matrix.json`
- `contracts/platform/package_portability.matrix.json`
- `contracts/platform/portability_status.registry.json`
- `contracts/platform/portability_refusal_policy.contract.toml`
- `tools/validators/platform/check_portability_matrix.py`
- `tests/contract/portability/**`
- `docs/architecture/portability_matrix.md`
- `docs/development/portability_guidelines.md`
- `docs/build/toolchain_portability.md`
- `docs/release/platform_support_policy.md`
- `.aide/reports/PORTABILITY-MATRIX-01-status.md`
- `.aide/reports/PORTABILITY-MATRIX-01-results.json`
- `.aide/reports/PORTABILITY-MATRIX-01-fast-strict.md`
- `docs/repo/audits/PORTABILITY_MATRIX_01.md`

## Changed Files Summary

Adds a provisional portability matrix and validator. Registers platform floors,
architectures, toolchains, runtime/renderer/product/package portability rows,
diagnostics, refusals, capabilities, and public surfaces without implementing
new build targets, CI jobs, providers, renderers, package runtime, product
behavior, or release artifacts.

## Validation Summary

Portability validator compiles and passes strict/json/fixtures/inventory modes.
Fixtures pass with 4 valid fixtures and 4 negative fixtures. Fast strict passes
32 commands in 312.297 seconds. Dependency-direction debt remains known existing
debt; ABI stable-promotion warnings remain known debt.

## Token Summary

This review packet is compact; full validation details live in
`.aide/reports/PORTABILITY-MATRIX-01-validation.md`.

## Risk Summary

Portability law is provisional. Existing release/platform docs are inventoried
as evidence sources, not support claims. No runtime provider, renderer,
package, product mode, build target, CI job, or release behavior is implemented.

## Non-Goals / Scope Guard

No new platform/toolchain support claim, CMake preset, CI job, build target,
provider runtime, renderer implementation, package runtime, Workbench UI,
gameplay/domain/native GUI behavior, release tag, upload, or GitHub settings
mutation.

## Reviewer Instructions

Confirm that support claims require evidence, planned/research/provisional rows
are not presented as supported, product modes reference runtime capabilities,
provider/render fallback is not silent, and unsupported requests have typed
diagnostics/refusals.
