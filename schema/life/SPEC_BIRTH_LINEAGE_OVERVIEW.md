--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Stable IDs, hashing, deterministic scheduling primitives.
GAME:
- Birth triggers, lineage policy, and cohort integration (LIFE3+).
SCHEMA:
- Lineage fields and birth record formats (overview only).
TOOLS:
- Future inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No fabricated births or lineage links.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_BIRTH_LINEAGE_OVERVIEW — Birth and Lineage (Overview)

Status: legacy (superseded by LIFE0+)
Version: 1

Note: LIFE0+ canonical specs live in `schema/life/SPEC_BIRTH_CONTRACTS.md` and
`schema/life/SPEC_IDENTITY_AND_LINEAGE.md`. This overview remains for legacy
context; if any statement conflicts with LIFE0+, LIFE0+ wins.

## Purpose
Define the overview schema for birth and lineage. Full implementation is deferred
to LIFE3. Birth is a construction event that creates a new Person with provenance.

## Birth overview (conceptual)
- Birth consumes resources and time.
- Birth produces a new Person and (optionally) a Body.
- Birth is scheduled and deterministic (event-driven).
- Birth does not fabricate population; it must be a constructed pipeline.

## Lineage schema fields (conceptual)
Required fields:
- person_id
- parent_ids (0..2 entries)
- lineage_certainty (EXACT | LIKELY | UNKNOWN)
- lineage_source_ref (sensor/comms record or document)
- provenance_id

Optional fields:
- guardian_ids
- adoption_refs
- cohort_ref (macro aggregate link)

## Parentage uncertainty handling
- Parentage may be UNKNOWN and must remain UNKNOWN until observed or documented.
- Conflicting lineage records are allowed and must be explicit.
- No implicit resolution or auto-selection is permitted.

## Cohort integration (macro)
- Macro cohorts may store aggregated lineage summaries and counts.
- Refinement must preserve lineage provenance when possible.
- No global scans are permitted to resolve lineage; scope must be bounded.

## Implementation notes (LIFE3)
- Runtime code lives under `game/include/dominium/life/*` and `game/core/life/*`.
- Births are scheduled via the ACT due-event scheduler; no per-tick scans.
- Lineage records are deterministic and stored per person.
- Cohort updates are explicit and bounded; micro births do not require cohort scans.
- Epistemic knowledge of birth is emitted via an explicit callback hook only.

## Integration points
- Provenance: `docs/specs/SPEC_PROVENANCE.md`
- Information model: `docs/specs/SPEC_INFORMATION_MODEL.md`
- Fidelity projection: `docs/specs/SPEC_FIDELITY_PROJECTION.md`

## Prohibitions
- Fabricating lineage links.
- Auto-assigning parents without provenance.
- Creating persons outside construction pipelines.
