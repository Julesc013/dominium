Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/contracts/SEMANTIC_CONTRACT_MODEL.md`, `docs/meta/UNIVERSE_CONTRACT_BUNDLE.md`, `docs/modding/MOD_TRUST_AND_CAPABILITIES.md`, and `docs/geo/OVERLAY_CONFLICT_POLICIES.md`

# Pack Compatibility Manifest

## Purpose

Define the deterministic compatibility sidecar for packs.

`pack.compat.json` makes a pack self-describing for:
- offline setup verification
- launcher compatibility checks
- deterministic pack-lock construction
- strict refusal with remediation when required contracts or registries are missing

This document does not change pack content semantics.
It governs validation, load eligibility, degrade posture, and migration references.

## Placement

Each pack directory may contain:
- `pack.json`
- `pack.trust.json`
- `pack.capabilities.json`
- `pack.compat.json`

`pack.compat.json` is the compatibility sidecar.

Backward-compatibility rule:
- older packs may omit `pack.compat.json`
- strict policy surfaces must refuse packs missing it
- lab/default policy surfaces may warn and continue deterministically

## PackCompatManifest Fields

Canonical fields:
- `pack_id`
- `pack_version`
- `trust_level_id`
- `capability_ids`
- `required_contract_ranges`
- `required_protocol_ranges` (optional)
- `supported_engine_version_range` (optional)
- `required_registry_ids` (optional)
- `provides` (optional declared surfaces)
- `degrade_mode_id`
- `migration_refs`
- `deterministic_fingerprint`
- `extensions`

### `required_contract_ranges`

Maps a semantic contract family to a required range or exact version.

Examples:
- `contract.worldgen.refinement.v1` exact
- `contract.overlay.merge.v1` exact

For MVP, exact `v1` is the normal case.

### `required_protocol_ranges`

Optional protocol requirements for products that interpret the pack through negotiated transports or IPC surfaces.

### `required_registry_ids`

Registry ids that must exist locally before the pack can load lawfully.
Missing required registries must refuse with a deterministic remediation path.

### `provides`

Declared surfaces the pack introduces, for example:
- templates
- processes
- logic elements
- schemas
- overlay layers

This is declarative and audit-facing.
It does not replace contribution parsing.

### `degrade_mode_id`

Canonical degrade modes:
- `pack.degrade.strict_refuse`
- `pack.degrade.best_effort`
- `pack.degrade.read_only_only`

Meaning:
- `strict_refuse`: pack must refuse if requirements are unmet
- `best_effort`: pack may disable optional surfaces deterministically
- `read_only_only`: pack may participate only in observation-safe flows when contracts mismatch

### `migration_refs`

Optional CompatX migration ids required for explicit migration or remediation.

## Deterministic Verification

Verification rules:
- `pack.compat.json` must be canonically serialized
- keys and list outputs must be deterministically ordered
- `deterministic_fingerprint` is computed with the fingerprint field blanked
- the manifest hash must be included in pack-lock identity when present

## Validation Rules

Offline validation must check:
- schema validity
- `pack_id` matches adjacent `pack.json`
- `pack_version` matches adjacent `pack.json`
- contract ranges are satisfiable against the current semantic contract registry
- capabilities are consistent with MOD-POLICY declarations
- required registries exist
- degrade mode exists in the degrade-mode registry

## Failure Modes

Canonical refusal codes:
- `refusal.pack.contract_mismatch`
- `refusal.pack.missing_capability`
- `refusal.pack.missing_registry`
- `refusal.pack.compat_manifest_missing`

Canonical remediation hints include:
- update engine/runtime
- remove pack
- run migration tool
- change mod policy

## Strictness

Policy behavior:
- `mod_policy.strict`: missing or invalid `pack.compat.json` is a refusal
- non-strict/lab policy: missing `pack.compat.json` produces deterministic warnings and continues only when all other rules permit

No pack may bypass compatibility validation in strict mode.
