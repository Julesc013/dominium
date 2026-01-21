--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Stable IDs, hashing, and deterministic ordering primitives.
GAME:
- Identity rules, lineage policy, and continuity handling.
SCHEMA:
- Identity/lineage record formats and validation constraints.
TOOLS:
- Inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No fabricated lineage.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_IDENTITY_AND_LINEAGE — Identity and Lineage Canon

Status: draft
Version: 1

## Purpose
Define identity vs instance, lineage records, and continuity across refinement,
collapse, archival, and forked timelines.

## Identity vs instance (canonical)
- Identity is persistent across time and survives collapse/refinement.
- Instance is a micro realization and is not identity-bearing alone.

This separation prevents "respawn breaks immersion" and "NPC popped with the
same name but different history."

## Lineage records (conceptual)
Required fields:
- life_id (identity anchor)
- parent_ids (0..2, may be UNKNOWN)
- lineage_certainty (EXACT | LIKELY | UNKNOWN)
- lineage_source_ref (observation or document)
- provenance_ref

Optional fields:
- adoption_refs
- guardian_refs
- cohort_ref (macro linkage)

## Continuity across time (rules)
- Refinement may realize instances but must preserve identity and lineage.
- Collapse aggregates instances but must preserve lineage summaries and
  provenance hashes.
- Archival freezes identity; mutation requires fork.
- Forking creates a new identity lineage root; parent remains immutable.

## What persists vs what does not
Persists across refinement/collapse:
- life_id, lineage_refs, provenance_refs, identity_state.

Does not persist automatically:
- micro instance details (location, health state).
- transient session/controller bindings.

## Integration points
- Existence and archival: `schema/existence/README.md`
- Refinement contracts: `schema/existence/SPEC_REFINEMENT_CONTRACTS.md`
- Reality layer: `docs/arch/REALITY_LAYER.md`

## See also
- `schema/life/SPEC_LIFE_ENTITIES.md`
- `schema/life/SPEC_REINCARNATION.md`
