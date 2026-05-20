Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# VERSION-DEPRECATION-LAW-01

Result: PASS_WITH_WARNINGS

## Why

Dominium public surfaces, schemas, protocols, artifacts, commands, diagnostics,
providers, modules, packs, app descriptors, release artifacts, and compatibility
promises need explicit lifecycle and versioning rules. Stable behavior cannot be
inferred from existence, paths, filenames, or implementation directories.

## Contract And Schema Files

- `contracts/versioning/versioning.contract.toml`
- `contracts/versioning/lifecycle_state.registry.json`
- `contracts/versioning/version_compatibility.schema.json`
- `contracts/versioning/compatibility_range.schema.json`
- `contracts/versioning/deprecation_notice.schema.json`
- `contracts/versioning/version_transition.schema.json`
- `contracts/versioning/deprecation_policy.contract.toml`
- `contracts/versioning/retirement_policy.contract.toml`
- `contracts/versioning/removal_policy.contract.toml`
- `contracts/versioning/surface_lifecycle.contract.toml`

## Validator And Fixtures

- `tools/validators/contracts/check_version_deprecation.py`
- `tests/contract/versioning/**`

The validator supports `--repo-root`, `--strict`, `--json`, `--fixtures`, and
`--inventory`.

## Initial Inventory

The inventory scanned 17,970 tracked files and classified 2,479 version-like
surfaces. The largest buckets were schema/protocol surfaces, fixtures, release
surfaces, historical/audit records, descriptor surfaces, and replacement policy
surfaces.

Existing surfaces are inventoried only. This task does not migrate broad
versions or mark active surfaces stable.

## Proof Result

- Version/deprecation validator strict: pass.
- Fixture validation: pass, 3 valid fixtures and 4 negative fixtures.
- Diagnostics registry: pass with 70 codes.
- Refusal registry consumers: pass with 29 refusal codes.
- Public surface registry: pass with 133 surfaces.
- Fast strict: pass, 32 commands in 308.563 seconds.

Known existing dependency-direction debt remains visible and is not hidden.

## Known Limitations

- Version/deprecation law is initial and provisional.
- No active surfaces are deprecated, retired, removed, migrated, or promoted.
- Runtime migration is not implemented.
- Release promotion gate is not implemented.
- Compatibility corpus is not populated.
- Mod/pack trust model remains future work.

## Next

`MOD-PACK-TRUST-MODEL-01`
