Status: DERIVED
Last Reviewed: 2026-02-13
Supersedes: none
Superseded By: none

# Universe Identity And State

## Split Contract
- `UniverseIdentity` is immutable after creation.
- `UniverseContractBundle` is an immutable semantic sidecar written at the same creation step.
- `UniverseState` evolves over time and references checkpoints/refinement/history.

## Why the Split Exists
- Prevents accidental semantic drift from runtime edits to creation identity.
- Enables compatibility checks and migrations to target identity changes explicitly.
- Keeps replay/save determinism anchored to stable identity and explicit state references.

## UniverseIdentity
- Stable keys:
  - `universe_id`
  - `global_seed`
  - domain binding IDs
  - physics/constants profile reference
  - default GEO profile references:
    - `topology_profile_id`
    - `metric_profile_id`
    - `partition_profile_id`
    - `projection_profile_id`
  - base scenario reference
  - compatibility schema refs
- `immutable_after_create=true` is required.
- `identity_hash` remains stable and does not fold semantic contract sidecar metadata into world/object id derivation.

## UniverseContractBundle
- Stable semantic pins:
  - worldgen refinement contract version
  - overlay merge contract version
  - logic evaluation contract version
  - process capsule contract version
  - system collapse contract version
  - GEO metric/projection/partition contract versions
  - app shell lifecycle contract version
- Replay/proof compares this bundle explicitly.
- The bundle is immutable for the universe lineage once created.

## UniverseState
- Mutable references:
  - current time anchor
  - refinement state
  - agent state refs
  - law/profile runtime refs
  - save/checkpoint refs
  - history log anchors

## Enforcement
- RepoX `INV-UNIVERSE_IDENTITY_IMMUTABLE` blocks identity-mutation symbols in runtime code.
- TestX `test_universe_identity_immutability` validates schema presence and immutable markers.
