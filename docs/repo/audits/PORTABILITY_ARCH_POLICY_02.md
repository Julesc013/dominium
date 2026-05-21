Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional
Task: PORTABILITY-ARCH-POLICY-02
Result: PASS_WITH_WARNINGS

# PORTABILITY_ARCH_POLICY_02

PORTABILITY-ARCH-POLICY-02 is PASS_WITH_WARNINGS.

## What Changed

- Added `contracts/platform/architecture_policy.contract.toml`.
- Added `contracts/platform/architecture_tier.registry.json`.
- Added `contracts/platform/pointer_width_policy.schema.json`.
- Added `contracts/platform/endian_policy.contract.toml`.
- Added `contracts/platform/architecture_claim.schema.json`.
- Added `tools/validators/platform/check_architecture_policy.py`.
- Added architecture policy fixtures under `tests/contract/architecture_policy/`.
- Added native architecture, pointer-width serialization, build-target, and release support docs.
- Updated portability matrix rows with `architecture_tier`, word-size, and endian declarations.
- Registered architecture diagnostics, refusals, capabilities, and public surfaces.
- Added the architecture policy validator to fast strict.

## Policy

- Full native products use `source_native_64`.
- Mainline full-native architectures are `x86_64` and `arm64`.
- `x64` remains a compatibility alias for `x86_64`.
- 32-bit targets are constrained/research/projection/archive lanes, not mainline product obligations.
- Persisted formats must not use pointer-width/native-layout fields.
- Mainline persisted and protocol formats use explicit little-endian fixed-width encodings.

## Validation

- Architecture policy validator: PASS.
- Portability matrix validator: PASS.
- Public surface, diagnostics, capability/refusal, provider, artifact, schema/protocol, language, ABI, dependency-direction, RepoX, AIDE, docs, build boundary, UI purity, and ABI boundary checks: PASS.
- Fast strict: PASS, 33 commands, 296.553 seconds.
- CMake configure/build and smoke CTest: PASS through fast strict.
- Full CTest: not run; remains T4/full-gate debt.

## Warnings

- RepoX STRICT keeps the known stale AuditX warning.
- ABI public-header stable-promotion warnings remain unrelated debt.
- Dependency-direction strict passes with 68 warnings.
- Pointer-width inventory is descriptive and recommends `POINTER-WIDTH-SERIALIZATION-AUDIT-01` if promoted.

## Next

`WORKBENCH-VALIDATION-SLICE-01`.
