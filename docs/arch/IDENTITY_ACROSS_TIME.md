# Identity Across Time (LIFE0+)

Status: binding.
Scope: identity continuity across refinement, collapse, archival, and forks.

## Identity vs instance
- Identity persists across time.
- Instance is a micro realization and can appear/disappear with refinement.

Identity survives refinement and collapse; instance details do not.

## What persists
Persists across refinement/collapse:
- life_id
- lineage_refs
- provenance_refs
- identity_state

Persists across archival:
- identity and lineage are immutable.
- history can only change via fork.

## What does not persist
- Embodiment state (location, health, inventory).
- Controller/session bindings.
- Ephemeral perception/epistemic cache.

## Forking rules
- Forking creates a new identity lineage root.
- Parent identity remains immutable and archived.
- Forked identity records must reference the parent lineage.

## Integration points
- Existence and archival: `schema/existence/README.md`
- Identity and lineage: `schema/life/SPEC_IDENTITY_AND_LINEAGE.md`
- Reality layer: `docs/arch/REALITY_LAYER.md`

## See also
- `docs/arch/DEATH_AND_CONTINUITY.md`
- `docs/arch/LIFE_AND_POPULATION.md`
