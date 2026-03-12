Status: CANONICAL
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/contracts/SEMANTIC_CONTRACT_MODEL.md`, and `data/registries/extension_interpretation_registry.json`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Extension Discipline

## Purpose
- Make `extensions` lawful forward-compatibility metadata instead of an ad hoc behavior backdoor.
- Keep unknown extensions deterministic and inert by default.
- Require any extension interpretation to be explicit, versioned, and profile-gated.

## Namespacing
- Valid extension namespaces are:
  - `official.*`
  - `mod.<pack_id>.*`
  - `dev.*`
- Bare keys are legacy compatibility inputs only.
- Bare keys are not new authoring surface.

## Deterministic Behavior
- `extensions` are inert metadata unless code interpretation is declared in `data/registries/extension_interpretation_registry.json`.
- Unknown keys have no authoritative effect in `extensions.default`.
- `extensions.warn` may emit deterministic warnings for unknown or legacy keys.
- `extensions.strict` may refuse unknown namespaced keys.
- Legacy bare keys are treated as compatibility aliases for `mod.unknown.<key>` and remain non-authoritative unless a registry entry declares interpretation.

## Extension Interpretation Registry
- Source of truth: `data/registries/extension_interpretation_registry.json`
- Any interpreted key must declare:
  - `extension_key`
  - `allowed_owners`
  - `value_type`
  - `semantic_contract_version_required`
  - `profile_gate_required`
  - `deterministic_fingerprint`
- Legacy bare-key interpretations are represented through namespaced registry rows with `extensions.legacy_alias_for`.
- Interpretation without a registry entry is forbidden.

## Serialization
- `extensions` maps must be serialized in sorted key order.
- Deterministic normalization must happen before canonical hashing and fingerprinting.
- Nested extension values must serialize with stable ordering and stable primitive formats.
- Floating-point extension payloads are non-canonical and may warn or refuse under validation policy.

## Enforcement
- Shared loaders and hashing surfaces must normalize extensions before validation, hashing, or persistence.
- Strictness is profile-controlled through:
  - `extensions.default`
  - `extensions.warn`
  - `extensions.strict`
- Runtime interpretation must use the registry-backed extension access path or an equivalent registry-declared compatibility alias.

## Non-Goals
- No runtime worldgen, logic, or physics behavior change.
- No silent migration.
- No requirement to delete existing legacy bare keys in v0.0.0 data.
