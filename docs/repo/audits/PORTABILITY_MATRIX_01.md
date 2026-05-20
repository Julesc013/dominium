# PORTABILITY-MATRIX-01 Audit

Status: PASS_WITH_WARNINGS
Task: PORTABILITY-MATRIX-01

## Why

Dominium portability claims now require matrix rows with explicit platform, architecture, toolchain, ABI, provider, package, product mode, status, limitation, diagnostic/refusal, and evidence fields.

## Added

- `contracts/platform/**`
- `tools/validators/platform/check_portability_matrix.py`
- `tests/contract/portability/**`
- `docs/architecture/portability_matrix.md`
- `docs/development/portability_guidelines.md`
- `docs/build/toolchain_portability.md`
- `docs/release/platform_support_policy.md`

## Proof

- Portability validator strict/json/fixtures/inventory: PASS.
- JSON/TOML parse: PASS.
- Public surface, diagnostics, command, capability/refusal, provider, module, replacement, versioning, mod/pack trust, schema/protocol, artifact validators: PASS.
- Fast strict: PASS, 32 commands, 312.297 seconds.

## Known Limitations

- Matrix is provisional.
- No new OS/toolchain/renderer/product/package/release support is claimed.
- No runtime provider, renderer, package, product, build, or release behavior is implemented.
- Dependency-direction and ABI warning debt remain visible.

Next task: `FOUNDATION-CLOSEOUT-01`.
