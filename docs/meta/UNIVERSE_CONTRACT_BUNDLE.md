Status: CANONICAL
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/contracts/SEMANTIC_CONTRACT_MODEL.md`, `schema/universe/universe_identity.schema`, and `schema/session/session_spec.schema`.

# Universe Contract Bundle

## Purpose
- Pin semantic contract versions at universe creation time.
- Make contract meaning an immutable part of save/load/replay compatibility.
- Prevent silent semantic drift across long-lived universes.

## Creation Rule
- Universe creation must load `data/registries/semantic_contract_registry.json`.
- Default v0.0.0 behavior pins the full `*.v1` semantic contract family.
- Overrides are allowed only through an explicit creation-time profile or migration tool.
- If the semantic contract registry is missing or invalid, universe creation must refuse.

## Storage Rule
- `UniverseIdentity` stores:
  - `universe_contract_bundle_ref`
  - `universe_contract_bundle_hash`
- The canonical sidecar file is `universe_contract_bundle.json`.
- The sidecar reference is relative to the identity artifact directory.
- `UniverseIdentity.identity_hash` must not fold the sidecar metadata into identity-derived object IDs.

## Session Rule
- Every created `SessionSpec` must store:
  - `universe_id`
  - `pack_lock_hash`
  - `contract_bundle_hash`
- `SessionSpec` may additionally store `semantic_contract_registry_hash` for explicit replay-proof validation.

## Enforcement Rule
- Load must refuse when:
  - `UniverseIdentity` has no contract-bundle ref/hash
  - the sidecar file is missing
  - the sidecar hash does not match identity or session metadata
  - the pinned bundle does not validate against the current semantic contract registry
- Replay must additionally refuse when the session-recorded semantic contract registry hash mismatches the current runtime registry hash.

## Refusal Codes
- `refusal.contract.missing_bundle`
- `refusal.contract.mismatch`

## Remediation
- Run the explicit CompatX migration tool for the affected universe lineage.
- If no migration exists, recreate the universe under the current semantic contract bundle.

## Proof Integration
- Proof bundles must carry:
  - `semantic_contract_registry_hash`
  - `universe_contract_bundle_hash`
- Replay validation must compare those pins before authoritative runtime work proceeds.

## Non-Goals
- No simulation behavior change.
- No silent migration.
- No network dependency.
