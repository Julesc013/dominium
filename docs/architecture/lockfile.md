Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` v1.0.0, `docs/canon/glossary_v1.md` v1.0.0, and `schemas/bundle_lockfile.schema.json` v1.0.0.

# Lockfile Contract v1

## Purpose
Define deterministic bundle composition output for pack resolution and derived registry hash binding.

## Schema
- File: `schemas/bundle_lockfile.schema.json`
- Version: `1.0.0`
- CLI producers/consumers:
  - `tools/xstack/lockfile_build.cmd`
  - `tools/xstack/lockfile_validate.cmd`
  - `tools/setup/build` (packages lockfile into dist)
  - `tools/launcher/launch` (enforces lockfile at launch)

## XStack Invocation
`tools/xstack/run` integrates lockfile lifecycle in deterministic order:
1. `04.registry.compile` (produces `build/lockfile.json`)
2. `05.lockfile.validate` (schema + hash validation)
3. `07.session_boot.smoke` (consumes validated lockfile for boot smoke)

## Fields
- `lockfile_version` (const `1.0.0`)
- `bundle_id` (for example `bundle.base.lab`)
- `resolved_packs[]`:
  - `pack_id`
  - `version`
  - `canonical_hash`
  - `signature_status`
- `registries`:
  - `domain_registry_hash`
  - `law_registry_hash`
  - `experience_registry_hash`
  - `lens_registry_hash`
  - `astronomy_catalog_index_hash`
  - `site_registry_index_hash`
  - `ui_registry_hash`
- `compatibility_version`
- `pack_lock_hash`

## Deterministic Hash Computation
`pack_lock_hash` is computed from canonical JSON over sorted `resolved_packs[]` projection:

```json
[
  {
    "pack_id": "...",
    "version": "...",
    "canonical_hash": "...",
    "signature_status": "..."
  }
]
```

Sort key:
1. `pack_id`
2. `version`
3. `canonical_hash`
4. `signature_status`

Canonical serialization:
- UTF-8
- sorted object keys
- newline-free canonical text for hashing
- no trailing whitespace

## Validation and Refusal
Validation rejects deterministically on:
- missing required field
- invalid registry hash shape (must be 64-hex sha256)
- invalid lockfile version
- malformed `resolved_packs`
- `pack_lock_hash` mismatch

`tools/xstack/lockfile_validate.cmd` emits deterministic refusal messages and stable-sorted errors.
`tools/launcher/launch` additionally refuses incompatible save/session combinations with:
- `LOCKFILE_MISMATCH`
- `PACK_INCOMPATIBLE`
- `REGISTRY_MISMATCH`

## Invariants
- No mode flags are introduced in lockfile generation or validation.
- Lockfile is derived tooling output and does not execute runtime simulation behavior.
- Rebuilding with identical inputs must produce bitwise-identical lockfile output.
- No nondeterministic timestamps appear in lockfile payload.

## Example
```json
{
  "lockfile_version": "1.0.0",
  "bundle_id": "bundle.base.lab",
  "resolved_packs": [
    {
      "pack_id": "pack.core.runtime",
      "version": "1.0.0",
      "canonical_hash": "placeholder.pack.core.runtime.v1",
      "signature_status": "verified"
    }
  ],
  "registries": {
    "domain_registry_hash": "16a4c655e0fdc0575bc0647fe7006891a68785dbddeeb1531b48832d7beb4b39",
    "law_registry_hash": "9815331875cbf9ae27bd9ad39f92b172ac5974367af0ff42751d6bde16e2ad49",
    "experience_registry_hash": "e6f832298d130c521ae93e254e0822a30df48ea63cdf6ec5c5b1d2243918ba6a",
    "lens_registry_hash": "2d1fc3eeb12dcc53d1c475f410873c1e06ae5b9047386ae3b4e5a6f6a1fc56b8",
    "astronomy_catalog_index_hash": "17d6d7e8f8fb7fb353555878beb42356ca5a5e628143ae3b4b121220c9b8e482",
    "site_registry_index_hash": "3c01c5f0bd3706be54fa2c4d7cc8a2d2255cfb3fa9b7d58808747bcd74d2718d",
    "ui_registry_hash": "c9457d0f9f67cd0deda35a90c4848136b83303ba5231dc152747dda6383294f3"
  },
  "compatibility_version": "1.0.0",
  "pack_lock_hash": "959cbb2f3e2929b887e05a79abb5d0f71b495960aa9418ebc923f1bd7b192daa"
}
```

## TODO
- Add CompatX migration route templates for future lockfile schema major versions.
- Add optional signature proof bindings once SecureX lock attestation is implemented.

## Cross-References
- `docs/architecture/registry_compile.md`
- `docs/architecture/pack_system.md`
- `docs/architecture/deterministic_packaging.md`
- `docs/architecture/setup_and_launcher.md`
- `docs/contracts/versioning_and_migration.md`
- `tools/xstack/registry_compile/lockfile.py`
