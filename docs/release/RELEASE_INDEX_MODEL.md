Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: UPDATE/TRUST
Replacement Target: signed multi-source release indices with trust-governed provider selection

# Release Index Model

## Release Index

`release_index.json` is the offline-first update surface for one release channel and platform artifact set.

Top-level fields:

- `channel`
- `release_series`
- `semantic_contract_registry_hash`
- `supported_protocol_ranges`
- `platform_matrix`
- `component_graph_hash`
- `components`
- `signatures` optional
- `deterministic_fingerprint`
- `extensions`

The `extensions` map carries additive runtime metadata:

- `release_id`
- `release_manifest_hash`
- `release_manifest_ref`
- `install_profile_id`
- embedded `component_graph`

## Channel Semantics

- `mock`: freeze/development validation surface; no auto-apply
- `alpha`: experimental opt-in channel
- `beta`: near-stable validation channel
- `rc`: release-candidate channel
- `stable`: production channel

## Update Resolution

Inputs:

- current install manifest
- local or explicit `release_index.json`
- selected install profile
- target platform/arch/abi
- trust policy later

Resolver steps:

1. load and canonicalize `release_index.json`
2. verify semantic contract hash and protocol-range compatibility
3. select the platform row deterministically
4. load the embedded component graph
5. resolve the target component set through the install profile
6. compare current selected components against target selected components
7. emit an `update_plan` with add/remove/upgrade sets and verification steps
8. log the resolution outcome and any refusal codes

## Offline-First

- If a remote index is unavailable, setup uses the local cached `manifests/release_index.json`.
- If no local index exists, update resolution refuses with `refusal.update.index_missing`.
- No network access is required for planning, verification, apply, or rollback.

## Rollback

- Setup maintains `.dsu/install_transaction_log.json`.
- Each successful update append records:
  - `transaction_id`
  - `from_release_id`
  - `to_release_id`
  - `backup_path`
  - `install_profile_id`
  - selected component ids
- `setup rollback --to <release_id>` selects the latest successful transaction whose `from_release_id` matches the requested target.

## Determinism

- Release index ordering is canonical.
- Component deltas are ordered lexicographically by component id.
- Verification steps are ordered deterministically by step id and component id.
- No wall-clock input participates in update resolution.
