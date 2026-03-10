Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none

# PACK-COMPAT-0 Baseline

## Scope

PACK-COMPAT-0 establishes the deterministic `pack.compat.json` sidecar and its offline validation path.

This baseline covers:
- manifest fields and degrade modes
- offline validation rules
- integration with MOD-POLICY capability/trust metadata
- pack-lock identity integration

Non-goals confirmed:
- no existing pack content semantics changed
- no online verification is required
- no simulation behavior changed

## Manifest Surface

Canonical sidecar:
- `pack.compat.json`

Canonical schema surface:
- `schemas/pack_compat_manifest.schema.json`
- `schema/packs/pack_compat_manifest.schema`

Required fields:
- `pack_id`
- `pack_version`
- `trust_level_id`
- `capability_ids`
- `required_contract_ranges`
- `required_registry_ids`
- `degrade_mode_id`
- `migration_refs`
- `deterministic_fingerprint`
- `extensions`

Optional fields:
- `required_protocol_ranges`
- `supported_engine_version_range`
- `provides`

Degrade registry:
- `pack.degrade.strict_refuse`
- `pack.degrade.best_effort`
- `pack.degrade.read_only_only`

## Validation Rules

Offline validation is performed by `src/packs/compat/pack_compat_validator.py`.

Validation checks:
- schema validity against `pack_compat_manifest`
- `pack_id` and `pack_version` match adjacent `pack.json`
- `trust_level_id` matches adjacent `pack.trust.json`
- `capability_ids` match adjacent `pack.capabilities.json`
- required semantic contracts exist in the semantic contract registry
- required registries exist locally
- `degrade_mode_id` exists in the pack degrade-mode registry
- deterministic fingerprint matches the canonically serialized payload

Strictness:
- `mod_policy.strict` refuses missing `pack.compat.json`
- non-strict/lab policy emits deterministic warnings for missing sidecars

Canonical refusals:
- `refusal.pack.contract_mismatch`
- `refusal.pack.missing_capability`
- `refusal.pack.missing_registry`
- `refusal.pack.compat_manifest_missing`

## Pack Lock Integration

`pack_lock_hash` identity now includes:
- `trust_level_id`
- `capability_ids`
- `trust_descriptor_hash`
- `capabilities_hash`
- `compat_manifest_hash`
- `pack_degrade_mode_id`

This means pack-lock identity changes whenever compatibility metadata changes, even if `pack.json` content stays constant.

MVP runtime bundle integration now requires compat sidecars for source packs and records:
- `compat_manifest_hash`
- `pack_degrade_mode_id`
- `source_pack_lock_hash`

## Mod Policy Integration

PACK-COMPAT-0 composes with MOD-POLICY-0:
- trust and capability declarations remain adjacent sidecars
- compatibility validation runs before pack load/compile proceeds
- strict policy can refuse missing compatibility metadata deterministically

The compatibility sidecar does not replace MOD-POLICY.
It adds explicit offline contract, registry, and degrade declarations.

## Readiness

Ready for:
- PACK-COMPAT-1 setup-time verification
- launcher/server deterministic pack refusal with remediation
- stronger offline pack-lock and replay validation
