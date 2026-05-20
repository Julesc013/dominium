# PORTABILITY-MATRIX-01 Status

Task: PORTABILITY-MATRIX-01
Phase: foundation-lock
Result: PASS_WITH_WARNINGS
Branch: `main`
Starting HEAD: `2a9c1dc11cf139b82343a08a78297ea3fe1333a0`
Origin/main at start: `2a9c1dc11cf139b82343a08a78297ea3fe1333a0`
Ending HEAD: pending commit
Origin/main at validation: `2a9c1dc11cf139b82343a08a78297ea3fe1333a0`

## Created

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
- `.aide/reports/PORTABILITY-MATRIX-01-fast-strict.*`
- `docs/repo/audits/PORTABILITY_MATRIX_01.md`

## Counts

- Platform floors registered: 8.
- Architectures registered: 6.
- Toolchains registered: 10.
- Portability statuses registered: 13.
- Runtime rows: 3.
- Renderer rows: 6.
- Product mode rows: 4.
- Package rows: 3.

## Registry Updates

- Public surface registry updated: yes, 148 surfaces total after update.
- Diagnostics registry updated: yes, 89 diagnostic codes total.
- Refusal registry updated: yes, 44 refusal codes total.
- Capability registry updated: yes, 30 capabilities total.

## Proof

- Portability validator: PASS.
- Fixture validation: PASS, 4 valid fixtures and 4 invalid fixtures behaved as expected.
- Inventory mode: PASS_WITH_WARNINGS, descriptive only.
- Fast strict: PASS, 32 commands in 312.297 seconds.

## Known Warnings

- Portability matrix is initial and provisional.
- No new platform/toolchain support is claimed.
- No new CMake targets, presets, CI jobs, providers, renderers, packages, product modes, or release artifacts are added.
- Dependency-direction validator still reports known existing debt: 358 violations and 38 warnings.
- ABI validator passes with 2851 stable-promotion warnings.
- Full CTest/full release gates remain outside this task.

Next task: `FOUNDATION-CLOSEOUT-01`.
