Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none

# PUBLIC-SURFACE-REGISTRY-01 Audit

## Scope

This task creates Dominium's initial machine-readable public surface registry.
It classifies important exposed surfaces as public, internal, provisional,
stable, generated, fixture, historical, or retired without changing product or
runtime behavior.

No feature code, Workbench implementation, renderer work, package runtime
change, ABI rewrite, release artifact, or broad directory move is in scope.

## Created Surfaces

- `contracts/public_surface/public_surface.contract.toml`
- `contracts/public_surface/surface.schema.json`
- `contracts/public_surface/surface_kind.registry.json`
- `contracts/public_surface/surface_stability.registry.json`
- `tools/validators/repo/check_public_surface.py`
- `tests/contract/public_surface/**`
- `docs/architecture/public_surface_registry.md`
- `docs/development/public_surface_guidelines.md`
- `.aide/reports/PUBLIC-SURFACE-REGISTRY-01-*`
- `docs/architecture/CANON_INDEX.md` DERIVED index entry for the new architecture doc
- `docs/archive/audit/identity_fingerprint.json` refreshed after the index update

## Initial Registry Approach

The initial registry uses umbrella surfaces for headers, schemas, registries,
content packs, release metadata, Workbench modules, generated archive evidence,
fixtures, and retired roots. It marks only repo layout and root allowlist as
`stable_data_contract` because both have strict validator proof in the normal
gate.

Everything else remains conservative: mostly `provisional`, `internal`,
`fixture`, `historical`, or `retired`.

## Proof

- public surface validator: PASS.
- fixture checks: PASS.
- RepoX STRICT: PASS.
- final fast strict proof: PASS, 30/30 commands, 299.828 seconds.
- final fast strict proof is recorded in `.aide/reports/PUBLIC-SURFACE-REGISTRY-01-validation.md`.

## Known Limitations

- Individual public headers are not split into stable API/ABI entries yet.
- Compatibility corpus is not populated by this task.
- Command, diagnostic, provider, schema/protocol, artifact identity, and
  replacement protocol hardening remain later Foundation Lock tasks.
- Full CTest remains T4 full/release proof and is not part of this normal gate.

## Next Task

`API-ABI-CANON-01`
