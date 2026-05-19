Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# LIB5_FORKING_PROVIDES

## Changed

- `schema/package/provides/provides_declaration.schema`
- `schema/package/provides/provides_resolution.schema`
- `schema/profile/instance_manifest.schema`
- `schema/instance.manifest.schema`
- `schema/packs/pack_lock.schema`
- `schema/packs/pack_compat_manifest.schema`
- `schema/pack_manifest.schema`
- `tools/package/libraries/provides/__init__.py`
- `tools/package/libraries/provides/provider_resolution.py`
- `tools/package/libraries/instance/instance_validator.py`
- `tools/validators/package/compatibility_payload/pack_compat_validator.py`
- `tools/validators/package/compatibility_payload/pack_verification_pipeline.py`
- `tools/package/ops/ops_cli.py`
- `tools/package/launcher/launcher_cli.py`
- `tools/xstack/pack_loader/loader.py`
- `contracts/registry/provides_registry.json`
- `contracts/registry/resolution_policy_registry.json`

## Demand IDs

- `surv.knap_stone_tools`

## Contract Meaning

- packs can declare shareable provider surfaces without colliding on `pack_id`
- instances and verified locks can pin deterministic provider choices
- strict policies refuse ambiguity instead of auto-selecting a winner
- anarchy-style policies still choose deterministically and log the choice
- provider-implied capabilities flow into CAP-NEG without changing authoritative simulation law

## Unchanged

- pack identity remains stable and separate from provider choice
- existing legacy reverse-DNS pack ids remain loadable
- installs, instances, saves, and shareable artifacts stay offline-first and content-addressed
- simulation behavior and process-only mutation rules remain unchanged
