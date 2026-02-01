Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Terrain Truth Model (TERRAIN0)

Status: binding.
Scope: canonical terrain/matter truth model for all domains.

## Canonical truth
- Terrain truth is NOT meshes.
- Terrain truth is a field-defined solid over a domain volume.
- The canonical solid boundary is the Signed Distance Field (SDF) `terrain.phi`:
  - phi(x) < 0 inside solid
  - phi(x) = 0 surface
  - phi(x) > 0 outside solid
- Meshes are view-only caches and MUST NOT be authoritative.
- Collision, containment, and legality checks use `terrain.phi` (or derived fields),
  never meshes.

## Mutation and overlays
- All modifications are Process outputs via overlay providers.
- Overlays are auditable, provenance-tagged, and deterministic.
- Collapse, decay, and regeneration are Processes, never implicit background mutation.

## Bodies and domains
- No special case for "planet", "station", or "megastructure".
- All terrain exists as generic domain volumes with provider chains.
- Composition is by provider order, not by body type.

## Compatibility
- Process-only mutation: `docs/architecture/PROCESS_ONLY_MUTATION.md`.
- Refusal semantics: `docs/architecture/REFUSAL_SEMANTICS.md`.
- Deterministic ordering: `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md`.
- RNG model: `docs/architecture/RNG_MODEL.md`.
- Float policy: `docs/architecture/FLOAT_POLICY.md`.
- Invariants: `docs/architecture/INVARIANTS.md`.
- Scaling and collapse: `docs/architecture/SCALING_MODEL.md`,
  `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`.
- Epistemics: field values carry explicit knowledge state; unknown/latent preserved.

## Non-goals
- This contract does NOT define terrain algorithms or simulation detail.
- This contract does NOT freeze balance or real-world constants.